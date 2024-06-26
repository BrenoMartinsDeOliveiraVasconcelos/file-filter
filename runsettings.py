# FILTER SETTINGS
import os
import shutil
import datetime
import json
import argparse

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

# Checking if all files are there
try:
    OPTIONS = json.load(open(os.path.join(SCRIPT_PATH, "options.json"), "r", encoding="utf-8"))
    AUTOMATION_DICT = json.load(open(os.path.join(SCRIPT_PATH, "automatization.json"), "r", encoding="utf-8"))
    CATEGORIES = json.load(open(os.path.join(SCRIPT_PATH, "categories.json"), "r", encoding="utf-8"))
except FileNotFoundError:
    print("Some essential files are missing... Is everything needed there?")
    exit(-1)


DELETE_DUPLICATE_NAME = OPTIONS["duplicates"]["delete"]
IGNORE_MOVE_ERROR = OPTIONS["move"]["ignore_errors"]
RENAME_ON_MOVE = OPTIONS["move"]["rename"]
MAX_LEN = OPTIONS["move"]["name_size_max"]
REMOVE_CHARS = OPTIONS["move"]["remove_char"]
VERBOSE = OPTIONS["system"]["allow_verbose"]
AUTO_EXTRACT_ZIP = OPTIONS["extracting"]["auto_extract"]
DELETE_ZIP_AFTER_EXTRACT = OPTIONS["extracting"]["delete_after_done"]
ZIP_CATEGORY = OPTIONS["extracting"]["category"]
LOG = OPTIONS["system"]["logging"]
DEV = OPTIONS["system"]["dev"]
AUTO = OPTIONS["system"]["automatization"]

OUTPUT = ""

IGNORES = ["__pycache__"]

parser = argparse.ArgumentParser(
                prog='Filter',
                description='Filter folders by categories',
                epilog='Null')

parser.add_argument("--output")
parser.add_argument("--source")

if not AUTO:
    args = parser.parse_args()
else:
    args = []

if not AUTO:
    OUTPUT = args.output

    if not os.path.exists(OUTPUT):
        print("No such directory.")
        exit(-1)


if not DEV:
    if AUTO:
        SOURCE = OUTPUT = AUTOMATION_DICT["source"]

        if SOURCE == "":
            print(f"Source is not defined! Define it at {os.path.join(SCRIPT_PATH, "automatization.json")}")
            exit(1)
    else:
        while True:
            path = args.source
            if os.path.exists(path):
                folders = [os.path.join(path, x) if os.path.isdir(os.path.join(path, x)) else 0 for x in os.listdir(path)]
                timestamp = datetime.datetime.now().timestamp()

                for folder in folders:
                    copy_folder = False
                    if folder != 0:
                        while True:
                            uin = input(f"Filter {folder}? Y/N -> ")
                            if uin in "Yy":
                                copy_folder = True
                                break
                            elif uin in "Nn":
                                copy_folder = False
                                break
                            else:
                                print("Invalid!")

                        if copy_folder:
                            try:
                                os.makedirs(OUTPUT)
                            except FileExistsError:
                                pass
                            shutil.copytree(src=folder, dst=os.path.join(OUTPUT, os.path.split(folder)[1]), dirs_exist_ok=True)
                SOURCE = OUTPUT
                break
            else:
                print("Invalid source! Try another one.")
                exit(-1)
else:
    SOURCE = input("PATH: ")

fileout = os.listdir(OUTPUT)
for fol in fileout:
    if fol not in [key for key in list(CATEGORIES.keys())]:
        fol_path = os.path.join(OUTPUT, fol)
        if os.path.isdir(fol_path):
            fol_path_files = os.listdir(fol_path)
            fold_path = os.path.join(fol_path, "folder")
            try:
                os.makedirs(fold_path)
            except FileExistsError:
                pass
            
            for f in fol_path_files:
                f_path = os.path.join(fol_path, f)
                if os.path.isdir(f_path):
                    if fol not in list(CATEGORIES.keys()):
                        shutil.copytree(src=f_path, dst=os.path.join(fold_path, f), dirs_exist_ok=True)
                        shutil.rmtree(f_path)
