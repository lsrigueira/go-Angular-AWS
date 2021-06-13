import time
import uuid
from botocore.exceptions import ClientError
import requests
from fpdf import FPDF
from clients3 import clientS3
from clientSQS import clientSQS
import logging

logger = logging.getLogger(__name__)
s3client = clientS3('tickets-tsa')
def get_queue(name):
    """
    Gets an SQS queue by name.

    Usage is shown in usage_demo at the end of this module.

    :param name: The name that was used to create the queue.
    :return: A Queue object.
    """
    try:
        queue = sqsclient.sqsresource.get_queue_by_name(QueueName=name)
        logger.info("Got queue '%s' with URL=%s", name, queue.url)
    except ClientError as error:
        logger.exception("Couldn't get queue named %s.", name)
        raise error
    else:
        return queue

def servir():
    while True:
        receivedAtts = False
        while not receivedAtts:
            print("Waiting...")
            receivedAtts = sqsclient.receiveMensage()
            time.sleep(3)
            continue
        msg = sqsclient.formatMensage(receivedAtts)
        print(msg["Option"])
        if msg["Option"] == "buy":
            msg["Number"] =int(msg["Number"])
            order = s3client.buyTickets(msg["Title"],msg["Number"])
            if order == False:
                print("Order falsa")
                sqsclient.sendMessage(uuid, msg["IdentityToken"],"Error: We dont have tickets enought", "NoRecover")       
            else:
                print("Tickets bought")
                content = s3client.ticketContent(msg["IdentityToken"], msg["Title"], str(msg['Number']))
                filename = s3client.ticketFileName(msg["IdentityToken"], msg["Title"], str(msg['Number']))
                s3client.uploadTicketCopy(content, filename)
                url2download = s3client.create_presigned_URL('tickets-tsa', filename)
                sqsclient.sendMessage(uuid, msg["IdentityToken"],url2download , filename)       
        if msg["Option"] == "Recover":
            url2download = s3client.create_presigned_URL('tickets-tsa', msg["Title"])
            sqsclient.sendMessage(uuid, msg["IdentityToken"],url2download , msg["Title"])       


    #sqsclient.sendMessage("thistoken","This is response")
sqsclient = clientSQS()
queue_urlInbox = get_queue("Inbox.fifo").url#'https://sqs.us-east-1.amazonaws.com/093218148560/Inbox.fifo'
queue_urlOutbox = get_queue("Outbox.fifo").url#'https://sqs.us-east-1.amazonaws.com/093218148560/Outbox.fifo'
sqsclient.set_urls(queue_urlInbox,queue_urlOutbox)
uuid = uuid.uuid4().hex
servir()
