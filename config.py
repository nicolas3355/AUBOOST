import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

SECRET_KEY = 'DPaNtV3fytAGtFhY9pH0AlTbGOXk1Aeqh'

#SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_DATABASE_URI = 'sqlite://///home/nicolas/project.db'
DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 8

CSRF_ENABLED=True
CSRF_SESSION_KEY="DPaNtV3fytAGtFhY9pH0AlTbGOXk1AeqhDPaNtV3fytAGtFhY9pH0AlTbGOXk1Aeqh"

DEBUG_TB_INTERCEPT_REDIRECTS= False




ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'nicolaselhaddad.nh@gmail.com')


STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_VIxXIrN650t8JpewRCsZ1CWV')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_8syeQsnsAF7ksOALEzrbeoml')
STRIPE_MONTHLY_PAYMENT = 50
STRIPE_PLAN_ID = 2
STRIP_TRIAL_PERIOD = 30 # Number of days




URL_PREFIX = 'http://localhost:5000'

MAIL_DEFAULT_SENDER='AUBOOST.team@gmail.com'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'AUBOOST.team@gmail.com'
MAIL_PASSWORD = 'nicolaspassword'