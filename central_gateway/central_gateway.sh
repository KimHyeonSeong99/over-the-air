#!/bin/bash

#install paho-mqtt
sudo apt-get install python3-paho-mqtt -y

cd "$(dirname "$0")"
sudo ip link set can0 up type can bitrate 1000000
python3 central_gateway.py
sudo ip link set can0 down