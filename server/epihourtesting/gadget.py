import cgi
import gviz_api
import logging
from google.appengine.api import urlfetch 
from xml.dom import minidom 
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache

class Gadget(webapp.RequestHandler):
  # This function is invoked when a user sends a get request
  def get(self):
	self.response.out.write("<html><body>hi</body></html>")


# Define the webapp applications and map the classes to different paths
application = webapp.WSGIApplication([('/', Gadget)],
                                     debug=True)

# Main global function
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
