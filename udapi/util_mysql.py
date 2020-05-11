# 
#   util_mysql.py
#   Start of util_mysql.py
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

def connectSQLServer(username, password):
    cnx = mysql.connector.connect(
            host="localhost",
            user=username,
            passwd=password
        )
    return cnx

def connectSQLServerDB(username, password, databaseName):
    cnx = mysql.connector.connect(
            host="localhost",
            user=username,
            passwd=password,
            database=databaseName
        )
    return cnx

def get_entities(mycursor, sql):
    mycursor.execute(sql)
    entities = mycursor.fetchall()
    attributes = [desc[0] for desc in mycursor.description]
    fieldType = [FieldType.get_info(desc[1]) for desc in mycursor.description]  # Debug code
    result = []
    for entity in entities:
        result.append(dict(zip(attributes, entity)))
    return result
