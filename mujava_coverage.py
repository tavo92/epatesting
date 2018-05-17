import argparse
import os
import subprocess
import re
import shutil
import utils

class MuJava:
    
    def __init__(self, mujava_home, dir_mutants, orig_class_bin_dir, test_suite_bin, test_suite_name, junit_path, hamcrest_path, output_dir):
        self.mujava_home = mujava_home
        self.dir_mutants = dir_mutants
        self.orig_class_bin_dir = orig_class_bin_dir
        self.test_suite_bin = test_suite_bin
        self.test_suite_name = test_suite_name + "_ESTest"
        self.junit_path = junit_path
        self.hamcrest_jar = hamcrest_path
        self.output_dir = output_dir
        self.running_cmd = ""
        
    def compute_mutation_score(self):
        def execute_testsuite(class_dir, testsuite_name, output_dir, id_name):
            def read_results(result):
                def get_line_with_test_results(result):
                    with open(result) as f:
                        content = f.readlines()
                    last_line = ""
                    for line in content:
                        if re.match(r'^\s*$', line):#line empty
                            continue
                        else:
                            last_line = line
                    return last_line
                
                def get_total_and_failures(line):
                    def all_test_ok(line):
                        return "OK" in line
                    
                    if all_test_ok(line):
                        return [[int(s) for s in line.replace("(","").split(" ") if s.isdigit()][0], 0]
                    ret = [int(s) for s in line.replace(",","").replace("\n","").split(" ") if s.isdigit()]
                    return ret
                
                last_line = get_line_with_test_results(result)
                total, failure = get_total_and_failures(last_line)
                return [total, failure]

            sep = os.path.pathsep
            output_dir = os.path.join(output_dir, "junit_results")
            utils.make_dirs_if_not_exist(output_dir)
            junit_log_name = id_name + "_junit_out.txt"
            junit_log_error_name = id_name + "_junit_err.txt"
            command_junit = "java -cp {}{}{}{}{}{}{} org.junit.runner.JUnitCore {} > {}{}{} 2> {}{}{}".format(self.junit_path, sep, self.hamcrest_jar, sep, class_dir, sep, self.test_suite_bin, testsuite_name, output_dir, os.path.sep, junit_log_name, output_dir, os.path.sep, junit_log_error_name)
            self.running_cmd += "\nRunning: {}".format(command_junit)
            try:
                subprocess.check_output(command_junit, shell=True)
            except:
                None
            ret = read_results("{}{}{}".format(output_dir, os.path.sep, junit_log_name))
            self.running_cmd += "\n\tResults: {}{} , Total: {} - Failure: {}\n".format(output_dir, junit_log_name, ret[0], ret[1])
            return ret
        
        def load_mutants_err_prot(file):
            with open(file) as f:
                content = f.readlines()
            err_prot_mutant_list = []
            for line in content:
                err_prot_mutant_list.append(line.replace("\n", ""))
            return err_prot_mutant_list
        
        def check_alive(self, class_dir, curr_mutant):
            cp_mutant = "{}{}{}".format(class_dir, os.path.pathsep, self.orig_class_bin_dir)
            mutant = execute_testsuite(cp_mutant, self.test_suite_name, self.output_dir, curr_mutant)
            return original[0] == mutant[0] and original[1] == mutant[1]
        
        def check_empty_dir(mutant_dir):
            for dirpath, dirnames, files in os.walk(mutant_dir):
                if os.listdir(dirpath) == []:
                        print("ERROR! MUTANT DIR: {} must not be empty! Check it!".format(mutant_dir))
                        exit(1)
                        
        def save_report_mujava(total, killed, err_prot_killed, err_prot, err_no_prot):
            save_report = "echo TOTAL,KILLED,MUTATION_COVERAGE,ERRPROTTOT,ERRPROT,ERRNOPROT> {}{}mujava_report.csv".format(self.output_dir, os.path.sep)
            subprocess.check_output(save_report, shell=True)
            save_report = "echo {},{},{},{},{},{} >> {}{}mujava_report.csv".format(total, killed, killed/total, err_prot_killed, err_prot, err_no_prot, self.output_dir, os.path.sep)
            subprocess.check_output(save_report, shell=True)
        
        def save_run_info(total, killed, err_prot_killed, err_no_prot):
            utils.save_file(os.path.join(self.output_dir, "running_info.txt"), self.running_cmd)
            extra_info = "\nTotal: {} - Killed: {} - coverage: {} - error_prot_killed: {} - Err prot: {} - Err NO prot: {}\n".format(total, killed, killed/total, err_prot_killed, err_prot, err_no_prot)
            extra_info += "Errores detectados pero que no son de protocolo {}------------------------\n".format(len(err_no_prot_list))
            i = 0
            for __ in err_no_prot_list:
                extra_info += "\n" + err_no_prot_list[i]
                i += 1
            extra_info += "\n\n\n\n"
            extra_info += "Mutantes sobrevivientes pero clasificados como de protocolo {}------------------------\n".format(len(no_error_list))
            i = 0
            for __ in no_error_list:
                extra_info += "\n" + no_error_list[i]
                i += 1
            utils.save_file(os.path.join(self.output_dir, "extra_info.txt"), extra_info)


# Prepare mujava mutants structure for future mutation score analysis

        print("Running mutation score...")
        utils.remove_and_make_dirs(self.output_dir)
        original = execute_testsuite(self.orig_class_bin_dir, self.test_suite_name, self.output_dir, "original")
        self.running_cmd += "\nORIGINAL <-------------------------------------------------------------------------------------------\n\n"
        total = 0; killed = 0; err_prot_killed = 0; err_no_prot = 0
        err_no_prot_list = []; no_error_list = []
        curr_subject = self.test_suite_name.replace("_ESTest","")
        curr_subject_dir = os.path.join(self.dir_mutants, curr_subject)
        mutant_subject_dir = os.path.join(self.mujava_home, "result", curr_subject, "err_prot_list.txt")
        err_prot_mutant_list = load_mutants_err_prot(mutant_subject_dir)
        for curr_mutant in os.listdir(curr_subject_dir):
            curr_mutant_dir = os.path.join(curr_subject_dir, curr_mutant)
            # only check dirs
            if not os.path.isdir(curr_mutant_dir):
                continue
            check_empty_dir(curr_mutant_dir)
            is_killed = not check_alive(self, curr_mutant_dir, curr_mutant)
            if(is_killed):
                killed += 1
                if curr_mutant in err_prot_mutant_list:
                    err_prot_killed += 1
                else:
                    err_no_prot += 1
                    err_no_prot_list.append(curr_mutant + ": " + os.path.join(self.output_dir, curr_mutant))
            else:
                if curr_mutant in err_prot_mutant_list:
                    no_error_list.append(curr_mutant + ": " + os.path.join(self.output_dir, curr_mutant))
                
            total += 1
        if total == 0:
            print("\tNo generated mutants for: {} subject".format(curr_subject))
            exit(1)
        err_prot = err_prot_killed / len(err_prot_mutant_list)
        save_report_mujava(total, killed, err_prot_killed, err_prot, err_no_prot)
        save_run_info(total, killed, err_prot_killed, err_no_prot)
        

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
    parser.add_argument("output_dir", help="Output dir to save info")
    args = parser.parse_args()
    
    setup_mujava(args.mujava_home, args.mutants_dir)
    mujava = MuJava(args.mutants_dir, args.orig_class_bin_name, args.test_suite_bin, args.test_suite_name, args.junit_path, args.hamcrest_jar, args.mutants_dir)
    mujava.compute_mutation_score()
    print("Done!")