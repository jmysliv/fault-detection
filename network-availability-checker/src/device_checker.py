import time
from ping3 import ping
from .config import Device
from .mqtt import MqttManager
from typing import List
from datetime import datetime

class DeviceChecker:
    devices: List[Device]
    mqtt_manager: MqttManager
    def __init__(self, devices: Device, mqtt_manager: MqttManager):
        self.devices = devices
        self.mqtt_manager = mqtt_manager

    def loop(self):
        print("loop")
        time.sleep(30)
        print("end sleep")
        for device in self.devices:
            delay = ping(device.ip)
            print(delay, device)
            if delay is None:
                data = {
                    "value": 0,
                    "timestamp": datetime.now(),
                    "sensor_id": device.id,
                 }
                self.mqtt_manager.publish_message(data, f'S_{device.id}')
            else:
                data = {
                    "value": 1,
                    "timestamp": datetime.now(),
                    "sensor_id": device.id,
                }
                self.mqtt_manager.publish_message(data, f'S_{device.id}')
