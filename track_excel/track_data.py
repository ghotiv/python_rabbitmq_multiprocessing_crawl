#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: ghoti
"""
import os
import time
import logging
from read_excel import Read_Excel, Export_Excel

# config args
STR_TODAY = time.strftime("%Y-%m-%d", time.localtime())
LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))
# put track.js in LOCAL_PATH
JS_PATH = os.path.join(LOCAL_PATH, 'track.js')
ERROR_DATA_PATH = os.path.join(LOCAL_PATH, 'error_data_%s.txt' % STR_TODAY)
SUCCESS_DATA_PATH = os.path.join(LOCAL_PATH, 'success_data_%s.txt' % STR_TODAY)
IMPORT_EXCEL_PATH = os.path.join(LOCAL_PATH, 'sample_import.xls')
SAVE_EXCEL_PATH = os.path.join(LOCAL_PATH, 'track_result.xls')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='track_%s.log' % STR_TODAY,
    filemode='a+')


# cost time for debug
def testtime(fun):
    def inner(*args, **kwargs):
        start = time.time()
        result = fun(*args, **kwargs)
        logging.info(u'cost time---------' + str(time.time() - start))
        return result

    return inner

# transfer way:
# 'USPS','AMSG','AMCH','AMNL','EMS','ENL','UPS','DHL','FEDEX','中俄快线','中英快线','澳洲快线','USPS-E','ZTO','SF'
url_dict = {
    'http://www.17track.net/zh-cn/result/post.shtml?nums=':
    ['AMSG', 'AMCH', 'AMNL', 'EMS', 'ENL'],
    'http://www.17track.net/zh-cn/track?fc=21051&nums=': ['USPS'],
    'http://www.17track.net/zh-cn/track?fc=100002&nums=': ['UPS', ],
    'http://www.17track.net/zh-cn/track?fc=100001&nums=': ['DHL', ],
    'http://www.17track.net/zh-cn/track?fc=100003&nums=': ['FEDEX', ],
    'http://www.17track.net/zh-cn/result/express-details-190004.shtml?nums=':
    [u'中俄快线', u'中英快线', u'澳洲快线'],
    'http://www.zto.cn/GuestService/Bill?txtbill=': ['ZTO'],
    'https://i.sf-express.com/new/cn/sc/waybillquery/waybillquery.html?queryWb=':
    ['SF'],
    'http://www.chukou1.com/LogistictsTrack.aspx?supplier=0&channeltype=0&trackNo=':
    ['USPS-E'],
}


def get_url_dict(data):
    d = {}
    d['transfer_way'] = data['transfer_way']
    d['logistic_sn'] = data['logistic_sn']
    d['id'] = data['id']
    for i, j in url_dict.items():
        if d['transfer_way'] in j:
            pre_url = i
            url = ''.join([pre_url, d['logistic_sn']])
            d['url'] = url
            return d
    return d


def get_list(file_name=None, limit=2000, data_list=[]):
    if data_list:
        return map(get_url_dict, data_list[:limit])
    if file_name:
        rows = []
        try:
            rows = Read_Excel(file_name=file_name)()
        except Exception, e:
            logging.info(u'read imprt excel error,' + str(e))
        check_data = rows[:limit]
        result = map(get_url_dict, check_data)
        return result
    return []


def write_list(data_from=SUCCESS_DATA_PATH, save_excel_path=SAVE_EXCEL_PATH):
    """write track info to excel"""
    f = open(data_from, 'r')
    track_info = []
    for i in f:
        track_info.append(eval(i))
    f.close()
    values = []
    headings = ['id', 'logistic_sn', 'transfer_way', 'track_state',
                'track_event', 'track_time']
    for track in track_info:
        values.append([track['id'], track['track_num'], track['transfer_way'],
                       track['track_state'], track['track_time'], track['track_event']])
    Export_Excel(headings, values, file_name=save_excel_path)()


if __name__ == '__main__':
    get_list(IMPORT_EXCEL_PATH)
