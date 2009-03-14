#!/usr/bin/python
## This script is used to generate statistics visualizations
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

# This class handles the statistics generation
class Statistics(webapp.RequestHandler):
    def get(self):
        try:
            type = self.request.get('type')
            limit = self.request.get('limit')
            friends = self.request.get('friends')
        except:
            type = 'genres'
            limit = '10'
            
        if type == '' or type is None:
            type = 'genres'
        if limit == '' or limit is None:
            limit = '10'
        
        # The content returned is a text/plain
        self.response.headers['Content-Type'] = 'text/plain'
        
        reqId = self.request.get('tqx')
        
        try :
            reqId = reqId[6:8]
            if reqId == None or reqId == '' :
                reqId = 0
        except :
            reqId = 0
            
        # Decide on the data table description
        description = {"name" : ("string", "Name"),
                       "count": ("number", "Appearances")}
        dicVisu = []
        if type == 'genres':
            genres = db.GqlQuery('SELECT * FROM Genre ORDER BY count DESC LIMIT %s' % limit)   
            dicVisu = [{'name' : g.name , 'count': g.count} for g in genres]
            
            genresOther = db.GqlQuery('SELECT * FROM Genre ORDER BY count DESC OFFSET %s' % limit)
            otherCounter =0
            otherCountersList = [g.count for g in genresOther]
            for counter in otherCountersList:
                otherCounter += counter
            if otherCounter > 0:
                dicVisu.append({'name' : 'Other', 'count' : otherCounter})
        elif type == 'shows':
            dic = {}
            shows = db.GqlQuery('SELECT * FROM Show ORDER BY showcount DESC LIMIT %s' % limit)
            if friends == '' or friends == None:
                dicVisu = [{'name' : g.name , 'count': g.showcount} for g in shows]
            # Using friends
            else :
                for show in shows:
                    dic[show.name] = 0
                    
                friendsIDs = friends.split(',')
                friendsList = []
                for friend in friendsIDs:
                    query = User.all()
                   
                    query.filter("userid = ", friend)
                    fuser = query.get()
                    friendsList.append(fuser)
        
                favShows = []
                for friend in friendsList:
                    if friend != None:
                        favShows.extend([db.get(k).name for k in friend.favorite_shows])
            
                for fShow in favShows:
                    if fShow in dic:
                        dic[fShow] += 1
                    else:
                        dic[fShow] = 1
                
                dicVisu = [{'name' : show.name , 'count': show.showcount, 'countfriends': dic[show.name]} for show in shows]
                description = {"name" : ("string", "Name"),
                               "count": ("number", "Appearances")}
                
                description["countfriends"] = ("number", "Friends Count")
                data_table = gviz_api.DataTable(description)
                data_table.LoadData(dicVisu)
                
                # Write the object as a JSon response back to the caller
                self.response.out.write(data_table.ToJSonResponse(columns_order=("name",
                                                                                 "count",
                                                                                 "countfriends"),
                                                                  order_by=('count','DESC'),
                                                                  req_id=reqId))
                return 
        
        # Build the data table object with description and shows dictionary
        # Only if no friends were available
        data_table = gviz_api.DataTable(description)
        data_table.LoadData(dicVisu)
        
        # Write the object as a JSon response back to the caller
        self.response.out.write(data_table.ToJSonResponse(columns_order=("name",
                                                                         "count"),
                                                          order_by=('count','DESC'),
                                                          req_id=reqId))
        return
