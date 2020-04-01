import os
import json
from .utils import move_to_processed, PAR_DIR, OUTPUT_DIR,\
PROCESSING_QUERY_FILES_PATH, PROCESSED_QUERY_FILES_PATH
from flask import Flask, request, abort, jsonify
from flask_restful import Resource, Api
import logging
from subprocess import call,check_output

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
api = Api(app)

def check_credentials(username, password):
    response = ''
    if not username or not password:
        response = jsonify({"response": "Not all the necessary arguments are passed. Please Check!"})
        response.status_code = 400

    return response

def send_error():
    response = jsonify({"response": "Resource temporarily unavailable"})
    response.status_code = 500
    return response


@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  response.headers.add('Access-Control-Allow-Credentials', 'true')
  return response

@app.route('/')
def home():
    abort(404)

@app.route('/api/v1/install', methods=['POST'])
def keep_truckin():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    error_check = check_credentials(username, password)
    if error_check:
        return error_check

    call(['scrapy crawl install_app -a username=%s -a password=%s' % (username, password)], shell=True)
    file_pattern = os.path.join(PROCESSING_QUERY_FILES_PATH, '%s.json' % username)
    try:
        with open(file_pattern, 'r') as items_file:
            data = items_file.read()
            items = json.loads(data)
            message = items.get('response','')
            oauth = items.get('auth_code','')
            company_id = items.get('companyID','')
            if oauth == '':
                response = jsonify({"response": {"message":message}})
            else:
                response = jsonify({"response": {"message":message,"oauth":oauth,"companyID":company_id}})
            response.status_code = items.get('code','')
            move_to_processed(file_pattern)
    except:
        response = send_error()

    return response

@app.route('/api/v1/mygeotab', methods=['POST'])
def mygeotab():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    error_check = check_credentials(username, password)
    if error_check:
        return error_check

    call(['scrapy crawl mygeotab_spider -a username=%s -a password=%s' % (username, password)], shell=True)
    file_pattern = os.path.join(PROCESSING_QUERY_FILES_PATH, 'mygeotab_spider_%s.json' % (username))
    try:
        with open(file_pattern, 'r') as items_file:
            item = json.loads(items_file.read())
            message = item.get('message','')
            reg_username = item.get('username','')
            reg_password = item.get('password', '')
            providercode = item.get('providercode','')

            if not reg_username or not reg_password or not providercode:
                response = jsonify({"response": {"message": message}})
            else:
                response = jsonify({"response": {"message": message, "username": reg_username,
                                    "password": reg_password, "providercode": providercode}})

            response.status_code = item.get('code','')

        move_to_processed(file_pattern)

    except:
        response = send_error()

    return response

@app.route('/api/v1/zonar', methods=['POST'])
def zonar():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    response = check_credentials(username, password)
    if response:
        return response
    call(['scrapy crawl install_app -a username=%s -a password=%s' % (username, password)], shell=True)
