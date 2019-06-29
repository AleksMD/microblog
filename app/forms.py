from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, InputRequired, Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[InputRequired()])
	password = PasswordField('Password', validators=[InputRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[InputRequired()])
	password = PasswordField('Password', validators=[InputRequired()])
	confirm_password = PasswordField('Confirm password', validators=[InputRequired(),
										EqualTo('password')])
	email = StringField('Email', validators=[InputRequired(), Email()])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValueError('Please use another username!')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValueError('Please use another email!')

class EditProfileForm(FlaskForm):
	username = StringField('Username', validators=[InputRequired()])
	about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
	submit = SubmitField('Submit')