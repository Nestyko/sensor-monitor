import requests
from pprint import pprint
from config import load_config, load_thing, update_thing
from Auth import Authentication

class Service:

    def __init__(self, thing_id=None):
        self.s = requests.Session()
        conf = load_config()
        self.base_url = conf['base_url']
        
        self.s.headers.update({'access_token': conf['jwt']['token']})
        if thing_id:
            self.thing = self.getThing(thing_id)

    def validateJwt(self):
        user_id = ''
        try:
            user_id = '/'+ conf['user_id']
        except Exception:
            pass
        dummy = self.s.get('/user'+user_id)
        if dummy.status_code == 403:
            auth = Authentication()
            if auth.is_auth:
                return True
            else:
                return False
        elif dummy.status_code == 200:
            return True
        else:
            return False
    
    def send_measure(self, measure):
        self.s.post(
            self.base_url+'/measure',
            data=measure
        )
    
    def setThing(self, thing):
        id = thing['id']
        self.thing = self.getThing(id=id)

    def getThing(self, id=None):
        if not id:
            id = self.thing['id']
        res = self.s.get(self.base_url+'/thing/{}'.format(id))
        if(res.status_code == 200):
            return res.json()
        elif(res.status_code == 403):
            #JWT expired
            self.validateJwt()
        elif(res.status_code == 404):
            #Definetely deleted
            print('404')
            quit()
        else:
            #One posible thing happening here is the deleting of the Thing
            print('Error getting the thing')
            return None

    def getUpdateRefreshRate(self):
        aux = self.getThing()
        print('polling')
        if aux['refreshRate'] != self.thing['refreshRate']:
            print('refresh rate updated to {}'.format(aux['refreshRate']))
            self.thing['refreshRate'] = aux['refreshRate']
            return True
        return False

    
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

    def get_unit(self, unit_name, abbreviation=None, unit_type=None):
        r = self.s.get(
            self.base_url+'/unit',
            params={'name': unit_name}
        )
        if r.status_code == 200:
            return r.json()[0]
        else:
            if not unit_type:
                return
            data = {
                    'name': unit_name,
                    'type': unit_type
                }
            if abbreviation:
                data['abbreviation'] = abbreviation
            r = self.s.post(
                self.base_url+'/unit',
                data=data
            )
            if r.status_code < 400:
                return r.json()

    def get_sensors(self):
        if self.thing and 'sensors' in self.thing:
            return self.thing['sensors']
        return []

    def get_groups(self, user):
        pass
