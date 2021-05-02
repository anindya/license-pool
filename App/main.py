from flask import abort
from app_pkg import app as app_lib

hostIP = "0.0.0.0"
serverPort = 9090

app = app_lib.app
licenseObj = app_lib.licenseObj

if __name__ == "__main__":
    _, status = licenseObj.getLicense()
    if status != 200:
        abort(status)
    
    app.run(host=hostIP, port=serverPort)

    _, status = licenseObj.giveupLicense()
    while status != 200:
        _, status = licenseObj.giveupLicense()
