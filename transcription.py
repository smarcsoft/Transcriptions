import assemblyai as aai
import logging

# Handle parametersimport argparse
import argparse

DEFAULT_API_KEY = "b4dd2fbbb4164707a20534980fa0bfb4"

def transcribe(inputfile:str, outputfile:str|None=None, api_key:str=DEFAULT_API_KEY, language_code:str|None=None, speaker_labels:bool=True):
    aai.settings.api_key = api_key
    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(language_code=language_code, speaker_labels=speaker_labels)

    logging.info(f"Transcribing file: {inputfile}")
    logging.info(f"Output file: {outputfile}")
    logging.info(f"API Key: {api_key}")
    logging.info(f"Language Code: {language_code}")
    logging.info(f"Speaker Labels: {speaker_labels}")

    transcript = transcriber.transcribe(inputfile, config=config)

    if transcript.status == aai.TranscriptStatus.error:
        raise Exception(f"Transcription error: {transcript.error}")
    else:
        if outputfile is not None:
            with open(outputfile, 'w', encoding='utf-8') as f:
                utterances = transcript.utterances
                if(utterances is not None):
                    for utterance in utterances:
                        f.write(f"Speaker {utterance.speaker}: {utterance.text}\n")
            logging.info(f"Transcription saved to file: {outputfile}")
        else:
            utterances = transcript.utterances
            if(utterances is not None):
                for utterance in utterances:
                    print(f"Speaker {utterance.speaker}: {utterance.text}")
            logging.info("Transcription printed to console")
        pass



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Transcribe audio files using AssemblyAI.")
    parser.add_argument("file_url", type=str, help="URL or path to the audio file to transcribe")
    parser.add_argument("--api_key", type=str, help="AssemblyAI API key", default=DEFAULT_API_KEY)
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

    transcribe(FILE, OUTPUT_FILE_URL, args.api_key, args.language_code, args.speaker_labels)
