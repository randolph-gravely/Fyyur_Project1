#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from datetime import datetime
import dateutil.parser
import babel
from sqlalchemy import func
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from sqlalchemy.dialects import postgresql
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TDONE ODO: connect to a local postgresql database DONE

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.String(20), nullable=False)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship("Show", backref='venue',lazy=True, cascade = "all, delete-orphan")

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

migrate = Migrate(app, db)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship("Show", backref='artist', lazy=True, cascade = "all, delete-orphan")

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  query = Venue.query.all()
  dict = []
  for q in query:
      area = {
        "city" : q.city,
        "state" : q.state,
        "venues" : Venue.query.filter_by(city=q.city).filter_by(state=q.state).all()
        }
      if area not in dict:
          dict.append(area)

  data = dict

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_query = request.form.get('search_term')
  response = {"count" : Venue.query.filter(Venue.name.ilike(f'%{search_query}%')).count(),
      'data' : Venue.query.filter(Venue.name.ilike(f'%{search_query}%')).all()
      }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE- DONE: replace with real venue data from the venues table, using venue_id
  show_query = Show.query.filter_by(venue_id=venue_id).all()
  past_shows_count = 0
  past_shows = []
  upcoming_shows_count = 0
  upcoming_shows = []
  now = datetime.now()
  for show in show_query:
      if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')  < now:
          past_shows_count += 1
          past_shows.append({
            "artist_id" : show.artist_id,
            "artist_name" : Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link" : Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time": show.start_time
            })
      else:
            upcoming_shows_count += 1
            upcoming_shows.append({
              "artist_id" : show.artist_id,
              "artist_name" : Artist.query.filter_by(id=show.artist_id).first().name,
              "artist_image_link" : Artist.query.filter_by(id=show.artist_id).first().image_link,
              "start_time": show.start_time
              })

  query = Venue.query.filter_by(id=venue_id).first()
  data = {
    "id" : query.id,
    "name" : query.name,
    "genres": query.genres,
    "city" : query.city,
    "address": query.address,
    "facebook_link" : query.facebook_link,
    "state" : query.state,
    "phone" : query.phone,
    "website": query.website,
    "seeking_talent" : query.seeking_talent,
    "seeking_description" : query.seeking_description,
    "image_link" : query.image_link,
    "past_shows" : past_shows,
    "past_shows_count" : past_shows_count,
    "upcoming_shows" : upcoming_shows,
    "upcoming_shows_count" : upcoming_shows_count
    }


  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # Done: insert form data as a new Venue record in the db, instead
  # Done: modify data to be the data object returned from db insertion
  try:
      name = request.form.get('name', '')
      city = request.form.get('city', '')
      state = request.form.get('state', '')
      phone = request.form.get('phone', '')
      address = request.form.get('address', '')
      genres = request.form.getlist('genres')
      facebook_link = request.form.get('facebook_link', '')
      venue = Venue(name=name,
          city=city,
          state=state,
          address=address,
          phone=phone,
          genres=genres,
          facebook_link=facebook_link
          )
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occured. Venue "' + request.form['name'] + '" has not been listed.')
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
      flash('Success! Venue "' + venue.name + '" has been deleted.')
  except:
      flash('An error occured. Venue "' + venue.name + '" has not been deleted.')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  finally:
     return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  data= Artist.query.all()


  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_query = request.form.get('search_term')
  response = {"count" : Artist.query.filter(Artist.name.ilike(f'%{search_query}%')).count(),
        'data' : Artist.query.filter(Artist.name.ilike(f'%{search_query}%')).all()
        }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  show_query = Show.query.filter_by(artist_id=artist_id).all()
  past_shows_count = 0
  past_shows = []
  upcoming_shows_count = 0
  upcoming_shows = []
  now = datetime.now()
  for show in show_query:
      if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')  < now:
          past_shows_count += 1
          past_shows.append({
            "venue_id" : show.venue_id,
            "venue_name" : Venue.query.filter_by(id=show.venue_id).first().name,
            "venue_image_link" : Venue.query.filter_by(id=show.venue_id).first().image_link,
            "start_time": show.start_time
            })
      else:
            upcoming_shows_count += 1
            upcoming_shows.append({
              "venue_id" : show.venue_id,
              "venue_name" : Venue.query.filter_by(id=show.venue_id).first().name,
              "venue_image_link" : Venue.query.filter_by(id=show.venue_id).first().image_link,
              "start_time": show.start_time
              })

  query = Artist.query.filter_by(id=artist_id).first()
  data = {
    "id" : query.id,
    "name" : query.name,
    "genres": query.genres,
    "city" : query.city,
    "state" : query.state,
    "phone" : query.phone,
    "facebook_link" : query.facebook_link,
    "website": query.website,
    "seeking_venue" : query.seeking_venue,
    "seeking_description" : query.seeking_description,
    "image_link" : query.image_link,
    "past_shows" : past_shows,
    "past_shows_count" : past_shows_count,
    "upcoming_shows" : upcoming_shows,
    "upcoming_shows_count" : upcoming_shows_count
    }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()

  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
     artist = Artist.query.get(artist_id)
     try:
         artist.name = request.form.get('name', '')
         artist.city = request.form.get('city', '')
         artist.state = request.form.get('state', '')
         artist.phone = request.form.get('phone', '')
         artist.address = request.form.get('address')
         artist.genres = request.form.getlist('genres')
         artist.facebook_link = request.form.get('facebook_link', '')
         db.session.commit()
         flash('Artist ' + request.form['name'] + ' was successfully updated!')
     except Exception as e:
       flash('An error occured. Artist ' + request.form['name'] + ' has not been edited. {}'.format(e))
       db.session.rollback()
     finally:
       db.session.close()
       return render_template('pages/home.html')
       return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  try:
      venue.name = request.form.get('name', '')
      venue.city = request.form.get('city', '')
      venue.state = request.form.get('state', '')
      venue.phone = request.form.get('phone', '')
      venue.address = request.form.get('address')
      venue.genres = request.form.getlist('genres')
      venue.facebook_link = request.form.get('facebook_link', '')
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except Exception as e:
       flash('An error occured. Venue ' + request.form['name'] + ' has not been edited. {}'.format(e))
       db.session.rollback()
  finally:
       db.session.close()
       return render_template('pages/home.html')


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
     try:
         name = request.form.get('name', '')
         city = request.form.get('city', '')
         state = request.form.get('state', '')
         phone = request.form.get('phone', '')
         address = request.form.get('address')
         genres = request.form.getlist('genres')
         facebook_link = request.form.get('facebook_link', '')
         artist = Artist(name=name,
             city=city,
             state=state,
             phone=phone,
             genres=genres,
             facebook_link=facebook_link
             )
         db.session.add(artist)
         db.session.commit()
         flash('Artist ' + request.form['name'] + ' was successfully listed!')
     except:
       flash('An error occured. Artist ' + request.form['name'] + 'has not been listed.')
       error = True
       db.session.rollback()
     finally:
       db.session.close()
       return render_template('pages/home.html')
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data =[]
  query = Show.query.order_by('start_time').all()
  for show in query:
      dict = {
        "venue_id" : show.venue_id,
        "artist_id" : show.artist_id,
        "venue_name" : Venue.query.filter_by(id=show.venue_id).first().name,
        "artist_name" : Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link" : Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time" : show.start_time
        }
      data.append(dict)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
    try:
        artist_id = request.form.get('artist_id')
        venue_id = request.form.get('venue_id')
        start_time = request.form.get('start_time')
        show = Show(venue_id=venue_id,
            artist_id=artist_id,
            start_time=start_time,
            )
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
      flash('An error occured. Show has not been listed.')
      db.session.rollback()
    finally:
      db.session.close()
  # on successful db insert, flash success
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      return render_template('pages/home.html')

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
