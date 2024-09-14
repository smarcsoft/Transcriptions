import os
import unittest
import boto3
from mypy_boto3_s3 import S3Client
from watchdog.events import FileSystemEvent
import sys

if sys.platform == "win32":
    from watcher import FileEventHandler

credentials = {
            'access_key': os.environ.get('AWS_ACCESS_KEY_ID'),
            'secret_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
            'region': 'eu-west-1'
        }
s3_client: S3Client = boto3.client('s3', 
                            aws_access_key_id=credentials['access_key'],
                            aws_secret_access_key=credentials['secret_key'],
                            region_name=credentials['region'])
s3_bucket_name = 'smarctranscriptions'

class FileEventHandlerTest(unittest.TestCase):
    def setUp(self):
        if sys.platform == "win32":
            self.event_handler = FileEventHandler(s3_client, s3_bucket_name)

    def test_on_created(self):
        if sys.platform == "win32":
            e = FileSystemEvent("C:\\Users\\sebma\\Documents\\transcribe\\sample.m4a")
            self.event_handler.on_created(e)
            self.assertTrue(True)
        else:
            self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()