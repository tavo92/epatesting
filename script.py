import argparse
import configparser
import subprocess

from run_test_epa import RunTestEPA
from make_report_resume import make_report_resume, merge_all_resumes


class Subject:
    def __init__(self, name, code_dir, instrumented_code_dir, original_code_dir, class_name, epa_path):
        self.name = name
        self.code_dir = code_dir
        self.instrumented_code_dir = instrumented_code_dir
        self.original_code_dir = original_code_dir
        self.class_name = class_name
        self.epa_path = epa_path


class EPAConfig:
    def read_config_file(self, config_file, method):
        config = configparser.ConfigParser()
        config.read(config_file)

        # Reads the configuration values that will be used in each run
        self.junit_jar = config['DEFAULT']['JUnitJAR']
        self.evosuite_classes = config['DEFAULT']['EvoSuiteClasses']
        self.evosuite_jar_path = config['DEFAULT']['EvoSuiteJARPath']
        self.chunk_size = int(config['DEFAULT']['ChunkSize'])

        # Reads each section witch defines a run
        #tests_to_run = []
        #runid = 0
        self.subjects = {}

        for section in config.sections():
            name = config[section]['Name']
            code_dir = config[section]['CodeDir']
            instrumented_code_dir = config[section]['InstrumentedCodeDir']
            original_code_dir = config[section]['OriginalCodeDir']
            class_name = config[section]['ClassName']
            epa_path = config[section]['EPAPath']
            self.subjects[section] = Subject(name, code_dir, instrumented_code_dir, original_code_dir, class_name, epa_path)


    def read_runs_file(self, file):
        # File format:
        # [SUBJECTS]*[BUDGETS]*[CRITERIOS]*METHOD*REP
        def parse_runs_values(values):
            # Remove brackets
            values = values[1:-1]
            # Split by commas
            return values.split(',')

        with open(file) as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]

        tests_to_run = []
        runid = 0
        for line in lines:
            terms = line.split('*')
            subjects_names = parse_runs_values(terms[0])
            search_budgets = parse_runs_values(terms[1])
            criterions = parse_runs_values(terms[2])
            method = int(terms[3])
            rep = int(terms[4])

            for subject_name in subjects_names:
                for search_budget in search_budgets:
                    for criterion in criterions:
                        for __ in range(rep):
                            subject = self.subjects[subject_name]
                            tests_to_run.append(RunTestEPA(name=subject.name, junit_jar=self.junit_jar, code_dir=subject.code_dir, instrumented_code_dir=subject.instrumented_code_dir, original_code_dir=subject.original_code_dir, evosuite_classes=self.evosuite_classes, evosuite_jar_path=self.evosuite_jar_path, class_name=subject.class_name, epa_path=subject.epa_path, criterion=criterion, search_budget=search_budget, runid=runid, method=method))
                            runid += 1

        return [tests_to_run[x:x+self.chunk_size] for x in range(0, len(tests_to_run), self.chunk_size)]

