import boto3
import time
import json

class clientSQS:
    def __init__(self, urlIn, urlOut):
        self.sqsclient = boto3.client('sqs')
        self.urlInbox = urlIn
        self.urlOutbox = urlOut

    def receiveMensage(self):
        # Receive message from SQS queue
        response = self.sqsclient.receive_message(
            QueueUrl=self.urlInbox,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )
        try:
            print("RECEIVING")
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']

            # Delete received message from queue
            self.sqsclient.delete_message(
                QueueUrl=self.urlInbox,
                ReceiptHandle=receipt_handle
            )
            #decoded = json.loads(message)
            return 'Received and deleted message: %s' % ola
        except Exception as e:
            return False


    def sendMessage(self):
        # Send message to SQS queue
        response = self.sqsclient.send_message(
            QueueUrl=self.urlOutbox,
            DelaySeconds=10,
            MessageAttributes={
                'Response': {
                    'DataType': 'String',
                    'StringValue': 'TU NO SABES NADA'
                },
                'IdentityToken': {
                    'DataType': 'String',
                    'StringValue': 'MyIdentity'
                },
            },
            MessageBody=(
                'Information about current NY Times fiction bestseller for '
                'week of 12/11/2016.'
            )
        )
    """
    while True:
        try:
            message = receiveMensage()
            sendMessage()
        except KeyError as e:
            print("There are no messages in the queu:  ", e)
            time.sleep(5)
    """