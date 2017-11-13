import sys
import argparse
import subprocess
import csv
import xml.etree.ElementTree as ET

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

def read_pitest_csv(workdir):
    subprocess.run("find -name '*.csv' > sources.txt", cwd=workdir, shell=True)
    with open('{}/sources.txt'.format(workdir)) as file:
        for line in file:
            # TODO: Juntar la informacion y devolverla
            file_path = '{}/{}'.format(workdir, line[2:-1])
            if 'mutations' in line:
                read_pit_csv(file_path)
                copy_csv(file_path, '{}_mutations'.format(workdir))
            elif 'jacoco' in line:
                read_jacoco_csv(file_path)
                copy_csv(file_path, '{}_jacoco'.format(workdir))

if __name__ == '__main__':

    # Esto deberia pasarlo por parametro
    original = '/home/lucas/LAFHIS/evosuite-subjects/workdir/listitr/original'
    instrumented = '/home/lucas/LAFHIS/evosuite-subjects/workdir/listitr/instrumented'
    evosuite_classes = '/home/lucas/LAFHIS/evosuite/client/target/classes'
    evosuite_jar_path = '/home/lucas/LAFHIS/evosuite/master/target/'
    class_name = 'ar.uba.dc.listitr.ListItr'
    epa_path = '/home/lucas/LAFHIS/evosuite-subjects/workdir/listitr/epa/ListItr.xml'

    # Compilo el codigo
    compile_workdir(instrumented, evosuite_classes)
    compile_workdir(original, evosuite_classes)

    # Corro Evosuite
    # Para el original
    run_evosuite(evosuite_jar_path=evosuite_jar_path, projectCP=original, class_name=class_name, criterion='LINE:BRANCH', epa_path=epa_path, test_dir='test_original')
    compile_test_workdir('test_original', original)
    measure_evosuite(evosuite_jar_path=evosuite_jar_path, projectCP=instrumented, testCP='test_original', class_name=class_name, epa_path=epa_path, report_dir='report_original')
    # Para el instrumentado
    run_evosuite(evosuite_jar_path=evosuite_jar_path, projectCP=instrumented, class_name=class_name, criterion='LINE:BRANCH:EPATRANSITION', epa_path=epa_path, test_dir='test_instrumented')
    compile_test_workdir('test_instrumented', instrumented)
    measure_evosuite(evosuite_jar_path=evosuite_jar_path, projectCP=instrumented, testCP='test_instrumented', class_name=class_name, epa_path=epa_path, report_dir='report_instrumented')

    # Corro pitest para medir
    pitest_measure('pitest_original', class_name, "{}_ESTest".format(class_name), original, 'test_original')
    pitest_measure('pitest_instrumented', class_name, "{}_ESTest".format(class_name), original, 'test_instrumented')

    # Recopilo informacion
    # De pitest
    subprocess.run('mkdir all_reports', shell=True)
    read_pitest_csv('pitest_original')
    read_pitest_csv('pitest_instrumented')
    copy_csv('report_original/statistics.csv', 'epacoverage_original')
    copy_csv('report_instrumented/statistics.csv', 'epacoverage_instrumented')
'''
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Experimentos TP2.')
    parser.add_argument('experimento', metavar='experimento', choices=[ 'componentes_ppales', 'pca_variando_knn', 'knn_solo', 'variar_cant_imagenes', 'variar_KValidation', 'variar_knn_validation'])
    args = parser.parse_args()
    if args.experimento == 'componentes_ppales':
        experimento_componentes_ppales()
    elif args.experimento == 'pca_variando_knn':
        experimento_pca_variando_knn()
    elif args.experimento == 'knn_solo':
        experimento_knn_solo()
    elif args.experimento == 'variar_cant_imagenes':
        experimento_variar_cant_imagenes()
    elif args.experimento == 'variar_KValidation':
        experimento_variar_KValidation()
    elif args.experimento == 'variar_knn_validation':
        experimento_variar_knn_validation()
'''
