# coding=utf-8

import os
import sys
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import InvalidElementStateException
from selenium import webdriver
import time
import pickle
from tools.logger import logger


LOGIN_URL = 'https://passport.weibo.cn/signin/login'
PHANTOM_JS_PATH = '/usr/bin/phantomjs'
COOKIES_SAVE_PATH = 'setting/cookies.pkl'




def get_cookie_from_network(account_id, account_password):
    url_login = LOGIN_URL
    phantom_js_driver_file = os.path.abspath(PHANTOM_JS_PATH)
    if os.path.exists(phantom_js_driver_file):
        try:
            logger.info('loading PhantomJS from {}'.format(phantom_js_driver_file))
            driver = webdriver.PhantomJS(phantom_js_driver_file)
            # must set window size or will not find element
            driver.set_window_size(1640, 688)
            driver.get(url_login)
            # before get element sleep for 10 seconds, waiting for page render complete.
            time.sleep(10)
            driver.find_element_by_xpath('//input[@id="loginName"]').send_keys(account_id)
            driver.find_element_by_xpath('//input[@id="loginPassword"]').send_keys(account_password)
            # driver.find_element_by_xpath('//input[@id="loginPassword"]').send_keys(Keys.RETURN)
            logger.info('account id: {}'.format(account_id))
            logger.info('account password: {}'.format(account_password))

            driver.find_element_by_xpath('//a[@id="loginAction"]').click()
        except InvalidElementStateException as e:
            logger.error(str(e))
            logger.error('error, account id {} is not valid, pass this account, you can edit it and then '
                  'update cookies. \n'
                  .format(account_id))

        try:
            cookie_list = driver.get_cookies()
            cookie_string = ''
            for cookie in cookie_list:
                if 'name' in cookie and 'value' in cookie:
                    cookie_string += cookie['name'] + '=' + cookie['value'] + ';'
            if 'SSOLoginState' in cookie_string:
                logger.info('success get cookies!! \n {}'.format(cookie_string))
                if os.path.exists(COOKIES_SAVE_PATH):
                    with open(COOKIES_SAVE_PATH, 'rb') as f:
                        cookies_dict = pickle.load(f)
                    if cookies_dict[account_id] is not None:
                        cookies_dict[account_id] = cookie_string
                        with open(COOKIES_SAVE_PATH, 'wb') as f:
                            pickle.dump(cookies_dict, f)
                        logger.info('successfully save cookies into {}. \n'.format(COOKIES_SAVE_PATH))
                    else:
                        cookies_dict[account_id] = cookie_string
                        with open(COOKIES_SAVE_PATH, 'wb') as f:
                            pickle.dump(cookies_dict, f)
                        logger.info('successfully save cookies into {}. \n'.format(COOKIES_SAVE_PATH))
                else:
                    cookies_dict = dict()
                    cookies_dict[account_id] = cookie_string
                    with open(COOKIES_SAVE_PATH, 'wb') as f:
                        pickle.dump(cookies_dict, f)
                    logger.info('successfully save cookies into {}. \n'.format(COOKIES_SAVE_PATH))
                return cookie_string
            else:
                logger.error('error, account id {} is not valid, pass this account, you can edit it and then '
                      'update cookies. \n'
                      .format(account_id))
                pass

        except Exception as e:
            print(e)

    else:
        logger.error('can not find PhantomJS driver, please download from http://phantomjs.org/download.html based on your '
              'system.')



if __name__ == '__main__':
    account = '412214410@qq.com'
    password = '4vYzvwdi'
    get_cookie_from_network(account,password)