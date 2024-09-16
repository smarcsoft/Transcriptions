from summarize import summarize_text
import logging
import json
import boto3
from mypy_boto3_s3.client import S3Client
import os
import tempfile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_content(file_url:str, bucket:str)->str:
    """
    Get the content of a file from a URL.
    Args:
        file_url (str): The URL of the file.
    Returns:
        str: The content of the file.
    Raises:
        Exception: If an error occurs while getting the content.
    """
    try:
        logger.info(f"Getting content from {file_url}")
        s3 = boto3.client('s3')
        key = '/'.join(file_url.split('/')[3:])
        logger.info(f"Getting object {key} from bucket {bucket}")
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        logger.info(f"Content retrieved from {file_url}")
        return content
    except Exception as e:
        logger.error(f"Error getting content from {file_url}: {e}")
        raise e
    

def lambda_handler(event, context):
    """
    Lambda function handler for summarization.
    Args:
        event (dict): The event data passed to the Lambda function.
            Each event is a dictionary with the following structure:
            {
                "files": [
                    {
                        "bucket": "XXXXXXXXXXX",
                        "inputfile": "file-name" where file-name is the name of the file to be summarized in an S3 bucket
                    }
                ]
            }
        context (object): The runtime information of the Lambda function.
    Returns:
        dict: The response object containing the status code.
    Raises:
        Exception: If an error occurs during the transcription.
    """

    try:
        logger.debug(f"Handler started with event: {event}")
        file_list:list = event['files']
        logger.info(f"Starting summarization lambda function with {len(file_list)} files to summarize")
        for file in file_list:
            file_url = file["inputfile"]
            logging.info(f"Summarizing file {file_url}")
            # Check if the file is an audio file
            if not file_url.lower().endswith(('.txt')):
                logger.warning(f"File {file_url} is not a text file. Skipping...")
                continue
            # The key might be URL encoded, so we may need to decode it
            # OUTPUT_FILE_NAME will contain the relative name with its extension as text
            OUTPUT_FILE_NAME = file_url.rsplit("/", 1)[1].split(".")[0] + "_summary.txt"
            TMP_DIR = tempfile.gettempdir()
            TMPFILE = os.path.join(TMP_DIR, OUTPUT_FILE_NAME)
            logger.info(f"Summarizing {file_url} into {OUTPUT_FILE_NAME}")
            bucket = file["bucket"]
            content = get_content(file_url, bucket)
            summary = summarize_text(content)
            with open(TMPFILE, 'w') as tmpfile:
                tmpfile.write(summary)
            logging.info(f"Summarization saved to file: {TMPFILE}")
            logging.info(f"Pushing summarization to S3 bucket with key {OUTPUT_FILE_NAME}")
            s3:S3Client = boto3.client('s3')

            logging.info(f"Uploading {TMPFILE} to bucket {bucket}")
            s3.upload_file(TMPFILE, bucket, f'{OUTPUT_FILE_NAME}')
            logging.info(f"{TMPFILE} has been uploaded to bucket {bucket} with key {OUTPUT_FILE_NAME}")
        return {
            'statusCode': 200
        }
    except Exception as e:
        logger.error(f"An error occurred during transcription: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps(f"An error occurred during transcription: {str(e)}")
        }

