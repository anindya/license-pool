# Code adapted from John J. Rofrano's [nyu-devops/lab-flask-tdd]:
# https://github.com/nyu-devops/lab-flask-tdd

"""
Authorizing Service
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# We use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from .models import User, License_Permit, License, DataValidationError
from utils import migrations, RSA_helper, constants
# Import Flask application
from . import app
import json

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

######################################################################
# ASSIGN a License
######################################################################
#TODO Use authentication function for getting user and remove redundant code.
@app.route("/license/request", methods=['POST'])
def assign_license():
    app.logger.info('Received a licence request')
    check_content_type("application/json")
    req = json.loads(RSA_helper.decryptBase64MessageWithPassphrase(constants.PRIVATE_KEY_PASSPHRASE, request.get_json()["val"], constants.PRIVATE_KEY))
    app.logger.info(req)
    authenticationStatus = authenticate(req)
    if authenticationStatus["status"] != 200:
        response = {"message" :authenticationStatus["message"]}
        return make_response(jsonify(response), authenticationStatus["status"])
    user = authenticationStatus["user"]
    
    permit = License_Permit.find_by_uid(user.id)
    if permit is None:
        response = {'message': 'permit not found'}
        return make_response(jsonify(response), status.HTTP_403_FORBIDDEN)
    app.logger.info(f'found permit {permit}')
    if permit.in_use < permit.max_licenses:
        # search for a license not in use
        lic = License.find_free_by_uid(user.id)
        app.logger.info(f'Investigating license {lic}')
        if not lic.in_use:
            lic.in_use = True
            lic.container_id = req['container_id']
            lic.update()
            permit.in_use += 1
            permit.update()
            # success, respond to user
            response = {
                'status': 200,
                'public_key': lic.public_key,
                'message': "OK",
                'funny_secret' : RSA_helper.encryptMessage(req["funny_secret"], request.get_json()["public_key"]).decode()
            }
            return make_response(jsonify(response), status.HTTP_200_OK)
    else:
        response = {'message': 'Max Limit Reached. Please revoke licence before proceeding.'}
        return make_response(jsonify(response), status.HTTP_403_FORBIDDEN)


######################################################################
# Handle container ping
######################################################################
@app.route("/container/ping", methods=["POST"])
def handle_ping():
    """
    Takes a ping from a container, finds corresponding user and deciphers the secret messages.
    Returns funny_message and timestamp from ping.
    """
    app.logger.info('Received a ping')
    check_content_type("application/json")
    req = json.loads(RSA_helper.decryptBase64MessageWithPassphrase(constants.PRIVATE_KEY_PASSPHRASE, request.get_json()["val"], constants.PRIVATE_KEY))
    # req = request.get_json()
    app.logger.info(req)
    authenticationStatus = authenticate(req)
    if authenticationStatus["status"] != 200:
        response = {"message" :authenticationStatus["message"]}
        return make_response(jsonify(response), authenticationStatus["status"])
    user = authenticationStatus["user"]

    licenseData = License.find_by_uid_container_id(user.id, req["container_id"])
    
    if licenseData is None:
        app.logger.info(f"Could not find license for user : {user.id} and container id : {req['container_id']}")
        response = {"message" : "License not found for container."}
        return make_response(jsonify(response), status.HTTP_404_NOT_FOUND)
    app.logger.info(f"Ping received for User : {user.id}, license id : {licenseData}")

    secretDecrypted = json.loads(RSA_helper.decryptBase64Message(user, request.get_json()["secret"], licenseData.private_key))
    app.logger.debug(secretDecrypted)
    if licenseData.last_used < datetime.strptime(secretDecrypted["timestamp"], '%Y-%m-%d %H:%M:%S.%f'):
        licenseData.last_used = datetime.now()
        licenseData.update()
        secretForContainer = RSA_helper.encryptMessage(secretDecrypted, request.get_json()["public_key"])
        response = {"message" : "Verified", "funny_secret" : secretForContainer.decode()}
        return make_response(jsonify(response), status.HTTP_200_OK)
    # elif licenseData.last_used + THRESHOLD < secretDecrypted["timestamp"]:
        # revokeLicense(licenseData)
        # response = {"message" : "Revoked", "funny_secret" : secretForContainer.decode()}
        # return make_response(jsonify(response), status.HTTP_204_NO_CONTENT)
    else :
        secretForContainer = RSA_helper.encryptMessage(secretDecrypted, request.get_json()["public_key"])
        response = {"message" : "Verified", "funny_secret" : secretForContainer.decode()}
        return make_response(jsonify(response), status.HTTP_200_OK)

    

######################################################################
# Revoke a license
######################################################################
@app.route("/license/giveup", methods=["POST"])
def giveup_license():
    """
    Revoke a license that is sent by the request.
    """
    app.logger.info('Received a revoke license request')
    check_content_type("application/json")
    # req = request.get_json()
    req = json.loads(RSA_helper.decryptBase64MessageWithPassphrase(constants.PRIVATE_KEY_PASSPHRASE, request.get_json()["val"], constants.PRIVATE_KEY))
    app.logger.info(req)
    authenticationStatus = authenticate(req)
    if authenticationStatus["status"] != 200:
        response = {"message" :authenticationStatus["message"]}
        return make_response(jsonify(response), authenticationStatus["status"])
    user = authenticationStatus["user"]

    licenseData = License.find_by_uid_container_id(user.id, req["container_id"])
    
    if licenseData is None:
        app.logger.info(f"Could not find license for user : {user.id} and container id : {req['container_id']}")
        response = {"message" : "License not found for container."}
        return make_response(jsonify(response), status.HTTP_404_NOT_FOUND)

# TODO Make this a transaction.
    revokeLicense(licenseData, request.get_json()["public_key"], user)    
    app.logger.info("LICENSE Revoked")
    response = {"message" : "Revoked"}
    app.logger.info(make_response(jsonify(response), status.HTTP_200_OK))
    return make_response(jsonify(response), status.HTTP_200_OK)

def revokeLicense(licenseData : License, public_key, user : User):
    if licenseData.public_key == public_key and licenseData.user_id == user.id:
        licenseData.in_use = False
        permit = License_Permit.find_by_uid(user.id)
        permit.in_use -= 1
        licenseData.update()
        permit.update() 
        
######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def authenticate(req):
    user = User.find_by_uname(req['username'])
    if user is None:
        return {'message': 'user not found', 'status' : status.HTTP_404_NOT_FOUND}    
    app.logger.info(f'User with uname {req["username"]} found')
    app.logger.info(f'User id: {user.id}')
    if user.password != req['password']:
        return {'message': 'incorrect passoword', 'status' : status.HTTP_403_FORBIDDEN}
    return {'message': 'user authenticated', 'user' : user, 'status' : status.HTTP_200_OK}

def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    License.init_db(app)
    migrations.runMigrations()


def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(415, "Content-Type must be {}".format(content_type))
