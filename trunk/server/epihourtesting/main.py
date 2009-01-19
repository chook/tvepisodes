#!/usr/bin/python
## This script is used to produce DataTables for Google Visualization API
## It maps /SearchShow=%s to SearchShow Class defined below and operates on GET
## It builds a DataTable and returns it as a response
##
import cgi
import os
import gviz_api
import logging
from opensocial import *
from google.appengine.api import urlfetch 
from xml.dom import minidom 
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache

import wsgiref
import wsgiref.handlers

__author__ = "Chen Harel"

PARAM = "__PARAM__"

# square = FunctionWrap("square", lambda x:x**2, "(%s)^2" % PARAM)

class Handler(webapp.RequestHandler):
	
  def get(self):
    self.test_friends('03067092798963641994')
 
  def get_container(self):
    config = ContainerConfig(oauth_consumer_key='orkut.com:623061448914',
        oauth_consumer_secret='uynAeXiWTisflWX99KU1D2q5',
        server_rest_base='http://sandbox.orkut.com/social/rest/',
        server_rpc_base='http://sandbox.orkut.com/social/rpc/')
    return ContainerContext(config)
    
  def test_friends(self, user_id):
    container = self.get_container()
    
    batch = RequestBatch()
    batch.add_request('me', request.FetchPersonRequest(user_id))
    batch.add_request('friends',
                      request.FetchPeopleRequest(user_id, '@friends'))
    batch.send(container)
    
    me = batch.get('me')
    friends = batch.get('friends')
    
    self.response.out.write('<h3>Test</h3>')
    self.output(me, friends)

  def output(self, me, friends):
    self.response.out.write('%s\'s Friends: ' % me.get_display_name())
    if not friends:
      self.response.out.write('You have no friends.')
    else:
      self.response.out.write('<ul>')
      for person in friends:
        self.response.out.write('<li>%s</li>' % person.get_display_name())
      self.response.out.write('</ul>')

class FunctionWrap(object):
	def __init__(self, name, func, rep):
		self.name = name
		self.func = func
		self.rep = rep
	
	def __repr__(self):
		return self.rep.replace(PARAM,"X")
	
	def calc(self, obj):
		return self.func(obj)
		
	def pretty(self, param):
		return self.rep.replace(PARAM,param)

class Formula(object):
	def __init__(self, name, funcs = []):
		self.name = name
		self.funcs = funcs
	
	def __repr__(self):
		return " + ".join(["%s" % (func,) for func in self.funcs])
		
	def pretty(self, param_names):
		return " + ".join([func.pretty(param) for (func,param) in zip(self.funcs, param_names)])
		
	def calc(self, params):
		return sum([func.calc(param) for (func,param) in zip(self.funcs,params)])

# This function parses a URL and returns a minidom object
def parse(url):    
  result = urlfetch.fetch(url)
  
  if result.status_code == 200:
    return minidom.parseString(result.content)

def getXMLField(tag, subTagName):
    subTag = tag.getElementsByTagName(subTagName)[0].firstChild
    if subTag:
        return subTag.data
    return None

# This function builds a data table for the visualizations
def build_table_for_search(showName):
  url = 'http://www.tvrage.com/feeds/full_search.php?show=%s' % showName
  dom = parse(url)

  return [{'showid'  : int(getXMLField(node, 'showid')),
		   'name'    : getXMLField(node, 'name'),
		   'started' : getXMLField(node, 'started'),
		   'seasons' : int(getXMLField(node, 'seasons')),
		   'country' : getXMLField(node, 'country'),
		   'link'    : getXMLField(node, 'link')}
		    for node in dom.getElementsByTagName('show')]
  
#  return dicShows

class Gadget(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  def get(self):
    url = 'gadget.html'
    result = urlfetch.fetch(os.path.join(os.path.dirname(__file__), 'gadget.html'))
    self.response.out.write(result.content)


class MainPage(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  def get(self):
    showId = self.request.get('ShowId')
    con = False
    for i in xrange(10):
        url = "http://images.tvrage.net/shows/%s/%s.jpg" % (i, showId)
        result = urlfetch.fetch(url)
        if result.status_code != 404:
            self.response.out.write(url)
            con = True
            break
    if con == False:
        self.response.out.write("Invalid usage")

class SearchShow(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  def get(self):
    # The content returned is a text/plain
    self.response.headers['Content-Type'] = 'text/plain'
    
    # The show name from the GET method (http://.../SearchShow?ShowName=<SHOW>)
    showName = self.request.get('ShowName')
    reqId = self.request.get('tqx')
    
    try :
        reqId = reqId[6:8]
        if reqId == None or reqId == '' :
            reqId = 0
    except :
        reqId = 0
        
    if(showName != ""):
        showName = showName.lower()
        
        # Trying to get the data table from memcache
        dicShows = memcache.get(showName)
        if dicShows is None:
            dicShows = build_table_for_search(showName)
            
            # Add the dictionary to the memcache, log errors
            if not memcache.add(showName, dicShows, 7200):
                logging.error("Memcache set failed.")
        
        # Decide on the data table description
        description = {"showid" : ("number", "ID"),
                       "name"   : ("string", "Name"),
                       "started": ("string", "Date Started"),
                       "seasons": ("number", "Seasons Number"),
                       "country": ("string", "Original Country"),
                       "link"   : ("string", "Link")}
        
        # Build the data table object with description and shows dictionary
        data_table = gviz_api.DataTable(description)
        data_table.LoadData(dicShows)
        
        # Write the object as a JSon response back to the caller
        self.response.out.write(data_table.ToJSonResponse(columns_order=("showid",
																		  "name",
																		  "started",
																		  "seasons",
																		  "country",
																		  "link"),
														  order_by=(),
														  req_id=reqId))
    else:
        # No show name specified, return the best shows
        self.response.out.write('Invalid')
        
        #shows = db.GqlQuery('SELECT * FROM Show ORDER BY showcount DESC LIMIT 5')
        #dicGenres = [{'name' : g.name , 'count': g.showcount} for g in shows]
        
# Define the webapp applications and map the classes to different paths
application = webapp.WSGIApplication([('/', MainPage),
                                      ('/SearchShow', SearchShow),
                                      ('/Gadget', Gadget),
                                      ('/Handler', Handler)],
                                     debug=True)

# Main global function
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
