#! /usr/bin/env python
#coding=utf-8

import tornado.web 
from blogxu.models.entity import getSession
from blogxu.models.entity import Type,Tag,Article,Upload,Link,Settings,Log
from sqlalchemy import extract 
import markdown

######################################
# 前台展示相关核心处理方法           #
# Author: Xu                         #
# Date: 2013.2.22                    #
######################################


#页面通用数据
class ArticleBase(object):
    def __init__(self):
        self.session = getSession()
        #settings数据
        blogsettings = self.session.query(Settings).all()
        self.bloginfos = {}
        for item in blogsettings:
            self.bloginfos[item.name] = item.content
        self.title = 'HOME'
        
        #顶部导航栏数据
        self.types = {}
        for type in self.session.query(Type).all():
            self.types[type.forurl] = type.name
        self.typeactive = 'HOME'
        
# 继承自上面那个，多了些数据。上面那个用于文章阅读和about页面的渲染
class StaticBase(ArticleBase):
    def __init__(self):
        #需要手动init一下
        ArticleBase.__init__(self)
        #侧边：最近更新
        self.newlyupdate = self.session.query(Article).order_by(Article.changetime.desc())[:5] 
        
        #侧边：标签云. 同时生成跟tag.id对应的bootstrap风格的多彩样式映射
        self.tags = self.session.query(Tag).all()
        self.tagcss = {}
        tagcolors = ['success', 'primary', 'info', 'danger', 'inverse', 'warning']
        for tag in self.tags:
            self.tagcss[tag.id] = tagcolors[tag.id % 6]
        
        #侧边：归档 
        articlelist = self.session.query(Article).order_by(Article.pubtime.desc()).all()  
        topyear =  articlelist[0].pubtime.year
        bottomyear =  articlelist[len(articlelist) - 1].pubtime.year
        self.articlebydate = []
        for year in range(bottomyear, topyear + 1):
            for month in range(1,13):
                nums = len([article for article in articlelist if article.pubtime.year == year and article.pubtime.month == month])
                if nums != 0:
                    self.articlebydate.insert(0,{ 'year':year, 'month' : month , 'num' : nums})
        
        #侧边：链接
        self.links = self.session.query(Link).all()

# 分页
class Pagination(object):
    def __init__(self):
        self.pre = '';
        self.next = '';
        self.pages = [];
        self.current = '';
        self.action = ''
         
#通用构造分页的函数
def generatePagination(action , bloglist , targetpage):

    pagination = Pagination()
    pagination.current = targetpage
    # 最大页数（规定一页10条）
    maxpage = len(bloglist)
    pagination.pages = range(1 ,maxpage / 10 + 2)
    pagination.pre = str(targetpage - 1) if targetpage - 1 in pagination.pages else str(targetpage)
    pagination.next = str(targetpage + 1) if targetpage + 1 in pagination.pages else str(targetpage)
    pagination.action = action
    #  分开
    bloglist = bloglist[(targetpage - 1) * 10 : targetpage * 10]
    return bloglist, pagination
    


#由于前台文章列表数据项跟实际Article实体不太一样，定义这个数据容器类做一个转换     
class ArticleListObject(object):
    def __init__(self, article):
        self.id = article.id
        self.title = article.title
        self.subcontent = article.content[:300] + ' ...'
        self.type = '无' if len(article.tags) == 0 else article.tags[0].type.name
        self.typelink = '' if len(article.tags) == 0 else article.tags[0].type.forurl
        self.tags = {}
        for tag in article.tags:
            self.tags[tag.id] = tag.name
        self.year = article.pubtime.year
        self.month = article.pubtime.strftime('%b')
        self.day = article.pubtime.day


# 主页
class Home(tornado.web.RequestHandler , StaticBase):
    def get(self):  
        self.redirect('/home', permanent=True) 

# home和各大type的通用列表展示页
class ListArticles(tornado.web.RequestHandler , StaticBase):
    def get(self,word):
        StaticBase.__init__(self)
        bloglist = []
        targetpage = int(self.get_argument('page',default='1'))
        #主页，展示所有文章条目
        if word == 'home':
            self.title = 'HOME'
            self.typeactive = 'HOME'
            for one in self.session.query(Article).order_by(Article.pubtime).all():
                bloglist.insert(0, ArticleListObject(one))
                
            bloglist, self.pagination = generatePagination('/home?page=', bloglist, targetpage)  
        
        #指定type页，先判断有没有这个类型
        elif word in [type.forurl for type in self.session.query(Type).all()]:
            self.title = self.session.query(Type).filter(Type.forurl == word).first().name
            self.typeactive = word
            
            for one in self.session.query(Article).all():
                bloglist.insert(0, ArticleListObject(one)) 
            # 由于Article表没存type，只能迂回通过tags来判断type了，多走了几步 -_-// 
            for item in bloglist[:]:
                if item.typelink != word: 
                    bloglist.remove(item)
                    
            bloglist, self.pagination = generatePagination('/'+word +'?page=', bloglist, targetpage)  
            
        #没有这个类型抛404
        else:
            raise tornado.web.HTTPError(404, "no such type")
        self.render("blog_list.html", bloglist = bloglist)

