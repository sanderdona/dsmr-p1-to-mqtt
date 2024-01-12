#!/bin/bash

REPO_NAME="dsmr-p1-to-mqtt"

# Create a directory, download the zip and extract.
echo "Downloading files..."
mkdir "${REPO_NAME}"
curl -L "https://github.com/sanderdona/${REPO_NAME}/archive/refs/heads/main.zip" -o "${REPO_NAME}/${REPO_NAME}.zip"
unzip "${REPO_NAME}/${REPO_NAME}.zip" -d "${REPO_NAME}"
rm "${REPO_NAME}/${REPO_NAME}.zip"
echo "Done"

#Installing python3-venv
apt-get install python3-venv

# Make the p1-to-mqtt file executable.
echo "Make service executable..."
# shellcheck disable=SC2164
cd "${REPO_NAME}"
chmod +x bin/p1-to-mqtt
echo "Done"

# Create a virtual environment and activate it.
echo "Create a virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
echo "Done"

# Install required packages
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

