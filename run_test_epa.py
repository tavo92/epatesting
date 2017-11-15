import sys
import argparse
import subprocess
import csv
import xml.etree.ElementTree as ET
import threading

JUNIT_JAR = '/usr/share/java/junit4-4.12.jar'

def run_evosuite(evosuite_jar_path, projectCP, class_name, criterion, epa_path, search_budget=60, test_dir='test', report_dir='report'):
    subprocess.run(
        'java -jar {}evosuite-master-1.0.4-SNAPSHOT.jar -projectCP {} -class {} -criterion {} -Dsearch_budget={} -Djunit_allow_restricted_libraries=true -Dp_functional_mocking=\'0.0\' -Dp_reflection_on_private=\'0.0\' -Duse_separate_classloader=\'false\' -Dwrite_covered_goals_file=\'true\' -Dwrite_all_goals_file=\'true\' -Dprint_missed_goals=\'true\' -Dtest_dir={} -Dreport_dir={} -Depa_xml_path={} -Dno_runtime_dependency=\'true\''.format(evosuite_jar_path, projectCP, class_name, criterion, search_budget, test_dir, report_dir, epa_path), shell=True)

def measure_evosuite(evosuite_jar_path, projectCP, testCP, class_name, epa_path, report_dir):
    subprocess.run('java -jar {}evosuite-master-1.0.4-SNAPSHOT.jar -projectCP {}:{} -class {} -Depa_xml_path={} -criterion LINE:BRANCH:EPATRANSITION -Dwrite_covered_goals_file=\'true\' -Dwrite_all_goals_file=\'true\' -Dreport_dir={} -measureCoverage'.format(evosuite_jar_path, projectCP, testCP, class_name, epa_path, report_dir), shell=True)

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
    subprocess.run("find -name '*.java' > sources.txt", cwd=workdir, shell=True)
    subprocess.run(["javac", "-classpath", evosuite_classes, "@sources.txt"], cwd=workdir)

def compile_test_workdir(workdir, subject_class):
    subprocess.run("find -name '*.java' > sources.txt", cwd=workdir, shell=True)
    subprocess.run("javac -classpath {}:{} @sources.txt".format(JUNIT_JAR, subject_class), cwd=workdir, shell=True)

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
    edit_pit_pom('/home/lucas/Descargas/stackar_rev/pom.xml', targetClasses, targetTests, '{}/pom.xml'.format(pitest_dir))
    subprocess.run('cp -r {}/* {}/src/main/java'.format(class_dir, pitest_dir), shell=True)
    subprocess.run('cp -r {}/* {}/src/test/java'.format(test_dir, pitest_dir), shell=True)
    run_pitest('{}/'.format(pitest_dir))

def read_pit_csv(file_name):
    with open(file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        print(reader)
        # TODO: Ver el formato


def read_jacoco_csv(file_name):
    with open(file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        # TODO: Ver el formato

def copy_csv(file_path, file_name):
    subprocess.run('cp -r {} all_reports/{}.csv'.format(file_path, file_name), shell=True)

def read_pitest_csv(name, workdir):
    subprocess.run("find -name '*.csv' > sources.txt", cwd=workdir, shell=True)
    with open('{}/sources.txt'.format(workdir)) as file:
        for line in file:
            # TODO: Juntar la informacion y devolverla
            file_path = '{}/{}'.format(workdir, line[2:-1])
            if 'mutations' in line:
                read_pit_csv(file_path)
                copy_csv(file_path, '{}_mutations'.format(name))
            elif 'jacoco' in line:
                read_jacoco_csv(file_path)
                copy_csv(file_path, '{}_jacoco'.format(name))


class RunTestEPA(threading.Thread):
    def __init__(self, name, junit_jar, code_dir, instrumented_code_dir, original_code_dir, evosuite_classes, evosuite_jar_path, class_name, epa_path, criterion, generated_test_dir, generated_report_evosuite_dir, generated_report_pitest_dir):
        threading.Thread.__init__(self)

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
        self.generated_test_dir = generated_test_dir
        self.generated_report_evosuite_dir = generated_report_evosuite_dir
        self.generated_report_pitest_dir = generated_report_pitest_dir

    def run(self):
        # Compilo el codigo
        compile_workdir(self.code_dir, self.evosuite_classes)

        # Corro Evosuite
        run_evosuite(evosuite_jar_path=self.evosuite_jar_path, projectCP=self.code_dir, class_name=self.class_name, criterion=self.criterion, epa_path=self.epa_path, test_dir=self.generated_test_dir)

        compile_test_workdir(self.generated_test_dir, self.code_dir)

        measure_evosuite(evosuite_jar_path=self.evosuite_jar_path, projectCP=self.instrumented_code_dir, testCP=self.generated_test_dir, class_name=self.class_name, epa_path=self.epa_path, report_dir=self.generated_report_evosuite_dir)

        # Corro pitest para medir
        pitest_measure(self.generated_report_pitest_dir, self.class_name, "{}_ESTest".format(self.class_name), self.original_code_dir, self.generated_test_dir)

        # Recopilo informacion
        # De pitest
        subprocess.run('mkdir all_reports', shell=True)
        read_pitest_csv(self.name, self.generated_report_pitest_dir)
        copy_csv('{}/statistics.csv'.format(self.generated_report_evosuite_dir), 'epacoverage_{}'.format(self.name))
