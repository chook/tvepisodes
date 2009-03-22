from google.appengine.ext import db

class User(db.Model):
	userid = db.StringProperty(required=True)
	friends_influence = db.RatingProperty(required=True)
#	main_stats_influence = db.RatingProperty(required=True)
#	similar_profiles_influence = db.RatingProperty(required=True)
	
	# a list of the user's favorite and removed_from_favorite shows
	favorite_shows = db.ListProperty(db.Key)
	removed_from_favorites_shows = db.ListProperty(db.Key)
	
class Show(db.Model):
	showid = db.IntegerProperty(required=True)
	name = db.StringProperty(required=True)
	link = db.StringProperty()
	seasons = db.IntegerProperty()
	started_year = db.IntegerProperty()
	started_date = db.StringProperty()
	ended_date   = db.StringProperty()
	country = db.StringProperty()
	status = db.StringProperty()
	classification = db.StringProperty()
	genres = db.StringListProperty()
	runtime = db.IntegerProperty()
	network = db.StringProperty()
	airtime = db.StringProperty()
	airday = db.StringProperty()
	timezone = db.StringProperty()
	is_show_over = db.BooleanProperty()#required=True)
	nextdate = db.StringProperty()
	prevdate = db.StringProperty()
	showcount = db.IntegerProperty(default=0)
	
	@property
	def user_members(self):
		return User.gql("WHERE favorite_shows = :1", self.key())
	
	def inc(self):
		self.showcount = self.showcount + 1
		[Genre.gql("WHERE name = :1", genre).get().inc() for genre in self.genres]
		self.put()
		
	def dec(self):
		self.showcount = self.showcount - 1
		if self.showcount < 0:
			self.showcount = 0
		[Genre.gql("WHERE name = :1", genre).get().dec() for genre in self.genres]
		self.put()
		
class Genre(db.Model):
	name = db.StringProperty(required=True)
	count = db.IntegerProperty(default=0)
	
	@property
	def shows_members(self):
		return Show.gql("WHERE genres = :1", self.key())
	
	def inc(self):
		self.count = self.count + 1
		self.put()
		
	def dec(self):
		self.count = self.count - 1
		self.put()	