import os
import shutil
import fileinput
import re

def get_package_dir(package_array):
    packages_dir = ""
    for f in package_array:
        packages_dir += f
        packages_dir += os.path.sep
    return packages_dir

def make_dirs(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    
def replace_assert_catch_in_tests(java_file):
    for line in fileinput.input(java_file, inplace=1, backup='.original'):
        line = re.sub('\sassert','//assert', line.rstrip())
        line = re.sub('catch\\(\w*','catch(Exception', line.rstrip())
        print(line)
        
def save_file(path, content):
    file = open(path,"w")
    file.write(content)
    file.close()
    