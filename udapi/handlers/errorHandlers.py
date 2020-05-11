# 
#   errorHanglers.py
#   Start of errorHanglers.py
#
#   Created by FOSS-X UDAPI Desgin Team on 7/05/20.
#   Copyright © 2020 FOSS-X. All rights reserved.
#

from flask import Blueprint,jsonify
import logging

mod = Blueprint('errorHanglers','__name__')

# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


@mod.app_errorhandler(404)
def handle_exceptions(e):
    print(f"{bcolors.FAIL}{e}{bcolors.ENDC}")
    return jsonify(success=0, error_code=404, message="Page Not Found."), 404

@mod.app_errorhandler(Exception)
def handle_unexpected_error(e):
    msg = "UnexpectedError: " + str(e)
    log.exception(f"{bcolors.FAIL}{msg}{bcolors.WARNING}")
    print(f"{bcolors.ENDC}")
    return jsonify(success=0, error_code=500, message="An unexpected error has occurred."), 500

