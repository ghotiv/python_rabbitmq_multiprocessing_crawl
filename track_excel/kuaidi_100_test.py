#-*- coding: utf-8 -*-
'''
Created on 2016-11-22
@author: ghoti
'''
from kuaidi_100 import KuaiDi100
r = KuaiDi100('your key','your secret')
url = 'http://api.kuaidi100.com/eorderapi.do'

partnerId = ''
need_template = 1
kuaidi_com = 'zhongtong'

content={
    "recMan":{"name":"张文轩","mobile":"13641644555","tel":"","zipCode":"",
              "province":"吉林省","city":"长春市","district":"香洲区",\
              "addr":"翠香街道镜新二街56号凤凰公寓A座1201房","company":""},
    "sendMan":{"name":"	bjhgs","mobile":"15999542842","tel":"","zipCode":"",\
                "province":"北京","city":"北京市","district":"房山区","addr":\
                "青龙湖镇良坨路甲1号北京首诚农业花果山","company":"深圳**有限公司"},
    "kuaidicom":"%s"%kuaidi_com,"partnerId":"%s"%partnerId,"partnerKey":"",\
    "net":"","kuaidinum":"","orderId":"hgsA2147_test","payType":"SHIPPER",\
    "expType":"标准快递","weight":"1","volumn":"0","count":1,"remark":"备注",\
    "valinsPay":"0","collection":"0","needChild":"0","needBack":"0",\
    "cargo":"水果","needTemplate":"%s"%need_template
    }

rsp,error_info = r(url,'getElecOrder',content)
bulkpen = rsp['data'][0]['bulkpen']
kuaidinum = rsp['data'][0]['kuaidinum']
print bulkpen,kuaidinum
