import os
import json
from flask import Flask, request, abort, jsonify
from flask_restful import Resource, Api
import logging
from subprocess import call,check_output

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
api = Api(app)

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

PAR_DIR = os.path.abspath('.')
OUTPUT_DIR = os.path.join(PAR_DIR, 'spiders/OUTPUT')
PROCESSING_QUERY_FILES_PATH = os.path.join(OUTPUT_DIR, 'processing')
PROCESSED_QUERY_FILES_PATH = os.path.join(OUTPUT_DIR, 'processed')

class AddUser(Resource):
    
    def move(self):
        file_path = "{0}/{1}.json".format(PROCESSING_QUERY_FILES_PATH,self.user)
        cmd = "mv %s %s" %(file_path, PROCESSED_QUERY_FILES_PATH)
        try:
            os.system(cmd)
        except:
            pass

    def post(self):
        self.user        = request.form.get('username', None)
        self.password    = request.form.get('password', None)
        if not self.user or not self.password:
            response = jsonify({"response":"Not all the necessary arguments are passed. Please Check!"})
            response.status_code = 400
            return response
        call(['scrapy crawl install_app -a username=%s -a password=%s'%(self.user,self.password)],shell=True) 
        try:
            with open("{0}/{1}.json".format(PROCESSING_QUERY_FILES_PATH,self.user)) as items_file:
                data = items_file.read()
                items = json.loads(data)
                message = items.get('response','')
                status_code = items.get('code','')
                oauth = items.get('auth_code','')
                company_id = items.get('companyID','')
                if oauth=='':
                    response = jsonify({"response":{"message":message}})
                else:
                    response = jsonify({"response":{"message":message,"oauth":oauth,"companyID":company_id}})
                response.status_code = status_code
                self.move()
                return response
        except:
            response = jsonify({"response":"Resource temporarily unavailable"})
            response.status_code = 404
            return response
        
api.add_resource(AddUser, '/api/v1/install')
