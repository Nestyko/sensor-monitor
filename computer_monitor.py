import psutil
import time
import requests as req

import pprint
import config
from Auth import Authentication

url = config.base_url # Validate the config file

measureUrl = url + "measure"
thing_url = url + "thing"

pp = pprint.PrettyPrinter(indent=4)
"""
name_ok = False
while not name_ok:
    #name = input('Enter the name: ')
    name = "Nestor-PC"
    name = name.replace(" ", "_")
    name_request = req.get(thing_url + "?name=" + name)
    pp.pprint(name_request.json())
    if(name_request.status_code != 200):
        print('Error asking to the server, try again')
        continue
    if(name_request.json() == []):
        name_ok = True
        continue
    else:
        print("Error the name is repeated")
"""
while True:
    print("CPU")
    ram = psutil.virtual_memory().used
    cpu = psutil.cpu_percent()
    data = [{
        "value": cpu,
        "unit": 3,
        "sensor": 1
    },{
        "value": ram,
        "unit": 1,
        "sensor": 3
    }]
    print('data:')
    pp.pprint(data)
    try:
        req.post(measureUrl, json=data, timeout=1)
    except ConnectionError as ce:
        pp.pprint(ce)
        print('Conecction error')
    except TimeoutError as te:
        print('Timeout')
    except:
        print('Error')
    time.sleep(5)
    