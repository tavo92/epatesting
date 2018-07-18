import csv

header_names = ['ID', 'BUG_TYPE', 'STOP_COND', 'BUD', 'SUBJ', 'TOOL', 'LINE', 'BRNCH', 'EPA', 'EXCEP', 'EXCEPTOT', 'ADJAC', 'ADJACTOT', 'ERR',
                'NERR', 'TERR', 'MUT', 'TIME', 'LOC', 'PIMUT', 'ERRF', 'MJMUT', 'MUT_KILLED', 'ERRPROT_KILLED', 'GENS', 'TOT_TIME']

def write_row(writer, row):
    writer.writerow({'ID': row[0], 'BUG_TYPE': row[1], 'STOP_COND': row[2], 'BUD': row[3], 'SUBJ': row[4], 'TOOL': row[5], 'LINE': row[6],
                     'BRNCH': row[7], 'EPA': row[8], 'EXCEP': row[9], 'EXCEPTOT': row[10], 'ADJAC': row[11], 'ADJACTOT': row[12],
                     'ERR': row[13], 'NERR': row[14], 'TERR': row[15], 'MUT': row[16], 'TIME': row[17], 'LOC': row[18], 'PIMUT': row[19],
                     'ERRF': row[20], 'MJMUT': row[21], 'MUT_KILLED': row[22], 'ERRPROT_KILLED': row[23], 'GENS': row[24],
                     'TOT_TIME': row[25]});

def get_complete_row(row):
    return [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', row[13],
            'N/A', row[14], row[15], row[16], row[17], row[18]]

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
    total_time = 'N/A'
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            generations = row['Generations']
            total_time = int(row['Total_Time'])/1000

    return generations, total_time


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
    mujava_coverage = 0.0
    mutants_killed = 0
    err_prot_killed = 0.0
    with open(mujava_csv, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            mutants_killed = row[1]
            mujava_coverage = row[2]
            err_prot_killed = row[4]
    return mujava_coverage, mutants_killed, err_prot_killed


def report_resume_row(target_class, evosuite, statistics_testgen, jacoco, pit, runid, bug_type, stopping_condition, search_budget, criterion, mujava_csv):
    epa_coverage, epa_exception, epa_exception_tot, epaadjacentedges, epaadjacentedges_tot = read_evosuite_csv(evosuite)
    generations_test, total_time_test = read_generations_csv(statistics_testgen)
    branch_coverage, line_coverage = read_jacoco_csv(target_class, jacoco)
    mutation_coverage = read_pit_csv(pit)
    mujava_coverage, mutants_killed, err_prot_killed = read_mujava_coverage_csv(mujava_csv)
    row = [runid, bug_type, stopping_condition, search_budget, target_class, criterion, line_coverage, branch_coverage, epa_coverage, epa_exception,
           epa_exception_tot, epaadjacentedges, epaadjacentedges_tot, mutation_coverage, mujava_coverage, mutants_killed, err_prot_killed,
           generations_test, total_time_test]
    return row


def make_report_resume(target_class, evosuite, statistics_testgen, jacoco, pit, output_file, runid, stopping_condition, search_budget, criterion, bug_type, mujava_csv):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header_names)

        writer.writeheader()
        row = report_resume_row(target_class, evosuite, statistics_testgen, jacoco, pit, runid, bug_type, stopping_condition, search_budget, criterion, mujava_csv)
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