import secrets

from flask import Flask, g
from flask_debugtoolbar import DebugToolbarExtension

import mysql.connector

app = Flask(__name__, static_url_path='/static')
app.secret_key = secrets.token_urlsafe(16)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.debug = True

toolbar = DebugToolbarExtension(app)

@app.before_request
def before_request():
   g.db = mysql.connector.connect(
       user='root',
       password='',
       host='localhost',
       database='bd2',
   )

@app.after_request
def after_request(response):
    if g.db is not None:
        g.db.close()
    return response
