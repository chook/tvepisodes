#!/usr/bin/python
## This script is used to produce DataTables for Google Visualization API
## It maps /SearchShow=%s to SearchShow Class defined below and operates on GET
## It builds a DataTable and returns it as a response
##
import cgi
import gviz_api
import logging
from google.appengine.api import urlfetch 
from xml.dom import minidom 
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
from google.appengine.ext import db
from datastore import *

__author__ = "Chen Harel"

class FetchUserPrefs(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  
  def post(self):
    # The content returned is a text/plain
    self.response.headers['Content-Type'] = 'text/plain'
    
    try:
        userid = self.request.get('uid')
        query = User.all()
        query.filter("userid = ", userid)
        user = query.get()
        self.response.out.write(user.friends_influence)
    except:
        self.response.out.write(50)
    return 
  def get(self):
      self.post()

class AssignUserPrefs(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  def get(self):
      self.post()
  def post(self):
    # The content returned is a text/plain
    self.response.headers['Content-Type'] = 'text/plain'
    
    # The following code handles the get request
    try:
        userid = self.request.get('uid') #int(self.request.get('userid'))
        inf = int(self.request.get('inf'))
        query = User.all()
        query.filter("userid = ", userid)
        user = query.get()
        user.friends_influence = inf
        user.put()
        self.response.out.write("True")
    except:
        self.response.out.write("False")
    return
    