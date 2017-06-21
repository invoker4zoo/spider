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


index_url = "http://weibo.com/login.php"
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Connection': 'keep-alive'
}

# 获取成功登陆返回的信息,包括用户id等重要信息,返回登陆session,存储cookies到redis
def get_session(name, password):
    url, yundama_obj, cid, session = do_login(name, password)

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
            if is_403(resp.text):
                other.error('账号{}已被冻结'.format(name))
                freeze_account(name, 0)
                return None
            other.info('本次登陆账号为:{}'.format(name))
            Cookies.store_cookies(name, session.cookies.get_dict())
            return session

    other.error('本次账号{}登陆失败'.format(name))
    return None