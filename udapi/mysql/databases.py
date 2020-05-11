# 
#   databases.py
#   Start of dataabases.py
#
#   Created by FOSS-X UDAPI Desgin Team on 7/05/20.
#   Copyright © 2020 FOSS-X. All rights reserved.
#   

from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import errorcode
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from ..util import *
from ..util_mysql import *

from flask import Blueprint
mod = Blueprint('databasesMysql', __name__)


@mod.route('/databases', methods=['GET'])
@token_required
def get_mysql_db(username):
    """ List all the databases of databaseType = mysql """
    databaseType = 'mysql'
    try:
        cnx = connectSQLServerDB('root', 'password', 'udapiDB')
        mycursor = cnx.cursor()
        sql = "SELECT * FROM udapiDB.configs WHERE (username='" + username + "') AND (databaseType='" + databaseType + "');"
        mycursor.execute(sql)
        entities = mycursor.fetchall()
        attributes = [desc[0] for desc in mycursor.description]
        results = []
        for entity in entities:
            results.append(entity[1])
        cnx.close()
        return jsonify(success=1, mysql=results)

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg)


# Create the Database if it doesn't exist
@mod.route('/databases', methods=['POST'])
@token_required
def create_mysql_db(username):
    databaseName = request.json['databaseName']
    password = get_password(username)

    try:
        cnx = connectSQLServerDB(username, password, username + "_" + databaseName)
        return jsonify(success=0, message="database Already Exists", error_code=401)

    except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                cnx = connectSQLServer(username, password)
                mycursor = cnx.cursor()
                sql = "CREATE DATABASE " + username + "_" + databaseName + ";"
                mycursor.execute(sql)
                cnx.commit()

                update_configs_add(username, databaseName, 'mysql')
                return jsonify(success=1, message="Database created successfully.")
            else:
                return jsonify(success=0, error_code=err.errno, message=err.msg)


@mod.route('/databases/<databaseName>', methods=["PUT"])
@token_required
def rename_mysql_db(username, databaseName):
    """ This Functionallity is not yet available. """
    return jsonify(success=0, message="Renaming the database name is not possible for MySql at the moment.")


@mod.route('/databases/<databaseName>', methods=['DELETE'])
@token_required
def delete_mysql_db(username, databaseName):
    password = get_password(username)
    try:
        cnx = connectSQLServer(username, password)
        mycursor = cnx.cursor()
        sql = "DROP DATABASE " + username + "_" + databaseName + ";"
        mycursor.execute(sql)
        cnx.close()
        update_configs_remove(username, databaseName)
        return jsonify(success=1, message="Database: " + databaseName + " deleted successfully.")

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg)
