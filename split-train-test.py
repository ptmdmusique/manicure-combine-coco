import json
from shutil import copyfile
from pathlib import Path

INPUT_FOLDER = "./output/"
META_FILE_NAME = "metadata.json"
OUTPUT_FOLDER = "./manicure/"

USE_SINGLE_LABEL = True
SINGLE_LABEL_INDEX = 1

TRAIN_TEST_RAIO = 0.95

def read_json(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

def write_json(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f)

def copy_img(img_name_list, type):
    for img_name in img_name_list:
        src = INPUT_FOLDER + img_name
        dst = OUTPUT_FOLDER + type + "/" + img_name
        copyfile(src, dst)


Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_FOLDER + "train").mkdir(parents=True, exist_ok=True)
Path(OUTPUT_FOLDER + "test").mkdir(parents=True, exist_ok=True)

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

total_meta = read_json(INPUT_FOLDER + META_FILE_NAME)
num_images = len(total_meta["images"])

num_train = int(num_images * TRAIN_TEST_RAIO)
num_test = num_images - num_train

categories = total_meta["categories"] if not USE_SINGLE_LABEL else [
    {
      "supercategory": "finger",
      "id": SINGLE_LABEL_INDEX,
      "name": "finger"
    }
  ]

annotation_map = {}
for annotation in total_meta["annotations"]:
    image_id = annotation["image_id"]
    if image_id not in annotation_map:
        annotation_map[image_id] = []
    annotation_map[image_id].append(annotation)


def get_new_json(base_counter, total):
    print(f"--- base counter: {base_counter} --- total {total} ---")
    annotations  = []
    images = []
    anno_counter = 1
    for counter in range(total):
        image_meta = total_meta["images"][base_counter + counter]

        # Re-adjust image id
        old_image_id = image_meta["id"]
        new_id = counter + 1
        image_meta["id"] = new_id

        images.append(image_meta)

        if old_image_id in annotation_map:
            for annotation in annotation_map[old_image_id]:
                annotation["image_id"] = new_id
                annotation["id"] = anno_counter

                annotation["category_id"] = SINGLE_LABEL_INDEX if USE_SINGLE_LABEL else annotation["category_id"]

                anno_counter += 1
                annotations.append(annotation)

    new_json = {
        "categories": categories,
        "images": images,
        "annotations": annotations
    }

    return new_json, images

print("Split train folder")
train_meta_file_name = OUTPUT_FOLDER + "train/" + META_FILE_NAME
train_json, train_images = get_new_json(0, num_train)
write_json(train_meta_file_name, train_json)
copy_img([image["file_name"] for image in train_images], "train")

print("Split test folder")
test_meta_file_name = OUTPUT_FOLDER + "test/" + META_FILE_NAME
test_json, test_images = get_new_json(num_train, num_test)
write_json(test_meta_file_name, test_json)
copy_img([image["file_name"] for image in test_images], "test")

print("Testing")
def test_meta_file(meta_json, expected_size):
    print("--- Test size")
    true_len = len(meta_json["images"])
    if true_len != expected_size:
        print(f"** Wrong size, expected: {expected_size} --- got: {true_len} **")
        return False

    print("--- Test annotation's image id")
    img_id_map = {}
    for image in meta_json["images"]:
        img_id_map[image["id"]] = True

    for annotation in meta_json["annotations"]:
        if annotation["image_id"] not in img_id_map:
            print("Image id not found:", annotation["image_id"])

    print("--- Test annotation index")
    counter = 1
    for annotation in meta_json["annotations"]:
        if annotation["id"] != counter:
            print("Annotation id not correct:", annotation["id"])
        counter += 1

    print("--- Test images index")
    counter = 1
    for images in meta_json["images"]:
        if images["id"] != counter:
            print("Annotation id not correct:", images["id"])
        counter += 1

print("Test train")
train_meta = read_json(train_meta_file_name)
test_meta_file(train_meta, num_train)

print("Test test")
test_meta = read_json(test_meta_file_name)
test_meta_file(test_meta, num_test)

total_images = len(train_meta["images"]) + len(test_meta["images"])
print(f"Total images: {total_images}")