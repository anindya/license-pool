from service import models
from utils import constants

from Crypto.PublicKey import RSA
import random
import logging

logger = logging.getLogger(__name__)

def getMigrations():
    for user in constants.DEFAULT_USERS:
        # print(user)
        # Create user
        # cls.logger.info(f"Adding user {user}")
        userObj = models.User()
        userObj = userObj.deserialize(user)
        userObj.create()
        # num_licenses = random.randint(1, constants.MAX_LICENSES)
        # for i in range(num_licenses):
        #     key = RSA.generate(2048)
        #     publicKey = key.publickey()
            
