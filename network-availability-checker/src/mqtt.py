from paho.mqtt import client as mqtt_client
from dataclasses import dataclass
import json
import threading

@dataclass
class MqttInfo:
    client_id: str
    username: str
    password: str
    broker: str
    port: int


class MqttManager:
    def __init__(self, mqtt_info: MqttInfo):
        self._mqtt_info = mqtt_info
        self._mqtt_client = self.connect_mqtt() if mqtt_info else None
        loop_thread = threading.Thread(target=self._mqtt_client.loop_forever, args=())
        loop_thread.start()

    def connect_mqtt(self):
        def on_connect(client_instance, userdata, flags, rc):
            print("connect")
            if rc == 0:
                print("Connected to MQTT broker")
            else:
                print("Failed to connect to MQTT broker, return code %d\n", rc)
        
        try:
            client = mqtt_client.Client(self._mqtt_info.client_id)
            client.username_pw_set(self._mqtt_info.username, self._mqtt_info.password)
            client.on_connect = on_connect
           
            client.connect(self._mqtt_info.broker, self._mqtt_info.port)
            return client
        except Exception as e:
            print(e)
            return None
        
    def publish_message(self, obj, topic):
        msg = json.dumps(obj, default=str)
        if self._mqtt_client:
            result = self._mqtt_client.publish(topic, msg)
            status = result[0]
            if status == 0:
                return True
            else:
                print(f"Failed to send message to MQTT topic")
                return False
     