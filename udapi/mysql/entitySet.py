# 
#   entitySet.py
#   Start of entitySet.py
#
#   Created by FOSS-X UDAPI Desgin Team on 7/05/20.
#   Copyright © 2020 FOSS-X. All rights reserved.
#   

from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import errorcode
from mysql.connector import FieldType
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from ..util import *
from ..util_mysql import *

from flask import Blueprint
mod = Blueprint('entitySetMysql', __name__)



@mod.route('/databases/<databaseName>', methods=['GET'])
@token_required
def get_mysql_entitySets(username, databaseName):
    """ View all the enity sets in the databaseName """
    password = get_password(username)
    try:
        cnx = connectSQLServerDB(username, password, username + "_" + databaseName)
        mycursor = cnx.cursor()
        sql = "USE " + username + "_" + databaseName + ";"
        mycursor.execute(sql)
        sql = "SHOW TABLES;"
        mycursor.execute(sql)
        tables = [table[0] for table in mycursor]

        cnx.close()
        return jsonify(success=1, entitySets=tables)

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg)



@mod.route('/databases/<databaseName>', methods=['POST'])
@token_required
def create_mysql_entitySet(username, databaseName):
    """ Create a new entity set in the databaseName """
    password = get_password(username)
    entitySetName = request.json['entitySetName']
    attributes = request.json['attributes']
    addToSchema(request.get_json(),"mysql")
    pks = []
    sql = "CREATE TABLE " + username + "_" + databaseName + "." + entitySetName + " ("
    for attribute in attributes:
        print(attribute, attributes[attribute])
        print(attributes[attribute]['DataType'])
        sql += " " + attribute + " " + attributes[attribute]['DataType']
        if attributes[attribute]['NN'] == 1:
            sql += " NOT NULL"
        if attributes[attribute]['AI'] == 1:
            sql += " AUTO_INCREMENT"
        if attributes[attribute]['PK'] == 1:
            pks.append(attribute)
        sql += ","
    sql += "PRIMARY KEY (" + pks[0]
    for i in range(1,len(pks)):
        sql += "," + pks[i] 
    sql += "));"

    try:
        cnx = connectSQLServerDB(username, password, username + "_" + databaseName)
        mycursor = cnx.cursor()
        mycursor.execute(sql)
        cnx.close()
        return jsonify(success=1, message="Entity Set '" + entitySetName + "' created successfully")

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg)



@mod.route('/databases/<databaseName>/<entitySetName>', methods=['PUT'])
@token_required
def rename_mysql_entitySet(username, databaseName, entitySetName):
    """ Edit Entity set Name """
    password = get_password(username)
    newEntitySetName = request.json["newEntitySetName"]

    try:
        cnx = connectSQLServerDB(username, password, username + "_" + databaseName)
        mycursor = cnx.cursor()
        sql = "ALTER TABLE " + entitySetName + " RENAME " + newEntitySetName + ";"
        mycursor.execute(sql)
        cnx.close()
        return jsonify(success=1, message="Table Name Altered")

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg)


@mod.route('/databases/<databaseName>/<entitySetName>', methods=['DELETE'])
@token_required
def delete_mysql_entitySetName(username, databaseName, entitySetName):
    """ Delete an Entity Set. """
    password = get_password(username)
    try:
        cnx = connectSQLServerDB(username, password, username + "_" + databaseName)
        mycursor = cnx.cursor()
        sql = "DROP TABLE " + entitySetName + ";"
        mycursor.execute(sql)
        cnx.close()
        return jsonify(success=1, message="Table " + entitySetName + " deleted.")

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg)

@mod.route('/databases/<databaseName>/schema/<entitySetName>', methods=['GET'])
def getSchema(databaseName, entitySetName):
    client = pymongo.MongoClient()
    apiConfig = client['api-config']
    schemas=apiConfig['schemas']
    outputSchema=schemas.find_one({'entitySetName':entitySetName,'databaseType':'mysql'},{'_id': False})
    return jsonify(outputSchema)