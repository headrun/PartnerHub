import scrapy
import re
import json
from urllib.parse import urlencode, unquote
import urllib
import os
import datetime
import requests
import glob
import logging
import logging.handlers
loggers = {}

TIMESTAMP = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
PAR_DIR = os.path.abspath('.')
LOG_PATH = os.path.abspath('logs/')
OUTPUT_DIR = os.path.join(PAR_DIR, 'spiders/OUTPUT')
PROCESSING_QUERY_FILES_PATH = os.path.join(OUTPUT_DIR, 'processing')
PROCESSED_QUERY_FILES_PATH = os.path.join(OUTPUT_DIR, 'processed')

def get_logger(spider_name, username):
    global loggers
    path = os.path.join(LOG_PATH, '%s_%s_%s.log')

    if loggers.get('spider_process'):
        return loggers.get('spider_process')
    else:
        logger = logging.getLogger('spider_process')
        logger.setLevel(logging.DEBUG)
        now = datetime.datetime.now()
        handler = logging.FileHandler(path % (spider_name, username, TIMESTAMP))
        formatter = logging.Formatter('%(asctime)s - %(filename)s - %(lineno)d - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        loggers.update(dict(name=logger))
        return logger

def get_process_dirs():
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    
    if not os.path.exists(PROCESSING_QUERY_FILES_PATH):
        os.mkdir(PROCESSING_QUERY_FILES_PATH)

    if not os.path.exists(PROCESSED_QUERY_FILES_PATH):
        os.mkdir(PROCESSED_QUERY_FILES_PATH)

    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)

def get_json(spider_name, username):
    query_file = os.path.join(PROCESSING_QUERY_FILES_PATH, '%s_%s.json' % (spider_name, username))
    return query_file

def write_json(path, item):
    with open(path, "w") as _file:
        _file.write(item)

def move_to_processed(filename):
    file_path = "{0}/{1}.json".format(PROCESSING_QUERY_FILES_PATH, filename)
    cmd = "mv %s %s" %(file_path, PROCESSED_QUERY_FILES_PATH)
    try:
        os.system(cmd)
    except:
        pass

