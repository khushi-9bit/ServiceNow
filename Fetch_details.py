import requests
from requests.auth import HTTPBasicAuth

# Your instance details
INSTANCE = 'dev209062'
USERNAME = 'admin'
PASSWORD = ''

incident_number = "INC0000040"

headers = {
    "Accept": "application/json"
}

#Step 1: Get incident record to extract sys_id
incident_url = f"https://{INSTANCE}.service-now.com/api/now/table/incident?sysparm_query=number={incident_number}"

response = requests.get(incident_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers)

if response.status_code == 200:
    result = response.json().get('result', [])
    if not result:
        print("No incident found with that number.")
    else:
        incident = result[0]
        sys_id = incident['sys_id']
        print("Incident Details:")
        for k, v in incident.items():
            print(f"{k}: {v}")

        # Step 2: Get Attachments
        attachment_url = f"https://{INSTANCE}.service-now.com/api/now/attachment?sysparm_query=table_sys_id={sys_id}"
        attach_response = requests.get(attachment_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers)

        if attach_response.status_code == 200:
            attachments = attach_response.json().get('result', [])
            if not attachments:
                print("No attachments found.")
            else:
                print("\nAttachments:")
                for att in attachments:
                    print(f"- File: {att['file_name']}")
                    print(f"  Size: {att['size_bytes']} bytes")
                    print(f"  Download URL: {att['download_link']}")
        else:
            print("Failed to fetch attachments.")
            print(attach_response.status_code, attach_response.text)

        # ✅ Step 3: Fetch Comments and Work Notes from sys_journal_field
        journal_url = f"https://{INSTANCE}.service-now.com/api/now/table/sys_journal_field?sysparm_query=element_id={sys_id}&sysparm_limit=100"

        journal_response = requests.get(journal_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers)

        if journal_response.status_code == 200:
            journals = journal_response.json().get('result', [])
            if not journals:
                print("\nNo journal entries (comments or work notes) found.")
            else:
                print("\nJournal Entries (Activity Section):")
                for j in journals:
                    entry_type = j.get('element', 'unknown')
                    entry_value = j.get('value', '')
                    created = j.get('sys_created_on', '')
                    created_by = j.get('sys_created_by', '')
                    print(f"- [{entry_type.upper()}] {created} by {created_by}:\n  {entry_value}\n")
        else:
            print("Failed to fetch journal entries.")
            print(journal_response.status_code, journal_response.text)

else:
    print("Failed to fetch incident.")
    print(response.status_code, response.text)

