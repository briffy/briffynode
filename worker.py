import json
import os
import errno
import requests
import base64
import subprocess
from multiprocessing import Process, Pool
import time
import ciso8601
import dns.zone
import dns.resolver
import socket
import urllib3
import random
import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info('Starting Sojourner scanning node...')

urllib3.disable_warnings()

now = time.time()
max_running_tasks = 10
token = open('cookie').read().split('\n')[0]
user_id = token.split('.')
user_id = user_id[1].encode("ascii")
user_id =  base64.b64decode(user_id)
user_id = json.loads(user_id.decode("ascii"))['sub']
running_tasks = []

def scan_MX(task):
    try:
        new_records = []

        records = dns.resolver.resolve(task['Domain'], 'MX')
        for x in dns.resolver.resolve(task['Domain'], 'MX'):
            record = x.to_text().split(' ')[1]
            update_data = {'ParentID': task['ParentID'], 'Value': record}
            new_records.append(update_data)
        response = requests.post('https://hax.efragz.net/api/MX/', headers={'Authorization': f'bearer {token}'}, json=new_records)
        logging.info('Added MX Record to ID: %s', task['ParentID'])
    except Exception as e:
        exit(1)
    finally:
        update_data = {'Status': 'Complete', 'AssignedTo': None }
        response = requests.put('https://hax.efragz.net/api/Task/'+str(task['ID']), headers={'Authorization': f'bearer {token}'}, json=update_data)

def scan_domains(task):

    new_records = []
    results = []

    subdomains = open('subdomains', 'r')
    subdomains = subdomains.readlines()

    for subdomain in subdomains:
        url = subdomain.strip("\n")+'.'+task['Domain']
        try:
            records = dns.resolver.resolve(url, 'A')
            results.append(url)
        except:
            pass
    
    for result in results:
        new_record = {'Value': result}
        new_records.append(new_record)

    response = requests.post('https://hax.efragz.net/api/Subdomains/'+str(task['ParentID']), headers={'Authorization': f'bearer {token}'}, json=new_records)
    logging.info('Added subdomain: %s', result)
    try:
        records = dns.resolver.resolve(task['Domain'], 'TXT')
        for record in records:
            if 'v=spf' in str(record):
                spf = str(record).replace('"','')
    except:
        spf = 'None'
        pass

    try:
        records = dns.resolver.resolve('_dmarc.'+task['Domain'], 'TXT')
        for record in records:
            if 'DMARC' in str(record):
                dmarc = str(record).replace('"', '')
    except:
        dmarc = 'None'
        pass

    update_data = { 'DMARC': dmarc, 'SPF': spf }
    response = requests.put('https://hax.efragz.net/api/Domain/'+str(task['ParentID']), headers={'Authorization': f'bearer {token}'}, json=update_data)
    logging.info(f'Added DMARC/SPFC Record to ID: %s', task['ParentID'])
    update_data = {'Status': 'Complete', 'AssignedTo': None }
    response = requests.put('https://hax.efragz.net/api/Task/'+str(task['ID']), headers={'Authorization': f'bearer {token}'}, json=update_data)

def check_port(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.2)
    try:
        s.connect((host, port))
    except:
        return False
    else:
        return True
    finally:
        s.close()

def scan_services(task):
    ports = [ 21, 22, 25, 80, 139, 443, 8080, 8443 ]

    subdomains = requests.get('https://hax.efragz.net/api/Subdomains/'+str(task['ParentID']), headers={'Authorization': f'bearer {token}'} )
    subdomains = subdomains.json()

    services = []

    for subdomain in subdomains:
        for port in ports:
            port_open = check_port(subdomain['Value'], port)

            if port_open == True:
                info = 'No info'

                value = { 'ParentID': subdomain['ID'], 'Port': port, 'Info': info }
                services.append(value)

    response = requests.post('https://hax.efragz.net/api/Service/'+str(task['ParentID']), headers={'Authorization': f'bearer {token}'}, json=services)

    update_data = {'Status': 'Complete', 'AssignedTo': None }
    response = requests.put('https://hax.efragz.net/api/Task/'+str(task['ID']), headers={'Authorization': f'bearer {token}'}, json=update_data)

