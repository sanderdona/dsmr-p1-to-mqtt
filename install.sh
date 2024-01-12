#!/bin/bash

REPO_NAME="dsmr-p1-to-mqtt"

echo "Download and extract files..."
mkdir "${REPO_NAME}"
curl -L "https://github.com/sanderdona/${REPO_NAME}/archive/refs/heads/main.zip" -o "${REPO_NAME}/${REPO_NAME}.zip"
unzip "${REPO_NAME}/${REPO_NAME}.zip" -d "${REPO_NAME}"
rm "${REPO_NAME}/${REPO_NAME}.zip"
echo "Done"

if [ -d "${REPO_NAME}" ]; then
    cd "${REPO_NAME}"
else
  echo "Failed to create directory."
  exit
fi

echo "Installing python3-venv..."
sudo apt-get install python3-venv
echo "Done"

echo "Make service executable..."
chmod +x bin/p1-to-mqtt
echo "Done"

echo "Create a virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
echo "Done"

echo "Install required packages in virtual environment..."
pip install .
echo "Done"

echo "Getting USB device to communicate with P1 port..."
for dir in /sys/class/tty/ttyUSB*
do
  echo "Device: $dir"
#  cu -l dir
#  if timeout 2s cat dir | grep -q "/" ; then
#      device=${dir%*/}
#      break
#  fi
done

if [ -z "$device" ]; then
    echo "No device found."
    read -pr "Device path: " "$device"
fi

