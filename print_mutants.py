import argparse
import os
import utils

class Mutants:

    def print_mutants(self, mutant_dir, subject_name):
        ret = ""
        traditional_mutant_dir = os.path.join(mutant_dir, "traditional_mutants")
        for method_dir_name in os.listdir(traditional_mutant_dir):
            if not os.path.isdir(os.path.join(traditional_mutant_dir, method_dir_name)):
                continue
            for operator_dir_name in os.listdir(os.path.join(traditional_mutant_dir, method_dir_name)):
                ret = ret+ "{};{};{}\n".format(os.path.basename(traditional_mutant_dir).split("_")[0], method_dir_name, operator_dir_name)
        
        class_mutants = os.path.join(mutant_dir, "class_mutants")
        for operator_dir_name in os.listdir(class_mutants):
            if not os.path.isdir(os.path.join(class_mutants, operator_dir_name)):
                continue
            ret = ret+ "{};{};{}\n".format(os.path.basename(class_mutants).split("_")[0], "", operator_dir_name)
        utils.save_file("mutants_mujava_{}.txt".format(subject_name), ret)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mutant_dir", help="Directorio donde estan los mutantes (traditional o classes)")
    parser.add_argument("subject_name", help="Nombre del subject")
    args = parser.parse_args()
    mutants = Mutants()
    mutants.print_mutants(args.mutant_dir, args.subject_name)
    print("Done!")


                
    