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
            "$addToSet": {
                'categories': {'$each': request.json['categories'] if 'categories' in request.json else []},
                'users': {'$each': request.json['users'] if 'users' in request.json else []},
                'tags': {'$each': request.json['tags'] if 'tags' in request.json else []}
            }
        }, upsert=True)

        return json.dumps({'status':'OK'});

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

        data = {
            'tags': request.form['hidden-tm-tags'].split(','),
            'categories': request.form['hidden-tm-categories'].split(','),
            'users': request.form['hidden-tm-users'].split(','),
            'date': parse_date(request.form['hidden-tm-date']),
            'message': request.form['activity']
        }
        # insert into db. using update in case we want to update tags/etc on an
        # existing post, or in case of client repost
        mongo.db.activities.update({'message': data['message'], 'date': data['date']}, data, upsert=True)
        return json.dumps({'status':'OK'});

    elif request.method == 'GET':
        return render_template('activities.html')
    else:
        return "Unsupported request header: " + request.method

@app.route("/reports", methods=['GET'])
def report():
    return "Not Yet Implemented"

def parse_date(date_str):
    '''parse_date()
    Attempt to parse a string into a datetime object, return None if failure
    '''
    date = None
    try:
        date = dateutil.parser.parse(date_str)
    except Exception:
        # couldn't parse automatically, try some other stuff
        app.logger.error("Unable to parse date %s" % date_str)

    return date
