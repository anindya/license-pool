# Code adapted from John J. Rofrano's [nyu-devops/lab-flask-tdd]:
# https://github.com/nyu-devops/lab-flask-tdd

"""
Authorizing Service

# Paths:
# ------
# GET /pets - Returns a list all of the Pets
# GET /pets/{id} - Returns the Pet with a given id number
# POST /pets - creates a new Pet record in the database
# PUT /pets/{id} - updates a Pet record in the database
# DELETE /pets/{id} - deletes a Pet record in the database
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from .models import License, DataValidationError

# Import Flask application
from . import app

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)


@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST, error="Bad Request", message=str(error)
        ),
        status.HTTP_400_BAD_REQUEST,
    )


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_404_NOT_FOUND, error="Not Found", message=str(error)
        ),
        status.HTTP_404_NOT_FOUND,
    )


@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=str(error),
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            error="Unsupported media type",
            message=str(error),
        ),
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    )


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    app.logger.error(str(error))
    return (
        jsonify(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message=str(error),
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Authorizing Service",
            version="1.0",
            paths=url_for("list_licenses", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# LIST ALL License
######################################################################
@app.route("/licenses", methods=["GET"])
def list_licenses():
    """ Returns all of the Licenses """
    app.logger.info("Request for license list")
    licenses = []
    # category = request.args.get("category")
    # name = request.args.get("name")

    # if category:
    #     licenses = License.find_by_category(category)
    # elif name:
    #     licenses = License.find_by_name(name)
    # else:
    #     licenses = License.all()
    licenses = License.all()

    results = [license.serialize() for license in licenses]
    app.logger.info("Returning %d licenses", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE A License
######################################################################
@app.route("/licenses/<int:license_id>", methods=["GET"])
def get_licenses(license_id):
    """
    Retrieve a single License

    This endpoint will return a License based on it's id
    """
    app.logger.info("Request for license with id: %s", license_id)
    lic = License.find(license_id)
    if not lic:
        raise NotFound("License with id '{}' was not found.".format(license_id))

    app.logger.info("Returning lic: %s", lic.name)
    return make_response(jsonify(lic.serialize()), status.HTTP_200_OK)


######################################################################
# UPDATE AN EXISTING License
######################################################################
@app.route("/licenses/<int:license_id>", methods=["PUT"])
def update_licenses(license_id):
    """
    Update a License

    This endpoint will update a License based the body that is posted
    """
    app.logger.info("Request to update license with id: %s", license_id)
    check_content_type("application/json")
    lic = License.find(license_id)
    if not lic:
        raise NotFound("License with id '{}' was not found.".format(license_id))
    lic.deserialize(request.get_json())
    lic.id = license_id
    lic.update()

    app.logger.info("License with ID [%s] updated.", lic.id)
    return make_response(jsonify(lic.serialize()), status.HTTP_200_OK)


######################################################################
# ADD A NEW License
######################################################################
@app.route("/licenses", methods=["POST"])
def create_licenses():
    """
    Creates a License
    This endpoint will create a License based the data in the body that is posted
    """
    app.logger.info("Request to create a license")
    check_content_type("application/json")
    lic = License()
    lic.deserialize(request.get_json())

    lic.last_issued = None
    lic.used_by = None
    lic.is_available = True
    lic.create()

    message = lic.serialize()
    location_url = url_for("get_licenses", license_id=lic.id, _external=True)

    app.logger.info("License with ID [%s] created.", lic.id)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


# ######################################################################
# # DELETE A PET
# ######################################################################
# @app.route("/pets/<int:pet_id>", methods=["DELETE"])
# def delete_pets(pet_id):
#     """
#     Delete a Pet

#     This endpoint will delete a Pet based the id specified in the path
#     """
#     app.logger.info("Request to delete pet with id: %s", pet_id)
#     pet = Pet.find(pet_id)
#     if pet:
#         pet.delete()

#     app.logger.info("Pet with ID [%s] delete complete.", pet_id)
#     return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    License.init_db(app)


def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(415, "Content-Type must be {}".format(content_type))
