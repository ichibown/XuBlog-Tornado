#! /usr/bin/env python
#coding=utf-8

from handlers import admin, blog, uploader

######################################
# 所有的url路由映射                  #
# Author: Xu                         #
# Date: 2013.2.20                    #
######################################


blogurls = [
    # 前台页面所有路由
    (r'/', blog.Home),
    (r'/about', blog.ShowAbout),

    (r'/([0-9a-zA-Z]*)', blog.ListArticles),
    (r'/q/tag/([0-9]+)', blog.ListByTag),
    (r'/q/date/([0-9]+)/([0-9]+)', blog.ListByDate),
    (r'/q/search', blog.ListSearch),
    (r'/p/([0-9]+)', blog.ReadArticle),

    # 文件上传路由
    (r'/file/upload/?',uploader.FileUpload),
    
    # 后台登陆路由
    (r'/admin/login', admin.Login),  
    (r'/admin/logout', admin.Logout),  
  
    # 以下均为后台管理相关路由    
    (r'/admin/new',     admin.WriteBlog),
    (r'/admin/save',     admin.SaveBlog),
    (r'/admin/article', admin.ArticleManage),
    (r'/admin/article/change/([0-9]+)', admin.ArticleChange),
    (r'/admin/article/del/([0-9]+)', admin.ArticleDel),
    (r'/admin/upload', admin.UploadManage),
    (r'/admin/upload/del/([0-9]+)', admin.UploadDel),
    (r'/admin/type', admin.TypeManage),
    (r'/admin/type/change/([0-9]+)', admin.TypeChange),
    (r'/admin/type/del/([0-9]+)', admin.TypeDel),
    (r'/admin/type/add', admin.TypeAdd),
    (r'/admin/tag', admin.TagManage),
    (r'/admin/tag/del/([0-9]+)', admin.TagDel),
    (r'/admin/tag/change/([0-9]+)', admin.TagChange),
    (r'/admin/link', admin.LinkManage),
    (r'/admin/link/add', admin.LinkAdd),
    (r'/admin/link/del/([0-9]+)', admin.LinkDel),
    (r'/admin/log', admin.LogManage),
    (r'/admin/log/clear', admin.LogClear),
    (r'/admin/settings', admin.SettingManage),
    (r'/admin/settings/cset', admin.ChangeSettings),
    (r'/admin/settings/cpsw', admin.ChangePsw),
    (r'/admin/sum', admin.SumManage), 
    
    # 初始化BAE数据库
    (r'/admin/initBlog', admin.InitBlog), 
]