import boto3
import time
import json

class clientSQS:
    def __init__(self):
        self.sqsresource = boto3.resource('sqs')
        self.sqsclient = boto3.client('sqs')
        
    def set_urls(self, urlIn, urlOut):
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
            VisibilityTimeout=5,
            WaitTimeSeconds=0
        )
        try:
            message = response['Messages'][0]
            attributes = message['MessageAttributes']
            receipt_handle = message['ReceiptHandle']
            # Delete received message from queue
            self.sqsclient.delete_message(
                QueueUrl=self.urlInbox,
                ReceiptHandle=receipt_handle
            )
            #decoded = json.loads(message)
            print("Succesfull receiving")
            return attributes
        except Exception as e:
            print("No messages in the queue")
            return False


    def sendMessage(self,uuid, token, response, recover):
        # Send message to SQS queue
        body = str(time.time())+uuid
        response = self.sqsclient.send_message(
            QueueUrl=self.urlOutbox,
            MessageAttributes={
                'Response': {
                    'DataType': 'String',
                    'StringValue': response
                },
                'Recover': {
                    'DataType': 'String',
                    'StringValue': recover
                },
                'IdentityToken': {
                    'DataType': 'String',
                    'StringValue': token
                },
            },
            MessageGroupId='messageGroup1',
            MessageBody=(
                body
            )   
        )

    def formatMensage(self, msg):
        recIdentity = msg['IdentityToken']["StringValue"].replace("\n","")
        recTitle = msg['Title']["StringValue"].replace("\n","")
        recOption = msg['Option']["StringValue"].replace("\n","")
        recNUmber = msg['Number']["StringValue"].replace("\n","")
        mydict =dict(IdentityToken=recIdentity, Title=recTitle, Option=recOption, Number=recNUmber)
        return mydict