# -*- coding: utf-8 -*-
"""DynamoDB result backend."""

from __future__ import absolute_import, unicode_literals

from kombu.utils.objects import cached_property
from kombu.utils.url import _parse_url

from dyna_veggie.dynamodb_client import DynamoDBClient
from celery.backends.base import KeyValueStoreBackend

__all__ = ['DynamoDBBackend']


class DynamoDBBackend(KeyValueStoreBackend):

    # this backend supports native join with Dynamodb's atomic counter
    supports_native_join = True
    implements_incr = True
    supports_autoexpire = False

    def __init__(self, url=None, *args, **kwargs):
        super(DynamoDBBackend, self).__init__(*args, **kwargs)
        self.url = url

    def get(self, key):
        return self.client.get(key)

    def mget(self, keys):
        return self.client.mget(keys)

    def set(self, key, value):
        self.client.set(key, value)

    def delete(self, key):
        return self.client.delete(key)

    def _apply_chord_incr(self, header, partial_args, group_id, body, **opts):
        key = self.get_key_for_chord(group_id)
        self.client.set(key, 0)
        return super(DynamoDBBackend, self)._apply_chord_incr(
            header, partial_args, group_id, body, **opts)

    def incr(self, key):
        return self.client.incr(key)

    @cached_property
    def client(self):
        scheme, region, port, access_key, secret_key, table, query = \
            _parse_url(self.url)
        return DynamoDBClient(access_key, secret_key, region, port, table, query)
