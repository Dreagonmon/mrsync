import sys
import os
import shutil
import zipapp
import subprocess
import argparse

WORKSPACE = os.path.abspath(os.path.dirname(__file__))
SOURCE_DIR = os.path.join(WORKSPACE, "mrsync")
SOURCE_EXEC = "" # has __main__.py, ignore
LIBRARY_INDEX_URL = "https://mirrors.aliyun.com/pypi/simple"
LIBRARY_LIST_FILE = os.path.join(WORKSPACE, "requirements.txt")
LIBRARY_INSTALL_DIR = SOURCE_DIR
LIBRARY_CLEANUP_FILES = [
    os.path.join(WORKSPACE, "mrsync", "bin"),
]
DIST_INTERPRETER = "/usr/bin/env python3"
DIST_DIR = os.path.join(WORKSPACE, "dist")
DIST_NAME = "mrsync.pyz"

def purge_cache(path):
    # walk all files
    for file_name in os.listdir(path):
        file_name: str = file_name
        abs_path = os.path.join(path, file_name)
        if file_name == "__pycache__" or file_name.endswith(".dist-info"):
            print(abs_path)
            # delete `__pycache__`
            shutil.rmtree(abs_path)
        elif os.path.isdir(abs_path):
            # call for subdir
            purge_cache(abs_path)

if __name__ == "__main__":
    os.chdir(WORKSPACE)
    # check args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-D", "--skip-install-dependences",
        dest="skip_install_dependences",
        action="store_true",
        help="Skip installing the dependences",
    )
    args = parser.parse_args()
    # install library
    if not args.skip_install_dependences:
        subprocess.run([
            sys.executable,
            "-m", "pip", "install",
            "-r", LIBRARY_LIST_FILE,
            "-i", LIBRARY_INDEX_URL,
            "--target", LIBRARY_INSTALL_DIR,
        ])
    # purge __pycache__ and .dist-info
    for p in LIBRARY_CLEANUP_FILES:
        if os.path.exists(p):
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
    purge_cache(".")
    # clean dist dir
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.mkdir(DIST_DIR)
    # zipapp
    zipapp.create_archive(
        SOURCE_DIR,
        os.path.join(DIST_DIR, DIST_NAME),
        DIST_INTERPRETER,
        SOURCE_EXEC,
        compressed=True,
    )
