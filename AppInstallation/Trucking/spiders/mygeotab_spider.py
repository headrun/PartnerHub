from json import dumps, loads
from datetime import datetime
from scrapy.spiders import Spider
from scrapy.http import Request, FormRequest
from Trucking.utils import get_process_dirs,\
        get_logger, get_json, write_json

get_process_dirs()

class MyGeoTab(Spider):
    name = 'mygeotab_spider'
    start_urls = []

    def __init__(self, *args, **kwargs):
        self.username = kwargs.get('username', '')
        self.password = kwargs.get('password', '')
        if not self.username and not self.password:
            return "Credentials Missing"

        self.four_username = "geotab@fourkites.com"
        self.four_firstname = "Four"
        self.four_lastname = "Kites"
        self.four_password = "partnerhub1"
        self.json_file = get_json(self.name, '%s' % self.username)

    def start_requests(self):
        logger = get_logger(self.name, '%s' % self.username)
        _dict = {
                "JSON-RPC": dumps({
                    "method": "Authenticate",
                    "params": {
                        "database": "",
                        "userName": self.username,
                        "password": self.password
                        }
                    })
                }
        url = 'https://my664.geotab.com/apiv1'
        return FormRequest(url, callback=self.parse_login, formdata=_dict, meta={'logger': logger})

    def parse_login(self, response):
        logger = response.meta.get('logger', '')
        _data = loads(response.body)
        error_check = _data.get('error', {}).get('message', '')
        if error_check:
            self.logger.info("User Name: %s - Password: %s - Status: 401 - response: %s", self.username, self.password, error_check)
            item = dumps({"response": error_check, "code":401})
            write_json(self.json_file, item)
            return

        session_id = _data.get('result', {}).get(
            'credentials', {}).get('sessionId', '')
        database = _data.get('result', {}).get(
            'credentials', {}).get('database', '')

        _dict = {
                "JSON-RPC": dumps({
                    "method": "Add",
                    "params": {
                        "typeName": "User",
                        "entity": {
                            "userAuthenticationType": "BasicAuthentication",
                            "name": self.four_username,
                            "firstName": self.four_firstname.title(),
                            "lastName": self.four_lastname.title(),
                            "password": self.four_password,
                            "securityGroups": [{"id": "GroupDriveUserSecurityId"}],
                            "changePassword": False,
                            "designation": "",
                            "employeeNo": "",
                            "comment": "",
                            "isMetric": False,
                            "fuelEconomyUnit": "MPGUS",
                            "electricEnergyEconomyUnit": "MPGEUS",
                            "dateFormat": "MM/dd/yy hh:mm:ss tt",
                            "timeZoneId": "America/New_York",
                            "firstDayOfWeek": "Sunday",
                            "language": "en",
                            "defaultPage": "dashboard",
                            "hosRuleSet": None,
                            "isLabsEnabled": False,
                            "isNewsEnabled": True,
                            "isEmailReportEnabled": True,
                            "companyName": database.replace('_', ' '),
                            "companyAddress": "",
                            "carrierNumber": "",
                            "licenseNumber": "",
                            "licenseProvince": "",
                            "isYardMoveEnabled": False,
                            "isPersonalConveyanceEnabled": False,
                            "authorityName": database.replace('_', ' '),
                            "authorityAddress": "",
                            "defaultGoogleMapStyle": "Roadmap",
                            "defaultOpenStreetMapStyle": "MapBox",
                            "defaultHereMapStyle": "Roadmap",
                            "isDriver": False,
                            "activeFrom": "%sZ" % datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],
                            "activeTo": "2050-01-01T00:00:00.000Z",
                            "companyGroups": [{"id": "GroupCompanyId"}],
                            "reportGroups": [],
                            "WindowsAuthenticationUserId": self.four_username
                            },
                        "credentials": {
                            "database": database,
                            "sessionId": session_id,
                            "userName": self.username
                            }
                        }
                    })
                }

        response.meta.update({'database': database})
        url='https://my664.geotab.com/apiv1'
        return FormRequest(url, callback=self.parse_adduser, formdata=_dict, meta=response.meta)

    def parse_adduser(self, response):
        _data = loads(response.body)
        logger = response.meta['logger']
        database = response.meta['database']
        msg = ''
        success_check = _data.get("result", '')
        error_check = _data.get("error", {}).get('message', '')
        if success_check:
            code = 200
            msg = 'User added successfully.'
            item = dumps({
                    'username': self.four_username,
                    'password': self.four_password,
                    'providercode': database,
                    'code': 200,
                    'message': msg
                    })

        if error_check or not success_check:
            code = 401
            if 'duplicate' in error_check.lower():
                msg = 'Username already registered.'
            else:
                msg = 'Something went wrong. Please check.'

            item = dumps({"response": error_check, "code": 401, 'message': msg})

        write_json(self.json_file, item)
        logger.info("User Name: %s - Password: %s - Status: %s - response: %s", self.username, self.password, code, msg)

