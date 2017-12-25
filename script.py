from run_test_epa import RunTestEPA
from make_report_resume import make_report_resume
import configparser


def read_config_file(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    # Leo primero los valores de configuracion que se usan en todas las corridas
    junit_jar = config['DEFAULT']['JUnitJAR']
    evosuite_classes = config['DEFAULT']['EvoSuiteClasses']
    evosuite_jar_path = config['DEFAULT']['EvoSuiteJARPath']

    # Voy recorriendo lo que este definido
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
        tests_to_run.append(RunTestEPA(name=name, junit_jar=junit_jar, code_dir=code_dir, instrumented_code_dir=instrumented_code_dir, original_code_dir=original_code_dir, evosuite_classes=evosuite_classes, evosuite_jar_path=evosuite_jar_path, class_name=class_name, epa_path=epa_path, criterion=criterion, search_budget=search_budget, runid=runid))
        runid += 1
    return tests_to_run

if __name__ == '__main__':
    # Crear la clase y llamarla
    name = 'ListItr'
    junit_jar = '/usr/share/java/junit4-4.12.jar'
    instrumented_code_dir = '/home/lucas/LAFHIS/evosuite-subjects/workdir/listitr/instrumented'
    original_code_dir = '/home/lucas/LAFHIS/evosuite-subjects/workdir/listitr/original'
    evosuite_classes ='/home/lucas/LAFHIS/evosuite/client/target/classes'
    evosuite_jar_path = '/home/lucas/LAFHIS/evosuite/master/target/'
    class_name = 'ar.uba.dc.listitr.ListItr'
    epa_path = '/home/lucas/LAFHIS/evosuite-subjects/workdir/listitr/epa/ListItr.xml'

    test_original = RunTestEPA(name=name, junit_jar=junit_jar, code_dir=original_code_dir, instrumented_code_dir=instrumented_code_dir, original_code_dir=original_code_dir, evosuite_classes=evosuite_classes, evosuite_jar_path=evosuite_jar_path, class_name=class_name, epa_path=epa_path, criterion='LINE:BRANCH', search_budget=20, runid=1)

    test_instrumented = RunTestEPA(name=name, junit_jar=junit_jar, code_dir=instrumented_code_dir, instrumented_code_dir=instrumented_code_dir, original_code_dir=original_code_dir, evosuite_classes=evosuite_classes, evosuite_jar_path=evosuite_jar_path, class_name=class_name, epa_path=epa_path, criterion='LINE:BRANCH:EPATRANSITION', search_budget=20, runid=1)

    # Corro los threads
    test_original.start()
    test_instrumented.start()

    # Espero que terminen
    test_original.join()
    test_instrumented.join()

    # Corro todos los tests
    tests_to_run = read_config_file('config.txt')
    chunk_size = 4
    test_chunks = [tests_to_run[x:x+chunk_size] for x in range(0, len(tests_to_run), chunk_size)]
    for chunk in test_chunks:
        for test in chunk:
            test.start()
        for test in chunk:
            test.join()
    
