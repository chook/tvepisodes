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

TVRAGE_SEARCH_URL = "http://www.tvrage.com/feeds/full_search.php?show="
#class Shows(db.Model):
#    showid = db.IntegerProperty(required=True)
#    name = db.StringProperty(required=True)
#    genres = db.StringListProperty()
#    country = db.StringProperty()
#    started_year = db.DateTimeProperty()
#    is_show_over = db.BooleanProperty()#required=True)

# This function parses a URL and returns a minidom object
def parse(url):    
  result = urlfetch.fetch(url)
  
  if result.status_code == 200:
    return minidom.parseString(result.content)
    #return

# This function builds a data table for the visualizations
def build_table_for_search(showName):
  url = 'http://www.tvrage.com/feeds/full_search.php?show=%s' % showName
#  on Nadav's computer, this next line is CRUCIAL otherwise nothing works!
#  url = url.encode("utf-8")
  dom = parse(url)

  # Init the dictionary for the data table
  dicShows = []

  shows = dom.getElementsByTagName('show')
#  print "number of shows - %s" % shows.length
#  print "number of shows - %s" % shows.item(1).nodeValue
#  print shows.firstChild.toxml()
  # Running on the show elements in the XML  
  for show in shows:

    dicShows.append({ 
        'showid': int(show.getElementsByTagName('showid')[0].firstChild.data), 
        'name'  : show.getElementsByTagName('name')[0].firstChild.data
    })
  dom.unlink();
  return dicShows 

def addDataToDS(showName):
    url = TVRAGE_SEARCH_URL + showName
#    url = url.encode("utf-8")
    dom = parse(url)

    # Init the dictionary for the data table
#   dicShows = []

    shows = dom.getElementsByTagName('show')
#  print "number of shows - %s" % shows.length
#  print "number of shows - %s" % shows.item(1).nodeValue
#  print shows.firstChild.toxml()
  # Running on the show elements in the XML  
    for show in shows:
    # Appending the showid as int and name as string
        showid = show.getElementsByTagName('showid')[0].firstChild.data
        name = show.getElementsByTagName('name')[0].firstChild.data
        country = show.getElementsByTagName('country')[0].firstChild.data
        
        showRecord = Show(showid = int(showid),
                           name = name,
                           country = country)
        print "entering to the datastore:<br>"
        print "showid = %s<br>" % showid
        print "name = %s<br>" % name
        print "country = %s<br>" % country
        print "==================================================<br>"
        showRecord.put()
        
#        print "show's name = %s" % showname
#        dicShows.append({ 
#                         'showid': int(show.childNodes[1].firstChild.data), 
#                         'name'  : show.childNodes[3].firstChild.data
#                         })
    dom.unlink();
#    return dicShows

def show_from_datastore():

    query = Show.gql("WHERE name = :name ",
                      name='Rescue Heroes')

    query2 = Show.gql("WHERE showid > 20000")
        
    results = query.fetch(1)
    for result in results:
        print "Name: " + result.name + "<br>"
        print "Country: " + result.country + "<br>"
#        print "Showid: " + str(result.showid)
        
    print "query2:<br>"
    print "=====================<br>"
    results = query2.fetch(1000)
    for result in results:
        print "Name: " + result.name + "<br>"
        print "Country: " + result.country + "<br>"
#        print "Showid: " + str(result.showid)
    
    
    

    
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
#        self.response.out.write("handleQueryResponse({'version':'0.5', "
#                                "'reqId':'%s', 'status':'OK', 'table': %s});" % (0, data_table.ToJSon(columns_order=("showid", "name"))))
        
        self.response.out.write(data_table.ToJSonResponse(columns_order=("showid", "name")))
    else:
        # No show name specified, return
        self.response.out.write("Search Show: Invalid usage\n")


class SearchAndStoreShow(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  def get(self):
    # The content returned is a text/plain
    self.response.headers['Content-Type'] = 'text/plain'
    
    # The show name from the GET method (http://.../SearchShow?ShowName=<SHOW>)
    showName = self.request.get('name')
    if(showName != ""):
        showName = showName.lower()
        
        # Trying to get the data table from memcache
#        dicShows = memcache.get(showName)
##        if dicShows is None:
#        dicShows = build_table_for_search(showName)
            
            # Add the dictionary to the memcache, log errors
#            if not memcache.add(showName, dicShows, 7200):
#                logging.error("Memcache set failed.")
        
        # Decide on the data table description
#        description = {"showid": ("number", "ID"),
#                       "name":   ("string", "Name")}
        
        # Build the data table object with description and shows dictionary
 #       data_table = gviz_api.DataTable(description)
#        data_table.LoadData(dicShows)
        
        # Write the object as a JSon response back to the caller
        #table = self.ToJSon(columns_order, order_by)
#        self.response.out.write("handleQueryResponse({'version':'0.5', "
#                                "'reqId':'%s', 'status':'OK', 'table': %s});" % (0, data_table.ToJSon(columns_order=("showid", "name"))))
        
        print "Entering information into the datastore<br>"
#        self.response.out.write("Entering information into the datastore")
        add_data_to_datastore(showName)

        print "showing a certain show in Datastore:<br>"
#        self.response.out.write("showing a certain show in Datastore:")
        show_from_datastore()
        #self.response.out.write(data_table.ToJSon(columns_order=("showid", "name")))
    else:
        # No show name specified, return
        self.response.out.write("Search Show: Invalid usage\n")
       
def addShowsFromSearch(searchString):
    
    print "Entering information into the datastore<br>"
#        self.response.out.write("Entering information into the datastore")
    addDataToDS(searchString)

#        print "showing a certain show in Datastore:<br>"
#        self.response.out.write("showing a certain show in Datastore:")
#       show_from_datastore()
        #self.response.out.write(data_table.ToJSon(columns_order=("showid", "name")))
        
def clearAllShows():
    
    query = db.GqlQuery("SELECT * FROM Show")
    results = query.fetch(1000)
    db.delete(results)
