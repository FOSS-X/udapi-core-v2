# 
#   util.py
#   Start of util.py
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
import pymongo

import os
SECRET_KEY = str(os.environ.get("SECRET_KEY"))

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'jwtToken' in request.headers:
            token = request.headers['jwtToken']

        if not token:
            return jsonify(success=0, error_code=401, message="JWT Token is missing!"), 401
        try:
            jwtData = jwt.decode(token, SECRET_KEY)
        except:
            return jsonify(success=0, error_code=401, message="JWT Token is invalid."), 401

        try:
            cnx = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="password",
                database="udapiDB"
            )
            mycursor = cnx.cursor()
            sql = "SELECT * FROM udapiDB.users WHERE username='" + jwtData['username'] + "';"
            mycursor.execute(sql)
            entities = mycursor.fetchall()
            attributes = [desc[0] for desc in mycursor.description]
            data = []
            for entity in entities:
                data.append(dict(zip(attributes, entity)))
            cnx.close()
            
            if not data:
                return jsonify(success=0, error_code=401, message="JWT Token is invalid."), 401

        except mysql.connector.Error as err:
            return jsonify(success=0, error_code=err.errno, message=err.msg)

        return f(jwtData['username'], *args, **kwargs)

    return decorated

def admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'jwtToken' in request.headers:
            token = request.headers['jwtToken']

        if not token:
            return jsonify(success=0, error_code=401, message="JWT Token is missing!")
        try:
            jwtData = jwt.decode(token, SECRET_KEY)
        except:
            return jsonify(success=0, error_code=401, message="JWT Token is invalid.")

        try:
            cnx = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="password",
                database="udapiDB"
            )
            mycursor = cnx.cursor()
            sql = "SELECT * FROM udapiDB.users WHERE username='" + jwtData['username'] + "';"
            mycursor.execute(sql)
            entities = mycursor.fetchall()
            attributes = [desc[0] for desc in mycursor.description]
            data = []
            for entity in entities:
                data.append(dict(zip(attributes, entity)))
            cnx.close()
            
            if not data:
                return jsonify(success=0, error_code=401, message="JWT Token is invalid.")

        except mysql.connector.Error as err:
            return jsonify(success=0, error_code=err.errno, message=err.msg)

        if not data[0]['admin']:
            return jsonify(success=0, error_code=401, message="You don't have permissions.")

        return f(jwtData['username'], *args, **kwargs)
    

    return decorated

# for debuging
# @app.route('/password', methods=['GET'])
# @token_required
def get_password(username):
    """ Function to return the password for the given username from user table of udapiDB """
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="password",
            database='udapiDB'
        )
        mycursor = cnx.cursor()
        sql = "SELECT * FROM udapiDB.users WHERE username='" + username + "';"
        mycursor.execute(sql)
        entities = mycursor.fetchall()
        attributes = [desc[0] for desc in mycursor.description]
        data = []
        for entity in entities:
            data.append(dict(zip(attributes, entity)))
        cnx.close()
    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg)

    return data[0]['password']


def update_configs_add(username, databaseName, databaseType):
    """ Update the configs table in udapiDB for each new database created by the user. """
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="password"
        )
        mycursor = cnx.cursor()
        sql = "INSERT INTO `udapiDB`.`configs` (`username`, `databaseName`, `databaseType`) "
        sql += "VALUES ('" + username + "', '" + databaseName + "', '" + databaseType +"');"
        mycursor.execute(sql)
        cnx.commit()
        cnx.close()
        return "Configs updated!"

    except mysql.connector.Error as err:
        cnx.close()
        return jsonify(success=0, error_code=err.errno, message=err.msg)


def update_configs_remove(username, databaseType, databaseName):
    """ Update the configs table in udapiDB for the deleted database by the user. """
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="password"
        )
        mycursor = cnx.cursor()
        sql = "DELETE FROM `udapiDB`.`configs` WHERE (`username` = '" + username + "') and (`databaseName` = '" + databaseName +"') and (`databaseType` = '" + databaseType +"');"
        mycursor.execute(sql)
        cnx.commit()
        cnx.close()
        return "Configs updated!"

    except mysql.connector.Error as err:
        cnx.close()
        return jsonify(success=0, error_code=err.errno, message=err.msg)

def addToSchema(requestData,databaseType):
    client = pymongo.MongoClient()
    apiConfig = client['api-config']
    schemas=apiConfig['schemas']
    collectionSchema={}
    collectionSchema["schema"]={}
    collectionSchema["entitySetName"]=requestData['entitySetName']
    collectionSchema["databaseType"]=databaseType
    for attribute in requestData["attributes"].keys():
        if(requestData['attributes'][attribute]["PK"]):
            collectionSchema["primary_key"]=attribute
        collectionSchema['schema'][attribute] = requestData['attributes'][attribute]['DataType']
    schemas.insert_one(collectionSchema)

def removeFromSchema(entitySetName,databaseType):
    client = pymongo.MongoClient()
    apiConfig = client['api-config']
    schemas=apiConfig['schemas']
    schemas.find_one_and_delete({"entitySetName":entitySetName,"databaseType":databaseType})

def updateSchema(entitySetName, newEntitySetName, databaseType):
    client = pymongo.MongoClient()
    apiConfig = client['api-config']
    schemas=apiConfig['schemas']
    schemas.find_one_and_update({"entitySetName":entitySetName,"databaseType":databaseType},{"$set": {"entitySetName":newEntitySetName}})