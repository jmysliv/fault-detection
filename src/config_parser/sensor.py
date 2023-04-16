class Sensor:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.faults_associated = 0
        self.data = []