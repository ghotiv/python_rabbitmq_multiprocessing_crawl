#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
from ftplib import FTP
from track_data import logging, testtime
time_now = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
store_name = time_now + '.json'

str_today = time.strftime("%Y-%m-%d", time.localtime())
local_path = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(local_path, 'track_%s.json' % str_today)


@testtime
def ftp_up(filename=json_file_path, store_name=store_name):
    """"""
    ftp = FTP()
    # open the debug level,2.list the detail,0.shut debug
    ftp.set_debuglevel(2)
    ftp.connect('host', 'port')
    # login,if the user or password is none,use an empty string
    ftp.login('user', 'password')
    # set the buf size
    bufsize = 1024
    # open the read only file
    file_handler = open(filename, 'rb')
    # ftp up
    ftp.storbinary('STOR %s' % store_name, file_handler, bufsize)
    ftp.set_debuglevel(0)
    file_handler.close()
    ftp.quit()
    logging.info('ftp_up----------')
