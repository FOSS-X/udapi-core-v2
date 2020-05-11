from flask import Blueprint,jsonify
from werkzeug.exceptions import HTTPException
from .mongoUtils import *

mod = Blueprint('error_handlers','__name__')

# @mod.app_errorhandler(HTTPException)
# def handle_exception(e):
#     response = e.get_response()
#     response.data = jsonify({
#         "error_code": e.code,
#         "description": e.description,
#         "success": 0
#     })
#     return response

@mod.app_errorhandler(mongoCustomException)
def handle_duplicate_resource(error):
    response = error.toJson()
    return response

