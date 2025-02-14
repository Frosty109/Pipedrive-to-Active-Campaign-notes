from bs4 import BeautifulSoup
from datetime import datetime
import requests
import html
import json

# Pipedrive data
pipedrive_api_token = '2674d30bb3f0022a571484f0ae9f6143c47981ce'
pipedrive_base_url = 'https://api.pipedrive.com/v1'

# Activecampaign data

# Put username and api key list here
active_campaign_api_list = {

}

# Single API to get note information for account. 
api_key_one = list(active_campaign_api_list.values())[0]

active_campaign_base_url = 'https://sorenliv.api-us1.com'

def main():
    pipedrive_api_token = input("Enter Pipedrive API Token/Key in form of 2624c30bb3...")

    active_campaign_base_url = input('https://account_name.api-us1.com')

    # Get pipedrive notes data
    pipe_drive_note_data = get_pipedrive_notes()

    active_campaign_accounts = get_active_campaign_accounts()

    active_campaign_users = get_active_campaign_users(active_campaign_base_url, api_key_one)

    sync_notes(pipe_drive_note_data, active_campaign_accounts, active_campaign_users)

# Find matching account based on pipedrive organization and list of active campaign accounts
def find_matching_account(pipedrive_note, active_campaign_accounts_list):
    # Loop through active campaign accounts
    for account in active_campaign_accounts_list:
        try:
            # If active campaign account equals pipedrive account name, return active campaign account
            if account['name'] == pipedrive_note['organization_name']['name']:
                print("ACCOUNT FOUND!")
                print("ACTIVE", account['name'])
                print("PIPEDRIVE", pipedrive_note["organization_name"]['name'])
                return account
        except TypeError:
            continue
        
# Find matching account between pipedrive note and active campaign user list
# This returns the active campaign username and firstName + lastName combination
def find_matching_user(pipedrive_note, active_campaign_users):
    for username, full_name, user_id, email in active_campaign_users:
        if (pipedrive_note['email'] == username) or (pipedrive_note['email'] == email): # Check if pipedrive email matches Active Campaign username or email
            print("EMAIL FOUND!")
            print("PIPEDRIVE EMAIL", pipedrive_note['email'])
            print("ACTIVE EMAIL", email)
            return username, full_name, user_id, email

# Sync notes between pipedrive and active campaign
def sync_notes(pipe_drive_data, active_campaign_data, active_campaign_users):
    pipedrive_notes = pipe_drive_data
    active_campaign_accounts = active_campaign_data

    # Limit note count
    count = 0

    if pipedrive_notes and active_campaign_accounts:
        for pipedrive_note in pipedrive_notes:

            # Find matching account based on pipedrive organization and list of active campaign accounts
            matching_account = find_matching_account(pipedrive_note, active_campaign_accounts)

            # Need to find matching user
            matching_user = find_matching_user(pipedrive_note, active_campaign_users)

            # If matching account is found
            if matching_account and matching_user:

                # Get id of active campaign account
                active_campaign_account_notes_link = matching_account['links']['notes']

                print("NOTES LINK:", active_campaign_account_notes_link)

                pipedrive_content = (
                    f"{pipedrive_note['content']}\n\n"
                    f"Original add time - {pipedrive_note['add_time']}\n\n"
                )

                # Get API Key Based On User
                active_user_api_key = match_api_key_to_user(matching_user)

                print("USER API", active_user_api_key, '\n')

                if active_user_api_key is not None:
                    # Update comment in active campaign
                    update_successful = update_active_campaign_account_notes(active_campaign_account_notes_link, pipedrive_content, matching_user, active_user_api_key)
                    if update_successful:
                        print("Success", '\n')
                        print(count)
                        count += 1

            # Limit count for testing
            #if count >= 100:
            #    break

## Active Campaign Functions
def update_active_campaign_account_notes(account_notes_url, notes_to_copy, user_for_note, active_user_api_key):
    print(account_notes_url)

    headers = {
        'Api-Token': active_user_api_key,
        'Content-Type': 'application/json'
    }


    # Remove unwanted characters and tags from Pipedrive comment
    cleaned_note = note_clean_up(notes_to_copy)

    # Get Active Campaign Notes for Account
    note_content = get_active_campaign_notes(account_notes_url, headers)

    if cleaned_note not in note_content:
        print("NOTE NOT FOUND! Adding Note: ", "\n")

        # Prepare the data for the note update
        data = {
            "note": {
                "note": cleaned_note,
            }
        }

        # Send the PUT request to update the note
        response = requests.post(account_notes_url, json=data, headers=headers)
        
        if response.status_code == 201:
            print(f"{cleaned_note}\n")
            return True
        else:
            print(f"Failed to update note: {response.status_code}, {response.text}")
            return False

    else: 
        print("Note Already Exists! ", "\n")
        return 1

# Get total number of active campaign accounts
def total_active_campaign_accounts():
    # Get total number of accounts:
    headers = {'API-Token': api_key_one}
    url = f'{active_campaign_base_url}/api/3/accounts'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        total_accounts = data.get('meta', {})

    return total_accounts

# Get main active campaign data
def get_active_campaign_accounts(limit=100):

    headers = {'API-Token': api_key_one}
    total_retrieved = 0
    total_accounts = total_active_campaign_accounts()
    total_accounts = int(total_accounts['total'])
    all_accounts = []

    while total_retrieved < total_accounts:
        url = f'{active_campaign_base_url}/api/3/accounts?limit={limit}&offset={total_retrieved}'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('accounts', [])
            all_accounts.extend(accounts)  # Add the current page of accounts to the list
            total_retrieved += len(accounts)  # Update the count of retrieved accounts
            
            # If fewer accounts are returned than the limit, we're likely at the last page
            if len(accounts) < limit:
                break
        else:
            print(f"Failed to retrieve accounts: {response.status_code} - {response.text}")
            break
    
    return all_accounts

