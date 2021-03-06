# 
#   login.py
#   Start of login.py
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
from ..util_mysql import *

import os
SECRET_KEY = str(os.environ.get("SECRET_KEY"))

from flask import Blueprint
mod = Blueprint('login', __name__)


@mod.route('/login', methods=['POST'])
def login():
    username = request.json['username'].lower()
    password = request.json['password']
    databaseName = 'udapiDB'

    # Find if user exists in the user table of udapi DB
    try:
        cnx = connectSQLServerDB('root', 'password', databaseName)
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
        return jsonify(success=0, error_code=err.errno, message=err.msg), 401

    # Username doesn't exists
    if not data:
        return jsonify(success=0, error_code=401, message="User doesn't exists.")

    if check_password_hash(data[0]['password'], password):
        token = jwt.encode({'username' : username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=500)}, SECRET_KEY)
        return jsonify(success=1, jwtToken=token.decode('UTF-8'))

    return jsonify(success=0, error_code=401, message="Invalid password."), 401