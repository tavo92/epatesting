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
        tabular_desc += "c|"
        i += 1
    declaration_init = "% Please add the following required packages to your document preamble:\n% \\usepackage{multirow}\n"
    declaration_init += "\\begin{table*}[t]\n"
    declaration_init += "\\center\n"
    declaration_init += "\\caption{Insert here description}\label{summary-table}\n"
    declaration_init += "\\begin{tabular}{" + "{}".format(tabular_desc)+"}"
    declaration_init += "\n\\hline"
    header = ""
    subheader = ""
    with open(r_results_file, "r") as results:
        lines = []
        i = 0
        p_values_index = []
        for line in results:
            line = line.replace("_", "\_")
            if i == 0:
                firstLine = line.split(",")
                i += 1
                continue
            if i == 1:
                secondLine = line.split(",")
                j = 0
                for __ in secondLine:
                    if "p-value" in __:
                        p_values_index.append(j)
                    j += 1
                    
                j = 0
                while j < len(firstLine):
                    curr_first_line_header = firstLine[j].strip()
                    curr_second_line_header = secondLine[j].strip()
                    #Celda de doble fila
                    if curr_second_line_header == curr_first_line_header:
                        header += "\multirow{2}{*}"
                        header += "{}".format("{"+curr_second_line_header+"}")
                        subheader += " & "
                        j += 1
                        continue
                    #Celda de doble columna
                    elif j+1 < len(firstLine) and firstLine[j].strip() == firstLine[j+1].strip():
                        header += " & \multicolumn{2}{c|}"
                        header += "{}".format("{"+firstLine[j+1].strip()+"}")
                    subheader += curr_second_line_header
                    if not j == len(firstLine)-1:
                        subheader += " & "
                    j += 1
                header += " \\\\ \\cline{2-"+"{}".format(rows_size)+"}"
                subheader += "\\\\ \\hline"
            else:
                line = line.replace("\n", "")
                columns_fields = line.split(",")
                i = 0
                previous_field = ""
                for __ in columns_fields:
                    if i in p_values_index:
                        if "< 0.05" in __ or "< 0.005" in __:
                            previous_field = "\\textbf{"+previous_field+"}"
                            curr_field = __.replace("<", "\\textless{ ")
                            curr_field += "}"
                            columns_fields[i-1] = previous_field
                            columns_fields[i] = curr_field
                        #final_line += final_line + " & " + previous_field + " & " + curr_field 
                    previous_field = __
                    i += 1
                #line = line.replace("< 0.05", "\\textless{ 0.05}")
                #line = line.replace("< 0.005", "\\textless{ 0.005}")
                #curr_line = line.replace(",", " &")
                final_line = ""
                first = True
                for __ in columns_fields:
                    if first:
                        final_line = __
                        first = False
                        continue
                    final_line += " & " + __
                final_line += " \\\\ \\hline"
                lines.append(final_line)
            i += 1

    content = ""
    for __ in lines:
        content += __ + "\n"
    declaration_end = "{}\n{}".format("\end{tabular}", "\end{table*}")
    
    table = declaration_init
    table += header + "\n"
    table += subheader + "\n"
    table += content
    table += declaration_end
    # Save file
    file = open(output,"w")
    file.write(table)
    file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", help="input_csv")
    parser.add_argument("output_tex", help="output.tex")
    args = parser.parse_args()
    generate_latex_table(args.input_csv, args.output_tex)
    print("Done!")