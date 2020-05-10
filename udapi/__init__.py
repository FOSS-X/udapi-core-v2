from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import errorcode
from mysql.connector import FieldType
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return "hello World 2020"

@app.route('/register', methods=['POST'])
def register():
    # Create udapi DB with user table for storing users information
    databaseName = 'udapi'
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="password",
            database=databaseName
        )
    except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                cnx = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    passwd="password",
                )
                mycursor = cnx.cursor()
                sql = "CREATE DATABASE " + databaseName
                mycursor.execute(sql)
                sql = """CREATE TABLE `udapi`.`users` (
                        `id` INT NOT NULL AUTO_INCREMENT,
                        `email` VARCHAR(45) NOT NULL,
                        `username` VARCHAR(45) NOT NULL,
                        `password` VARCHAR(256) NOT NULL,
                        PRIMARY KEY (`id`),
                        UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE,
                        UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE);
                    """
                mycursor.execute(sql)
            else:
                cnx.close()
                return jsonify(ErrorCode=err.errno, ErrorDesc=err.msg)

    # Inserting user data in the user table of udapi DB
    email = request.json['email']
    username = request.json['username']
    password = request.json['password']
    hashed_password = generate_password_hash(password, method='sha256')
    try:
        mycursor = cnx.cursor()
        sql = "INSERT INTO `udapi`.`users` (`email`, `username`, `password`) VALUES ('" + email + "', '" + username + "', '" + hashed_password +"');"
        mycursor.execute(sql)
        cnx.commit()
    except mysql.connector.Error as err:
        cnx.close()
        return jsonify(success=0, error_code=err.errno, message=err.msg)

        # Creating user for mysql connections with username and password
    try:
        sql = "DROP USER IF EXISTS '" + username + "'@'localhost';"
        mycursor.execute(sql)
        sql = "create user " + username + "@localhost identified by '" + hashed_password + "'"
        mycursor.execute(sql)

    except mysql.connector.Error as err:
        cnx.close()
        return jsonify(success=0, error_code=err.errno, message=err.msg)

    cnx.close()
    return jsonify(success=1, message= email + " successfully registered as " + username + "!")
