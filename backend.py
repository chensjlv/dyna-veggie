# -*- coding: utf-8 -*-
 """Memcached and in-memory cache result backend."""
 from __future__ import absolute_import
 
 from kombu.utils import cached_property
 from kombu.utils.url import _parse_url
 
 import boto3
 import logging
 import decimal
 from time import sleep
 
 from .base import KeyValueStoreBackend
 
 __all__ = ['DynamoDBBackend']
 
 
 class Client(object):
     """docstring for Client"""
 
     def __init__(self, url):
         super(Client, self).__init__()
         _, region_name, _, access_key, secret_key, table_name, _ = _parse_url(url)
         session = boto3.Session(
             aws_access_key_id=access_key,
             aws_secret_access_key=secret_key
         )
         dynamodb = session.resource('dynamodb', region_name=region_name)
         table = dynamodb.Table(table_name)
         self.table = table
         self.dynamodb = dynamodb
 
     def get(self, key):
         while True:
             response = self.table.get_item(
                 Key={
                     'id': key
                 },
                 ConsistentRead=True
             )
             item = response.get('Item')
             if item:
                 break
             else:
                 sleep(0.1)
         return item['result']
