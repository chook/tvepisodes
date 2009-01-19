from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users

from datastore import *

__author__ = "Nadav Shamgar"

class AddUser(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  def get(self):
    # The content returned is a text/plain
    
    # get userid & showid to add to the favorites table
    userid = self.request.get('uid')
    friends_influence = 40
    main_stats_influence = 10
    similar_profiles_influence = 50

    userRecord = User(userid = userid,
                       friends_influence = friends_influence,
                       main_stats_influence = main_stats_influence,
                       similar_profiles_influence = similar_profiles_influence)
    userRecord.put()
    
    print "entered the following values to the DS:"
    print "%s / %d / %d / %d" % (userid, friends_influence, main_stats_influence, similar_profiles_influence)

    query = User.all()
    query.filter("userid = ", userid)
    
    result = query.get()
    
    if result:
        print "the user already exists in the DS:"
        print "%s / %d / %d / %d" % (result.userid, result.friends_influence, result.main_stats_influence, result.similar_profiles_influence)


    results = query.fetch(1000)
    
    for result in results:
         print "users in the DS:"
         print "%s / %d / %d / %d" % (result.userid, result.friends_influence, result.main_stats_influence, result.similar_profiles_influence)
#    usersList = query.fetch
   
#    usersList = Users.all()
    
#    if usersList:
#        print "users table is not empty"
 #       print "users count = %d" % usersList.count
 #       print "%d" % usersList[0].user
    
#    print "showing all the users in the DS:<br>"
#    for userRecordList in usersList:
#        print "%s, %d, %d, %d" % (userid, friends_influence, main_stats_influence, similar_profiles_influence)

def clearAllUsers():
    
    query = db.GqlQuery("SELECT * FROM User")
    results = query.fetch(1000)
    db.delete(results)
