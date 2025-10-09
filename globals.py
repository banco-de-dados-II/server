from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost/bd2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Recommended to disable for performance


db = SQLAlchemy(app)

