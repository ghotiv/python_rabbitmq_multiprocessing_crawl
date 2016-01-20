#!/usr/bin/env python
# -*- encoding: utf-8 -*-
try:
    import json
except ImportError:
    import simplejson as json
import pika
import time
from do_track import do_track

# define config
# queque for mulitiprocessing
QUEUE_LIST = []
# rabbitmq server
HOST = '127.0.0.1'


class RabbitMQ():
    def __connect(self):
        """connet to rabbitmq server"""
        connection = pika.BlockingConnection(pika.ConnectionParameters(
               host=HOST))
        channel = connection.channel()
        self.connection = connection
        self.channel = channel

    def get_queue_list(self, queue_name=None, limit=2):
        """
            get queue list,if queque increase to limit,
            push to mulitiprocessing
        """
        if not queue_name:
            return None
        self.__connect()
        self.channel.queue_declare(queue=queue_name, durable=True)

        def callback(ch, method, properties, body):
            data = json.loads(body)
            global QUEUE_LIST
            QUEUE_LIST.append(data)
            if len(QUEUE_LIST) >= limit:
                do_track(data_list=QUEUE_LIST)
                QUEUE_LIST = []
                time.sleep(20)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_qos(prefetch_count=limit)
        self.channel.basic_consume(callback, queue=queue_name)
        self.channel.start_consuming()
        self.connection.close()
        return None

    def put_queue_list(self, queue_name=None, message_list=None):
        """put queue to list"""
        if not queue_name:
            return None
        try:
            if not message_list:
                return None
            if isinstance(message_list, dict):
                message_list = [message_list]
            self.__connect()
            self.channel.queue_declare(queue=queue_name, durable=True)
            for message in message_list:
                message = json.dumps(message)
                self.channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=message,
                    properties=pika.BasicProperties(delivery_mode=2, ))
            self.connection.close()
        except Exception as e:
            print e
            return None

    def qsize(self, queue_name=None):
        """get queue size"""
        if not queue_name:
            return 0
        try:
            self.__connect()
            ret = self.channel.queue_declare(queue_name, passive=True)
            qsize = ret.method.message_count
            self.connection.close()
            return qsize
        except Exception as e:
            print e
            return 0

    def purge(self, queue_name=None):
        """ clean queque """
        if not queue_name:
            return None
        try:
            self.__connect()
            self.channel.queue_declare(queue=queue_name, durable=True)
            return self.channel.queue_purge(queue_name)
        except Exception as e:
            print e
            return None
        finally:
            self.connection.close()
