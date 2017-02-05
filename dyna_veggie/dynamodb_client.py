import decimal
from time import sleep

import boto3
from boto3.dynamodb.types import Binary
from retrying import retry
from botocore.exceptions import ClientError


def retry_if_throttled(exception):
    """
    Return True if we should retry, in this case when it's an ProvisionedThroughputExceededException, False otherwise
    """
    if hasattr(exception, 'message'):
        if isinstance(exception, ClientError) and 'ProvisionedThroughputExceededException' in exception.message:
            return True
        else:
            return False
    else:
        return False


def dynamodb_retry():
    """
    Wait 2^x * 1000 milliseconds between each retry, up to 10 seconds, then 10 seconds afterwards
    Retry 5 times if an ProvisionedThroughputExceededException occurs, raise any other errors wrapped in RetryError
    """
    return retry(
        retry_on_exception=retry_if_throttled,
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
        stop_max_attempt_number=5
    )


class DynamoDBClient(object):
    """docstring for DynamoDBClient"""

    def __init__(self, access_key, secret_key, region_name, table_name):
        super(DynamoDBClient, self).__init__()
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        dynamodb = session.resource('dynamodb', region_name=region_name)
        table = dynamodb.Table(table_name)
        self.table = table
        self.table_name = table_name
        self.dynamodb = dynamodb
        self.consistency_wait_time = 1  # seconds

    @dynamodb_retry()
    def _get_item(self, **kwargs):
        response = self.table.get_item(**kwargs)
        return response

    @dynamodb_retry()
    def __batch_get_item(self, **kwargs):
        response = self.dynamodb.batch_get_item(**kwargs)
        return response

    @dynamodb_retry()
    def _put_item(self, **kwargs):
        response = self.table.put_item(**kwargs)
        return response

    @dynamodb_retry()
    def _delete_item(self, **kwargs):
        response = self.table.delete_item(**kwargs)
        return response

    @dynamodb_retry()
    def _update_item(self, **kwargs):
        response = self.table.update_item(**kwargs)
        return response

    def get(self, key):
        """
        Get the item by key until it shows up in Dynamodb or fail when it exceeds max wait time.
        We wait 0.1 second to retry if item does not present in DynamoDB.
        Why do we need this? Because of network latency and read consistency,
        http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html
        Why can't we just use ConsistentRead=True? Because the get request has the potential to 
        reach to DynamoDB faster than a set request reaches it, if the set and get requests are 
        issued on different machines/processes. Thus the only way to ensure we can get item in a 
        distributed setting is to retry.
        """
        not_presented = True
        wait_time = 0
        max_wait_time = self.consistency_wait_time
        gap = 0.1  # second

        while not_presented and wait_time <= max_wait_time:
            response = self._get_item(
                Key={
                    'id': key
                },
                ConsistentRead=False
            )
            item = response.get('Item')
            if item:
                not_presented = False
            else:
                # sleep for a while if the item does not present in dynamodb
                sleep(gap)
                wait_time += gap
        return item['result']

    def _batch_get_item(self, keys):
        result = []
        remaining_keys = [{'id': key} for key in keys]
        still_has_unprocessed = True

        # dynamodb does not promise to get all items at once if it exceeds the
        # api limit, read until there are no unprocessed keys left in response
        while still_has_unprocessed:
            response = self.__batch_get_item(
                RequestItems={
                    self.table_name: {
                        'Keys': remaining_keys,
                        'ConsistentRead': False,
                    }
                }
            )
            batch_result = [r['result']
                            for r in response['Responses'][self.table_name]]
            result.extend(batch_result)
            if response.get('UnprocessedKeys'):
                remaining_keys = response['UnprocessedKeys'][
                    self.table_name]['Keys']
            else:
                still_has_unprocessed = False
        return result

    def _partition_chunks(self, items, size):
        """partition items into chunks of certain size"""
        for x in xrange(0, len(items), size):
            yield items[x:x + size]

    def mget(self, keys):
        result = []
        # dynamodb supports batch size of 100 in maximum
        chunks = self._partition_chunks(keys, 100)
        for chunk in chunks:
            result.extend(self._batch_get_item(chunk))
        return result

    def set(self, key, value):
        """
        Boto3 does not handles unicode encoding and decoding well with pickled string.
        Storing them as binary data type solves the problems.
        """
        if isinstance(value, basestring) or isinstance(value, bytearray):
            return self._put_item(
                Item={
                    'id': key,
                    'result': Binary(value)
                }
            )
        else:
            return self._put_item(
                Item={
                    'id': key,
                    'result': value
                }
            )

    def delete(self, key):
        """delete item by key"""
        return self._delete_item(
            Key={
                'id': key
            }
        )

    def incr(self, key):
        """Increase atomic counter by 1 for the key"""
        response = self._update_item(
            Key={
                'id': key
            },
            UpdateExpression="set #r = #r + :val",
            ExpressionAttributeNames={
                '#r': 'result'
            },
            ExpressionAttributeValues={
                ':val': decimal.Decimal(1)
            },
            ReturnValues="UPDATED_NEW"
        )
        return response['Attributes']['result']
