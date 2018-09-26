import argparse
import csv
import threading
import shutil
import os
import sys

class Mutant_result:
    def __init__(self):
        self.survived = 0
        self.no_coverage = 0
        self.killed = 0
        self.test = ""
    
    def get_survived(self):
        return self.survived
    def get_nocoverage(self):
        return self.no_coverage
    def get_killed(self):
        return self.killed
    def get_test(self):
        return self.test
    
    def add_survived(self):
        self.survived += 1
    def add_nocoverage(self):
        self.no_coverage += 1
    def add_killed(self):
        self.killed += 1

    def add_result_and_save_test(self, mutant_result, test_name, test_dir, pitest_dir, mutant_name, runid):
        if "SURVIVED" == mutant_result:
            self.add_survived()
        elif "NO_COVERAGE" == mutant_result:
            self.add_nocoverage()
        elif "KILLED" == mutant_result:
            self.add_killed()
            saved = save_killer_test(test_dir, pitest_dir, mutant_name, test_name)
            if not self.test and saved:
                self.test = test_name+"#{}".format(runid)

mutants_histogram = {}

def get_first_key(subject, budget, stopping_condition, mutant):
    return "{} {} {} {}".format(subject, budget, stopping_condition, mutant)

def get_second_key(criterion):
    return "{}".format(criterion)

def save_killer_test(src, dst, mutant_name, test_name):
    mutant_name = mutant_name.replace("org.pitest.mutationtest.engine.gregor.mutators.","")
    mutant_name = mutant_name.replace("<","_")
    mutant_name = mutant_name.replace(">","_")
    new_dir = os.path.join(dst, mutant_name+"#"+test_name)
    try:
        if os.path.exists(new_dir):
            shutil.rmtree(new_dir)
        shutil.copytree(src, new_dir)
    except:
        print("save_killer_test - ERROR copying '{}' to '{}'".format(src, new_dir))
        print("save_killer_test - ERROR INFO: {}, {}".format(sys.exc_info()[0], sys.exc_info()[1]))
        return False
    return True

def count_mutant(subject, criterion, budget, stopping_condition, mutant_name, result, test_name, test_dir, pitest_dir, runid):
    lock.acquire()
    try:
        global mutants_histogram
        first_key = get_first_key(subject, budget, stopping_condition, mutant_name)
        second_key = get_second_key(criterion)
        value = {} # {criterio:mutant_result}
        mutant_result = Mutant_result()
        if first_key in mutants_histogram:
            value = mutants_histogram[first_key]
            if second_key in value:
                mutant_result = value[second_key]
        
        mutant_result.add_result_and_save_test(result, test_name, test_dir, pitest_dir, mutant_name, runid)
        value.update({second_key:mutant_result})
        mutants_histogram.update({first_key:value})
    except:
            print("ERROR! Adding mutant_name {}".format(first_key))
    finally:
        lock.release()

def pit_mutants_histogram(criterion, budget, stopping_condition, mutations_csv_path, test_dir, pitest_dir, runid):
    #file = csv.DictReader(open(mutations_csv_path), newline='', )
    with open(mutations_csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=['NAME','SUBJECT','MUTANT_NAME','METHOD','LINE','RESULT','TEST'])
        keys_by_file = set()
        for row in reader:
            subject = row["SUBJECT"]
            mutant_key = row["MUTANT_NAME"]+"_"+row["METHOD"]+"_"+row["LINE"]
            result = row["RESULT"]
            test_name = row["TEST"]
            test_name = test_name[0:test_name.find("(")]
            new_key = mutant_key
            i = 2
            while new_key in keys_by_file:
                new_key = mutant_key + "_{}".format(i)
                i += 1
            mutant_key = new_key
            
            count_mutant(subject, criterion, budget, stopping_condition, mutant_key, result, test_name, test_dir, pitest_dir, runid)
            keys_by_file.add(mutant_key)

lock = threading.Lock()
headers_list = ["SUBJECT","BUDGET","STOP_COND","MUTANT_METHOD_LINE"]
def get_histogram():
    def add_header(name):
        global headers_list
        if name not in headers_list:
            headers_list.append(name)

    global mutants_histogram
    data = ""
    for key in mutants_histogram.keys():
        key_value = key.split(" ")
        subject = key_value[0]
        budget = key_value[1]
        stopping_condition = key_value[2]
        mutant = key_value[3]
        killer_test = ""
        data += "{},{},{},{}".format(subject, budget, stopping_condition, mutant)
        value = mutants_histogram[key]
        for sec_key in value.keys():
            criterion = sec_key
            sec_value = value[sec_key]
            survived = sec_value.get_survived()
            no_coverage = sec_value.get_nocoverage()
            killed = sec_value.get_killed()
            alive = survived + no_coverage
            if not killer_test:
                killer_test = sec_value.get_test()
            add_header("SURVIVED_{}".format(criterion))
            add_header("NO_COVERAGE_{}".format(criterion))
            add_header("KILLED_{}".format(criterion))
            add_header("ALIVE_{}".format(criterion))
            data += ",{},{},{},{}".format(survived, no_coverage, killed, alive)
        
        add_header("KILLER_TEST")
        data += ",{}".format(killer_test)
        data += "\n"
    headers = ""
    add_colon = False
    for header in headers_list:
        if add_colon:
            headers += ","
        else:
            add_colon = True
        headers += header
    return headers + "\n" + data

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mutations_csv", help="mutations.csv file generated by pit")
    args = parser.parse_args()
    pit_mutants_histogram("epaadjacentedges", "600", "maxtime", args.mutations_csv)
    print(get_histogram())
    print("Done!")