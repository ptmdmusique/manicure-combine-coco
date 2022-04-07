import os
from os.path import isfile, join
from os import listdir
import json
from shutil import copyfile

META_FILE_NAME = "metadata.json"
INPUT_FOLDER = "./output-no-aug/"
AUG_INPUT_FOLDER = "./aug-data/"
OUTPUT_FOLDER = "./output/"


def read_json(path):
    with open(path) as f:
        return json.load(f)


def write_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)


metadata = read_json(INPUT_FOLDER + META_FILE_NAME)
annotation_data_list = metadata["annotations"]
img_data_list = metadata["images"]

'''
{
  [image_id] {
    img_info: // ...
    anno_list: [// ...]
  }
}
'''
print("Create data dict")
last_id = 0
img_data_dict = {}
for img_data in img_data_list:
    img_id = img_data["id"]
    img_data_dict[img_id] = {
        "img_info": img_data,
        "anno_list": []
    }

    if img_id > last_id:
        last_id = img_id

print("Add annotation to data dict")
for anno_data in annotation_data_list:
    img_id = anno_data["image_id"]
    img_data_dict[img_id]["anno_list"].append(anno_data)

print("Create name lookup dict")
# Build a dict based on img name and also copy images from INPUT_FOLDER to OUTPUT_FOLDER
img_name_dict = {}
for img_id in img_data_dict:
    img_data = img_data_dict[img_id]
    img_info = img_data["img_info"]
    img_name = img_info["file_name"]
    img_name_dict[img_name] = img_id

    copyfile(INPUT_FOLDER + img_name, OUTPUT_FOLDER + img_name)

print("Check for matching aug images")
# Get list of image that is not a json file in aug folder
aug_image_name_list = [f for f in listdir(
    AUG_INPUT_FOLDER) if ".json" not in f]

print("Check for matching aug images and create new info")
# Check if there is a matching image in OUTPUT folder, if yes, create a new image info with new image_id
for aug_image_name in aug_image_name_list:
    if aug_image_name in img_name_dict:
        new_id = last_id + 1

        file_info = os.path.splitext(aug_image_name)
        img_name = file_info[0]
        img_ext = file_info[1]

        new_aug_image_name = img_name + "_aug" + "." + img_ext
        img_id = img_name_dict[aug_image_name]
        img_data = img_data_dict[img_id]
        img_info = img_data["img_info"]
        img_name = img_info["file_name"]

        # Create new image info
        new_img_info = {
            "id": new_id,
            "file_name": new_aug_image_name,
            "width": img_info["width"],
            "height": img_info["height"]
        }

        # Create new annotation list
        new_anno_list = []
        for anno_data in img_data["anno_list"]:
            new_data = anno_data.copy()
            new_data["image_id"] = new_id
            new_anno_list.append(new_data)

        # Add new image info and annotation list to dict
        img_data_dict[last_id + 1] = {
            "img_info": new_img_info,
            "anno_list": new_anno_list
        }

        # Copy image from aug folder to OUTPUT folder
        copyfile(AUG_INPUT_FOLDER + aug_image_name,
                 OUTPUT_FOLDER + new_aug_image_name)

        # Update max_id
        last_id += 1

# write the result dict to json file
print("Write to json file")
metadata["images"] = []
metadata["annotations"] = []
for img_id in img_data_dict:
    img_data = img_data_dict[img_id]
    img_info = img_data["img_info"]
    img_name = img_info["file_name"]
    img_info["file_name"] = img_name
    metadata["images"].append(img_info)

    for anno_data in img_data["anno_list"]:
        metadata["annotations"].append(anno_data)


write_json(OUTPUT_FOLDER + META_FILE_NAME, metadata)
