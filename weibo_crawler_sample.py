# coding=utf-8

import os
import re
import requests
import pickle
from lxml import etree
import time
from tools.tools import is_number,now
from tools.logger import logger
from setting.config import COOKIES_SAVE_PATH
from copy import deepcopy
from pymongo import MongoClient


time.time()
MONGO = MongoClient('192.168.48.92', 27017)
DB_NAME, COLL_NAME_USER, COLL_NAME_CONTENT = 'weibo', 'userInfo', 'weiboContent'

class WeiboCrawler(object):

    def __init__(self, using_account, uuid, filter_flag=0):
        """

        :param using_account: 爬取使用的账户
        :param uuid: 正在爬取的用户id
        :param filter_flag: 微博展示类型，url中的filter表示是否显示转发微博,filter=0显示转发微博
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
            'url': '',
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
        selector = etree.HTML(self.html)
        pattern = r"\d+\.?\d*"
        try:
            if selector.xpath('//input[@name="mp"]') is None:
                page_num = 1
            else:
                page_num = int(selector.xpath('//input[@name="mp"]')[0].attrib['value'])

            try:
                # traverse all weibo, and we will got weibo detail urls
                # TODO: inside for loop must set sleep time to avoid banned by sina.
                for page in range(1, page_num):
                    url2 = 'http://weibo.cn/%s?filter=%s&page=%s' % (self.user_id, self.filter, page)
                    html2 = requests.get(url2, cookies=self.cookie, headers=self.headers).content
                    selector2 = etree.HTML(html2)
                    info = selector2.xpath("//div[@class='c']")
                    logger.info('crawl No.{} page for user [{}]'.format(page,self.user_info['userName']))

                    if page % 10 == 0:
                        logger.info('sleeping for 5 minutes to avoid being banned')
                        time.sleep(60 * 5)

                    if len(info) > 3:
                        single_content = deepcopy(self.weibo_content)
                        single_content['userId'] = self.user_id
                        for i in range(0, len(info) - 2):
                            detail = info[i].xpath("@id")[0]
                            single_content['url'] = 'http://weibo.cn/comment/{}?uid={}&rl=0'.\
                                                          format(detail.split('_')[-1], self.user_id)
                            self.weibo_detail_urls.append(single_content['url'])

                            single_content['weiboOriginalNum'] += 1
                            str_t = info[i].xpath("div/span[@class='ctt']")
                            weibos = str_t[0].xpath('string(.)')
                            single_content['content'] = weibos
                            # print(weibos)

                            str_zan = info[i].xpath("div/a/text()")[-4]
                            guid = re.findall(pattern, str_zan, re.M)
                            num_zan = int(guid[0])
                            single_content['numZan'] = num_zan

                            forwarding = info[i].xpath("div/a/text()")[-3]
                            guid = re.findall(pattern, forwarding, re.M)
                            num_forwarding = int(guid[0])
                            single_content['numForward'] = num_forwarding

                            comment = info[i].xpath("div/a/text()")[-2]
                            guid = re.findall(pattern, comment, re.M)
                            num_comment = int(guid[0])
                            single_content['numComment'] = num_comment

                            # save single_content
                            self._weibo_single_content_saved(single_content)
                            logger.info('get weibo content success:{}'.format(single_content))

            except etree.XMLSyntaxError as e:
                logger.error('parsed weibo html failed for:{}'.format(str(e)))
            # if self.filter == 0:
            #     print(u'共' + str(self.weibo_scraped) + u'条微博')
            #
            # else:
            #     print(u'共' + str(self.weibo_num) + u'条微博，其中' + str(self.weibo_scraped) + u'条为原创微博')
        except IndexError as e:
            logger.error('get weibo info done, current user {} has no weibo yet.'.format(self.user_id))

    def _weibo_user_info_saved(self, user_info):
        pass

    def _weibo_single_content_saved(self, single_content):
        single_content['updateTime'] = now()
        try:
            old_data = MONGO[DB_NAME][COLL_NAME_CONTENT].find_one({'url':single_content['url']})
            if not old_data:
                pass
            else:
                pass
        except Exception as e:
            logger.error('saving weibo content info failed for:{}'.format(str(e)))

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

            # save user info
            self._weibo_user_info_saved(self.user_info)
            logger.info('crawl for user:%d done'%self.user_id)
            return True
        except Exception as e:
            logger.error('crawl weibo failed for:{}'.format(str(e)))
            return False


if __name__ == '__main__':
    user_id = 5019589537
    uuid = 1669879400
    filter_flag = 1
    wb = WeiboCrawler(user_id, uuid, filter_flag)
    if wb.crawl():
        pass
    else:
        pass
