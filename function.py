#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : upload_photo_bank.py
# @Author: lxy
# @Date  : 2018/1/29
# @Desc  :
from concurrent.futures import ThreadPoolExecutor
import pymysql
import requests
import json
import os

import time

from PIL import Image
from termcolor import cprint
from tqdm import tqdm

from model import AliCookie, ImgListData, PhotoBankUpload, PhotoBankImageMetadata, PhotoInformation


HEADERS = {
    "accept-encoding": "gzip, deflate, br",
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
                  "63.0.3239.132 Safari/537.36",
    "origin": "https://photobank.alibaba.com",
    "referer": "https://photobank.alibaba.com/photobank/uploader_dialog/index.htm",
}
PHOTO_BANK_GROUP_URL = "https://photobank.alibaba.com/photobank/node/ajax/groups/-1.do"
pool = ThreadPoolExecutor(max_workers=4)


def get_cookie(shop_cn_name):
    pass
    # 数据库提取cookie
    HEADERS["cookie"] = "cookie"
    return AliCookie("cookie", "ctoken", "csrf_token")


def get_all_group_id(cookie):
    group_dict = dict()

    r = requests.get(PHOTO_BANK_GROUP_URL, headers=HEADERS, params={"ctoken": cookie.ctoken})
    if r.status_code == 200:
        for group in r.json()["object"]:
            group_dict[group["name"].lower()] = group["id"]
    return group_dict


def upload_photo(photos, cna):
    upload_result = list()
    if "content-type" in HEADERS:
        HEADERS.pop("content-type")
    params = {
        "gmkey": "CLK",
        "gokey": "evt=beforeupload",
        "cna": cna,
        "logtype": "2",
    }
    HEADERS["referer"] = "https://photobank.alibaba.com/photobank/uploader_dialog/index.htm"
    requests.get("https://gj.mmstat.com/icbu-product.photobank.pcupload", headers=HEADERS, params=params)
    for photo in tqdm(photos):
        pool.submit(upload, upload_result, photo)

    return upload_result


def upload(upload_result, photo):
    img = Image.open(photo)
    if img.height > 1000 or img.width > 1000:
        cprint("\n" + photo + " 尺寸不规范", "yellow")
    files = {
        "scene": (None, "photobankImageNsRule"),
        "name": (None, photo),
        "file": (photo, open(photo, "rb"), "image/png")
    }
    response = requests.post("https://kfupload.alibaba.com/mupload", headers=HEADERS, files=files)
    if response.status_code == 200:
        try:
            upload_result.append(PhotoInformation(photo, **json.loads(response.text)))
            time.sleep(0.1)
        except Exception as e:
            print(photo + "上传失败" + e)


def package_img_data(info: PhotoInformation):
    metadata1 = PhotoBankImageMetadata(info.hash, info.height, info.width, info.size)
    return ImgListData(info.photo_name, info.hash, info.fs_url, "//sc02.alicdn.com/kf/"+info.fs_url, metadata1)


def traversal_folder(work_path, file, all_group_id, cookie):
    if file.lower() in all_group_id or file == "未分组":
        add_to_photo_bank(work_path, file, all_group_id, cookie)
    else:
        cprint("图片银行不存在分组 " + file, "red")


def add_to_photo_bank(work_path, file, all_group_id, cookie):
    if file == "未分组":
        group_id = None
    else:
        group_id = all_group_id[file]
    url = "https://photobank.alibaba.com/photobank/node/ajax/photos/uploadImage.do"
    params = {"ctoken": cookie.ctoken}
    os.chdir(os.path.join(work_path, file))
    photos, img_data = [], []
    for f in os.listdir(os.getcwd()):
        if os.path.isfile(f) and f.lower().endswith((".jpg", ".png")):
            photos.append(f)
        elif os.path.isdir(f):
            traversal_folder(os.getcwd(), f, all_group_id, cookie)
            os.chdir(os.path.join(work_path, file))

    print("开始上传 " + file)
    for photo_info in upload_photo(photos, cookie.cna):
        img_data.append(package_img_data(photo_info))
        if len(img_data) == 20:
            HEADERS["content-type"] = "application/json"
            data = json.dumps(PhotoBankUpload(img_data, group_id), default=lambda o: o.__dict__, sort_keys=True,
                              indent=4)
            requests.post(url, headers=HEADERS, params=params, data=data)
            img_data.clear()
    if len(img_data) > 0:
        HEADERS["content-type"] = "application/json"
        data = json.dumps(PhotoBankUpload(img_data, group_id), default=lambda o: o.__dict__, sort_keys=True, indent=4)
        requests.post(url, headers=HEADERS, params=params, data=data)
