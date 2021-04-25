from flask import Flask, request, abort
from socket import *
import time

from AuthServer import license

# initialize license obj
licenseObj = license.License()

# initialize app obj
app = Flask(__name__)
#app.debug = True

@app.route("/")
def hello():
    return "<h1>Hello, This is a Fibonacci Server</h1>"

@app.route("/fibonacci", methods = ['GET'])
def fibonacci():
    try:
        if not licenseObj.is_valid():
            _, status = licenseObj.getLicense()
            if status != 200:
                raise Exception(403)
        print("Got a request: ", request.args.get("number"))
        n = int(request.args.get("number"))
    except:
        return "Forbidden", 403
    return str(fib(n)), 200

@app.route("/revoke", methods = ['GET'])
def giveupLicense():
    try:
        if not licenseObj.is_valid():
            print("Container has no valid license. exit.")
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
