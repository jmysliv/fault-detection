from dataclasses import dataclass
from typing import List
from .symptom import Symptom
@dataclass
class SensorData:
    sensor_id: int
    timestamp: str
    value: int

@dataclass
class Alarm:
    sensor_id: int
    value: str # high or low

avg_length = 100
class Sensor:
    name: str
    id: int
    low: int
    high: int
    data: List[SensorData]
    def __init__(self, name: str, id: int, low: int, high: int):
        self.name = name
        self.id = id
        self.low = low
        self.high = high
        self.data = []

    def get_symptom_probability(self, symptom: Symptom) -> float:
        if symptom.sensor_id != self.id:
            return 0

        avg_value = sum([d['value'] for d in self.data[-avg_length:]]) / avg_length
        if symptom.value == 'low':
            return min(1 - (avg_value - self.low) / (self.high - self.low), 1)
        else:
            return min(1 - (self.high - avg_value) / (self.high - self.low), 1)

    def on_data_received(self, data: SensorData, checkForAnomaly: bool) -> Alarm | None:
        self.data.append({
            'timestamp': data['timestamp'],
            'value': data['value']
        })

        if checkForAnomaly and len(self.data) > avg_length:
            avg_value = sum([d['value'] for d in self.data[-avg_length:]]) / avg_length
            print(avg_value)
            if avg_value < self.low:
                return Alarm(self.id, 'low')
            elif avg_value > self.high:
                return Alarm(self.id, 'high')
            return None

