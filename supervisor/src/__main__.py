from .config import Config
from .supervisor import Supervisor
import yaml
from .mqtt import MqttManager, MqttInfo
from .supervisor_tester import SupervisorTester

if __name__ == "__main__":
    config_parser = Config()
    supervisor = Supervisor(config_parser)
    tester = SupervisorTester(supervisor)
    tester.test()
    # file_path = 'config/config.yaml'
    # with open(file_path, 'r') as stream:
    #     conf = yaml.safe_load(stream)
    # info = conf['mqtt_info']
    # mqtt_info = MqttInfo(
    #     client_id=info['client_id'], username=info['username'], password=info['password'],
    #     broker=info['broker'], port=info['port']
    # )
    # manager = MqttManager(mqtt_info, supervisor.handle_sensor_data, [f'S_{sensor.id}' for sensor in supervisor.config.sensor_list])