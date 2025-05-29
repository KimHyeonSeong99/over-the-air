#!/bin/bash

#install mosquitto
sudo apt-get update
sudo apt-get install mosquitto -y

sudo mosquitto_passwd -b /etc/mosquitto/pwfile mose mose
sudo bash -c 'cat >> /etc/mosquitto/mosquitto.conf <<EOF
listener 1883 0.0.0.0
allow_anonymous false
password_file /etc/mosquitto/pwfile
EOF
'

sudo systemctl restart mosquitto

#install paho-mqtt
sudo apt-get install python3-paho-mqtt -y

#install flask
sudo apt-get install python3-flask -y

#start server
cd "$(dirname "$0")"  # Move to the directory where the script is located
python3 server_notice.py
python3 server_download.py