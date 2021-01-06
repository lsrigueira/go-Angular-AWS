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
            print("Error receiving message: " +str(e))
            return False


    def sendMessage(self, token, response, recover):
        # Send message to SQS queue
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
                'Ola son o body e vou vacio'
            )   
        )

    def formatMensage(self, msg):
        recIdentity = msg['IdentityToken']["StringValue"].replace("\n","")
        recTitle = msg['Title']["StringValue"].replace("\n","")
        recOption = msg['Option']["StringValue"].replace("\n","")
        recNUmber = msg['Number']["StringValue"].replace("\n","")
        mydict =dict(IdentityToken=recIdentity, Title=recTitle, Option=recOption, Number=recNUmber)
        return mydict