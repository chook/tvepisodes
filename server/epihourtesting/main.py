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

__author__ = "Chen Harel"

# This function parses a URL and returns a minidom object
def parse(url):    
  result = urlfetch.fetch(url)
  
  if result.status_code == 200:
    return minidom.parseString(result.content)

# This function builds a data table for the visualizations
def build_table_for_search(showName):
  url = 'http://www.tvrage.com/feeds/full_search.php?show=%s' % showName
  dom = parse(url)

  # Init the dictionary for the data table
  dicShows = []

  # Running on the show elements in the XML  
  for node in dom.getElementsByTagName('show'):
    # Appending the showid as int and name as string
    dicShows.append({ 
        'showid': int(node.childNodes[1].firstChild.data), 
        'name'  : node.childNodes[3].firstChild.data
    })
  return dicShows 

class MainPage(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  def get(self):
    self.response.out.write("Invalid usage")

class SearchShow(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  def get(self):
    # The content returned is a text/plain
    self.response.headers['Content-Type'] = 'text/plain'
    
    # The show name from the GET method (http://.../SearchShow?ShowName=<SHOW>)
    showName = self.request.get('ShowName')
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
        description = {"showid": ("number", "ID"),
                       "name":   ("string", "Name")}
        
        # Build the data table object with description and shows dictionary
        data_table = gviz_api.DataTable(description)
        data_table.LoadData(dicShows)
        
        # Write the object as a JSon response back to the caller
        #table = self.ToJSon(columns_order, order_by)
        #self.response.out.write("handleQueryResponse({version:'0.5'," +
        #                        "reqId:'%s',status:'ok',table:%s});" % (0, data_table.ToJSon(columns_order=("showid", "name"))))
        self.response.out.write(data_table.ToJSonResponse(columns_order=("showid", "name")))
    else:
        # No show name specified, return
        self.response.out.write("Search Show: Invalid usage")

# Define the webapp applications and map the classes to different paths
application = webapp.WSGIApplication([('/', MainPage),
                                     ('/SearchShow', SearchShow)],
                                     debug=True)

# Main global function
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()