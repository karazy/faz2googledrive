faz2drive
==========

faz2drive is a script to automatically download faz.net e-paper abonements and send them to a Google Apps Drive.
Currently the script is targeted at Google Apps users, since here a permission delegation is possible
without manually allowing access via browser. 

To run the script check the execute_FAZ_loader.py

Script can either be run standalone, via Dockerfile or as a scheduled task in Google Container Engine.

Attention: a valid e-paper abo is required to run this script. 


## Configuration
Create an env.cfg file and put it under src
    [FAZ]
    Username = YOUR-FAZ-USER
    Password = YOUR-FAZ-PASS

    [DRIVE]
    Upload_folder_id = ID-OF-A-DRIVE-FOLDER
    Delegate = EMAIL-OF-DRIVE-FOLDER-OWNER
    Key_file = SERVICE_ACCOUNT_KEY_FILE

Create a Service Account with delegation rights in google apps and download the key file.
Put the key file under src and refer to it in google_drive.py

## Run locally
python execute_FAZ_loader.py

## Run docker
Run ./buildAndRun.sh in src.

#Token error
http://stackoverflow.com/questions/36189612/token-must-be-a-short-lived-token-and-in-a-reasonable-timeframe



