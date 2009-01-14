from google.appengine.ext import webapp
from google.appengine.ext import db

from django.utils import simplejson as json
from datastore import *
from shows import *

__author__ = "Nadav Shamgar"

class AddFavorite(webapp.RequestHandler):
  
# this function is invoked when a user sends a POST request
    def post(self):
        
        self.response.headers['Content-Type'] = 'text/plain'
        
#        args = json.loads(self.request.body)
#        
#        # get userid & showid to add to the favorites table
#        userid = args['uid']
#        showid = args['sid']
#        searchString = args['search']   # the search string for adding shows to the DS
        
        userid = self.request.get('uid')
        showid = self.request.get('sid')
        searchString = self.request.get('search')
        
        addFavorite(userid, showid, searchString)
    

      
# This function is invoked when a user sends a get request
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
            
        # get userid & showid to add to the favorites table
        userid = self.request.get('uid')
        showid = self.request.get('sid')
        searchString = self.request.get('search')
    
        addFavorite(userid, showid, searchString)

class GetFavorites(webapp.RequestHandler):
  
# This function is invoked when a user sends a get request
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
            
        # get userid
        userid = self.request.get('uid')
        
        # if userid wasn't given, return error
        if not userid:
            print "ERROR: userid wasn't given"
            return
        
        query = User.all()
        query.filter("userid = ", userid)
        user = query.get()
        
        if not user:
            print "ERROR: User doesn't exist"
            return
        
        dicUserFavorites = []
        
        # Running on the show elements in the XML  
        favoriteShows = [db.get(key) for key in user.favorite_shows]
        for favoriteShow in favoriteShows:
            # Appending the showid as int and name as string
            dicUserFavorites.append({ 
                'showid': favoriteShow.showid, 
                'name'  : favoriteShow.name
            })        
        # Decide on the data table description
        description = {"showid": ("number", "ID"),
                       "name":   ("string", "Name")}
        
        # Build the data table object with description and shows dictionary
        data_table = gviz_api.DataTable(description)
        data_table.LoadData(dicUserFavorites)
        
        # Write the object as a JSon response back to the caller
        self.response.out.write(data_table.ToJSonResponse(columns_order=("showid", "name")))
        
    

def addFavorite(userid, showid, searchString):
    
        # making sure data was received properly
        if not (userid == "" or showid == "" or searchString == ""):
    
            # checking if the shows exists
            query = Show.all()
            query.filter("showid = ", int(showid))
            show = query.get()
            
            if not show:
                print "show doesn't exist on DS, adding all the shows from the search string<br>"
                # if the show isn't in the DS,
                # run over the search string, and add all the missing shows from it
                # do this only once, and only if one of the shows that were marked as favorite
                # wasn't in the DS
                addShow(showid)
                
                return
                # running the query again to get the new show that was added
                query = Show.all()
                query.filter("showid = ", int(showid))
                show = query.get()
                
                # if this still didn't work
                if not show:
                    print "something not working with addShowToDS<br>"
                    return
            else:
                print "show exists<br>"
                
            # checking if the user exists
            query = User.all()
            query.filter("userid = ", userid)
            user = query.get()
            
            if not user:
                print "user doesn't exist, creating it<br>"
                # adding the user to the DS
                newRecord = User(userid = userid,
                                  friends_influence = 40,
                                  main_stats_influence = 10,
                                  similar_profiles_influence = 50)
                newRecord.put()
                user = newRecord
            else:
                print "user exists<br>"
            
            
            if show.key() not in user.favorite_shows:
                print "show isn't in user's favorites list, adding it"
                # adding the show as a favorite for this user
                user.favorite_shows.append(show.key())
                user.put()
            else:
                print "show is already in user's favorites list"
                
            print "user's favorites list:"
            favoriteShows = [db.get(key) for key in user.favorite_shows] 
            for show in favoriteShows:
                print show.name
    
            print "OK"
    
    #        query.filter("user = ", userid)
    #        userFavorites = query.fetch(1000)
    #        print "user %s has these shows as favorites:<br>" % userid
    #        print "favorites count = %d" % userFavorites.count(1000)
    #        for favoriteShow in userFavorites:
    #            print "show: %d" % favoriteShow.showid
            
        else:
            # No show name specified, return
            print "get information missing (needs uid, sid & searchString)<br>"