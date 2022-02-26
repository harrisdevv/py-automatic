import time
import json
from datetime import datetime
import copy
import os.path
import shutil
import sys
import glob
import hashlib

FILE_IMAGE_JSON = "image-excalidraw.json"

def dump_to_file(filename, obj):
    with open(filename, "w") as file:
        my_json_object = json.dump(obj, file)

def load_from_file(filename):
    with open(filename, "r") as file:
        return json.load(file)

def genId(str):
    hash_object = hashlib.sha512(str.encode("utf-8"))
    hex_dig = hash_object.hexdigest()
    return hex_dig

def genFileId(str):
    hash_object = hashlib.sha384(str.encode("utf-8"))
    hex_dig = hash_object.hexdigest()
    return hex_dig

def format_json_obj(obj):
    json_formatted_str = json.dumps(obj, indent=4)
    return json_formatted_str

def write_excalidraw(files_with_id, full_image_obj, input_file_path, output_file_path):
    with open(output_file_path, "w") as output_file:
        with open(input_file_path, "r") as input_file:
            for line in input_file.readlines():
                output_file.write(line)
                if (line.startswith("# Text Elements")):
                    output_file.write("# Embedded files\n")
                    for file in files_with_id:
                        output_file.write(file["file_id"] + ": " + file["rel_file_md"] + "\n")
                elif (line.startswith("# Drawing")):
                    output_file.write("```json\n")
                    output_file.write(format_json_obj(full_image_obj))
                    output_file.write("\n")
                    output_file.write("```")
                    output_file.flush()
                    output_file.close()
                    print("Done")
                    break
            input_file.close()

def main():
    if (len(sys.argv) < 2):
        print("Missing output file path")
        return
    DEFAULT_MP_IMAGE_FOLDER = "/home/harrison-hienp/Downloads/MemoryPalace/"
    image_folder_path = DEFAULT_MP_IMAGE_FOLDER
    if (len(sys.argv) == 3):
        image_folder_path = sys.argv[1]
    filenames_in_image_folder = []
    filenames_in_image_folder= list(filter(os.path.isfile, glob.glob(image_folder_path + "*")))
    filenames_in_image_folder.sort(key=lambda x: os.path.getmtime(x))
    counter = 1
    NOTE_ATTACHMENT_FOLDER= "/home/harrison-hienp/Desktop/notes/Attachment/"
    files_with_id = []
    for file in filenames_in_image_folder:
        now = datetime.now()
        date_str= now.strftime("%Y-%m-%d %H-%M-%S")
        pasted_file_name = "Pasted Image " + date_str
        pasted_file_name_with_ext = pasted_file_name + "." + file.split(".")[1]
        while (os.path.exists(NOTE_ATTACHMENT_FOLDER + pasted_file_name_with_ext)):
            pasted_file_name_with_ext = pasted_file_name + "_" + str(counter) + "." + file.split(".")[1]
            counter += 1
        dest = NOTE_ATTACHMENT_FOLDER + pasted_file_name_with_ext
        shutil.copyfile(file, dest)
        files_with_id.append({"file_id": genFileId(dest), 
        "rel_file_md": "[[Attachment/" + pasted_file_name_with_ext + "]]",
        "file_abs_path": dest})
    full_image_obj = load_from_file("full-image.json")
    elements = full_image_obj["elements"]
    for idx, file in enumerate(files_with_id):
        image_obj = load_from_file(FILE_IMAGE_JSON)
        new_image_obj = copy.copy(image_obj) 
        new_image_obj["id"] = genId(file["file_abs_path"])
        new_image_obj["y"] += 800 * idx
        new_image_obj["seed"] = hash((datetime.now()))
        new_image_obj["versionNonce"] = hash((datetime.now()))
        new_image_obj["fileId"] = file["file_id"]
        elements.append(new_image_obj)
    NOTES_FOLDER = "/home/harrison-hienp/Desktop/notes/"
    input_file_path = NOTES_FOLDER + sys.argv[1]
    output_file_path = NOTES_FOLDER + sys.argv[1]
    backup_file_path = input_file_path[0:input_file_path.rindex("/")] + "/backup/" + \
        input_file_path[input_file_path.rindex("/") + 1:]
    shutil.move(input_file_path, backup_file_path)
    write_excalidraw(files_with_id, full_image_obj, backup_file_path, output_file_path)

main()
