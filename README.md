# Dyna-Veggie
Dyna-Veggie is the first fully compatible **DynamoDB result backend for Celery**. It supports both supports both DynamoDB in AWS and DynamoDB Local. Dyna-Veggie also supports these features out of the box:

* Fully suports **Native join operation** in Celery just like the Redis backend, which bring the best performance for canvas operations like chord and group. 
* Uses batch get for retrieving large amount of items which provides much better performance than sequential gets.
* Automatically creates the table if not presented
* Allows customizable options for DynamoDB throttling retry and exponential backoff
* Handles DynamoDB's consistency issue appropriately

# Installation

You can install Dyna-Veggie either via the Python Package Index (PyPI) or from source.

To install using pip:

```bash
$ pip install -U dyna-veggie
```

# Get Started
To use Dyna-Veggie in your celery project is simple. All you need to do is:

1. Install dyna-veggie through pip
2. Add the following to your celery config file, and **Enjoy!**:

```python
# celeryconfig.py maybe?

from dyna_veggie import DynamoDBBackend

result_backend = DynamoDBBackend
# instead of using backend url to config backend, 
# we use a dictionary named dynamodb_backend_settings
dynamodb_backend_settings = {
    "access_key": "your aws account's access key",
    "secret_key": "your aws account's secret key",
    "region": "us-east-1",  # AWS region your DynamoDB table's in
    "table": "celery",  # Optional. DynamoDB table for storing results. Default to celery
    "port": 8000,  # Optional unless you use DynamoDBLocal
    "read_throughput": 5,  # Optional. Default to 5
    "write_throughput": 5,  # Optional. Default to 5
    "retry_if_throttled": True,  # Optional. Default to True
    "consistency_wait_time": 1,  # Optional. Seconds to wait for data consistency
}
```

## Settings

### access_key & secret_key

The credentials for accessing AWS API resources. These can also be resolved by the [boto3](https://boto3.readthedocs.io/en/latest/) library from various sources, as described [here](http://boto3.readthedocs.io/en/latest/guide/configuration.html#configuring-credentials).

### region

The AWS region, e.g. us-east-1 or **local** for DynamoDB Local. See the [boto3](https://boto3.readthedocs.io/en/latest/) library documentation for definition options.

### port

The listening port of the local DynamoDB instance, if you are using the DynamoDB Local. If you have not specified the region parameter as **local**, setting this parameter has no effect.

### table

Table name to use. Default is celery. See the DynamoDB Naming Rules for information on the allowed characters and length.

### read_throughput & write_throughput

The Read & Write Capacity Units for the created DynamoDB table. Default is 5 for both read and write. More details can be found in the [Provisioned Throughput documentation](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ProvisionedThroughput.html).

### retry_if_throttled

Whether to retry is the throttling exception is raised. Exponential backoff is used in the retry operations. More parameters for the exponential backoff behavior will be allowed to be customized in future version. Default to True.

### consistency_wait_time

Seconds to wait for data to become consistent before the backend thinks the data is not available. Why do we need this? Because of network latency and [read consistency](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html). Why can't we just set ConsistentRead to True? Because the get request has the potential to reach to DynamoDB faster than a set request reaches it, if the set and get requests are issued on different machines/processes. Thus the only way to ensure we can get item in a distributed setting is to retry. Default to 1, because typically 1 second is enough for the data to present.

# License

Apache License, Version 2.0
