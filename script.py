import argparse
import configparser

from run_test_epa import RunTestEPA
from make_report_resume import merge_all_resumes
import os
import time
import utils

class Subject:

    def __init__(self, name, instrumented_code_dir, original_code_dir, class_name, epa_path, mutants_dir, error_prot_list):
        self.name = name
        self.instrumented_code_dir = instrumented_code_dir
        self.original_code_dir = original_code_dir
        self.class_name = class_name
        self.epa_path = epa_path
        self.mutants_dir = mutants_dir
        self.error_prot_list = error_prot_list


class EPAConfig:

    def read_config_file(self, config_file):
        
        def replace_paths_separator(path):
            path = path.replace("\\", os.path.sep)
            return path.replace("/", os.path.sep)
    
        config = configparser.ConfigParser()
        config.read(config_file)

        user_home_dir = os.path.expanduser('~')
        # Reads the configuration values that will be used in each run
        self.junit_jar = replace_paths_separator(config['DEFAULT']['JUnitJAR'])
        self.junit_jar = os.path.join(user_home_dir, self.junit_jar)
        self.evosuite_classes = replace_paths_separator(config['DEFAULT']['EvoSuiteClasses'])
        self.evosuite_classes = os.path.join(user_home_dir, self.evosuite_classes)
        self.evosuite_jar_path = replace_paths_separator(config['DEFAULT']['EvoSuiteJARPath'])
        self.evosuite_jar_path = os.path.join(user_home_dir, self.evosuite_jar_path)
        self.evosuite_runtime_jar_path = replace_paths_separator(config['DEFAULT']['EvoSuiteRuntimeJARPath'])
        self.evosuite_runtime_jar_path = os.path.join(user_home_dir, self.evosuite_runtime_jar_path)
        self.results_dir_name = replace_paths_separator(config['DEFAULT']['ResultsDirName'])
        self.results_dir_name = os.path.join(user_home_dir, self.results_dir_name)
        self.workers = int(config['DEFAULT']['Workers'])
        self.hamcrest_jar_path = replace_paths_separator(config['DEFAULT']['HamcrestJarPath'])
        self.hamcrest_jar_path = os.path.join(user_home_dir, self.hamcrest_jar_path)

        # Reads each section witch defines a run
        # tests_to_run = []
        # runid = 0
        self.subjects = {}

        for section in config.sections():
            name = config[section]['Name']
            instrumented_code_dir = replace_paths_separator(config[section]['InstrumentedCodeDir'])
            instrumented_code_dir = os.path.join(user_home_dir, instrumented_code_dir)
            original_code_dir = replace_paths_separator(config[section]['OriginalCodeDir'])
            original_code_dir = os.path.join(user_home_dir, original_code_dir)
            class_name = config[section]['ClassName']
            epa_path = replace_paths_separator(config[section]['EPAPath'])
            epa_path = os.path.join(user_home_dir, epa_path)
            mutants_dir = replace_paths_separator(config[section]['MutantsDir'])
            mutants_dir = os.path.join(user_home_dir, mutants_dir)
            error_prot_list = replace_paths_separator(config[section]['ErrorProtList'])
            error_prot_list = os.path.join(user_home_dir, error_prot_list)
            self.subjects[section] = Subject(name, instrumented_code_dir, original_code_dir, class_name, epa_path, mutants_dir, error_prot_list)
            

    def read_runs_file(self, runs_file):

        with open(runs_file) as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]

        tests_to_run = []
        for line in lines:
            terms = line.split('*')
            subject_name = terms[0][1:-1]
            search_budget = terms[1][1:-1]
            criterion = terms[2][1:-1]
            method = int(terms[3])
            rep = int(terms[4])

            runid = 0
            for __ in range(rep):
                subject = self.subjects[subject_name]
                tests_to_run.append(RunTestEPA(name=subject.name, junit_jar=self.junit_jar, instrumented_code_dir=subject.instrumented_code_dir, original_code_dir=subject.original_code_dir, evosuite_classes=self.evosuite_classes, evosuite_jar_path=self.evosuite_jar_path, evosuite_runtime_jar_path=self.evosuite_runtime_jar_path, class_name=subject.class_name, epa_path=subject.epa_path, criterion=criterion, search_budget=search_budget, runid=runid, method=method, results_dir_name=self.results_dir_name, subdir_mutants=subject.mutants_dir, error_prot_list=subject.error_prot_list, hamcrest_jar_path=self.hamcrest_jar_path))
                runid += 1

        return [tests_to_run[x:x + self.workers] for x in range(0, len(tests_to_run), self.workers)]


_start_time = time.time()
def init():
    global _start_time 
    _start_time = time.time()
    
def elapsed_time():
    t_sec = round(time.time() - _start_time)
    (t_min, t_sec) = divmod(t_sec,60)
    (t_hour,t_min) = divmod(t_min,60)
    return [t_hour, t_min, t_sec]
    
def print_elapsed_time():
    total_time = elapsed_time()
    print('Total time: {}hour:{}min:{}sec'.format(total_time[0], total_time[1], total_time[2]))

global finished_subjects
global total_subjects
if __name__ == '__main__':
    init()
    config = EPAConfig()
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="The config file needed to run epatesting. See config_example.ini for an example.")
    parser.add_argument("runs_file", help="The runs file needed to run epatesting. See runs_example.ini for an example.")
    args = parser.parse_args()

    # Run all the tests
    config.read_config_file(args.config_file)
    test_chunks = config.read_runs_file(args.runs_file)
    
    all_resumes = []
    total_subjects = 0
    finished_subjects = 0
    for chunk in test_chunks:
        total_subjects = total_subjects + len(chunk)

    for chunk in test_chunks:
        for test in chunk:
            test.start()
        for test in chunk:
            test.join()
            all_resumes.append(os.path.join(test.subdir_metrics,'resume.csv'))
            finished_subjects = finished_subjects + 1
            percent_finished = finished_subjects*100/total_subjects
            total_time = elapsed_time()
            print("=====================================> PROGRESS {}% ({}/{}) Elapsed time: {}:{}:{}<=====================================".format(percent_finished, finished_subjects, total_subjects, total_time[0], total_time[1], total_time[2]))
    
    merge_all_resumes(all_resumes, 'all_resumes.csv')
    print_elapsed_time()
    utils.save_file("histogram.txt", utils.get_mutant_histogram())
    print("Done!")
