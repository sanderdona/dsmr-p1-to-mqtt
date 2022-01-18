import logging
import re
from datetime import datetime
import pytz

from reader.domain import MqttMessage
from reader.service import MqttService

interesting_codes = {
    '0-0:1.0.0': {'topic': 'timestamp', 'type': 'timestamp'},
    '1-0:1.8.1': {'topic': 'electricity_delivered_1', 'type': 'energy'},
    '1-0:1.8.2': {'topic': 'electricity_delivered_2', 'type': 'energy'},
    '1-0:2.8.1': {'topic': 'electricity_returned_1', 'type': 'energy'},
    '1-0:2.8.2': {'topic': 'electricity_returned_2', 'type': 'energy'},
    '0-0:96.14.0': {'topic': 'tariff_indicator', 'type': 'boolean'},
    '1-0:1.7.0': {'topic': 'electricity_currently_delivered', 'type': 'current'},
    '1-0:2.7.0': {'topic': 'electricity_currently_returned', 'type': 'current'},
    '1-0:21.7.0': {'topic': 'phase_currently_delivered_l1', 'type': 'current'},
    '1-0:41.7.0': {'topic': 'phase_currently_delivered_l2', 'type': 'current'},
    '1-0:61.7.0': {'topic': 'phase_currently_delivered_l3', 'type': 'current'},
    '1-0:22.7.0': {'topic': 'phase_currently_returned_l1', 'type': 'current'},
    '1-0:42.7.0': {'topic': 'phase_currently_returned_l2', 'type': 'current'},
    '1-0:62.7.0': {'topic': 'phase_currently_returned_l3', 'type': 'current'},
}


class TelegramToMqtt:

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
        logging.debug(f"Publishing messages to MQTT")

        for message in messages:
            await self.mqtt_service.publish(message)
        logging.info(f"Published {len(messages)} messages successfully")

    def convert_to_messages(self, telegram):
        messages = []
        for telegram_row in telegram:
            if TelegramToMqtt.is_interesting_row(telegram_row):
                messages.append(self.convert_to_message(telegram_row))
        return messages

    def convert_to_message(self, telegram_row):
        for code in interesting_codes:
            if re.match(rf'(?={code})', telegram_row):
                topic = interesting_codes[code]['topic']
                value_type = interesting_codes[code]['type']
                value = TelegramToMqtt.clean_value(telegram_row, value_type)
                return MqttMessage(value, f"{self.mqtt_config.base_topic}{topic}")

    @staticmethod
    def clean_value(telegram_row, value_type):
        value = telegram_row[telegram_row.find('(') + 1: telegram_row.find(')')]
        if 'energy' == value_type:
            return float(value[:-4])
        elif 'current' == value_type:
            return float(value[:-3])
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
    def timestamp_to_utc_datetime(timestamp: str):
        timezone = pytz.timezone('Europe/Amsterdam')
        naive_datetime = datetime.strptime(timestamp[:-1], '%y%m%d%H%M%S')
        dst_active = timestamp[-1:] == 'S'
        local_datetime = timezone.localize(naive_datetime, dst_active)
        return local_datetime.astimezone(pytz.utc)
