from google.appengine.ext import webapp
from google.appengine.ext import db
from django.utils import simplejson as json
from datastore import *
from shows import *
from datetime import *
import time
import datetime
import logging
__author__ = "Nadav Shamgar"

            
def parse(url):    
  result = urlfetch.fetch(url)
  if result.status_code == 200:
    return minidom.parseString(result.content)

def getXMLField(tag, subTagName):
    try:
        subTag = tag.getElementsByTagName(subTagName)[0].firstChild
    except:
        subTag = None
    if subTag:
    #    if '\x96' in subTag.data:
        return subTag.data
    return subTag

# This function builds a data table for the visualizations
def build_table_for_search(showName):
  url = 'http://www.tvrage.com/feeds/episode_list.php?private_feed=yes&sid=%s' % showName
  
  try:
      dom = parse(url)
  except:
      dom = None
      logging.error('Error getting in favorites: ' + url)
  return dom

def stringToDate(str):
    try:
        return datetime.date(int(str[0:4]), int(str[5:7]), int(str[8:10]))
    except:
        return None
        

class AddFavorite(webapp.RequestHandler):
    # this function is invoked when a user sends a POST request
    def post(self):
        
        self.response.headers['Content-Type'] = 'text/plain'

        userid = self.request.get('uid')
        showid = self.request.get('sid')
        logging.error('userid %s showid %s' % (userid, showid))
        
        if addFavorite(userid, showid):
            self.response.out.write("Add " + showid)
        else:
            self.response.out.write("Add 0")

    # This function is invoked when a user sends a get request
    def get(self):
        self.post()

class RemoveFavorite(webapp.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'

        userid = self.request.get('uid')
        showid = self.request.get('sid')

        if removeFavorite(userid, showid):
            self.response.out.write("Remove " + showid)
        else:
            self.response.out.write("Remove 0")

    # This function is invoked when a user sends a get request
    def get(self):
        self.post()

# This class handles the fetching of favorites
class GetFavorites(webapp.RequestHandler):
  
    # This function is invoked when a user sends a get request
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
            
        # get userid
        userid = self.request.get('uid')
        reqId = self.request.get('tqx')
    
        try :
            reqId = reqId[6:8]
            if reqId == None or reqId == '' :
                reqId = 0
        except :
            reqId = 0
        
        # if userid wasn't given, return error
        if not userid:
            print "ERROR: userid wasn't given"
            return
        
        query = User.all()
        query.filter("userid = ", userid)
        user = query.get()
        
        dicUserFavorites = []
        if user:
            # Running on the show elements in the XML  
            favoriteShows = [db.get(key) for key in user.favorite_shows]
            for favoriteShow in favoriteShows:    
                if favoriteShow.nextdate is not None :
                    dNextDateInDB = stringToDate(favoriteShow.nextdate)
                else :
                    dNextDateInDB = datetime.date(2500,1,1)

                # If the next air date has passed (episode broadcasted)
                foundNewDate = False
                if dNextDateInDB < datetime.date.today():
                    showEpisodes = build_table_for_search(str(favoriteShow.showid))
                    episodeNodes = []
                    if showEpisodes is not None:
                        for node in showEpisodes.getElementsByTagName('episode'):
                            episodeNodes.extend([node])
                    
                    dates = [getXMLField(n, 'airdate') for n in episodeNodes]
                   
                    for date in dates:
                        try:
                            d = datetime.date(int(date[0:4]),int(date[5:7]), int(date[8:10]))
                            if d > datetime.date.today():
                                favoriteShow.prevdate = favoriteShow.nextdate
                                favoriteShow.nextdate = date
                                foundNewDate = True
                                break
                        except:
                            d = '1900-01-01'
                    if foundNewDate:
                        favoriteShow.put()
                if favoriteShow.nextdate == '1900-01-01':
                    nextAirDateFixed = 'Show Ended'
                else:
                    nextAirDateFixed = favoriteShow.nextdate
                # Appending the showid as int and name as string
                dicUserFavorites.append({ 
                    'showid'         : favoriteShow.showid, 
                    'name'           : favoriteShow.name,
                    'started'        : favoriteShow.started_year,
                    'seasons'        : favoriteShow.seasons,
                    'country'        : favoriteShow.country,
                    'classification' : favoriteShow.classification,
                    'status'         : favoriteShow.status,
                    'link'           : favoriteShow.link,
                    'airtime'        : favoriteShow.airtime,
                    'airday'         : favoriteShow.airday,                   
                    'prevdate'       : favoriteShow.prevdate,
                    'nextdate'       : nextAirDateFixed})
            # End For
        # End If
                  
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
                       "prevdate"       : ("string", "Prev Date"),
                       "nextdate"       : ("string", "Next Date")}
        
        # Build the data table object with description and shows dictionary
        data_table = gviz_api.DataTable(description)
        data_table.LoadData(dicUserFavorites)
        
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
                                                                         "prevdate",
                                                                         "nextdate"),
                                                          order_by=("nextdate","asc"),
                                                          req_id=reqId))

# This function links a user and a show
# If the user / show doesn't exist, they are added to the datastore
def addFavorite(userid, showid): 
    # making sure data was received properly
    if not (userid == "" or showid == ""):

        # checking if the shows exists
        query = Show.all()
        query.filter("showid = ", int(showid))
        show = query.get()
        
        if not show:
            # if the show isn't in the DS,
            addShow(showid)
            
            # Make sure the show was actually added
            query = Show.all()
            query.filter("showid = ", int(showid))
            show = query.get()
            if show is None:
                return False
            
        # checking if the user exists
        query = User.all()
        query.filter("userid = ", userid)
        user = query.get()
        
        if not user:
            # adding the user to the DS
            newRecord = User(userid = userid,
                             friends_influence = 50)
            newRecord.put()
            user = newRecord
        
        if show.key() not in user.favorite_shows:
            # adding the show as a favorite for this user
            user.favorite_shows.append(show.key())
            show.inc()
            user.put()
            return True
    return False

# This function disconnected the link between a user and a show
def removeFavorite(userid, showid):
    # Remove from reference list
    # decrease counters
    query = User.all()
    query.filter("userid = ", userid)
    user = query.get()
    
    query2 = Show.all()
    query2.filter("showid = ", int(showid))
    show = query2.get()
    if user and show and show.key() in user.favorite_shows:
        user.favorite_shows.remove(show.key())
        show.dec()
        show.put()
        user.put()
        return True
    return False
