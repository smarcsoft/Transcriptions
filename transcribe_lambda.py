# `pip3 install assemblyai` (macOS)
# `pip install assemblyai` (Windows)

from typing import List
import assemblyai as aai
import logging
import json
import boto3
from mypy_boto3_s3.client import S3Client
import urllib.parse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#TODO: Save this API key in a secured location on AWS.
aai.settings.api_key = "b4dd2fbbb4164707a20534980fa0bfb4"

#TODO: Save these config parameters in an appropriate location
language_code="en"
speaker_labels=True

def lambda_handler(event, context):
    try:
        logger.info(f"Starting transcription lambda function with {event['Records'].length} records")
        for record in event['Records']:
            key = record['s3']['object']['key']
            bucket = record['s3']['bucket']['name']
            logging.info(f"Transcribing file {key} from bucket {bucket}")
            # The key might be URL encoded, so we may need to decode it
            key = urllib.parse.unquote_plus(key)
            FILE_URL = f"https://{bucket}.s3.amazonaws.com/{key}"
            OUTPUT_FILE_NAME = FILE_URL.rsplit("/", 1)[1].split(".")[0] + ".txt"

            logger.info(f"Transcribing {FILE_URL} into {OUTPUT_FILE_NAME}")
            transcriber = aai.Transcriber()
            config = aai.TranscriptionConfig(language_code=language_code, speaker_labels=speaker_labels)
            transcript = transcriber.transcribe(FILE_URL, config=config)
            if transcript.status == aai.TranscriptStatus.error:
                logger.error(f"Transcription error: {transcript.error}")
                return {
                    'statusCode': 400,
                    'body': json.dumps(f"File {FILE_URL} could not be transcribed : {transcript.error}")
                }
            else:
                TMPFILE = f"/tmp/{OUTPUT_FILE_NAME}"
                with open(TMPFILE, 'w', encoding='utf-8') as f:
                    utterances = transcript.utterances
                    if utterances is None:
                        logger.error(f"No utterances found in transcription")
                        return {
                            'statusCode': 400,
                            'body': json.dumps(f"File {FILE_URL} could not be transcribed : No utterances found in transcription")
                        }
                    for utterance in utterances:
                        f.write(f"Speaker {utterance.speaker}: {utterance.text}\n")
                logging.info(f"Transcription saved to file: {TMPFILE}")
                logging.info(f"Pushing transcription to {OUTPUT_FILE_NAME}")
                s3:S3Client = boto3.client('s3')
                logging.info(f"Uploading {TMPFILE} to bucket smarctranscription")
                s3.upload_file(TMPFILE, 'smarctranscriptions', f'{OUTPUT_FILE_NAME}')
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

