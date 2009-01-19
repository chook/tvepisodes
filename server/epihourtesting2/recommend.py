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

def go_to_ds(self):
        try:
            userid = self.request.get('user') #int(self.request.get('userid'))
            useFriends = 'False'
            useFriends = self.request.get('usefriends')
        except:
            userid = '03067092798963641994'
            useFriends = 'False'
        
        reqId = self.request.get('tqx')
    
        try :
            reqId = reqId[6:8]
            if reqId == None or reqId == '' :
                reqId = 0
        except :
            reqId = 0
        
        # 1. Get user from DS
        query = User.all()
        query.filter("userid = ", userid)
        user = query.get()
        
        #2. Get user favorite shows from DS
        userFavShows = []
        userFavShows.extend([db.get(k) for k in user.favorite_shows])
        
        listFavGenres = []
        for temp in userFavShows:
            listFavGenres.extend([k for k in temp.genres])

        #3. Get top show that he is not watching
        #3.1 Get 20 shows
        globalTopShows = db.GqlQuery('SELECT * FROM Show ORDER BY showcount DESC LIMIT 20')
        
        #3.1.1
        if useFriends == 'True':
            try:
                config = ContainerConfig(oauth_consumer_key='orkut.com:623061448914',
                oauth_consumer_secret='uynAeXiWTisflWX99KU1D2q5',
                server_rest_base='http://sandbox.orkut.com/social/rest/',
                server_rpc_base='http://sandbox.orkut.com/social/rpc/')
                container = ContainerContext(config)
                
                batch = RequestBatch()
                batch.add_request('friends',
                                  request.FetchPeopleRequest(userid, '@friends'))
                batch.send(container)
                friends = batch.get('friends')
                friendsList = []
                for friend in friends:
                    query = User.all()
                    query.filter("userid = ", friend.fields['id'])
                    fuser = query.get()
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
            if not tempShow.showid in [show.showid for show in userFavShows]:
                possibleRecommendShows.append(tempShow)
                listOfGenres.extend([k for k in tempShow.genres])
                    #self.response.out.write(genrename)
        
        oldestGrade = -9999
        recommendedShow = possibleRecommendShows[0]
        listForVisualization = []
        for show in possibleRecommendShows:
            match = 0.0
            mismatch = 0.0
            genres = [k for k in show.genres] 
            for g in genres:
                if g in listFavGenres:
                    match += listFavGenres.count(g)
                else:
                    mismatch += 1
            genresGrade = ((3*match) - (mismatch*1.5)) * user.similar_profiles_influence / 100
            
            if useFriends == 'True':
                if show.showid in favShows:
                    genresGrade = max(1, (1.5 * favShows.count(show.showid) * user.friends_influence / 100)  + genresGrade)
            
            listForVisualization.extend([{'showid'   : show.showid,
                                          'name'     : show.name,
                                          'nextdate' : show.nextdate,
                                          'started'  : show.started_year,
                                          'seasons'  : show.seasons,
                                          'country'  : show.country,
                                          'link'     : show.link,
                                          'grade'    : genresGrade}])
        
        description = {"showid"  : ("number", "ID"),
                       "name"    : ("string", "Name"),
                       "nextdate": ("string", "Next Date"),
                       "started" : ("string", "Year Started"),
                       "seasons" : ("number", "Seasons Number"),
                       "country" : ("string", "Original Country"),
                       "link"    : ("string", "Link"),
                       "grade"  : ("number", "Grade")}
        
        # Build the data table object with description and shows dictionary
        data_table = gviz_api.DataTable(description)
        data_table.LoadData(listForVisualization)
        
        # Write the object as a JSon response back to the caller
        self.response.out.write(data_table.ToJSonResponse(columns_order=("showid", "name", "nextdate", "started", "seasons", "country", "link", "grade"),order_by=("grade","desc"),req_id=reqId))
                        
            #if genresGrade > oldestGrade:
            #    recommendedShow = show
            #    oldestGrade = genresGrade
