import subprocess
import xml.etree.ElementTree as ET
import threading
import os
import shutil
from enum import Enum

from make_report_resume import make_report_resume
import mujava_coverage
import utils

class EpatestingMethod(Enum):
    TESTGEN = 1
    METRICS = 2
    BOTH = 3


def run_evosuite(evosuite_jar_path, projectCP, class_name, criterion, epa_path, search_budget, test_dir='test', report_dir='report'):
    command = 'java -jar {}evosuite-master-1.0.4-SNAPSHOT.jar -projectCP {} -class {} -criterion {} -Dsearch_budget={} -Djunit_allow_restricted_libraries=true -Dp_functional_mocking=\"0.0\" -Dp_reflection_on_private=\"0.0\" -Duse_separate_classloader=\"false\" -Dwrite_covered_goals_file=\"true\" -Dwrite_all_goals_file=\"true\" -Dprint_missed_goals=\"true\" -Dtest_dir={} -Dreport_dir={} -Depa_xml_path={} -Dno_runtime_dependency=\"true\" -Dassertions=\"true\" -Dshow_progress=\"false\" > {}ge_out.txt 2> {}gen_err.txt'.format(evosuite_jar_path, projectCP, class_name, criterion, search_budget, test_dir, report_dir, epa_path, test_dir, test_dir)
    utils.print_command(command)
    subprocess.check_output(command, shell=True)

def workaround_test(test_dir, class_name, file_name):
    packages = class_name.split(".")[0:-1]
    packages_dir = utils.get_package_dir(packages)
    java_file = os.path.join(test_dir, packages_dir, file_name)
    utils.replace_assert_catch_in_tests(java_file)

def measure_evosuite(evosuite_jar_path, projectCP, testCP, class_name, epa_path, report_dir):
    utils.make_dirs_if_not_exist(report_dir)
    err_file = os.path.join(report_dir, "epatransition_err.txt")
    out_file = os.path.join(report_dir, "epatransition_out.txt")
    sep = os.path.pathsep
    command = 'java -jar {}evosuite-master-1.0.4-SNAPSHOT.jar -projectCP {}{}{} -class {} -Depa_xml_path={} -criterion EPATRANSITION -Dwrite_covered_goals_file=\"true\" -Dwrite_all_goals_file=\"true\" -Dreport_dir={} -measureCoverage > {} 2> {}'.format(evosuite_jar_path, projectCP, sep, testCP, class_name, epa_path, report_dir, out_file, err_file)
    utils.print_command(command)
    subprocess.check_output(command, shell=True)


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
    command = "mvn clean install org.pitest:pitest-maven:mutationCoverage > {}out.txt 2> {}err.txt".format(workdir, workdir)
    utils.print_command(command, workdir)
    subprocess.check_output(command, cwd=workdir, shell=True)


def generate_pitest_workdir(pitest_dir):
    # To generate the pitest workdir we need the following hierachy:
    # pom.xml
    # src/main/java/ < source code we want to test
    # src/test/java/ < testsuite
    command_mkdir_home = "mkdir {}".format(pitest_dir)
    utils.print_command(command_mkdir_home)
    if not os.path.exists(pitest_dir):
        os.makedirs(pitest_dir)
    pitest_dir_src = os.path.join(pitest_dir, "src");
    command_mkdir_src = "mkdir {}".format(pitest_dir_src)
    utils.print_command(command_mkdir_src)
    if not os.path.exists(pitest_dir_src):
        os.makedirs(pitest_dir_src)

    pitest_dir_src_main = os.path.join(pitest_dir, "src", "main");
    command_mkdir_src_main = "mkdir {}".format(pitest_dir_src_main)
    utils.print_command(command_mkdir_src_main)
    if not os.path.exists(pitest_dir_src_main):
        os.makedirs(pitest_dir_src_main)

    pitest_dir_src_main_java = os.path.join(pitest_dir, "src", "main", "java")
    command_mkdir_src_main_java = "mkdir {}".format(pitest_dir_src_main_java)
    utils.print_command(command_mkdir_src_main_java)
    if not os.path.exists(pitest_dir_src_main_java):
        os.makedirs(pitest_dir_src_main_java)
    
    pitest_dir_src_test = os.path.join(pitest_dir, "src", "test")
    command_mkdir_src_test = "mkdir {}".format(pitest_dir_src_test)
    utils.print_command(command_mkdir_src_test)
    if not os.path.exists(pitest_dir_src_test):
        os.makedirs(pitest_dir_src_test)
        
    pitest_dir_src_test_java = os.path.join(pitest_dir, "src", "test", "java")        
    command_mkdir_src_test_java = "mkdir {}".format(pitest_dir_src_test_java)
    utils.print_command(command_mkdir_src_test_java)
    if not os.path.exists(pitest_dir_src_test_java):
        os.makedirs(pitest_dir_src_test_java)


