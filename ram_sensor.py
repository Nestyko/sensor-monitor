import psutil
from service import Service
import threading, time

class RamSensor(threading.Thread):

    def create_sensor(self, available_sensor):
        sensor = {
            'name': available_sensor['name'],
            'type': 'ram',
            'lastMeasure': None,
        }
        return self.service.create_sensor(sensor)

    def __init__(self, sensors, service):
        threading.Thread.__init__(self)
        self.exit = False
        self.service = service
        sensors = [sensor for sensor in sensors if sensor['type'] == 'ram']
        self.sensors = []
        self.sensors_available = [
        {
            'name': 'total',
            'unit': 'Byte',
            'created': False
        },{
            'name': 'available',
            'unit': 'Byte',
            'created': False
        },{
            'name': 'percent',
            'unit': 'Percentage',
            'created': False
        },{
            'name':'used',
            'unit':'Byte',
            'created': False
        } 
        ]
        #Gets or creates units if doesnt already exists
        self.units = {
            'byte': self.service.getUnit('Byte', abbreviation='B', type="Memory"),
            'percentage': self.service.getUnit('Percentage', abbreviation='%', type="Percentage")
        }
        for sensor in sensors:
            if 'name' in sensor:
                for available_sensor in self.sensors_available:
                    if sensor['name'] == available_sensor['name']:
                        available_sensor['created'] = True
                        self.sensors.append(sensor)
            for available_sensor in self.sensors_available:
                if available_sensor['created'] == False:
                    created_sensor = self.create_sensor(available_sensor)
                    if created_sensor:
                        self.sensors.append(created_sensor)
                    else:
                        print('error creando sensor de ram')

    
    def run(self):
        counter = 0
        while not self.exit:
            refreshRate = int(int(self.service.thing['refreshRate'])/1000)
            if(counter >= refreshRate):
                counter = 0
                vm = psutil.virtual_memory()
                measures = []
                
                for sensor in self.sensors:
                    measure = None
                    if sensor['name'] == 'total':
                        measure = {
                            'sensor': sensor['id'],
                            'unit': self.units['byte'],
                            'value': vm.total
                        }
                        measures.append(measure)
                    if sensor['name'] == 'available':
                        measure = {
                            'sensor': sensor['id'],
                            'unit': self.units['byte'],
                            'value': vm.available
                        }
                        measures.append(measure)
                    if sensor['name'] == 'percent':
                        measure = {
                            'sensor': sensor['id'],
                            'unit': self.units['percentage'],
                            'value': vm.percent
                        }
                        measures.append(measure)
                    if sensor['name'] == 'used':
                        measure = {
                            'sensor': sensor['id'],
                            'unit': self.units['byte'],
                            'value': vm.used
                        }
                        measures.append(measure)
                for measure in measures:
                    self.service.send_measure(measure)
            counter += 1
            time.sleep(1)
        print('exiting thread')
                    
