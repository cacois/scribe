#!flask/bin/python
from app import app

# load config
app.config.from_object('config.settings')

app.run(host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG'])
