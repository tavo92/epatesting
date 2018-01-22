import argparse
import configparser
import subprocess

from run_test_epa import RunTestEPA
from make_report_resume import make_report_resume


def read_config_file(config_file, method):
    config = configparser.ConfigParser()
    config.read(config_file)

    # Reads the configuration values that will be used in each run
    junit_jar = config['DEFAULT']['JUnitJAR']
    evosuite_classes = config['DEFAULT']['EvoSuiteClasses']
    evosuite_jar_path = config['DEFAULT']['EvoSuiteJARPath']
    chunk_size = int(config['DEFAULT']['ChunkSize'])

    # Reads each section witch defines a run
    tests_to_run = []
    runid = 0
    for section in config.sections():
        name = config[section]['Name']
        code_dir = config[section]['CodeDir']
        instrumented_code_dir = config[section]['InstrumentedCodeDir']
        original_code_dir = config[section]['OriginalCodeDir']
        class_name = config[section]['ClassName']
        epa_path = config[section]['EPAPath']
        criterion = config[section]['Criterion']
        search_budget = config[section]['SearchBudget']
        tests_to_run.append(RunTestEPA(name=name, junit_jar=junit_jar, code_dir=code_dir, instrumented_code_dir=instrumented_code_dir, original_code_dir=original_code_dir, evosuite_classes=evosuite_classes, evosuite_jar_path=evosuite_jar_path, class_name=class_name, epa_path=epa_path, criterion=criterion, search_budget=search_budget, runid=runid, method=method))
        runid += 1
    return [tests_to_run[x:x+chunk_size] for x in range(0, len(tests_to_run), chunk_size)]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="The config file needed to run epatesting. See config_example.ini for an example.")
    parser.add_argument("method", help="Use 1 to generate the testsuites, 2 to generate the metrics and 3 to generate both.", type=int)
    args = parser.parse_args()

    # Run all the tests
    test_chunks = read_config_file(args.config_file, args.method)
    for chunk in test_chunks:
        for test in chunk:
            test.start()
        for test in chunk:
            test.join()

    # Clean directorys
    subprocess.run('rm -r evosuite-report/ report/', shell=True)
