from google.appengine.ext import webapp
from google.appengine.ext import db
from epihour import *

__author__ = "Nadav Shamgar"

class AddFavorite(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  def get(self):
    # The content returned is a text/plain
    self.response.headers['Content-Type'] = 'text/plain'
    
    # get userid & showid to add to the favorites table
    userid = self.request.get('uid')
    showid = self.request.get('sid')

    if not (userid == "" or showid == ""):

        query = Shows.gql("WHERE showid = :showid",
                          showid=int(showid))
        show = query.fetch(1)
        
        if not show:
            print "showid doesn't exist in the DS"
        else:       
            print "adding show %s as a favorite to user %s<br>" % (showid, userid)
            favoriteRecord = UsersFavorites(userid = int(userid),
                                            showid = show[0].key(),
                                            favorite = True)
            favoriteRecord.put()
    else:
        # No show name specified, return
        print "error in data"
