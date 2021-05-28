from pymongo import MongoClient
from os import environ, getenv
import hmac
import hashlib

required = ["MONGO_URL","PASSWORD","IMGUR_CLIENT","WEBHOOK_SECRET"]
for i in required:
    if i not in environ.keys():
        print("Missing env value " + i)
        exit()

MDURL = getenv("MONGO_URL")
PASSWORD = getenv("PASSWORD")
IMGUR_CLIENT = getenv("IMGUR_CLIENT")
WEBHOOK_SECRET = getenv("WEBHOOK_SECRET")

mongo_client = MongoClient(MDURL.format(PASSWORD), connectTimeoutMS=30000, socketTimeoutMS=None,
                           socketKeepAlive=True, connect=False, maxPoolsize=1)

def github_valid(signature, data):
    hash_algorithm, github_signature = signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(WEBHOOK_SECRET, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)
