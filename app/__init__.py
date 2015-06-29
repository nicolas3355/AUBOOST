from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.mail import Mail

import os

app = Flask(__name__)
app.config.from_object('config')

try:
    assert os.environ['APP_PRODUCTION']
    app.config.from_object('config_prod')
except KeyError:
    pass

if not app.debug:
    import logging
    from logging.handlers import SysLogHandler
    stream_handler = SysLogHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)

if app.debug:
    toolbar = DebugToolbarExtension(app)

app.mail=Mail(app)
db = SQLAlchemy(app, use_native_unicode=True)

'''
#Create
from app.models import clients
db.drop_all()
db.create_all()
'''


from app.AUBOOST.views import mod as AUBOOSTModule
from app.AUBOOST.auth import mod as AUBOOSTAuthenticationModule

app.register_blueprint(AUBOOSTModule)
app.register_blueprint(AUBOOSTAuthenticationModule)


