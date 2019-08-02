from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, InputRequired, Email, EqualTo, Length
from app.models import User
from flask_babel import _, lazy_gettext as _l

class LoginForm(FlaskForm):
	username = StringField(_l('Username'), validators=[InputRequired()])
	password = PasswordField(_l('Password'), validators=[InputRequired()])
	remember_me = BooleanField(_l('Remember Me'))
	submit = SubmitField(_l('Sign In'))

class RegistrationForm(FlaskForm):
	username = StringField(_l('Username'), validators=[InputRequired()])
	password = PasswordField(_l('Password'), validators=[InputRequired()])
	confirm_password = PasswordField(_l('Confirm password'), validators=[InputRequired(),
										EqualTo('password')])
	email = StringField(_l('Email'), validators=[InputRequired(), Email()])
	submit = SubmitField(_l('Register'))

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValueError(_('Please use another username!'))

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValueError(_('Please use another email!'))

class EditProfileForm(FlaskForm):
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
