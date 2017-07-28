# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: main.py
@ time: $17-7-24 下午3:47
"""

import argparse
from dispatch import Dispatch
from setting.config import SEEKING_ID,DEFAULT_ID
from tools.logger import logger

def parse_args():
    parse = argparse.ArgumentParser(description='Weibo crawler. Invoker')

    # setting uid
    _help = 'set seeking uid'
    parse.add_argument('-u', '--uid', default=DEFAULT_ID, help=_help)

    # setting flag filter
    _help = 'set weibo filter flag, if filter flag is 0, weibo seeking is original, ' \
            'if is 1 contains repost info; default is 0'
    parse.add_argument('-f', '--filter', default='1', help=_help)

    # setting update_cookies
    _help = 'set update cookies, set True, update cookies before crawler, set False, without update'
    parse.add_argument('-uc', '--updatecookies', default='0', help=_help)

    # setting retry
    _help = 'set account retry'
    parse.add_argument('-t', '--retry', default='0', help=_help)

    # setting mode
    _help = 'set running mode'
    parse.add_argument('-m', '--mode', default='test', help=_help)


if __name__ == '__main__':
    args = parse_args()
    if args.mode == 'test':
        pass
    elif args.mode == 'online':
        pass
    elif args.mode == 'offline':
        pass
    else:
        logger.info('mode setting is invaild')
