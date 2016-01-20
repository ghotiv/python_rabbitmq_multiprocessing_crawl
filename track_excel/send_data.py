#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: ghoti
"""
from my_rabbitmq import RabbitMQ
from read_excel import Read_Excel
from track_data import IMPORT_EXCEL_PATH


def main():
    a = RabbitMQ()
    r = Read_Excel(file_name=IMPORT_EXCEL_PATH)()
    a.put_queue_list(queue_name='a', message_list=r)


if __name__ == '__main__':
    main()
