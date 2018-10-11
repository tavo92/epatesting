import csv

header_names = ['ID', 'BUG_TYPE', 'STOP_COND', 'BUD', 'SUBJ',
                'TOOL', 'LINE', 'BRNCH', 'EPACOV', 'EPA',
                'EPATOT', 'EXCEPCOV', 'EXCEP', 'EXCEPTOT', 'ADJACCOV',
                'ADJAC', 'ADJACTOT', 'ERR', 'NERR', 'TERR',
                'MUT', 'TIME', 'LOC', 'PIMUT', 'ERRF',
                'MJMUT', 'MUT_KILLED', 'ERRPROT_KILLED', 'GENS', 'TOT_TIME']

def write_row(writer, row):
    writer.writerow({'ID': row[0], 'BUG_TYPE': row[1], 'STOP_COND': row[2], 'BUD': row[3], 'SUBJ': row[4],
                     'TOOL': row[5], 'LINE': row[6], 'BRNCH': row[7], 'EPACOV': row[8], 'EPA': row[9],
                     'EPATOT': row[10], 'EXCEPCOV': row[11], 'EXCEP': row[12], 'EXCEPTOT': row[13], 'ADJACCOV': row[14],
                     'ADJAC': row[15], 'ADJACTOT': row[16], 'ERR': row[17], 'NERR': row[18], 'TERR': row[19],
                     'MUT': row[20], 'TIME': row[21], 'LOC': row[22], 'PIMUT': row[23], 'ERRF': row[24],
                     'MJMUT': row[25], 'MUT_KILLED': row[26], 'ERRPROT_KILLED': row[27], 'GENS': row[28], 'TOT_TIME': row[29]});

def get_complete_row(row):
    return [row[0], row[1], row[2], row[3], row[4],
            row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12], row[13], row[14],
            row[15], row[16], 'N/A', 'N/A', 'N/A',
            'N/A', 'N/A', 'N/A', row[17], 'N/A',
            row[18], row[19], row[20], row[21], row[22]]

def read_evosuite_csv(file_path):
    epatransition_coverage = 'N/A'
    epatransition_covered = 'N/A'
    epatransition_tot = 'N/A'
    epaexception_coverage = 'N/A'
    epaexception_covered = 'N/A'
    epaexception_tot = 'N/A'
    epaadjacentedges_coverage = 'N/A'
    epaadjacentedges_covered = 'N/A'
    epaadjacentedges_tot = 'N/A'
    
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'EPATRANSITION' == row['criterion']:
                epatransition_coverage = row['Coverage']
                epatransition_covered = row['Covered_Goals']
                epatransition_tot = row['Total_Goals']
            if 'EPAEXCEPTION' == row['criterion']:
                epaexception_coverage = row['Coverage']
                epaexception_covered = row['Covered_Goals']
                epaexception_tot = row['Total_Goals']
            if 'EPAADJACENTEDGES' == row['criterion']:
                epaadjacentedges_coverage = row['Coverage']
                epaadjacentedges_covered = row['Covered_Goals']
                epaadjacentedges_tot = row['Total_Goals']
    return epatransition_coverage, epatransition_covered, epatransition_tot, epaexception_coverage, epaexception_covered, epaexception_tot, epaadjacentedges_coverage, epaadjacentedges_covered, epaadjacentedges_tot

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
    mujava_coverage = 'N/A'
    mutants_killed = 'N/A'
    err_prot_killed = 'N/A'
    try:
        with open(mujava_csv, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                mutants_killed = row[1]
                mujava_coverage = row[2]
                err_prot_killed = row[4]
    except:
        print("File {} doesn't exists".format(mujava_csv))
    return mujava_coverage, mutants_killed, err_prot_killed


def report_resume_row(target_class, evosuite, statistics_testgen, jacoco, pit, runid, bug_type, stopping_condition, search_budget, criterion, mujava_csv):
    epa_coverage, epa_covered, epa_tot, epaex_coverage, epaex_covered, epaex_tot, edges_coverage, edges_covered, edges_tot = read_evosuite_csv(evosuite)
    generations_test, total_time_test = read_generations_csv(statistics_testgen)
    branch_coverage, line_coverage = read_jacoco_csv(target_class, jacoco)
    mutation_coverage = read_pit_csv(pit)
    mujava_coverage, mutants_killed, err_prot_killed = read_mujava_coverage_csv(mujava_csv)
    row = [runid, bug_type, stopping_condition, search_budget, target_class,
           criterion, line_coverage, branch_coverage, epa_coverage, epa_covered,
           epa_tot, epaex_coverage, epaex_covered, epaex_tot, edges_coverage,
           edges_covered, edges_tot, mutation_coverage, mujava_coverage, mutants_killed,
           err_prot_killed, generations_test, total_time_test]
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