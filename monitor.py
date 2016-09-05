from cpu_sensor import CpuSensor
from service import Service

class Monitor:

    def __init__(self):
        self.threads = []
        self.s = Service()
        sensors = self.s.get_sensors()
        cpu_monitor = CpuSensor(sensors)
        self.threads.append(cpu_monitor)
    
    def start(self):
        for t in self.threads:
            t.start()
        
