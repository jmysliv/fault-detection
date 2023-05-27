from .src.config import Config
from .src.mqtt import MqttManager
from .src.device_checker import DeviceChecker

if __name__ == "__main__":
    config_parser = Config()
    print(config_parser.devices)
    mqtt_manager = MqttManager(config_parser.mqtt_info)
    device_checker = DeviceChecker(config_parser.devices, mqtt_manager)
    device_checker.loop()
