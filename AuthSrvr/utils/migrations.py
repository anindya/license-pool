from service import models
from utils import constants, RSA_helper

import random
import logging

def runMigrations():
    for user in constants.DEFAULT_USERS:
        userObj = models.User()
        userObj = userObj.deserialize(user)
        userObj.create()
        # num_licenses = random.randint(1, constants.MAX_LICENSES)
        num_licenses = 5
        licensePermits = models.License_Permit()
        licensePermits.deserialize({
            "user_id" : userObj.id,
            "max_licenses" : num_licenses,
            "in_use" : 0
        })
        licensePermits.create()
        for _ in range(num_licenses):
            publicKey,  privateKey = RSA_helper.generateKeyPairs(userObj)
            license = models.License();
            license.deserialize({
                "user_id" : userObj.id,
                "public_key" : publicKey,
                "private_key" : privateKey,
                "in_use" : False,
                "container_id" : None,
                "last_used" : None
            })
            license.create()

            
