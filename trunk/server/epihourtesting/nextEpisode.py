#!/usr/bin/python

from google.appengine.api import urlfetch 
from xml.dom import minidom 
import time
import cgi
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import gviz_api

description = {"name": ("string", "Name"),
               "salary": ("number", "Salary"),
               "full_time": ("boolean", "Full Time Employee")}
data = [{"name": "Mike", "salary": (10000, "$10,000"), "full_time": True},
        {"name": "Jim", "salary": (800, "$800"), "full_time": False},
        {"name": "Alice", "salary": (12500, "$12,500"), "full_time": True},
        {"name": "Bob", "salary": (7000, "$7,000"), "full_time": True}]

data_table = gviz_api.DataTable(description)
data_table.LoadData(data)
print "Content-type: text/plain"
print
print data_table.ToJSonResponse(columns_order=("name", "salary", "full_time"),
                                order_by="salary")

# Put the url (http://google-visualization.appspot.com/python/dynamic_example) as your
# Google Visualization data source.

class MainPage(webapp.RequestHandler):
  def get(self):
    print self.request.get("ShowName")
    print "AHHHHHHH"

application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()


WEATHER_URL = 'http://www.tvrage.com/feeds/episode_list.php?sid=%s'
WEATHER_NS = '' 

def parse( url ) : 
   result = urlfetch.fetch(url)
   #print result.content
   if result.status_code == 200: 
           return minidom.parseString(result.content) 

def weather_for_zip(zip_code): 
    url = WEATHER_URL % zip_code 
    dom = parse(url) 
    forecasts = []
    #print dom
    print dom.getElementsByTagName('episode')[0].childNodes.length
    for node in dom.getElementsByTagName('episode'):
        #print node.childNodes[0].firstChild.data
        forecasts.append({ 
            'epnum': node.childNodes[0].firstChild.data, 
            'seasonnum': node.childNodes[1].firstChild.data,
            'prodnum': node.childNodes[2].firstChild.data,
            'airdate': node.childNodes[3].firstChild.data
        })
    return forecasts 
        
print 'Content-Type: text/plain' 
print '' 
#print weather_for_zip('8172') 
shows = weather_for_zip('8172')
now = time.gmtime()
print now
for node in shows:
    #print node['airdate']
    #print type(node.airdate)
    #print node['airdate'][0:4]
    try:
        if(int(node['airdate'][0:4]) < int(now[0])):
            print node['epnum'] + ' was already shown last year'
    except:
        print 'Error'
