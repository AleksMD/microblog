from app import db, login, app

from werkzeug.security import generate_password_hash as gen_pswrd, \
check_password_hash as check_pswrd # for generating and checking users passwords during verification

from flask_login import UserMixin # tracks users current login status

from datetime import datetime

now = datetime.utcnow # is needed for further representation 
				   #without microseconds in timestampField

from hashlib import md5 # for generating and obtaining user avatar
from time import time
import jwt


followers = db.Table('followers',#association table for many-to-many relationship in "User" table
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
	)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128), index=True, unique=True)
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	followed = db.relationship('User', secondary=followers,
	 	primaryjoin=(followers.c.follower_id == id),
	 	secondaryjoin=(followers.c.followed_id == id),
	 	backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')



	def __repr__(self):
		return 'User {}'.format(self.username)

	def set_password(self, password):
		self.password_hash = gen_pswrd(password)

	def check_password(self, password):
		return check_pswrd(self.password_hash, password)

	@login.user_loader
	def load_user(id):
		return User.query.get(int(id))

	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
			digest, size)

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
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, app.config['SECRET_KEY'],
							algorithm=['HS256'])['reset_password']
		except:
			return None
		return User.query.get(id)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=now().replace(microsecond=0))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return 'Post {}'.format(self.body)


