from flask import Flask
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

migrate= Migrate(app,db)


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(1500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(800))
    seeking_talent =db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))

    shows= db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<{self.id} {self.name} {self.city}  {self.state}>'

db.create_all()

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(800))
    seeking_venue =db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))


    shows= db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<{self.id} {self.name} {self.city}  {self.state}>'


db.create_all()

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String(), nullable=False)    
    start_time_ = db.Column(db.DateTime, nullable=False)    

    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False) 
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

    def __repr__(self):
        return f'<{self.id} {self.start_time} artist_id={self.artist_id} venue_id={self.venue_id}>'

db.create_all()

# The Genres object pattern is a variant on many-to-many

# class Genres(db.Model):
#     __tablename__= 'genres'

#     id = db.Column(db.Integer, primary_key=True)
#     name= db.Column(db.String(), nullable=False)
#     artist_id =db.Column(db.String(), db.ForeignKey("artist.id"))
#     venue_id=db.Column(db.Integer, db.ForeignKey("venue.id"))

#     artist= db.relationship('Artist', backref='genres', lazy=True)
#     venue= db.relationship('Venue', backref='genres', lazy=True)



#     def __repr__(self):
#         return f'<{self.id} {self.name}>'

# db.create_all()



# Many To Many relationship pattern
# venue_genres = db.Table(
#     "venue_genres",
#     genre =db.Column(db.String(), db.ForeignKey("genre.name")),
#     venue_id=db.Column(db.Integer, db.ForeignKey("venue.id")),
# )
