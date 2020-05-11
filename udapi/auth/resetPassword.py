# 
#   resetPassword.py
#   Start of resetPassword.py
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


from flask import Blueprint
mod = Blueprint('resetPassword', __name__)


@mod.route('/resetpassword', methods=['POST'])
def reset_password():
    databaseName = 'udapiDB'
    email = request.json['email']
    new_password = request.json['new_password'].strip()
    confirm_password = request.json['confirm_password'].strip()
    hashed_password = generate_password_hash(new_password, method='sha256')

    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="password",
            database=databaseName
        )
        mycursor = cnx.cursor()
        sql = "SELECT * FROM udapiDB.users WHERE email='" + email + "';"
        mycursor.execute(sql)
        entities = mycursor.fetchall()
        attributes = [desc[0] for desc in mycursor.description]
        data = []
        for entity in entities:
            data.append(dict(zip(attributes, entity)))
    except mysql.connector.Error as err:
        return jsonify(ErrorCode=err.errno, ErrorDesc=err.msg), 401

    # Check if email exists in users table
    if not data:
        return jsonify(success=0, error_code=7000, message="Email not registerd."), 401

    # Validate password to have atleast 1 letter
    if not new_password:
        return jsonify(success=0, error_code=7001, message="Password can't be empty"), 401

    # Check if passwords are equal
    if new_password != confirm_password:
        return jsonify(success=0, error_code=7002, message="Password and Confirm Password doesn't match."), 401

    # Check if password is same as the previous password
    if check_password_hash(data[0]['password'], new_password):
        return jsonify(success=0, error_code=7003, message="Password can't be same as the previous one."), 401
    
    # Update the password in udapiDB.users and mysql users
    try:
        sql = "UPDATE users SET password='" + hashed_password + "' WHERE email='" + email + "';"
        mycursor.execute(sql)
        cnx.commit()
        sql = "ALTER USER '" + data[0]['username'] + "'@'localhost' IDENTIFIED BY '" + hashed_password + "';"
        mycursor.execute(sql)
        cnx.close()
        return jsonify(success=1, message="Password updated successfully.")

    except mysql.connector.Error as err:
        return jsonify(success=0, error_code=err.errno, message=err.msg), 401
