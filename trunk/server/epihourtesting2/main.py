from google.appengine.ext import db
from datastore import *

from shows import *
from favorites import *
from recommend import *
from statistics import *
def clearAll():
    clearAllShows()
    clearAllGenres()
 
class MainPage(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  def get(self):
    self.response.out.write("Invalid usage")

# Define the webapp applications and map the classes to different paths
application = webapp.WSGIApplication([('/', MainPage),
                                     ('/searchShow', SearchShow),
                                     ('/addFavorite', AddFavorite),
                                     ('/getFavorites', GetFavorites),
                                     ('/removeFavorite', RemoveFavorite),
                                     ('/clearAllShows',clearAllShows),
                                     ('/clearAllGenres',clearAllGenres),
                                     ('/clearAll',clearAll),
                                     ('/recommend',Recommend),
                                     ('/statistics',Statistics),
                                     ('/topShows',TopShows)],
                                     debug=True)

# Main global function
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()