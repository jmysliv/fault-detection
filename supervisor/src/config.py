import yaml
from .sensor import Sensor
from .symptom import Symptom
from .fault import Fault
from typing import List

class Config:
    faults: List[Fault]
    sensor_list: List[Sensor]

    def __init__(self):
        # Load the YAML file
        with open('supervisor/config/sensors.yaml', 'r') as f:
            data = yaml.safe_load(f)

        sensors = data.get('sensors', {})

        # Create an array of Sensor objects
        self.sensor_list = []
        for sensor_name, sensor_data in sensors.items():
            # Get the ID of the sensor
            sensor_id = sensor_data.get('id', None)
            sensor_low = sensor_data.get('low', None)
            sensor_high = sensor_data.get('high', None)
            # Create a new Sensor object and add it to the list
            sensor = Sensor(sensor_name, sensor_id, sensor_low, sensor_high)
            self.sensor_list.append(sensor)

        # get fault cards
        with open('supervisor/config/faults.yaml', 'r') as f:
                data = yaml.safe_load(f)
        faults = data.get('faults', {})
        self.faults = []
        for fault in faults:
            id = fault.get('id', None)
            fault_name = fault.get('name', None)
            symptoms = fault.get('symptoms', [])
            reasons = fault.get('reasons', [])
            symptom_list = []
            for symptom in symptoms:
                sensor_id = symptom.get('sensor_id', None)
                value = symptom.get('value', None)
                temporal = symptom.get('temporal', None)
                symptom_list.append(Symptom(sensor_id, value, temporal))
            reason_list = []
            action_list = []
            for reason in reasons:
                name = reason.get('name', None)
                action = reason.get('action', None)
                reason_list.append(name)
                action_list.append(action)
            self.faults.append(Fault(id, fault_name, symptom_list, reason_list, action_list))

    def get_sensor(self, sensor_id: int) -> Sensor | None:
        for sensor in self.sensor_list:
            if sensor.id == sensor_id:
                return sensor
        return None
