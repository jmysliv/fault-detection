import yaml
from typing import List
from .mqtt import MqttInfo
from dataclasses import dataclass

@dataclass
class Device:
    id: int
    ip: str


class Config:
    devices: List[Device]
    mqtt_info: MqttInfo

    def __init__(self):
        # Load the YAML file
        with open('./network-availability-checker/config/conf.yaml', 'r') as f:
            data = yaml.safe_load(f)
        info = data['mqtt_info']
        self.mqtt_info = MqttInfo(
            client_id=info['client_id'], username=info['username'], password=info['password'],
            broker=info['broker'], port=info['port']
        )
        self.devices = []
        devices = data['devices']
        for device in devices:
            device_id = int(device['id'])
            device_ip = device['ip']
            self.devices.append(Device(device_id, device_ip))