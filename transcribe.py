# `pip3 install assemblyai` (macOS)
# `pip install assemblyai` (Windows)

import assemblyai as aai
import logging

# Handle parametersimport argparse
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up argument parser
parser = argparse.ArgumentParser(description="Transcribe audio files using AssemblyAI.")
parser.add_argument("file_url", type=str, help="URL or path to the audio file to transcribe")
parser.add_argument("--api_key", type=str, help="AssemblyAI API key", default="b4dd2fbbb4164707a20534980fa0bfb4")
parser.add_argument("--language_code", type=str, default="fr", help="Language code for transcription")
parser.add_argument("--speaker_labels", type=bool, default=True, help="Enable speaker labels")
parser.add_argument("--file", type=bool, help="Generate a file in the same directory (by default) as the input file. The name of the file is the same as the input file with a .txt extension.")
parser.add_argument("--output_file_dir", type=str, help="Directory where the file will be generated if file is set to True. The name of the file is the same as the input file with a .txt extension.")

args = parser.parse_args()

# Handle parameters
FILE_URL = args.file_url
aai.settings.api_key = args.api_key
OUTPUT_FILE_DIR = args.output_file_dir
if not OUTPUT_FILE_DIR:
    OUTPUT_FILE_DIR = FILE_URL.rsplit("\\", 1)[0]
    OUTPUT_FILE_URL = OUTPUT_FILE_DIR + "\\" + FILE_URL.split("\\")[-1].split(".")[0] + ".txt"
else:
    OUTPUT_FILE_URL = OUTPUT_FILE_DIR + "\\" + FILE_URL.split("\\")[-1].split(".")[0] + ".txt"
FILE=args.file

transcriber = aai.Transcriber()
config = aai.TranscriptionConfig(language_code=args.language_code, speaker_labels=args.speaker_labels)

logging.info(f"Transcribing file: {FILE_URL}")
logging.info(f"Output file directory: {OUTPUT_FILE_DIR}")
logging.info(f"Output file URL: {OUTPUT_FILE_URL}")
logging.info(f"API Key: {aai.settings.api_key}")
logging.info(f"Language Code: {args.language_code}")
logging.info(f"Speaker Labels: {args.speaker_labels}")
logging.info(f"Generate File: {FILE}")

transcript = transcriber.transcribe(FILE_URL, config=config)

if transcript.status == aai.TranscriptStatus.error:
    logging.error(f"Transcription error: {transcript.error}")
else:
    if FILE:
        with open(OUTPUT_FILE_URL, 'w', encoding='utf-8') as f:
            for utterance in transcript.utterances:
                f.write(f"Speaker {utterance.speaker}: {utterance.text}\n")
        logging.info(f"Transcription saved to file: {OUTPUT_FILE_URL}")
    else:
        for utterance in transcript.utterances:
            print(f"Speaker {utterance.speaker}: {utterance.text}")
        logging.info("Transcription printed to console")