from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import json
import base64

def encryptMessage(message, public_key):
    pkey = RSA.importKey(public_key)
    cipher = PKCS1_OAEP.new(pkey)
    return base64.b64encode(cipher.encrypt((json.dumps(message, default=str)).encode()))