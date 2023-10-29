import sys
import json
import base64
import requests
import dns.zone
import dns.resolver

def scan_subdomains(address):
    results = []

    for subdomain in subdomains:
        try:
            url = subdomain.strip("\n")+'.'+task['Domain'].strip('\n')
            records = dns.resolver.resolve(url, 'A')
            results.append(url)
        except Exception as e:
            pass
        
    return results

try:
    task = json.loads(sys.argv[1])

    token = open('cookie').read().split('\n')[0]
    user_id = token.split('.')
    user_id = user_id[1].encode("ascii")
    user_id = base64.b64decode(user_id)
    user_id = json.loads(user_id.decode("ascii"))['sub']
    new_records = []

    subdomains = open('subdomains.txt', 'r')
    subdomains = subdomains.readlines()

    subdomains = scan_subdomains(task['Domain'])
    
    for subdomain in subdomains:
        new_record = {'Value': subdomain}
        new_records.append(new_record)

    response = requests.post('https://hax.efragz.net/api/Subdomains/'+str(task['ParentID']), headers={'Authorization': f'bearer {token}'}, json=new_records)

    records = dns.resolver.resolve(task['Domain'], 'TXT')
    for record in records:
        if 'v=spf' in str(record):
            spf = str(record).replace('"','')

    records = dns.resolver.resolve('_dmarc.'+task['Domain'], 'TXT')
    for record in records:
        if 'DMARC' in str(record):
            dmarc = str(record).replace('"', '')

    update_data = { 'DMARC': dmarc, 'SPF': spf }
    response = requests.put('https://hax.efragz.net/api/Domain/'+str(task['ParentID']), headers={'Authorization': f'bearer {token}'}, json=update_data)

    exit(0)
except Exception as e:
    exit(1)
finally:
    update_data = {'Status': 'Complete', 'AssignedTo': None }
    response = requests.put('https://hax.efragz.net/api/Task/'+str(task['ID']), headers={'Authorization': f'bearer {token}'}, json=update_data)
