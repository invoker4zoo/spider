# -*-coding:utf-8 -*-
# url https://github.com/ResolveWang/WeiboSpider
import re
import os
import rsa
import math
import time
import random
import base64
import binascii
import requests
import urllib
from tools.logger import logger
import pickle

COOKIES_FILE_PATH = 'setting/cookies.pkl'
index_url = "http://weibo.com/login.php"
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Connection': 'keep-alive'
}


def get_password(password, servertime, nonce, pubkey):
    rsa_publickey = int(pubkey, 16)
    key = rsa.PublicKey(rsa_publickey, 65537)  # 创建公钥,
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)  # 拼接明文js加密文件中得到
    message = message.encode("utf-8")
    passwd = rsa.encrypt(message, key)  # 加密
    passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制。
    return passwd


# 使用post提交加密后的所有数据,并且获得下一次需要get请求的地址
def get_redirect(name, data, post_url, session):
    """
    :param name: 登录用户名
    :param data: 需要提交的数据，可以通过抓包来确定部分不变的
    :param post_url: post地址
    :param session:
    :return: 服务器返回的下一次需要请求的url,如果打码出错，返回特定字符串好做特殊处理
    """
    logining_page = session.post(post_url, data=data, headers=headers)
    login_loop = logining_page.content.decode("GBK")

    # 如果是账号密码不正确，那么就将该字段置为2
    if 'retcode=101' in login_loop:
        logger.error(u'账号{}的密码不正确'.format(name))
        return ''

    if 'retcode=2070' in login_loop:
        logger.error(u'输入的验证码不正确')
        return 'pinerror'

    if 'retcode=4049' in login_loop:
        logger.error(u'账号{}登录需要验证码'.format(name))
        return 'login_need_pincode'

    if '正在登录' or 'Signing in' in login_loop:
        pa = r'location\.replace\([\'"](.*?)[\'"]\)'
        return re.findall(pa, login_loop)[0]
    else:
        return ''


def login_no_pincode(name, password, session, server_data):
    post_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'

    servertime = server_data["servertime"]
    nonce = server_data['nonce']
    rsakv = server_data["rsakv"]
    pubkey = server_data["pubkey"]
    sp = get_password(password, servertime, nonce, pubkey)

    # 提交的数据可以根据抓包获得
    data = {
        'encoding': 'UTF-8',
        'entry': 'weibo',
        'from': '',
        'gateway': '1',
        'nonce': nonce,
        'pagerefer': "",
        'prelt': 67,
        'pwencode': 'rsa2',
        "returntype": "META",
        'rsakv': rsakv,
        'savestate': '7',
        'servertime': servertime,
        'service': 'miniblog',
        'sp': sp,
        'sr': '1920*1080',
        'su': get_encodename(name),
        'useticket': '1',
        'vsnf': '1',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack'
    }

    rs = get_redirect(name, data, post_url, session)

    return rs, '', session


def get_encodename(name):
    # 如果用户名是手机号，那么需要转为字符串才能继续操作
    username_quote = urllib.quote_plus(str(name))
    username_base64 = base64.b64encode(username_quote.encode("utf-8"))
    return username_base64.decode("utf-8")


# 预登陆获得 servertime, nonce, pubkey, rsakv
def get_server_data(su, session):
    pre_url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="
    pre_url = pre_url + su + "&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_="
    prelogin_url = pre_url + str(int(time.time() * 1000))
    pre_data_res = session.get(prelogin_url, headers=headers)

    sever_data = eval(pre_data_res.content.decode("utf-8").replace("sinaSSOController.preloginCallBack", ''))

    return sever_data


def do_login(name, password):
    session = requests.Session()
    su = get_encodename(name)
    server_data = get_server_data(su, session)

    if server_data['showpin']:
        logger.info('need captcha identification')
        return '', None, None

    else:
        rs, yundama_obj, cid, session = login_no_pincode(name, password, session, server_data)
        if rs == 'login_need_pincode':
            # session = requests.Session()
            # su = get_encodename(name)
            # server_data = get_server_data(su, session)
            # rs, yundama_obj, cid, session = login_by_pincode(name, password, session, server_data, 0)
            logger.info('need captcha identification')
            return '', None, None

        if rs == 'pinerror':
            # rs, yundama_obj, cid, session = login_retry(name, password, session, yundama_obj, cid)
            logger.info('captcha error')
            return '', None, None

    return rs, cid, session


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


# 获取成功登陆返回的信息,包括用户id等重要信息,返回登陆session,存储cookies到redis
def get_session(name, password):
    url, cid, session = do_login(name, password)

    if url != '':
        rs_cont = session.get(url, headers=headers)
        login_info = rs_cont.text

        u_pattern = r'"uniqueid":"(.*)",'
        m = re.search(u_pattern, login_info)
        if m and m.group(1):
            # 访问微博官方账号看是否正常
            check_url = 'http://weibo.com/2671109275/about'
            resp = session.get(check_url, headers=headers)
            # 通过实验，目前发现未经过手机验证的账号是救不回来了...
            if resp.status_code == 403:
                logger.error('账号{}已被冻结'.format(name))
                # freeze_account(name, 0)
                return None
            logger.info('本次登陆账号为:{}'.format(name))
            return session


    return None


if __name__ == '__main__':
    user_name = '412214410@qq.com'
    password = '4vYzvwdi'
    session = get_session(user_name, password)
    if session:
        save_cookies(session.cookies.get_dict(),user_name)
    else:
        logger.error('本次账号{}登陆失败'.format(user_name))