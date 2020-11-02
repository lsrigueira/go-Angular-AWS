import time
from clients3 import clientS3
from clientSQS import clientSQS

queue_urlInbox = 'https://sqs.us-east-1.amazonaws.com/093218148560/Inbox.fifo'
queue_urlOutbox = 'https://sqs.us-east-1.amazonaws.com/093218148560/Outbox.fifo'


s3client = clientS3('tickets-tsa')
sqsclient = clientSQS(queue_urlInbox,queue_urlOutbox)
received = False
while not received:
    received = sqsclient.receiveMensage()
    time.sleep(3)
    print(received)
"""
while True:
    if s3client.databaseIsLocked():
        print("locked")
        time.sleep(3)
    else:
        print("unlocking")
        s3client.lockDatabase()
"""
