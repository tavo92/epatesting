import argparse
import os
import subprocess
import re

class MuJava:
    
    #def create_mutants(self, class_name, output_dir):
    def __init__(self, dir_mutants, orig_class_bin_dir, test_suite_bin, test_suite_name, junit_path, hamcrest_path):
        self.dir_mutants = dir_mutants
        self.orig_class_bin_dir = orig_class_bin_dir
        self.test_suite_bin = test_suite_bin
        self.test_suite_name = test_suite_name
        self.junit_path = junit_path
        self.hamcrest_path = hamcrest_path
        
    def compute_mutation_score(self):
        
        def check_alive(self, cp_mutant):
            junit = JUnit(self.junit_path, self.hamcrest_path, self.test_suite_bin)
            original = junit.execute_testsuite(self.orig_class_bin_dir, self.test_suite_name)
            mutant = junit.execute_testsuite(cp_mutant, self.test_suite_name)
            return original[0] == mutant[0] and original[1] == mutant[1]
        
        total = 0
        killed = 0
        for curr_mutant in os.listdir(self.dir_mutants):
            curr_mutant = os.path.join(self.dir_mutants, curr_mutant)
            # only check dirs
            if not os.path.isdir(curr_mutant):
                continue
            is_killed = not check_alive(self, curr_mutant)
            if(is_killed):
                killed += 1
            total += 1
        print("total: {} - Killed: {} - coverage: {}".format(total, killed, killed/total))
        
            
class JUnit:
    
    def __init__(self, junit_path, hamcrest_path, testsuite_bin_dir):
        self.junit_path = junit_path
        self.hamcrest_path = hamcrest_path
        self.testsuite_bin_dir = testsuite_bin_dir
    
    def execute_testsuite(self, class_dir, testsuite_name):
        def read_results(result):
            
            def all_ok(line):
                return "OK" in line
            
            def get_values(line):
                if all_ok(line):
                    return [[int(s) for s in line.replace("(","").split(" ") if s.isdigit()][0], 0]
                return [int(s) for s in line.split(",") if s.isdigit()]
                
            
            with open(result) as f:
                content = f.readlines()
            last_line = ""
            for line in content:
                if re.match(r'^\s*$', line):
                    continue
                else:
                    last_line = line
            
            total = get_values(last_line)[0]
            failure = get_values(last_line)[1]
            return [total, failure]
        
        sep = os.path.pathsep
        command_junit = "java -cp {}{}{}{}{}{}{} org.junit.runner.JUnitCore {} > {}_out.txt 2> {}_err.txt".format(self.junit_path, sep, self.hamcrest_path, sep, class_dir, sep, self.testsuite_bin_dir, testsuite_name, class_dir, class_dir)
        print("Running: {}".format(command_junit))
        subprocess.check_output(command_junit, shell=True)
        return read_results("{}_out.txt".format(class_dir))
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mutants_dir", help="Directorio donde estan los mutantes")
    #C:\Users\JGodoy\workspace-epa\epatesting\mujava
    parser.add_argument("orig_class_bin_name", help="Path al archivo .class original")
    #workspace-epa/evosuite-subjects/workdir/socket/original
    parser.add_argument("test_suite_bin", help="Path al archivo .class original del test suite")
    #C:\Users\JGodoy\workspace-epa\evosuite-subjects\workdir\socket\test
    parser.add_argument("test_suite_name", help="Nombre del test suite")
    #TestSocket
    parser.add_argument("junit_path", help="Path a junit.jar")
    #C:\Users\JGodoy\Documents\MuJava\junit.jar
    parser.add_argument("hamcrest_path", help="Path a hamcrest_path.jar")
    #C:\Users\JGodoy\Documents\MuJava\org.hamcrest.core_1.3.0.v201303031735.jar
    args = parser.parse_args()
    
    mujava = MuJava(args.mutants_dir, args.orig_class_bin_name, args.test_suite_bin, args.test_suite_name, args.junit_path, args.hamcrest_path)
    mujava.compute_mutation_score()
    
    print("Done!")


                
    