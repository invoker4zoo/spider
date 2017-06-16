# coding=utf-8

import os
import re
import requests
import pickle
from lxml import etree
import time
from tools.tools import is_number
from tools.logger import logger
from setting.config import COOKIES_SAVE_PATH
from copy import deepcopy

logger.debug('testing')

class WeiboCrawler(object):

    def __init__(self, using_account, uuid, filter_flag=0):
        """

        :param using_account: 爬取使用的账户
        :param uuid: 正在爬取的用户id
        :param filter_flag: 微博展示类型，url中的filter表示是否显示转发微博
        """
        self.using_account = using_account
        self._init_cookies()
        self._init_headers()

        self.user_id = uuid
        self.filter = filter_flag
        self.user_info = {
            'userName': '',
            'weiboNum': 0,
            'weiboOriginalNum': 0,
            'following': 0,
            'followers': 0,
        }
        # self.user_name = ''
        # self.weibo_num = 0
        # self.weibo_scraped = 0
        # self.following = 0
        # self.followers = 0
        self.weibo_content_list = []
        self.weibo_content = {
            'numZan': 0,
            'numForwarding': 0,
            'numComment': 0,
            'content': ''
        }
        # self.num_zan = []
        # self.num_forwarding = []
        # self.num_comment = []
        self.weibo_detail_urls = []

    def _init_cookies(self):
        """
        initial request cookies
        """
        try:
            with open(COOKIES_SAVE_PATH, 'rb') as f:
                cookies_dict = pickle.load(f)
            cookies = cookies_dict[self.using_account]
            cookie = {
                "Cookie": cookies
            }
            self.cookie = cookie
        except Exception as e:
            logger.error('intial cookies failed for:' + str(e))

    def _init_headers(self):
        """
        initial request header
        """
        headers = requests.utils.default_headers()
        user_agent = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko/20100101 Firefox/11.0'
        }
        headers.update(user_agent)
        self.headers = headers

    def _get_html(self):
        try:
            if is_number(self.user_id):
                url = 'http://weibo.cn/u/%s?filter=%s&page=1' % (self.user_id, self.filter)
                logger.info('crawl url is :{}'.format(url))
            else:
                url = 'http://weibo.cn/%s?filter=%s&page=1' % (self.user_id, self.filter)
                logger.info('crawl url is :{}'.format(url))
            self.html = requests.get(url, cookies=self.cookie, headers=self.headers).content
            logger.info('load html success')
        except Exception as e:
            logger.error('getting html failed for {}'.format(str(e)))

    def _get_user_info(self):
        # getting user name
        try:
            selector = etree.HTML(self.html)
            self.user_info['userName'] = selector.xpath('//table//div[@class="ut"]/span[1]/text()')[0]
            logger.info('user name is %s'%self.user_name)
        except Exception as e:
            logger.error('getting user name failed for:{}'.format(str(e)))

        # getting user other info
        try:
            selector = etree.HTML(self.html)
            pattern = r"\d+\.?\d*"
            str_wb = selector.xpath('//span[@class="tc"]/text()')[0]
            guid = re.findall(pattern, str_wb, re.S | re.M)
            for value in guid:
                num_wb = int(value)
                break
            self.user_info['weiboNum'] = num_wb

            str_gz = selector.xpath("//div[@class='tip2']/a/text()")[0]
            guid = re.findall(pattern, str_gz, re.M)
            self.user_info['following'] = int(guid[0])

            str_fs = selector.xpath("//div[@class='tip2']/a/text()")[1]
            guid = re.findall(pattern, str_fs, re.M)
            self.user_info['followers'] = int(guid[0])
            logger.info('current user all weibo num {}, following {}, followers {}'.format(self.user_info['weiboNum'],
                                                                                     self.user_info['following'],
                                                                                     self.user_info['followers']))
        except Exception as e:
            logger.error('getting user info failed for:{}'.format(str(e)))

    def _get_weibo_info(self):
        pass

    def crawl(self):
        """
        main function for [Weibocrawler]
        :return: crawl status
        """
        try:
            self._get_html()
            # self._get_user_name()
            self._get_user_info()
            self._get_weibo_info()
            # self._get_weibo_detail_comment()
            logger.info('crawl for user:%d done'%self.user_id)
            return True
        except Exception as e:
            return False