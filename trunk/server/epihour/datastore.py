from google.appengine.ext import db

class User(db.Model):
	userid = db.StringProperty(required=True)
	friends_influence = db.RatingProperty(required=True)
	main_stats_influence = db.RatingProperty(required=True)
	similar_profiles_influence = db.RatingProperty(required=True)
	
	# a list of the user's favorite and removed_from_favorite shows
	favorite_shows = db.ListProperty(db.Key)
	removed_from_favorites_shows = db.ListProperty(db.Key)
	
class Show(db.Model):
	showid = db.IntegerProperty(required=True)
	name = db.StringProperty(required=True)
	genres = db.ListProperty(db.Key)
	country = db.StringProperty()
	started_year = db.IntegerProperty()
	is_show_over = db.BooleanProperty()#required=True)

	@property
	def user_members(self):
		return User.gql("WHERE favorite_shows = :1", self.key())
	
class Genre(db.Model):
	name = db.StringProperty(required=True)
	
	@property
	def shows_members(self):
		return Show.gql("WHERE genres = :1", self.key())
	
	
class Suggestion(db.Model):
	user = db.ReferenceProperty(User)
	showid = db.ReferenceProperty(Show)
	suggestion_date = db.DateTimeProperty(auto_now_add=True)
	shown = db.BooleanProperty(required=True, default=True)
	
	
#	
#class UsersFavorites(db.Model):
#	user = db.StringProperty(required=True)
#	#user = db.ReferenceProperty(Users, collection_name="favorites_user_set")
#	#showid = db.ReferenceProperty(Shows, collection_name="shows_user_set")
#	showid = db.IntegerProperty(required=True)
#	favorite = db.BooleanProperty(default=True)
