import csv

header_names = ['ID', 'STOP_COND', 'BUD', 'SUBJ', 'TOOL', 'LINE', 'BRNCH', 'EPA', 'EXCEP', 'EXCEPTOT', 'ADJAC', 'ADJACTOT', 'ERR', 'NERR', 'TERR', 'MUT', 'TIME', 'LOC', 'PIMUT', 'ERRF', 'MJMUT', 'ERRPROTKILLED', 'ERRPROT', 'ERRNOPROT', 'GENS']

def write_row(writer, row):
    writer.writerow({'ID': row[0], 'STOP_COND': row[1], 'BUD': row[2], 'SUBJ': row[3], 'TOOL': row[4], 'LINE': row[5], 'BRNCH': row[6],
                     'EPA': row[7], 'EXCEP': row[8], 'EXCEPTOT': row[9], 'ADJAC': row[10], 'ADJACTOT': row[11], 'ERR': row[12], 'NERR': row[13],
                     'TERR': row[14], 'MUT': row[15], 'TIME': row[16], 'LOC': row[17], 'PIMUT': row[18], 'ERRF': row[19], 'MJMUT': row[20],
                     'ERRPROTKILLED': row[21], 'ERRPROT': row[22], 'ERRNOPROT': row[23], 'GENS': row[24]});

def get_complete_row(row):
    return [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', row[12],
            'N/A', row[13], row[14], row[15], row[16], row[17]]

def read_evosuite_csv(file_path):
    epatransition = 'N/A'
    epaexception = 'N/A'
    epaexception_tot = 'N/A'
    epaadjacentedges = 'N/A'
    epaadjacentedges_tot = 'N/A'
    
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'EPATRANSITION' == row['criterion']:
                epatransition = row['Coverage']
            if 'EPAEXCEPTION' == row['criterion']:
                epaexception = row['Covered_Goals']
                epaexception_tot = row['Total_Goals']
            if 'EPAADJACENTEDGES' == row['criterion']:
                epaadjacentedges = row['Covered_Goals']
                epaadjacentedges_tot = row['Total_Goals']
    return epatransition, epaexception, epaexception_tot, epaadjacentedges, epaadjacentedges_tot

def read_generations_csv(file_path):
    generations = 'N/A'
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            generations = row['Generations']

    return generations


def read_jacoco_csv(target_class, file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            package_name = row['PACKAGE']
            class_name = row['CLASS']
            if package_name.strip() != "":
                fully_qualified_class_name = "{}.{}".format(package_name, class_name)
            else:
                fully_qualified_class_name = class_name
                
            if fully_qualified_class_name == target_class:
                branch_missed = float(row['BRANCH_MISSED'])
                branch_covered = float(row['BRANCH_COVERED'])
                line_missed = float(row['LINE_MISSED'])
                line_covered = float(row['LINE_COVERED'])
                return branch_covered / (branch_missed + branch_covered), line_covered / (line_missed + line_covered)
    return 0, 0


def read_pit_csv(file_path):
    killed = 0
    total = 0
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            total += 1
            if row[5] == 'KILLED':
                killed += 1
    return killed / total

def read_mujava_coverage_csv(mujava_csv):
    coverage = 0.0
    err_prot_total = 0
    err_prot = 0.0
    err_no_prot_total = 0
    with open(mujava_csv, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            coverage = row[2]
            err_prot_total = row[3]
            err_prot = row[4]
            err_no_prot_total = row[5]
    return coverage, err_prot_total, err_prot, err_no_prot_total.strip()


def report_resume_row(target_class, evosuite, generations, jacoco, pit, runid, stopping_condition, search_budget, criterion, mujava_csv):
    epa_coverage, epa_exception, epa_exception_tot, epaadjacentedges, epaadjacentedges_tot = read_evosuite_csv(evosuite)
    generations_test = read_generations_csv(generations)
    branch_coverage, line_coverage = read_jacoco_csv(target_class, jacoco)
    mutation_coverage = read_pit_csv(pit)
    mujava_coverage, err_prot_killed, err_prot, err_no_prot_killed = read_mujava_coverage_csv(mujava_csv)
    row = [runid, stopping_condition, search_budget, target_class, criterion, line_coverage, branch_coverage, epa_coverage, epa_exception, epa_exception_tot, epaadjacentedges, epaadjacentedges_tot, mutation_coverage, mujava_coverage, err_prot_killed, err_prot, err_no_prot_killed, generations_test]
    return row


def make_report_resume(target_class, evosuite, generations, jacoco, pit, output_file, runid, stopping_condition, search_budget, criterion, mujava_csv):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header_names)

        writer.writeheader()
        row = report_resume_row(target_class, evosuite, generations, jacoco, pit, runid, stopping_condition, search_budget, criterion, mujava_csv)
        row = get_complete_row(row)
        write_row(writer, row)


def merge_all_resumes(all_resumes, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header_names)
        writer.writeheader()

        for resume in all_resumes:
            try:
                with open(resume, newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader) # Evito el header
                    for row in reader:
                        write_row(writer, row)
            except FileNotFoundError:
                print("{} doesn't exists".format(resume))