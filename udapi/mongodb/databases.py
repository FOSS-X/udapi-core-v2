# 
#   databases.py
#   Start of dataabases.py
#
#   Created by FOSS-X UDAPI Desgin Team on 7/05/20.
#   Copyright © 2020 FOSS-X. All rights reserved.
#   

from flask import Flask, jsonify, request,Blueprint
from .mongoUtils import *
from ..util import *
import pymongo


mod = Blueprint('databasesMongodb', __name__)
client = pymongo.MongoClient()

@mod.route('/databases', methods=['GET'])
@token_required
def get_mysql_db(username):
    """ List all the databases of databaseType = mongodb """
    databaseType = 'mongodb'
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="password",
            database='udapiDB'
        )
        mycursor = cnx.cursor()
        sql = "SELECT * FROM udapiDB.configs WHERE (username='" + username + "') AND (databaseType='" + databaseType + "');"
        mycursor.execute(sql)
        entities = mycursor.fetchall()
        attributes = [desc[0] for desc in mycursor.description]
        fieldType = [FieldType.get_info(desc[1]) for desc in mycursor.description]  # Debug code
        results = []
        for entity in entities:
            results.append(entity[1])
        cnx.close()
        return jsonify(success=1, databases=results)

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg)

@mod.route('/databases/', methods=['POST'])
@token_required
def createDatabase(username):
    configData = request.get_json()
    databaseName = configData['databaseName']
    processedDBName = getDBName(username, databaseName)
    if dbExists(databaseName, processedDBName):
        raise duplicateResource(
            f"Database '{databaseName}' already exists.")
    print('creating Db', processedDBName)
    print(processedDBName)
    client[processedDBName]
    addToConfig(username,databaseName,processedDBName)
    return jsonify({'code': 200, 'message': f"Database '{databaseName}' created successfully", "success": 1})

@mod.route('/databases/<databaseName>', methods=['DELETE'])
@token_required
def deleteDB(username,databaseName):
    storedDB=getDBName(username,databaseName)
    if not dbExists(databaseName, storedDB):
        raise notFound(f"Unknown database '{databaseName}'.")
    removeFromConfig(username,databaseName, storedDB)
    client.drop_database(storedDB)
    return jsonify({'code': 200, 'message': f"Database {databaseName} deleted successfully", "success": 1})


