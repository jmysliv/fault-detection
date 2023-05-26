from dataclasses import dataclass
from typing import List
from .symptom import Symptom
import numpy as np

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

def weighted_average(time_series):
    weights = np.arange(1, len(time_series) + 1)  # Increasing weights
    weighted_sum = np.sum(time_series * weights)
    weight_sum = np.sum(weights)
    weighted_avg = weighted_sum / weight_sum
    return weighted_avg

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
        # refactor
        if symptom.sensor_id != self.id or len(self.data) < avg_length:
            return 0
        
        avg = weighted_average([d['value'] for d in self.data[-avg_length:]])
        range = (self.high - self.low)

        if symptom.value == 'low':
            low_probability = 0.5 - 2 * (avg - self.low) / range
            return max(min(low_probability, 1), 0)
        elif symptom.value == 'ok':
            ok_probability = 1.5 - abs(2 * (avg - (self.high - range/2)) / range)
            return max(min(ok_probability, 1), 0)
        else:
            high_probability = 0.5 + 2 * (avg - self.high) / range
            return max(min(high_probability, 1), 0)

    def on_data_received(self, data: SensorData, checkForAnomaly: bool) -> Alarm | None:
        self.data.append({
            'timestamp': data['timestamp'],
            'value': data['value']
        })

        if checkForAnomaly and len(self.data) > avg_length:
            avg_value = weighted_average([d['value'] for d in self.data[-avg_length:]])
            print(avg_value)
            if avg_value < self.low:
                return Alarm(self.id, 'low')
            elif avg_value > self.high:
                return Alarm(self.id, 'high')
            return None

