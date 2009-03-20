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
from datetime import *

__author__ = "Chen Harel"

TVRAGE_SEARCH_URL = "http://www.tvrage.com/feeds/full_search.php?private_feed=yes&show="
TVRAGE_SHOWINFO_URL = "http://www.tvrage.com/feeds/showinfo.php?private_feed=yes&sid="

# This function parses a URL and returns a minidom object
def parse(url):  
  try:  
    result = urlfetch.fetch(url)

    if result.status_code == 200:
        return minidom.parseString(result.content)
  except:
      return None
    
def build_table_for_search(showName):
  url = TVRAGE_SEARCH_URL + showName

  try:
      url = url.replace(' ','%20')
      url = url.encode("utf-8")
  except:
      logging.debug('Can''t encode url to be utf-8 ot change space to %20')
  
  try:
      logging.debug('about to get: ' + url)
      dom = parse(url)
  
  # Handling parsing errors
  except:
      dom = None
      
  if dom is None :
      return [{'showid'  : 0,
               'name'    : 'Error In Search',
               'started' : '',
               'seasons' : 0,
               'country' : '',
               'classification' : '',
               'status' : '',
               'link'    : '',
               'airtime' : '',
               'airday' : '',
               'favorite' : '0'}]
  
  return [{'showid'  : int(getXMLField(node, 'showid')),
           'name'    : getXMLField(node, 'name'),
           'started' : getXMLField(node, 'started'),
           'seasons' : int(getXMLField(node, 'seasons')),
           'country' : getXMLField(node, 'country'),
           'classification' : getXMLField(node, 'classification'),
           'status' : getXMLField(node, 'status'),
           'link'    : getXMLField(node, 'link'),
           'airtime' : getXMLField(node, 'airtime'),
           'airday' : getXMLField(node, 'airday'),
           'favorite' : '0'}
            for node in dom.getElementsByTagName('show')]

