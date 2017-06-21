#coding=utf8

import os
import sys
import urllib
import urllib2
import cookielib
import base64
import re
import hashlib
import json
import rsa
import binascii
import requests
import pickle
from tools.logger import logger
from lxml import etree

COOKIES_FILE_PATH = 'setting/cookies.pkl'


def get_prelogin_status(username):
    """
    Perform prelogin action, get prelogin status, including servertime, nonce, rsakv, etc.
    """
    #prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&client=ssologin.js(v1.4.5)'
    prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=' + get_user(username) + \
     '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.11)';

    # using requests
    # data = urllib2.urlopen(prelogin_url).read()
    response = requests.get(prelogin_url)
    data = response.content

    p = re.compile('\((.*)\)')

    try:
        json_data = p.search(data).group(1)
        data = json.loads(json_data)
        servertime = str(data['servertime'])
        nonce = data['nonce']
        rsakv = data['rsakv']
        return servertime, nonce, rsakv
    except:
        print 'Getting prelogin status met error!'
        return None


def _login(username, pwd, cookie_file):
    """"
        Login with use name, password and cookies.
        (1) If cookie file exists then try to load cookies;
        (2) If no cookies found then do login
    """
    return do_login(username, pwd, cookie_file)


def do_login(username,pwd,cookie_file):
    """"
    Perform login action with use name, password and saving cookies.
    @param username: login user name
    @param pwd: login password
    @param cookie_file: file name where to save cookies when login succeeded
    """
    #POST data per LOGIN WEIBO, these fields can be captured using httpfox extension in FIrefox
    login_data = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '7',
        'userticket': '1',
        'pagerefer':'',
        'vsnf': '1',
        'su': '',
        'service': 'miniblog',
        'servertime': '',
        'nonce': '',
        'pwencode': 'rsa2',
        'rsakv': '',
        'sp': '',
        'encoding': 'UTF-8',
        'prelt': '45',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META'
        }

    # cookie_jar2     = cookielib.LWPCookieJar()
    # cookie_support2 = urllib2.HTTPCookieProcessor(cookie_jar2)
    # opener2         = urllib2.build_opener(cookie_support2, urllib2.HTTPHandler)
    # urllib2.install_opener(opener2)
    login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.11)'
    try:
        servertime, nonce, rsakv = get_prelogin_status(username)
    except:
        return

    #Fill POST data
    print 'starting to set login_data'
    login_data['servertime'] = servertime
    login_data['nonce'] = nonce
    login_data['su'] = get_user(username)
    login_data['sp'] = get_pwd_rsa(pwd, servertime, nonce)
    login_data['rsakv'] = rsakv
    # login_data = urllib.urlencode(login_data)
    http_headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
    # trans to request
    # req_login  = urllib2.Request(
    #     url = login_url,
    #     data = login_data,
    #     headers = http_headers
    # )
    # # testing request/cookies part
    session = requests.session()
    reponse = session.post(login_url,data=login_data,headers=http_headers)
    text = reponse.content


    # result = urllib2.urlopen(req_login)
    # text = result.read()
    p = re.compile('location\.replace\(\'(.*?)\'\)')
    try:
        #Search login redirection URL
        trans_login_url = p.search(text).group(1)
        # if trans_login_url:
        #     login_status = 1
        # else:
        #     login_status = 0
        # _response = session.get(trans_login_url)
        # p = re.compile("framelogin\=(.*)\&callback")
        # data = _response.content
        # login_status = int(p.search(data).group(1))
        # # visit testing page
        testing_url = 'http://weibo.cn/u/1669879400?filter=0&page=1'
        __response = session.get(testing_url)
        selector = etree.HTML(__response.content)
        status = selector.xpath('//div[@class="tm"]')
        if len(status):
            login_status = 1
        else:
            login_status = 0

        cookies_dic = requests.utils.dict_from_cookiejar(session.cookies)
        if login_status:
            save_cookies(cookies_dic,username)
            return 1
        else:
            return 0
    except Exception as e:
        logger.error('login failed for %s'%(str(e)))
        return 0


def save_cookies(cookies_dic,using_account):
    try:
        _cookies_dic = cookies_dic
        if os.path.exists(COOKIES_FILE_PATH):
            with open(COOKIES_FILE_PATH, 'r+') as f:
                saving_cookies_dic = pickle.load(f)
                if using_account in saving_cookies_dic.keys():
                    saving_cookies_dic[using_account] = _cookies_dic
                    pickle.dump(saving_cookies_dic,f)
                    logger.info('update cookies of using account {}'.format(using_account))
                else:
                    saving_cookies_dic[using_account] = _cookies_dic
                    pickle.dump(saving_cookies_dic,f)
                    logger.info('saving cookies of using account {}'.format(using_account))
        else:
            with open(COOKIES_FILE_PATH, 'w') as f:
                saving_cookies_dic = {using_account:_cookies_dic}
                pickle.dump(saving_cookies_dic,f)
    except Exception as e:
        logger.error('saving cookies failed for' + str(e))


def get_pwd_wsse(pwd, servertime, nonce):
    """
        Get wsse encrypted password
    """
    pwd1 = hashlib.sha1(pwd).hexdigest()
    pwd2 = hashlib.sha1(pwd1).hexdigest()
    pwd3_ = pwd2 + servertime + nonce
    pwd3 = hashlib.sha1(pwd3_).hexdigest()
    return pwd3


def get_pwd_rsa(pwd, servertime, nonce):
    """
        Get rsa2 encrypted password, using RSA module from https://pypi.python.org/pypi/rsa/3.1.1, documents can be accessed at
        http://stuvel.eu/files/python-rsa-doc/index.html
    """
    #n, n parameter of RSA public key, which is published by WEIBO.COM
    #hardcoded here but you can also find it from values return from prelogin status above
    weibo_rsa_n = 'EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443'

    #e, exponent parameter of RSA public key, WEIBO uses 0x10001, which is 65537 in Decimal
    weibo_rsa_e = 65537
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd)

    #construct WEIBO RSA Publickey using n and e above, note that n is a hex string
    key = rsa.PublicKey(int(weibo_rsa_n, 16), weibo_rsa_e)

    #get encrypted password
    encropy_pwd = rsa.encrypt(message, key)
    #trun back encrypted password binaries to hex string
    return binascii.b2a_hex(encropy_pwd)


def get_user(username):
    username_ = urllib.quote(username)
    username = base64.encodestring(username_)[:-1]
    return username


if __name__ == '__main__':


    username = '412214410@qq.com'
    pwd = '4vYzvwdi'
    cookie_file = 'weibo_login_cookies.dat'

    if _login(username, pwd, cookie_file):
        print 'Login WEIBO succeeded'
        #if you see the above message, then do whatever you want with urllib2, following is a example for fetch Kaifu's Weibo Home Page
        #Trying to fetch Kaifu Lee's Weibo home page
        # test page
        # kaifu_page = urllib2.urlopen('http://www.weibo.com/kaifulee').read()
        # print kaifu_page

    else:
        print 'Login WEIBO failed'