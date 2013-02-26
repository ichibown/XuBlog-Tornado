#! /usr/bin/env python
#coding=utf-8

import tornado.web 
from blogxu.models.entity import getSession,initDatabase
from blogxu.models.entity import Type,Tag,Article,Upload,Link,Settings,Log
from datetime import datetime
import re,hashlib
######################################
# 后台管理相关核心处理方法           #
# Author: Xu                         #
# Date: 2013.2.21                    #
######################################


# 纯粹数据容器。容纳各个界面都通用的不变的数据。比如这里的博客名和admin名
# 其他需要展示这种数据的多重继承一下
# 这种类的属性前台模板中需要 handler.XXX 来获取
class StaticData(object):
    def __init__(self):
        self.session = getSession()
        blog_name = self.session.query(Settings).filter(Settings.name=='BLOG_TITLE').one().content
        admin_name = self.session.query(Settings).filter(Settings.name=='BLOG_ADMIN_NAME').one().content
        self.staticdata = {'blog_name' : blog_name , 'admin_name' : admin_name}


# 用于后台身份验证
class LoginValidateBase(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie('username')
    
# 登陆
class Login(LoginValidateBase , StaticData):
    def get(self):
        self.render('admin_login.html')
        
    def post(self):
        StaticData.__init__(self)
        username = self.get_argument('username',default='')
        password = self.get_argument('password',default='')
        psw_md5 = hashlib.md5(password).hexdigest()
        name = self.session.query(Settings).filter(Settings.name == 'BLOG_ADMIN_NAME').first().content
        password = self.session.query(Settings).filter(Settings.name == 'BLOG_ADMIN_PASSWORD').first().content
        if username == name and psw_md5 == password:
            self.set_secure_cookie('username', username)
            self.redirect('/admin/new')
        else:
            self.write('<script language="javascript">alert("错了错了！！");self.location="/admin/login";</script>')
         

class Logout(LoginValidateBase):
    def get(self):
        self.clear_cookie('username')
        self.redirect('/')
        

# 写新文章
class WriteBlog(LoginValidateBase, StaticData):
    @tornado.web.authenticated
    def get(self):
        StaticData.__init__(self)
        types = self.session.query(Type).all() 
        self.render('admin_write.html', types = types)    
        
# 存文章（包括新写的和修改的）
class SaveBlog(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def post(self): 
        StaticData.__init__(self)
        title = self.get_argument('title',default='')
        content = self.get_argument('content',default='')
        typeid = self.get_argument('type',default='')
        tags = self.get_argument('tags',default='')
        aid = self.get_argument('aid',default=None)
        
        tagsobj = [] 
        articletype = self.session.query(Type).filter(Type.id == typeid).first() 
        tagsOftype  = articletype.tags
        
        for tag in tags.split('-'):
            existance = [one for one in tagsOftype if one.name == tag]
            if len(existance) == 0:
                tagsobj.insert(0, Tag(tag, typeid))
            else:
                tagsobj.insert(0, existance[0])
        
        # 取不到aid，说明是新写文章
        if aid == None: 
            newarticle = Article(title,content,tagsobj)
            self.session.add(newarticle)
        else:
            # 否则就是修改了
            myarticle = self.session.query(Article).filter(Article.id == aid).first()
            myarticle.title = title
            myarticle.content = content
            myarticle.tags = tagsobj
            myarticle.changetime = datetime.now()
            
        self.session.commit()
        self.redirect('/admin/article', permanent=True) 


###################### 文章管理 ###########################
class ArticleManage(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def get(self):
        StaticData.__init__(self)
        data = self.session.query(Article).all()
        tagdict = {}
        for item in data:
            tagstr = '' if len(item.tags) == 0 else '<' + item.tags[0].type.name + '> '
            tagstr += " | ".join([tag.name for tag in item.tags])
            tagdict[item.id] = tagstr
        
        self.render('admin_blog.html', data = data , tagdict = tagdict)
        
class ArticleChange(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def get(self, aid):
        StaticData.__init__(self)
        blog = self.session.query(Article).filter(Article.id == aid).first()
        types = self.session.query(Type).all()
        tagstr = '-'.join([tag.name for tag in blog.tags])
        typeselected = 0 if len(blog.tags) == 0 else blog.tags[0].type.id
        if blog == None:
            self.write('no such id !') 
        else:
            self.render('admin_rewrite.html', blog = blog , types = types , tagstr = tagstr , typeselected = typeselected)
        
class ArticleDel(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def get(self, aid):
        StaticData.__init__(self)
        article = self.session.query(Article).filter(Article.id == aid).first()
        if article == None:
            self.write('no such id')
        else:
            self.session.delete(article)
            self.session.commit()
            self.redirect('/admin/article', permanent=True)  


#################### 上传 ###############################
class UploadManage(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def get(self): 
        StaticData.__init__(self)
        data = self.session.query(Upload).all()
        self.render('admin_upload.html' , data = data)

# 删除
from uploader import deleteFromBCS
class UploadDel(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def get(self, uid): 
        StaticData.__init__(self)
        up = self.session.query(Upload).filter(Upload.id == uid).first()
        if up == None:
            self.write('no such id !')
        else:
            self.session.delete(up)
            self.session.commit()
            deleteFromBCS(up.name)
            self.redirect('/admin/upload', permanent=True)  


##################### 类别 ##############################
class TypeManage(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def get(self): 
        StaticData.__init__(self)
        data = self.session.query(Type).all()
        self.render('admin_type.html', data = data)

class TypeDel(LoginValidateBase, StaticData):
    @tornado.web.authenticated
    def get(self , typeid):
        StaticData.__init__(self)
        type = self.session.query(Type).filter(Type.id == typeid).first()
        if type == None:
            self.write('no such id !')
        if len(type.tags) != 0:
            self.write('please delete all the related tags first!')
        else:
            self.session.delete(type)
            self.session.commit()
            self.redirect('/admin/type', permanent=True)        

class TypeChange(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def get(self , typeid):    
        StaticData.__init__(self) 
        newname = self.get_argument('newname',default='')
        type = self.session.query(Type).filter(Type.id == typeid).first()
        if type == None:
            self.write('no such id !')
        else:
            type.name = newname
            self.session.commit()
            self.redirect('/admin/type', permanent=True)        
        
class TypeAdd(LoginValidateBase, StaticData):
    @tornado.web.authenticated
    def post(self):     
        StaticData.__init__(self)
        newname = self.get_argument('newname',default=None)
        newforurl = self.get_argument('newforurl',default=None)
        pattern = re.compile(r'^[0-9a-zA-Z]+$')
        if pattern.match(newforurl):
            self.session.add(Type(newname, newforurl))
            self.session.commit()
            self.redirect('/admin/type', permanent=True) 
        else:
            self.write('please use num and alpha !')


###################### 标签 ##############################
class TagManage(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def get(self): 
        StaticData.__init__(self)
        data = self.session.query(Tag).all()
        self.render('admin_tag.html', data = data)
        
class TagDel(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def get(self, tagid):  
        StaticData.__init__(self)
        tag = self.session.query(Tag).filter(Tag.id == tagid).first()
        if tag == None:
            self.write('no such id !') 
        else:
            # 第三关联表无法删除，尝试使用原生SQL
            
            
            self.session.delete(tag)
            self.session.commit()
            self.redirect('/admin/tag', permanent=True)

class TagChange(LoginValidateBase, StaticData):
    @tornado.web.authenticated
    def get(self, tagid):  
        StaticData.__init__(self)
        newname = self.get_argument('newname',default='')
        tag = self.session.query(Tag).filter(Tag.id == tagid).first()
        if tag == None:
            self.write('no such id !')
        else:
            tag.name = newname
            self.session.commit()
            self.redirect('/admin/tag', permanent=True)

          
#################### 链接 ################################
class LinkManage(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def get(self): 
        StaticData.__init__(self)
        data = self.session.query(Link).all()
        self.render('admin_link.html',data = data)

class LinkAdd(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def post(self):
        StaticData.__init__(self)
        name = self.get_argument('linkname' , default='')
        url = self.get_argument('linkurl' , default='')
        self.session.add(Link(name,url))
        self.session.commit() 
        self.redirect('/admin/link', permanent=True)
        
class LinkDel(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def get(self, linkid):
        StaticData.__init__(self)
        link = self.session.query(Link).filter(Link.id == linkid).first()
        if link == None:
            self.write('ERROR , no such id ')
        else:
            self.session.delete(link)
            self.session.commit() 
            self.redirect('/admin/link', permanent=True)


#################### 日志 #################################
class LogManage(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def get(self): 
        StaticData.__init__(self)
        data = self.session.query(Log).all()
        self.session.commit()
        self.render('admin_log.html' , data = data)

class LogClear(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def get(self):
        StaticData.__init__(self)
        data = self.session.query(Log).all()
        for item in data:
            self.session.delete(item)
        self.session.commit()
        self.redirect('/admin/log', permanent=True)
        

################### 功能设置 ##############################
class SettingManage(LoginValidateBase, StaticData):
    @tornado.web.authenticated
    def get(self): 
        StaticData.__init__(self)
        settings = {}
        for item in self.session.query(Settings):
            settings[item.name] = item.content
            
        self.render('admin_func.html' , settings = settings)

#改 
class ChangeSettings(LoginValidateBase , StaticData):
    @tornado.web.authenticated
    def get(self):
        self.write('WRONG')

    @tornado.web.authenticated
    def post(self):
        StaticData.__init__(self)
        old_settings = self.session.query(Settings)
        for item in old_settings:
            newvalue = self.get_argument(item.name , default = None)
            if newvalue != None:
                item.content = newvalue
        self.session.commit()
        self.redirect('/admin/settings', permanent=True)

#改密码
import hashlib
class ChangePsw(LoginValidateBase, StaticData):
    @tornado.web.authenticated
    def post(self):
        StaticData.__init__(self)
        psw = self.session.query(Settings).filter(Settings.name=='BLOG_ADMIN_PASSWORD').one()
        oldpsw = self.get_argument('oldpsw', default = None)
        newpsw = self.get_argument('newpsw', default = None)
        if oldpsw == None or newpsw == None:
            self.write('<script language="javascript">alert("请勿输入任意空值！");self.location="/admin/settings";</script>')
        else:
            oldpsw_md5 = hashlib.md5(oldpsw).hexdigest()
            if oldpsw_md5 != psw.content:
                self.write('<script language="javascript">alert("原口令错误！");self.location="/admin/settings";</script>')
            else:
                psw.content = hashlib.md5(newpsw).hexdigest()
                self.session.commit()
                self.redirect('/admin/settings', permanent=True)
        
        
        
################### 博客统计 ##############################
class SumManage(LoginValidateBase, StaticData):
    @tornado.web.authenticated
    def get(self): 
        StaticData.__init__(self)
        data = {}
        data['blog_num'] = self.session.query(Article).count()
        data['type_num'] = self.session.query(Type).count()
        data['tag_num'] = self.session.query(Tag).count()
        data['file_num'] = self.session.query(Upload).count()
        self.render('admin_sum.html', data = data)


# For BAE
class InitBlog(tornado.web.RequestHandler):
    def get(self):
        initDatabase()
        self.write('初始化成功!初始管理账号密码admin.<br><a href="/admin/login">进入后台</a>')