if __name__ == '__main__':
    '''
    config = EPAConfig()

    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="The config file needed to run epatesting. See config_example.ini for an example.")
    parser.add_argument("method", help="Use 1 to generate the testsuites, 2 to generate the metrics and 3 to generate both.", type=int)
    args = parser.parse_args()

    # Run all the tests
    config.read_config_file(args.config_file, args.method)
    test_chunks = config.read_runs_file('config2.ini')
    all_resumes = []
    for chunk in test_chunks:
        for test in chunk:
            test.start()
        for test in chunk:
            test.join()
            all_resumes.append('{}resume.csv'.format(test.subdir_metrics))

    print(all_resumes)
    '''
    all_resumes = ['results/metrics/ListItr/10/line/0/resume.csv', 'results/metrics/ListItr/10/line/1/resume.csv', 'results/metrics/ListItr/10/line/2/resume.csv', 'results/metrics/ListItr/10/line/3/resume.csv', 'results/metrics/ListItr/10/line/4/resume.csv', 'results/metrics/ListItr/10/line_branch/5/resume.csv', 'results/metrics/ListItr/10/line_branch/6/resume.csv', 'results/metrics/ListItr/10/line_branch/7/resume.csv', 'results/metrics/ListItr/10/line_branch/8/resume.csv', 'results/metrics/ListItr/10/line_branch/9/resume.csv', 'results/metrics/ListItr/20/line/10/resume.csv', 'results/metrics/ListItr/20/line/11/resume.csv', 'results/metrics/ListItr/20/line/12/resume.csv', 'results/metrics/ListItr/20/line/13/resume.csv', 'results/metrics/ListItr/20/line/14/resume.csv', 'results/metrics/ListItr/20/line_branch/15/resume.csv', 'results/metrics/ListItr/20/line_branch/16/resume.csv', 'results/metrics/ListItr/20/line_branch/17/resume.csv', 'results/metrics/ListItr/20/line_branch/18/resume.csv', 'results/metrics/ListItr/20/line_branch/19/resume.csv', 'results/metrics/ListItr/30/line/20/resume.csv', 'results/metrics/ListItr/30/line/21/resume.csv', 'results/metrics/ListItr/30/line/22/resume.csv', 'results/metrics/ListItr/30/line/23/resume.csv', 'results/metrics/ListItr/30/line/24/resume.csv', 'results/metrics/ListItr/30/line_branch/25/resume.csv', 'results/metrics/ListItr/30/line_branch/26/resume.csv', 'results/metrics/ListItr/30/line_branch/27/resume.csv', 'results/metrics/ListItr/30/line_branch/28/resume.csv', 'results/metrics/ListItr/30/line_branch/29/resume.csv', 'results/metrics/ListItr/10/line/30/resume.csv', 'results/metrics/ListItr/10/line/31/resume.csv', 'results/metrics/ListItr/10/line/32/resume.csv', 'results/metrics/ListItr/10/line/33/resume.csv', 'results/metrics/ListItr/10/line/34/resume.csv', 'results/metrics/ListItr/10/line_branch/35/resume.csv', 'results/metrics/ListItr/10/line_branch/36/resume.csv', 'results/metrics/ListItr/10/line_branch/37/resume.csv', 'results/metrics/ListItr/10/line_branch/38/resume.csv', 'results/metrics/ListItr/10/line_branch/39/resume.csv', 'results/metrics/ListItr/20/line/40/resume.csv', 'results/metrics/ListItr/20/line/41/resume.csv', 'results/metrics/ListItr/20/line/42/resume.csv', 'results/metrics/ListItr/20/line/43/resume.csv', 'results/metrics/ListItr/20/line/44/resume.csv', 'results/metrics/ListItr/20/line_branch/45/resume.csv', 'results/metrics/ListItr/20/line_branch/46/resume.csv', 'results/metrics/ListItr/20/line_branch/47/resume.csv', 'results/metrics/ListItr/20/line_branch/48/resume.csv', 'results/metrics/ListItr/20/line_branch/49/resume.csv', 'results/metrics/ListItr/30/line/50/resume.csv', 'results/metrics/ListItr/30/line/51/resume.csv', 'results/metrics/ListItr/30/line/52/resume.csv', 'results/metrics/ListItr/30/line/53/resume.csv', 'results/metrics/ListItr/30/line/54/resume.csv', 'results/metrics/ListItr/30/line_branch/55/resume.csv', 'results/metrics/ListItr/30/line_branch/56/resume.csv', 'results/metrics/ListItr/30/line_branch/57/resume.csv', 'results/metrics/ListItr/30/line_branch/58/resume.csv', 'results/metrics/ListItr/30/line_branch/59/resume.csv']

    merge_all_resumes(all_resumes, 'all_resumes.csv')

    # Clean directorys
    subprocess.run('rm -r evosuite-report/ report/', shell=True)
