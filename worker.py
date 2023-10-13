import json
import os
import errno
import requests
import base64
import subprocess
import time
import ciso8601
import warnings
warnings.filterwarnings('ignore')

now = time.time()
max_tasks = 5
token = open('cookie').read().split('\n')[0]
user_id = token.split('.')
user_id = user_id[1].encode("ascii")
user_id =  base64.b64decode(user_id)
user_id = json.loads(user_id.decode("ascii"))['sub']
running_tasks = []

def Main():
    data = requests.get('https://hax.efragz.net/api/Task', headers={'Authorization': f'bearer {token}'} )
    data = data.json()

    for running_task in running_tasks:
        running_task.poll()
        if running_task.returncode != 'None':
            running_tasks.remove(running_task)
    
    if len(running_tasks) < max_tasks:
        for task in data:
            last_updated = time.mktime(ciso8601.parse_datetime(task['LastUpdated']).timetuple())
            if ((now - last_updated) > 86400 and task['Status'] == 'Complete') or (task['Status'] == 'New'):
                if task['Type'] == 'MX':
                    process = subprocess.Popen(['python', 'mx.py', json.dumps(task)])
                    running_tasks.append(process)
                elif task['Type'] == 'Domain':
                    process = subprocess.Popen(['python', 'domains.py', json.dumps(task)])
                    running_tasks.append(process)
                elif task['Type'] == 'Services':
                    process = subprocess.Popen(['python', 'services.py', json.dumps(task)])
                    running_tasks.append(process)

                update_data = {'Status': 'Running', 'AssignedTo': user_id }
                response = requests.put('https://hax.efragz.net/api/Task/'+str(task['ID']), headers={'Authorization': f'bearer {token}'}, json=update_data)
    time.sleep(240)
    Main()

Main()