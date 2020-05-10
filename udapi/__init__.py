from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import errorcode
from mysql.connector import FieldType
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FOSS-X-udapi'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'jwtToken' in request.headers:
            token = request.headers['jwtToken']

        if not token:
            return jsonify(success=0, error_code=401, message="JWT Token is missing!")
        try:
            jwtData = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify(success=0, error_code=401, message="JWT Token is invalid.")

        try:
            cnx = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="password",
                database="udapiDB"
            )
            mycursor = cnx.cursor()
            sql = "SELECT * FROM udapiDB.users WHERE username='" + jwtData['username'] + "';"
            mycursor.execute(sql)
            entities = mycursor.fetchall()
            attributes = [desc[0] for desc in mycursor.description]
            data = []
            for entity in entities:
                data.append(dict(zip(attributes, entity)))
            cnx.close()
            
            if not data:
                return jsonify(success=0, error_code=401, message="JWT Token is invalid.")

        except mysql.connector.Error as err:
            return jsonify(success=0, error_code=err.errno, message=err.msg)

        return f(jwtData['username'], *args, **kwargs)

    return decorated

@app.route('/', methods=['GET', 'POST'])
@token_required
def index(username):
    return "hello World 2020"

@app.route('/register', methods=['POST'])
def register():
    # Create udapi DB with user table for storing users information
    databaseName = 'udapiDB'
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
                sql = """CREATE TABLE `udapiDB`.`users` (
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
        sql = "INSERT INTO `udapiDB`.`users` (`email`, `username`, `password`) VALUES ('" + email + "', '" + username + "', '" + hashed_password +"');"
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


@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    databaseName = 'udapiDB'

    # Find if user exists in the user table of udapi DB
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="password",
            database=databaseName
        )
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
        return jsonify(success=0, error_code=err.errno, message=err.msg)

    # Username doesn't exists
    if not data:
        return jsonify(success=0, error_code=401, message="User doesn't exists.")

    if check_password_hash(data[0]['password'], password):
        token = jwt.encode({'username' : username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=1)}, app.config['SECRET_KEY'])
        return jsonify({'jwtToken' : token.decode('UTF-8')})

    return jsonify(success=0, error_code=401, message="Invalid password.")
