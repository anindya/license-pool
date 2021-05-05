from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import json
import base64

def encryptMessage(message, public_key):
    pkey = RSA.importKey(public_key)
    cipher = PKCS1_OAEP.new(pkey)
    return base64.b64encode(cipher.encrypt((json.dumps(message, default=str)).encode()))

def generateKeyPairs(password):
    key = RSA.generate(2048)
    return key.publickey().exportKey("OpenSSH").decode('utf-8'), key.export_key(pkcs=8, passphrase=password).decode('utf-8')

def decryptMessage(password, message, private_key):
    key = RSA.import_key(private_key, passphrase=password)
    cipher = PKCS1_OAEP.new(key)
    return cipher.decrypt(message)

def decryptBase64Message(password, message, private_key):
    return decryptMessage(password, base64.b64decode(message.encode()), private_key).decode()