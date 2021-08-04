
"""#dotenv not working properly therfore defined variables explicitly and removed import from config.py file.#""" 

from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection
#import crawler.config as config

MONGODB_URI="mongodb://localhost:27017"
#MONGODB_URI = os.getenv('MONGODB_URI')
if MONGODB_URI is None:
    raise Exception('MONGODB_URI not set')

#MONGO_DBNAME = os.getenv('MONGO_DBNAME', 'haystack')
#MONGO_COLLNAME = os.getenv('MONGO_COLLNAME', 'crawl_info')
MONGO_DBNAME='new_haystack'
MONGO_COLLNAME='crawl_info'


def getMongoCollection():# -> Collection:
    client = MongoClient(host=MONGODB_URI)
    db = client[MONGO_DBNAME]
    collection = db[MONGO_COLLNAME]
    collections={
    "pdf": db["PDFs"],
    "text" : db["Documents"],
    "ppt" : db["PPTs"],
    "spreadsheet" : db["Spreadsheets"],
    "programs" : db["Programs"],
    }
    return [collection,collections]

def getMongoCollectionForFiles():
    client = MongoClient(host=MONGODB_URI)
    db = client[MONGO_DBNAME]
    collections={
    "pdf": db["PDFs"],
    "document" : db["Documents"],
    "ppt" : db["PPTs"],
    "spreadsheet" : db["Spreadsheets"],
    "program" : db["Programs"],
    }
    return collections

#ELASTIC_URI = os.getenv('ELASTIC_URI')
ELASTIC_URI ="localhost:9200"
if ELASTIC_URI is None:
    raise Exception('ELASTIC_URI not set')
#ELASTIC_INDEX_NAME = os.getenv('ELASTIC_INDEX_NAME', 'iitd_sites')
ELASTIC_INDEX_NAME = "iit"

mongo_collection=getMongoCollection()


