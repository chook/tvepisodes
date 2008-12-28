#!/usr/bin/python
## This script is used to produce DataTables for Google Visualization API
## It maps /SearchShow=%s to SearchShow Class defined below and operates on GET
## It builds a DataTable and returns it as a response
##
import cgi
import gviz_api
from google.appengine.api import urlfetch 
from xml.dom import minidom 
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

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
  shows = []

  # Running on the show elements in the XML  
  for node in dom.getElementsByTagName('show'):
    # Appending the showid as int and name as string
    shows.append({ 
        'showid': int(node.childNodes[1].firstChild.data), 
        'name'  : node.childNodes[3].firstChild.data
    })
  return shows 

class MainPage(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  def get(self):
    self.response.out.write("Invalid usage")

class SearchShow(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  def get(self):
    showName = self.request.get('ShowName')
    self.response.headers['Content-Type'] = 'text/plain'
    if(showName != ""):
      shows = build_table_for_search(showName)
      description = {"showid": ("number", "ID"),
                     "name":   ("string", "Name")}
      
      data_table = gviz_api.DataTable(description)
      data_table.LoadData(shows)
      self.response.out.write(data_table.ToJSonResponse(columns_order=("showid", "name")))
    else:
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
