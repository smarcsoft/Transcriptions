import tkinter as tk
from tkinter.ttk import Progressbar
import logging
from os import path, makedirs, _exit
#import boto3
from transcribe import transcribe_file
from threading import Thread
#from mypy_boto3_s3 import S3Client
from summarize import summarize_file
import argparse


def update_progress():
    progress['value'] += 10

logger = None
stop_spinning = False
file_to_summarize = ""

# def copy_file_to_s3(file: str) -> S3Client: 
#     global logger
#     try:
#         s3 = boto3.client('s3')
#         s3.upload_file(file, 'smarctranscriptions', os.path.basename(file))
#         logging.getLogger().info(f"File {file} uploaded to S3 bucket.")
#         return s3
#     except Exception as e:
#         logging.getLogger().error(f"Error uploading file {file} to S3 bucket: {str(e)}") 
#         raise e
    
# def copy_file_from_s3(url, output_directory: str):
#     try:
#         s3 = boto3.client('s3')
#         filename = os.path.basename(url)
#         output_path = os.path.join(output_directory, filename)
#         s3.download_file('smarctranscriptions', filename, output_path)
#         logging.getLogger().info(f"File {filename} downloaded from S3 bucket to {output_path}.")
#     except Exception as e:
#         logging.getLogger().error(f"Error downloading file from S3 bucket: {str(e)}")
#         raise e
    
# def wait_for_transcription(s3: S3Client, transcribed_file: str) -> str:
#     try:
#         waiter = s3.get_waiter('object_exists')
#         waiter.wait(Bucket='smarctranscriptions', Key=transcribed_file)
#         logging.getLogger().info(f"File {transcribed_file} is available in S3 bucket.")
#         transcribe_url = f"https://smarctranscriptions.s3.amazonaws.com/{transcribed_file}"
#         logging.getLogger().info(f"Transcription file URL: {transcribe_url}")
#         return transcribe_url
#     except Exception as e:
#         logging.getLogger().error(f"Error waiting for transccritpion file {transcribed_file} in S3 bucket: {str(e)}")
#         raise e

# def clean_s3(keyaudio: str, keytxt: str):
#     try:
#         s3 = boto3.client('s3')
#         s3.delete_object(Bucket='smarctranscriptions', Key=keyaudio)
#         s3.delete_object(Bucket='smarctranscriptions', Key=keytxt)
#         logging.getLogger().info(f"Files {keyaudio} and {keytxt} deleted from S3 bucket.")
#     except Exception as e:
#         logging.getLogger().error(f"Error deleting files {keyaudio} and {keytxt} from S3 bucket: {str(e)}")
#         raise e

def spin_progress_bar(progress):
    while stop_spinning == False:
        progress['value'] += 10
        progress['value'] = progress['value'] % 100
        logging.getLogger().info(f"Progress bar:{progress['value']}")
        progress.update_idletasks()
        progress.after(1000)

def summarize_button_click(button: tk.Button):
    global stop_spinning
    global file_to_summarize
    inputfile = file_to_summarize
    logging.getLogger().info("Summarizing the transcribed text...")
    progress['value'] = 0
    spinthread:Thread = Thread(target=spin_progress_bar, args=(progress,))
    spinthread.start()
    button.config(state=tk.DISABLED)
    progress_value = 0
    try:
        outputfile = path.splitext(inputfile)[0] + "_summary.txt"
        summarize_file(inputfile, outputfile=outputfile)
        progress_value = 100
        logging.getLogger().info("Summarization complete.")
        label.config(text=f"File {inputfile} has been summarized in {outputfile}.")
    except Exception as e:
        logging.getLogger().error(f"Error during summarization: {str(e)}")
        label.config(text=f"Error summarizing file {inputfile}: {str(e)}.")
        progress_value = 0
        raise e
    finally:
        stop_spinning = True
        spinthread.join()
        progress['value'] = progress_value
        progress.update_idletasks()


def _transcribe_file(file: str)-> str:
    global stop_spinning
    global file_to_summarize
    outputfile = path.splitext(file)[0] + ".txt"
    logging.getLogger().info(f"Transcribing file {file} in {outputfile}...")
    
    spinthread:Thread = Thread(target=spin_progress_bar, args=(progress,))
    spinthread.start()
    # Uncomment the following line to transcribe the file without AWS lamdba function
    progress_value = 100
    try:
        transcribe_file(file, outputfile)
        progress_value = 100
        logging.getLogger().info("Transcription complete.")
        label.config(text=f"File {file} has been transcribed in {outputfile}.")
        summarize_button.config(state=tk.NORMAL)
        file_to_summarize = outputfile
        return outputfile
    except Exception as e:
        logging.getLogger().error(f"Error during transcription: {str(e)}")
        label.config(text=f"Error transcribing file {file}: {str(e)}.")
        progress_value = 0
        raise e
    finally:
        stop_spinning = True
        spinthread.join()
        progress['value'] = progress_value
        progress.update_idletasks()

    # outputpath = os.path.dirname(file)
    # keytxt = os.path.basename(outputfile)
    # keyaudio = os.path.basename(file)
    # copy_file_from_s3(wait_for_transcription(copy_file_to_s3(file), keytxt), outputpath)
    # clean_s3(keyaudio, keytxt)


if __name__ == "__main__":
    log_directory = 'C:\\Logs\\Transcriptions'
    if not path.exists(log_directory):
        makedirs(log_directory)

    file_to_transcribe = None

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", help="Specify the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    parser.add_argument("--stdout", help="Debugging logs to stdout", action="store_true")
    parser.add_argument('--file', type=str, required=True, help='The name of the file to process')
    args = parser.parse_args()

    if args.stdout:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    else:    
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=f'{log_directory}\\transcriptionUX.log')
    logger = logging.getLogger()

    # Set the log level based on the command line argument
    if args.log:
        log_level = getattr(logging, args.log.upper(), None)
        if not isinstance(log_level, int):
            raise ValueError(f"Invalid log level: {args.log}")
        logger.setLevel(log_level)
        logger.info(f"Log level set to {args.log}")

    if args.file:
        file_to_transcribe = args.file
        logger.info(f"Transcribing file {file_to_transcribe}...")

    # Create the main window
    window = tk.Tk()
    window.title("Transcription service (assemblyAI)")

    # Create a progress bar
    progress = Progressbar(window, orient=tk.HORIZONTAL, length=400, mode='determinate')
    progress.pack(pady=10, padx=20)

    # Create a button
    summarize_button = tk.Button(window, text="Summarize...", command=lambda: summarize_button_click(summarize_button), state=tk.DISABLED)
    summarize_button.pack(pady=10)

    # Create a label
    label = tk.Label(window, text="Transcription in progress...")
    label.pack()


    # Parse command line arguments
    if file_to_transcribe:
        label.config(text=f"File {file_to_transcribe} is being transcribed...")
        # Create a separate thread for transcribing
        transcribe_thread = Thread(target=_transcribe_file, args=(file_to_transcribe,))
        transcribe_thread.start()
    else:
        label.config(text="No file to transcribe.")

    # Start the main event loop
    window.mainloop()
    _exit(0)

