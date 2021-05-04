from flask import Flask, request, abort
from flask_apscheduler import APScheduler
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import os
import requests
import socket
import json
from datetime import datetime

from .utils import RSAHelper, StringUtils, constants

auth_server_url = os.getenv("AUTH_SERVER_URL", "172.16.238.1")
auth_server_port = os.getenv("AUTH_SERVER_PORT", 5000)
user = os.getenv("USER")
user_pass = os.getenv("USER_PASS")

class License:
    #TODO Change print to logging.
    __instance = None
    @staticmethod
    def getInstance():
        if License.__instance == None:
            License()

    def __init__(self):
        if License.__instance != None:
            print("Object Already exists")
            return License.__instance
        else:
            self.auth_server_public_key = None
            self.jobId = "ping Job"
            self.apsched = APScheduler()
            self.apsched.start()
            self.session = requests.Session()
            self.session.mount(f"http://{auth_server_url}", HTTPAdapter(max_retries=Retry(total=constants.MAX_RETRIES)))  
            __instance = self
        # self.job = None

    def initializePing(self): 
        self.apsched.add_job(func=self.pingAuthServer, seconds=constants.PING_FREQUENCY_SECONDS, id=self.jobId, trigger='interval')

    def pingAuthServer(self):
        print("Trying ping")
        if self.auth_server_public_key == None:
            self.apsched.remove_job(self.jobId)
        try:
            cid = socket.gethostname()
            rolling_public_key, rolling_private_key = RSAHelper.generateKeyPairs(user_pass)
            secretMessage = {
                'container_id' : cid,
                'timestamp' : datetime.now(),
                'funny_secret' : StringUtils.getRandomString(23)
            }

            res = self.session.post(f'http://{auth_server_url}:{auth_server_port}/container/ping',
                                json={'username': user,
                                    'password': user_pass,
                                    'container_id': cid,
                                    'secret': RSAHelper.encryptMessage(secretMessage, self.auth_server_public_key).decode(),
                                    'public_key': rolling_public_key
                                })
            
            if res is None or res.status_code != 200:
                self.revoke()
            elif res.status_code == 204:
                self.revoke()
                # Clear any jobs currently running
                return
            print(res.status_code)
            secretReturnedByAuthServer = json.loads(RSAHelper.decryptBase64Message(user_pass, res.json()["funny_secret"], rolling_private_key))
            print("Ping Succesful")
            if secretReturnedByAuthServer["funny_secret"] != secretMessage["funny_secret"]:
                self.revoke()
        except Exception as e:
            print(e)
            self.revoke()
            self.session.close()
        # except requests.exceptions.Timeout as e:
        #     print(e)
        #     self.revoke()


    def revoke(self):
        self.auth_server_public_key = None
        print("License has been revoked on this server.")
        self.apsched.remove_job(self.jobId)

    def getLicense(self):
        try:
            cid = socket.gethostname()
            
            res = requests.post(f'http://{auth_server_url}:{auth_server_port}/license/request',
                                json={'username': user,
                                    'password': user_pass,
                                    'container_id': cid})
            print(res.text)
            if res.status_code == 200:
                content = json.loads(res.text)
                self.auth_server_public_key = content['public_key']  # todo: store it somewhere
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
            
            res = requests.post(f'http://{auth_server_url}:{auth_server_port}/license/giveup',
                                json={'username': user,
                                    'password': user_pass,
                                    'container_id': cid,
                                    'public_key' : self.auth_server_public_key}, timeout = 5)
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
        return self.auth_server_public_key != None
