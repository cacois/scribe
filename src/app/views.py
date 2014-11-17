from app import app
from flask.ext.pymongo import PyMongo
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash

mongo = PyMongo(app)

@app.route("/")
def hello():
    online_users = mongo.db.users.find({'online': True})
    return render_template('index.html',
        online_users=online_users)

@app.route("/activities/:user", methods=['GET'])
def user_activities():
    return "Not Yet Implemented"

@app.route("/activities", methods=['GET', 'POST'])
def activities():
    return render_template('activities.html')

@app.route("/reports", methods=['GET'])
def report():
    return "Not Yet Implemented"
