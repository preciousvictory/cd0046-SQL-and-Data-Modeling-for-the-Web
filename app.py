#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from tabnanny import check
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
# from models import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
db.init_app(app)


migrate= Migrate(app,db)

# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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

    genres= db.relationship('Genres', backref='artist', lazy=True)


    def __repr__(self):
      return f'<{self.id} {self.name} {self.city}  {self.state}>'


db.create_all()

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    # start_time = db.Column(db.String(), nullable=False)    
    start_time_ = db.Column(db.DateTime, nullable=False)    

    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False) 
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

    def __repr__(self):
        return f'<{self.id} {self.start_time_} artist_id={self.artist_id} venue_id={self.venue_id}>'

db.create_all()


class Genres(db.Model):
    __tablename__= 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(), nullable=False)
    artist_id =db.Column(db.Integer, db.ForeignKey("artist.id"))
    venue_id= db.Column(db.Integer, db.ForeignKey("venue.id"))

    def __repr__(self):
        return f'<{self.id} {self.name}>'

db.create_all()

  

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.order_by(Venue.id).all()
  data=[]

  city_state={}
  for venue in venues:
    _id=venue.id  
    city=venue.city
    state=venue.state
    city_state[_id]=[city, state]

    
  for key,value in city_state.items():
    venue_list=[]  
    upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==Venue.id).filter(Show.start_time_>datetime.now()).all()   

    for venue in venues:
      if (venue.city == value[0]) and (venue.state == value[1]):
        info={
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(upcoming_shows_query),
        }
        venue_list.append(info)

    data.append({
      "city": value[0],
      "state": value[1],
      "venues": venue_list
    })


  return render_template('pages/venues.html', areas=data)

  '''[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]'''

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '').strip()
  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  searchlist=[]
  
  for venue in venues:
      
    searchlist.append({
      "id": venue.id,
      "name": venue.name,
    })

  response={
    "count": len(searchlist),
    "data": searchlist
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  venue=Venue.query.get(venue_id)

  past_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time_<datetime.now()).all()   

  past_shows = []
  for show in past_shows_query:
    artists= Artist.query.filter(Artist.id==show.artist_id).all()
    for artist in artists:
      info={
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time_)
          }
      past_shows.append(info)

  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time_>datetime.now()).all()   

  print(upcoming_shows_query)
  upcoming_shows = []
  for shows in upcoming_shows_query:
    artists= Artist.query.filter(Artist.id==shows.artist_id).all()
    for artist in artists:
      info={
            "artist_id": shows.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(shows.start_time_)
          }
      upcoming_shows.append(info)
  print(upcoming_shows)

  genres= Genres.query.filter(Genres.venue_id==venue_id).all()
  print(genres)

  gen=[]
  for genre in genres:
    gen.append(genre.name)
    
  data={
    "id": venue_id,
    "name": venue.name,
    "genres": gen,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "image_link": venue.image_link,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  print(data)

  return render_template('pages/show_venue.html', venue=data)

  '''data1={
      "id": 1,
      "name": "The Musical Hop",
      "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
      "address": "1015 Folsom Street",
      "city": "San Francisco",
      "state": "CA",
      "phone": "123-123-1234",
      "website": "https://www.themusicalhop.com",
      "facebook_link": "https://www.facebook.com/TheMusicalHop",
      "seeking_talent": True,
      "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
      "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "past_shows": [{
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
      }],
      "upcoming_shows": [],
      "past_shows_count": 1,
      "upcoming_shows_count": 0,
    }
    data2={
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "genres": ["Classical", "R&B", "Hip-Hop"],
      "address": "335 Delancey Street",
      "city": "New York",
      "state": "NY",
      "phone": "914-003-1132",
      "website": "https://www.theduelingpianos.com",
      "facebook_link": "https://www.facebook.com/theduelingpianos",
      "seeking_talent": False,
      "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
      "past_shows": [],
      "upcoming_shows": [],
      "past_shows_count": 0,
      "upcoming_shows_count": 0,
    }
    data3={
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
      "address": "34 Whiskey Moore Ave",
      "city": "San Francisco",
      "state": "CA",
      "phone": "415-000-1234",
      "website": "https://www.parksquarelivemusicandcoffee.com",
      "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
      "seeking_talent": False,
      "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "past_shows": [{
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
      }],
      "upcoming_shows": [{
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
      }, {
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
      }, {
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
      }],
      "past_shows_count": 1,
      "upcoming_shows_count": 1,
    }'''

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']

  website = request.form['website_link']
  if request.form['seeking_talent'] =='y':
    seeking_talent = True
  else:
    seeking_talent = False
  seeking_description = request.form['seeking_description']

  print(name, city, state)

  error=False
  try:
      new_venue= Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
    
      db.session.add(new_venue)            
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  except:
      error=True
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      return render_template('pages/home.html')
  finally:
      db.session.close()
  if not error:
        return render_template('pages/home.html')

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error=False
  try:
      del_=Venue.query.get(venue_id)
      
      db.session.delete(del_)
      db.session.commit()
      flash('Venue ' + del_.name + ' was successfully deleted!')
      return render_template('pages/home.html')
  except:
      error=True
      db.session.rollback()
      flash('An error occurred. Venue ' + del_.name + ' could not be deleted.')
      return render_template('pages/home.html')
  finally:
      db.session.close()
  if not error:
        return render_template('pages/home.html')


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data=[]
 
  for artist in artists:
      data.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=data)
  ''' data=[{
    "id": 4,
    "name": "Guns N Petals"
    ,
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]'''

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '').strip()
  artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  searchlist=[]
  
  for artist in artists:
      
    searchlist.append({
      "id": artist.id,
      "name": artist.name,
    })

  response={
    "count": len(searchlist),
    "data": searchlist
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist=Artist.query.get(artist_id)

  past_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time_<datetime.now()).all()   

  past_shows = []
  for show in past_shows_query:
    venues= Venue.query.filter(Venue.id==show.artist_id).all()
    for venue in venues:
      past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.start_time_)
          })

  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time_>datetime.now()).all()   

  upcoming_shows = []
  for shows in upcoming_shows_query:
    venues= Venue.query.filter(Venue.id==shows.artist_id).all()
    for venue in venues:
      upcoming_shows.append({
        "venue_id": shows.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(shows.start_time_)
          })

  genres= Genres.query.filter(Genres.artist_id==artist_id).all()
  print(genres)

  gen=[]
  for genre in genres:
    gen.append(genre.name)

  data={
    "id": artist_id,
    "name": artist.name,
    "genres": gen,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "image_link": artist.image_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

  '''data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }'''

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)

  artist_s={
    "id": artist_id,
    "name": artist.name,
    # "genres": ["Rock n Roll"],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_s)
'''artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
     }'''

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']

  website = request.form['website_link']

  if request.form.get('seeking_venue') == 'Yes':
    seeking_venue = True
  else:
    seeking_venue = False
  print(seeking_venue)
  seeking_description = request.form['seeking_description']



  error=False
  try:
      artist_s=Artist.query.get(artist_id)
     
      artist_s.name=name
      artist_s.city=city
      artist_s.state=state
      artist_s.phone=phone
      artist_s.image_link=image_link
      artist_s.facebook_link=facebook_link
      artist_s.website=website
      artist_s.seeking_description=seeking_description

      artist_s.seeking_venue=seeking_venue
      print(city)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully edited!')
      return redirect(url_for('show_artist', artist_id=artist_id))
  except:
      error=True
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
      return render_template('pages/home.html')
  finally:
      db.session.close()
  if not error:
    return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)

  venue_s={
    "id": venue_id,
    "name": venue.name,
    # "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "address": venue.address,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_s)

  '''venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }'''

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']

  website = request.form['website_link']

  if request.form.get('seeking_venue') == 'Yes':
    seeking_venue = True
  else:
    seeking_venue = False
  print(seeking_venue)
  seeking_description = request.form['seeking_description']



  error=False
  try:
      venue_s=Artist.query.get(venue_id)
     
      venue_s.name=name
      venue_s.city=city
      venue_s.state=state
      venue_s.phone=phone
      venue_s.image_link=image_link
      venue_s.facebook_link=facebook_link
      venue_s.website=website
      venue_s.seeking_description=seeking_description
      venue_s.seeking_venue=seeking_venue

      print(phone)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully edited!')
      return redirect(url_for('show_venue', venue_id=venue_id))
  except:
      error=True
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
      return render_template('pages/home.html')
  finally:
      db.session.close()
  if not error:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm()

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']

  website = request.form['website_link']
  if request.form.get('seeking_talent') =='Yes':
    seeking_talent = True
  else:
    seeking_talent = False
  seeking_description = request.form['seeking_description']

  print(name, city, state)

  error=False
  try:
      new_artist= Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, facebook_link=facebook_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
    
      db.session.add(new_artist)            
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  except:
      error=True
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      return render_template('pages/home.html')
  finally:
      db.session.close()
  if not error:
        return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows= Show.query.all()
  print(shows)
  data=[]

  for show in shows:
    print(show)
    venue= Venue.query.get(show.venue_id)
    artist= Artist.query.get(show.venue_id)
    

    data.append({
    "venue_id": show.venue_id,
    "venue_name": venue.name,
    "artist_id": show.artist_id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time": str(show.start_time_)
  })

  return render_template('pages/shows.html', shows=data)

  '''data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]'''

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()

  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']
  
  print(artist_id, venue_id, start_time)

  error=False
  try:
      new_show= Show(start_time=str(start_time), artist_id=artist_id, venue_id=venue_id)
      print(new_show)
      db.session.add(new_show)            
      db.session.commit()
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
  except:
      error=True
      db.session.rollback()
      flash('Show was was not listed!')
      return render_template('pages/home.html')
  finally:
      db.session.close()
  if not error:
    return render_template('pages/home.html')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
