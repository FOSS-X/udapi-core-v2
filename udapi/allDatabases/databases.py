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
from ..util import *
from ..util_mysql import *
import pymongo

from flask import Blueprint
mod = Blueprint('databasesAll', __name__)


@mod.route('/databases', methods=['GET'])
@token_required
def get_mysql_db(username):
    """ List all the databases of all the databaseType """
    try:
        cnx = connectSQLServerDB('root', 'password', 'udapiDB')
        mycursor = cnx.cursor()
        sql = "SELECT databaseName, databaseType FROM udapiDB.configs WHERE (username='" + username + "');"
        mycursor.execute(sql)
        entities = mycursor.fetchall()
        attributes = [desc[0] for desc in mycursor.description]
        dbs_mysql = []
        dbs_mongodb = []
        for entity in entities:
            if entity[1] == 'mysql':
                dbs_mysql.append(entity[0])
            if entity[1] == 'mongodb':
                dbs_mongodb.append(entity[0])
        cnx.close()
        return jsonify(success=1, mongodb=dbs_mongodb, mysql=dbs_mysql)

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg)


    