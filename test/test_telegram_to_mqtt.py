import sys
import json
from unittest import mock, IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock

from reader import TelegramToMqtt


class TelegramToMqttTest(IsolatedAsyncioTestCase):

    @mock.patch.object(sys.modules['reader.telegram_to_mqtt'], 'MqttService')
    async def test_handle_telegram(self, mocked_mqtt_service):
        base_topic = 'dsmr/reading/'
        positions = 'electricity_positions/'
        live = 'electricity_live/'

        with open('telegram.out') as telegram_file:
            telegram = telegram_file.readlines()

        serial_port = Mock()
        serial_port.get_telegram.return_value = telegram

        config = Mock()
        config.base_topic = base_topic

        telegram_to_mqtt = TelegramToMqtt(serial_port, config)
        telegram_to_mqtt.mqtt_service.publish = AsyncMock()

        await telegram_to_mqtt.handle_new_telegram()

        self.assertEqual(20, telegram_to_mqtt.mqtt_service.publish.call_count)

        self.assertEqual('2021-12-16T09:40:25.000Z', self.get_value_by_topic(base_topic + 'timestamp', telegram_to_mqtt))
        self.assertEqual('2', self.get_value_by_topic(base_topic + 'tariff_indicator', telegram_to_mqtt))

        self.assertEqual(3382.928, self.get_value_by_topic(base_topic + positions + 'delivered/t1', telegram_to_mqtt))
        self.assertEqual(1576.309, self.get_value_by_topic(base_topic + positions + 'delivered/t2', telegram_to_mqtt))
        self.assertEqual(1944.285, self.get_value_by_topic(base_topic + positions + 'returned/t1', telegram_to_mqtt))
        self.assertEqual(4445.037, self.get_value_by_topic(base_topic + positions + 'returned/t2', telegram_to_mqtt))

        self.assertEqual(0.0, self.get_value_by_topic(base_topic + live + 'delivered/combined', telegram_to_mqtt))
        self.assertEqual(0.807, self.get_value_by_topic(base_topic + live + 'returned/combined', telegram_to_mqtt))

        self.assertEqual(0.0, self.get_value_by_topic(base_topic + live + 'delivered/l1', telegram_to_mqtt))
        self.assertEqual(0.0, self.get_value_by_topic(base_topic + live + 'delivered/l2', telegram_to_mqtt))
        self.assertEqual(0.0, self.get_value_by_topic(base_topic + live + 'delivered/l3', telegram_to_mqtt))

        self.assertEqual(0.152, self.get_value_by_topic(base_topic + live + 'returned/l1', telegram_to_mqtt))
        self.assertEqual(0.309, self.get_value_by_topic(base_topic + live + 'returned/l2', telegram_to_mqtt))
        self.assertEqual(0.345, self.get_value_by_topic(base_topic + live + 'returned/l3', telegram_to_mqtt))

        self.assertEqual(236.0, self.get_value_by_topic(base_topic + live + 'voltage/l1', telegram_to_mqtt))
        self.assertEqual(236.0, self.get_value_by_topic(base_topic + live + 'voltage/l2', telegram_to_mqtt))
        self.assertEqual(236.0, self.get_value_by_topic(base_topic + live + 'voltage/l3', telegram_to_mqtt))

        self.assertEqual(1, self.get_value_by_topic(base_topic + live + 'current/l1', telegram_to_mqtt))
        self.assertEqual(1, self.get_value_by_topic(base_topic + live + 'current/l2', telegram_to_mqtt))
        self.assertEqual(1, self.get_value_by_topic(base_topic + live + 'current/l3', telegram_to_mqtt))

    @mock.patch.object(sys.modules['reader.telegram_to_mqtt'], 'MqttService')
    async def test_only_update_current(self, mocked_mqtt_service):
        with open('telegram.out') as telegram_file:
            telegram = telegram_file.readlines()

        self.set_defaults()

        serial_port = Mock()
        serial_port.get_telegram.return_value = telegram

        config = Mock()
        config.base_topic = 'dsmr/reading/'

        telegram_to_mqtt = TelegramToMqtt(serial_port, config)
        telegram_to_mqtt.mqtt_service.publish = AsyncMock()

        await telegram_to_mqtt.handle_new_telegram()
        await telegram_to_mqtt.handle_new_telegram()

        self.assertEqual(34, telegram_to_mqtt.mqtt_service.publish.call_count)

    @mock.patch.object(sys.modules['reader.telegram_to_mqtt'], 'MqttService')
    async def test_convert_to_message(self, mocked_mqtt_service):
        telegram_row = [
            '0-0:1.0.0(211216104026W)',  # we need the timestamp to set the initial time
            '1-0:1.8.1(003382.357*kWh)'
        ]

        serial_port = Mock()
        config = Mock()
        config.base_topic = 'dsmr/reading/'

        telegram_to_mqtt = TelegramToMqtt(serial_port, config)

        messages = telegram_to_mqtt.convert_to_messages(telegram_row)

        self.assertIsNotNone(messages)
        self.assertEqual('dsmr/reading/electricity_positions/delivered/t1', messages[1].topic)
        self.assertEqual('{"value": 3382.357, "time": "2021-12-16T09:40:26.000Z"}', messages[1].payload)

    @staticmethod
    def set_defaults():
        TelegramToMqtt.published_vars = {
            'timestamp': '',
            'tariff_indicator': '',
            'electricity_positions/delivered/t1': 0.0,
            'electricity_positions/delivered/t2': 0.0,
            'electricity_positions/returned/t1': 0.0,
            'electricity_positions/returned/t2': 0.0,
        }

    @staticmethod
    def get_value_by_topic(topic, telegram_to_mqtt: TelegramToMqtt):
        call_args_list = telegram_to_mqtt.mqtt_service.publish.call_args_list
        for call_arg in call_args_list:
            args, kwargs = call_arg
            for arg in args:
                if topic == arg.topic:
                    return json.loads(arg.payload)['value']
