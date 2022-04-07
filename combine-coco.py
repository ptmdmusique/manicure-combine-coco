from shutil import copyfile
from pathlib import Path
import json

META_FILE_NAME = "metadata.json"
OUTPUT_FOLDER = "./output-no-aug/"


def read_json(path):
    with open(path) as f:
        return json.load(f)


def write_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)


def get_input_path(index):
    return f"input_{index}/"


NUM_OF_INPUTS = 4

'''
{
  categories: [
    {
      id: number,
      name: string,
      supercategory: string,
    }
  ],
  images: [
    {
      id: number,
      file_name: string,
      width: number,
      height: number,
    }
  ],
  annotations: [
    {
      id: number,
      image_id: number,
      category_id: number,
      bbox: [x, y, width, height],
      area: number,
      segmentation: [
        [x, y, x, y, x, y, x, y, ...],
        [x, y, x, y, x, y, x, y, ...],
        [x, y, x, y, x, y, x, y, ...],
      ],
      iscrowd: 0 or 1,
    }
  ]
}
'''

# Prepare output
Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

# Read metadata
meta_data = read_json(f"{get_input_path(0)}{META_FILE_NAME}")

counter = 0
for img in meta_data["images"]:
    img_name = img["file_name"]
    try:
        src = f"{get_input_path(0)}{img_name}"
        dst = f"{OUTPUT_FOLDER}{img_name}"
        copyfile(src, dst)
        counter += 1
    except Exception as e:
        print(img_name)

cur_img_index = counter

# Combine, move forward with image_id
for i in range(0, NUM_OF_INPUTS):
    image_names = []

    input_meta_data = read_json(f"{get_input_path(i)}{META_FILE_NAME}")
    for img in input_meta_data["images"]:
        img["id"] += cur_img_index
        meta_data["images"].append(img)
        image_names.append(img["file_name"])

    for ann in input_meta_data["annotations"]:
        ann["image_id"] += cur_img_index
        meta_data["annotations"].append(ann)

    for cat in input_meta_data["categories"]:
        cat["id"] += cur_img_index
        meta_data["categories"].append(cat)

    cur_img_index += len(input_meta_data["images"])

    for img_name in image_names:
        src = f"{get_input_path(i)}{img_name}"
        dst = f"{OUTPUT_FOLDER}{img_name}"
        copyfile(src, dst)

print(f"Total images {cur_img_index}")
write_json(f"{OUTPUT_FOLDER}{META_FILE_NAME}", meta_data)
