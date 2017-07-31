# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: dispatch.py
@ time: $17-7-24 下午3:34
"""

from weibo_crawler_sample import WeiboCrawler
from setting.config import COOKIES_SAVE_PATH, accounts,SEEKING_ID
from tools.logger import logger
from phantom_login import get_cookie_from_network
import pickle
import random


class Dispatch(object):
    """
    Dispatch account and work,
    base class
    if using info queue ,rewrite fun
    """
    def __init__(self, uid, filter_flag=0, account_dic=accounts, cookies_path=COOKIES_SAVE_PATH,
                 update_cookies=False, retry=False):
        self.filter_flag = filter_flag
        self.uid = uid
        self.account_dic = account_dic
        self.account_list = self.account_dic.keys()
        self.cookies_path = cookies_path
        self.update_cookies = update_cookies
        self.used_account = list()
        self.using_account = self.choose_using_account()
        self.retry = retry

        self._init_accounts_cookies()
        # self._init_cookie_dic()

        # main fun execute crawler

    def _init_cookie_dic(self):
        try:
            with open(self.cookies_path, 'rb') as f:
                self.cookies_dic = pickle.load(f)
        except Exception,e:
            logger.error('get cookies failed for %s'%str(e))

    def _init_accounts_cookies(self):
        if self.update_cookies:
            for account in self.account_list:
                password = self.account_dic[account]
                logger.info('update account[%s] cookie'%account)
                get_cookie_from_network(account, password)
        else:
            pass

    def re_choose_using_account(self):
        while 1:
            if len(self.used_account)<len(self.account_list):
                choose_account = random.sample(self.account_list, 1)[0]
                if choose_account in self.used_account:
                    continue
                else:
                    self.used_account.append(choose_account)
                    return choose_account
            else:
                logger.info('all account used')
                return None

    def choose_using_account(self):
        choose_account = random.sample(self.account_list, 1)[0]
        self.used_account.append(choose_account)
        logger.info('choosing [%s] account'%choose_account)
        return choose_account

    def execute(self):
        while 1:
            try:
                wb = WeiboCrawler(self.using_account, self.uid, self.filter_flag)
                if wb.crawl():
                    logger.info('execute weibo crawler success for user %s'%str(self.uid))
                    break
                else:
                    logger.info('execute weibo crawler failed for user %s' % str(self.uid))
                    break
            except Exception,e:
                logger.error('execute weibo crawler failed %s with account'%(str(e),self.using_account))
                if self.retry:
                    re_choose_account = self.re_choose_using_account()
                    if re_choose_account:
                        self.used_account = re_choose_account
                    else:
                        logger.info('all account tried, execute failed')
                        break
                else:
                    break


if __name__ == '__main__':
    logger.info('begin testing')
    for uid in SEEKING_ID:
        dispatch = Dispatch(uid=uid, update_cookies=True, retry=True)
        dispatch.execute()
