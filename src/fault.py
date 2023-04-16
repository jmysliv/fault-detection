class Fault:
    def __init__(self, id, name, symptoms, reasons, actions):
        self.id = id
        self.name = name
        self.symptoms = symptoms
        self.reasons = reasons
        self.actions = actions


    def has_symptom(self, sensor_id, value):
        for symptom in self.symptoms:
            if symptom.sensor_id == sensor_id and symptom.value == value:
                return True
        return False