import requests
from pprint import pprint
from config import load_config, load_thing, update_thing

class Service:

    def __init__(self):
        self.s = requests.Session()
        conf = load_config()
        self.base_url = conf['base_url']
        self.thing = load_thing()
        self.s.headers.update({'access_token': conf['jwt']['token']})
    
    def send_measure(self, measure):
        self.s.post(
            self.base_url+'/measure',
            data=measure
        )
    
    def create_sensor(self, sensor):
        sensor['thing'] = self.thing['id']
        r = self.s.post(
            self.base_url+'/sensor',
            data=sensor)
        pprint(r.json())
        thing = self.s.get(
            self.base_url+'/thing/'+str(self.thing['id'])
        )
        if(thing.status_code == 200):
            update_thing(thing.json())
            self.thing = thing.json()
        if(r.status_code == 201 or 200):
            return r.json()   
        return None

    def get_unit(self, unit_name):
        r = self.s.get(
            self.base_url+'/unit',
            params={'name': unit_name}
        )
        if r.status_code == 200:
            return r.json()[0]
        return None

    def get_sensors(self):
        if 'sensors' in self.thing:
            return self.thing['sensors']
        return []

    def get_groups(self, user):
        pass
