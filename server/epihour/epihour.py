from google.appengine.ext import db

class Users(db.Model):
	user = db.UserProperty(required=True)
	friends_influence = db.RatingProperty(required=True)
	main_stats_influence = db.RatingProperty(required=True)
	similar_profiles_influence = db.RatingProperty(required=True)
	
class Shows(db.Model):
	showid = db.IntegerProperty(required=True)
	name = db.StringProperty(required=True)
	genres = db.StringListProperty()
	country = db.StringProperty()
	started_year = db.DateTimeProperty()
	is_show_over = db.BooleanProperty()#required=True)
	
class UsersFavorites(db.Model):
	user = db.ReferenceProperty(Users, collection_name="favorites_user_set")
	showid = db.ReferenceProperty(Shows, collection_name="shows_user_set")
	favorite = db.BooleanProperty(required=True, default=True)
	
class Suggestions(db.Model):
	user = db.ReferenceProperty(Users)
	showid = db.ReferenceProperty(Shows)
	suggestion_date = db.DateTimeProperty(auto_now_add=True)
	shown = db.BooleanProperty(required=True, default=True)
	
class Suggestionss(db.Model):
	user = db.ReferenceProperty(Users)
	showid = db.ReferenceProperty(Shows)
	suggestion_date = db.DateTimeProperty(auto_now_add=True)
	shown = db.BooleanProperty(required=True, default=True)