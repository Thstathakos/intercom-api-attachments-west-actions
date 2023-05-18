import requests
from requests.auth import HTTPBasicAuth
import json
from bs4 import BeautifulSoup
import os
import shutil
import config
import time
import logging
import logging.handlers
import glob
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def get_conversation_ids():
    # set authentication token
    try:
        token = os.getenv("TOKEN_INTERCOM")
    except KeyError:
        token = "Token not available!"
    # create an empty list to store the ticket IDs
    ticket_ids = [187701600007224, 187701600007304]
    initial_timestamp = int(time.time())
    # set up the Intercom API client
    url = "https://api.intercom.io/conversations/search"
    for i in range(1, config.days_to_check + 1):
        # Calculate UNIX timestamps
        start_timestamp = initial_timestamp - ((i - 1) * 24 * 60 * 60)
        end_timestamp = start_timestamp - (1 * 24 * 60 * 60)
        payload = {"query": {
            "operator": "AND",
            "value": [
                {
                    "field": "created_at",
                    "operator": "<",
                    "value": f"{start_timestamp}"
                },
                {
                    "field": "created_at",
                    "operator": ">",
                    "value": f"{end_timestamp}"
                }
            ]
        }}
        headers = {
            "accept": "application/json",
            "Intercom-Version": "2.8",
            "content-type": "application/json",
            "authorization": f"Bearer {token}"
        }
        tickets_in_requested_time_response = requests.post(url, json=payload, headers=headers, verify=False)
        data = tickets_in_requested_time_response.json()
        # iterate through the tickets and append their IDs to the list
        for ticket in data['conversations']:
            ticket_ids.append(ticket['id'])
        print(f"Days checked : {i}. Found {len(ticket_ids)} tickets in total")
    print(f"Found {len(ticket_ids)} tickets within the specified parameters")
    ticket_ids.sort()
    print(ticket_ids)
    return ticket_ids


def download_attachments_by_id(conversation_data_inner, conversation_id_inner):
    # Initialise counters
    image_counter = 0
    print(conversation_data_inner)
    store_code = conversation_data_inner['custom_attributes']['Store code']
    folder_path = f"attachments/Data extracted on_{date}/{store_code}"
    accepted_values = False
    # Extract image URLs from the HTML content
    print(conversation_data_inner['custom_attributes']['Phase'])
    print(conversation_data_inner['custom_attributes']['Common Issue'])
    if conversation_data_inner['custom_attributes']['Phase'] in config.accepted_phase_list \
            and conversation_data_inner['custom_attributes']['Common Issue'] in config.accepted_common_issue_list:
        accepted_values = True
    print(accepted_values)
    if accepted_values == True:
        for i in range(len(conversation_data['source']['attachments'])):
            html_content = conversation_data['source']['attachments'][i]['url']
            try:
                image_url = conversation_data['source']['attachments'][i]['url']
            except TypeError:
                pass
            # Download image
            else:
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    print(f"Folder {store_code} created successfully.")
                response_inner = requests.get(image_url, verify=False)
                # Categorise image
                if "gif" in image_url.lower():
                    pass
                else:
                    with open(f'{folder_path}/{store_code}_{image_counter}.jpg', 'wb') as f:
                        f.write(response_inner.content)
                    image_counter += 1
        html_content = conversation_data['source']['body']
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            image_url = soup.find('img')['src']
        except TypeError:
            pass
        # Download image
        else:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Folder {store_code} created successfully.")
            response_inner = requests.get(image_url, verify=False)
            # Categorise image
            if "gif" in image_url.lower():
                pass
            else:
                with open(f'{folder_path}/{store_code}_{image_counter}.jpg', 'wb') as f:
                    f.write(response_inner.content)
                image_counter += 1
        for i in range(len(conversation_data['conversation_parts']['conversation_parts'])):
            html_content = conversation_data['conversation_parts']['conversation_parts'][i]['body']
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                image_url = soup.find('img')['src']
            except TypeError:
                pass
            # Download image
            else:
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    print(f"Folder {store_code} created successfully.")
                response_inner = requests.get(image_url, verify=False)
                # Categorise image
                if "gif" in image_url.lower():
                    pass
                else:
                    with open(f'{folder_path}/{store_code}_{image_counter}.jpg', 'wb') as f:
                        f.write(response_inner.content)
                    image_counter += 1

    print(f"Ticket {conversation_id_inner} Done."
          f"Saved {image_counter} attachments")


def delete_empty_folders(root_folder):
    """
    Deletes all empty folders within a given root folder.
    """
    for foldername, subfolders, filenames in os.walk(root_folder, topdown=False):
        # Check if the folder is empty
        if not any((subfolders, filenames)):
            print(f"Deleting empty folder: {foldername}")
            shutil.rmtree(foldername)


def get_date():
    # Get the current time in seconds
    current_time = time.time()

    # Convert the current time to a struct_time object
    current_struct_time = time.localtime(current_time)

    # Extract the day, month, and year from the struct_time object
    day = current_struct_time.tm_mday
    month = current_struct_time.tm_mon
    year = current_struct_time.tm_year

    # Create the formatted date string
    date_string = f"{day:02d}-{month:02d}-{year}"

    # Print the formatted date string
    return date_string


def log_file():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger_file_handler = logging.handlers.RotatingFileHandler(
        "status.log",
        maxBytes=1024 * 1024,
        backupCount=1,
        encoding="utf8",
    )
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger_file_handler.setFormatter(formatter)
    logger.addHandler(logger_file_handler)
    logger.info(f'Job Completed')


def upload_to_google_drive():
    # Path to the folder you want to upload
    folder_path = 'attachments'

    # Path to the service account JSON key file
    credentials_json = os.getenv("CREDENTIALS")

    # Initialize the Drive API client
    credentials = service_account.Credentials.from_service_account_file(credentials_json, scopes=[
        'https://www.googleapis.com/auth/drive'])
    drive_service = build('drive', 'v3', credentials=credentials)
    folder_id = os.getenv("FOLDERID")

    # Iterate over files in the folder and upload them
    files = glob.glob(os.path.join(folder_path, '*'))
    for file_path in files:
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        drive_service.files().create(body=file_metadata, media_body=media).execute()

    print("Folder uploaded successfully!")


# initial values
TOKEN = os.getenv("TOKEN_INTERCOM")
conversation_ids = get_conversation_ids()
date = get_date()
# Get the conversation data
for conversation_id in conversation_ids:
    response = requests.get(f'https://api.intercom.io/conversations/{conversation_id}', auth=HTTPBasicAuth(TOKEN, ""),
                            verify=False)
    conversation_data = json.loads(response.text)
    download_attachments_by_id(conversation_data, conversation_id)
# Delete empty Folders:
delete_empty_folders("attachments")
upload_to_google_drive()
log_file()
