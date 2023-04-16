from paho.mqtt import client as mqtt_client
from dataclasses import dataclass

@dataclass
class MqttInfo:
    client_id: str
    username: str
    password: str
    broker: str
    port: int


class MqttManager:
    def __init__(self, mqtt_info: MqttInfo, handle_data, topics: list[str]):
        self._mqtt_info = mqtt_info
        self._mqtt_client = self.connect_mqtt() if mqtt_info else None
        def on_message(client, userdata, msg):
            handle_data(msg.topic, msg.payload)
        self._mqtt_client.subscribe([(topic, 0) for topic in topics])
        self._mqtt_client.on_message = on_message
        self._mqtt_client.loop_forever()

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

    def stop(self):
        if self._mqtt_client:
            self._mqtt_client.disconnect()
