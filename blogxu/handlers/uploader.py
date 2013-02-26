#! /usr/bin/env python
#coding=utf-8

import tornado.web 
from bae.core import const
from bae.api import bcs
from bae.api import logging
from blogxu.models.entity import getSession, Upload
import time
######################################
# 文件上传专用。For BCS              #
# Author: Xu                         #
# Date: 2013.2.21                    #
######################################


HOST = const.BCS_ADDR
AK = const.ACCESS_KEY
SK = const.SECRET_KEY
bname = 'bucket的名字'
bucket_url = "http://bcs.duapp.com/你的bcs地址/"

def bcs_upload(data, filename): 
    timeline_int = int(time.time())
    name_split = filename.split('.')
    # 视有没有后缀名的情况随机一个名字 
    if len(name_split) == 1:
        filename = filename + str(timeline_int)
    else:
        filename = name_split[0] + str(timeline_int) + '.' + name_split[1] 
    ### 创建BCS管理对象
    bcs2 = bcs.BaeBCS(HOST, AK, SK)
    o1 = '/' + filename
    e,d = bcs2.put_object(bname, o1, data) 
    return e,filename

def saveIntoDB(filename, type):
    session = getSession()
    session.add(Upload(type, filename , bucket_url  +  filename))
    session.commit()
    
# 这里得注意不管是删除还是上传，文件名前都得有个'/' .. 找这个问题找了好久因为一直删不掉文件
def deleteFromBCS(name):
    bcs2 = bcs.BaeBCS(HOST, AK, SK)
    bcs2.del_object(bname, '/' + name.encode('utf8'))

class FileUpload(tornado.web.RequestHandler):
    def post(self): 
        file_dict_list = self.request.files['file']
        errorcode = 1
        name = ''
        for file_dict in file_dict_list:
            filename = file_dict["filename"]  
            data = file_dict["body"]
            errorcode, name = bcs_upload(data, filename.encode('utf8'))
        if errorcode == 0:
            # 本来准备图片、文件分开的，还加了个类型，不过想想还是算了，没什么必要
            saveIntoDB(name ,"文件")
            self.redirect('/admin/upload', permanent=True)
        else:
            self.write('Upload Failed!')
       