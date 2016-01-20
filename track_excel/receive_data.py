#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""rabbitmq client to receive and do the data"""
from my_rabbitmq import RabbitMQ


def main():
    a = RabbitMQ()
    a.get_queue_list(queue_name='a')


if __name__ == '__main__':
    main()
