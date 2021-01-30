import pymongo
from pymongo import MongoClient


def test_connection():
    host = "localhost"
    port = 27017
    try:
        client = MongoClient(host, port, serverSelectionTimeoutMS=3000)
        client.stockticker.command("ping")
        return True
    except pymongo.errors.ServerSelectionTimeoutError:
        return False