def pitest_measure(pitest_dir, targetClasses, targetTests, class_dir, test_dir):
    generate_pitest_workdir(pitest_dir)
    edit_pit_pom('pit_pom.xml', targetClasses, targetTests, os.path.join(pitest_dir, "pom.xml"))

    pitest_dir_src_main_java = os.path.join(pitest_dir, "src", "main", "java")
    command_copy_source = 'cp -r {}/* {}'.format(class_dir, pitest_dir_src_main_java)
    utils.print_command(command_copy_source)
    # Si existe el directorio lo elimino (sino tira error shutil.copytree)
    if os.path.exists(pitest_dir_src_main_java):
        shutil.rmtree(pitest_dir_src_main_java)
    shutil.copytree(class_dir, pitest_dir_src_main_java)
    
    pitest_dir_src_test_java = os.path.join(pitest_dir, "src", "test", "java")
    command_copy_test = 'cp -r {}/* {}'.format(test_dir, pitest_dir_src_test_java)
    utils.print_command(command_copy_test)
    if os.path.exists(pitest_dir_src_test_java):
        shutil.rmtree(pitest_dir_src_test_java)
    shutil.copytree(test_dir, pitest_dir_src_test_java)

    run_pitest(os.path.join(pitest_dir, ""))
    
def mujava_measure(subdir_mutants, error_prot_list, compiled_original_code_dir, generated_test_dir, class_name, junit_jar, hamcrest_jar, generated_report_mujava):
    mujava = mujava_coverage.MuJava(subdir_mutants, error_prot_list, compiled_original_code_dir, generated_test_dir, class_name, junit_jar, hamcrest_jar, generated_report_mujava)
    mujava.compute_mutation_score()


def copy_csv(file_path, file_name, all_report_dir):
    dest = os.path.join(all_report_dir, "{}.csv".format(file_name))
    command = 'cp {} {}'.format(file_path, dest)
    utils.print_command(command)
    shutil.copyfile(file_path, dest)


def copy_pitest_csv(name, workdir, all_report_dir):
    command = utils.find_and_save_command("*.csv", "sources.txt")
    utils.print_command(command, workdir)
    
    utils.lock_if_windows()
    subprocess.check_output(command, cwd=workdir, shell=True)
    utils.release_if_windows()

    with open(os.path.join(workdir, "sources.txt")) as file:
        for line in file:
            file_path = os.path.join(workdir, line[2:-1])
            if 'mutations' in line:
                copy_csv(file_path, '{}_mutations'.format(name), all_report_dir)
            elif 'jacoco' in line:
                copy_csv(file_path, '{}_jacoco'.format(name), all_report_dir)


