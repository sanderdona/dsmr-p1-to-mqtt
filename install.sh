#!/bin/bash

REPO_NAME="dsmr-p1-to-mqtt"
BRANCH_NAME="main"

echo "Download and extract files..."
curl -L "https://github.com/sanderdona/$REPO_NAME/archive/refs/heads/$BRANCH_NAME.zip" -o "$REPO_NAME.zip"
unzip "$REPO_NAME.zip"
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

echo "Getting USB devices..."
devices=$(ls /dev/ttyUSB* 2>/dev/null)

# Check if any devices are found
if [ -z "$devices" ]; then
  echo "No devices found"
else
  while true; do
    echo "Available devices:"
    i=1
    for device in $devices; do
      # Extract vendor and model info
      vendor=$(udevadm info --query=property --name=$device | grep '^ID_VENDOR_FROM_DATABASE=' | cut -d= -f2)
      model=$(udevadm info --query=property --name=$device | grep '^ID_MODEL_FROM_DATABASE=' | cut -d= -f2)

      # Display device with vendor and model
      echo "$i) $device | $vendor - $model"
      i=$((i+1))
    done

    # Prompt the user to choose a device
    read -p "Enter the number of the device you want to use (or 'q' to quit): " selection

    # Check if the user wants to quit
    if [ "$selection" == "q" ]; then
      echo "Exiting the script."
      break
    fi

    # Validate user input
    if [[ "$selection" =~ ^[0-9]+$ && "$selection" -ge 1 && "$selection" -le ${#devices[@]} ]]; then
      selected_device=${devices[$((selection-1))]}
      # Display the selected device with vendor and model
      echo "Selected: $selected_device"
      break
    else
      echo "Invalid selection. Please choose a valid device or enter 'q' to quit."
    fi
  done
fi
