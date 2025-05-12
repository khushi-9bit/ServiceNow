import requests
from requests.auth import HTTPBasicAuth

# Your instance details
INSTANCE = 'dev209062'
USERNAME = 'admin'
PASSWORD = ''

headers = {
    "Accept": "application/json"
}

# Date range parameters
start_date = "2024-05-09"
start_time = "00:00:00"
end_date = "2025-05-11"
end_time = "00:00:00"

# ServiceNow query for date filtering
date_filter_query = (
    f"sys_created_on>=javascript:gs.dateGenerate('{start_date}','{start_time}')^"
    f"sys_created_on<=javascript:gs.dateGenerate('{end_date}','{end_time}')"
)

# Pagination settings
limit = 100
offset = 0
all_incidents = []

while True:
    url = (
        f"https://{INSTANCE}.service-now.com/api/now/table/incident?"
        f"sysparm_query={date_filter_query}&sysparm_limit={limit}&sysparm_offset={offset}"
    )

    response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers)

    if response.status_code == 200:
        incidents = response.json().get('result', [])
        if not incidents:
            break  # Exit if no more data

        all_incidents.extend(incidents)
        offset += limit  # Move to next page
    else:
        print("Failed to fetch incidents")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        break

# Print all retrieved incidents
print(f"\nTotal incidents from {start_date} to {end_date}: {len(all_incidents)}")
for i, inc in enumerate(all_incidents, start=1):
    print(f"{i}. {inc['number']} | {inc['short_description']} | Created: {inc['sys_created_on']}")
print("THANK YOU")