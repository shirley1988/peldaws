import subprocess
import matplotlib.pyplot as plt
from flask import Flask, request, g, session, redirect, url_for, abort, jsonify, send_from_directory
from flask_login import login_user, login_required, LoginManager, UserMixin
from flask_googlelogin import GoogleLogin
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, UniqueConstraint, ForeignKey, Table
import datetime, json
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
app = Flask(__name__, static_url_path="", template_folder="templates")
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

'''
membership_table = Table('members', Base.metadata,
    Column('group_id', String(60), ForeignKey('groups.id')),
    Column('user_id', String(60), ForeignKey('users.id')),
)
'''


class Member(Base):
    __tablename__ = 'members'
    id = Column(String(60), primary_key=True)
    group_id = Column(String(60), ForeignKey('groups.id'))
    user_id = Column(String(60), ForeignKey('users.id'))
    role = Column(Enum(Role))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    __table_args__ = (UniqueConstraint('group_id', 'user_id', name='_member_tuple'),)
    user = relationship('User', back_populates='i_membership')
    group = relationship('Group', back_populates='i_members')

    def __init__(self, group, user, role=Role.reader,  _id=None):
        self.id = utils.generate_id(_id)
        self.group_id = group.id
        self.user_id = user.id
	self.role = role

    def summary(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
	    'user_id': self.user_id,
            'role': self.descriptive_role(),
            'created_at': self.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    def descriptive_role(self):
        if self.role == Role.reader:
            return 'reader'
        if self.role == Role.editor:
            return 'editor'
        return 'none'

    def user_summary(self):
        _summary = self.user.summary()
        _summary['role'] = self.descriptive_role()
        return _summary

    def group_summary(self):
        _summary = self.group.summary()
        _summary['role'] = self.descriptive_role()
        return _summary

class ActionNotAuthorized(Exception):
    pass

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(String(60), primary_key=True)
    name = Column(String(120))
    google_id = Column(String(60), unique=True)
    email = Column(String(240))
    current_group_id = Column(String(60), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    ownership = relationship('Group', back_populates='owner')
    membership = relationship('Group', secondary=Member.__table__, back_populates='members')
    i_membership = relationship('Member', back_populates='user')

    def __init__(self, name, google_id, email, _id=None):
        self.id = utils.generate_id(_id)
        self.name = name
        self.google_id = google_id
        self.email = email

    def summary(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'currentGroupId': self.current_group_id,
	    'googleId': self.google_id,
            'createdAt': self.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    def details(self):
        s = self.summary()
        cg = Group.query.get(self.current_group_id)
        s['details'] = {
            'currentGroup': cg.summary(),
            #'ownership': list(grp.summary() for grp in self.ownership),
            'ownership': self.__owned_groups(),
            'membership': list(member.group_summary() for member in self.i_membership),
        }
        return s

    def __owned_groups(self):
        _groups = []
        for grp in self.ownership:
            member = Member.query.filter_by(user_id=self.id).filter_by(group_id=grp.id).first()
            _groups.append(member.group_summary())
        return _groups

class Group(Base):
    __tablename__ = 'groups'
    id = Column(String(60), primary_key=True)
    name = Column(String(240), unique=True)
    owner_id = Column(String(60), ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    owner = relationship('User', back_populates='ownership')
    audios = relationship('Audio', back_populates='owner')
    members = relationship('User', secondary=Member.__table__, back_populates='membership')
    i_members = relationship('Member', back_populates='group')

    def __init__(self, name, owner, _id=None):
        self.id = utils.generate_id(_id)
        self.name = name
        self.owner_id = owner.id

    def summary(self):
        return {
            'id': self.id,
            'name': self.name,
            'ownerId': self.owner_id,
            'ownerName': self.owner.name,
            'ownerEmail': self.owner.email,
            'createdAt': self.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    def details(self):
        s = self.summary()
        s['details'] = {
            'members': list(member.user_summary() for member in self.i_members),
            'audios': list(audio.summary() for audio in self.audios),
        }
        return s


class Audio(Base):
    __tablename__ = 'audios'
    id = Column(String(60), primary_key=True)
    name = Column(String(240))
    creator_id = Column(String(60), ForeignKey('users.id'))
    owner_id = Column(String(60), ForeignKey('groups.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    owner = relationship('Group', back_populates='audios')
    annotations = relationship('AudioAnnotation', back_populates='audio')

    def __init__(self, name, creator, owner,  _id=None):
        self.id = utils.generate_id(_id)
        self.name = name
        self.creator_id = creator.id
        self.owner_id = owner.id

    def summary(self):
        return {
            'id': self.id,
            'name': self.name,
            'ownerId': self.owner_id,
            'ownerName': self.owner.name,
            'createdAt': self.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'updatedAt': self.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }


class AudioAnnotation(Base):
    __tablename__ = 'annotations'
    id = Column(String(60), primary_key=True)
    name = Column(String(240))
    audio_id = Column(String(60), ForeignKey('audios.id'))
    audio_version = Column(String(60))
    start_time = Column(String(20))
    end_time = Column(String(20))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    audio = relationship('Audio', back_populates='annotations')

    def __init__(self, name, audio_id, audio_version, start_time, end_time, _id=None):
        self.id = utils.generate_id(_id)
        self.name = name
        self.audio_id = audio_id
        self.audio_version = audio_version
        self.start_time = start_time
        self.end_time = end_time

    def summary(self):
        return {
            'id': self.id,
            'name': self.name,
            'audioId': self.audio_id,
            'audioVersion': self.audio_version,
            'startTime': self.start_time,
            'endTime': self.end_time,
            'createdAt': self.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'updatedAt': self.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }


@app.route('/oauth2callback')
@googlelogin.oauth2callback
def create_or_update_user(token, userinfo, **params):
    print("User info: " + str(userinfo))
    user = User.query.filter_by(google_id=userinfo['id']).first()
    #user = User.query.get(userinfo['id'])
    if user:
        user.name = userinfo['name']
        #group = Group.query.get(utils.generate_id(user.id))
        #group.name = utils.personal_group_name(user)
    else:
        user = User(userinfo['name'], userinfo['id'], userinfo['email'], userinfo['id'])
        db_session.add(user)
        #g_name = utils.personal_group_name(user)
        #group = Group(g_name, user, user.id)
        #db_session.add(group)
        #db_session.commit()
        #user.current_group_id = group.id
    db_session.commit()
    login_user(user)
    check_personal_group(user)
    print("Session:")
    if session:
        print(session)
    return redirect(url_for('index'))

def check_personal_group(user):
    p_gid = utils.generate_id(user.id)
    group = Group.query.get(p_gid)
    # if personal group does not exist, create it
    if group is None:
        _name = utils.personal_group_name(user)
        group = Group(_name, user, user.id)
        db_session.add(group)
        db_session.commit()
    # if user has no current group id, use personal group
    if not user.current_group_id:
        user.current_group_id = group.id
    # make sure user has membership of personal group
    add_owner_to_group(user, user, group)


def add_owner_to_group(operator, user, group):
    if not is_owner(operator, group):
        msg = "User %s is not an owner of group %s" % (operator.name, group.name)
        raise ActionNotAuthorized(msg)

    if user not in group.members:
        print "Adding owner to group"
        member = Member(group, user, Role.editor)
        db_session.add(member)
        db_session.commit()

def add_user_to_group(operator, user, group, role=Role.reader):
    if user not in group.members:
	print "Adding user to group"
	member = Member(group, user, role)
	db_session.add(member)
	db_session.commit()

def update_user_role(operator, user_id, group_id, role):
    group = Group.query.get(group_id)
    if not is_owner(operator, group):
        msg = "User %s is not an owner of group %s" % (operator.name, group_id)
        raise ActionNotAuthorized(msg)
    member = Member.query.filter_by(group_id=group_id).filter_by(user_id=user_id).first()
    if role == 'reader' and member.role != Role.reader:
        member.role = Role.reader
        db_session.commit()
    elif role == 'editor' and member.role != Role.editor:
        member.role = Role.editor
        db_session.commit()


def remove_user_from_group(operator, user, group):
    if not is_owner(operator, group):
        msg = "User %s is not an owner of group %s" % (operator.name, group.name)
        raise ActionNotAuthorized(msg)
    member = Member.query.filter_by(group_id=group.id).filter_by(user_id=user.id).first()
    # print "User: " + json.dumps(user.id);
    # print "Group: " + json.dumps(group.owner_id);
    if user.id == group.owner_id:
	print "User input is the owner of group, and cannot be deleted"
	msg = "User %s is the owner of current group, owner cannot be deleted" % (operator.name)
	raise ActionNotAuthorized(msg)

    if member is not None:
        print "Removing user from group"
        db_session.delete(member)
        db_session.commit()

def transfer_group(operator, user, group):
    if not is_owner(operator, group):
        msg = "User %s is not an owner of group %s" % (operator.name, group.name)
        raise ActionNotAuthorized(msg)
    if group.id == utils.generate_id(operator.id):
        raise ActionNotAuthorized("Personal group ownership cannot be transferred")
    if group.owner_id != user.id:
        # make sure new owner has membership
        print "Adding user %s to group %s as editor" % (user.id, group.id)
        add_user_to_group(operator, user, group, Role.editor)
        # transfer owner
        group.owner_id = user.id
        db_session.commit()

def create_group(operator, g_name):
    group = Group(g_name, operator)
    db_session.add(group)
    db_session.commit()
    member = Member(group, operator, Role.editor)
    db_session.add(member)
    db_session.commit()


def is_owner(entity, resource):
    return resource.owner_id == entity.id

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

