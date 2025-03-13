import os
import time
import base64
import json
import shutil
from flask import Response
import jpg_compress_mechanisms

directory_in_str = "C:\\DocScan"


class Object:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=False, indent=4)


def clear_crap(folder_path):
    """Delete all files and directories in the given folder."""
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def main_scanner_driver():
    image_data = []
    images = list()
    os.system("CmdTwain -q C:\\DocScan\\Doc_Scan_Test_Document.jpg")
    time.sleep(0.5)
    print(os.listdir(directory_in_str))
    print(os.listdir(directory_in_str))
    time.sleep(0.5)
    os.listdir(directory_in_str)
    jpg_compress_mechanisms.resize_without_loosing_quality()
    directory = os.fsencode(directory_in_str)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".jpg") or filename.endswith(".jpeg"):
            filename = directory_in_str + "\\" + str(filename)
            with open(filename, "rb") as image_file:
                encoded_string = str(base64.b64encode(image_file.read()))
                images.append(str(encoded_string))
        else:
            continue
    print(len(images))
    # lis = list()
    # me = Object()
    for ind, i in enumerate(images):
        img = {
            "id": ind,
            "baseX64": i[:-1]
        }
        image_data.append(img)
        # me.name = str(ind)
        # me.base = (i[2:])
        # lis.append(me.toJSON())
    folder = directory_in_str
    clear_crap(folder)
    # res = Response(json.dumps(lis))
    # res.headers.add('Access-Control-Allow-Origin', '*')
    return image_data


