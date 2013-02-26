#-*- coding:utf-8 -*- 
from bae.core.wsgi import WSGIApplication

from blogxu.application import app

application = WSGIApplication(app)