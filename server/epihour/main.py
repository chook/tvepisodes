from google.appengine.ext import db
from epihour import *

from shows import *
from favorites import *


# Define the webapp applications and map the classes to different paths
application = webapp.WSGIApplication([('/', MainPage),
                                     ('/SearchShow', SearchShow),
                                     ('/SearchAndStoreShow', SearchAndStoreShow),
                                     ('/favorites', AddFavorite)],
                                     debug=True)

# Main global function
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()