from google.appengine.ext import db
from datastore import *

from shows import *
from favorites import *
from users import *
from recommend import *
from statistics import *
def clearAll():
    clearAllShows()
    clearAllUsers()
    clearAllGenres()
    
# Define the webapp applications and map the classes to different paths
application = webapp.WSGIApplication([('/', MainPage),
                                     ('/searchShow', SearchShow),
                                     ('/addFavorite', AddFavorite),
                                     ('/getFavorites', GetFavorites),
                                     ('/removeFavorite', RemoveFavorite),
                                     ('/users',AddUser),
                                     ('/clearAllShows',clearAllShows),
                                     ('/clearAllUsers',clearAllUsers),
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