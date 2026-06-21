import os
import xml.etree.ElementTree as ET

XML_DIR = r"F:\PRERANA GURAV\MTECH 24-25\Project\Dataset\2750\labels"
OUTPUT_DIR = r"F:\PRERANA GURAV\MTECH 24-25\Project\Dataset\YOLO_Crack\labels"

os.makedirs(OUTPUT_DIR, exist_ok=True)

count = 0
skipped = 0

for xml_file in os.listdir(XML_DIR):

    if not xml_file.lower().endswith(".xml"):
        continue

    xml_path = os.path.join(XML_DIR, xml_file)

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        size = root.find("size")

        if size is None:
            skipped += 1
            continue

        width = int(size.find("width").text)
        height = int(size.find("height").text)

        if width <= 0 or height <= 0:
            skipped += 1
            continue

        txt_file = os.path.join(
            OUTPUT_DIR,
            xml_file.replace(".xml", ".txt")
        )

        with open(txt_file, "w") as f:

            for obj in root.findall("object"):

                box = obj.find("bndbox")

                xmin = float(box.find("xmin").text)
                ymin = float(box.find("ymin").text)
                xmax = float(box.find("xmax").text)
                ymax = float(box.find("ymax").text)

                x_center = ((xmin + xmax) / 2.0) / width
                y_center = ((ymin + ymax) / 2.0) / height

                bw = (xmax - xmin) / width
                bh = (ymax - ymin) / height

                f.write(
                    f"0 {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}\n"
                )

        count += 1

    except Exception as e:
        print("Skipped:", xml_file, e)
        skipped += 1

print(f"\nDone!")
print(f"Converted = {count}")
print(f"Skipped = {skipped}")