class MessageDTO:
    value_type: str
    topic: str

    def __init__(self, value, value_type: str, topic: str):
        self.value = value
        self.value_type = value_type
        self.topic = topic
