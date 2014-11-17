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

@app.route("/activities/:user")
def user_activities():
    return "Not Yet Implemented"

@app.route("/activities")
def activities():
    return "Not Yet Implemented"

@app.route("/report")
def report():
    return "Not Yet Implemented"
