scribe
======

A user-friendly activity tracking and reporting application

## Getting Started

    vagrant up

This will initialize the vagrant box and start two docker containers comprising the application: one running mongodb, and one running the flask app.

The configuration of Scribe is stored in MongoDB, in a collections called 'config'. You can insert a default configuration by running the following command in MongoDB:

    db.config.insert{"statTags" : [ { "text" : "deliverable", "label" : "Deliverables" }, { "text" : "blog", "label" : "Blog Posts" }, { "text" : "publication", "label" : "Publications" } ], "categories" : [ "blog", "publication", "presentation", "deliverable" ], "active" : true }

## Contributing

If you add/change bower dependencies, go ahead and add them to bower.json and then re-run:

    bower install --allow-root

on your local source. It will put updated libraries into /src/app/static/bower_components, which you will then check into the repo.
