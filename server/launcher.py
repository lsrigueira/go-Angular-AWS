import logging
import sys
import boto3
from botocore import args
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)
sqs = boto3.resource('sqs')
sqsclient = boto3.client('sqs')
s3 = boto3.client('s3')

def create_queue(name, attributes=None):

    if not attributes:
        attributes = {
            'MessageRetentionPeriod':'60',
            'ReceiveMessageWaitTimeSeconds':'20',
            'FifoQueue':'true',
            'ContentBasedDeduplication':'true'
        }

    try:
        queue = sqs.create_queue(
            QueueName=name,
            Attributes=attributes
        )
        logger.info("Created queue '%s' with URL=%s", name, queue.url)
    except ClientError as error:
        logger.exception("Couldn't create queue named '%s'.", name)
        raise error
    else:
        return queue

def remove_queue(queue):
    """
    Removes an SQS queue. When run against an AWS account, it can take up to
    60 seconds before the queue is actually deleted.

    Usage is shown in usage_demo at the end of this module.

    :param queue: The queue to delete.
    :return: None
    """
    try:
        queue.delete()
        logger.info("Deleted queue with URL=%s.", queue.url)
    except ClientError as error:
        logger.exception("Couldn't delete queue with URL=%s!", queue.url)
        raise error

def get_queues(prefix=None):
    """
    Gets a list of SQS queues. When a prefix is specified, only queues with names
    that start with the prefix are returned.

    Usage is shown in usage_demo at the end of this module.

    :param prefix: The prefix used to restrict the list of returned queues.
    :return: A list of Queue objects.
    """
    if prefix:
        queue_iter = sqs.queues.filter(QueueNamePrefix=prefix)
    else:
        queue_iter = sqs.queues.all()
    queues = list(queue_iter)
    if queues:
        logger.info("Got queues: %s", ', '.join([q.url for q in queues]))
    else:
        logger.warning("No queues found.")
    return queues

def remove_all_queues():
    myqueues = get_queues()
    for thisqueue in myqueues:
        try:
            remove_queue(thisqueue)
        except e:
            print("No queue named: "+thisqueue)


def create_bucket():
    s3.create_bucket(
        Bucket='tickets-tsa',
        ACL='public-read'
    )
    s3.upload_file("./Descargado/Database.pdf", 'tickets-tsa', 'Database.pdf')

def delete_bucket():
    s3.delete_bucket(
        Bucket='tickets-tsa',
    )

def clean_queues():
    for i in get_queues():
        sqsclient.purge_queue(QueueUrl= i.url)

args=sys.argv
if len(args) != 2:
    print(
        """Comando incorrecto. 
        \n\t start: Crea los componentes e inicia el sistema
        \n\t stop: Apaga y borra los componentes
        \n\t clean: Borra los mensages de las colas
        """
    )
    sys.exit(0)
print(args[0])
if args[1].lower() == "start":
    create_queue("Inbox.fifo")
    create_queue("Outbox.fifo")
    create_bucket()
elif args[1].lower() == "clean":
    clean_queues()
else:
    remove_all_queues()
    delete_bucket()

    