##        dictGlobalGenresCount = {}
##        for s in listOfGenres:
##            if s not in dictGlobalGenresCount:
##                dictGlobalGenresCount[s] = listOfGenres.count(s)
##        self.response.out.write('This is the datastore distribution: %s<br />' % dictGlobalGenresCount)
        
        #4. Get the show that is most relevant to him 
        #4.1. Get the show that has the highest genres hit
        # Check the show in a loop, for the highest rank in genres
##        self.response.out.write('<ul>')

                
##            self.response.out.write('<li>')    
##            self.response.out.write('id: %d. Show name: %s, match:%f. mismatch:%f  <b>grade:%f</b><br />' % (show.showid, show.name,match, mismatch, genresGrade))
##            self.response.out.write('Show genres are: %s' % (genres))
##            self.response.out.write('</li>')
##        self.response.out.write('</ul>')

        #4.2. Send the recommendation to the user
##        self.response.out.write('<h1>Recommended show is: %d %s</h1>' % (recommendedShow.showid, recommendedShow.name))

class Recommend(webapp.RequestHandler):
    
    # This function is invoked when a user sends a get request
    def get(self):
        try:
            SHOWS_LOW = 0
            SHOWS_HIGH = int(self.request.get('sh'))
            USERS_LOW = 0
            USERS_HIGH = int(self.request.get('uh'))
        except:
            go_to_ds(self)
            return
        
        genres = ['action', 'horror', 'comedy', 'thriller', 'family','fantasy','Adventure','Sci-Fi']
        classifications = ['Documentary','Scripted','Reality','Animated']
        #shows = [Show(i,"show%d" % i, genres[random.randint(0,4)],'animation') for i in xrange(1,11)]
        #shows = [Show(i, "show%d" % i, ([random.choice(genres) for j in xrange(random.randint(1,10))]), random.choice(classifications)) for i in xrange(1000,1100)]
        
        # Populate a shows object
        shows = [LShow(i, "show%d" % i, random.sample(genres,random.randint(1,8)), random.choice(classifications)) for i in xrange(SHOWS_LOW,SHOWS_HIGH)]
       
        # This code looks at the user ids
        users = [LUser(i, "user%d" % i, [], random.sample([i for i in xrange(SHOWS_LOW,SHOWS_HIGH)], int(max(random.normalvariate(15,5),0)))) for i in xrange(USERS_LOW,USERS_HIGH)]
        [user.friends.extend(random.sample([user.userid for user in users], int(max(random.normalvariate(100,50),0)))) for user in users]
        
        # First try to calculate a show grade
        randomShow = shows[random.randint(SHOWS_LOW, SHOWS_HIGH)]
        randomUser = users[random.randint(USERS_LOW, USERS_HIGH)]
        self.response.out.write('Selected user %s' % randomUser + '<br />')
        self.response.out.write('Selected show %s' % randomShow + '<br />')
        
        # Now total viewers
        totalViewers = 0
        for user in users:
            for i in user.favorites:
                if i == randomShow.showid:
                    totalViewers = totalViewers + 1
        self.response.out.write('Total viewers of the show is %d' % totalViewers + '<br />')
        
        #Now for friends
        totalFriendsViewers = 0
        for user in randomUser.friends:
            for tempUser in users:
                if tempUser.userid == user:
                    for i in tempUser.favorites:
                        if i == randomShow.showid:
                            totalFriendsViewers = totalFriendsViewers + 1
        self.response.out.write('Total friends viewers of the show is %d' % totalFriendsViewers + '<br />')
        
        #for user in users:
        #    if 
        #self.response.out.write([3,5,7].find(3))
        
        
        #for user in users:
            #result = (i for i in user.favorites if i == randomShowid).next()
            #self.response.out.write(user.favorites)
        #    user.friends.extend(random.sample(users.)
        
        #self.response.out.write(genres)
        
        #genresList = [genres[random.randint(0,4)] for i in xrange(20)]
        
        #self.response.out.write(genresList)
        #for s in users:
        #     self.response.out.write(s)