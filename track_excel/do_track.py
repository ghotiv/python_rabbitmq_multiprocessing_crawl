#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: ghoti
the main function
get the data from excel and crawl from website then write to excel,
"""
import sys
import os
import re
import datetime
import multiprocessing
import requests
from lxml import etree
from my_process_pool import LoggingPool
from track_data import get_list, testtime, logging
from track_data import JS_PATH, ERROR_DATA_PATH
from track_data import SUCCESS_DATA_PATH, IMPORT_EXCEL_PATH

reload(sys)
sys.setdefaultencoding('utf8')

# xpth to parse the html
p_xpath = {
    'p_packState': ".//*[@class='track-infos']/span",
    'p_lastEvent': ".//*[@class='col-summary']",
    'p_allEvent': ".//*[@id='jsResultList']/section/div/dl/dd",
    'p_zto_lastEvent': ".//*[@class='pr firstChild current1']",
    'p_zto_allEvent': ".//*[@class='state']/ul/li",
    'p_sf_lastEvent': ".//*[@class='waybillTit']/td[2]",
    'p_sf_allEvent': ".//*[@class='routeList']/dd",
    'p_ck_state':
    ".//*[@class='table table-bordered orders']/tbody[1]/tr[1]/td[3]",
    'p_ck_lastEvent': ".//*[@class='table table-striped']/tbody/tr[2]",
    'p_ck_allEvent':
    ".//*[@class='table table-striped']/tbody/tr[position()>1]",
}


def get_strftime(s):
    """get date from text"""
    pat = r'\d{4}(?:-|年|/){1}\d{1,2}(?:-|月|/){1}\d{1,2}(?:-|日|/){,1}(?:\s\d{1,2}:\d{1,2}(?:\:\d{1,2}){,1}){0,1}'
    find_list = re.findall(pat, s)
    time_s = (find_list and [find_list[0]] or [''])[0]
    strf_time = (time_s and [datetime.datetime(*map(int, re.findall(
        '(\d+)', time_s))[:6])] or [''])[0]
    return strf_time


def del_time(s):
    """remove date from text"""
    pat = r"\d{4}(?:-|年|/){1}\d{1,2}(?:-|月|/){1}\d{1,2}(?:-|日|/){,1}(?:\s\d{1,2}:\d{1,2}(?:\:\d{1,2}){,1}){0,1},?"
    find_list = re.findall(pat, s)
    time_s = (find_list and [find_list[0]] or [''])[0]
    return s.replace(time_s, '').replace('.', '', 1).strip()


def get_all_event(all_event, reverse=False):
    """get all event"""
    if not all_event:
        return []
    list_all_event = []
    all_event_list = all_event.split('\n')
    if reverse:
        all_event_list.reverse()
    for i in all_event_list:
        dict_one = {}
        current_time, current_event = str(get_strftime(i)), del_time(i)
        if current_time:
            dict_one['current_time'] = current_time
        current_event = current_event.decode('utf-8', 'ignore').encode('utf-8')
        dict_one['current_event'] = current_event
        if dict_one.get('current_time', None) or dict_one.get('current_event',
                                                              None):
            list_all_event.append(dict_one)
    return list_all_event


def get_ck_event(tree, pattern, encoding='raw_unicode_escape'):
    """get the event from schukou1.com"""
    nodes = tree.xpath(pattern)
    if nodes:
        track_all_event = []
        for node in nodes:
            time_s = node.xpath('.//td[1]')
            current_time = etree.tostring(
                time_s[0],
                encoding=encoding,
                method='text').replace('\r\n', ' ').replace('\n', ' ').strip()
            events = node.xpath('.//td[position()>1]')
            text = ' '.join(
                [etree.tostring(event,
                                encoding=encoding,
                                method='text').replace('\r\n', ' ').replace(
                                    '\n', ' ').strip() for event in events])
            track_event = {}
            track_event['current_time'] = current_time
            track_event['current_event'] = text.decode(
                'utf-8', 'ignore').encode('utf-8')
            track_all_event.append(track_event)
        return track_all_event
    else:
        return []


def get_pattern_text(tree, pattern, encoding):
    """get the node text of tree"""
    nodes = tree.xpath(pattern)
    if nodes:
        if len(nodes) == 1:
            text = etree.tostring(nodes[0], encoding=encoding, method='text')
        if len(nodes) > 1:
            text = '\n'.join([etree.tostring(node,
                                             encoding=encoding,
                                             method='text') for node in nodes])
        return text
    else:
        return ''


def get_file_list():
    """get the fail data then remove the error file"""
    if os.path.exists(ERROR_DATA_PATH):
        fp_data = open(ERROR_DATA_PATH, 'r')
        result = []
        for l in fp_data.readlines():
            result.append(eval(l))
        fp_data.close()
        os.remove(ERROR_DATA_PATH)
        return result


def get_result(d, time_out=60000):
    """
        use requests or casperjs to get website html code,
        then parse,get the transfer result
    """
    state, last_event, list_all_event, track_time = '', '', '', ''
    try:
        if d['transfer_way'] in ['ZTO', ]:
            html = requests.get(d['url'], timeout=6).content
        else:
            cmd = '/usr/local/bin/casperjs "%s" "%s" "%s" ' % (
                JS_PATH, d['url'], time_out)
            r = os.popen(cmd)
            html = r.read()
            r.close()
    except Exception, e:
        logging.info(u'get html fail,' + str(e))
        return ''

    if not html:
        return
    try:
        tree = etree.HTML(html)
    except:
        return ''

    # use xpath to parse the html,get transfer result
    if d['transfer_way'] in ['ZTO', 'SF']:
        p_lastEvent = p_xpath['p_zto_lastEvent'] if d[
            'transfer_way'] == 'ZTO' else p_xpath['p_sf_lastEvent']
        p_allEvent = p_xpath['p_zto_allEvent'] if d[
            'transfer_way'] == 'ZTO' else p_xpath['p_sf_allEvent']
        last_event = get_pattern_text(
            tree,
            p_lastEvent,
            encoding='utf-8').replace('\r\n', ' ').replace('\n', ' ').replace(
                '   ', '').strip()
        all_event = get_pattern_text(tree, p_allEvent, encoding='utf-8')
        if (u'签收人' in last_event) or (u'已签收' in last_event)\
                or (u'草签' in last_event) or (u'已收取' in last_event)\
                or (u'已入库' in last_event) or (u'提货' in last_event):
            state = u'已签收'.encode('utf-8')
        else:
            state = ''
        list_all_event = get_all_event(all_event, reverse=True)
        track_time = str(get_strftime(last_event))

    if d['transfer_way'] in ['USPS-E']:
        state = get_pattern_text(tree, p_xpath['p_ck_state'],
                                 'raw_unicode_escape').replace(
                                     '\r\n', ' ').replace('\n', ' ').strip()
        list_all_event = get_ck_event(tree, p_xpath['p_ck_allEvent'],
                                      'raw_unicode_escape')
        if state == 'Delivered':
            state = u'成功签收'
        track_time = list_all_event and list_all_event[0]['current_time'] or ''
        last_event = list_all_event and (
            list_all_event[0]['current_time'] + ' ' +
            list_all_event[0]['current_event'])

    elif d['transfer_way'] in ['USPS', 'AMSG', 'AMCH', 'AMNL', 'EMS', 'ENL',
                               'DHL', 'UPS', 'FEDEX', u'中俄快线', u'中英快线', u'澳洲快线']:
        state = get_pattern_text(tree,
                                 p_xpath['p_packState'],
                                 encoding='raw_unicode_escape')
        last_event = get_pattern_text(tree,
                                      p_xpath['p_lastEvent'],
                                      encoding='raw_unicode_escape')
        all_event = get_pattern_text(tree,
                                     p_xpath['p_allEvent'],
                                     encoding='raw_unicode_escape')
        list_all_event = get_all_event(all_event)
        track_time = str(get_strftime(last_event))

    result = {}
    result['track_num'], result['track_time'] = d['logistic_sn'], track_time
    result['track_state'], result['track_event'], result[
        'track_all_event'] = state, last_event, list_all_event
    return result


def create_event(success_q, error_q):
    """get data from success_q,write to excel"""
    fp_success = open(SUCCESS_DATA_PATH, 'a+')
    fp_error = open(ERROR_DATA_PATH, 'a+')
    logging.info(u'total,success:%s，fail:%s' %
                 (str(success_q.qsize()), str(error_q.qsize())))
    error_list = []
    while not error_q.empty():
        error_list.append(error_q.get())
        error_str = '\n'.join([str(i) for i in error_list])
        fp_error.write(error_str + '\n')
        error_list = []
    fp_error.close()

    success_list = []
    success_count = 0
    while not success_q.empty():
        success_list.append(success_q.get())
        success_count += 1
        if success_count >= 200 or success_q.empty():
            success_file_str = '\n'.join([str(i) for i in success_list])
            fp_success.write(success_file_str + '\n')
            success_count = 0
            success_list = []
            logging.info(u'create event result;')
    fp_success.close()


def data_handle(data, success_q, error_q, time_out=15000):
    """get the crawl result,and debug"""
    for i, d in enumerate(data):
        try:
            result = get_result(d, time_out)
            logging.info(result)
        except Exception, e:
            d['error_reason'] = 'Exception' + str(e)
            error_q.put(d)
            continue

        if result:
            if result['track_event'] or result['track_state']:
                result['id'] = d['id']
                result['transfer_way'] = d['transfer_way']
                success_q.put(result)
            else:
                d['error_reason'] = 'no_data'
                error_q.put(d)

        else:
            d['error_reason'] = 'no_html'
            error_q.put(d)


@testtime
def do_process(process_num=8,
               time_out=20000,
               data_list=None,
               file_name=IMPORT_EXCEL_PATH):
    """
        use multiprocessing to do the data,
        then create_event,write to txt,
    """
    # get data from excel
    if data_list:
        logging.info(u'get the logistic data from rabbitmq')
        data_list = get_list(data_list=data_list)
    else:
        logging.info(u'get the logistic data from excel')
        data_list = get_list(file_name=file_name)

    # use multiprocessing
    length = len(data_list)
    logging.info(u'total data length:%s' % str(length))
    if length <= process_num:
        process_num = 1
    step = (length / process_num) or 1
    nloop = range(0, length, step)
    if len(nloop) == process_num:
        nloop.append(length)
    elif len(nloop) == process_num + 1:
        nloop[-1] = length
    pool = LoggingPool(processes=process_num)
    error_q = multiprocessing.Manager().Queue()
    success_q = multiprocessing.Manager().Queue()
    for i, n in enumerate(nloop):
        if i < len(nloop):
            data = data_list[n:n + step]
            pool.apply_async(data_handle, (data,
                                           success_q,
                                           error_q,
                                           time_out, ))
    pool.close()
    pool.join()

    # write to txt
    create_event(success_q, error_q)


@testtime
def do_track(data_list=None, file_name=IMPORT_EXCEL_PATH):
    """
        get the data from excel then crawl,write to success file
        then read success file,write to excel
    """
    logging.info('do_process---------------')
    do_process(process_num=8,
               time_out=60000,
               data_list=data_list,
               file_name=IMPORT_EXCEL_PATH)
    logging.info('finally done--------------')


if __name__ == '__main__':
    do_track(file_name=IMPORT_EXCEL_PATH)
