from flask import Flask, request, abort

import os
import requests
import socket
import json

auth_server_url = "10.0.0.5"
auth_server_port = 5000

#TODO Change print to logging.
public_key = None

def get_license():
    try:
        cid = socket.gethostname()
        
        res = requests.post(f'http://{auth_server_url}:{auth_server_port}/license/request',
                            json={'username': os.getenv("USER"),
                                'password': os.getenv("USER_PASS"),
                                'container_id': cid})
        if res.status_code == 200:
            content = json.loads(res.text)
            public_key = content['public_key']  # todo: store it somewhere
            return "ok", 200
        else:
            return "forbidden", 403
    except requests.exceptions.RequestException as e:
        print(e)
        return "bad_request", 400

def is_valid():
    return public_key != None