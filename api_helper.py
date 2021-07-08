from os import environ, getenv
import hmac
import hashlib

required = ["SQL_USERNAME", "SQL_PASSWORD", "SQL_URI", "SQL_HOSTNAME", "IMGUR_CLIENT", "WEBHOOK_SECRET", "ADMIN_HASH"]
for i in required:
    if i not in environ.keys():
        print("Missing env value " + i)
        exit()

SQL_USERNAME, SQL_PASSWORD, SQL_URI, SQL_HOSTNAME = getenv("SQL_USERNAME"), getenv("SQL_PASSWORD"),\
                                                    getenv("SQL_URI"), getenv("SQL_HOSTNAME")
IMGUR_CLIENT = getenv("IMGUR_CLIENT")
WEBHOOK_SECRET = getenv("WEBHOOK_SECRET")
ADMIN_HASH = getenv("ADMIN_HASH")

def github_valid(signature, data):
    hash_algorithm, github_signature = signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(WEBHOOK_SECRET, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)