# Get Active Campaign Notes
def get_active_campaign_notes(notes_url, headers):
    # Get Active Campaign Notes
    active_campaign_notes_response = requests.get(notes_url, headers=headers)

    if active_campaign_notes_response.status_code != 200:
        print(f"Failed to retrive existing notes: {active_campaign_notes_response.status_code}")
        return False
    
    active_campaign_notes = [note["note"] for note in active_campaign_notes_response.json().get("notes", [])]

    cleaned_note_list = [note_clean_up(note) for note in active_campaign_notes]

    # Return Cleaned Up Active Campaign Note content
    return cleaned_note_list

# Get user list from Active Campaign
def get_active_campaign_users(base_url, api_key):

    # Make a request to Active Campaign for user list data
    headers = {'API-Token': api_key}
    user_url = f'{base_url}/api/3/users'
    user_list_response = requests.get(user_url, headers=headers)

    if user_list_response.status_code != 200:
        print(f"Failed to retrieve Active Campaign User List {user_list_response}")
        return False
    
    user_list = user_list_response.json()

    # Set empty list
    user_info = []

    # Get username and name data from Active Campaign Users List
    for user in user_list['users']:
        username = user['username'].strip()
        first_name = user['firstName'].strip()
        last_name = user['lastName'].strip()
        user_id = user['id'].strip()
        user_email = user['email'].strip()

        # Append to list - Combine first and lastname into one name - This will be used for comparison to pipedrive username
        user_info.append((username, f"{first_name} {last_name}", user_id, user_email))

    return user_info

    # Get Active Campaign User List Documentation Here - https://developers.activecampaign.com/reference/list-all-users

# Get API Key Based On User
def match_api_key_to_user(matching_user):
    username = matching_user[0]
    user_email = matching_user[3]

    #user_api_key = active_campaign_api_keys[int(user_id) - 1]

    try:
        return active_campaign_api_list[username]
    except KeyError:
        try:
            return active_campaign_api_list[user_email]
        except KeyError:
            return None

    

## Pipedrive Functions
# Get Pipedrive data and return organisation name, notes, note add time, etc.
def get_pipedrive_notes(limit=500):
    print("get_pipedrive_notes CALLED")

    # Create base url for fetching notes from Pipedrive api
    url = f'{pipedrive_base_url}/notes?api_token={pipedrive_api_token}'
    notes = [] # Create empty list to store notes in
    start = 0

    while True:
        # Modify the url to include pagination info/parameters
        paginated_url = f'{url}&start={start}&limit={limit}'
        response = requests.get(paginated_url)

        if response.status_code == 200:
            data = response.json()
            page_notes = data.get('data', []) 
            notes.extend(page_notes) # Add the current page from pipedrive notes to main list of notes

            # Check to see if there are any more notes in pipedrive
            pagination_info = data.get('additional_data', {}).get('pagination', {})
            if not pagination_info.get('more_items_in_collection', False):
                break # Exit as we have found all notes

            start = pagination_info.get('next_start', start + limit)

        else:
            print(f"Failed to retrieve notes: {response.status_code} - {response.text}\n")
            return None
        
    print(f"Retrived {len(notes)} notes.\n")

    # Optionally, sort notes by data
    notes.sort(key=lambda x: x.get('add_time'), reverse=False)

    contents = [] # for user inputed notes from pipedrive

    # Get and organise relavent data from Pipedrive
    for note in notes:
        organization_name = note.get('organization', 'Unknown')
        id = note.get('id')
        content = note.get('content', '')
        add_time = note.get('add_time', 'Unknown')
        update_time = note.get('update_time', 'Unknown')
        user = note.get('user', {}).get('name', 'Unknown') 
        email = note.get('user', {}).get('email', 'Unknown')

        updated_add_time = modified_date(add_time)

        # Append to contents list
        contents.append({
            'organization_name': organization_name,
            'id': id,
            'content': content,
            'add_time': updated_add_time,
            'update_time': update_time,
            'user': user,
            'email': email
        })

    return contents
    
    # Get notes documentation here - https://developers.pipedrive.com/docs/api/v1/Notes

# Modify the date to be only the date, not the with the time
def modified_date(original_date):
    # Split the string
    dt_object = datetime.strptime(original_date, "%Y-%m-%d %H:%M:%S")

    return dt_object.strftime("%d/%m/%Y")

# Clean up note/comment - Removes html tags, etc.
def note_clean_up(note):
    soup = BeautifulSoup(note, "html.parser")

    text_after_BeautifulSoup  = soup.get_text()

    cleaned_note = html.unescape(text_after_BeautifulSoup)

    cleaned_note = cleaned_note.replace("\xa0", " ")

    return cleaned_note.strip() 

# Get company domain from api key - NOT IN USE
def get_company_domain(api_token):
    url = f'https://api.pipedrive.com/v1/users/me?api_token={api_token}'

    print('sending request...')

    response = requests.get(url)

    if response.status_code == 200:
        result = response.json()
        if 'data' in result and 'company_name' in result['data']:
            return result['data']['company_domain']
    else:
        print('Failed to retrieve data. Status code:', response.status_code)

if __name__ == '__main__':
    main()
