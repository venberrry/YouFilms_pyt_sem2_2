from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Film(db.Model):
    __tablename__ = 'films'
    fid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    engname = db.Column(db.String(40))
    poster = db.Column(db.String(150))
    genres = db.Column(db.String(100))
    year_of_release = db.Column(db.String(20))
    county = db.Column(db.String(100))
    mpaa = db.Column(db.String(5))
    time_duration = db.Column(db.String(20))
    description = db.Column(db.String(500))
    director = db.Column(db.String(200))
    average_rating = db.Column(db.Float, default=0.0)
    amount_rating = db.Column(db.Integer, default=0)

class Serial(db.Model):
    __tablename__ = 'serials'
    sid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    engname = db.Column(db.String(40))
    poster = db.Column(db.String(150))
    genres = db.Column(db.String(100))
    year_of_release = db.Column(db.String(20))
    county = db.Column(db.String(100))
    mpaa = db.Column(db.String(5))
    time_duration = db.Column(db.String(20))
    description = db.Column(db.String(500))
    director = db.Column(db.String(50))
    average_rating = db.Column(db.Float, default=0.0)
    amount_rating = db.Column(db.Integer, default=0)

class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(300))

class Profile(db.Model):
    __tablename__ = 'profile'
    pid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), unique=True)
    avatar = db.Column(db.String(150))
    email = db.Column(db.String(40))
    bio = db.Column(db.String(400))

class FilmReview(db.Model):
    __tablename__ = 'film_reviews'
    frid = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.pid'))
    film_id = db.Column(db.Integer, db.ForeignKey('films.fid'))
    title = db.Column(db.String(40))
    rating = db.Column(db.Float, default=0.0)
    review_text = db.Column(db.String(1000))

class SerialReview(db.Model):
    __tablename__ = 'serial_reviews'
    srid = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.pid'))
    serial_id = db.Column(db.Integer, db.ForeignKey('serials.sid'))
    title = db.Column(db.String(40))
    rating = db.Column(db.Float, default=0.0)
    review_text = db.Column(db.String(1000))

favorite_films = db.Table('favorite_films',
    db.Column('profile_id', db.Integer, db.ForeignKey('profile.pid'), primary_key=True),
    db.Column('film_id', db.Integer, db.ForeignKey('films.fid'), primary_key=True)
)

favorite_serials = db.Table('favorite_serials',
    db.Column('profile_id', db.Integer, db.ForeignKey('profile.pid'), primary_key=True),
    db.Column('serial_id', db.Integer, db.ForeignKey('serials.sid'), primary_key=True)
)
