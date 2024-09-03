import unittest
import boto3
from mypy_boto3_s3.client import S3Client
from transcribe_lambda import lambda_handler

class TestLambdaHandler(unittest.TestCase):
    def setUp(self) -> None:
        # Copy sample transction file to s3 bucket
        s3:S3Client = boto3.client('s3')
        s3.upload_file("testfiles/sample.m4a", 'smarctranscriptions', 'sample.m4a')
        return super().setUp()
    
    def test_lambda_handler(self):
        filename = "https://smarctranscriptions.s3.eu-west-1.amazonaws.com/sample.m4a"
        # Arrange
        event = {
            "filename": filename
        }
        context = None
        result = lambda_handler(event, context)

        # Assert
        self.assertEqual(result['statusCode'], 200)
        self.assertTrue(f"File {filename} has been transcribed" in result['body'])
 

if __name__ == '__main__':
    unittest.main()