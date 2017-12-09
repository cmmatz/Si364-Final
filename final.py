## SI 364

## Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request, jsonify
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
import json

from flask_migrate import Migrate, MigrateCommand
from wtforms import StringField, SubmitField, FileField, PasswordField, BooleanField, SelectMultipleField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_script import Manager, Shell
from wtforms.validators import Required

from flask_mail import Mail, Message
from threading import Thread
from werkzeug import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user

import requests
import feedparser

# Configure base directory of app
basedir = os.path.abspath(os.path.dirname(__file__))

# Application configurations
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364(thisisnotsupersecure)'

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/cmmatz_final"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587 
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'carlymatz5@gmail.com' 
app.config['MAIL_SUBJECT_PREFIX'] = '[New Podcast Results]'
app.config['MAIL_SENDER'] = 'Admin <carlymatz5@gmail.com>' 
app.config['ADMIN'] = 'carlymatz5@gmail.com'

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)
# Set up Flask debug stuff
manager = Manager(app)
db = SQLAlchemy(app) # For database use
migrate = Migrate(app, db) # For database use/updating
manager.add_command('db', MigrateCommand) # Add migrate command to manager
mail = Mail(app) # For email sending

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs): 
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject, sender=app.config['MAIL_SENDER'], recipients=[to])
    with app.app_context():
        msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + '.html', **kwargs)
        thr = Thread(target=send_async_email, args=[app, msg]) 
        thr.start()
        return thr



##### Set up Models #####

user_subscription = db.Table('user_subscription', db.Column('listener_id', db.Integer, db.ForeignKey('listeners.listener_id')), db.Column('podcast_id', db.Integer, db.ForeignKey('podcasts.podcast_id')))

# User model
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(200), unique=True)    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

## DB load functions
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # returns User object or None

class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
    password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
    password2 = PasswordField("Confirm Password:",validators=[Required()])
    submit = SubmitField('Register User')

    #Additional checking methods for the form
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

# Podcast model
class Podcast(db.Model):
    __tablename__ = 'podcasts'
    podcast_id = db.Column(db.Integer, primary_key=True) ## -- id (Primary Key)
    title = db.Column(db.String, unique=True) 
    podcast_maker = db.Column(db.String)
    podcast_art = db.Column(db.String)
    link = db.Column(db.String)

class Episode(db.Model):
    __tablename__ = 'episodes'
    episode_id = db.Column(db.Integer, primary_key=True) ## -- id (Primary Key)
    title = db.Column(db.String, unique=True) 
    podcast_id = db.Column(db.Integer, db.ForeignKey('podcasts.podcast_id'))
    link = db.Column(db.String)
    published = db.Column(db.String)
    summary = db.Column(db.String)

class PodSubscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    podcast_id = db.Column(db.Integer, db.ForeignKey('podcasts.podcast_id'))


##### Set up Forms #####

class PodcastSearch(FlaskForm):
    text = StringField("Search by producer/title/content", validators=[Required()])
    send_email = BooleanField("Email me matching podcast names.")
    submit = SubmitField('Submit')

def get_or_create_podcast(title, artist, art, feed):
    cast = db.session.query(Podcast).filter_by(title=title).first()
    if cast:
        return cast
    else:
        cast = Podcast(title=title, podcast_maker=artist, podcast_art=art, link=feed)
        db.session.add(cast)
        db.session.commit()
        return cast

def getSearchResults(searchTerm):
    data = requests.get("https://itunes.apple.com/search?entity=podcast&term={}".format(searchTerm)).json()["results"]
    for res in data:
        get_or_create_podcast(res["trackName"], res["artistName"], res["artworkUrl600"], res["feedUrl"])
    return data

def get_or_create_episode(title, podcast_id, link, date, summary):
    epi = db.session.query(Episode).filter_by(title=title, podcast_id=podcast_id).first()
    if epi:
        return epi
    else:
        epi = Episode(title=title, podcast_id=podcast_id, link=link, published=date, summary=summary)
        db.session.add(epi)
        db.session.commit()
        return epi

def getEpisodesFromFeed(feed_url, podcast_id):
    data = feedparser.parse(feed_url)
    for epi in data["entries"]:
        get_or_create_episode(epi["title"], podcast_id, epi['links'][0]['href'], epi["published"], epi["summary"])
    return data

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

##### Controllers (view functions) #####

## Error handling routes
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/register',methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

@app.route('/', methods=['GET'])
@login_required
def index():
    form = PodcastSearch()
    return render_template("index.html", form=form)

@app.route('/results',methods=["POST"])
@login_required
def results():
    form = PodcastSearch()
    if form.validate_on_submit():
        results = getSearchResults(form.text.data)
        if form.send_email.data:
            send_email(current_user.email, "Podcast Results", "mail/results", data=results, search=form.text.data)
        return render_template("results.html", data=results, search=form.text.data)

@app.route('/podcast/<name>',methods=["GET", "POST"])
@login_required
def episodes(name):
    podcast = db.session.query(Podcast).filter_by(title=name).first()
    if request.method == "POST":
        new_sub = PodSubscription(user_id=current_user.id, podcast_id=podcast.podcast_id)
        db.session.add(new_sub)
        db.session.commit()
    return render_template("podcast.html", data=getEpisodesFromFeed(getSearchResults(name)[0]["feedUrl"], podcast.podcast_id), name=name)

@app.route('/subscriptions',methods=["GET"])
@login_required
def subs():
    return render_template("subscriptions.html")

@app.route('/subscriptions_data',methods=["GET"])
@login_required
def subs_api():
    subscripts = db.session.query(PodSubscription, Podcast).filter(PodSubscription.user_id==current_user.id).join(Podcast).all()
    return jsonify({"subscriptions":[sub.Podcast.title for sub in subscripts]})

if __name__ == '__main__':
    db.create_all()
    manager.run() # Run with this: python final.py runserver
    # Also provides more tools for debugging
