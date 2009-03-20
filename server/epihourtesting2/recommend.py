#!/usr/bin/python
## This script is used to recommend a show
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
from datastore import *

__author__ = "Chen Harel"

# This function is the main process for getting the recommendation
# The algorithm in a nut shell is getting the shows, based on popularity,
# Clear the shows that the user already favors.
# Count for each show, the number of hits from his friend's favorites.
# Make a cross between the genres he likes the most, and the "wanna-be recommended" shows
# Calculate a 'grade' for each show, based on all the above, and the user personal properties
# Output the shows as a visualization
# 
# Note: This request is a get request that needs the strings: user, friends and tqx, and the number showscount.
# Chen Harel - 05-03-09
class Recommend(webapp.RequestHandler):       
     def get(self): 
        # The following code handles the get request
        try:
            userid = self.request.get('uid') #int(self.request.get('userid'))
            
            friendsString = self.request.get('friends')
            if friendsString == None or friendsString == '':
                useFriends = 'False'
            else:
                useFriends = 'True'
            showscount = self.request.get('showscount')
        except:
            userid = 'ndef'
            useFriends = 'False'
            showscount = 21
    
        try :
            reqId = self.request.get('tqx')
            reqId = reqId[6:8]
            if reqId == None or reqId == '' :
                reqId = 0
        except :
            reqId = 0
        
        listForVisualization = []

        # 1. Get user from DataStore
        query = User.all()
        query.filter("userid = ", userid)
        user = query.get()
        
        friendsinf = user.friends_influence
        genresinf = 100 - friendsinf
        
        if user is not None:            
            #2. Get user favorite shows and favorite genres from DS
            userFavShows = []
            userFavShows.extend([db.get(k) for k in user.favorite_shows])
            
            listFavGenres = []
            for temp in userFavShows:
                if temp is not None:
                    listFavGenres.extend([k for k in temp.genres])
    
            #3. Get top show that he is not watching
            #3.1 Get shows from DS
            globalTopShows = db.GqlQuery('SELECT * FROM Show ORDER BY showcount DESC LIMIT %s' % showscount)
            
            #3.1.1 - Start going over the friends list and retrieve friend's favorite shows
            if useFriends == 'True':
                try:
                    friends = friendsString.split(',')
                    friendsList = []
                    for friend in friends:
                        query = User.all()
                        
                        query.filter("userid = ", friend)
                        fuser = query.get()
                        if fuser:
                            friendsList.append(fuser)
            
                    favShows = []
                    for f in friendsList:
                        if f != None:
                            favShows.extend([db.get(k).showid for k in f.favorite_shows])
                except:
                    useFriends = 'False';
                 
            # 3.2 Cross reference with his favorite shows and select those that don't match
            possibleRecommendShows = []
            listOfGenres = []
            for tempShow in globalTopShows:
                if not tempShow.showid in [show.showid for show in userFavShows if show is not None]:
                    possibleRecommendShows.append(tempShow)
                    listOfGenres.extend([k for k in tempShow.genres])
                    
            # 4. Start processing the possibly recommended shows for grading
            oldestGrade = -9999
            
            if len(possibleRecommendShows) > 0:
                recommendedShow = possibleRecommendShows[0]
                for show in possibleRecommendShows:
                    sentence = 'This show was recommended to you because'
                    match = 0.0
                    mismatch = 0.0
                    genres = [k for k in show.genres] 
                    bestGenreCounter = 0
                    bestGenreName = ''
                    for g in genres:
                        if g in listFavGenres:
                            match += listFavGenres.count(g)
                            if listFavGenres.count(g) >  bestGenreCounter:
                                bestGenreCounter = listFavGenres.count(g)
                                bestGenreName = g
                        else:
                            mismatch += 1
                    genresGrade = ((2*match) - (7*mismatch)) * user.similar_profiles_influence / 100
                    
                    if useFriends == 'True':
                        if show.showid in favShows:
                            genresGrade += (favShows.count(show.showid) * min(len(friendsList),8) * user.friends_influence / 100)
                            sentence += ' ' + str(favShows.count(show.showid)) + ' of your friends are watching it'
                            if bestGenreCounter > 0:
                                sentence += ' and because you like ' + bestGenreName + ' shows so much. (We know. don''t deny it)'
                        else:
                            genresGrade -= (max(len(friendsList),8) * user.friends_influence / 100)
                            if bestGenreCounter > 0:
                                sentence += ' you like ' + bestGenreName + ' shows so much. (We know. don''t deny it)'
                            else:
                                sentence = 'Count on us, this show is right for you.'
                    else:
                        if bestGenreCounter > 0:
                            sentence += ' you like ' + bestGenreName + ' shows so much. (We know. don''t deny it)'
                        else:
                            sentence = 'Count on us, this show is right for you.'

                    listForVisualization.extend([{
                                'showid'         : show.showid, 
                                'name'           : show.name,
                                'started'        : show.started_year,
                                'seasons'        : show.seasons,
                                'country'        : show.country,
                                'classification' : show.classification,
                                'status'         : show.status,
                                'link'           : show.link,
                                'airtime'        : show.airtime,
                                'airday'         : show.airday,
                                'sentence'       : sentence, 
                                'grade'          : genresGrade}])
                
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
                       "sentence"       : ("string", "Recommendation Sentence"),
                       "grade"          : ("number", "Grade")}
        
        # 5. Build the data table object with description and shows dictionary
        data_table = gviz_api.DataTable(description)
        data_table.LoadData(listForVisualization)
        
        # 6. Write the object as a JSon response back to the caller
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
                                                                         "sentence",
                                                                         "grade"),
                                                        order_by=("grade","desc"),
                                                        req_id=reqId))
        return