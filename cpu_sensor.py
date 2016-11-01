import psutil
from service import Service
import time
import threading

from pprint import pprint

class CpuSensor(threading.Thread):

    def __init__(self, sensors, service):
        self.exit = False
        threading.Thread.__init__(self)
        sensors = [sensor for sensor in sensors if sensor['type'] == 'cpu']
        self.sensors = []
        self.interval = 5 #seconds
        num_of_cores = psutil.cpu_count()
        self.service = service
        self.unit = self.service.get_unit('Percentage', abbreviation='%', unit_type='percentage')
        for x in range(1,num_of_cores+1):
            created = False
            for sensor in sensors:
                if 'name' in sensor and (sensor['name'].endswith(str(x))):
                    created = True
                    self.sensors.append(sensor)
            if not created:
                sensor = {
                    'name': 'CPU #'+str(x),
                    'type': 'cpu',
                    'lastMeasure': None
                }
                sensor = self.service.create_sensor(sensor)
                if sensor:
                    self.sensors.append(sensor)


    def run(self):
        counter = 0
        while not self.exit:
            refreshRate = int(int(self.service.thing['refreshRate'])/1000)
            if(counter >= refreshRate):
                counter = 0
                measures = psutil.cpu_percent(percpu=True)
                
                for index, val in enumerate(measures):
                    measure = {
                        'sensor': self.sensors[index]['id'],
                        'unit' : self.unit['id'],
                        'value': val
                    }
                    print('{name}: {value}{unit}'.format(
                        name=self.sensors[index]['name'],
                        value=val,
                        unit=self.unit['abbreviation']
                    ))
                    self.service.send_measure(measure)
                
            counter += 1
            time.sleep(1)
        print('exiting thread')


