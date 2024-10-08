import logging
import openai
import argparse
from config import get_parameter

OPENAI_KEY=get_parameter("/transcription/OPENAI_APIKEY")

def summarize_text(text:str)->str:
    """
    Summarizes the given text using OpenAI's GPT-3.5-turbo model.
    Args:
        text (str): The text to be summarized.
    Returns:
        str: The summarized text. Returns an empty string if the response is None.
    """

    openai.api_key = OPENAI_KEY
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": f"Please summarize the following text:\n\n{text}"}
        ]
    )
    toReturn = response.choices[0].message.content
    if toReturn == None:
        return ""
    return toReturn


def summarize_file(inputfile:str, outputfile:str|None):
    """
    Summarizes the content of a given input file and writes the summary to an output file or prints it.
    Args:
        inputfile (str): The path to the input file containing the text to be summarized.
        outputfile (str | None): The path to the output file where the summary will be written. 
                                    If None, the summary will be printed to the console.
    Returns:
        None
    """
    with open(inputfile, 'r') as file:
        text_to_summarize = file.read() 
    summary = summarize_text(text_to_summarize)

    if outputfile:
        with open(outputfile, 'w') as file:
            file.write(summary)
    else:
        print(summary)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Transcribe audio files using AssemblyAI.")
    parser.add_argument("--api_key", type=str, help="OpenAI API key", default=OPENAI_KEY)
    parser.add_argument("--file", type=str, help="Generate a file in the same directory (by default) as the input file. The name of the file is the same as the input file with a .txt extension.")
    parser.add_argument("--output_file_dir", type=str, help="Directory where the file will be generated if file is set to True. The name of the file is the same as the input file with a .txt extension.")

    args = parser.parse_args()

    # Handle parameters
    FILE = args.file
    OUTPUT_FILE_DIR = args.output_file_dir
    if not OUTPUT_FILE_DIR:
        OUTPUT_FILE_DIR = FILE.rsplit("\\", 1)[0]
    OUTPUT_FILE_URL = OUTPUT_FILE_DIR + "\\" + FILE.split("\\")[-1].split(".")[0] + "_summary.txt"

    summarize_file(FILE, OUTPUT_FILE_URL)