def scan_subdirectories_parallel(url):
    try:
        sleeptime = random.randint(6, 12)
        time.sleep(sleeptime)
        redirect = False
        response = requests.get(url['Value'], verify=False)

        for history in response.history:
            if history.status_code == 302:
                redirect = True

        if response.status_code == 200 and redirect == False:
            new_data = [{'Value': url['Word'], 'ParentID': url['ParentID'], 'Type': 'GET'}]
            response = requests.put('https://hax.efragz.net/api/Subdirectory/', headers={'Authorization': f'bearer {token}'}, json=new_data)
            logging.info(f'Added subdirectory: %s', url['Value'])
    except:
        pass

def scan_subdirectories(task):
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
    urls = []
    for result in results:
        for word in word_list:
            if int(result['Port']) == 80 or int(result['Port'] == 8080):
                protocol = 'http://'
            else:
                protocol = 'https://'

            url = {'Word': word, 'ParentID': result['ParentID'], 'Process': None, 'Value': protocol+result['Domain']+':'+result['Port']+'/'+word}
            urls.append(url)

    with Pool(processes=4) as pool:
        pool.map(scan_subdirectories_parallel, urls)
                
    update_data = {'Status': 'Complete', 'AssignedTo': None }
    response = requests.put('https://hax.efragz.net/api/Task/'+str(task['ID']), headers={'Authorization': f'bearer {token}'}, json=update_data)


def main():
    results = requests.get('https://hax.efragz.net/api/Task', headers={'Authorization': f'bearer {token}'} )
    results = results.json()

    for running_task in running_tasks:
        if running_task.is_alive() == False:
            running_tasks.remove(running_task)

    for result in results:
        if len(running_tasks) < max_running_tasks:
            last_updated = time.mktime(ciso8601.parse_datetime(result['LastUpdated']).timetuple())
            if ((now - last_updated) > 86400) or (result['Status'] == 'New'):
                if result['Type'] == 'MX':
                    process = Process(target=scan_MX,args=[result])
                    running_tasks.append(process)
                    process.start()
                    update_data = {'Status': 'Running', 'AssignedTo': user_id }
                    response = requests.put('https://hax.efragz.net/api/Task/'+str(result['ID']), headers={'Authorization': f'bearer {token}'}, json=update_data)

                elif result['Type'] == 'Domain':      
                    process = Process(target=scan_domains,args=[result])
                    running_tasks.append(process)
                    process.start()
                    update_data = {'Status': 'Running', 'AssignedTo': user_id }
                    response = requests.put('https://hax.efragz.net/api/Task/'+str(result['ID']), headers={'Authorization': f'bearer {token}'}, json=update_data)

                elif result['Type'] == 'Services':
                    for prerequisite in results:
                        if (result['ParentID'] == prerequisite['ParentID']) and (prerequisite['Type'] == 'Domain') and (prerequisite['Status'] == 'Complete'):
                            process = Process(target=scan_services,args=[result])
                            running_tasks.append(process)
                            process.start()
                            update_data = {'Status': 'Running', 'AssignedTo': user_id }
                            response = requests.put('https://hax.efragz.net/api/Task/'+str(result['ID']), headers={'Authorization': f'bearer {token}'}, json=update_data)

                elif result['Type'] == 'Subdirectory':
                    for prerequisite in results:
                        if (result['ParentID'] == prerequisite['ParentID']) and (prerequisite['Type'] == 'Services') and (prerequisite['Status'] == 'Complete'):
                            process = Process(target=scan_subdirectories,args=[result])
                            running_tasks.append(process)
                            process.start()
                            update_data = {'Status': 'Running', 'AssignedTo': user_id }
                            response = requests.put('https://hax.efragz.net/api/Task/'+str(result['ID']), headers={'Authorization': f'bearer {token}'}, json=update_data)

                

    time.sleep(5)
    main()

if __name__ == '__main__':
    main()