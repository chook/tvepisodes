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
TVRAGE_SHOWINFO_URL = "http://www.tvrage.com/feeds/showinfo.php?sid="

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
       
def getXMLField(tag, subTagName):
    subTag = tag.getElementsByTagName(subTagName)[0].firstChild
    if subTag:
        return subTag.data

def addShow(showid):
    print "Entering information into the datastore<br>"
    url = TVRAGE_SHOWINFO_URL + showid
#    url = url.encode("utf-8")
    dom = parse(url)

    show = dom.getElementsByTagName('Showinfo')
    # Appending the showid as int and name as string
    name = getXMLField(dom, 'showname')
    started_year = int(getXMLField(dom, 'started'))
    country = getXMLField(dom, 'origin_country')
    if getXMLField(dom, 'ended'):
        is_show_over = True
    else:
        is_show_over = False
    showGenres = dom.getElementsByTagName('genre')
    
    # creating the show in the DS
    newShow = Show(showid = int(showid),
                   name = name,
                   country = country,
                   started_year = started_year,
                   is_show_over = is_show_over)
    # running over the genres
    showGenresToAdd = []
    for showGenre in showGenres:
        genreName = showGenre.firstChild.data
        # checking if the genre exists
        query = Genre.all()
        query.filter("name = ", genreName)
        genre = query.get() 
        if not genre:
            print "the genre %s doesn't exist in the DS, adding it<br>" % genreName
            # adding the user to the DS
            newGenre = Genre(name = genreName)
            newGenre.put()
            genre = newGenre
        showGenresToAdd += [genre.key()]
#        newShow = genres.put(genre)
    newShow.genres = showGenresToAdd   
    newShow.put()

                        
    print "entering show to the datastore:<br>"
    print "showid: " + showid + "<br>"
    print "showname: " + name + "<br>"
    print "started_year: " + str(started_year) + "<br>"
    print "country: " + country + "<br>"
    print "is_show_over?: " + str(is_show_over) + "<br>"
    print "show's genres:<br>"
    for genre in showGenres:
        print genre.firstChild.data + "<br>"
    
    dom.unlink();
    return
        
    
    
    
    
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

def clearAllGenres():
    
    query = db.GqlQuery("SELECT * FROM Genre")
    results = query.fetch(1000)
    db.delete(results)