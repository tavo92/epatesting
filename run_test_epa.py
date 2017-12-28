import sys
import argparse
import subprocess
import csv
import xml.etree.ElementTree as ET
import threading

from make_report_resume import make_report_resume

def run_evosuite(evosuite_jar_path, projectCP, class_name, criterion, epa_path, search_budget, test_dir='test', report_dir='report'):
    subprocess.run(
        'java -jar {}evosuite-master-1.0.4-SNAPSHOT.jar -projectCP {} -class {} -criterion {} -Dsearch_budget={} -Djunit_allow_restricted_libraries=true -Dp_functional_mocking=\'0.0\' -Dp_reflection_on_private=\'0.0\' -Duse_separate_classloader=\'false\' -Dwrite_covered_goals_file=\'true\' -Dwrite_all_goals_file=\'true\' -Dprint_missed_goals=\'true\' -Dtest_dir={} -Dreport_dir={} -Depa_xml_path={} -Dno_runtime_dependency=\'true\''.format(evosuite_jar_path, projectCP, class_name, criterion, search_budget, test_dir, report_dir, epa_path), shell=True)

def measure_evosuite(evosuite_jar_path, projectCP, testCP, class_name, epa_path, report_dir):
    subprocess.run('java -jar {}evosuite-master-1.0.4-SNAPSHOT.jar -projectCP {}:{} -class {} -Depa_xml_path={} -criterion EPATRANSITION -Dwrite_covered_goals_file=\'true\' -Dwrite_all_goals_file=\'true\' -Dreport_dir={} -measureCoverage'.format(evosuite_jar_path, projectCP, testCP, class_name, epa_path, report_dir), shell=True)

def edit_pit_pom(file_path, targetClasses, targetTests, output_file):
    def find_by_subtag(node, subtag):
        for child in node:
            if subtag in child.tag:
                return child
    def find_pit_plugin(plugins):
        for plugin in plugins:
            for child in plugin:
                if "groupId" in child.tag and child.text == "org.pitest":
                    return plugin
    tree = ET.parse(file_path)
    root = tree.getroot()
    build = find_by_subtag(root, "build")
    plugins = find_by_subtag(build, "plugins")
    pitest_plugin = find_pit_plugin(plugins)
    configuration = find_by_subtag(pitest_plugin, "configuration")
    # Cambio el targetClasses
    configuration[0][0].text = targetClasses
    # Cambio el targetTests
    configuration[1][0].text = targetTests
    ET.register_namespace('', "http://maven.apache.org/POM/4.0.0")
    ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
    tree.write(output_file, default_namespace="")

def run_pitest(workdir):
    subprocess.run("mvn clean install org.pitest:pitest-maven:mutationCoverage", cwd=workdir, shell=True)

def compile_workdir(workdir, evosuite_classes):
    subprocess.run("find . -name '*.java' > sources.txt", cwd=workdir, shell=True)
    print("javac -classpath {} @sources.txt".format(evosuite_classes))
    print("En workdir {}".format(workdir))
    subprocess.run("javac -classpath {} @sources.txt".format(evosuite_classes), cwd=workdir, shell=True)
    #subprocess.run(["javac", "-classpath", evosuite_classes, "@sources.txt"], cwd=workdir)

def compile_test_workdir(workdir, subject_class, junit_jar):
    subprocess.run("find . -name '*.java' > sources.txt", cwd=workdir, shell=True)
    subprocess.run("javac -classpath {}:{} @sources.txt".format(junit_jar, subject_class), cwd=workdir, shell=True)

def generate_pitest_workdir(pitest_dir):
    # Hay que mover todo y trabajar con los directorios de la siguiente
    # manera:
    # pom.xml
    # src/main/java/ < codigo que queremos testear
    # src/test/java/ < testsuite
    subprocess.run("mkdir {}".format(pitest_dir), shell=True)
    subprocess.run("mkdir {}/src".format(pitest_dir), shell=True)
    subprocess.run("mkdir {}/src/main".format(pitest_dir), shell=True)
    subprocess.run("mkdir {}/src/main/java".format(pitest_dir), shell=True)
    subprocess.run("mkdir {}/src/test".format(pitest_dir), shell=True)
    subprocess.run("mkdir {}/src/test/java".format(pitest_dir), shell=True)

