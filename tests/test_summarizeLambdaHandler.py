import unittest
import boto3
from mypy_boto3_s3.client import S3Client
import sys
sys.path.append('.')
from summarize_lambda import lambda_handler


class TestLambdaHandler(unittest.TestCase):
    def setUp(self) -> None:
        # Copy sample transction file to s3 bucket
        s3:S3Client = boto3.client('s3')
        s3.upload_file("tests/testfiles/story.txt", 'smarctranscriptions', 'story.txt')
        return super().setUp()
    
    def test_lambda_handler(self):
        filename = "story.txt"
        event={'Records':[{'s3':{'object':{'key':filename},'bucket':{'name':'smarctranscriptions'}}}]}
        context = None
        result = lambda_handler(event, context)

        # Assert
        self.assertEqual(result['statusCode'], 200)
        self.assertTrue(f"has been transcribed" in result['body'])

    def tearDown(self) -> None:
        s3 = boto3.client('s3')
        s3.delete_object(Bucket='smarctranscriptions', Key='story.txt')
        # TODO s3.delete_object(Bucket='smarctranscriptions', Key='story_summary.txt')
        return super().tearDown()
 

if __name__ == '__main__':
    unittest.main()