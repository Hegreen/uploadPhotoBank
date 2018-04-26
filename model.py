#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : model.py
# @Author: lxy
# @Date  : 2018/1/29
# @Desc  :
import re


class PhotoBankUpload(object):
    def __init__(self, img_list_data, group_id):
        if group_id:
            self.groupId = str(group_id)
        self.imgListData = img_list_data
        self.photobankImageWatermark = {"frame": "N", "position": "center", "watermarkContent": ""}
        self.useWatermark = False


class ImgListData(object):
    def __init__(self, display_name, file_md5, filename, photo_url, photo_bank_image_metadata):
        self.displayName = display_name
        self.fileMd5 = file_md5
        self.filename = filename
        self.photoUrl = photo_url
        self.photobankImageMetadata = photo_bank_image_metadata


class PhotoBankImageMetadata(object):
    def __init__(self, hash_code, height, width, size):
        self.hashCode = hash_code
        self.height = height
        self.width = width
        self.size = size


class AliCookie(object):
    def __init__(self, cookie, ctoken, csrf_token):
        self.cookie = cookie
        self.ctoken = ctoken
        self.csrf_token = csrf_token
        match = re.match(".*?cna=(.*?);.*", cookie)
        if match:
            self.cna = match.group(1)
        else:
            self.cna = None


class PhotoInformation(object):
    def __init__(self, photo_name, code, fs_url, hash, height, size, url, width):
        self.photo_name = photo_name
        self.code = code
        self.fs_url = fs_url
        self.hash = hash
        self.height = height
        self.size = size
        self.url = url
        self.width = width
