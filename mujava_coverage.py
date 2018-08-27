import os
import subprocess
import re
import utils
import shutil

class MuJava:
    
    def __init__(self, bug_type, name, criterion, subdir_mutants, error_prot_list, ignore_mutant_list, orig_class_bin_dir, test_suite_bin, test_suite_name, junit_path, hamcrest_path, output_dir):
        self.bug_type = bug_type
        self.subject_name = name
        self.criterion = criterion
        self.mutants_dir = subdir_mutants
        self.error_prot_list = error_prot_list
        self.ignore_mutants_list = ignore_mutant_list
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
        
        def check_alive(self, class_dir, curr_mutant):
            cp_mutant = "{}{}{}".format(class_dir, os.path.pathsep, self.orig_class_bin_dir)
            mutant = execute_testsuite(cp_mutant, self.test_suite_name, self.output_dir, curr_mutant)
            return original[0] == mutant[0] and original[1] == mutant[1]
        
        def check_empty_dir(mutant_dir):
            for dirpath, dirnames, files in os.walk(mutant_dir):
                if os.listdir(dirpath) == []:
                        print("ERROR! MUTANT DIR: {} must not be empty! Check it!".format(mutant_dir))
                        exit(1)
                        
        def save_report_mujava(total, killed, total_errprot, killed_mutants_in_errorprot_list, err_no_prot):
            save_report = "echo TOTAL,KILLED,MUTATION_COVERAGE,TOT_ERRPROT,KILLED_ERRPROT,ERRPROT_COVERAGE,ERRNOPROT> {}{}mujava_report.csv".format(self.output_dir, os.path.sep)
            subprocess.check_output(save_report, shell=True)
            errprot_coverage = "N/A" if total_errprot == 0 else killed_mutants_in_errorprot_list/total_errprot
            save_report = "echo {},{},{},{},{},{},{} >> {}{}mujava_report.csv".format(total, killed, killed/total, total_errprot, killed_mutants_in_errorprot_list, errprot_coverage, err_no_prot, self.output_dir, os.path.sep)
            subprocess.check_output(save_report, shell=True)
        
        def save_run_info(total, killed, killed_mutants_in_errorprot_list, err_no_prot):
            utils.save_file(os.path.join(self.output_dir, "running_info.txt"), self.running_cmd)
            extra_info = "\nTotal: {} - Killed: {} - coverage: {} - error_prot_killed: {} - Err NO prot: {}\n".format(total, killed, killed/total, killed_mutants_in_errorprot_list, err_no_prot)
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


        print("Running mutation score...")
        utils.remove_and_make_dirs(self.output_dir)
        original = execute_testsuite(self.orig_class_bin_dir, self.test_suite_name, self.output_dir, "original")
        self.running_cmd += "\nORIGINAL <-------------------------------------------------------------------------------------------\n\n"
        total = 0; killed = 0; killed_mutants_in_errorprot_list = 0; err_no_prot = 0
        err_no_prot_list = []; no_error_list = []
        curr_subject = self.test_suite_name.replace("_ESTest","")
        curr_subject_dir = os.path.join(self.mutants_dir, curr_subject)
        for curr_mutant in os.listdir(curr_subject_dir):
            if curr_mutant in self.ignore_mutants_list:
                continue
            
            curr_mutant_dir = os.path.join(curr_subject_dir, curr_mutant)
            # only check dirs
            if not os.path.isdir(curr_mutant_dir):
                continue
            check_empty_dir(curr_mutant_dir)
            is_killed = not check_alive(self, curr_mutant_dir, curr_mutant)
            if(is_killed):
                killed += 1
                utils.count_mutant(self.bug_type, self.subject_name, self.criterion, curr_mutant)
                if curr_mutant in self.error_prot_list:
                    killed_mutants_in_errorprot_list += 1
                else:
                    err_no_prot += 1
                    err_no_prot_list.append(curr_mutant + ": " + os.path.join(self.output_dir, curr_mutant))
            else:
                if curr_mutant in self.error_prot_list:
                    no_error_list.append(curr_mutant + ": " + os.path.join(self.output_dir, curr_mutant))
                
            total += 1
        if total == 0:
            print("\tNo generated mutants for {}:{}".format(curr_subject, self.mutants_dir))
            exit(1)
        save_report_mujava(total, killed, len(self.error_prot_list), killed_mutants_in_errorprot_list, err_no_prot)
        save_run_info(total, killed, killed_mutants_in_errorprot_list, err_no_prot)
        
# Prepare mujava mutants structure for future mutation score analysis
def setup_mujava(origin_mutants_dir, subject_name, subdir_mutants, original_code_dir):
    def mk_and_cp_operator_mutant_dir(src_dir, subject_name, operator_dir_name, packages_dir):
        new_dirs = os.path.join(subdir_mutants, subject_name, operator_dir_name)
        new_dirs_packages = os.path.join(new_dirs, packages_dir)
        src_dir = os.path.join(src_dir, operator_dir_name)
        # si existe el directorio, ya deberia contener los .class, entonces no copio los mutantes ni compilo
        if not os.path.exists(new_dirs):
            shutil.copytree(src_dir, new_dirs_packages)
            utils.compile_workdir(new_dirs, new_dirs, new_dirs, original_code_dir)
        
    print("Setting up mujava...")
    packages = subject_name.split(".")[0:-1]
    packages_dir = utils.get_package_dir(packages)
    class_mutant_dir = os.path.join(origin_mutants_dir, "class_mutants")
    traditional_mutant_dir = os.path.join(origin_mutants_dir, "traditional_mutants")
    
    for operator_dir_name in os.listdir(class_mutant_dir):
        if not os.path.isdir(os.path.join(class_mutant_dir,operator_dir_name)):
            continue
        mk_and_cp_operator_mutant_dir(class_mutant_dir, subject_name, operator_dir_name, packages_dir)
    
    for method_dir_name in os.listdir(traditional_mutant_dir):
        method_dir = os.path.join(traditional_mutant_dir, method_dir_name)
        if not os.path.isdir(method_dir):
            continue
        for operator_dir_name in os.listdir(method_dir):
            if not os.path.isdir(os.path.join(method_dir, operator_dir_name)):
                continue
            mk_and_cp_operator_mutant_dir(method_dir, subject_name, operator_dir_name, packages_dir)
    print("Mujava setup ready!")