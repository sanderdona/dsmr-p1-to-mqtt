import sys
import unittest
from unittest import mock
from unittest.mock import Mock, AsyncMock

from reader import TelegramToMqtt


class TelegramToMqttTest(unittest.IsolatedAsyncioTestCase):

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

        self.assertEqual(telegram_to_mqtt.mqtt_service.publish.call_count, 9)
