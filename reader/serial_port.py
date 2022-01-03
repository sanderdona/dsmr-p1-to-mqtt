import re

import serial
import logging


class SerialPort:
    defaults = {
        'baudrate': 115200,
        'bytesize': serial.EIGHTBITS,
        'parity': serial.PARITY_NONE,
        'stopbits': serial.STOPBITS_ONE,
        'xonxoff': False,
        'rtscts': False,
        'timeout': 12
    }

    def __init__(self, port, **kwargs):
        self.port = port

        config = {}
        config.update(self.defaults)
        config.update(kwargs)

        try:
            self.serial = serial.Serial(port, **config)
            self.serial.port = port
            self.serial.close()
        except serial.SerialException as e:
            logging.error(f"Could not open port {port}")
            raise SerialPortError(e)

    def get_telegram(self):
        result = []
        logging.debug("Reading serial port...")
        self.serial.open()
        checksum_found = False
        while not checksum_found:
            try:
                data = self.serial.readline()
                data = data.decode('ascii').strip()
            except serial.SerialException as e:
                logging.error(f"Cannot read serial data: {e}")
            if re.match(r'(?=!)', data, 0):
                checksum_found = True
            else:
                result.append(data)
        self.serial.close()
        logging.debug("Done reading")
        return result


class SerialPortError(Exception):
    pass
