import sys
from unittest import mock, IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock

from reader import TelegramToMqtt


class TelegramToMqttTest(IsolatedAsyncioTestCase):

    @mock.patch.object(sys.modules['reader.telegram_to_mqtt'], 'MqttService')
    async def test_handle_telegram(self, mocked_mqtt_service):
        with open('telegram.out') as telegram_file:
            telegram = telegram_file.readlines()

        serial_port = Mock()
        serial_port.get_telegram.return_value = telegram

        config = Mock()
        config.base_topic = 'dsmr/reading/'

        telegram_to_mqtt = TelegramToMqtt(serial_port, config)
        telegram_to_mqtt.mqtt_service.publish = AsyncMock()

        await telegram_to_mqtt.handle_new_telegram()

        self.assertEqual(10, telegram_to_mqtt.mqtt_service.publish.call_count)

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
        self.assertEqual('dsmr/reading/electricity_delivered_1', messages[1].topic)
        self.assertEqual('{"value": 3382.357, "time": "2021-12-16T09:40:26.000Z"}', messages[1].payload)