class SearchShow(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  def get(self):
    # The content returned is a text/plain
    self.response.headers['Content-Type'] = 'text/plain'

    # The show name from the GET method (http://.../SearchShow?ShowName=<SHOW>)
    showName = self.request.get('name')
    reqId = self.request.get('tqx')
    userid  = self.request.get('uid')
    
    try :
        reqId = reqId[6:8]
        if reqId == None or reqId == '' :
            reqId = 0
    except :
        reqId = 0
        
    if(showName != ""):
        showName = showName.lower()
        
        # Get user to disable shows he already favors
        
        
        # Trying to get the data table from memcache
        dicShows = memcache.get(showName)
        if dicShows is None:
            dicShows = build_table_for_search(showName)
            
            # Add the dictionary to the memcache, log errors
            if not memcache.add(showName, dicShows, 7200):
                logging.error("Memcache set failed.")
        
        if userid is not '':
            query = User.all()
            query.filter("userid = ", userid)
            user = query.get()
            userFavShows = []
            for k in user.favorite_shows:
                show = db.get(k)
                if show is not None:
                    userFavShows.append(show.showid)
    
            for show in dicShows:
                if show.get("showid") in userFavShows:
                    show["favorite"] = "1" 
        
        # Decide on the data table description
        description = {"showid"         : ("number", "ID"),
                       "name"           : ("string", "Name"),
                       "started"        : ("string", "Year Started"),
                       "seasons"        : ("number", "Seasons Number"),
                       "country"        : ("string", "Original Country"),
                       "classification" : ("string", "Classification"),
                       "status"         : ("string", "Status"),
                       "link"           : ("string", "Link"),
                       "airtime"        : ("string", "Air Time"),
                       "airday"         : ("string", "Air Day"),
                       "favorite"       : ("string", "Favorite")}               
        
        # Build the data table object with description and shows dictionary
        data_table = gviz_api.DataTable(description)
        data_table.LoadData(dicShows)
        
        # Write the object as a JSon response back to the caller
        try:
            logging.debug('About to call ToJSonResponse from search shows')
            self.response.out.write(data_table.ToJSonResponse(columns_order=("showid",
                                                                         "name",
                                                                         "started",
                                                                         "seasons",
                                                                         "country",
                                                                         "classification",
                                                                         "status",
                                                                         "link",
                                                                         "airtime",
                                                                         "airday",
                                                                         "favorite"),
                                                          order_by=(),
                                                          req_id=reqId))
        except:
            logging.error('visu in search shows failed')
            #for show in dicShows:
            #    show['name'] = show['name'].unicode("utf-8")
            data_table.LoadData(dicShows)
            self.response.out.write(data_table.ToJSonResponse(columns_order=("showid",
                                                                         "name",
                                                                         "started",
                                                                         "seasons",
                                                                         "country",
                                                                         "classification",
                                                                         "status",
                                                                         "link",
                                                                         "airtime",
                                                                         "airday",
                                                                         "favorite"),
                                                          order_by=(),
                                                          req_id=reqId))
    else:
        # No show name specified, return the best shows
        self.response.out.write('Invalid')

# Gets the top shows
class TopShows(webapp.RequestHandler):
  def get(self):
    # The content returned is a text/plain
    self.response.headers['Content-Type'] = 'text/plain'
    FAVORITE_SHOWS_KEY = "favoriteshows"
    reqId = self.request.get('tqx')
    userid = self.request.get('uid')
    
    try:
        limit = self.request.get('limit')
    except:
        limit = '5'
    if limit == '' or limit is None:
        limit = '5'

    try :
        reqId = reqId[6:8]
        if reqId == None or reqId == '' :
            reqId = 0
    except :
        reqId = 0
        
    # Trying to get the data table from memcache
    dicShows = memcache.get(FAVORITE_SHOWS_KEY)
    if dicShows is None:
        shows = db.GqlQuery('SELECT * FROM Show ORDER BY showcount DESC LIMIT %s' % limit)
        dicShows = [{'showid' : s.showid,
                     'name'   : s.name,
                     'started': s.started_year,
                     'seasons': s.seasons,
                     'country': s.country,
                     'classification' : s.classification,
                     'status' : s.status,
                     'link'   : s.link,
                     'airtime': s.airtime,
                     'airday' : s.airday,
                     'count'  : s.showcount,
                     'favorite' : '0'} for s in shows]
                   
        # Add the dictionary to the memcache, log errors
        if not memcache.add(FAVORITE_SHOWS_KEY, dicShows, 7200):
            logging.error("Memcache set failed.")
    
    # Get user to disable shows he already favors
    if userid is not '':
        query = User.all()
        query.filter("userid = ", userid)
        user = query.get()
        userFavShows = []
        for k in user.favorite_shows:
            show = db.get(k)
            if show is not None:
                userFavShows.append(show.showid)

        for show in dicShows:
            if show.get("showid") in userFavShows:
                show["favorite"] = "1" 
    
    # Decide on the data table description
    description = {"showid"         : ("number", "ID"),
                   "name"           : ("string", "Name"),
                   "started"        : ("string", "Year Started"),
                   "seasons"        : ("number", "Seasons Number"),
                   "country"        : ("string", "Original Country"),
                   "classification" : ("string", "Classification"),
                   "status"         : ("string", "Status"),
                   "link"           : ("string", "Link"),
                   "airtime"        : ("string", "Air Time"),
                   "airday"         : ("string", "Air Day"),
                   "count"          : ("number", "Count"),
                   "favorite"       : ("string", "Favorite")}
    
    # Build the data table object with description and shows dictionary
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(dicShows)
    
    # Write the object as a JSon response back to the caller
    self.response.out.write(data_table.ToJSonResponse(columns_order=("showid",
                                                                     "name",
                                                                     "started",
                                                                     "seasons",
                                                                     "country",
                                                                     "classification",
                                                                     "status",
                                                                     "link",
                                                                     "airtime",
                                                                     "airday",
                                                                     "count",
                                                                     "favorite"),
                                                      order_by=("count","desc"),
                                                      req_id=reqId))


def getXMLField(tag, subTagName):
    try:
        subTag = tag.getElementsByTagName(subTagName)[0].firstChild
    except:
        subTag = None
    if subTag:
        return subTag.data
    else:
        return None

# This function retrieves information from TVRAGE and enters it to the DS
def addShow(showid):
    url = TVRAGE_SHOWINFO_URL + showid
    dom = parse(url)
    if dom is None:
        return False
    else :
        show = dom.getElementsByTagName('Showinfo')
    
        # Checking if there is a name to the show, if not - error
        name = getXMLField(dom, 'showname')
        if name is None:
            return False       
        else:
            link = getXMLField(dom, 'showlink')
            started_year = int(getXMLField(dom, 'started'))
            startdate = getXMLField(dom, 'startdate')
            endeddate = getXMLField(dom, 'ended')
            seasons   = getXMLField(dom, 'seasons')
            country = getXMLField(dom, 'origin_country')
            status = getXMLField(dom, 'status')
            classification = getXMLField(dom, 'classification')
            runtime = getXMLField(dom, 'runtime')
            network = getXMLField(dom, 'network')
            airtime = getXMLField(dom, 'airtime')
            airday = getXMLField(dom, 'airday')
            timezone = getXMLField(dom, 'timezone')
    
#    try:
#        airtimesplit = airtime.split(":")
#        date1 = datetime(2000,1,1,int(airtimesplit[0]), int(airtimesplit[1],0))
#        x = timedelta(0,int(timezone[4:5])*60*60)
#        if timezone[3:4] == "+":
#            date1 -= x
#        else:
#            date1 += x
#        airtime = str(date1.hour).zfill(2) + ":" + str(date1.minute).zfill(2)
#    except:
#        airtime = getXMLField(dom, 'airtime')
        
    if endeddate:
        is_show_over = True
    else:
        is_show_over = False
    
    try:
        # creating the show in the DS
        newShow = Show(showid = int(showid),
                       name = name,
                       country = country,
                       started_year = started_year,
                       is_show_over = is_show_over,
                       link = link,
                       start_date = startdate,
                       ended_date = endeddate,
                       seasons = int(seasons),
                       status = status,
                       classification = classification,
                       runtime = int(runtime),
                       network = network,
                       airtime = airtime,
                       airday = airday,
                       timezone = timezone,
                       nextdate = '1900-01-01',
                       prevdate = '1900-01-01')
        
        # running over the genres
        showGenres = dom.getElementsByTagName('genre')
        showGenresToAdd = []
        
        for showGenre in showGenres:
            genreName = showGenre.firstChild.data
            
            # checking if the genre exists
            query = Genre.all()
            query.filter("name = ", genreName)
            genre = query.get() 
            if not genre:
                # adding the user to the DS
                newGenre = Genre(name = genreName)
                newGenre.put()
                genre = newGenre
                
            showGenresToAdd.append(genreName)
 
        newShow.genres = showGenresToAdd   
        newShow.put()
        return True
    finally:
        dom.unlink();
    return False

## TODO: Remove this functions
def clearAllShows():
    query = db.GqlQuery("SELECT * FROM Show")
    results = query.fetch(1000)
    db.delete(results)
def clearAllGenres():
    query = db.GqlQuery("SELECT * FROM Genre")
    results = query.fetch(1000)
    db.delete(results)
    
class ClearCache(webapp.RequestHandler):
    def get(self):
        memcache.flush_all()
