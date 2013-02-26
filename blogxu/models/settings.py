#! /usr/bin/env python
#coding=utf-8

from bae.core import const

######################################
# 数据库相关配置(MySQL)              #
# Author: Xu                         #
# Date: 2013.2.20                    #
######################################

DBSETTINGS = dict(
    db_name = 'BAE数据库名',
    db_host = const.MYSQL_HOST,
    db_port = int(const.MYSQL_PORT),
    db_user = const.MYSQL_USER,
    db_password = const.MYSQL_PASS,
    db_encode = 'utf8',
)

#存在数据库中的博客设置项的name. 初始化数据库时要用
#密码初始化为的“admin”的md5值
BLOG_SETTINGS_DEFAULTS = dict(
    BLOG_TITLE = 'XuBlog Beta',
    BLOG_SUBTITLE = '这里是我的博客，欢迎来访!',
    BLOG_ADMIN_NAME = 'admin',
    BLOG_ADMIN_PASSWORD = '21232f297a57a5a743894a0e4a801fc3',
    BLOG_SUM_CODE = '',
    BLOG_COMMENT_CODE = '',
)
