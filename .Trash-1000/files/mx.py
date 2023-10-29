import sys
import dns.resolver
import json
import base64
import requests

try:
    task = json.loads(sys.argv[1])

    token = open('cookie').read().split('\n')[0]
    user_id = token.split('.')
    user_id = user_id[1].encode("ascii")
    user_id = base64.b64decode(user_id)
    user_id = json.loads(user_id.decode("ascii"))['sub']
    new_records = []

    records = dns.resolver.resolve(task['Domain'], 'MX')
    for x in dns.resolver.resolve(task['Domain'], 'MX'):
        record = x.to_text().split(' ')[1]
        update_data = {'ParentID': task['ParentID'], 'Value': record}
        new_records.append(update_data)
    response = requests.post('https://hax.efragz.net/api/MX/', headers={'Authorization': f'bearer {token}'}, json=new_records)

    exit(0)
except Exception as e:
    exit(1)
finally:
    update_data = {'Status': 'Complete', 'AssignedTo': None }
    response = requests.put('https://hax.efragz.net/api/Task/'+str(task['ID']), headers={'Authorization': f'bearer {token}'}, json=update_data)
