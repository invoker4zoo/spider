# coding=utf-8

import os
import re
import requests
import pickle
from lxml import etree
import time
from tools.logger import logger

logger.debug('testing')

class WeiboCrawler(object):

    def __init__(self, used_count, uuid, filter):
        pass