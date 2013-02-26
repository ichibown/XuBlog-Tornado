#! /usr/bin/env python
#coding=utf-8

from urls import blogurls

import tornado.wsgi
import os

######################################
# tornado框架配置                    #
# Author: Xu                         #
# Date: 2013.2.19                    #
######################################


SETTINGS = dict(
    debug = False,
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    cookie_secret="dEr2Viz6TrqsoQVbQCRdxUmzKB5q40U0jYtp+fnsAOY=",
    login_url="/admin/login",
    autoescape=None,
)

#cookie_secret生成方式：base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)

app = tornado.wsgi.WSGIApplication(
                    handlers = blogurls,
                    **SETTINGS
)