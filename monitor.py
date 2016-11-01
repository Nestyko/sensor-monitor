from cpu_sensor import CpuSensor
from service import Service
from ram_sensor import RamSensor
import threading
import time

class Monitor:

    def __init__(self, thing_id):
        self.s = Service(thing_id=thing_id)
        self.start()
        self.initThreads()
        while True:
            if self.s.getUpdateRefreshRate():
                pass
                #self.restart()
            time.sleep(10)

    
    def start(self):
        self.threads = []
        
        sensors = self.s.get_sensors()
        cpu_monitor = CpuSensor(sensors, self.s)
        ram_sensor = RamSensor(sensors, self.s)
        self.threads.append(cpu_monitor)
        self.threads.append(ram_sensor)


    def initThreads(self):
        for t in self.threads:
            t.start()
    
    def restart(self):
        for t in self.threads:
            t.exit = True
            t.join()
        self.start()
        self.initThreads()
        
        
