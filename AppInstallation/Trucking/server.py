import os
import json
from utils import move_to_processed, PAR_DIR, OUTPUT_DIR,\
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
        response.status_code = 400
        response = jsonify({"response":"Not all the necessary arguments are passed. Please Check!"})

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

@app.route('/api/v1/keeptruckin', methods=['POST'])
def keep_truckin():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    response = check_credentials(username, password)
    if response:
        return response
    call(['scrapy crawl install_app -a username=%s -a password=%s' % (username, password)], shell=True)
    try:
        with open("{0}/{1}.json".format(PROCESSING_QUERY_FILES_PATH,self.user)) as items_file:
            data = items_file.read()
            items = json.loads(data)
            response.status_code = items.get('code','')
            message = items.get('response','')
            oauth = items.get('auth_code','')
            company_id = items.get('companyID','')
            if oauth == '':
                response = jsonify({"response":{"message":message}})
            else:
                response = jsonify({"response":{"message":message,"oauth":oauth,"companyID":company_id}})
            move()
    except:
        response.status_code = 404
        response = jsonify({"response":"Resource temporarily unavailable"})

    return response

@app.route('/api/v1/mygeotab', methods=['POST'])
def mygeotab():
    username = request.form.get('username', '')
    firstname = request.form.get('firstname', '')
    lastname = request.form.get('lastname', '')
    response = check_credentials(username, password)
    if not username or not lastname or not firstname:
        return response

    call(['scrapy crawl mygeotab_spider -a username=%s -a firstname=%s -a lastname=%s' % (username, firstname, lastname)], shell=True)
    file_pattern = os.path.join(PROCESSING_QUERY_FILES_PATH, 'mygeotab_spider_%s%s.json' % (firstname, lastname))
    try:
        with open(os.path.join(file_pattern, 'r')) as items_file:
            item = json.loads(items_file.read())
            response.status_code = item.get('code','')
            message = item.get('message','')
            reg_username = item.get('username','')
            reg_password = item.get('password', '')
            providercode = items.get('providercode','')
            if not reg_username or not reg_password or not providercode:
                response = jsonify({"response":{"message": message}})
            else:
                response = jsonify({"response":{"message": message, "username": username, "password": password, "providercode": providercode}})
        move()
    except:
        response.status_code = 404
        response = jsonify({"response":"Resource temporarily unavailable"})

    return response

@app.route('/api/v1/zonar', methods=['POST'])
def zonar():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    response = check_credentials(username, password)
    if response:
        return response
    call(['scrapy crawl install_app -a username=%s -a password=%s' % (username, password)], shell=True)
