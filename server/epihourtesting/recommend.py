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
        
        userid = '13314698784882897227' #int(self.request.get('userid'))
        
        query = User.all()
        query.filter("userid = ", userid)
        user = query.get()
        
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
        for friend in friends:
            print friend.fields['id']
            print
        
#        friendsList = []
#        for friend in friends:
#            query.filter("userid = ", friend.fields['id'])
#            fuser = query.get()
#            friendsList.append(fuser)
#        
#        listOflists = []
#        for friend in friendsList:
#            favoriteShows = [db.get(key) for key in user.favorite_shows]
#            listOflists.append(favoriteShows)
        
        print 'FINISH go_to_ds'
        
class MainPage(webapp.RequestHandler):
    
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
             

        
# Define the webapp applications and map the classes to different paths
application = webapp.WSGIApplication([('/Recommend', MainPage)],
                                     debug=True)

# Main global function
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
