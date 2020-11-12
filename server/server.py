import time
import requests
from fpdf import FPDF
from clients3 import clientS3
from clientSQS import clientSQS

queue_urlInbox = 'https://sqs.us-east-1.amazonaws.com/093218148560/Inbox.fifo'
queue_urlOutbox = 'https://sqs.us-east-1.amazonaws.com/093218148560/Outbox.fifo'
s3client = clientS3('tickets-tsa')
sqsclient = clientSQS(queue_urlInbox,queue_urlOutbox)

while True:
    receivedAtts = False
    while not receivedAtts:
        receivedAtts = sqsclient.receiveMensage()
        time.sleep(3)
        print("Waiting")
        continue
    msg = sqsclient.formatMensage(receivedAtts)
    print(msg["Option"])
    if msg["Option"] == "buy":
        msg["Number"] =int(msg["Number"])
        order = s3client.buyTickets(msg["Title"],msg["Number"])
        if order == False:
            print("Order falsa")
            sqsclient.sendMessage(msg["IdentityToken"],"Error: We dont have tickets enought", "NoRecover")       
        else:
            print("Tickets bought")
            content = s3client.ticketContent(msg["IdentityToken"], msg["Title"], str(msg['Number']))
            filename = s3client.ticketFileName(msg["IdentityToken"], msg["Title"], str(msg['Number']))
            s3client.uploadTicketCopy(content, filename)
            url2download = s3client.create_presigned_URL('tickets-tsa', filename)
            sqsclient.sendMessage(msg["IdentityToken"],url2download , filename)       
    if msg["Option"] == "Recover":
        url2download = s3client.create_presigned_URL('tickets-tsa', msg["Title"])
        sqsclient.sendMessage(msg["IdentityToken"],url2download , msg["Title"])       


    #sqsclient.sendMessage("thistoken","This is response")
