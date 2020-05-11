# 
#   user.py
#   Start of user.py
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
import os
import pymongo
from ..util_mongodb import *
from ..util_mysql import *

from flask import Blueprint
mod = Blueprint('user', __name__)


client = pymongo.MongoClient()
apiConfig = client['api-config']


@mod.route('/user', methods=['GET'])
@admin
def get_users(username):
    try:
        cnx = connectSQLServer('root', 'password')
        mycursor = cnx.cursor()
        sql = "SELECT admin, username, email FROM udapiDB.users;"
        users = get_entities(mycursor, sql)
        cnx.close()
        return jsonify(success=1, users=users)

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg), 401

        
# Delete an entity for the entitySetName 
@mod.route('/user/<username_toDelete>', methods=['DELETE'])
@admin
def delete_user(username, username_toDelete): 
    try:
        cnx = connectSQLServer('root', 'password')
        mycursor = cnx.cursor()

        # Check if user exists
        sql = "SELECT * FROM udapiDB.users WHERE (username='" + username_toDelete + "');"
        mycursor.execute(sql)
        users = mycursor.fetchall()
        if not users:
            return jsonify(success=0, error_code=401, message="User doesn't exists."), 401

        sql = "SELECT databaseName FROM udapiDB.configs WHERE (username='" + username_toDelete + "') AND (databaseType='mysql');"
        mycursor.execute(sql)
        sqlDatabaseNames = mycursor.fetchall()
        for databaseName in sqlDatabaseNames:
            sql = "DROP DATABASE IF EXISTS " + username_toDelete + "_" + databaseName[0] + ";"
            mycursor.execute(sql)

        # mongo DBs for the user
        sql = "SELECT databaseName FROM udapiDB.configs WHERE (username='" + username_toDelete + "') AND (databaseType='mongodb');"
        mycursor.execute(sql)
        mongoDatabaseNames = mycursor.fetchall()

        # Delete configs of the Databases in udapiDB.configs
        sql = "DELETE FROM `udapiDB`.`configs` WHERE (`username` = '" + username_toDelete + "');"
        mycursor.execute(sql)
        cnx.commit()

        # Delete the user form udapiDB.users Table
        sql = "DELETE FROM `udapiDB`.`users` WHERE (`username` = '" + username_toDelete + "');"
        mycursor.execute(sql)
        cnx.commit()

        # Delete the user from mysql users
        sql = "DROP USER IF EXISTS '" + username_toDelete + "'@'localhost';"
        mycursor.execute(sql)
        cnx.close()
    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg), 401

    # Mongo data base deletes
    for databaseName in mongoDatabaseNames:
        storedDB=getDBName(username_toDelete,databaseName[0])
        if not dbExists(databaseName[0], storedDB):
            raise notFound(f"Unknown database '{databaseName[0]}'.")
        removeFromConfig(username_toDelete,databaseName[0], storedDB)
        client.drop_database(storedDB)

    return jsonify(success=1, message="Deleted user: " + username_toDelete)


@mod.route('/secret_key', methods=['GET'])
@admin
def get_secret_key(admin):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    return admin