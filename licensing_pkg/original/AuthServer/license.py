from flask import Flask, request, abort
from flask_apscheduler import APScheduler
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import os
import requests
import socket
import json
import logging
from datetime import datetime

from .utils import RSAHelper, StringUtils, constants

auth_server_url = os.getenv("AUTH_SERVER_URL", "172.16.238.1")
auth_server_port = os.getenv("AUTH_SERVER_PORT", 5000)
user = os.getenv("USER")
user_pass = os.getenv("USER_PASS")
cid = socket.gethostname()

logging.basicConfig(format='[%(asctime)s] [%(levelname)s] : %(message)s')
logger = logging.getLogger('apscheduler')
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

class License:
    #TODO Change print to logging.
    __instance = None
    @staticmethod
    def getInstance():
        if License.__instance == None:
            License()
        return __instance

    def __init__(self):
        if License.__instance != None:
            logger.info("License Object Already exists")
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
        logger.info("Ping service initialized.")

    def pingAuthServer(self):
        logger.info("Trying ping...")
        if self.auth_server_public_key == None:
            self.apsched.remove_job(self.jobId)
        try:
            cid = socket.gethostname()
            rolling_public_key, rolling_private_key = RSAHelper.generateKeyPairs(user_pass)
            secretMessage = {
                'container_id' : cid,
                'timestamp' : datetime.now(),
                'funny_secret' : StringUtils.getRandomString(23),
                'username': user,
                'password': user_pass
            }
            credentials, _ = self.getCredentials()

            res = self.session.post(f'http://{auth_server_url}:{auth_server_port}/container/ping',
                                json={
                                    'val' : credentials,
                                    'secret': RSAHelper.encryptMessage(secretMessage, self.auth_server_public_key).decode(),
                                    'public_key': rolling_public_key
                                })            
            logger.debug('res.status_code={}'.format(res.status_code))

            if res is None or res.status_code != 200:
                self.revoke()
            elif res.status_code == 204:
                self.revoke()
                # Clear any jobs currently running
                return

            secretReturnedByAuthServer = json.loads(RSAHelper.decryptBase64Message(user_pass, res.json()["funny_secret"], rolling_private_key))
            logger.debug('secret returned by AuthServer = {}'.format(secretReturnedByAuthServer["funny_secret"]))
            logger.debug('secret = {}'.format(secretMessage["funny_secret"]))

            if secretReturnedByAuthServer["funny_secret"] != secretMessage["funny_secret"]:
                logger.info("Ping Failed: secret messages don't match.")
                self.revoke()
            else:
                logger.info("Ping Succeeded.")
        except Exception as e:
            logger.error(e)
            self.revoke()
            # self.session.close() #TODO Remove.
        # except requests.exceptions.Timeout as e:
        #     print(e)
        #     self.revoke()

    def revoke(self):
        self.auth_server_public_key = None
        logger.info("License has been revoked on this server.")
        self.apsched.remove_job(self.jobId)

    def getLicense(self):
        try:
            cid = socket.gethostname()
            rolling_public_key, rolling_private_key = RSAHelper.generateKeyPairs(user_pass)
            credentials, funny_secret = self.getCredentials()
            res = requests.post(f'http://{auth_server_url}:{auth_server_port}/license/request',
                                json={
                                    "val" : credentials,
                                    "public_key" : rolling_public_key
                                })
            # print(res.text)
            if res.status_code == 200:
                content = json.loads(res.text)
                secretReturnedByAuthServer = RSAHelper.decryptBase64Message(user_pass, res.json()["funny_secret"], rolling_private_key).strip('"\'')
                logger.debug('secretReturnedByAuthServer:{}'.format(secretReturnedByAuthServer))
                logger.debug('funny_secret:{}'.format(funny_secret))
                logger.debug('content:{}'.format(content))
                if funny_secret == secretReturnedByAuthServer:
                    self.auth_server_public_key = content['public_key']  # todo: store it somewhere
                    self.initializePing()
                    return "ok", 200
                else:
                    return "forbidden", 403
            else:
                return "forbidden", 403
        except requests.exceptions.RequestException as e:
            logger.info('get license failed.')
            logger.error(e)
            return "bad_request", 400

    def giveupLicense(self):
        try:
            credentials, funny_secret = self.getCredentials()
            res = requests.post(f"http://{auth_server_url}:{auth_server_port}/license/giveup",
                                json={"val" : credentials,
                                    "public_key" : self.auth_server_public_key
                                }, timeout = 5)
            logger.debug('res.json(): '.format(res.json()))
            if res.status_code == 200:
                logger.debug('res.text: '.format(res.text))
                self.revoke()
                return "ok", 200
            else:
                logger.error(res.status_code)
                return "Internal Error", 500
        except requests.exceptions.RequestException as e:
            logger.error(e)
            return "bad_request", 400
    
    def getCredentials(self):
        
        jsonVal = {
            'username': user,
            'password': user_pass,
            'container_id': cid,
            'funny_secret' : StringUtils.getRandomString(23)
        }
        return RSAHelper.encryptMessage(jsonVal, constants.SHARED_PUBLIC_KEY).decode(), jsonVal["funny_secret"]

    def is_valid(self):
        return self.auth_server_public_key != None
