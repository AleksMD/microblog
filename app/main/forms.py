from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, InputRequired, Email, EqualTo, Length
from app.models import User
from flask_babel import _, lazy_gettext as _l
from flask import request 


class LoginForm(FlaskForm):
	'''
		
		Contains fields for registered users to log in.

		LoginForm is presented on index page

	'''
	username = StringField(_l('Username'), validators=[InputRequired()])
	
	password = PasswordField(_l('Password'), validators=[InputRequired()])
	
	remember_me = BooleanField(_l('Remember Me'))
	
	submit = SubmitField(_l('Sign In'))

class RegistrationForm(FlaskForm):
	'''
		Contains fields for unregistered users in order to get registration
		RegistrationForm is presented on login page
		
		Any methods that match the pattern "validate_<field_name>", 
		WTForms takes those as custom validators and 
		invokes them in addition to the stock validators
	'''

	username = StringField(_l('Username'), validators=[InputRequired()])
	
	password = PasswordField(_l('Password'), validators=[InputRequired()])
	
	confirm_password = PasswordField(_l('Confirm password'), validators=[InputRequired(),
										EqualTo('password')])
	
	email = StringField(_l('Email'), validators=[InputRequired(), Email()])
	
	submit = SubmitField(_l('Register'))

	def validate_username(self, username: str):
		'''

			Checks user via username in database. 
			If username alredy exists in db -> raise ValueError.

		'''
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValueError(_('Please use another username!'))

	def validate_email(self, email: str):
		'''

			Checks user via email in database.
			If email already exists in db -> raise ValueError

		'''

		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValueError(_('Please use another email!'))

class EditProfileForm(FlaskForm):
	'''
		Allows user to add some additional information about them

	'''

	username = StringField(_l('Username'), validators=[InputRequired()])
	
	about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)])
	
	submit = SubmitField(_l('Submit'))

	def __init__(self, original_username, *args, **kwargs):
		super(EditProfileForm, self).__init__(*args, **kwargs)
		self.original_username = original_username

	def validate_username(self, username):
		if username.data != self.original_username:
			user = User.query.filter_by(username=self.username.data).first()
			if user is not None:
				raise ValidationError(_('Please use a different username!'))

class PostForm(FlaskForm):
	'''

		Creates a web form for users' posts

	'''
	post = TextAreaField(_l('Say something'), validators=[
		InputRequired(), Length(min=1, max=140)])
	
	submit = SubmitField(_l('Submit'))
	

class ResetPasswordRequestForm(FlaskForm):
	
	email = StringField(_l('Email'), validators=[InputRequired(), Email()])
	submit = SubmitField(_l('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
	
	password = PasswordField(_l('Password'), validators=[InputRequired()])
	password2 = PasswordField(_l('Repeat Password'), validators=[InputRequired(),
								EqualTo('password')])
	submit = SubmitField(_l('Request Password Reset'))

class SearchForm(FlaskForm):
	
	q = StringField(_l('Search'), validators=[InputRequired()])

	def __init__(self, *args, **kwargs):
		if 'formdata' not in kwargs:
			kwargs['formdata'] = request.args
		if 'csrf_enabled' not in kwargs:
			kwargs['csrf_enabled'] = False
		super(SearchForm, self).__init__(*args, **kwargs)