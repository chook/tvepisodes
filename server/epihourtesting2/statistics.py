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

class Statistics(webapp.RequestHandler):
    def get(self):
        try:
            type = self.request.get('type')
            limit = self.request.get('limit')
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
        if type == 'genres':
            genres = db.GqlQuery('SELECT * FROM Genre ORDER BY count DESC LIMIT %s' % limit)   
            dicVisu = [{'name' : g.name , 'count': g.count} for g in genres]
            genres = db.GqlQuery('SELECT * FROM Genre ORDER BY count DESC OFFSET %s' % limit)
            x=0
            y = [g.count for g in genres]
            for n in y:
                x += n
            if x > 0:
                dicVisu.append({'name' : 'Other', 'count' : x})
        elif type == 'shows':
            shows = db.GqlQuery('SELECT * FROM Show ORDER BY showcount DESC LIMIT %s' % limit)
            dicVisu = [{'name' : g.name , 'count': g.showcount} for g in shows]
            
        # Build the data table object with description and shows dictionary
        data_table = gviz_api.DataTable(description)
        data_table.LoadData(dicVisu)
        
        # Write the object as a JSon response back to the caller
        self.response.out.write(data_table.ToJSonResponse(columns_order=("name",
                                                                         "count"),
                                                          order_by=('count','DESC'),
                                                          req_id=reqId))
