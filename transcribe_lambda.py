# `pip3 install assemblyai` (macOS)
# `pip install assemblyai` (Windows)

from transcription import transcribe
import logging
import json
import boto3
from mypy_boto3_s3.client import S3Client
import urllib.parse
from config import get_parameter
import os
import tempfile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

api_key = get_parameter("/transcription/ASSEMBLYAI_APIKEY")
# TODO Implement language detection
language_code="en"
speaker_labels=True




def lambda_handler(event, context):
    try:
        event_list:list = event['Records']
        logger.info(f"Starting transcription lambda function with {len(event_list)} records")
        for record in event_list:
            key = record['s3']['object']['key']
            bucket = record['s3']['bucket']['name']
            logging.info(f"Transcribing file {key} from bucket {bucket}")
            # Check if the file is an audio file
            if not key.lower().endswith(('.mp3', '.wav', '.flac', '.ogg', '.mp4', '.m4a', '.wma', '.aac')):
                logger.warning(f"File {key} is not an audio file. Skipping...")
                continue
            # The key might be URL encoded, so we may need to decode it
            key = urllib.parse.unquote_plus(key)
            FILE_URL = f"https://{bucket}.s3.amazonaws.com/{key}"
            # OUTPUT_FILE_NAME will contain the relative name with its extension as text
            OUTPUT_FILE_NAME = FILE_URL.rsplit("/", 1)[1].split(".")[0] + ".txt"
            TMP_DIR = tempfile.gettempdir()
            TMPFILE = os.path.join(TMP_DIR, OUTPUT_FILE_NAME)
            logger.info(f"Transcribing {FILE_URL} into {OUTPUT_FILE_NAME}")
            transcribe(FILE_URL, TMPFILE, api_key, language_code, speaker_labels)
            logging.info(f"Transcription saved to file: {TMPFILE}")
            logging.info(f"Pushing transcription to S3 bucket with key {OUTPUT_FILE_NAME}")
            s3:S3Client = boto3.client('s3')
            logging.info(f"Uploading {TMPFILE} to bucket {bucket}")
            s3.upload_file(TMPFILE, bucket, f'{OUTPUT_FILE_NAME}')
            logging.info(f"{TMPFILE} has been uploaded to bucket smarctranscription with key {OUTPUT_FILE_NAME}")
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

