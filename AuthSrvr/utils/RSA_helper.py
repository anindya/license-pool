from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

from service import models

def generateKeyPairs(userObj : models.User):
    key = RSA.generate(2048)
    return key.publickey().exportKey("OpenSSH").decode('utf-8'), key.export_key(pkcs=8, passphrase=userObj.password).decode('utf-8')

def decryptMessage(userObj : models.User, message, private_key):
    key = RSA.import_key(private_key, userObj.password)
    cipher = PKCS1_OAEP.new(key)
    return cipher.decrypt(message)