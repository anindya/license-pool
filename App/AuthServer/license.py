from flask import Flask, request, abort
from flask_apscheduler import APScheduler
from requests.adapters import HTTPAdapter

import os
import requests
import socket
import json
from datetime import datetime

from .utils import RSAHelper, StringUtils, constants

class License:
    #TODO Change print to logging.

    def __init__(self):
        self.public_key = None
        self.jobId = "ping Job"
        self.apsched = APScheduler()
        self.apsched.start()

    def initializePing(self):  
        s = requests.Session()
        s.mount(f"http://{constants.auth_server_url}", HTTPAdapter(max_retries=constants.MAX_RETRIES))  
        self.apsched.add_job(func=self.pingAuthServer, seconds=constants.PING_FREQUENCY_SECONDS, id=self.jobId, trigger='interval')

    def pingAuthServer(self):
        if self.public_key == None:
            self.apsched.remove_job(self.jobId)
        try:
            cid = socket.gethostname()
            secretMessage = {
                'container_id' : cid,
                'timestamp' : datetime.now(),
                'funny_secret' : StringUtils.getRandomString(23)
            }
            res = requests.post(f'http://{constants.auth_server_url}:{constants.auth_server_port}/container/ping',
                                json={'username': os.getenv("USER"),
                                    'password': os.getenv("USER_PASS"),
                                    'container_id': cid,
                                    'secret': RSAHelper.encryptMessage(secretMessage, self.public_key).decode()
                                })
            
            if res is None or res.status_code != 200:
                self.revoke()
            
            if res.json()["funny_secret"] != secretMessage["funny_secret"]:
                self.revoke()
        except requests.exceptions.RequestException as e:
            print(e)
            return "bad_request", 400

    def revoke(self):
        self.public_key = None
        print("License has been revoked on this server.")
        self.apsched.remove_job(self.jobId)
    def getLicense(self):
        try:
            cid = socket.gethostname()
            
            res = requests.post(f'http://{constants.auth_server_url}:{constants.auth_server_port}/license/request',
                                json={'username': os.getenv("USER"),
                                    'password': os.getenv("USER_PASS"),
                                    'container_id': cid})
            print(res.text)
            if res.status_code == 200:
                content = json.loads(res.text)
                self.public_key = content['public_key']  # todo: store it somewhere
                self.initializePing()
                return "ok", 200
            else:
                return "forbidden", 403
        except requests.exceptions.RequestException as e:
            print(e)
            return "bad_request", 400

    def giveupLicense(self):
        try:
            cid = socket.gethostname()
            
            res = requests.post(f'http://{constants.auth_server_url}:{constants.auth_server_port}/license/giveup',
                                json={'username': os.getenv("USER"),
                                    'password': os.getenv("USER_PASS"),
                                    'container_id': cid,
                                    'public_key' : self.public_key})
            print(res.text)
            if res.status_code == 200:
                self.revoke()
                return "ok", 200
            else:
                return "Internal Error", 500
        except requests.exceptions.RequestException as e:
            print(e)
            return "bad_request", 400

    def is_valid(self):
        return self.public_key != None