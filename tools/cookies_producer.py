# coding=utf-8

import pickle
import os


if os.path.exists('../setting'):
    pass
else:
    os.mkdir('../setting')

with open('../setting/cookies.pkl','w') as f:
    loggin_info = {'412214410@qq.com':'_T_WM=506fcb086463ec3bfb85f5e61696fe33; SCF=AtjsPPzqXqHVMjFpeV4UM1w5dcdenHEFMfbnrvEkws7S-VEH6jcbPtrhjtphg4hBvFR2HEhrphIcU8Mp1CxFTL0.; SUB=_2A250T-C4DeThGeNO6lsU-CfJyDuIHXVXs4DwrDV6PUJbktAKLUfVkW0kVOmkePb4hVRJZjl-AoXLKdyPBw..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Whfjb7E_YcGTQ1HKpEoi9Jh5JpX5oz75NHD95Qfeh24SKn4SKeNWs4DqcjzqcSXUbfbIPBt; SUHB=0jBY8QSk6FLbOi; SSOLoginState=1498124520; ALF=1500716520'}
    pickle.dump(loggin_info,f)