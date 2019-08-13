

from flask import current_app

from werkzeug.security import generate_password_hash as gen_pswrd, \
check_password_hash as check_pswrd # for generating and checking users passwords during verification

from flask_login import UserMixin # tracks users current login status

from datetime import datetime

from app import db, login

from hashlib import md5 # for generating and obtaining user avatar// creates hash

from time import time

import jwt # creates tokens in case of reseting and/or recreating users passwords

from app.search import add_to_index, \
remove_from_index, query_index # is used for creating mixin class for interacting 
                               #between search engine and SQLDB



followers = db.Table('followers',#association table for many-to-many relationship in "User" table
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
	)

class User(UserMixin, db.Model):
'''
	Represents user model in SQL db.
	UserMixin if part of Flask-Login extension 
		works with the application's user model.
'''

	id = db.Column(db.Integer, primary_key=True)
	
	username = db.Column(db.String(64), index=True, unique=True)
	
	email = db.Column(db.String(120), index=True, unique=True)
	
	password_hash = db.Column(db.String(128), index=True, unique=True)
	
	#referes to 'Post' model via user.id and will be labeled post.author
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	
	about_me = db.Column(db.String(140))
	
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	
	#selfreference -> one user can refere to another one(and/or more than one) via id
	followed = db.relationship('User', secondary=followers,
	 	primaryjoin=(followers.c.follower_id == id),
	 	secondaryjoin=(followers.c.followed_id == id),
	 	backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')



	def __repr__(self):
		return 'User {}'.format(self.username)

	def set_password(self, password: str):
		'''
			Set hash representation of given password-argument
		'''
		self.password_hash = gen_pswrd(password)

	def check_password(self, password: str):
		'''
			Returns True or False after comparing of a hash of suggested
			password with those in 'self.password_hash' variable
		'''
		return check_pswrd(self.password_hash, password)

	@login.user_loader#tracks logged in users
	def load_user(id):
		'''
			Load user from database via id
		'''
		return User.query.get(int(id))

	def avatar(self, size):
		
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()#make hash that will be use to obtain avatar
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
			digest, size)#URL for avatar

	def follow(self, user):
		
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self, user):
		
		if self.is_following(user):
			self.followed.remove(user)

	def is_following(self, user):
		
		return self.followed.filter(
			followers.c.followed_id == user.id).count() > 0 #built-in method in SQLAlchemy

	def followed_posts(self):#get post of followed user
		
		followed = Post.query.join(
			followers, (followers.c.followed_id == Post.user_id)).filter(
				followers.c.follower_id == self.id)
		
		own = Post.query.filter_by(user_id =self.id)
		
		return followed.union(own).order_by(Post.timestamp.desc())

	def get_reset_password_token(self, expires_in=600):
		'''
		Generates a JWT token as a string. 
			The decode('utf-8') is necessary because the jwt.encode() 
			function returns the token as a byte sequence.

		'''
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_reset_password_token(token):
		
		try:
			id = jwt.decode(token, current_app.config['SECRET_KEY'],
							algorithm=['HS256'])['reset_password']
		except:
			return None
		
		return User.query.get(id)

class SearchableMixin(object):

	@classmethod
	def search(cls, expression, page, per_page):
		
		ids, total = query_index(cls.__tablename__, expression, page, per_page)
		if total == 0:
			return cls.query.filter_by(id=0), 0
		
		when = [(ids[i], i) for i in range(len(ids))]
		
		return cls.query.filter(cls.id.in_(ids)).order_by(
			db.case(when, value=cls.id)), total

	@classmethod
	def before_commit(cls, session):
		
		session._changes = {
							'add': list(session.new),
							'update': list(session.dirty),
							'delete': list(session.deleted)
							}

	@classmethod
	def after_commit(cls, session):
		
		for obj in session._changes['add']:
			if isinstance(obj, SearchableMixin):
				add_to_index(obj.__tablename__, obj)
		
		for obj in session._changes['update']:
			if isinstance(obj, SearchableMixin):
				add_to_index(obj.__tablename__, obj)
		
		for obj in session._changes['delete']:
			if isinstance(obj, SearchableMixin):
				remove_from_index(obj.__tablename__, obj)
		session._changes = None

	@classmethod
	def reindex(cls):
		
		for obj in cls.query:
			add_to_index(cls.__tablename__, obj)
			
db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

class Post(SearchableMixin, db.Model):
	
	__searchable__ = ['body'] # is needed for indexing fields

	id = db.Column(db.Integer, primary_key=True)
	
	body = db.Column(db.String(140))
	
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	language = db.Column(db.String(5))

	def __repr__(self):
		return 'Post {}'.format(self.body)


