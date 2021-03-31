from flask import Flask, request, abort
import socket
import time
import json
import requests

hostIP = "0.0.0.0"
serverPort = 9090

app = Flask(__name__)

auth_server_url = '192.168.33.10'
auth_server_port = 5000


# app.debug = True

@app.route("/")
def hello():
    return "<h1>Hello, This is a Fibonacci Server</h1>"


@app.route("/fibonacci", methods=['GET'])
def fibonacci():
    try:
        print("Got a request: ", request.args.get("number"))
        n = int(request.args.get("number"))
        cid = socket.gethostname()
        uname = 'Emma'
        password = 'abcd'
        res = requests.post(f'http://{auth_server_url}:{auth_server_port}/license/request',
                            json={'username': uname,
                                  'password': password,
                                  'container_id': cid})
        if res.status_code == 200:
            content = json.loads(res.text)
            pub_key = content['public_key']  # todo: store it somewhere
        else:
            abort(403)
    except:
        abort(400)
    return str(fib(n)), 200


def fib(n):
    minusTwo = 0
    minusOne = 1
    for i in range(2, n + 1):
        answer = minusOne + minusTwo
        minusTwo = minusOne
        minusOne = answer
    return answer


if __name__ == "__main__":
    # TODO call server for getting license
    app.run(host=hostIP, port=serverPort)
