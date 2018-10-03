import subprocess
import csv
import argparse
import os 


def generate_latex_table(r_results_file, output):
    def get_rows_columns_size(r_results_file):
        with open(r_results_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return len(reader.fieldnames)

    if not os.path.exists(r_results_file):
        print("generate_latex_table: Does not exits file (r_results_file): {}".format(r_results_file))
        return
    i = 0
    rows_size = get_rows_columns_size(r_results_file)
    tabular_desc = "|"
    while i < rows_size:
        tabular_desc += "l|"
        i += 1
    declaration_init = "% Please add the following required packages to your document preamble:\n% \\usepackage{multirow}\n"
    declaration_init += "\\begin{table}[]\n"
    declaration_init += "\\caption{Insert here description}\label{summary-table}\n"
    declaration_init += "\\begin{tabular}{" + "{}".format(tabular_desc)+"}"
    declaration_init += "\n\\hline"
    header = ""
    subheader = ""
    with open(r_results_file, "r") as results:
        lines = []
        i = 0
        for line in results:
            line = line.replace("_", "\_")
            if i == 0:
                firstLine = line.split(",")
                i += 1
                continue
            if i == 1:
                secondLine = line.split(",")
                j = 0
                while j < len(firstLine):
                    curr_first_line_header = firstLine[j].strip()
                    curr_second_line_header = secondLine[j].strip()
                    if curr_second_line_header == curr_first_line_header:
                        header += "\multirow{2}{*}"
                        header += "{}".format("{"+curr_second_line_header+"}")
                        subheader += " & "
                        j += 1
                        continue
                    elif j+1 < len(firstLine) and firstLine[j].strip() == firstLine[j+1].strip():
                        header += " & \multicolumn{2}{l|}"
                        header += "{}".format("{"+firstLine[j+1].strip()+"}")
                    subheader += curr_second_line_header
                    if not j == len(firstLine)-1:
                        subheader += " & "
                    j += 1
                header += " \\\\ \\cline{2-"+"{}".format(rows_size)+"}"
                subheader += "\\\\ \\hline"
            else:
                curr_line = line.replace(",", " &")
                curr_line = curr_line.replace("\n", "")
                curr_line += " \\\\ \\hline"
                lines.append(curr_line)
            i += 1

    content = ""
    for __ in lines:
        content += __ + "\n"
    declaration_end = "{}\n{}".format("\end{tabular}", "\end{table}")
    
    table = declaration_init
    table += header + "\n"
    table += subheader + "\n"
    table += content
    table += declaration_end
    # Save file
    file = open(output,"w")
    file.write(table)
    file.close()


def generate_r_results(r_executable_path, script_r_path, file_path, criterios_list, output):
    def get_all_criterios_in_file(file_path):
        criterios = []
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not row['TOOL'] in criterios:
                    criterios.append(row['TOOL'])
        return criterios
    
    def exists_criterion_in_file(file_path, criterion):
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['TOOL'] == criterion:
                    return True
        return False
    
    def exists_default_criterion(file_path):
        return exists_criterion_in_file(file_path, "line_branch_exception")

    if not os.path.exists(r_executable_path):
        print("generate_r_results: Does not exists file (r_executable_path): {}".format(r_executable_path))
        return
    if not os.path.exists(script_r_path):
        print("generate_r_results: Does not exists file (script_r_path): {}".format(script_r_path))
        return
    if not os.path.exists(file_path):
        print("generate_r_results: Does not exists file (file_path): {}".format(file_path))
        return

    criterios = ""
    if criterios_list[0] == "ALL":
        criterios_list = get_all_criterios_in_file(file_path)
        
    i = 0
    while i < len(criterios_list):
        curr_criterion = criterios_list[i].strip()
        if not exists_default_criterion(file_path):
            print("Does not exists criterion 'line_branch_exception' in all_resumes file. You need it for compare results!")
            return
        if not exists_criterion_in_file(file_path, curr_criterion):
            print("Does not exists criterion '{}' in all_resumes file. Check it!".format(curr_criterion))
            return
        criterios += "\"{}\" ".format(curr_criterion)
        i += 1
    command = "\"{}\" \"{}\" \"{}\" {} > {} 2> {}".format(r_executable_path, script_r_path, file_path, criterios, output, output+".err")
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
    generate_latex_table(args.output_csv, args.output_tex)
    print("Done!")