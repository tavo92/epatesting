import sys
import argparse
import subprocess
import csv
import xml.etree.ElementTree as ET
import threading
import os

from make_report_resume import make_report_resume

def print_command(command, workdir=None):
    print('Executing command in shell:')
    if workdir is not None:
        print('In workdir: {}'.format(workdir))
    print(command)

def run_evosuite(evosuite_jar_path, projectCP, class_name, criterion, epa_path, search_budget, test_dir='test', report_dir='report'):
    command = 'java -jar {}evosuite-master-1.0.4-SNAPSHOT.jar -projectCP {} -class {} -criterion {} -Dsearch_budget={} -Djunit_allow_restricted_libraries=true -Dp_functional_mocking=\'0.0\' -Dp_reflection_on_private=\'0.0\' -Duse_separate_classloader=\'false\' -Dwrite_covered_goals_file=\'true\' -Dwrite_all_goals_file=\'true\' -Dprint_missed_goals=\'true\' -Dtest_dir={} -Dreport_dir={} -Depa_xml_path={} -Dno_runtime_dependency=\'true\''.format(evosuite_jar_path, projectCP, class_name, criterion, search_budget, test_dir, report_dir, epa_path)
    print_command(command)
    subprocess.run(command, shell=True)

def measure_evosuite(evosuite_jar_path, projectCP, testCP, class_name, epa_path, report_dir):
    command = 'java -jar {}evosuite-master-1.0.4-SNAPSHOT.jar -projectCP {}:{} -class {} -Depa_xml_path={} -criterion EPATRANSITION -Dwrite_covered_goals_file=\'true\' -Dwrite_all_goals_file=\'true\' -Dreport_dir={} -measureCoverage'.format(evosuite_jar_path, projectCP, testCP, class_name, epa_path, report_dir)
    print_command(command)
    subprocess.run(command, shell=True)

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
    # Changes the targetClasses
    configuration[0][0].text = targetClasses
    # Changes the targetTests
    configuration[1][0].text = targetTests
    ET.register_namespace('', "http://maven.apache.org/POM/4.0.0")
    ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
    tree.write(output_file, default_namespace="")

def run_pitest(workdir):
    command = "mvn clean install org.pitest:pitest-maven:mutationCoverage"
    print_command(command, workdir)
    subprocess.run(command, cwd=workdir, shell=True)

def compile_workdir(workdir, evosuite_classes, output_directory):
    ''' TODO:
    -d directory
Set the destination directory for class files. The directory must already exist; javac will not create it. If a class is part of a package, javac puts the class file in a subdirectory reflecting the package name, creating directories as needed. For example, if you specify -d C:\myclasses and the class is called com.mypackage.MyClass, then the class file is called C:\myclasses\com\mypackage\MyClass.class.
If -d is not specified, javac puts each class files in the same directory as the source file from which it was generated.

Note: The directory specified by -d is not automatically added to your user class path.

    '''
    command_find = "find . -name '*.java' > sources.txt"
    print_command(command_find, workdir)
    subprocess.run(command_find, cwd=workdir, shell=True)

    command_mkdir_output = 'mkdir -p {}'.format(output_directory)
    print_command(command_mkdir_output)
    subprocess.run(command_mkdir_output, shell=True)

    command_compile = "javac -classpath {} -d {} @sources.txt".format(evosuite_classes, output_directory)
    print_command(command_compile, workdir)
    subprocess.run(command_compile, cwd=workdir, shell=True)

def compile_test_workdir(workdir, subject_class, junit_jar):
    command_find = "find . -name '*.java' > sources.txt"
    print_command(command_find, workdir)
    subprocess.run(command_find, cwd=workdir, shell=True)

    command_compile = "javac -classpath {}:{} @sources.txt".format(junit_jar, subject_class)
    print_command(command_compile, workdir)
    subprocess.run(command_compile, cwd=workdir, shell=True)

