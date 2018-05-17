import os
import shutil
import fileinput
import re
import subprocess
from sys import platform
import threading

def get_package_dir(package_array):
    packages_dir = ""
    for f in package_array:
        packages_dir += f
        packages_dir += os.path.sep
    return packages_dir

def remove_and_make_dirs(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

def make_dirs_if_not_exist(path):
    if not os.path.exists(path):
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

def compile_workdir(workdir, output_directory, *classpath):
    command_find = find_and_save_command("*.java", "sources.txt")
    print_command(command_find, workdir)
    
    lock_if_windows()
    subprocess.check_output(command_find, cwd=workdir, shell=True)
    release_if_windows()

    print_command("mkdir {}".format(output_directory))
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        
    all_classpath = ""
    for p in classpath:
        all_classpath += p + os.path.pathsep

    command_compile = "javac -classpath {} -d {} @sources.txt".format(all_classpath, output_directory)
    print_command(command_compile, workdir)
    lock_if_windows()
    subprocess.check_output(command_compile, cwd=workdir, shell=True)
    release_if_windows()
    
def find_and_save_command(toFind, saveIn):
    command_win = "FORFILES /S /M {} /C \"CMD /C echo|set /p=@relpath & echo:\" > {}".format(toFind, saveIn)
    command_unix = "find . -name '{}' > {}".format(toFind, saveIn)
    command_find = command_win if (platform == "win32") else command_unix
    return command_find

def print_command(command, workdir=None):
    print('Executing command in shell:')
    if workdir is not None:
        print('In workdir: {}'.format(workdir))
    print(command)
    
lock = threading.Lock()
def lock_if_windows():
    if(platform == "win32"):
        lock.acquire()

def release_if_windows():
    if(platform == "win32"):
        lock.release()