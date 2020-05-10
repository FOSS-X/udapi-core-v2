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
from functools import wraps
from ..util import *

from flask import Blueprint
mod = Blueprint('databasesMongodb', __name__)


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