class RunTestEPA(threading.Thread):

    def __init__(self, name, junit_jar, code_dir, instrumented_code_dir, original_code_dir, evosuite_classes, evosuite_jar_path, evosuite_runtime_jar_path, class_name, epa_path, criterion, search_budget, runid, method, results_dir_name, subdir_mutants, error_prot_list, hamcrest_jar_path):
        threading.Thread.__init__(self)

        self.subdir_testgen = os.path.join(results_dir_name, "testgen", name, search_budget, criterion.replace(':', '_').lower(), "{}".format(runid))
        self.subdir_metrics = os.path.join(results_dir_name, "metrics", name, search_budget, criterion.replace(':', '_').lower(), "{}".format(runid))
        self.subdir_mutants = os.path.join(results_dir_name, "mutants")

        self.name = name
        self.junit_jar = junit_jar
        self.code_dir = code_dir
        self.instrumented_code_dir = instrumented_code_dir
        self.original_code_dir = original_code_dir
        self.evosuite_classes = evosuite_classes
        self.evosuite_jar_path = evosuite_jar_path
        self.evosuite_runtime_jar_path = evosuite_runtime_jar_path
        self.class_name = class_name
        self.epa_path = epa_path
        self.criterion = criterion
        self.generated_test_dir = os.path.join(self.subdir_testgen, 'test')
        self.generated_report_evosuite_dir = os.path.join(self.subdir_metrics, 'report_evosuite')
        self.generated_report_pitest_dir = os.path.join(self.subdir_metrics, 'report_pitest')
        self.generated_report_mujava = os.path.join(self.subdir_metrics, 'report_mujava')
        self.search_budget = search_budget
        self.runid = runid

        self.home_dir = os.path.dirname(os.path.abspath(__file__))
        self.compiled_code_dir = os.path.join(self.home_dir, self.subdir_testgen, "compiled", "code")
        self.compiled_original_code_dir = os.path.join(self.home_dir, self.subdir_testgen, "compiled", "original")
        self.compiled_instrumented_code_dir = os.path.join(self.home_dir, self.subdir_testgen, "compiled", "instrumented")
        self.method = method
        
        self.mutants_dir = subdir_mutants
        self.error_prot_list = error_prot_list
        self.hamcrest_jar_path = hamcrest_jar_path 

    def run(self):
        if self.method in [EpatestingMethod.TESTGEN.value, EpatestingMethod.BOTH.value]:
            print('GENERATING TESTS')
            # Compile code
            #lock_if_windows()
            utils.compile_workdir(self.code_dir, self.compiled_code_dir, self.evosuite_classes)
            utils.compile_workdir(self.original_code_dir, self.compiled_original_code_dir, self.evosuite_classes)
            utils.compile_workdir(self.instrumented_code_dir, self.compiled_instrumented_code_dir, self.evosuite_classes)
            #release_if_windows()
            
            #Copy and compile mujava directories
            mujava_coverage.setup_mujava(self.mutants_dir, self.class_name, self.subdir_mutants, self.compiled_code_dir, self.error_prot_list)
            
            # Run Evosuite
            generated_test_report_evosuite_dir = os.path.join(self.subdir_testgen, 'report_evosuite_generated_test')
            run_evosuite(evosuite_jar_path=self.evosuite_jar_path, projectCP=self.compiled_code_dir, class_name=self.class_name, criterion=self.criterion, epa_path=self.epa_path, test_dir=self.generated_test_dir, search_budget=self.search_budget, report_dir=generated_test_report_evosuite_dir)
            workaround_test(self.generated_test_dir, self.class_name, self.class_name.split(".")[-1]+"_ESTest.java")

            utils.compile_workdir(self.generated_test_dir, self.generated_test_dir, self.code_dir, self.junit_jar, self.evosuite_classes, self.evosuite_runtime_jar_path)

        if self.method in [EpatestingMethod.METRICS.value, EpatestingMethod.BOTH.value]:
            print('GENERATING METRICS')
            if not os.path.exists(self.subdir_testgen):
                print("not found testgen folder !")
                exit(1)
                
            measure_evosuite(evosuite_jar_path=self.evosuite_jar_path, projectCP=self.compiled_instrumented_code_dir, testCP=self.generated_test_dir, class_name=self.class_name, epa_path=self.epa_path, report_dir=self.generated_report_evosuite_dir)

            # Run Pitest to measure
            pitest_measure(self.generated_report_pitest_dir, self.class_name, "{}_ESTest".format(self.class_name), self.original_code_dir, self.generated_test_dir)
            
            mujava_measure(self.subdir_mutants, self.error_prot_list, self.compiled_original_code_dir, self.generated_test_dir, self.class_name, self.junit_jar, self.hamcrest_jar_path, self.generated_report_mujava)

            # Resume the reports generated
            all_report_dir = os.path.join(self.subdir_metrics, 'all_reports')
            command_mkdir_report = 'mkdir {}'.format(all_report_dir)
            utils.print_command(command_mkdir_report)
            if not os.path.exists(all_report_dir):
                os.makedirs(all_report_dir)

            copy_pitest_csv(self.name, self.generated_report_pitest_dir, all_report_dir)
            
            statistics_csv = os.path.join(self.generated_report_evosuite_dir, "statistics.csv")
            copy_csv(statistics_csv, 'epacoverage_{}'.format(self.name), all_report_dir)
            
            mujava_csv = os.path.join(self.generated_report_mujava, "mujava_report.csv")
            copy_csv(mujava_csv, 'mujava_{}'.format(self.name), all_report_dir)
            
            epacoverage_csv = os.path.join(all_report_dir, "epacoverage_{}.csv".format(self.name))
            jacoco_csv = os.path.join(all_report_dir, "{}_jacoco.csv".format(self.name))
            mutations_csv = os.path.join(all_report_dir, "{}_mutations.csv".format(self.name))
            resume_csv = os.path.join(self.subdir_metrics, 'resume.csv')
            criterion = get_alternative_criterion_names(self.criterion)
            make_report_resume(self.class_name, epacoverage_csv, jacoco_csv, mutations_csv, resume_csv, self.runid, self.search_budget, criterion, mujava_csv)
            
def get_alternative_criterion_names(criterion):
    if (criterion == "line:branch"):
        criterion = "evosuite_default"
    if (criterion == "epatransition"):
        criterion = "evosuite_epaalone"
    if (criterion == "line:branch:epatransition"):
        criterion = "evosuite_epamixed"
    return criterion