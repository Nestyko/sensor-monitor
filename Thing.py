from rx.subjects import Subject
import requests
import socket
import json

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
        self.thing = None

    def __str__(self):
        return str(self.id) + ' ' + self.name

    def find_self(self, allThings):
        thing = load_thing()
        if thing:
            self.thing = thing
            return self.thing
        for thing in allThings:
            if 'mac' in thing and thing['mac'] in self.macs:
                self.thing = thing
                return thing
        return None


    def register(self):
        thing_response = None
        count = 0
        thing = self.__dict__
        thing['mac'] = thing['macs'][0]
        thing['macs'] = None
        s = requests.Session()
        s.headers.update({'access_token': conf['jwt']['token']})
        while count < 3:
            try:
                thing_response = s.post( str(base_url+'/thing') , data=thing, timeout=5)
                break
            except Exception:
                count += 1
                continue
        self.save_to_disk(thing_response)
        return thing_response
        
    def save_to_disk(self, thing_response):
        with open('thing.data.json', 'w') as outfile:
            json.dump(thing_response.json(), outfile, ensure_ascii=False, indent=4)
    
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

    def update_thing(self):
        if not self.thing:
            thing = load_thing()
            if thing:
                self.thing = thing
        r = requests.get(
            base_url+'/thing/'+self.thing['id'],
            headers={'access_token': conf['jwt']['token']})
        self.thing = r.json()

