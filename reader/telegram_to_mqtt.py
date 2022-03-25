import logging
import re
import json
from datetime import datetime
import pytz

from reader.domain import MqttMessage, MessageDTO
from reader.service import MqttService

interesting_codes = {
    '0-0:1.0.0': {'topic': 'timestamp', 'type': 'timestamp'},
    '0-0:96.14.0': {'topic': 'tariff_indicator', 'type': 'boolean'},
    '1-0:1.8.1': {'topic': 'electricity_positions/delivered/t1', 'type': 'energy'},
    '1-0:1.8.2': {'topic': 'electricity_positions/delivered/t2', 'type': 'energy'},
    '1-0:2.8.1': {'topic': 'electricity_positions/returned/t1', 'type': 'energy'},
    '1-0:2.8.2': {'topic': 'electricity_positions/returned/t2', 'type': 'energy'},
    '1-0:1.7.0': {'topic': 'electricity_live/delivered/combined', 'type': 'power'},
    '1-0:2.7.0': {'topic': 'electricity_live/returned/combined', 'type': 'power'},
    '1-0:21.7.0': {'topic': 'electricity_live/delivered/l1', 'type': 'power'},
    '1-0:41.7.0': {'topic': 'electricity_live/delivered/l2', 'type': 'power'},
    '1-0:61.7.0': {'topic': 'electricity_live/delivered/l3', 'type': 'power'},
    '1-0:22.7.0': {'topic': 'electricity_live/returned/l1', 'type': 'power'},
    '1-0:42.7.0': {'topic': 'electricity_live/returned/l2', 'type': 'power'},
    '1-0:62.7.0': {'topic': 'electricity_live/returned/l3', 'type': 'power'},
    '1-0:32.7.0': {'topic': 'electricity_live/voltage/l1', 'type': 'voltage'},
    '1-0:52.7.0': {'topic': 'electricity_live/voltage/l2', 'type': 'voltage'},
    '1-0:72.7.0': {'topic': 'electricity_live/voltage/l3', 'type': 'voltage'},
}

always_update_types = [
    'power',
    'voltage',
]


class TelegramToMqtt:
    published_vars = {
        'timestamp': '',
        'tariff_indicator': '',
        'electricity_positions/delivered/t1': 0.0,
        'electricity_positions/delivered/t2': 0.0,
        'electricity_positions/returned/t1': 0.0,
        'electricity_positions/returned/t2': 0.0,
    }

    def __init__(self, serial_port, mqtt_config):
        self.serial_port = serial_port
        logging.info(f"Handling messages on port {self.serial_port.port}")

        self.mqtt_config = mqtt_config
        logging.info(f"Publishing MQTT messages to host {self.mqtt_config.host} "
                     f"on port {self.mqtt_config.port} "
                     f"with client id {self.mqtt_config.client_id}")
        self.mqtt_service = MqttService(self.mqtt_config)

    async def handle_new_telegram(self):
        telegram = self.serial_port.get_telegram()
        logging.debug(f"Handling telegram containing {len(telegram)} rows")

        messages = self.convert_to_messages(telegram)
        logging.debug("Publishing messages to MQTT")

        for message in messages:
            await self.mqtt_service.publish(message)
        logging.info(f"Published {len(messages)} messages successfully")

    def convert_to_messages(self, telegram):
        messages = []
        for telegram_row in telegram:
            if TelegramToMqtt.is_interesting_row(telegram_row):
                message_dto = self.extract_data(telegram_row)
                if TelegramToMqtt.has_updated_value(message_dto) or TelegramToMqtt.always_update(message_dto):
                    messages.append(self.convert_to_message(message_dto, telegram_row))
        return messages

    def convert_to_message(self, message_dto: MessageDTO, telegram_row):
        topic = message_dto.topic
        value_type = message_dto.value_type
        value = TelegramToMqtt.clean_value(telegram_row, value_type)
        payload = TelegramToMqtt.create_payload(value, value_type)
        return MqttMessage(json.dumps(payload), f"{self.mqtt_config.base_topic}{topic}")

    @staticmethod
    def extract_data(telegram_row):
        for code in interesting_codes:
            if re.match(rf'(?={code})', telegram_row):
                topic = interesting_codes[code]['topic']
                value_type = interesting_codes[code]['type']
                value = TelegramToMqtt.clean_value(telegram_row, value_type)
                return MessageDTO(value, value_type, topic)

    @staticmethod
    def create_payload(value, value_type):
        if value_type == 'timestamp':
            return {
                'value': value
            }
        else:
            return {
                'value': value,
                'time': TelegramToMqtt.published_vars['timestamp']
            }

    @staticmethod
    def clean_value(telegram_row, value_type):
        value = telegram_row[telegram_row.find('(') + 1: telegram_row.find(')')]
        if 'energy' == value_type:
            return float(value[:-4])
        elif 'power' == value_type:
            return float(value[:-3])
        elif 'voltage' == value_type:
            return float(value[:-2])
        elif 'timestamp' == value_type:
            return TelegramToMqtt.timestamp_to_utc_datetime(value).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        elif 'boolean' == value_type:
            return value.lstrip('0')
        else:
            return value

    @staticmethod
    def is_interesting_row(telegram_row):
        for code in interesting_codes:
            if re.match(rf'(?={code})', telegram_row):
                return True
        return False

    @staticmethod
    def has_updated_value(message_dto: MessageDTO):
        new_value = message_dto.value
        for published_var in TelegramToMqtt.published_vars:
            if re.match(rf'(?={published_var})', message_dto.topic):
                old_value = TelegramToMqtt.published_vars[published_var]
                if old_value != new_value:
                    TelegramToMqtt.published_vars[published_var] = new_value
                    return True
        return False

    @staticmethod
    def always_update(message_dto: MessageDTO):
        return message_dto.value_type in always_update_types

    @staticmethod
    def timestamp_to_utc_datetime(timestamp: str):
        timezone = pytz.timezone('Europe/Amsterdam')
        naive_datetime = datetime.strptime(timestamp[:-1], '%y%m%d%H%M%S')
        dst_active = timestamp[-1:] == 'S'
        local_datetime = timezone.localize(naive_datetime, dst_active)
        return local_datetime.astimezone(pytz.utc)
