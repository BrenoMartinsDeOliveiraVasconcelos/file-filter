import os
import shutil
import json
import runsettings as config
import random
import datetime
import hashlib
import sys
import threading
import time


def get_hash(filename) -> str:
    try:
        with open(filename, "rb") as f:
            # Read the file in chunks to avoid memory issues with large files
            data = f.read(1024)
            h = hashlib.sha256()  # You can choose a different hashing algorithm here (e.g., md5)

            while data:
                h.update(data)
                data = f.read(1024)

            # Get the final hash digest
            return h.hexdigest()
    except IsADirectoryError:
        return ""


def output(out: str, system_call=False):
    outp = f'{datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")} -> {out}\n'

    if config.VERBOSE or system_call:
        print(outp)

    if config.LOG:
        open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt"), "a+", encoding="utf-8").write(outp)
        


def main(fpath: str):
    print(f"Script is going to run at {fpath}")
    # Get the list of folders
    folders = [name for name in os.listdir(fpath) if os.path.isdir(os.path.join(fpath, name)) and name not in config.IGNORES]

    print(f"Folders are {folders}")
    
    # List of file types
    filetp = config.CATEGORIES

    # Separates files into categories
    for folder in folders:
        folderpath = os.path.join(fpath, folder)
        for category, mime in filetp.items():
            catpath = os.path.join(fpath, folder, category)
            
            try:
                os.makedirs(catpath)
            except FileExistsError:
                pass

            cat_files = os.listdir(catpath)
            cat_hashes = []

            for file in cat_files:
                cat_hashes.append(get_hash(os.path.join(catpath, file)))

            output(f"Generated an array with {len(cat_hashes)} strings of hashes.")

            try:
                os.mkdir(catpath)
            except FileExistsError:
                pass

            files = os.listdir(folderpath)
            file_num = len(files)

            
            threading.Thread(target=output, args=[f"Moving {file_num} files from {folderpath} to {catpath}.", ]).start()

            for file in files:
                file_path = os.path.join(folderpath, file)

                for suffix in mime:
                    if file.endswith(suffix):
                        try:
                            duplicate = False
                            file_hash = get_hash(file_path)
                            if file_hash in cat_hashes:
                                duplicate = True
                                threading.Thread(target=output, args=[f"{file_path} is a duplicate!", ]).start()
                            else:
                                duplicate = False
                                threading.Thread(target=output, args=[f"{file_path} is not a duplicate!", ]).start()
                            
                            while True:
                                new_name_chars = []
                                new_name = "."

                                if config.RENAME_ON_MOVE:
                                    new_name = f"{random.randint(0, 2147483647)}{suffix}"
                                else:
                                    new_name = file if new_name not in cat_files else f"{random.randint(0, 5)}"+new_name

                                    if len(new_name) > config.MAX_LEN:
                                        new_name = new_name[0:config.MAX_LEN]
                                    
                                    index = 0
                                    new_name_chars = [x for x in new_name]
                                    for char in new_name_chars:
                                        if char in config.REMOVE_CHARS:
                                            new_name_chars[index] = ""
                                        
                                        index += 1

                                    new_name = "".join(new_name_chars)+suffix

                                if new_name not in cat_files:
                                    break

                            if not duplicate:
                                shutil.move(file_path, os.path.join(catpath, new_name))
                                threading.Thread(target=output, args=[f"Moved {file_path} to {catpath}", ]).start()
                            else:
                                if config.IGNORE_MOVE_ERROR:
                                    threading.Thread(target=output, args=[f"Ignoring duplicate!", ]).start()
                                else: 
                                    if config.DELETE_DUPLICATE_NAME:
                                        try:
                                            os.remove(file_path)
                                        except PermissionError:
                                            threading.Thread(target=output, args=[f"Permission denied remobing {file_path}", ]).start()
                                    else:
                                        threading.Thread(target=output, args=["No config set for duplicates, ignoring.", ]).start()
                            file_num -= 1
                        except shutil.Error:
                            threading.Thread(target=output, args=[f"Unknown error at {file_path}", ]).start()

                    if config.AUTO_EXTRACT_ZIP and category:
                        if category == config.ZIP_CATEGORY and suffix in filetp[config.ZIP_CATEGORY]:
                            zips = os.listdir(catpath)
                            for zip in zips:
                                zip_path = os.path.join(folderpath, "zip", zip)
                                try:
                                    shutil.unpack_archive(zip_path, os.path.join(zip_path+".folder"))
                                except shutil.ReadError:
                                    threading.Thread(target=output, args=[f"Error at {zip}", ]).start()

                                output(zip_path)
                                if config.DELETE_ZIP_AFTER_EXTRACT:
                                    try:
                                        os.remove(zip_path)
                                    except PermissionError:
                                        threading.Thread(target=output, args=[f"Permission denied while deleting {zip}.", ]).start()
                                    except IsADirectoryError:
                                        pass
            threading.Thread(target=output, args=[f"{category} at {folder} has {file_num} non-moved files.", ]).start()


if __name__ == '__main__':
    output("Executing...", system_call=True)
    main(fpath=config.SOURCE)
    output(f"Filtered at {config.SOURCE}")
