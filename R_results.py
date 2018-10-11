import subprocess
import csv
import argparse
import os 
import Latex_table
from sys import platform

def generate_r_results(r_executable_path, script_r_path, input_path, criterios_list, output):
    def get_all_criterios_in_file(input_path):
        criterios = []
        with open(input_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not row['TOOL'] in criterios:
                    criterios.append(row['TOOL'])
        return criterios
    
    def exists_criterion_in_file(input_path, criterion):
        with open(input_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['TOOL'] == criterion:
                    return True
        return False
    
    def exists_default_criterion(input_path):
        return exists_criterion_in_file(input_path, "line_branch_exception")

    if platform == "win32" and not os.path.exists(r_executable_path):
        print("generate_r_results: Does not exists file (r_executable_path): {}".format(r_executable_path))
        return
    if not os.path.exists(script_r_path):
        print("generate_r_results: Does not exists file (script_r_path): {}".format(script_r_path))
        return
    if not os.path.exists(input_path):
        print("generate_r_results: Does not exists file (input_path): {}".format(input_path))
        return

    criterios = ""
    if criterios_list[0] == "ALL":
        criterios_list = get_all_criterios_in_file(input_path)
        
    i = 0
    while i < len(criterios_list):
        curr_criterion = criterios_list[i].strip()
        if not exists_default_criterion(input_path):
            print("Does not exists criterion 'line_branch_exception' in all_resumes file. You need it for compare results!")
            return
        if not exists_criterion_in_file(input_path, curr_criterion):
            print("Does not exists criterion '{}' in all_resumes file. Check it!".format(curr_criterion))
            return
        criterios += "\"{}\" ".format(curr_criterion)
        i += 1
    command = "\"{}\" \"{}\" \"{}\" {} > {} 2> {}".format(r_executable_path, script_r_path, input_path, criterios, output, output+".err")
    subprocess.check_output(command, shell=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("r_executable_path", help="r_executable_path")
    parser.add_argument("effect_size_pit_vs_default_script", help="effect_size_pit_vs_default.R")
    parser.add_argument("all_resumes", help="all_resumes.csv")
    parser.add_argument("criterios", help="criterios")
    parser.add_argument("output_csv", help="output.csv")
    parser.add_argument("output_tex", help="output.tex")
    args = parser.parse_args()
    generate_r_results(args.r_executable_path, args.effect_size_pit_vs_default_script, args.all_resumes, args.criterios.split(","), args.output_csv)
    Latex_table.generate_latex_table(args.output_csv, args.output_tex)
    print("Done!")