import requests
from requests.auth import HTTPBasicAuth
import json
from bs4 import BeautifulSoup
import os
import shutil
import config
import time


def get_conversation_ids():
    # set authentication token
    token = config.TOKEN
    # create an empty list to store the ticket IDs
    ticket_ids = []
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
        tickets_in_requested_time_response = requests.post(url, json=payload, headers=headers)
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
    folder_path = f"attachments/{store_code}"
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
                response_inner = requests.get(image_url)
                # Categorise image
                if "gif" in image_url.lower():
                    pass
                else:
                    with open(f'attachments/{store_code}/{store_code}_{image_counter}.jpg', 'wb') as f:
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
            response_inner = requests.get(image_url)
            # Categorise image
            if "gif" in image_url.lower():
                pass
            else:
                with open(f'attachments/{store_code}/{store_code}_{image_counter}.jpg', 'wb') as f:
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
                response_inner = requests.get(image_url)
                # Categorise image
                if "gif" in image_url.lower():
                    pass
                else:
                    with open(f'attachments/{store_code}/{store_code}_{image_counter}.jpg', 'wb') as f:
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


# initial values
TOKEN = config.TOKEN
conversation_ids = get_conversation_ids()
# Get the conversation data
for conversation_id in conversation_ids:
    response = requests.get(f'https://api.intercom.io/conversations/{conversation_id}', auth=HTTPBasicAuth(TOKEN, ""))
    conversation_data = json.loads(response.text)
    download_attachments_by_id(conversation_data, conversation_id)
# Delete empty Folders:
delete_empty_folders("attachments")
