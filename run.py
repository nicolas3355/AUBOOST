from app import app
from os import environ
port = int(environ.get('PORT', 5000))
app.run(host='127.0.0.1', port=port)
