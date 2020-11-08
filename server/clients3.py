
from fpdf import FPDF
import textract
import requests
import time
import sys
import os
import boto3
import botocore.session
import botocore.exceptions
from botocore.exceptions import ClientError

sleeptimeRequest = 2
RestartBD = """
    Ariana Grande,1
    Justin Bieber,2
    Dua Lipa,3
    Lady Gaga,4
    Ed Sheeran,5
    Travis Scott,6
    Nicki Minaj,7
    Post Malone,8
"""

class clientS3:

    def __init__(self, bucket):
        self.s3client = boto3.client('s3')
        self.s3resource = boto3.resource('s3')
        self.bucket = bucket
        s3_client = boto3.client('s3')
        self.DatabaseTurn = False

    def create_presigned_URL(self, bucket_name, object_name, expiration=3600):
        try:
            response = self.s3client.generate_presigned_url('get_object',
                                                Params={'Bucket': bucket_name,
                                                        'Key': object_name},
                                                ExpiresIn=3600)
            return response
        except ClientError as e:
            logging.error(e)
            return e

    def download_from_aws(self, s3_file,local_file):
        self.s3resource.meta.client.download_file(self.bucket, s3_file, local_file)


    def upload_to_aws(self, local_file, s3_file):
        """
        Upload a <local_file> to the <bucket> with the name <s3_file>
        """
        try:
            self.s3client.upload_file(local_file, self.bucket, s3_file)
            print("Upload Successful: "+s3_file)
            return True
        except FileNotFoundError:
            print("The file was not found: "+local_file)
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False

    def ticketFileName(self,token, event, number):
        filename=token+event+number+".pdf"
        return filename

    def ticketContent(self,token, event, number):
        content = "User "+ token + " bought "+ number +"tickets for "+event
        return content

    def uploadTicketCopy(self, content, filename):
        self.generatePDF(content,filename)
        self.upload_to_aws(filename,filename)

    def applyDatabaseChanges(self, newDB):
        """
        Call this function at the end of Database modification because you will loose the turn
        """
        self.generatePDF(newDB, "Database.pdf")
        self.upload_to_aws("Database.pdf","Database.pdf")
        os.remove("Database.pdf")
        self.unlockDatabase()

    def delete_file(self, s3_file):
        response = self.s3client.delete_object(
            Bucket=self.bucket,
            Key=s3_file,
        )
        return response

    def existFile(self, filename):
        try:
            self.s3resource.Bucket(self.bucket).Object(filename).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                return e
        else:
            return True

    def formatDict(self, content):
        formatedContent = ""
        for key,value in content.items():
            formatedContent = formatedContent+key+","+str(value)+"\n"
        return formatedContent


    def generatePDF(self, content, outputname):
        if type(content) == dict:
            content=self.formatDict(content)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 14)  
        pdf.ln(10)
        #5 is the LineHeigh
        pdf.write(5, content)
        pdf.output(outputname, 'F')
        return pdf

    def lockDatabase(self):
        pdf = self.generatePDF("locked","temporalfile.lock")
        self.upload_to_aws('temporalfile.lock','Database.lock')
        os.remove('temporalfile.lock')

    def unlockDatabase(self):
        self.delete_file('Database.lock')

    def databaseIsLocked(self):
        return self.existFile('Database.lock')
    
    def getDatabaseTurn(self):
        while self.databaseIsLocked():
            print("Waiting turn")
            time.sleep(sleeptimeRequest)
        self.lockDatabase()

    def leaveDatabaseTurn(self):
        self.unlockDatabase()

    def formatFile(self, filename):
        raw = textract.process(filename) 
        content = raw.decode("utf-8")
        files = content.strip().split('\n')
        myDB = {"":""}
        for x in files:
            values = x.split(',')
            myDB[values[0].strip()]= int(values[1])
        del myDB[""]
        return myDB

    def getDatabase(self):
        self.getDatabaseTurn()
        self.download_from_aws('Database.pdf','Database.pdf')
        myDB = self.formatFile("Database.pdf")
        print(myDB)
        return myDB

    def ticketsEnough(self, dict, event, numerTickets):
        print("Wanna buy "+str(numerTickets)+" tickets of "+event+".")
        print(type(numerTickets))
        try:
            if dict[event] < int(numerTickets):
                return False
            else:
                return True
        except Exception as e:
            print("Error getting tickets: "+str(e))
            return False

    def buyTickets(self, event, numberTickets):
        myDB = self.getDatabase()
        if self.ticketsEnough(myDB, event, numberTickets):
            myDB[event] = myDB[event]- numberTickets
            self.applyDatabaseChanges(myDB)
            return True
        else:
            print("Not enought tickets")
            self.applyDatabaseChanges(myDB)
            return False

    def newTicket(self, nameFile, event, Number):
        print("Uploadingfile")
