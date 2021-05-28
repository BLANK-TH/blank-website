from pymongo import MongoClient
from os import environ, getenv
from pathlib import Path
from dotenv import load_dotenv

try:
    load_dotenv(dotenv_path=Path(".") / ".env")
except:
    pass
required = ["MONGO_URL","PASSWORD","IMGUR_CLIENT"]
for i in required:
    if i not in environ.keys():
        print("Missing env value")
        exit()

MDURL = getenv("MONGO_URL")
PASSWORD = getenv("PASSWORD")
IMGUR_CLIENT = getenv("IMGUR_CLIENT")


mongo_client = MongoClient(MDURL.format(PASSWORD))
