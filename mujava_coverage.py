import argparse
import os
import subprocess
import re
import shutil
import utils

class MuJava:
    
    def __init__(self, dir_mutants, orig_class_bin_dir, test_suite_bin, test_suite_name, junit_path, hamcrest_path, output_dir):
        self.dir_mutants = dir_mutants
        self.orig_class_bin_dir = orig_class_bin_dir
        self.test_suite_bin = test_suite_bin
        self.test_suite_name = test_suite_name
        self.junit_path = junit_path
        self.hamcrest_jar = hamcrest_path
        self.output_dir = output_dir
        
    def compute_mutation_score(self):
        print("Running mutation score...")
        junit = JUnit(self.junit_path, self.hamcrest_jar, self.test_suite_bin)
        original = junit.execute_testsuite(self.orig_class_bin_dir, self.test_suite_name, self.orig_class_bin_dir)
        
        def check_alive(self, class_dir):
            cp_mutant = "{}{}{}".format(class_dir, os.path.pathsep, self.orig_class_bin_dir)
            mutant = junit.execute_testsuite(cp_mutant, self.test_suite_name, class_dir)
            return original[0] == mutant[0] and original[1] == mutant[1]
        
        def check_empty_dir(mutant_dir):
            for dirpath, dirnames, files in os.walk(mutant_dir):
                if os.listdir(dirpath) == []:
                        print("ERROR! MUTANT DIR: {} must not be empty! Check it!".format(mutant_dir))
                        exit(1)
        
        total = 0
        killed = 0
        curr_subject = self.test_suite_name.replace("Test","")
        curr_subject_dir = os.path.join(self.dir_mutants, curr_subject)
        for curr_mutant in os.listdir(curr_subject_dir):
            curr_mutant = os.path.join(curr_subject_dir, curr_mutant)
            # only check dirs
            if not os.path.isdir(curr_mutant):
                continue
            check_empty_dir(curr_mutant)
            is_killed = not check_alive(self, curr_mutant)
            if(is_killed):
                killed += 1
            total += 1
        if total == 0:
            print("\tNo generated mutants for: {} subject".format(curr_subject))
            exit(1)
        save_report = "(echo TOTAL,KILLED,MUTATION_COVERAGE & echo {},{},{}) > {}{}mujava_report.csv".format(total, killed, (killed/total), self.output_dir, os.path.sep)
        print("\tRunning: {}".format(save_report))
        subprocess.check_output(save_report, shell=True)
        
        print("total: {} - Killed: {} - coverage: {}".format(total, killed, killed/total))


class JUnit:
    
    def __init__(self, junit_path, hamcrest_path, testsuite_bin_dir):
        self.junit_path = junit_path
        self.hamcrest_jar = hamcrest_path
        self.testsuite_bin_dir = testsuite_bin_dir
    
    def execute_testsuite(self, class_dir, testsuite_name, output_dir):
        def read_results(result):
            
            def all_ok(line):
                return "OK" in line
            
            def get_values(line):
                if all_ok(line):
                    return [[int(s) for s in line.replace("(","").split(" ") if s.isdigit()][0], 0]
                ret = [int(s) for s in line.replace(",","").replace("\n","").split(" ") if s.isdigit()]
                return ret
                
            
            with open(result) as f:
                content = f.readlines()
            last_line = ""
            for line in content:
                if re.match(r'^\s*$', line):#line empty
                    continue
                else:
                    last_line = line
            #print("Last Line: {}".format(last_line))
            total = get_values(last_line)[0]
            failure = get_values(last_line)[1]
            return [total, failure]
        
        sep = os.path.pathsep
        output_dir += os.path.sep
        command_junit = "java -cp {}{}{}{}{}{}{} org.junit.runner.JUnitCore {} > {}mujava_out.txt 2> {}mujava_err.txt".format(self.junit_path, sep, self.hamcrest_jar, sep, class_dir, sep, self.testsuite_bin_dir, testsuite_name, output_dir, output_dir)
        print("\tRunning: {}".format(command_junit))
        try:
            subprocess.check_output(command_junit, shell=True)
        except:
            None
        ret = read_results("{}mujava_out.txt".format(output_dir))
        return ret
    

# Prepare mujava mutants structure for future mutation score analysis
def setup_mujava(mujava_home, mutants_dir):
    def mk_and_cp_operator_mutant_dir(src_dir, mutants_dir, subject_name, operator_dir_name, packages_dir):
        new_dirs = os.path.join(mutants_dir, subject_name, operator_dir_name, packages_dir)
        if os.path.exists(new_dirs):
            shutil.rmtree(new_dirs)
        shutil.copytree(os.path.join(src_dir, operator_dir_name), new_dirs)

    print("Setting up mujava...")
    result_dir = os.path.join(mujava_home, "result")
            
    for subject_dir_name in os.listdir(result_dir):
        packages = subject_dir_name.split(".")[0:-1]
        packages_dir = utils.get_package_dir(packages)
        subject_dir = os.path.join(result_dir, subject_dir_name)
        class_mutant_dir = os.path.join(subject_dir, "class_mutants")
        traditional_mutant_dir = os.path.join(subject_dir, "traditional_mutants")
        
        for operator_dir_name in os.listdir(class_mutant_dir):
            if not os.path.isdir(os.path.join(class_mutant_dir,operator_dir_name)):
                continue
            mk_and_cp_operator_mutant_dir(class_mutant_dir, mutants_dir, subject_dir_name, operator_dir_name, packages_dir)
        
        for method_dir_name in os.listdir(traditional_mutant_dir):
            method_dir = os.path.join(traditional_mutant_dir, method_dir_name)
            if not os.path.isdir(method_dir):
                continue
            for operator_dir_name in os.listdir(method_dir):
                if not os.path.isdir(os.path.join(method_dir, operator_dir_name)):
                    continue
                mk_and_cp_operator_mutant_dir(method_dir, mutants_dir, subject_dir_name, operator_dir_name, packages_dir)
        
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mutants_dir", help="Directorio donde estan los mutantes")
    #C:\Users\JGodoy\workspace-epa\epatesting\mutants
    parser.add_argument("mujava_home", help="Directorio donde estan los mutantes")
    #C:\Users\JGodoy\Documents\MuJava
    parser.add_argument("orig_class_bin_name", help="Path al archivo .class original")
    #workspace-epa/evosuite-subjects/workdir/socket/original
    parser.add_argument("test_suite_bin", help="Path al archivo .class original del test suite")
    #C:\Users\JGodoy\workspace-epa\evosuite-subjects\workdir\socket\test
    parser.add_argument("test_suite_name", help="Nombre del test suite")
    #TestSocket
    parser.add_argument("junit_path", help="Path a junit.jar")
    #C:\Users\JGodoy\Documents\MuJava\junit.jar
    parser.add_argument("hamcrest_jar", help="Path a hamcrest_jar.jar")
    #C:\Users\JGodoy\Documents\MuJava\org.hamcrest.core_1.3.0.v201303031735.jar
    args = parser.parse_args()
    
    setup_mujava(args.mujava_home, args.mutants_dir)
    
    mujava = MuJava(args.mutants_dir, args.orig_class_bin_name, args.test_suite_bin, args.test_suite_name, args.junit_path, args.hamcrest_jar, args.mutants_dir)
    mujava.compute_mutation_score()
    
    print("Done!")
                
    