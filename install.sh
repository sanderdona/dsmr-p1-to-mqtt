#!/bin/bash

REPO_NAME="dsmr-p1-to-mqtt"
BRANCH_NAME="main"

echo "Download and extract files..."
curl -L "https://github.com/sanderdona/$REPO_NAME/archive/refs/heads/$BRANCH_NAME.zip" -o "$REPO_NAME.zip"
unzip "$REPO_NAME.zip" -d "$REPO_NAME"
echo "Delete zip file..."
rm "$REPO_NAME.zip"
cd "$REPO_NAME-$BRANCH_NAME" || { echo "Something went wrong while downloading or extracting."; exit 1;}
echo "Done"

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

