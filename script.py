import argparse
import configparser
import mujava_coverage
from run_test_epa import RunTestEPA
import run_test_epa
from make_report_resume import merge_all_resumes
import os
import time
import utils
import pit_mutants_histogram
import R_results

class Subject:

    def __init__(self, name, instrumented_code_dir, original_code_dir, class_name, epa_path, mutants_dir, subdir_mutants, error_prot_list, all_mutants_list, ignore_mutants_list):
        self.name = name
        self.instrumented_code_dir = instrumented_code_dir
        self.original_code_dir = original_code_dir
        self.class_name = class_name
        self.epa_path = epa_path
        self.mutants_dir = mutants_dir
        self.subdir_mutants = subdir_mutants
        self.error_prot_list = error_prot_list
        self.all_mutants_list = all_mutants_list
        self.ignore_mutants_list = ignore_mutants_list


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
        
        # R SetUp
        self.r_executable_path = replace_paths_separator(config['R_SETUP']['R_executable_path'])
        self.R_script = config['R_SETUP']['R_script']
        self.Criterion_list = config['R_SETUP']['Criterion_list']

        # Reads each section witch defines a run
        # tests_to_run = []
        # runid = 0
        self.subjects = {}

        for section in config.sections():
            if section == "R_SETUP":
                continue
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
            all_mutants_list = replace_paths_separator(config[section]['AllMutantsList'])
            all_mutants_list = os.path.join(user_home_dir, all_mutants_list)
            try: # Que sea opcional tener la lista de mutantes a ignorar
                ignore_mutants_list = replace_paths_separator(config[section]['IgnoreMutantsList'])
                ignore_mutants_list = os.path.join(user_home_dir, ignore_mutants_list)
            except:
                ignore_mutants_list = ""
            subdir_mutants = os.path.join(self.results_dir_name, "mutants")
            error_prot_list = utils.load_list_from_file(error_prot_list)
            all_mutants_list = utils.load_list_from_file(all_mutants_list)
            ignore_mutants_list = utils.load_list_from_file(ignore_mutants_list)
            self.subjects[section] = Subject(name, instrumented_code_dir, original_code_dir, class_name, epa_path, mutants_dir, subdir_mutants, error_prot_list, all_mutants_list, ignore_mutants_list)
            
    
    def read_runs_file(self, runs_file):

        with open(runs_file) as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]

        tests_to_run = []
        for line in lines:
            terms = line.split('*')
            subject_name = terms[0][1:-1]
            bug_type = terms[1][1:-1]
            stopping_condition = terms[2][1:-1]
            search_budget = terms[3][1:-1]
            criterion = terms[4][1:-1]
            method = int(terms[5])
            rep = int(terms[6])
            
            subject = self.subjects[subject_name]
            mutant_list = subject.all_mutants_list
            if(bug_type.upper() == run_test_epa.BugType.ERRPROT.name):
                mutant_list = subject.error_prot_list
            
            utils.init_histogram(bug_type, subject_name, criterion, mutant_list, subject.ignore_mutants_list)
            
            runid = 0
            for __ in range(rep):
                tests_to_run.append(RunTestEPA(name=subject.name, junit_jar=self.junit_jar, instrumented_code_dir=subject.instrumented_code_dir, original_code_dir=subject.original_code_dir, evosuite_classes=self.evosuite_classes, evosuite_jar_path=self.evosuite_jar_path, evosuite_runtime_jar_path=self.evosuite_runtime_jar_path, class_name=subject.class_name, epa_path=subject.epa_path, criterion=criterion, bug_type=bug_type, stopping_condition=stopping_condition, search_budget=search_budget, runid=runid, method=method, results_dir_name=self.results_dir_name, subdir_mutants=subject.subdir_mutants, error_prot_list=subject.error_prot_list, ignore_mutants_list=subject.ignore_mutants_list, hamcrest_jar_path=self.hamcrest_jar_path))
                runid += 1

        return [tests_to_run[x:x + self.workers] for x in range(0, len(tests_to_run), self.workers)]
    
    def setupmujava_and_subjects(self, test_chunks):
        subjects = set()
        for chunk in test_chunks:
            for test in chunk:
                if test.name in self.subjects:
                    subjects.add(self.subjects[test.name])
        
        for subject in subjects:
            mujava_coverage.setup_mujava(subject.mutants_dir, subject.class_name, subject.subdir_mutants, subject.original_code_dir)
            run_test_epa.setup_subjects(self.results_dir_name, subject.original_code_dir, subject.instrumented_code_dir, subject.name, self.evosuite_classes, subject.class_name)


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
    print("Starting... {}".format(time.strftime("%H:%M:%S")))
    config = EPAConfig()
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="The config file needed to run epatesting. See config_example.ini for an example.")
    parser.add_argument("runs_file", help="The runs file needed to run epatesting. See runs_example.ini for an example.")
    args = parser.parse_args()

    # Run all the tests
    config.read_config_file(args.config_file)
    test_chunks = config.read_runs_file(args.runs_file)
    
    config.setupmujava_and_subjects(test_chunks)
    
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
            print("=====================================>{} PROGRESS {}% ({}/{}) Elapsed time: {}:{}:{}<=====================================".format(time.strftime("%H:%M:%S"), percent_finished, finished_subjects, total_subjects, total_time[0], total_time[1], total_time[2]))
    
    merge_all_resumes(all_resumes, 'all_resumes.csv')
    utils.save_file("mujava_histogram.txt", utils.get_mutant_histogram())
    utils.save_file("pit_histogram.txt", pit_mutants_histogram.get_histogram())
    #print("Generating R Results...")
    #R_results.generate_r_results(config.r_executable_path, config.R_script, "all_resumes.csv", config.Criterion_list.split(","), "summary_table.csv")
    #R_results.generate_latex_table("summary_table.csv", "summary_table.tex")
    print("Done! {}".format(time.strftime("%H:%M:%S")))
    print_elapsed_time()
