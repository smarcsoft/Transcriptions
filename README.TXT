Build:
pyinstaller --hiddenimport win32timezone -F watcher.py

Procedure to install the service
dist\watcher.exe install

Procedure to start the service
dist\watcher.exe start

Procedure to remove the service
dist\watcherr.exe remove

