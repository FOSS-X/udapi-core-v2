# 
#   entitySet.py
#   Start of entitySet.py
#
#   Created by FOSS-X UDAPI Desgin Team on 7/05/20.
#   Copyright © 2020 FOSS-X. All rights reserved.
#   



from flask import Flask, jsonify, request,Blueprint
mod = Blueprint('entitySetMongodb', __name__)
from bson.json_util import dumps, loads
from ..util import *
from ..util_mongodb import *


@mod.route('/databases/<databaseName>', methods=['GET'])
@token_required
def viewEntitySets(username,databaseName):
    storedDB=getDBName(username,databaseName)
    if not dbExists(databaseName, storedDB):
        raise notFound(f"Unknown database {databaseName}.")
    db = client[storedDB]
    # print(dumps(db.list_collection_names()))
    return jsonify(entitySets=db.list_collection_names(), success=1)


@mod.route('/databases/<databaseName>', methods=['POST'])
@token_required
def createEntitySet(username,databaseName):
    storedDB=getDBName(username,databaseName)

    db = client[storedDB]
    requestData = request.get_json()
    entitySet = requestData['entitySetName']
    if dbExists(databaseName, storedDB):
        if collectionExists(db, entitySet):
            raise duplicateResource(
                f"Entity Set '{entitySet}' already exists.")
        else:
            newES = db[entitySet]
            addToSchema(requestData,"mongodb")
            try:
                newES.insert_one({'test': 'data'})
                newES.delete_one({'test': 'data'})
                return jsonify({'code': 200, 'message': f"Entity Set '{entitySet}' created successfully", "success": 1})
            except:
                return jsonify({'code': 400, 'message': f"Attributes have to be incuded in the request", "success": 0})
    else:
        raise notFound(f"Unknown database {databaseName}.")


@mod.route('/databases/<databaseName>/<entitySetName>', methods=['PUT'])
@token_required
def updateEntitySetName(username,databaseName,entitySetName):
    storedDB=getDBName(username,databaseName)
    db = client[storedDB]
    eSet = db[entitySetName]
    if dbExists(databaseName, storedDB):
        if collectionExists(db, entitySetName):
            newDbName = request.json['newEntitySetName']
            eSet.rename(newDbName)
            return jsonify({'code': 200, 'message': f"Entity Set altered", "success": 1})
        else:
            raise notFound(f"Unknown entity set '{entitySetName}''")
    else:
        raise notFound(f"Unknown database {databaseName}.")


@mod.route('/databases/<databaseName>/<entitySetName>', methods=['DELETE'])
@token_required
def deleteEntitySet(username,databaseName, entitySetName):
    storedDB=getDBName(username,databaseName)
    db = client[storedDB]
    if dbExists(databaseName, storedDB):
        if collectionExists(db, entitySetName):
            db.drop_collection(entitySetName)
            return jsonify({'code': 200, 'message': f"Entity Set '{entitySetName}' deleted successfully", "success": 1})
        else:
            raise notFound(f"Unknown entity set '{entitySetName}''")
    else:
        raise notFound(f"Unknown database {databaseName}.")

@mod.route('/databases/<databaseName>/schema/<entitySetName>', methods=['GET'])
def getSchema(databaseName,entitySetName):
    client = pymongo.MongoClient()
    apiConfig = client['api-config']
    schemas=apiConfig['schemas']
    outputSchema=schemas.find_one({'entitySetName':entitySetName,'databaseType':'mongodb'},{'_id': False})
    return jsonify(outputSchema)