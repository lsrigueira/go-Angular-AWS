
from fpdf import FPDF
from tika import parser
import sys
import os
import boto3
import botocore.session
import botocore.exceptions

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


    def upload_to_aws(self, local_file, s3_file):
        """
        Upload a <local_file> to the <bucket> with the name <s3_file>
        """
        
        try:
            self.s3client.upload_file(local_file, self.bucket, s3_file)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False

#uploaded = upload_to_aws('Database.pdf', 'tickets-tsa', 'Database.pdf')

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

    def lockDatabase(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 14)  
        pdf.ln(10)
        pdf.write(5, 'locked')
        pdf.output('temporalfile.lock', 'F')
        self.upload_to_aws('temporalfile.lock','Database.lock')
        os.remove('temporalfile.lock')

    def unlockDatabase(self):
        self.delete_file('Database.lock')

    def databaseIsLocked(self):
        return self.existFile('Database.lock')

    def formatFile(self, filename):
        raw = parser.from_file('Database.pdf')
        content = raw['content']
        files = content.strip().split('\n')
        myDB = {"":""}
        for x in files:
            values = x.split(',')
            myDB[values[0].strip()]= int(values[1])
        return myDB
