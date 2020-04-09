from json import dumps
from time import sleep
from selenium import webdriver
from pyvirtualdisplay import Display
from scrapy.http import Request
from scrapy.spiders import Spider
from scrapy.selector import Selector
from Trucking.utils import get_process_dirs,\
        get_logger, get_json, write_json


get_process_dirs()

class ZonarSelenium(Spider):
    name = 'zonar_selinum'
    start_urls = []

    def __init__(self, **kwargs):
        self.username = kwargs.get('username', '')
        self.password = kwargs.get('password', '')
        self.four_email = "zonar@fourkites.com"
        self.four_fname = "Four"
        self.four_lname = "Kites"
        self.four_password = "partnerhub"
        self.four_uname = "FourKites_partnerhub"

        self.display = Display(visible=1, size=(1400, 1000))
        self.display.start()
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        #options.add_argument('--headless')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.json_file = get_json(self.name, '%s' % self.username)

    def start_requests(self):
        username, customer = '', ''
        logger = get_logger(self.name, '%s' % self.username)
        self.driver.get("https://zonar-login.auth0.com/login?state=g6Fo2SAzdkY0SVdOeTVhU1dWYTZWdHZzbS1QbUpVZWtxM1NReqN0aWTZIGxWTWkya3duWlhiZDFyaFNaRGM2cU15d0x1VjhGMjV5o2NpZNkgMExrVFVzSHFwZzFwSlJ6MGc0VFhXeEdNRnRQd2FvYTk&client=0LkTUsHqpg1pJRz0g4TXWxGMFtPwaoa9&protocol=oauth2&response_type=code&redirect_uri=https%3A%2F%2Fgtclegacy.zonarsystems.net%2Fcallback&scope=openid")
        sleep(2)
        try:
            self.driver.find_element_by_name("email").click()
            self.driver.find_element_by_name("email").clear()
            self.driver.find_element_by_name("email").send_keys(self.username)
            self.driver.find_element_by_name("password").click()
            self.driver.find_element_by_name("password").click()
            self.driver.find_element_by_name("password").clear()
            self.driver.find_element_by_name("password").send_keys(self.password)
            self.driver.find_element_by_xpath("//button[@type='submit']").click()
            try:
                sleep(10)
                self.driver.find_element_by_xpath('//div[@class="auth0-lock-social-button-text"]').click()
                sleep(3)
                self.driver.find_element_by_xpath('//div[@class="auth0-lock-social-button-text"]').click()
            except:
                logger.info("No Active Session")

            username = self.driver.find_element_by_xpath('//div[@class="znr-font-table-body-dark"]').text
            customer = self.driver.find_element_by_xpath('//div[@class="znr-font-header-black"]').text

        except Exception as error:
            logger.error(error)
            logger.info("failed to get the username & customer")

        finally:
            self.display.stop()
            self.driver.quit()

        if not username or not customer:
            logger.info("User Name: %s - Password: %s - Status: 500 - response: %s", self.username, self.password, "Server Error")
            item = dumps({"response": "Internal Server Error", "code": 500})
            write_json(self.json_file, item)
            return

        url = 'https://omi.zonarsystems.net/interface.php?customer=%s&username=%s&password=%s&action=adminusers&operation=add&format=xml&uname=%s&fname=%s&lname=%s&role=Admin&upassword=%s&email=%s&location=Home&isactive=true&timezone=PST8PDT&displaycount=20' % (customer.lower(), username.replace(' User', ''), self.password, self.four_uname, self.four_fname, self.four_lname, self.four_password, self.four_email)
        yield Request(url, self.parse_adduser, meta={'customer': customer, 'logger': logger})

    def parse_adduser(self, response):
        sel = Selector(response)
        logger = response.meta['logger']
        status_message = ''.join(sel.xpath('//message/text()').extract())
        if 'another user' in status_message:
            code = 401
            msg = 'Username already registered.'
            item = dumps({"response": status_message, "code": 401, 'message': msg})

        else:
            item = dumps({
                'username': self.four_uname,
                'password': self.four_password,
                'providercode': response.meta['customer'],
                'code': 200,
                'message': 'User added successfully.'
                })

        write_json(self.json_file, item)
        logger.info("User Name: %s - Password: %s - Status: %s - response: %s", self.username, self.password, code, msg)
