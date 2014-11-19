from app import app
from flask.ext.pymongo import PyMongo
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash, jsonify

mongo = PyMongo(app)

@app.route('/_get_config')
def add_numbers():
    config = mongo.db.config.find_one({},{'_id': False})
    return jsonify(config)

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
    config = mongo.db.config.find({},{'categories': True})
    return render_template('activities.html',
        appconfig=config)

@app.route("/reports", methods=['GET'])
def report():
    return "Not Yet Implemented"
