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


from flask import Blueprint
mod = Blueprint('user', __name__)

# Delete an entity for the entitySetName 
@mod.route('/user', methods=['DELETE'])
@token_required
@admin`
def delete_mysql_entities(username): 
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="password",
        )
        mycursor = cnx.cursor()

        sql = "DELETE FROM `udapiDB`.`configs` WHERE (`username` = '" + username + "');"
        mycursor.execute(sql)
        cnx.commit()

        sql = "DELETE FROM `udapiDB`.`users` WHERE (`username` = '" + username + "');"
        mycursor.execute(sql)
        cnx.commit()

        sql = "DROP USER IF EXISTS '" + username + "'@'localhost';"
        mycursor.execute(sql)

        cnx.close()
        return jsonify(success=1, message="Deleted user: " + username)

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg)


@mod.route('/secret_key', methods=['GET'])
def get_secret_key():
    SECRET_KEY = os.environ.get("SECRET_KEY")
    return SECRET_KEY