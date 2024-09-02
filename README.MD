This project is an addon to Windows to transcribe and summarize audio files.
The files are dropped into a Windows directory.
A windows service implemented in python (watcher.py) is watching for new files
These new files are dowloaded into an AWS S3 bucket
This is triggering a AWS step function 
The Step Function then triggers a lamdba function doing the transcription and if successful it triggers another lambda function doing the summarization
The files (transcribed text and summarized texts) and then pushed to the windows directory by the same windows service


# How to build the windows service
You first need to clone the git repo in windows
You need to build it as administrator (to be able to install or uninstall the serrice)

## Create the windows service executable
First create the Windows executable
pyinstaller --hiddenimport win32timezone -F watcher.py

## Install the service
dist\watcher.exe install

## Start the service
dist\watcher.exe start

## Remove the service
If you need to remove the sevice:
dist\watcherr.exe remove

