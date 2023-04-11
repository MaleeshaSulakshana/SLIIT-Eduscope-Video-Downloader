import requests
import json
import m3u8
import subprocess
import os
import sys
from datetime import datetime

from InquirerPy.utils import color_print

today_date_time = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')

config = {}
with open('config.json', 'r') as f:
    config = json.load(f)

base_path = "https://lecturecapture.sliit.lk/archive/saved/Personal_Capture/"


def getPreferredFolder():

    folder = ""
    if "savePath" in config:
        folder = config["savePath"]

    if folder == "":
        return "./Downloads/"
    else:
        if folder[-1] != "\\" or folder[-1] != "/":
            folder = folder + "\\"

        folder = f"{folder}{today_date_time}/"

        if os.path.exists(folder):
            return folder
        else:
            try:
                os.makedirs(folder)
                return folder
            except:
                color_print(formatted_text=[
                    ("gold", folder),
                    ("red", " <- Invalid Path")])
                sys.exit()


def get_actual_path(link):

    # _144.m3u8
    # _360.m3u8
    quality = config["quality"]

    if(len(link) == 68):
        ID = link[-23:] + "&full=ZnVsbA%3D%3D"
    else:
        ID = link.replace("https://lecturecapture.sliit.lk/neplayer.php?", "")

    MAIN_URL = "https://lecturecapture.sliit.lk/webservice.php?key=vhjgyu456dCT&type=video_paths&"
    URL = MAIN_URL + ID

    session = requests.Session()

    response = session.get(URL, verify="cert.pem").text

    data = json.loads(response)

    video_path_prefix = data['video_1_m3u8_list']

    video_path_postfix = video_path_prefix.replace(
        "../../archive/saved/Personal_Capture/", "")
    main_path = base_path + \
        video_path_postfix.replace(".m3u8", "") + quality
    return main_path


def download_video(main_path, folderPath):
    # requests.get(
    #     "https://api.countapi.xyz/hit/com.navindu.eduscope/download-start")
    char = ''

    main_path_length = len(main_path)
    count = main_path_length - 1
    url_cmp = ""

    for i in range(main_path_length):
        char = main_path[count]
        url_cmp += char
        if(char == "/"):
            break
        count -= 1

    fileNameInUrl = ""
    count_file_name = len(url_cmp) - 1

    while(count_file_name >= 0):
        fileNameInUrl += url_cmp[count_file_name]
        count_file_name -= 1

    file_path = folderPath
    url_info = main_path.replace(fileNameInUrl, " ")
    url_cmp = fileNameInUrl.lstrip("/")
    url_info = url_info.rstrip(" ") + "/"
    file_name = url_cmp.rstrip(".m3u8")
    url_1 = url_info + url_cmp
    r_1 = requests.get(url_1, verify="cert.pem")
    m3u8_master = m3u8.loads(r_1.text)
    file_number = 0
    i = 0
    percentage = 0.0

    color_print(formatted_text=[
                ("green", "\nDownloading to: "),
                ("white", file_path + "\n")])

    for segment in m3u8_master.data['segments']:
        file_number += 1

    with open(file_path + file_name + '.ts', 'wb') as f:
        for segment in m3u8_master.data['segments']:
            url = url_info + segment['uri']
            while(True):
                try:
                    r = requests.get(url, timeout=15, verify="cert.pem")
                except:
                    continue
                break

            f.write(r.content)
            i += 1
            percentage = i / file_number * 100
            # progress_bar.update(i/2)

            print(f"=" * int(percentage / 2), end="")
            print("[", end="")
            print(f"{(str(percentage))[0:5]} %", end="")
            # print("\r\x1b[20C[",end = "")
            print("]", end="")
            print("\r", end="")

    print("\n")
    color_print(formatted_text=[
        ("green", "\nDownload Complete!.")])

    # requests.get(
    #     "https://api.countapi.xyz/hit/com.navindu.eduscope/download-complete")

    return file_name


def convert(file_name, file_path, is_delete_ts_files):

    color_print(formatted_text=[("gold", "\nConverting to mp4... ")])

    infile = file_path + file_name + ".ts"
    outfile = file_path + file_name + ".mp4"

    if is_delete_ts_files == False:
        outfile = f"{file_path}mp4/{file_name}.mp4"

    subprocess.run(['ffmpeg', '-i', infile, outfile,
                   "-hide_banner", "-nostats", "-loglevel", "panic"])
    
    if is_delete_ts_files == True:
        os.remove(file_path + file_name + ".ts")

    color_print(formatted_text=[("green", "\Convert Complete!")])


if __name__ == '__main__':

    is_delete_ts_files = False
    if "isDeleteTsFiles" in config:
        is_delete_ts_files = config["isDeleteTsFiles"]

    convert_to_mp4 = True
    if "convertToMP4" in config:
        convert_to_mp4 = config["convertToMP4"]

    print(f"** Task Started **")
    downloaded_files = []

    # Download videos
    try: 
        for link in config["links"]:

            color_print(formatted_text=[
                        ("gold", "\nReady to download: "),
                        ("white", link + "\n")])

            path = get_actual_path(link)
            filePath = getPreferredFolder()
            file = download_video(path, filePath)

            downloaded_files.append([file, filePath])
    
    except Exception as e:
        print(f"{e}")

    # Convert videos
    if convert_to_mp4 == True:
        try:
            for file in downloaded_files:
                convert(file[0], file[1], is_delete_ts_files)

        except Exception as e:
            print(f"{e}")

    print(f"** Task Completed **")
    sys.exit()
