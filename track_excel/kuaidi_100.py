# -*- coding: utf-8 -*-
'''
Created on 2016-11-22
@author: ghoti
'''
import time
from hashlib import md5
import requests
import json
 
class KuaiDi100(object):
    '''
       get express number via kuaidi100
       kuaidi_com:物流公司(zhongtong)，partnerId:月结账号
    '''
    def __init__(self, key=None, secret=None):
        self.key = key
        self.secret = secret

    def _sign(self,params):
        '''
        Generate API sign code
        '''
        src = params['param']+params['t']+self.key+self.secret      
        return md5(src).hexdigest().upper()

    def _get_timestamp(self):
        return str(time.time()).split('.')[0]

    def _get_content(self,content):
        return json.dumps(content)

    def _get_top_resp(self, url, params):
        try:
            r = requests.post(url,data=params)
            return r.json(),None
        except Exception,e:
            msg = "request error：kuaidi100 _get_top_resp e:%s" % e
            return None, msg

    def execute(self, API_address, method_name, content, **kwargs):
        params = {}
        params['key'] = self.key
        params['t'] = self._get_timestamp()
        params['param'] = self._get_content(content)
        params['sign'] = self._sign(params)
        params['method']=method_name
        
        rsp, error_info = self._get_top_resp(API_address, params)
        if not rsp: 
            return None,error_info
        
        try :
            if rsp.get('result',None) and rsp['status'] == '200':
                return rsp,None
            else:
                return None,rsp['message']
        except Exception,e:
            msg = 'get message from rainbow fail.  e = %s  rsp = %s' % (str(e), str(rsp))
            return None,msg

    def __call__(self, API_address, method_name, content, **kwargs):
        return self.execute(API_address, method_name, content, **kwargs)


##for test
r = KuaiDi100('your key','your secret')
url = 'http://api.kuaidi100.com/eorderapi.do'

partnerId = ''
need_template = 1
kuaidi_com = 'zhongtong'

content={
    "recMan":{"name":"张文轩","mobile":"13641644555","tel":"","zipCode":"","province":"吉林省",\
        "city":"长春市","district":"香洲区","addr":"翠香街道镜新二街56号凤凰公寓A座1201房","company":""},
    "sendMan":{"name":"	bjhgs","mobile":"15999542842","tel":"","zipCode":"","province":"北京",\
        "city":"北京市","district":"房山区","addr":"青龙湖镇良坨路甲1号北京首诚农业花果山","company":"深圳**有限公司"},
    "kuaidicom":"%s"%kuaidi_com,"partnerId":"%s"%partnerId,"partnerKey":"","net":"","kuaidinum":"",\
    "orderId":"hgsA2147_test","payType":"SHIPPER","expType":"标准快递","weight":"1","volumn":"0","count":1,\
    "remark":"备注","valinsPay":"0","collection":"0","needChild":"0","needBack":"0","cargo":"水果","needTemplate":"%s"%need_template}

rsp,error_info = r(url,'getElecOrder',content)
#print rsp
bulkpen = rsp['data'][0]['bulkpen']
kuaidinum = rsp['data'][0]['kuaidinum']
print bulkpen,kuaidinum
