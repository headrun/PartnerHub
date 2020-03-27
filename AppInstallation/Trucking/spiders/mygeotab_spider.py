from json import dumps, loads
from datetime import datetime
from scrapy.spiders import Spider
from scrapy.http import Request, FormRequest
from Trucking.utils import get_process_dirs,\
        get_logger, get_json, write_json

get_process_dirs()

class MyGeoTab(Spider):
    name = 'mygeotab_spider'
    start_urls = ['https://my.geotab.com/']

    def __init__(self, *args, **kwargs):
        self.username = kwargs.get('username', '')
        self.firstname = kwargs.get('firstname', '')
        self.lastname = kwargs.get('lastname', '')
        self.password = "%s%s_partnerhub1" % (self.firstname, self.lastname)
        if not self.username or not self.firstname or not self.lastname:
            return "Credentials Missing"

        self.login_username = "greg.pruitt@fourkites.com"
        self.login_password = "KitesFlyHigh1"
        self.json_file = get_json(self.name, '%s%s' % (self.firstname, self.lastname))

    def parse(self, response):
        logger = get_logger(self.name, '%s%s' % (self.firstname, self.lastname))
        _dict = {
                "JSON-RPC": dumps({
                    "method": "Authenticate",
                    "params": {
                        "database": "",
                        "userName": self.login_username,
                        "password": self.login_password
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
                            "name": self.username,
                            "firstName": self.firstname.title(),
                            "lastName": self.lastname.title(),
                            "password": self.password.replace('.', '').strip(),
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
                            "WindowsAuthenticationUserId": self.username
                            },
                        "credentials": {
                            "database": database,
                            "sessionId": session_id,
                            "userName": self.login_username
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
                    'username': self.username,
                    'password': self.password,
                    'providercode': 'database',
                    'code': 200,
                    'message': msg
                    })

            write_json(self.json_file, item)

        if error_check or not success_check:
            code = 401
            if 'duplicate' in error_check.lower():
                msg = 'Username already registered.'
            else:
                msg = 'Something went wrong. Please check.'

        logger.info("User Name: %s - Password: %s - Status: %s - response: %s", self.username, self.password, code, msg)

