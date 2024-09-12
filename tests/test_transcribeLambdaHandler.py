import unittest
import boto3
from mypy_boto3_s3.client import S3Client
import sys
sys.path.append('.')
from transcribe_lambda import lambda_handler


class TestLambdaHandler(unittest.TestCase):
    def setUp(self) -> None:
        # Copy sample transction file to s3 bucket
        s3:S3Client = boto3.client('s3')
        s3.upload_file("tests/testfiles/sample.m4a", 'smarctranscriptions', 'sample.m4a')
        return super().setUp()
    
    def test_lambda_handler(self):
        filename = "sample.m4a"
        
        event={'Records':[{'s3':{'object':{'key':filename},'bucket':{'name':'smarctranscriptions'}}}]}
        context = None
        result = lambda_handler(event, context)
        print(result)
        self.assertEqual(result['statusCode'], 200)

    def tearDown(self) -> None:
        s3 = boto3.client('s3')
        s3.delete_object(Bucket='smarctranscriptions', Key='sample.m4a')
        s3.delete_object(Bucket='smarctranscriptions', Key='sample.txt')
        return super().tearDown()
 

if __name__ == '__main__':
    unittest.main()