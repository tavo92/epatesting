import os
import shutil

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