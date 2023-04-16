from dataclasses import dataclass
from enum import Enum

@dataclass
class SensorData:
    sensor_id: str
    timestamp: str
    value: str # high or low

@dataclass
class Alarm:
    sensor_id: str
    value: Enum

class Sensor:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.faults_associated = 0
        self.data = []

    def onDataReceived(self, data: SensorData, checkForAnomaly: bool) -> Alarm | None:
        self.data.append({
            'timestamp': data['timestamp'],
            'value': data['value']
        })

        if checkForAnomaly:
            return Alarm(self.id, 'high')
            # TODO Implement anomaly detection

