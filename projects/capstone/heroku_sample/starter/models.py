from sqlalchemy import Column, String, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

class Movie(db.Model):  
  __tablename__ = 'movie'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  producer = Column(String)
  director = Column(String)
  genres = Column(ARRAY(String))
  release_date = Column(Date)

  def __init__(self, name, producer, director, genres, release_date):
    self.name = name
    self.producer = producer
    self.director = director
    self.genres = genres
    self.release_date = release_date

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'producer': self.producer,
      'director': self.director,
      'genres': self.genres,
      'release_date': self.release_date
    }