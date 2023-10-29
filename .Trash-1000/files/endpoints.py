import sys
import json
import base64
import requests
import urllib3

urllib3.disable_warnings()

task = json.loads(sys.argv[1])

token = open('cookie').read().split('\n')[0]

subdomains = []
results = []
new_data = []
known_ports = [ 21, 22, 25, 139, 587 ]

with open('subdirectories', 'r') as file:
        word_list = [line.strip() for line in file]

subdomains.append({ 'ParentID': task['ParentID'], 'Value': task['Domain']})

data = requests.get('https://hax.efragz.net/api/Subdomains/'+str(task['ParentID']), headers={'Authorization': f'bearer {token}'} )

data = data.json()

for subdomain in data:
    subdomains.append({ 'ParentID': subdomain['ID'], 'Value': subdomain['Value'] })

for subdomain in subdomains:
        services = requests.get('https://hax.efragz.net/api/Service/'+str(subdomain['ParentID']), headers={'Authorization': f'bearer {token}'} )
        services = services.json()
        
        for service in services:
            known = False
            for port in known_ports:
                if port == int(service['Port']):
                    known = True

            if known == False:
                service['ParentID'] = subdomain['ParentID']
                results.append(service)

for result in results:
    for word in word_list:
        if int(result['Port']) == 80:
            protocol = 'http://'
        else:
            protocol = 'https://'

        url = protocol+result['Domain']+':'+result['Port']+'/'+word

        try:
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                new_data.append({'ParentID': result['ParentID'], 'Value': word, 'Type': 'GET'})
        # If there's an error
        except Exception as e:
            pass

print(new_data)