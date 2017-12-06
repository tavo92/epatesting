import csv

def read_evosuite_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            coverage = row['Coverage']
    return coverage

def read_jacoco_csv(name, file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            class_name = row['CLASS']
            if class_name == name:
                branch_missed = float(row['BRANCH_MISSED'])
                branch_covered = float(row['BRANCH_COVERED'])
                line_missed = float(row['LINE_MISSED'])
                line_covered = float(row['LINE_COVERED'])
                return branch_covered/(branch_missed+branch_covered), line_covered/(line_missed+line_covered)
    return coverage

def read_pit_csv(file_path):
    killed = 0
    total = 0
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            total += 1
            if row[5] == 'KILLED':
                killed += 1
    return killed/total

def report_resume_row(name, code_type, evosuite, jacoco, pit):
    epa_coverage = read_evosuite_csv(evosuite)
    branch_coverage, line_coverage = read_jacoco_csv(name, jacoco)
    mutation_coverage = read_pit_csv(pit)
    return {'Class': name, 'Type': code_type, 'EPA Coverage': epa_coverage, 'Branch Coverage': branch_coverage, 'Line Coverage': line_coverage, 'Mutation Coverage': mutation_coverage}

def make_report_resume(name, original_evosuite, original_jacoco, original_pit, instrumented_evosuite, instrumented_jacoco, instrumented_pit, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Class', 'Type', 'EPA Coverage', 'Branch Coverage', 'Line Coverage', 'Mutation Coverage']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow(report_resume_row(name, 'Original', original_evosuite, original_jacoco, original_pit))
        writer.writerow(report_resume_row(name, 'Instrumented', instrumented_evosuite, instrumented_jacoco, instrumented_pit))