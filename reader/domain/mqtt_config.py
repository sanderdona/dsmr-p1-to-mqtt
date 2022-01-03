class MqttConfig:
    host: str
    port: int
    username: str
    password: str
    base_topic: str
    client_id: str

    def __init__(self, host: str, port: int, username: str, password: str, base_topic: str, client_id: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.base_topic = base_topic
        self.client_id = client_id
