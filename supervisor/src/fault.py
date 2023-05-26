from typing import List
from .symptom import Symptom

class Fault:
    id: int
    name: str
    symptoms: List[Symptom]
    reasons: List[str]
    actions: List[str]
    def __init__(self, id: int, name: str, symptoms: List[Symptom], reasons: List[str], actions: List[str]):
        self.id = id
        self.name = name
        self.symptoms = symptoms
        self.reasons = reasons
        self.actions = actions


    def has_symptom(self, sensor_id: int, value: str) -> bool:
        for symptom in self.symptoms:
            if symptom.sensor_id == sensor_id and symptom.value == value:
                return True
        return False