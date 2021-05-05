from flask import Flask, request, abort
from socket import *
import time
import logging

from AuthServer import license

hostIP = "0.0.0.0"
serverPort = 9090

app = Flask(__name__)
#app.debug = True
# config logger
logging.basicConfig()
app.logger.setLevel(logging.INFO)

licenseObj = license.License()

@app.route("/")
def hello():
    return "<h1>Hello, This is a Fibonacci Server</h1>"

@app.route("/fibonacci", methods = ['GET'])
def fibonacci():
    try:
        if not licenseObj.is_valid():
            # Try getting a new license
            _, status = licenseObj.getLicense()
            if status != 200:
                raise Exception(403)
        app.logger.info("Got a request: {}".format(request.args.get("number")))
        n = int(request.args.get("number"))
    except:
        return "Forbidden", 403
    return str(fib(n)), 200

@app.route("/revoke", methods = ['GET'])
def giveupLicense():
    try:
        if not licenseObj.is_valid():
            app.logger.info("Container has no valid license. exit.")
            abort(500)
        licenseObj.giveupLicense()
    except:
        return "Internal Server Error", 500
    return "License Revoked", 200

def fib(n):
    minusTwo = 0
    minusOne = 1
    for i in range(2, n + 1):
        answer = minusOne + minusTwo
        minusTwo = minusOne
        minusOne = answer
    return answer
    
if __name__ == "__main__":
    _, status = licenseObj.getLicense()
    if status != 200:
        abort(status)
    
    app.run(host=hostIP, port=serverPort)

    _, status = licenseObj.giveupLicense()
    # No need to force this, will be auto removed by server if pings are not received.
    # while status != 200:
    #     _, status = licenseObj.giveupLicense()
