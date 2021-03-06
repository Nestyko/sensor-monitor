import requests
import socket
import json
from service import Service

import netifaces as nif

from config import load_config, load_thing

conf = load_config()
base_url = conf['base_url']

class Thing:
    
    def __init__(self):
        self.id = None
        self.name = None
        self.domain = None
        self.ip = self.getLocalIp()
        self.macs = self.getMacs()
        self.alert = None
        self.sensors = []
        self.group = None
        self.service = Service()
        self.thing = None


    def __str__(self):
        return str(self.id) + ' ' + self.name

    def find_self(self, allThings):
        for thing in allThings:
            if 'mac' in thing and thing['mac'] in self.macs:
                self.thing = thing
                self.service.setThing(thing)
                return thing
        return None


    def register(self):
        thing_response = None
        count = 0
        thing = self.__dict__
        thing['mac'] = thing['macs'][0]
        thing['macs'] = None
        thing['service'] = None
        s = Service().s
        while count < 3:
            try:
                thing_response = s.post( str(base_url+'/thing') , data=thing, timeout=5)
                break
            except Exception as e:
                print(e)
                count += 1
                continue
        self.save_to_disk(thing_response=thing_response)
        return thing_response
        
    def save_to_disk(self, thing_response=None):
        with open('thing.data.json', 'w') as outfile:
            if thing_response:
                json.dump(thing_response.json(), outfile, ensure_ascii=False, indent=4)
            else:
                json.dump(self.thing, outfile, ensure_ascii=False, indent=4)
    
    def getMacs(self):
        macs = []
        for i in nif.interfaces():
            addrs = nif.ifaddresses(i)
            try:
                if_mac = addrs[nif.AF_LINK][0]['addr']
            except KeyError:
                if_mac = if_ip = None
            except IndexError:
                if_mac = if_ip = None
            if if_mac == '' or if_mac.startswith('00:00'):
                continue
            macs.append(if_mac)
        return macs

    def getLocalIp(self):
        ip = socket.gethostbyname(socket.gethostname())
        if ip == '127.0.0.1' or 'localhost' or '0.0.0.0':
            ip = socket.gethostbyname(socket.getfqdn())
        return ip

    def update_thing(self, thingId):
        if not self.thing:
            thing = load_thing()
            if thing:
                self.thing = thing
        r = requests.get(
            base_url+'/thing/'+self.thing['id'],
            headers={'access_token': conf['jwt']['token']})
        if(r.status_code == 200):
            self.thing = r.json()
            self.save_to_disk();
        else:
            print('Error updating the thing')

