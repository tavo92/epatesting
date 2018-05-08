import csv

header_names = ['ID', 'BUD', 'SUBJ', 'TOOL', 'LINE', 'BRNCH', 'EPA', 'ERR', 'NERR', 'TERR', 'MUT', 'TIME', 'LOC', 'PIMUT', 'ERRF', 'MJMUT', 'ERRPROTKILLED', 'ERRPROT', 'ERRNOPROT']

def write_row(writer, row):
    writer.writerow({'ID': row[0], 'BUD': row[1], 'SUBJ': row[2], 'TOOL': row[3], 'LINE': row[4], 'BRNCH': row[5], 'EPA': row[6], 'ERR': row[7],
                     'NERR': row[8], 'TERR': row[9], 'MUT': row[10], 'TIME': row[11], 'LOC': row[12], 'PIMUT': row[13], 'ERRF': row[14], 'MJMUT': row[15], 'ERRPROTKILLED': row[16], 'ERRPROT': row[17], 'ERRNOPROT': row[18]});
                     
def get_complete_row(row):
    return [row[0], row[1], row[2], row[3], row[4], row[5], row[6], 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', row[7], 'N/A', row[8], row[9], row[10], row[11]]

def read_evosuite_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            coverage = row['Coverage']
    return coverage


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
    return coverage, err_prot_total, err_prot, err_no_prot_total


def report_resume_row(target_class, evosuite, jacoco, pit, runid, search_budget, criterion, mujava_csv):
    epa_coverage = read_evosuite_csv(evosuite)
    branch_coverage, line_coverage = read_jacoco_csv(target_class, jacoco)
    mutation_coverage = read_pit_csv(pit)
    mujava_coverage, err_prot_killed, err_prot, err_no_prot_killed = read_mujava_coverage_csv(mujava_csv)
    row = [runid, search_budget, target_class, criterion, line_coverage, branch_coverage, epa_coverage, mutation_coverage, mujava_coverage, err_prot_killed, err_prot, err_no_prot_killed]
    return row


def make_report_resume(target_class, evosuite, jacoco, pit, output_file, runid, search_budget, criterion, mujava_csv):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header_names)

        writer.writeheader()
        row = report_resume_row(target_class, evosuite, jacoco, pit, runid, search_budget, criterion, mujava_csv)
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