def generate_pitest_workdir(pitest_dir):
    # To generate the pitest workdir we need the following hierachy:
    # pom.xml
    # src/main/java/ < source code we want to test
    # src/test/java/ < testsuite
    command_mkdir_home = "mkdir {}".format(pitest_dir)
    print_command(command_mkdir_home)
    subprocess.run(command_mkdir_home, shell=True)

    command_mkdir_src = "mkdir {}/src".format(pitest_dir)
    print_command(command_mkdir_src)
    subprocess.run(command_mkdir_src, shell=True)

    command_mkdir_src_main = "mkdir {}/src/main".format(pitest_dir)
    print_command(command_mkdir_src_main)
    subprocess.run(command_mkdir_src_main, shell=True)

    command_mkdir_src_main_java = "mkdir {}/src/main/java".format(pitest_dir)
    print_command(command_mkdir_src_main_java)
    subprocess.run(command_mkdir_src_main_java, shell=True)

    command_mkdir_src_test = "mkdir {}/src/test".format(pitest_dir)
    print_command(command_mkdir_src_test)
    subprocess.run(command_mkdir_src_test, shell=True)

    command_mkdir_src_test_java = "mkdir {}/src/test/java".format(pitest_dir)
    print_command(command_mkdir_src_test_java)
    subprocess.run(command_mkdir_src_test_java, shell=True)

def pitest_measure(pitest_dir, targetClasses, targetTests, class_dir, test_dir):
    generate_pitest_workdir(pitest_dir)
    edit_pit_pom('pit_pom.xml', targetClasses, targetTests, '{}/pom.xml'.format(pitest_dir))

    command_copy_source = 'cp -r {}/* {}/src/main/java'.format(class_dir, pitest_dir)
    print_command(command_copy_source)
    subprocess.run(command_copy_source, shell=True)

    command_copy_test = 'cp -r {}/* {}/src/test/java'.format(test_dir, pitest_dir)
    print_command(command_copy_test)
    subprocess.run(command_copy_test, shell=True)

    run_pitest('{}/'.format(pitest_dir))

def copy_csv(file_path, file_name, all_report_dir):
    command = 'cp {} {}/{}.csv'.format(file_path, all_report_dir, file_name)
    print_command(command)
    subprocess.run(command, shell=True)

def copy_pitest_csv(name, workdir, all_report_dir):
    command = "find . -name '*.csv' > sources.txt"
    print_command(command, workdir)
    subprocess.run(command, cwd=workdir, shell=True)

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

        self.home_dir = os.path.dirname(os.path.abspath(__file__))
        self.compiled_code_dir = '{}/{}compiled/code'.format(self.home_dir, self.subdir)
        self.compiled_original_code_dir = '{}/{}compiled/original'.format(self.home_dir, self.subdir)
        self.compiled_instrumented_code_dir = '{}/{}compiled/instrumented'.format(self.home_dir, self.subdir)

    def run(self):
        # Compile code
        compile_workdir(self.code_dir, self.evosuite_classes, self.compiled_code_dir)
        compile_workdir(self.original_code_dir, self.evosuite_classes, self.compiled_original_code_dir)
        compile_workdir(self.instrumented_code_dir, self.evosuite_classes, self.compiled_instrumented_code_dir)

        # Run Evosuite
        run_evosuite(evosuite_jar_path=self.evosuite_jar_path, projectCP=self.compiled_code_dir, class_name=self.class_name, criterion=self.criterion, epa_path=self.epa_path, test_dir=self.generated_test_dir, search_budget=self.search_budget)

        compile_test_workdir(self.generated_test_dir, self.code_dir, self.junit_jar)

        measure_evosuite(evosuite_jar_path=self.evosuite_jar_path, projectCP=self.compiled_instrumented_code_dir, testCP=self.generated_test_dir, class_name=self.class_name, epa_path=self.epa_path, report_dir=self.generated_report_evosuite_dir)

        # Run Pitest to measure
        pitest_measure(self.generated_report_pitest_dir, self.class_name, "{}_ESTest".format(self.class_name), self.original_code_dir, self.generated_test_dir)

        # Clean directorys
        subprocess.run('rm -r evosuite-report/ report/', shell=True)

        # Resume the reports generated
        all_report_dir = '{}all_reports'.format(self.subdir)
        command_mkdir_report = 'mkdir {}'.format(all_report_dir)
        print_command(command_mkdir_report)
        subprocess.run(command_mkdir_report, shell=True)

        copy_pitest_csv(self.name, self.generated_report_pitest_dir, all_report_dir)
        copy_csv('{}/statistics.csv'.format(self.generated_report_evosuite_dir), 'epacoverage_{}'.format(self.name), all_report_dir)
        make_report_resume(self.name, '{}/epacoverage_{}.csv'.format(all_report_dir, self.name), '{}/{}_jacoco.csv'.format(all_report_dir, self.name), '{}/{}_mutations.csv'.format(all_report_dir, self.name), '{}resume.csv'.format(self.subdir))
