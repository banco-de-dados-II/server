"""
configuração de Flask, mysql, mongodb e suas variaveis globais
"""

import secrets

from flask import Flask, g
from flask_debugtoolbar import DebugToolbarExtension
from pymongo import MongoClient

import mysql.connector

import db_gen

app = Flask(__name__, static_url_path='/static')
app.secret_key = secrets.token_urlsafe(16)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.debug = True

toolbar = DebugToolbarExtension(app)

@app.before_request
def before_request():
   g.mongo = MongoClient('mongodb://root:root@localhost:27017')
   g.mdb = g.mongo.get_database('db2')

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

   if g.mongo is not None:
      g.mongo.close()

   return response
