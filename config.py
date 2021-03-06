import os
from dotenv import load_dotenv #load environmental variable from .flaskenv file


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))



class Config(object):
	#following options are for development mode and CSRF protection
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret'
	DEBUG = False

	#following options are for implementing relational db usage
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	
	#following options are for email support for users or/and admins
	MAIL_SERVER = os.environ.get('MAIL_SERVER')
	MAIL_PORT = int(os.environ.get('MAIL_PORT')) if os.environ.get('MAIL_PORT')  else 85
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	ADMINS = ['email@gmail.com']
	
	#lazy loading and pagination
	POSTS_PER_PAGE = 1

	#options for translator API
	LANGUAGES = ['en', 'fr']
	MS_TRANSLATOR_KEY =  os.environ.get('MS_TRANSLATOR_KEY') or None
	
	#implementing search engine
	ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')