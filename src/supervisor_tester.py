from .supervisor import Supervisor
import numpy as np
import random
import json 

class SupervisorTester:
    supervisor: Supervisor
    def __init__(self, supervisor: Supervisor):
        self.supervisor = supervisor

    def test(self):
        # mock sensor data
        size = 101
        sensor_data = {}
        sensor_ids = []
        for sensor in self.supervisor.config.sensor_list:
            std_dev = int((sensor.high - sensor.low) / 2)
            mean = std_dev + random.randint(-std_dev, std_dev)
            data = np.random.normal(loc=mean, scale=(std_dev), size=size).astype(int)
            sensor_data[sensor.id] = data
            sensor_ids.append(sensor.id)

        # mock data for sensor 6
        sensor_data[6] = np.random.normal(loc=0.4, scale=5, size=size).astype(int)
        
        for i in range(size):
            for sensor_id in sensor_ids:
                json_data = {
                    'sensor_id': sensor_id,
                    'value': int(sensor_data[sensor_id][i]),
                    'timestamp': i
                }
                self.supervisor.handle_sensor_data(f'S_{sensor_id}', json.dumps(json_data))
                