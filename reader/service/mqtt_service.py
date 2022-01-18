import logging

import paho.mqtt.client as mqtt

from reader.domain import MqttConfig, MqttMessage


class MqttService:

    def __init__(self, mqtt_config: MqttConfig):
        self.client = mqtt.Client(mqtt_config.client_id)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.username_pw_set(mqtt_config.username, mqtt_config.password)
        try:
            self.client.connect(mqtt_config.host, mqtt_config.port)
        except ConnectionRefusedError as e:
            logging.error(f"Failed to connect to {mqtt_config.host}:{mqtt_config.port} ({e.strerror})")
            exit(1)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT broker")
            logging.debug("Starting loop...")
            self.client.loop_start()
            logging.debug("Loop started")
        else:
            logging.warning("Failed to connect to MQTT broker. Return code: " + rc)

    def on_disconnect(self):
        logging.debug("Disconnected. Stopping loop...")
        self.client.loop_stop()
        logging.debug("Loop stopped")

    def on_log(self, client, userdata, level, buf):
        logging.debug("MQTT log: " + buf)

    async def publish(self, message: MqttMessage):
        logging.debug(f"Publishing payload {message.payload} to topic {message.topic}")
        self.client.publish(message.topic, message.payload)
