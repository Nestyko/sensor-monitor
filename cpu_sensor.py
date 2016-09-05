import psutil
import rx
from service import Service
import time
import threading

from pprint import pprint

class CpuSensor(threading.Thread):

    def __init__(self, sensors):
        self.cpus = rx.subjects.Subject()
        threading.Thread.__init__(self)
        sensors = [sensor for sensor in sensors if sensor['type'] == 'cpu']
        self.sensors = []
        self.interval = 5 #seconds
        num_of_cores = psutil.cpu_count()
        self.s = Service()
        self.unit = self.s.get_unit('Percentage')
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
                sensor = self.s.create_sensor(sensor)
                if sensor:
                    self.sensors.append(sensor)


    def run(self):
        while True:
            measures = psutil.cpu_percent(percpu=True)
            
            for index, val in enumerate(measures):
                measure = {
                    'sensor': self.sensors[index]['id'],
                    'unit' : self.unit['id'],
                    'value': val
                }
                pprint(measure)
                self.s.send_measure(measure)
            time.sleep(self.interval)


