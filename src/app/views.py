from app import app
from flask.ext.pymongo import PyMongo
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash, jsonify, json
import arrow
from datetime import datetime

mongo = PyMongo(app)

####################
#  REST API Routes
####################

@app.route('/api/config', methods=['GET', 'POST'])
def config_api():
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

@app.route("/api/activities", methods=['GET'])
def activities_api():
    users = []
    tags = []
    categories = []
    if(request.json):
        categories = request.json['categories'] if 'categories' in request.json else []
        users = request.json['users'] if 'users' in request.json else []
        tags = request.json['tags'] if 'tags' in request.json else []
        start_date = request.json['start_date']
        end_date = request.json['end_date']

    user_filters = [[{'users': user}] for user in users]
    tag_filters = [[{'tags': tag}] for tag in tags]
    category_filters = [[{'categories': category}] for category in categories]
    filters = user_filters + tag_filters + category_filters

    # build a mongo query
    if(len(filters) > 0):
        cursor = mongo.db.activities.find({'$or': filters}, {'_id': False})
    else:
        cursor = mongo.db.activities.find({},{'_id': False})

    json = [doc for doc in cursor]
    return jsonify({'activities': json})

@app.route("/api/activities/<ObjectId:activity_id>", methods=['GET'])
def activities_api_id(activity_id):
    cursor = mongo.db.activities.find_one_or_404(activity_id)
    json = [doc for doc in cursor]
    return jsonify(json[0])


################
#  View Routes
################

@app.route("/")
def index():
    online_users = mongo.db.users.find({'online': True})
    return render_template('index.html',
        online_users=online_users)

@app.route("/activities", methods=['GET', 'POST'])
def activities():
    if request.method == 'POST':

        date = parse_date(request.form['hidden-tm-date'])
        data = {
            'tags': request.form['hidden-tm-tags'].split(','),
            'categories': request.form['hidden-tm-categories'].split(','),
            'users': request.form['hidden-tm-users'].split(','),
            'date': date if date else datetime.now(),
            'message': request.form['activity']
        }
        # insert into db. using update in case we want to update tags/etc on an
        # existing post, or in case of client repost
        mongo.db.activities.update({
            'message': data['message'], 'date': data['date']},
            data,
            upsert=True)

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
