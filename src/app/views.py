from app import app
from flask.ext.pymongo import PyMongo
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash, jsonify, json, make_response
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
        # get config from DB
        cursor = mongo.db.config.find({'active': True},{'_id': False})
        json_config = [doc for doc in cursor]
        config = json_config[0]

        app.logger.info('Returning config: ' + json.dumps(config))
        return jsonify(config)
    else:
        return "Unsupported request header: " + request.method

@app.route('/api/users', methods=['GET'])
def users_api():
    if request.method == 'GET':
        # get users from DB
        cursor = mongo.db.users.find({},{'_id': False})
        users = [doc['username'] for doc in cursor]
        users = [{'value': s} for s in users]
        return make_response(json.dumps(users))
    else:
        return "Unsupported request header: " + request.method

@app.route('/api/states', methods=['GET'])
def states_api():
    if request.method == 'GET':
        # get users from DB
        statesData = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
        'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii',
        'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
        'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
        'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
        'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota',
        'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
        'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
        'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
        ];
        statesData = [{'value': s} for s in statesData]
        return make_response(json.dumps(statesData))
    else:
        return "Unsupported request header: " + request.method

@app.route("/api/activities", methods=['GET', 'POST'])
def activities_api():
    app.logger.info('Received request for activities: ' + str(request))
    users = []
    tags = []
    categories = []

    data = request.json
    app.logger.info('received data: ' + str(data))

    if(data is not None):
        app.logger.info('here')
        categories = [s.encode('utf-8') for s in data['categories']] if 'categories' in data else []
        users = [s.encode('utf-8') for s in data['users']] if 'users' in data else []
        tags = [s.encode('utf-8') for s in data['tags']] if 'tags' in data else []
        start_date = arrow.get(data['start_date']).datetime if 'start_date' in data else None
        end_date = arrow.get(data['end_date']).datetime if 'end_date' in data else None

    # remove empty strings from arrays
    categories = filter(None, categories)
    tags = filter(None, tags)
    users = filter(None, users)

    app.logger.info('tags: ' + str(tags))
    app.logger.info('users: ' + str(users))
    app.logger.info('categories: ' + str(categories))
    app.logger.info('start_date: ' + str(start_date))
    app.logger.info('end_date: ' + str(end_date))

    user_filters = [{'users': user.encode('utf-8')} for user in users]
    tag_filters = [{'tags': tag.encode('utf-8')} for tag in tags]
    category_filters = [{'categories': category.encode('utf-8')} for category in categories]
    filters = user_filters + tag_filters + category_filters

    app.logger.info('filters: ' + str(filters))

    # build a mongo query
    if(len(filters) > 0):
        cursor = mongo.db.activities.find({'$and': filters, "date": {"$gte": start_date, "$lte": end_date}}, {'_id': False})
    else:
        cursor = mongo.db.activities.find({"date": {"$gte": start_date, "$lte": end_date}},{'_id': False})

    json_docs = [doc for doc in cursor]
    return jsonify({'activities': json_docs})

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
    return render_template('index.html')

@app.route("/activities", methods=['GET', 'POST'])
def activities():
    if request.method == 'POST':

        date = parse_date(request.form['hidden-tm-date'])
        data = {
            'tags': request.form['hidden-tm-tags'].split(','),
            'categories': request.form['hidden-tm-categories'].split(','),
            'users': request.form['hidden-tm-users'].split(','),
            'date': arrow.get(date).datetime if date else datetime.now(),
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


##################
#  Helper Methods
##################

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
