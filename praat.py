import subprocess
import matplotlib.pyplot as plt
from flask import Flask, request, g, session, redirect, url_for, abort, jsonify, send_from_directory
from flask_login import login_user, login_required, LoginManager, UserMixin
from flask_googlelogin import GoogleLogin
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, UniqueConstraint, ForeignKey
import datetime
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_cors import CORS
import utils

# Locations of required files
_images_dir = "images/"
_scripts_dir = "scripts/"
_sounds_dir = "sounds/"
_eaf_dir = "eaf/"
_linkElanPraat_dir = "combined/"

# Run script 'scriptName' with the provided parameters
def runScript(scriptName, args):
   praatExec = ["/usr/bin/praat", "--run", "--no-pref-files", scriptName];
   praatExec.extend(args)
   #print str(praatExec)
   output = subprocess.check_output(praatExec);
   #print "output from praat.py is: "+str(output)
   return output

# Create flask app
app = Flask(__name__, static_url_path="")
app.config.update(
    # https://code.google.com/apis/console
    GOOGLE_LOGIN_SCOPES = 'email,profile',
    DEBUG = True
)

login_manager = LoginManager()

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

googlelogin = GoogleLogin(app, login_manager)
googlelogin.user_loader(user_loader)


# setup sqlalchemy
db_session = None
Base = declarative_base()

def init_db():
    engine = create_engine(app.config['DATABASE_URI'], echo=True)
    global db_session
    global Base
    db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=True,
                                         bind=engine))
    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)

import enum
class Role(enum.Enum):
    reader = 1
    editor = 2

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(String(60), primary_key=True)
    name = Column(String(120))
    google_id = Column(String(60), unique=True)
    email = Column(String(240))
    current_group_id = Column(String(60), nullable=True)
    groups = relationship('Group', back_populates='owner')
    annotations = relationship('Annotation', back_populates='owner')
    annotation_permissions = relationship('AnnotationPermission', back_populates='user')

    def __init__(self, name, google_id, email, _id=None):
        self.id = utils.generate_id(_id)
        self.name = name
        self.google_id = google_id
        self.email = email

class Group(Base):
    __tablename__ = 'groups'
    id = Column(String(60), primary_key=True)
    name = Column(String(240), unique=True)
    owner_id = Column(String(60), ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    owner = relationship('User', back_populates='groups')
    audios = relationship('Audio', back_populates='owner')

    def __init__(self, name, owner, _id=None):
        self.id = utils.generate_id(_id)
        self.name = name
        self.owner_id = owner.id

class Audio(Base):
    __tablename__ = 'audios'
    id = Column(String(60), primary_key=True)
    name = Column(String(240))
    creator_id = Column(String(60), ForeignKey('users.id'))
    owner_id = Column(String(60), ForeignKey('groups.id'))
    location = Column(String(60), default='')
    owner = relationship('Group', back_populates='audios')
    annotations = relationship('Annotation', back_populates='audio')

    def __init__(self, name, creator, owner, location='', _id=None):
        self.id = utils.generate_id(_id)
        self.name = name
        self.creator_id = creator.id
        self.owner_id = owner.id
        self.location = location


class Annotation(Base):
    __tablename__ = 'annotations'
    id = Column(String(60), primary_key=True)
    name = Column(String(240))
    audio_id = Column(String(60), ForeignKey('audios.id'))
    owner_id = Column(String(60), ForeignKey('users.id'))
    audio = relationship('Audio', back_populates='annotations')
    owner = relationship('User', back_populates='annotations')
    annotation_permissions = relationship('AnnotationPermission', back_populates='annotation')

    def __init__(self, name, audio, owner, _id=None):
        self.id = utils.generate_id(_id)
        self.name = name
        self.audio_id = audio.id
        self.owner = owner.id


class AnnotationPermission(Base):
    __tablename__ = 'annotation_permissions'
    id = Column(String(60), primary_key=True)
    user_id = Column(String(60), ForeignKey('users.id'))
    annotation_id = Column(String(60), ForeignKey('annotations.id'))
    role = Column(Enum(Role))
    __table_args__ = (UniqueConstraint('user_id', 'annotation_id', name='_usr_atn_tuple'),)
    user = relationship('User', back_populates='annotation_permissions')
    annotation = relationship('Annotation', back_populates='annotation_permissions')

    def __init__(self, user, annotation, role, _id):
        self.id = utils.generate_id(_id)
        self.user_id = user.id
        self.annotation_id = annotation.id
        self.role = role


@app.route('/oauth2callback')
@googlelogin.oauth2callback
def create_or_update_user(token, userinfo, **params):
    print("User info: " + str(userinfo))
    user = User.query.filter_by(google_id=userinfo['id']).first()
    #user = User.query.get(userinfo['id'])
    if user:
        user.name = userinfo['name']
        group = Group.query.get(utils.generate_id(user.id))
        group.name = utils.personal_group_name(user)
    else:
        user = User(userinfo['name'], userinfo['id'], userinfo['email'], userinfo['id'])
        db_session.add(user)
        db_session.commit()
        g_name = utils.personal_group_name(user)
        group = Group(g_name, user, user.id)
        db_session.add(group)
        db_session.commit()
        user.current_group_id = group.id
    db_session.commit()
    login_user(user)
    print("Session:")
    print("User %s is in groups %s" % (user.name, str(user.groups)))
    if session:
        print(session)
    return redirect(url_for('index'))

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.after_request
def after_request(response):
    db_session.remove()
    return response


# Add CORS headers to allow cross-origin requests
CORS(app)

#Import views
from views import *

