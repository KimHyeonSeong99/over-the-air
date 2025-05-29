#!/bin/bash

#install paho-mqtt
sudo apt-get install python3-paho-mqtt -y

#install flask
sudo apt-get install python3-flask -y

#start server
cd "$(dirname "$0")"  # Move to the directory where the script is located
python3 server_notice.py &
python3 server_download.py &
wait