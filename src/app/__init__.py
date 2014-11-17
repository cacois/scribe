from flask import Flask
from flask.ext.pymongo import PyMongo
import os

app = Flask(__name__)
app.config['MONGO_HOST'] = os.getenv('MONGO_PORT_27017_TCP_ADDR')

from app import views
