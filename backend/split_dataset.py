import os
import random
import shutil

SOURCE_IMAGES = r"F:\PRERANA GURAV\MTECH 24-25\Project\Dataset\YOLO_Crack\images"
SOURCE_LABELS = r"F:\PRERANA GURAV\MTECH 24-25\Project\Dataset\YOLO_Crack\labels"

DEST = r"F:\PRERANA GURAV\MTECH 24-25\Project\Dataset\YOLO_Crack"

random.seed(42)

images = []

for file in os.listdir(SOURCE_IMAGES):
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        images.append(file)

random.shuffle(images)

train_size = int(len(images) * 0.8)
valid_size = int(len(images) * 0.1)

train_files = images[:train_size]
valid_files = images[train_size:train_size + valid_size]
test_files = images[train_size + valid_size:]

for split in ["train", "valid", "test"]:

    os.makedirs(os.path.join(DEST, split, "images"), exist_ok=True)
    os.makedirs(os.path.join(DEST, split, "labels"), exist_ok=True)

def copy_files(file_list, split_name):

    for img in file_list:

        img_src = os.path.join(SOURCE_IMAGES, img)
        img_dst = os.path.join(DEST, split_name, "images", img)

        shutil.copy2(img_src, img_dst)

        txt = os.path.splitext(img)[0] + ".txt"

        txt_src = os.path.join(SOURCE_LABELS, txt)

        if os.path.exists(txt_src):

            txt_dst = os.path.join(
                DEST,
                split_name,
                "labels",
                txt
            )

            shutil.copy2(txt_src, txt_dst)

copy_files(train_files, "train")
copy_files(valid_files, "valid")
copy_files(test_files, "test")

print("DONE")
print("Train :", len(train_files))
print("Valid :", len(valid_files))
print("Test  :", len(test_files))