class MqttMessage:
    payload: str
    topic: str

    def __init__(self, payload: str, topic: str):
        self.payload = payload
        self.topic = topic
