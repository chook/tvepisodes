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

class LShow(object):
    def __init__(self, showid, sname, genre, classification):
        self.showid = showid
        self.sname = sname
        self.genre = genre
        self.classification = classification
    def __repr__(self):
        return 'id: %d. name: %s. genre: %s. type:%s.<br />' % (self.showid, 
                                                         self.sname,
                                                         self.genre, 
                                                         self.classification)

class LUser(object):
    def __init__(self, userid, uname, friends, favorites):
        self.userid = userid
        self.uname = uname
        self.friends = friends
        self.favorites = favorites
    def __repr__(self):
        return 'id: %d. name: %s. friends: %s. favorites: %s.<br />' % (self.userid, 
                                                         self.uname,
                                                         self.friends,
                                                         self.favorites) 

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
# TODO: DELETE ---def handleRecommendRequest(self):
class Recommend(webapp.RequestHandler):       
     def get(self): 
        # The following code handles the get request
        try:
            userid = self.request.get('user') #int(self.request.get('userid'))
            
            friendsString = self.request.get('friends')
            if friendsString == None or friendsString == '':
                useFriends = 'False'
            else:
                useFriends = 'True'
            showscount = self.request.get('showscount')
        except:
            userid = '03067092798963641994'
            useFriends = 'False'
            showscount = 20
        
    
        try :
            reqId = self.request.get('tqx')
            reqId = reqId[6:8]
            if reqId == None or reqId == '' :
                reqId = 0
        except :
            reqId = 0
        
        try :
            friendsinf = int(self.request.get('friendsinf'))
            genresinf = int(self.request.get('genresinf'))
        except : 
            friendsinf = 40
            genresinf = 50
        
        # 1. Get user from DataStore
        query = User.all()
        query.filter("userid = ", userid)
        user = query.get()
        changedInf = False
        if not user.similar_profiles_influence == genresinf :
            user.similar_profiles_influence = genresinf
            changedInf = True
        if not user.friends_influence == friendsinf :
            user.friends_influence = friendsinf
            changedInf = True
        
        logging.debug('Recommend to user ' + userid)
        
        #2. Get user favorite shows and favorite genres from DS
        userFavShows = []
        userFavShows.extend([db.get(k) for k in user.favorite_shows])
        logging.debug('His shows are ' + str([t.showid for t in userFavShows]))
        listFavGenres = []
        for temp in userFavShows:
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
                    #query.filter("userid = ", friend.fields['id'])
                    query.filter("userid = ", friend)
                    fuser = query.get()
                    friendsList.append(fuser)
        
                favShows = []
                for f in friendsList:
                    if f != None:
                        favShows.extend([db.get(k).showid for k in f.favorite_shows])
                logging.debug('Friends like ' + str(favShows))
            except:
                useFriends = 'False';
             
        # 3.2 Cross reference with his favorite shows and select those that don't match
        possibleRecommendShows = []
        listOfGenres = []
        for tempShow in globalTopShows:
            if not tempShow.showid in [show.showid for show in userFavShows]:
                possibleRecommendShows.append(tempShow)
                listOfGenres.extend([k for k in tempShow.genres])
                    #self.response.out.write(genrename)
        logging.debug('Possible recommendations are ' + str([x.showid for x in possibleRecommendShows]))
        
        # 4. Start processing the possibly recommended shows for grading
        oldestGrade = -9999
        listForVisualization = []
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
                genresGrade = ((3*match) - (mismatch*2)) * user.similar_profiles_influence / 100
                logging.debug('Genres grade before friends: ' + str(genresGrade))
                
                if useFriends == 'True':
                    if show.showid in favShows:
                        genresGrade = max(1, (1.5 * favShows.count(show.showid) * user.friends_influence / 100)  + genresGrade)
                        sentence += ' ' + str(favShows.count(show.showid)) + ' of your friends are watching it'
                        if bestGenreCounter > 0:
                            sentence += ' and because you like ' + bestGenreName + ' shows so much. (We know. don''t deny it)'
                        logging.debug('Genres grade after friends: ' + str(genresGrade))
                    else:
                        genresGrade -= (user.friends_influence * 2.5 / 10)
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
                       "sentence"       : ("string", "Sentence"),
                       "grade"          : ("number", "Grade")}
        
        # 5. Build the data table object with description and shows dictionary
        data_table = gviz_api.DataTable(description)
        
#        TODO: Remove this
#        if len(listForVisualization) > 3:
#            listForVisualization = listForVisualization[0:3]
#        
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
        
        if changedInf:
            user.put() 
# This handler is called from main.py
#class Recommend(webapp.RequestHandler):
#    
#    # This function is invoked when a user sends a get request
#    def get(self):
#        try:
#            SHOWS_LOW = 0
#            SHOWS_HIGH = int(self.request.get('sh'))
#            USERS_LOW = 0
#            USERS_HIGH = int(self.request.get('uh'))
#        except:
#            
#            # This function is the one that actually process and returns the recommended shows visualization
#            handleRecommendRequest(self)
#        return
##        
##        genres = ['action', 'horror', 'comedy', 'thriller', 'family','fantasy','Adventure','Sci-Fi']
##        classifications = ['Documentary','Scripted','Reality','Animated']
##        #shows = [Show(i,"show%d" % i, genres[random.randint(0,4)],'animation') for i in xrange(1,11)]
##        #shows = [Show(i, "show%d" % i, ([random.choice(genres) for j in xrange(random.randint(1,10))]), random.choice(classifications)) for i in xrange(1000,1100)]
##        
##        # Populate a shows object
##        shows = [LShow(i, "show%d" % i, random.sample(genres,random.randint(1,8)), random.choice(classifications)) for i in xrange(SHOWS_LOW,SHOWS_HIGH)]
##       
##        # This code looks at the user ids
##        users = [LUser(i, "user%d" % i, [], random.sample([i for i in xrange(SHOWS_LOW,SHOWS_HIGH)], int(max(random.normalvariate(15,5),0)))) for i in xrange(USERS_LOW,USERS_HIGH)]
##        [user.friends.extend(random.sample([user.userid for user in users], int(max(random.normalvariate(100,50),0)))) for user in users]
##        
##        # First try to calculate a show grade
##        randomShow = shows[random.randint(SHOWS_LOW, SHOWS_HIGH)]
##        randomUser = users[random.randint(USERS_LOW, USERS_HIGH)]
##        self.response.out.write('Selected user %s' % randomUser + '<br />')
##        self.response.out.write('Selected show %s' % randomShow + '<br />')
##        
##        # Now total viewers
##        totalViewers = 0
##        for user in users:
##            for i in user.favorites:
##                if i == randomShow.showid:
##                    totalViewers = totalViewers + 1
##        self.response.out.write('Total viewers of the show is %d' % totalViewers + '<br />')
##        
##        #Now for friends
##        totalFriendsViewers = 0
##        for user in randomUser.friends:
##            for tempUser in users:
##                if tempUser.userid == user:
##                    for i in tempUser.favorites:
##                        if i == randomShow.showid:
##                            totalFriendsViewers = totalFriendsViewers + 1
##        self.response.out.write('Total friends viewers of the show is %d' % totalFriendsViewers + '<br />')
#        