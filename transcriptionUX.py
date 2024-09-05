import tkinter as tk
from tkinter import ttk
import sys
import threading
import logging
import os
from transcription import transcribe


def update_progress():
    progress['value'] += 10

# Create the main window
window = tk.Tk()
window.title("Progress Bar Example")

# Create a progress bar
progress = ttk.Progressbar(window, orient=tk.HORIZONTAL, length=300, mode='determinate')
progress.pack(pady=10, padx=20)

# Create a label
label = tk.Label(window, text="Transcription in progress...")
label.pack()

def transcribe_file(file: str):
    logger.info(f"Transcribing file {file}...")
    transcribe(file)
    pass

if __name__ == "__main__":
    log_directory = 'C:\\Logs\\Transcriptions'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=f'{log_directory}\\transcriptionUX.log')
    logger = logging.getLogger()

    # Parse command line arguments
    if len(sys.argv) > 1:
        file_to_transcribe = sys.argv[1]
        label.config(text=f"File {file_to_transcribe} is being transcribed...")
        # Create a separate thread for transcribing
        transcribe_thread = threading.Thread(target=transcribe_file, args=(file_to_transcribe,))
        transcribe_thread.start()
        # Start the main event loop
        window.mainloop()
    else:
        label.config(text="No file to transcribe.")

    # Rest of the code goes here