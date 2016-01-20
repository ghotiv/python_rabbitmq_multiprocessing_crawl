#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: ghoti
"""
import xmlrpclib
import os
import json
import time
import datetime
import logging
from datetime import date
DEBUG = False
STR_TODAY = time.strftime("%Y-%m-%d", time.localtime())
str_today = time.strftime("%Y-%m-%d", time.localtime())
LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))
JSON_FILE_PATH = os.path.join(LOCAL_PATH, 'track_%s.json' % STR_TODAY)

if DEBUG:
    username = 'update_logistic'
    pwd = 'test1234'
    dbname = '######'
    host = 'http://192.168.5.45:8068'
    LIMIT = 2
else:
    username = 'update_logistic'
    pwd = '######'
    dbname = 'Seeed_ERP'
    host = 'http://192.168.1.117:8069'
    LIMIT = 20000


# cost time for debug
def testtime(fun):
    def inner(*args, **kwargs):
        start = time.time()
        result = fun(*args, **kwargs)
        logging.info(u'cost time---------' + str(time.time() - start))
        return result

    return inner


# log in the openerp use function then log out to shut the connect
# to avoid the full connection pool
def log_in_out(*logs, **kwlogs):
    def deco(func):
        def wrapper(*args, **kwargs):
            dbname, username, pwd, host = kwlogs['dbname'], kwlogs[
                'username'], kwlogs['pwd'], kwlogs['host']
            sock_common = xmlrpclib.ServerProxy('%s/xmlrpc/common' % host)
            uid = sock_common.login(dbname, username, pwd)
            sock = xmlrpclib.ServerProxy('%s/xmlrpc/object' % host)
            kwargs['sock'] = sock
            kwargs['uid'] = uid
            data = func(*args, **kwargs)
            sock_common.logout(dbname, username, pwd)
            return data

        return wrapper

    return deco

# transfer way:
# 'USPS','AMSG','AMCH','AMNL','EMS','ENL','UPS','DHL','FEDEX','中俄快线','中英快线','澳洲快线','USPS-E','ZTO','SF'
url_dict = {
    'http://www.17track.net/zh-cn/result/post.shtml?nums=':
    ['AMSG', 'AMCH', 'AMNL', 'EMS', 'ENL'],
    'http://www.17track.net/zh-cn/result/post.shtml?pt=1&cm=2105&nums=':
    ['USPS'],
    'http://www.17track.net/zh-cn/result/express-details-100002.shtml?nums=':
    ['UPS', ],
    'http://www.17track.net/zh-cn/result/express-details-100001.shtml?nums=':
    ['DHL', ],
    'http://www.17track.net/zh-cn/result/express-details-100003.shtml?nums=':
    ['FEDEX', ],
    'http://www.17track.net/zh-cn/result/express-details-190004.shtml?nums=':
    [u'中俄快线', u'中英快线', u'澳洲快线'],
    'http://www.zto.cn/GuestService/Bill?txtbill=': ['ZTO'],
    'https://i.sf-express.com/new/cn/sc/waybillquery/waybillquery.html?queryWb=':
    ['SF'],
    'http://www.chukou1.com/LogistictsTrack.aspx?supplier=0&channeltype=0&trackNo=':
    ['USPS-E'],
}


# use in openerp
def get_url_dict(l):
    d = {}
    d['transfer_way'] = l[2]
    d['logistic_sn'] = l[1]
    d['id'] = l[0]
    for i, j in url_dict.items():
        if d['transfer_way'] in j:
            pre_url = i
            url = ''.join([pre_url, d['logistic_sn']])
            d['url'] = url
            return d
    return d


def get_list_sql(limit=LIMIT, date_start=None, date_end=None):
    """
       get transfer data from openerp use xmlrpc
    """
    sql = """select cast(id as text) as id,logistic_sn,transfer_way
           from stock_seeed_delivery
           where state in ('traceable','partdone','done')
           and transfer_way not like '%自取%'
           and transfer_way is not NULL and logistic_sn is not NULL
           and transfer_way not in ('') and logistic_sn not in ('')
           and ((track_state not like '%成功签收%' and track_state not like '%已签收%')\
            or track_state is NULL)"""

    if (not date_start) and (not date_end):
        date_start = (
            date.today() - datetime.timedelta(60)).strftime('%Y-%m-%d')
    if date_start:
        sql += " and traceable_time >= '%s'" % date_start
    if date_end:
        sql += " and traceable_time <= '%s'" % date_end
    sql += 'LIMIT %s' % limit
    return sql


@log_in_out(dbname=dbname, username=username, pwd=pwd, host=host)
def get_list_rpc(limit=LIMIT,
                 date_start=None,
                 date_end=None,
                 sock=None,
                 uid=None):
    rows = []
    try:
        rows = sock.execute(dbname, uid, pwd, 'stock.seeed.delivery',
                            'get_list_rpc', limit, date_start, date_end)
    except Exception, e:
        logging.info(u'rpc get_list_rpc error,' + str(e))
    check_data = rows[:limit]
    result = map(get_url_dict, check_data)
    return result


@testtime
def getlist():
    return get_list_rpc()


@log_in_out(dbname=dbname, username=username, pwd=pwd, host=host)
def get_events(date_start=STR_TODAY, date_end=None, sock=None, uid=None):
    '''get the events from openerp'''
    args = []
    if date_start:
        args.append((('create_date', '>=', date_start)))
    if date_end:
        args.insert(0, ('create_date', '<=', date_end), )

    ids = sock.execute(dbname, uid, pwd, 'stock.seeed.delivery.event',
                       'search', args)
    fields = ['delivery_id']
    data = sock.execute(dbname, uid, pwd, 'stock.seeed.delivery.event', 'read',
                        ids, fields)
    all_delivery_ids = [i['delivery_id'][0] for i in data if i['delivery_id']]
    delivery_ids = list(set(all_delivery_ids))
    del_fields = ['logistic_sn', 'track_state']
    del_data = sock.execute(dbname, uid, pwd, 'stock.seeed.delivery', 'read',
                            delivery_ids, del_fields)
    track_info = del_data
    for track in track_info:
        del_id = track['id']
        track['track_state'] = get_en_event(track['track_state'])
        event_ids = sock.execute(dbname, uid, pwd,
                                 'stock.seeed.delivery.event', 'search', [(
                                     'delivery_id', '=', del_id)])
        event_fields = ['current_time', 'current_event']
        event_datas = sock.execute(
            dbname, uid, pwd, 'stock.seeed.delivery.event', 'read', event_ids,
            event_fields)
        track['track_all_event'] = event_datas
    return track_info


def get_en_event(s):
    dict_en = {u'成功签收': 'Delivered',
               u'查询不到': 'Not Found',
               u'天': 'Days',
               u'到达待取': 'Pick Up',
               u'运输途中': 'Trasnsporting'}
    if not s:
        return s
    for i, j in dict_en.items():
        s = s.replace(i, j)
    return s


@testtime
def create_track_json(date_start=STR_TODAY):
    """
        create track josn data,write to file for ftp
    """
    if os.path.exists(JSON_FILE_PATH):
        os.remove(JSON_FILE_PATH)
    events = get_events(date_start=date_start)
    json_data = json.dumps(events)
    f = open(JSON_FILE_PATH, 'w+')
    f.write(json_data)
    f.close()


if __name__ == '__main__':
    get_list_rpc()
