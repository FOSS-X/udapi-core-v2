# 
#   entity.py
#   Start of entity.py
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

from flask import Blueprint
mod = Blueprint('entityMysql', __name__)



@mod.route('/databases/<databaseName>/<entitySetName>', methods=['GET'])
@token_required
def get_mysql_entities(username, databaseName, entitySetName):
    """ View all the entites in the entitySetName  """
    password = get_password(username)
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user=username,
            passwd=password,
            database=username + "_" + databaseName
        )
        mycursor = cnx.cursor()
        sql = "SELECT * FROM " + entitySetName + ";"
        mycursor.execute(sql)
        entities = mycursor.fetchall()
        attributes = [desc[0] for desc in mycursor.description]
        fieldType = [FieldType.get_info(desc[1]) for desc in mycursor.description]  # Debug code
        results = []
        for entity in entities:
            results.append(dict(zip(attributes, entity)))
        cnx.close()
        # results = json.dumps(results, use_decimal=True)
        return jsonify(success=1, message=results)

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg)



@mod.route('/databases/<databaseName>/<entitySetName>', methods=['POST'])
@token_required
def create_mysql_entities(username, databaseName, entitySetName):
    """ Create new entity for the entitySetName """
    password = get_password(username)
    entity = request.json['entity']
    
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="password",
            database=username + "_" + databaseName
        )
        mycursor = cnx.cursor()
        sql = "INSERT INTO " + entitySetName + " VALUES ('" 
        print(entity.values())
        values = list(entity.values())
        sql += str(values[0])
        for i in range(1, len(values)):
            sql += "', '" + str(values[i])
        sql += "');"
        mycursor.execute(sql)
        cnx.commit()
        cnx.close()
        return jsonify(success=1, message="Inserted into " + entitySetName + " successfully.")

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg)

    
@mod.route('/databases/<databaseName>/<entitySetName>/<primeAttributeName>', methods=['PUT'])
@token_required
def edit_mysql_entities(username, databaseName, entitySetName, primeAttributeName):
    """ Edit the entity for the entitySetName  """
    password = get_password(username)
    primeAttributeValue = request.json['primeAttributeValue']
    attributeName = request.json['attributeName']
    attributeValue = request.json['attributeValue']
    
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="password",
            database=username + "_" + databaseName
        )
        mycursor = cnx.cursor()
        sql = "UPDATE " + entitySetName + " SET " + attributeName + "='" + attributeValue 
        sql += "' WHERE " + primeAttributeName + "='" + primeAttributeValue + "';"

        mycursor.execute(sql)
        cnx.commit()
        cnx.close()
        return jsonify(success=1, message="updated value of " + primeAttributeName + " ('" + primeAttributeValue + "').")

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg)



@mod.route('/databases/<databaseName>/<entitySetName>/<primeAttributeName>', methods=['DELETE'])
@token_required
def delete_mysql_entities(username, databaseName, entitySetName, primeAttributeName):
    """ Delete an entity for the entitySetName """
    primeAttributeValue = str(request.json['primeAttributeValue'])
    
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="password",
            database=username + "_" + databaseName
        )
        mycursor = cnx.cursor()
        sql = "DELETE FROM " + entitySetName + " WHERE " + primeAttributeName + "='" + primeAttributeValue + "';"

        mycursor.execute(sql)
        cnx.commit()
        cnx.close()
        return jsonify(success=1, message="Deleted entity having " + primeAttributeName + " ('" + primeAttributeValue + "').")

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg)