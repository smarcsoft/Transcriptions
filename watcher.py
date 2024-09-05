import argparse
import time
import boto3
import socket
import win32serviceutil
import win32event
import win32service
import servicemanager  # Add this line to import servicemanager module
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from mypy_boto3_s3 import S3Client
import logging
import os
import threading

testing = False

# Define the event handler class
class FileEventHandler(FileSystemEventHandler):
    def __init__(self, s3client: S3Client,s3_bucket_name):
        self.s3client: S3Client = s3client
        self.s3_bucket_name = s3_bucket_name

    
    def on_created(self, event):
        logging.info(f"New file created: {event.src_path}")
        # Upload the file to S3 bucket
        file_path = event.src_path
        file_name = os.path.basename(file_path)
        for i in range(3):
            try:
                logging.info(f"Uploading file '{file_name}' to S3 bucket {self.s3_bucket_name}...")
                self.s3client.upload_file(file_path, self.s3_bucket_name, file_name)
                logging.info(f"File '{file_name}' uploaded to S3 bucket.")
                break
            except Exception as e:
                logging.warning(f"Error uploading file '{file_name}' to S3 bucket: {str(e)}")
                if i < 2:
                    logging.info("Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    logging.error(f"Error Failed uploading file '{file_name}' after 3 times to S3 bucket: {str(e)}")


class FileTransferService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'TranscriptionWatcher'
    _svc_display_name_ = 'Transcription File Watcher Service'
    _svc_description_ = 'Watch a directory for audio files to be transcribed and summarized'

    # Define the directory to watch
    directory_to_watch = 'C:\\Users\\sebma\\Documents\\transcribe'
    # Define the S3 bucket name
    s3_bucket_name = 'smarctranscriptions'

    credentials = None

    def __init__(self, args):
        # Configure logging
        
        print("Initializing service.")
        if not testing:
            logging.info("Initializing service.")
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            socket.setdefaulttimeout(60)
        logging.info("Service is running.")

    def getAWSCredentials(self):
        # Retrieve AWS credentials from a secure location
        # and return them as a dictionary
        if self.credentials:
            return self.credentials
        
        self.credentials = {
            'access_key': os.environ.get('AWS_ACCESS_KEY'),
            'secret_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
            'region': 'eu-west-1'
        }
        return self.credentials

    def SvcStop(self):
        if not testing:
           self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
           win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        if not testing:
            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                  servicemanager.PYS_SERVICE_STARTED,
                                  (self._svc_name_, ''))
        logging.info("Command line arguments: {args}".format(args=sys.argv))
        testmode = "test" if testing == True else "run"
        logging.info(f"Service started in {testmode} mode")
        logging.info("Watching directory {dir}....".format(dir=self.directory_to_watch))
        t = threading.Thread(target=self.watch_directory)
        t.start()
        logging.info("Looping until the service is stopped....")
        if not testing:
            while True:
                logging.debug("Waiting until service is interrupted...")
                rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
                if rc == win32event.WAIT_OBJECT_0:
                    break
        else:
            logging.info("Waiting until interruption.")
            t.join()
        logging.info("Exiting the service....")


    def watch_directory(self):
        logging.info("watching directory thread started...")
        # Get AWS credentials
        credentials = self.getAWSCredentials()

        # Initialize the S3 client
        s3_client: S3Client = boto3.client('s3', 
                                aws_access_key_id=credentials['access_key'],
                                aws_secret_access_key=credentials['secret_key'],
                                region_name=credentials['region'])
        logging.info("S3 client initialized.")
        # Create the observer and event handler
        
        event_handler = FileEventHandler(s3_client, self.s3_bucket_name)
        logging.info("File Event Handler created")
        observer = Observer()
        logging.info("File observer created.")
        observer.schedule(event_handler, self.directory_to_watch, recursive=False)
        logging.info("Observer scheduled. Starting observer loop.")
        observer.start()
        logging.info("Observing {dir}...".format(dir=self.directory_to_watch))
        observer.join()
        logging.info("Observation finished. We are no longer monitoring {dir}.".format(dir=self.directory_to_watch))
        
            

if __name__ == '__main__':
    # Create the log directory if it doesn't exist
    log_directory = 'C:\\Logs\\Transcriptions'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_file = 'C:\\Logs\\Transcriptions\\watcher.log'
    logging.basicConfig(level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[logging.FileHandler(log_file), logging.StreamHandler()])
    
    logging.info("Starting transcription watcher...")
    if '--test' in sys.argv:
        logging.info("Running in test mode.")
        testing = True
        sys.argv.remove('--test')
        FileTransferService(sys.argv).SvcDoRun()
    else:
        testing = False
        if len(sys.argv) == 1:
            logging.info("Initializing service manager...")
            servicemanager.Initialize()
            logging.info("Preparing to host single...")
            servicemanager.PrepareToHostSingle(FileTransferService)
            logging.info("Starting service control dispatcher...")
            servicemanager.StartServiceCtrlDispatcher()
        else:
            logging.info("Handling command line...")
            win32serviceutil.HandleCommandLine(FileTransferService)


        