#!/usr/bin/env python3
import requests
import sys
import json

# Your Wappsto Username and Password
username = ""
password = ""

# THe type of values that you want to get the log from
valuesToLog = ["energy", "total_energy"]

# The API endpoint
url = "https://wappsto.com/services/2.1"
headers = {"Content-Type": "application/json; charset=utf-8"}
logQuery = "type_timestamp=internal&request=updated&limit=1000"
session = ""

try:
    response = requests.post(url + "/session",
        headers=headers,
        json={
            "username": username,
            "password": password
        }
    )
    session = response.json()['meta']['id']
    headers['x-session'] = session
except Exception as e:
    sys.exit("Failed to login", e)
else:
    print("Logged in to wappsto.com with session", session)

# Get all networks
response = requests.get(url + '/network', headers=headers)

networks = response.json()['id']
for id in networks:
    devices = []
    try:
        print("Loading network", id)
        response = requests.get(url + '/network/' + id + "?expand=3", headers=headers)
        devices = response.json()['device']
    except Exception as e:
        print("Failed to load network", id)
        continue

    for device in devices:
        for value in device['value']:
            if type(value) is str:
                try:
                    response = requests.get(url + '/value/' + value + "?expand=2", headers=headers)
                    value = response.json()
                except Exception as e:
                    print("Failed to load value", value)
                    continue
            if value['type'] in valuesToLog:
                if type(value['state'][0]) is str:
                    continue
                print("Loading log values for", value['name'], "with type", value['type'])
                logID = value['state'][0]['meta']['id']
                last = ""
                data = []

                while True:
                    if last != "":
                        response = requests.get(url + '/log/' + logID + "/state?" + logQuery + "&start=" + last, headers=headers)
                    else:
                        response = requests.get(url + '/log/' + logID + "/state?" + logQuery, headers=headers)
                    logs = response.json()
                    print("Log data count", len(logs['data']), logs['data'][0]['time'], "=>", logs['data'][-1]['time'])
                    last = logs['data'][-1]['updated']
                    data.extend(logs['data'])
                    if logs['more'] == False:
                        break

                with open(logID+".json", 'w') as file:
                    file.write(json.dumps(data))
