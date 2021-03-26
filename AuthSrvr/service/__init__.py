# Code adapted from John J. Rofrano's [nyu-devops/lab-flask-tdd]:
# https://github.com/nyu-devops/lab-flask-tdd

"""
Package: app

Package for the application models and services
This module also sets up the logging to be used with gunicorn
"""

import os
import logging
from flask import Flask

# Create Flask application
app = Flask(__name__)
app.config.from_object("config")

# Import the routes After the Flask app is created
from service import routes, models

# Set up logging for production
print("Setting up logging for {}...".format(__name__))
app.logger.propagate = False
if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    if gunicorn_logger:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    app.logger.info("Logging established")

app.logger.info(70 * "*")
app.logger.info("  A U T H O R I Z I N G   S E R V E R   ".center(70, "*"))
app.logger.info(70 * "*")

# make our sqlalchemy tables
routes.init_db()

app.logger.info("Service initialized!")
