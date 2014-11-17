scribe
======

A user-friendly activity tracking and reporting application

## Getting Started

    vagrant up

This will initialize the vagrant box and start two docker containers comprising the application: one running mongodb, and one running the flask app.

## Contributing

If you add/change bower dependencies, go ahead and add them to bower.json and then re-run:

    bower install --allow-root

on your local source. It will put updated libraries into /src/app/static/bower_components, which you will then check into the repo.
