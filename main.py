#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : main.py
# @Author: lxy
# @Date  : 2018/1/30
# @Desc  :
import os

from function import get_cookie, get_all_group_id, traversal_folder


if __name__ == "__main__":
    work_path, cookie = None, None
    for file in os.listdir(os.getcwd()):
        if os.path.isdir(file) and "上传图片" in file:
            cookie = get_cookie(file.split("-")[1])
            work_path = os.path.join(os.getcwd(), file)

    if work_path and cookie:
        all_group_id = get_all_group_id(cookie)
        os.chdir(work_path)
        for file in os.listdir(os.getcwd()):
            if os.path.isdir(file):
                traversal_folder(work_path, file, all_group_id, cookie)
                os.chdir(work_path)
    else:
        print("目标文件夹不存在")