def pitest_measure(pitest_dir, targetClasses, targetTests, class_dir, test_dir):
    generate_pitest_workdir(pitest_dir)
    edit_pit_pom('pit_pom.xml', targetClasses, targetTests, '{}/pom.xml'.format(pitest_dir))
    subprocess.run('cp -r {}/* {}/src/main/java'.format(class_dir, pitest_dir), shell=True)
    subprocess.run('cp -r {}/* {}/src/test/java'.format(test_dir, pitest_dir), shell=True)
    run_pitest('{}/'.format(pitest_dir))

def copy_csv(file_path, file_name, all_report_dir):
    print('cp {} {}/{}.csv'.format(file_path, all_report_dir, file_name))
    subprocess.run('cp {} {}/{}.csv'.format(file_path, all_report_dir, file_name), shell=True)

def copy_pitest_csv(name, workdir, all_report_dir):
    subprocess.run("find . -name '*.csv' > sources.txt", cwd=workdir, shell=True)
    with open('{}/sources.txt'.format(workdir)) as file:
        for line in file:
            file_path = '{}/{}'.format(workdir, line[2:-1])
            if 'mutations' in line:
                copy_csv(file_path, '{}_mutations'.format(name), all_report_dir)
            elif 'jacoco' in line:
                copy_csv(file_path, '{}_jacoco'.format(name), all_report_dir)


class RunTestEPA(threading.Thread):
    def __init__(self, name, junit_jar, code_dir, instrumented_code_dir, original_code_dir, evosuite_classes, evosuite_jar_path, class_name, epa_path, criterion, search_budget, runid):
        threading.Thread.__init__(self)

        self.subdir = 'results/{}/{}/{}/'.format(criterion.replace(':', '_').lower(), search_budget, runid)
        self.name = name
        self.junit_jar = junit_jar
        self.code_dir = code_dir
        self.instrumented_code_dir = instrumented_code_dir
        self.original_code_dir = original_code_dir
        self.evosuite_classes = evosuite_classes
        self.evosuite_jar_path = evosuite_jar_path
        self.class_name = class_name
        self.epa_path = epa_path
        self.criterion = criterion
        self.generated_test_dir = '{}test'.format(self.subdir)
        self.generated_report_evosuite_dir = '{}report_evosuite'.format(self.subdir)
        self.generated_report_pitest_dir = '{}report_pitest'.format(self.subdir)
        self.search_budget = search_budget
        self.runid = runid

    def run(self):
        # Compilo el codigo
        compile_workdir(self.code_dir, self.evosuite_classes)

        # Corro Evosuite
        run_evosuite(evosuite_jar_path=self.evosuite_jar_path, projectCP=self.code_dir, class_name=self.class_name, criterion=self.criterion, epa_path=self.epa_path, test_dir=self.generated_test_dir, search_budget=self.search_budget)

        compile_test_workdir(self.generated_test_dir, self.code_dir, self.junit_jar)

        measure_evosuite(evosuite_jar_path=self.evosuite_jar_path, projectCP=self.instrumented_code_dir, testCP=self.generated_test_dir, class_name=self.class_name, epa_path=self.epa_path, report_dir=self.generated_report_evosuite_dir)

        # Corro pitest para medir
        pitest_measure(self.generated_report_pitest_dir, self.class_name, "{}_ESTest".format(self.class_name), self.original_code_dir, self.generated_test_dir)

        # Borro directorios generados que no son necesarios
        subprocess.run('rm -r evosuite-report/ report/', shell=True)

        # Recopilo informacion
        # De pitest
        all_report_dir = '{}all_reports'.format(self.subdir)
        subprocess.run('mkdir {}'.format(all_report_dir), shell=True)
        copy_pitest_csv(self.name, self.generated_report_pitest_dir, all_report_dir)
        copy_csv('{}/statistics.csv'.format(self.generated_report_evosuite_dir), 'epacoverage_{}'.format(self.name), all_report_dir)

        make_report_resume(self.name, '{}/epacoverage_{}.csv'.format(all_report_dir, self.name), '{}/{}_jacoco.csv'.format(all_report_dir, self.name), '{}/{}_mutations.csv'.format(all_report_dir, self.name), '{}resume.csv'.format(self.subdir))
