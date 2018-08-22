import argparse
import csv

class Mutant_result:
    def __init__(self):
        self.survived = 0
        self.no_coverage = 0
        self.killed = 0
    
    def get_survived(self):
        return self.survived
    def get_nocoverage(self):
        return self.no_coverage
    def get_killed(self):
        return self.killed
    
    def add_survived(self):
        self.survived += 1
    def add_nocoverage(self):
        self.no_coverage += 1
    def add_killed(self):
        self.killed += 1

    def add_result(self, mutant_result):
        if("SURVIVED" == mutant_result):
            self.add_survived()
        if("NO_COVERAGE" == mutant_result):
            self.add_nocoverage()
        if("KILLED" == mutant_result):
            self.add_killed()

mutants_histogram = {}

def get_key(subject, criterion, budget, conditionstopping, mutant):
    return "{} {} {} {} {}".format(subject, criterion, budget, conditionstopping, mutant)

def count_mutant(subject, criterion, budget, stopping_condition, mutant, result):
    try:
        global mutants_histogram
        mutant_name_key = get_key(subject, criterion, budget, stopping_condition, mutant)
        if not mutant_name_key in mutants_histogram:
            mutant_result = Mutant_result()
        else:
            mutant_result = mutants_histogram[mutant_name_key]
        
        mutant_result.add_result(result)
        value = mutant_result
        mutants_histogram.update({mutant_name_key:value})
    except:
            print("ERROR! Adding mutant {}".format(mutant_name_key))

def pit_mutants_histogram(criterion, budget, stopping_condition, mutations_csv_path):
    #file = csv.DictReader(open(mutations_csv_path), newline='', )
    with open(mutations_csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=['NAME','SUBJECT','MUTANT_NAME','METHOD','LINE','RESULT','TEST'])
        keys_by_file = set()
        for row in reader:
            subject = row["SUBJECT"]
            mutant_key = row["MUTANT_NAME"]+"_"+row["METHOD"]+"_"+row["LINE"]
            result = row["RESULT"]
            if mutant_key not in keys_by_file:
                count_mutant(subject, criterion, budget, stopping_condition, mutant_key, result)
                keys_by_file.add(mutant_key)

def get_histogram():
    global mutants_histogram
    ret = "SUBJECT,CRITERION,BUDGET,STOP_COND,MUTANT_METHOD_LINE,SURVIVED,NO_COVERAGE,KILLED,ALIVE(SURVIVED+NO_COVERAGE)"
    for key in mutants_histogram.keys():
        key_value = key.split(" ")
        subject = key_value[0]
        criterion = key_value[1]
        budget = key_value[2]
        stopping_condition = key_value[3]
        mutant = key_value[4]
        value = mutants_histogram[key]
        survived = value.get_survived()
        no_coverage = value.get_nocoverage()
        killed = value.get_killed()
        alive = survived + no_coverage
        ret += "\n{},{},{},{},{},{},{},{},{} ".format(subject, criterion, budget, stopping_condition, mutant, survived, no_coverage, killed, alive)
    return ret

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mutations_csv", help="mutations.csv file generated by pit")
    args = parser.parse_args()
    pit_mutants_histogram("epaadjacentedges", "600", "maxtime", args.mutations_csv)
    print(get_histogram())
    print("Done!")