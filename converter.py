import json
import subprocess
import os
import sys
import glob
from datetime import datetime

from InquirerPy.utils import color_print


# Read config json
config = {}
with open('convertConfig.json', 'r') as f:
    config = json.load(f)


# Function for convert .ts to .mp4
def convert(file_name, file_path, save_path, is_delete_ts_files):

    color_print(formatted_text=[("gold", "\nConverting to mp4... ")])

    in_file = f"{file_path}{file_name}.ts"
    out_file = f"{save_path}{file_name}.mp4"

    subprocess.run(['ffmpeg', '-i', in_file, out_file,
                   "-hide_banner", "-nostats", "-loglevel", "panic"])
    
    if is_delete_ts_files == True:
        os.remove(file_path + file_name + ".ts")

    color_print(formatted_text=[("green", "\Convert Complete!")])


if __name__ == '__main__':

    is_delete_ts_files = False
    if "isDeleteTsFiles" in config:
        is_delete_ts_files = config["isDeleteTsFiles"]

    downloaded_files = []

    if "path" in config and config["path"] != "":
        folder = config["path"]
        if folder[-1] != "\\" or folder[-1] != "/":
            folder = folder + "\\"

        if "allTs" in config and config["allTs"] == True:
            for file in glob.glob(f"{folder}*.ts"):
                filename = os.path.splitext(os.path.basename(file))[0]
                downloaded_files.append([filename, folder])

        else:
            if "fileNames" in config:
                for filename in config["fileNames"]:
                    downloaded_files.append([filename, folder])

    else:
        print(f"-- Path not found!")
        sys.exit()

    save_path = ""
    if "save" in config and config["save"] != "":
        save_path = config["save"]
        if save_path[-1] != "\\" or save_path[-1] != "/":
            save_path = save_path + "\\"

        if not os.path.exists(save_path):
            os.makedirs(save_path)

    print(f"** Task Started **")

    # Convert videos
    try:
        for file in downloaded_files:
            convert(file[0], file[1], save_path, is_delete_ts_files)

    except Exception as e:
        print(f"{e}")

    print(f"** Task Completed **")
    sys.exit()