class ListByTag(tornado.web.RequestHandler , StaticBase):
    def get(self,tagid):
        StaticBase.__init__(self)
        targetpage = int(self.get_argument('page',default='1'))
        self.pagination = Pagination()
        tag = self.session.query(Tag).filter(Tag.id == tagid).one()
        bloglist = [ArticleListObject(article) for article in tag.articles]
        
        bloglist, self.pagination = generatePagination('/q/tag/' + str(tag.id) + '?page=', bloglist, targetpage)  
        
        self.title = "TAG:" + tag.name
        self.typeactive = "new-li"
        self.render("blog_list.html", bloglist = bloglist, thisquery = "/q/tag/" + str(tag.id) )

class ListByDate(tornado.web.RequestHandler , StaticBase):
    def get(self,year,month): 
        StaticBase.__init__(self)  
        targetpage = int(self.get_argument('page',default='1'))
        self.pagination = Pagination()
        bloglist = [ArticleListObject(article) for article in self.session.query(Article).all() if article.pubtime.year == int(year) and article.pubtime.month == int(month)]
        
        bloglist, self.pagination = generatePagination('/q/date/' + year + '/' + month + '?page=', bloglist, targetpage)
        
        self.title = "归档：" + str(year) + "年" + str(month) + "月"
        self.typeactive = "new-li"
        self.render("blog_list.html", bloglist = bloglist, thisquery = "/q/date/" + year + "/" + month )

class ListSearch(tornado.web.RequestHandler , StaticBase):
    def get(self): 
        StaticBase.__init__(self)
        targetpage = int(self.get_argument('page',default='1'))
        self.pagination = Pagination()
        keyword = self.get_argument('keyword',default='')
        blogs = []
        for blog in self.session.query(Article).all():
            if keyword in blog.title or keyword in blog.content:
                blogs.insert(0, blog)
                
        bloglist = [ArticleListObject(article) for article in blogs]
        
        bloglist, self.pagination = generatePagination('/q/search?keyword=' + keyword + '&page=', bloglist, targetpage)
        
        self.title = "搜索：" + keyword.encode('utf8')
        self.typeactive = "new-li"
        self.render("blog_list.html", bloglist = bloglist, thisquery = "" )
        

# 仅仅从ArticleBase继承，减少一些SQL查询
class ReadArticle(tornado.web.RequestHandler ,ArticleBase):
    def get(self,aid):
        ArticleBase.__init__(self)
        article = self.session.query(Article).filter(Article.id == aid).first()
        if article == None:
            raise tornado.web.HTTPError(404, "no such article")
        self.typeactive = 'new-li'
        self.title = article.title
        
        articletitle = article.title
        pubdate = article.pubtime.strftime('%Y-%m-%d日%H:%M:%S')
        articletype = '无归类' if len(article.tags) == 0 else article.tags[0].type.name
        markdowncontent = markdown.markdown(article.content, ['codehilite'])
        
        tagcolors = ['success', 'primary', 'info', 'danger', 'inverse', 'warning']
        tagcss = {}
        tags = article.tags
        for tag in tags:
            tagcss[tag.id] = tagcolors[tag.id % 6]
        
        thisquery = '/p/' + str(article.id)
        
        self.render("blog_read.html" , thisquery = thisquery, articletitle = articletitle, markdowncontent = markdowncontent , pubdate = pubdate , articletype = articletype , tagcss = tagcss ,tags = tags)



import os
# 关于。。  写在template目录下的aboutme.md中，markdown语法
class ShowAbout(tornado.web.RequestHandler, ArticleBase):
    def get(self):
        ArticleBase.__init__(self)
        about_path = os.path.join(self.get_template_path(),'aboutme.md') 
        aboutcontent = markdown.markdown(open(about_path).read(),['codehilite'])
        
        self.render('about.html', aboutcontent = aboutcontent)