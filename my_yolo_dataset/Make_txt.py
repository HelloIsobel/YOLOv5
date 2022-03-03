import xml.etree.ElementTree as ET
import os
import random
from shutil import copy


def convert(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def convert_annotation(xmlpath, txtpath):
    in_file = open(xmlpath)  # 输入路径
    out_file = open(txtpath, 'w')  # 输出路径
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
             float(xmlbox.find('ymax').text))
        bb = convert((w, h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')


# 留出方，K折交叉验证
if __name__ == "__main__":
    classes = ["people", "AGmachine", "car"]  # TODO: 自己定义的标签
    imagespaths = "data/allimages"  # TODO: 存放 image 文件的地址
    xmlpaths = "data/allxmls"  # TODO: 存放 .xml 文件的地址
    txtpaths = "data/alllabels"

    train_percent = 0.8

    if not os.path.exists(txtpaths):
        os.makedirs(txtpaths)

    for root, dirs, files in os.walk(xmlpaths):
        for file in files:
            xmlpath = os.path.join(root, file)
            txtpath = xmlpath.replace("allxmls", "alllabels")
            txtpath = txtpath.split(".")[0] + ".txt"  # 定义生成的.txt文件的路径：地址+文件名
            convert_annotation(xmlpath, txtpath)

    all_images = os.listdir(imagespaths)
    random.shuffle(all_images)

    num = len(all_images)
    train_num = int(num * train_percent)
    train = all_images[:train_num]
    val = all_images[train_num:]

    if not os.path.exists("train/images"):
        os.makedirs("train/images")
    if not os.path.exists("train/labels"):
        os.makedirs("train/labels")
    if not os.path.exists("val/images"):
        os.makedirs("val/images")
    if not os.path.exists("val/labels"):
        os.makedirs("val/labels")

    for filename in train:
        image_from_path = os.path.join(imagespaths, filename)
        image_to_path = "train/images/" + filename
        copy(image_from_path, image_to_path)

        txtname = filename.split(".")[0] + ".txt"
        label_from_path = os.path.join(txtpaths, txtname)
        label_to_path = "train/labels/" + txtname
        copy(label_from_path, label_to_path)

    for filename in val:
        image_from_path = os.path.join(imagespaths, filename)
        image_to_path = "val/images/" + filename
        copy(image_from_path, image_to_path)

        txtname = filename.split(".")[0] + ".txt"
        label_from_path = os.path.join(txtpaths, txtname)
        label_to_path = "val/labels/" + txtname
        copy(label_from_path, label_to_path)
