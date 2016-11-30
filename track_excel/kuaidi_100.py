# -*- coding: utf-8 -*-
'''
Created on 2016-11-22
@author: ghoti
'''
import time
from hashlib import md5
import json
import requests

class KuaiDi100(object):
    '''
       get express number via kuaidi100
       content important val:
           kuaidi_com:物流公司(zhongtong)，partnerId:月结账号
    '''
    def __init__(self, key=None, secret=None):
        self.key = key
        self.secret = secret

    def _sign(self, params):
        '''
        Generate API sign code
        '''
        src = params['param'] + params['t'] + self.key+self.secret      
        return md5(src).hexdigest().upper()

    def _get_timestamp(self):
        return str(time.time()).split('.')[0]

    def _get_content(self, content):
        return json.dumps(content)

    def _get_top_resp(self, url, params):
        try:
            r = requests.post(url, data=params)
            return r.json(), None
        except Exception, e:
            msg = "request error：kuaidi100 _get_top_resp e:%s" % e
            return None, msg

    def execute(self, API_address, method_name, content, **kwargs):
        params = {}
        params['key'] = self.key
        params['t'] = self._get_timestamp()
        params['param'] = self._get_content(content)
        params['sign'] = self._sign(params)
        params['method'] = method_name
        
        rsp, error_info = self._get_top_resp(API_address, params)
        if not rsp: 
            return None, error_info
        
        try :
            if rsp.get('result', None) and rsp['status'] == '200':
                return rsp, None
            else:
                return None, rsp['message']
        except Exception, e:
            msg = 'get message from rainbow fail.  e = %s  rsp = %s' % (str(e), str(rsp))
            return None, msg

    def __call__(self, API_address, method_name, content, **kwargs):
        return self.execute(API_address, method_name, content, **kwargs)
