# DSMR P1 to MQTT

DSMR P1 to MQTT is a lightweight service that can be used for reading DSMR telegrams from your smart meter and expose 
those energy statistics over MQTT. You will need a P1 to USB cable to communicate with the smart meter and hardware to 
run a Linux OS.

## Installation

Go to your home directory:
```bash
cd ~
```

Use the following command to install this service on your Linux machine.
```bash
bash <(curl -s https://raw.githubusercontent.com/sanderdona/dsmr-p1-to-mqtt/main/install.sh)
```

Check if the service is installed correctly.
```bash
systemctl status p1-to-mqtt
```