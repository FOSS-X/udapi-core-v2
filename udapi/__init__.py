# 
#   __init__.py
#   Start of main __init__.py
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
from .util import *


app = Flask(__name__)
# app.config['SECRET_KEY'] = 'FOSS-X-udapi'
app.config.from_pyfile('config.py')

from udapi.auth.register import mod
from udapi.auth.login import mod
from udapi.auth.user import mod
app.register_blueprint(auth.register.mod, url_prefix='/')
app.register_blueprint(auth.login.mod, url_prefix='/')
app.register_blueprint(auth.user.mod, url_prefix='/')

from udapi.allDatabases.databases import mod
app.register_blueprint(allDatabases.databases.mod, url_prefix='/all')


from udapi.mysql.databases import mod
from udapi.mysql.entitySet import mod
from udapi.mysql.entity import mod
app.register_blueprint(mysql.databases.mod, url_prefix='/mysql')
app.register_blueprint(mysql.entitySet.mod, url_prefix='/mysql')
app.register_blueprint(mysql.entity.mod, url_prefix='/mysql')

from udapi.mongodb.databases import mod
from udapi.mongodb.entitySet import mod
from udapi.mongodb.entity import mod
app.register_blueprint(mongodb.databases.mod, url_prefix='/mongodb')
app.register_blueprint(mongodb.entitySet.mod, url_prefix='/mongodb')
app.register_blueprint(mongodb.entity.mod, url_prefix='/mongodb')

@app.route('/', methods=['GET', 'POST'])
def index():
    return "Welcome to UDAPI 2020!!"