from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client.stockticker
print(db.list_collection_names())

glob = db.globalsymbols
sym = "TSLA"
price= "400"
res = glob.find_one({'symbol': sym})
print(res['triggers'])