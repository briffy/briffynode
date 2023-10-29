import sys
import json
import requests
import socket
import warnings
from threading import Thread, Lock
from queue import Queue

warnings.filterwarnings('ignore')

task = json.loads(sys.argv[1])
token = open('cookie').read().split('\n')[0]

ports = [ 21, 22, 25, 80, 139, 443, 8080, 8443 ]

subdomains = requests.get('https://hax.efragz.net/api/Subdomains/'+str(task['ParentID']), headers={'Authorization': f'bearer {token}'} )
subdomains = subdomains.json()

services = []

N_THREADS = 200

q = Queue()

print_lock = Lock()

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


for subdomain in subdomains:
    for port in ports:
        port_open = check_port(subdomain['Value'], port)

        if port_open == True:
            info = 'No info'

            value = { 'ParentID': subdomain['ID'], 'Port': port, 'Info': info }
            services.append(value)

response = requests.post('https://hax.efragz.net/api/Service/'+str(task['ParentID']), headers={'Authorization': f'bearer {token}'}, json=services)
print(services)
update_data = {'Status': 'Complete', 'AssignedTo': None }
response = requests.put('https://hax.efragz.net/api/Task/'+str(task['ID']), headers={'Authorization': f'bearer {token}'}, json=update_data)

exit(0)