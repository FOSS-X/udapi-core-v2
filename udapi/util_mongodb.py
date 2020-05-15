from bson.json_util import dumps, loads
import pymongo
from .util import *

client = pymongo.MongoClient()
apiConfig = client['api-config']


class mongoCustomException(Exception):
    def __init__(self):
        Exception.__init__(self)


class duplicateResource(mongoCustomException):
    def __init__(self, message):
        mongoCustomException.__init__(self)
        self.message = message
        self.code = 409
        self.success = 0

    def toJson(self):
        return dumps(self, default=lambda o: o.__dict__)


class notFound(mongoCustomException):
    def __init__(self, message):
        mongoCustomException.__init__(self)
        self.message = message
        self.code = 401
        self.success = 0

    def toJson(self):
        return dumps(self, default=lambda o: o.__dict__)

def getDBName(username, databaseName):
    return f"{username}-{databaseName}"

def dbExists(databaseName, storedDB):
    dblist = client.list_database_names()
    configDB = apiConfig['config']
    if storedDB not in dblist:
        if not configDB.find_one({"databaseName": storedDB}):
            return False
    return True

def collectionExists(db, collectionName):
    if collectionName in db.list_collection_names():
        return True
    return False


def addToConfig(username,databaseName,storedDB):
    configDB = apiConfig['config']
    configDB.insert_one({'username':username,'databaseName':storedDB})
    update_configs_add(username,databaseName,"mongodb")

def removeFromConfig(username,databaseName,storedDB):
    print(storedDB)
    configDB = apiConfig['config']
    configDB.find_one_and_delete({"databaseName":storedDB})
    update_configs_remove(username,"mongodb",databaseName)
