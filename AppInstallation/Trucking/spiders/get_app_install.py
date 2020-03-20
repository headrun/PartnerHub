import scrapy
import re
import json
from urllib.parse import urlencode,unquote
#from urllib import urlencode
import urllib
import os
import datetime
import requests
import glob
import logging
import logging.handlers
loggers = {}

PAR_DIR = os.path.abspath('.')
OUTPUT_DIR = os.path.join(PAR_DIR, 'spiders/OUTPUT')
PROCESSING_QUERY_FILES_PATH = os.path.join(OUTPUT_DIR, 'processing')
PROCESSED_QUERY_FILES_PATH = os.path.join(OUTPUT_DIR, 'processed')

def myLogger(name):
    log_path = os.path.abspath('logs/')
    try:
        os.mkdir(log_path)
    except:
        pass

    global loggers
    path = 'logs/get_install_app_%s.log'

    if loggers.get(name):
        return loggers.get(name)
    else:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        now = datetime.datetime.now()
        handler = logging.FileHandler(path %(datetime.datetime.now().date()))
        formatter = logging.Formatter('%(asctime)s - %(filename)s - %(lineno)d - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        loggers.update(dict(name=logger))
        return logger

process_logger = myLogger('process')

class GetAppInstall(scrapy.Spider):
    name = "install_app"
    custom_settings = {'COOKIES_ENABLED':True,'ROBOTSTXT_OBEY':False}

    def __init__(self, *args, **kwargs):
        self.username = kwargs.get('username','')
        self.password = kwargs.get('password','')
        self.company_id = ''
        try:
            os.mkdir(OUTPUT_DIR)
        except:
            pass
        try:
            os.mkdir(PROCESSING_QUERY_FILES_PATH)
        except:
            pass
        try:
            os.mkdir(PROCESSED_QUERY_FILES_PATH)
        except:
            pass

    def init_logger(filename, level=''):
       if not os.path.isdir(LOGS_DIR):
            os.mkdir(LOGS_DIR)

       file_name = os.path.join(LOGS_DIR, filename)
       log = logging.getLogger(file_name)
       handler = logging.handlers.RotatingFileHandler(file_name, maxBytes=524288000, backupCount=5)
       formatter = logging.Formatter('%(asctime)s.%(msecs)d: %(filename)s: %(lineno)d: %(funcName)s: %(levelname)s: %(message)s', "%Y%m%dT%H%M%S")
       handler.setFormatter(formatter)
       log.addHandler(handler)
       log.setLevel(logging.DEBUG)

       return log

    def start_requests(self):
        headers = {
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/66.0.3359.181 Chrome/66.0.3359.181 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }
        params = (
                ('return_url', 'https://keeptruckin.com/oauth/authorize?client_id=baac4693bc4ff187c4906ae3fdcec3e8577df741a584d372aafb467922f49172&redirect_uri=https://carrier-data-api-prod.fourkites.com/api/v1/keepTrukin/oauth&response_type=code&scope=locations.vehicle_locations_list+companies.read'),
        )
        yield scrapy.FormRequest('https://keeptruckin.com/log-in', headers=headers, callback = self.login_page)

    def login_page(self,response):
        token = response.xpath('//meta[@name="csrf-token"]/@content').extract_first()
        if token:
            headers = {
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'Origin': 'https://keeptruckin.com',
                'Upgrade-Insecure-Requests': '1',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
                'Sec-Fetch-User': '?1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'navigate',
                'Referer': 'https://keeptruckin.com/log-in',
            }
            data = {
              'utf8': '\u2713',
              'authenticity_token': token,
              'user[email]': self.username,
              'user[password]': self.password,
              'return_url': 'https://keeptruckin.com/oauth/authorize?client_id=baac4693bc4ff187c4906ae3fdcec3e8577df741a584d372aafb467922f49172&redirect_uri=https://carrier-data-api-prod.fourkites.com/api/v1/keepTrukin/oauth&response_type=code&scope=locations.vehicle_locations_list+companies.read',
              'ref': 'sign-up'
            }
            authenticity_token = response.xpath('//input[@name="authenticity_token"]/@value').extract_first() or ''
            response.meta.update({'authenticity_token':authenticity_token})
            yield scrapy.FormRequest('https://keeptruckin.com/log-in?ref=sign-up',formdata=data,callback=self.parse_next, headers=headers,meta=response.meta)
            data.update({'return_url':''})
            yield scrapy.FormRequest('https://keeptruckin.com/log-in?ref=sign-up',formdata=data,callback=self.parse_company_next, headers=headers,meta=response.meta)

    def parse_company_next(self,response):
        data = response.request.headers.get('Cookie',[])
        try:
            web_auth_user = re.findall(r'auth_token=(.*)',data.decode('utf-8'))[0] 
            web_auth_user = unquote(web_auth_user)
        except: web_auth_user  = ''
        headers = {
			'Connection': 'keep-alive',
			'Accept': '*/*',
			'Origin': 'https://web.keeptruckin.com',
			'Sec-Fetch-Dest': 'empty',
			'X-Web-User-Auth': web_auth_user,
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/80.0.3987.87 Chrome/80.0.3987.87 Safari/537.36',
			'DNT': '1',
			'Sec-Fetch-Site': 'same-site',
			'Sec-Fetch-Mode': 'cors',
			'Referer': 'https://web.keeptruckin.com/',
			'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
		}
        res_data = requests.get('https://api.keeptruckin.com/api/w2/sessions/validate', headers=headers) 
        json_data = json.loads(res_data.text)
        if json_data:
            user_data = json_data.get('user','')
            if user_data: 
                self.company_id = user_data.get('company_connection',{}).get('company',{}).get('company_id','')
            else:
                self.company_id = ''
    


    def parse_next(self,response):
        error_check = ''.join(response.xpath('//div[@class="flash-error flash-db flash-float text-xs-center login-d-none"]//text()').extract())
        if error_check:
            process_logger.info("User Name: %s - Password: %s - Status: 401 - response: Invalid email address or password",self.username,self.password)
            os.chdir(PROCESSING_QUERY_FILES_PATH)
            item ={"response": "Invalid email address or password", "code":401}
            json_object = json.dumps(item, indent = 4)
            with open("{0}.json".format(self.username), "w") as f:
                f.write(json_object)
            return
        if not error_check:
            data = {
              'utf8': '\u2713',
              'authenticity_token': response.meta['authenticity_token'],
              'client_id': 'baac4693bc4ff187c4906ae3fdcec3e8577df741a584d372aafb467922f49172',
              'redirect_uri': 'https://carrier-data-api-prod.fourkites.com/api/v1/keepTrukin/oauth',
              'state': '',
              'response_type': 'code',
              'scope': 'locations.vehicle_locations_list companies.read',
              'code_challenge': '',
              'code_challenge_method': '',
              'commit': 'Install'
            }
            headers = {
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'Origin': 'https://keeptruckin.com',
                'Upgrade-Insecure-Requests': '1',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
                'Sec-Fetch-User': '?1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'navigate',
                'Referer': 'https://keeptruckin.com/oauth/authorize?client_id=baac4693bc4ff187c4906ae3fdcec3e8577df741a584d372aafb467922f49172&redirect_uri=https://carrier-data-api-prod.fourkites.com/api/v1/keepTrukin/oauth&response_type=code&scope=locations.vehicle_locations_list+companies.read',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            yield scrapy.FormRequest('https://keeptruckin.com/oauth/authorize',formdata=data,callback=self.parse_finish, headers=headers)

    def parse_finish(self,response):
        if '//carrier-data-api-prod.fourkites.com/api/v1/keepTrukin/oauth?code' in response.url:
            auth_code = response.url.split('auth?code=')[-1]
            text = ''.join(response.xpath('//body//div/text()').extract()).replace('\n','').strip()
            if "Great, you're all set" in text:
                item = {'response':text, 'code':200,'auth_code':auth_code,"companyID": self.company_id}
                process_logger.info("User Name: %s - Password: %s - Status: 200 - response: %s - auth_code: %s - company_id: %s",self.username,self.password,text,auth_code,self.company_id)
                
                
        else:
            item = {'response':'failed', 'code':401}
            process_logger.info("User Name: %s - Password: %s - Status: 401 - response: failed",self.username,self.password)

        os.chdir(PROCESSING_QUERY_FILES_PATH)
        json_object = json.dumps(item, indent = 4)
        with open("{0}.json".format(self.username), "w") as f:
            f.write(json_object)
        return
