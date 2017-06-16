# coding=utf-8

import pickle
import os
import time

# if os.path.exists('../setting'):
#     pass
# else:
#     os.mkdir('../setting')
#
# with open('../setting/cookies.pkl','w') as f:
#     loggin_info = {5019589537:'_T_WM=506fcb086463ec3bfb85f5e61696fe33; SCF=AtjsPPzqXqHVMjFpeV4UM1w5dcdenHEFMfbnrvEkws7SGSex3tAlQFLq6zVMZOCtA6XIu9Mjf8I57F_1b0qpBE4.; ALF=1500025428; SUB=_2A250RXUEDeThGeNO6lsU-CfJyDuIHXVXxhtMrDV6PUJbktANLWPekW1m4KykoSrfMMbcSQjeI6hPV632Nw..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Whfjb7E_YcGTQ1HKpEoi9Jh5JpX5o2p5NHD95Qfeh24SKn4SKeNWs4DqcjzqcSXUbfbIPBt; SUHB=0IIFuQRDwizovd; SSOLoginState=1497433428_T_WM=506fcb086463ec3bfb85f5e61696fe33; SCF=AtjsPPzqXqHVMjFpeV4UM1w5dcdenHEFMfbnrvEkws7SGSex3tAlQFLq6zVMZOCtA6XIu9Mjf8I57F_1b0qpBE4.; ALF=1500025428; SUB=_2A250RXUEDeThGeNO6lsU-CfJyDuIHXVXxhtMrDV6PUJbktANLWPekW1m4KykoSrfMMbcSQjeI6hPV632Nw..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Whfjb7E_YcGTQ1HKpEoi9Jh5JpX5o2p5NHD95Qfeh24SKn4SKeNWs4DqcjzqcSXUbfbIPBt; SUHB=0IIFuQRDwizovd; SSOLoginState=1497433428'}
#     pickle.dump(loggin_info,f)
def is_number(s):
    try:
        a = float(s)
        return True
    except ValueError as e:
        return False
def now():
    time_format = '%Y-%m-%d %X'
    return time.strftime(time_format,time.localtime())

