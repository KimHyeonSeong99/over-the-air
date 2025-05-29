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