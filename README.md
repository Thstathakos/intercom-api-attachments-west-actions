# intercom_api_attachments_west_actions

## Description

- This project was build to avoid manually downloading and sorting and uploading screenshots form intercom live chat
- With this project I learned how to interact with intercom's and google's api as well as how to set up github actions

## Installation

In order to dun the project for your self you need to fork it and provide the following parameters :
In git hub actions secrets : 

TOKEN_INTERCOM = your intercom api access token
CREDENTIALS = your google api credentials provided in base64 encoding (this was the idea from another project and the only way I could make google api work)
FOLDERID = The id of the folder you want the data to be saved 

in actions.yml file the folloing parameters can be changed : 
lines 6-8
on:
	schedule:
		- cron :
this values can be changed in order to determine when the script will run

## Usage

Script can be configured from config file by changing the following parameters:
days_to_check = int (range of days that the script checks starting from the time you run the script to days spacified by this variable)
accepted_phase_list = list (list of strings that their attachments we want downloaded, phase refers to installation phase)
accepted_common_issue_list = list (list of strings that their attachments we want downloaded , common issue refers to common issues as seen in https://bespot.atlassian.net/wiki/spaces/OPS/pages/637829126/Common+Issue+Guide)

## Functions explained

get_conversation_ids : Searches for the tickets created between script runtime and days_to_check and returns a list with the ticket ids that fit the parameters
download_attachments_by_id : Itterates through list with ticket ids and downloads images in specific folder that gets created by the same function. Checks both chats and emails
delete_empty_folders : Files may be created but remain empty this function deletes empty folders
get_date : Function returns today's date in order to be used in the creation of folders used in function download_attachments_by_id
log_file :  log the datetime of script runs in status.log file
upload_to_google_drive : handles the file upload to google drive