from service import models
from utils import constants

from Crypto.PublicKey import RSA
import random
import logging

def runMigrations():
    for user in constants.DEFAULT_USERS:
        userObj = models.User()
        userObj = userObj.deserialize(user)
        userObj.create()
        num_licenses = random.randint(1, constants.MAX_LICENSES)
        licensePermits = models.License_Permit()
        licensePermits.deserialize({
            "user_id" : userObj.id,
            "max_licenses" : num_licenses,
            "in_use" : 0
        })
        licensePermits.create()
        for i in range(num_licenses):
            key = RSA.generate(2048)
            publicKey = key.publickey()
            license = models.License();
            license.deserialize({
                "user_id" : userObj.id,
                "public_key" : publicKey.export_key('PEM'),
                "private_key" : key.export_key('PEM', passphrase=userObj.password),
                "in_use" : False,
                "container_id" : None,
                "last_used" : None
            })
            license.create()

            
