from run_test_epa import RunTestEPA
from make_report_resume import make_report_resume

JUNIT_JAR = '/usr/share/java/junit4-4.12.jar'

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

    test_original = RunTestEPA(name='{}_original'.format(name), junit_jar=junit_jar, code_dir=original_code_dir, instrumented_code_dir=instrumented_code_dir, original_code_dir=original_code_dir, evosuite_classes=evosuite_classes, evosuite_jar_path=evosuite_jar_path, class_name=class_name, epa_path=epa_path, criterion='LINE:BRANCH', search_budget=20, runid=1)

    test_instrumented = RunTestEPA(name='{}_instrumented'.format(name), junit_jar=junit_jar, code_dir=instrumented_code_dir, instrumented_code_dir=instrumented_code_dir, original_code_dir=original_code_dir, evosuite_classes=evosuite_classes, evosuite_jar_path=evosuite_jar_path, class_name=class_name, epa_path=epa_path, criterion='LINE:BRANCH:EPATRANSITION', search_budget=20, runid=1)

    # Corro los threads
    test_original.start()
    test_instrumented.start()

    # Espero que terminen
    test_original.join()
    test_instrumented.join()

    make_report_resume(name, 'all_reports/epacoverage_{}_original.csv'.format(name), 'all_reports/{}_original_jacoco.csv'.format(name), 'all_reports/{}_original_mutations.csv'.format(name), 'all_reports/epacoverage_{}_instrumented.csv'.format(name), 'all_reports/{}_instrumented_jacoco.csv'.format(name), 'all_reports/{}_instrumented_mutations.csv'.format(name), 'resume.csv')
