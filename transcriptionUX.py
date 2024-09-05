import tkinter as tk
from tkinter import ttk
import sys
import logging
import os
from transcription import transcribe
from threading import Thread


def update_progress():
    progress['value'] += 10

logger = None
stop_spinning = False



def spin_progress_bar(progress):
    while stop_spinning == False:
        progress['value'] += 10
        progress['value'] = progress['value'] % 100
        logging.getLogger().info(f"Progress bar:{progress['value']}")
        progress.update_idletasks()
        progress.after(1000)

def transcribe_file(file: str):
    global stop_spinning
    outputfile = os.path.splitext(file)[0] + ".txt"
    logging.getLogger().info(f"Transcribing file {file} in {outputfile}...")
    
    spinthread:Thread = Thread(target=spin_progress_bar, args=(progress,))
    spinthread.start()
    transcribe(file, outputfile)
    stop_spinning = True
    spinthread.join()
    progress['value'] = 100
    logging.getLogger().info("Transcription complete.")
    label.config(text=f"File {file} has been transcribed in {outputfile}.")

if __name__ == "__main__":
    log_directory = 'C:\\Logs\\Transcriptions'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=f'{log_directory}\\transcriptionUX.log')
    logger = logging.getLogger()

    # Create the main window
    window = tk.Tk()
    window.title("Transcription service (assemblyAI)")

    # Create a progress bar
    progress = ttk.Progressbar(window, orient=tk.HORIZONTAL, length=400, mode='determinate')
    progress.pack(pady=10, padx=20)

    # Create a label
    label = tk.Label(window, text="Transcription in progress...")
    label.pack()


    # Parse command line arguments
    if len(sys.argv) > 1:
        file_to_transcribe = sys.argv[1]
        label.config(text=f"File {file_to_transcribe} is being transcribed...")
        # Create a separate thread for transcribing
        transcribe_thread = Thread(target=transcribe_file, args=(file_to_transcribe,))
        transcribe_thread.start()
        # Start the main event loop
        window.mainloop()
        os._exit(0)
    else:
        label.config(text="No file to transcribe.")

    # Rest of the code goes here