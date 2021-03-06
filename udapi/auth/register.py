# 
#   register.py
#   Start of register.py
#
#   Created by FOSS-X UDAPI Desgin Team on 7/05/20.
#   Copyright © 2020 FOSS-X. All rights reserved.
#   

from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import errorcode
from mysql.connector import FieldType
from werkzeug.security import generate_password_hash, check_password_hash
from ..util_mysql import *

from flask import Blueprint
mod = Blueprint('register', __name__)


@mod.route('/register', methods=['POST'])
def register():
    # Create udapi DB with user table for storing users information
    databaseName = 'udapiDB'
    try:
        cnx = connectSQLServerDB('root', 'password', databaseName)
    except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                cnx = connectSQLServer('root', 'password')
                mycursor = cnx.cursor()
                sql = "CREATE DATABASE " + databaseName
                mycursor.execute(sql)
                sql = """CREATE TABLE `udapiDB`.`users` (
                        `id` INT NOT NULL AUTO_INCREMENT,
                        `admin` INT NOT NULL DEFAULT 0,
                        `email` VARCHAR(45) NOT NULL,
                        `username` VARCHAR(45) NOT NULL,
                        `password` VARCHAR(256) NOT NULL,
                        PRIMARY KEY (`id`),
                        UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE,
                        UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE);
                    """
                mycursor.execute(sql)
                sql = """CREATE TABLE `udapiDB`.`configs` (
                        `username` VARCHAR(45) NOT NULL,
                        `databaseName` VARCHAR(45) NOT NULL,
                        `databaseType` VARCHAR(45) NOT NULL,
                        PRIMARY KEY (`username`, `databaseName`, `databaseType`));
                    """
                mycursor.execute(sql)
            else:
                cnx.close()
                return jsonify(ErrorCode=err.errno, ErrorDesc=err.msg), 401

    
    email = request.json['email']
    username = request.json['username'].lower()
    password = request.json['password'].strip()
    confirm_password = request.json['confirm_password'].strip()
    hashed_password = generate_password_hash(password, method='sha256')

    # Validate password to have atleast 1 letter
    if not password:
        return jsonify(success=0, error_code=7001, message="Password can't be empty"), 401

    # Check if passwords are equal
    if password != confirm_password:
        return jsonify(success=0, error_code=7002, message="Password and Confirm Password doesn't match"), 401

    # Inserting user data in the user table of udapi DB
    try:
        mycursor = cnx.cursor()
        sql = "INSERT INTO `udapiDB`.`users` (`email`, `username`, `password`) VALUES ('" + email + "', '" + username + "', '" + hashed_password +"');"
        mycursor.execute(sql)
        cnx.commit()
    except mysql.connector.Error as err:
        cnx.close()
        return jsonify(success=0, error_code=err.errno, message=err.msg), 401

    # Creating user for mysql connections with username and password
    try:
        sql = "DROP USER IF EXISTS '" + username + "'@'localhost';"
        mycursor.execute(sql)
        sql = "create user " + username + "@localhost identified by '" + hashed_password + "'"
        mycursor.execute(sql)
        sql = "grant all privileges on *.* to '" + username + "'@'localhost';"
        mycursor.execute(sql)
    except mysql.connector.Error as err:
        cnx.close()
        return jsonify(success=0, error_code=err.errno, message=err.msg), 401
    
    cnx.close()
    return jsonify(success=1, message= email + " successfully registered as " + username + "!")

