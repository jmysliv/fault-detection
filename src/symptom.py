class Symptom:
    sensor_id: int
    value: str
    temporal: str
    def __init__(self, sensor_id: int, value: str, temporal: str):
        self.sensor_id = sensor_id
        self.value = value
        self.temporal = temporal