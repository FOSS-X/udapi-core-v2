# 
#   entity.py
#   Start of entity.py
#
#   Created by FOSS-X UDAPI Desgin Team on 7/05/20.
#   Copyright © 2020 FOSS-X. All rights reserved.
#   

from flask import Flask, jsonify, request,Blueprint
from bson.json_util import dumps, loads
from ..util import *
from ..util_mongodb import *
from bson.objectid import ObjectId
mod = Blueprint('entityMongodb', __name__)

@mod.route('/databases/<databaseName>/<entitySetName>', methods=['GET'])
@token_required
def viewAllEntities(username, databaseName, entitySetName):
    storedDB=getDBName(username,databaseName)
    db = client[storedDB]
    if dbExists(databaseName, storedDB):
        if collectionExists(db, entitySetName):
            eSet = db[entitySetName]
            entities = eSet.find({},{'_id': False})
            results = []
            for entity in entities:
                results.append(entity)
            return dumps({"message": results, "success": 1})
        else:
            raise notFound(f"Unknown entity set '{entitySetName}''")
    else:
        raise notFound(f"Unknown database {databaseName}.")


@mod.route('/databases/<databaseName>/<entitySetName>', methods=['POST'])
@token_required
def createEntity(username, databaseName, entitySetName):
    
    storedDB=getDBName(username,databaseName)
    db = client[storedDB]
    if dbExists(databaseName, storedDB):
        if collectionExists(db, entitySetName):
            eSet = db[entitySetName]
            data = request.get_json()
            eSet.insert_one(data)
            return jsonify({'code': 200, 'message': f"Entity created successfully", "success": 1})
        else:
            raise notFound(f"Unknown entity set '{entitySetName}''")
    else:
        raise notFound(f"Unknown database {databaseName}.")


@mod.route('/databases/<databaseName>/<entitySetName>/<primaryKey>', methods=['PUT'])
@token_required
def updateEntityRecord(username, databaseName, entitySetName, primaryKey):
    storedDB=getDBName(username,databaseName)
    db = client[storedDB]
    if dbExists(databaseName, storedDB):
        if collectionExists(db, entitySetName):
            eSet = db[entitySetName]
            data = request.get_json()
            client = pymongo.MongoClient()
            apiConfig = client['api-config']
            schemas=apiConfig['schemas']
            primaryKey=schemas.find_one({'entitySetName':entitySetName},{'_id': False}).primary_key
            if eSet.find_one({primary_key : primaryKey}):
                eSet.find_one_and_update(
                    {primary_key : primaryKey}, {"$set": data})
                return jsonify({'code': 200, 'message': f"Entity updated successfully", "success": 1})
            else:
                raise notFound('Entity does not exist.')
        else:
            raise notFound(f"Unknown entity set '{entitySetName}''")
    else:
        raise notFound(f"Unknown database {databaseName}.")


@mod.route('/databases/<databaseName>/<entitySetName>/<primaryKey>', methods=['DELETE'])
@token_required
def deleteEntityRecord(username, databaseName, entitySetName, primaryKey):
    storedDB=getDBName(username,databaseName)
    db = client[storedDB]
    if dbExists(databaseName, storedDB):
        if collectionExists(db, entitySetName):
            primaryKey=schemas.find_one({'entitySetName':entitySetName},{'_id': False}).primary_key
            if eSet.find_one({primary_key : primaryKey}):
                eSet.find_one_and_update(
                    {primary_key : primaryKey}, {"$set": data})
                return jsonify({'code': 200, 'message': f"Entity deleted successfully", "success": 1})
            else:
                raise notFound('Entity does not exist.')
        else:
            raise notFound(f"Unknown entity set '{entitySetName}''")
    else:
        raise notFound(f"Unknown database {databaseName}.")


@mod.route('/databases/<databaseName>/<entitySetName>/<primaryKey>', methods=['GET'])
@token_required
def viewEntityRecord(username, databaseName, entitySetName, primaryKey):
    storedDB=getDBName(username,databaseName)
    db = client[storedDB]
    if dbExists(databaseName, storedDB):
        if collectionExists(db, entitySetName):
            eSet = db[entitySetName]
            result = eSet.find(
                {"_id": ObjectId(primaryKey)})
            if result != None:
                return dumps({"message": result, "success": 1})
            else:
                raise notFound('Entity does not exist.')
        else:
            raise notFound(f"Unknown entity set '{entitySetName}''")
    else:
        raise notFound(f"Unknown database {databaseName}.")

