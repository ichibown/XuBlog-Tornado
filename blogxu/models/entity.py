#! /usr/bin/env python
#coding=utf-8

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String , Sequence , DateTime , ForeignKey, Table, Text
from sqlalchemy.orm import relationship, backref
from datetime import datetime


######################################
# 数据库ORM定义，使用SQLAlchemy模块  #
# Author: Xu                         #
# Date: 2013.2.20                    #
######################################


# Type 实体类  
class Type(Base):
    __tablename__ = 'blog_type'
    
    id = Column(Integer,Sequence('type_id_seq'),primary_key=True)
    name = Column(String(20),nullable=False,unique=True)
    forurl = Column(String(10),nullable=False,unique=True)
    createtime = Column(DateTime,nullable=False)
    
    tags = relationship('Tag', order_by='Tag.id', backref='Type')
    
    def __init__(self, name , forurl):
        self.name = name 
        self.forurl = forurl
        self.createtime = datetime.now()

    def __repr__(self):
       return "<Type('%s','%s')>" % (self.name, self.createtime)

    
# 一个多对多关联。 Article <---> Tag
article_tag = Table('article_tag', Base.metadata,
     Column('article_id', Integer, ForeignKey('blog_article.id')),
     Column('tag_id', Integer, ForeignKey('blog_tag.id'))
)


# Tag 实体类
class Tag(Base):
    __tablename__ = 'blog_tag'
    
    id = Column(Integer,Sequence('tag_id_seq'),primary_key=True)
    name = Column(String(20),nullable=False,unique=True)
    createtime = Column(DateTime , nullable=False)
    type_id =Column(Integer, ForeignKey('blog_type.id'))
    
    type = relationship('Type', backref=backref('blog_tag', order_by=id))
    articles = relationship('Article', secondary=article_tag, backref='blog_tag',passive_deletes=True)
    
    def __init__(self, name , type):
        self.name = name 
        self.createtime = datetime.now()
        self.type_id = type
    
    def __repr__(self):
       return "<Tag('%s')>" % (self.name)


# 文章 实体类
class Article(Base):
    __tablename__ = 'blog_article'
    
    id = Column(Integer,Sequence('article_id_seq'),primary_key=True)
    title = Column(String(60), nullable=False)
    content = Column(Text, nullable=False)
    pubtime = Column(DateTime , nullable = False)
    changetime = Column(DateTime , nullable = False) 
    
    tags = relationship('Tag', secondary=article_tag, backref='blog_article',passive_deletes=True)    
    
    
    def __init__(self, title , content , tags):
        self.title = title 
        self.content = content
        self.pubtime = datetime.now()
        self.changetime = datetime.now()
        self.tags = tags
    
    def __repr__(self):
       return "<Article('%s')>" % (self.title)
    
# 上传的文件
class Upload(Base):
    __tablename__ = 'blog_upload'
    
    id = Column(Integer,Sequence('upload_id_seq'),primary_key=True)
    type = Column(String(10), nullable = False)
    name = Column(String(50), nullable = False)
    createtime = Column(DateTime , nullable = False)
    url = Column(String(100), nullable = False)
    
    def __init__(self, type, name, url):
        self.name = name 
        self.type = type
        self.url = url
        self.createtime = datetime.now()
        
    def __repr__(self): 
        return "<Upload('%s','%s')>" % (self.name, self.url)
    

# 主页链接
class Link(Base):
    __tablename__ = 'blog_link'
    
    id = Column(Integer,Sequence('link_id_seq'),primary_key=True) 
    name = Column(String(20), nullable = False)
    url = Column(String(60), nullable = False)
    createtime = Column(DateTime , nullable = False)

    
    def __init__(self, name, url):
        self.name = name  
        self.url = url
        self.createtime = datetime.now()
        
    def __repr__(self): 
        return "<Link('%s','%s')>" % (self.name, self.url)
    
# 博客各种设置项
class Settings(Base):
    __tablename__ = 'blog_settings'
    
    id = Column(Integer,Sequence('settings_id_seq'),primary_key=True) 
    name = Column(String(20), nullable = False, unique=True)
    content = Column(Text, nullable = True) 
    
    def __init__(self, name, content):
        self.name = name  
        self.content = content 
        
    def __repr__(self): 
        return "<Settings('%s','%s')>" % (self.name, self.content)


#待定：可以考虑对于关键行为写一些日志,记录来访ip、进行的行为。利用 decorator的AOP模式
class Log(Base):
    __tablename__ = 'blog_log'

    id = Column(Integer,Sequence('log_id_seq'),primary_key=True) 
    action = Column(String(20))
    ip = Column(String(20))
    time = Column(Text, nullable = False) 
    info = Column(String(50))
    
    def __init__(self,action,ip ,info):
        self.action = action  
        self.ip = ip
        self.time = datetime.now()
        self.info = info 
        
    def __repr__(self): 
        return "<Log('%s','%s')>" % (self.action, self.ip)



# 一些通用操作
from settings import DBSETTINGS
from settings import BLOG_SETTINGS_DEFAULTS as dbdefaults
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker

def getDbURL():
    return 'mysql://%s:%s@%s:%d/%s?charset=%s' % (DBSETTINGS['db_user'] ,DBSETTINGS['db_password'] , DBSETTINGS['db_host'], DBSETTINGS['db_port'] , DBSETTINGS['db_name'] , DBSETTINGS['db_encode'])


def getSession():
    engine = create_engine(getDbURL())  
    Session = sessionmaker(bind=engine)
    return Session() 


# 初始化数据库，包括建库和初始化部分数据
def initDatabase():
    engine = create_engine(getDbURL())  
    Base.metadata.create_all(engine) 
    datas = []
    for k,v in dbdefaults.items():
        datas.insert(0, Settings(k,v))
    session = getSession()
    session.add_all(datas)
    session.commit()

#s = getSession()
##s.add(Type('tornado'))
##s.add(Type('django'))
##
##s.add(Type('django22'))
##
##
##s.add(Type('django333'))
#
#
#s.add(Tag('android',8))
#s.add(Tag('android',9))
#s.add(Tag('android',10))
#
#s.commit()