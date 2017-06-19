# coding=utf-8

import pickle
import os


if os.path.exists('../setting'):
    pass
else:
    os.mkdir('../setting')

with open('../setting/cookies.pkl','w') as f:
    loggin_info = {5019589537:'_T_WM=506fcb086463ec3bfb85f5e61696fe33; SCF=AtjsPPzqXqHVMjFpeV4UM1w5dcdenHEFMfbnrvEkws7S5SeTGBQ7EoeANEgjs0h7_PeWm3JJu4lLD5ZCusZrbAs.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Whfjb7E_YcGTQ1HKpEoi9Jh5JpX5KMhUgL.Fo-7eK.f1h.fe0M2dJLoI7yoqNxcTgiDU5tt; SUB=_2A250QwDhDeThGeNO6lsU-CfJyDuIHXVXz6CprDV6PUJbkdANLWbtkW2GwlpDcbaXu7Vct-rRjGm0EDw2Sg..; SUHB=0M2VzpXIaDuVGx; SSOLoginState=1497854129; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D102803_ctg1_8999_-_ctg1_8999_home'}
    pickle.dump(loggin_info,f)