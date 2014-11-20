from app import app
from flask.ext.pymongo import PyMongo
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash, jsonify, json

mongo = PyMongo(app)

@app.route('/_config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        app.logger.info('Data: ' + str(request))
        app.logger.info('Config posted: ' + json.dumps(request.json))
        # use $set to update the active config record without removing
        # existing non-updated values
        mongo.db.config.update({'active': True}, {
            "$addToSet": {'categories': request.json.categories},
            "$addToSet": {'users': request.json.users},
            "$addToSet": {'tags': request.json.tags}
            },upsert=True)
    elif request.method == 'GET':
        # get config form DB
        cursor = mongo.db.config.find({'active': True},{'_id': False})
        json_config = [doc for doc in cursor]
        config = json_config[0]

        app.logger.info('Returning config: ' + json.dumps(config))
        return jsonify(config)
    else:
        return "Unsupported request header: " + request.method

@app.route("/")
def index():
    online_users = mongo.db.users.find({'online': True})
    return render_template('index.html',
        online_users=online_users)

@app.route("/activities", methods=['GET', 'POST'])
def activities():
    if request.method == 'POST':
        app.logger.info('Received POST of activities: ' + request.json)
    elif request.method == 'GET':
        return render_template('activities.html')
    else:
        return "Unsupported request header: " + request.method

@app.route("/reports", methods=['GET'])
def report():
    return "Not Yet Implemented"
