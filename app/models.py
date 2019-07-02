from app import db, login

from werkzeug.security import generate_password_hash as gen_pswrd, \
check_password_hash as check_pswrd # for generating and checking users passwords during verification

from flask_login import UserMixin # tracks users current login status

from datetime import datetime

now = datetime.utcnow # is needed for further representation 
				   #without microseconds in timestampField

from hashlib import md5 # for generating and obtaining user avatar


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128), index=True, unique=True)
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)

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

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=now().replace(microsecond=0))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return 'Post {}'.format(self.body)