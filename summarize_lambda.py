from summarization import summarize
import logging
import json
import boto3
from mypy_boto3_s3.client import S3Client
import urllib.parse
import os
import tempfile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        event_list:list = event['Records']
        logger.info(f"Starting summarization lambda function with {len(event_list)} records")
        for record in event_list:
            key = record['s3']['object']['key']
            bucket = record['s3']['bucket']['name']
            logging.info(f"Transcribing file {key} from bucket {bucket}")
            # Check if the file is an audio file
            if not key.lower().endswith(('.txt')):
                logger.warning(f"File {key} is not a text file. Skipping...")
                continue
            # The key might be URL encoded, so we may need to decode it
            key = urllib.parse.unquote_plus(key)
            FILE_URL = f"https://{bucket}.s3.amazonaws.com/{key}"
            # OUTPUT_FILE_NAME will contain the relative name with its extension as text
            OUTPUT_FILE_NAME = FILE_URL.rsplit("/", 1)[1].split(".")[0] + "_summary.txt"
            TMP_DIR = tempfile.gettempdir()
            TMPFILE = os.path.join(TMP_DIR, OUTPUT_FILE_NAME)
            logger.info(f"Summarizing {FILE_URL} into {OUTPUT_FILE_NAME}")
            summarize(FILE_URL, TMPFILE)
            logging.info(f"Summarization saved to file: {TMPFILE}")
            logging.info(f"Pushing summarization to S3 bucket with key {OUTPUT_FILE_NAME}")
            s3:S3Client = boto3.client('s3')
            logging.info(f"Uploading {TMPFILE} to bucket {bucket}")
            s3.upload_file(TMPFILE, bucket, f'{OUTPUT_FILE_NAME}')
            logging.info(f"{TMPFILE} has been uploaded to bucket {bucket} with key {OUTPUT_FILE_NAME}")
        return {
            'statusCode': 200,
            'body': json.dumps(f"File(s) {event['Records']} has been transcribed")
        }
    except Exception as e:
        logger.error(f"An error occurred during transcription: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps(f"An error occurred during transcription: {str(e)}")
        }

