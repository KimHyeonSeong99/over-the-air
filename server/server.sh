#!/bin/bash
sudo apt-get update

#install mosquitto
if [ ! -f /etc/mosquitto/pwfile ]; then
    sudo mosquitto_passwd -b /etc/mosquitto/pwfile mose mose
fi

# mosquitto.conf에 listener 설정이 없을 때만 추가 (주석이 있어도 동작)
if ! grep -E '^[[:space:]]*listener 1883 0.0.0.0' /etc/mosquitto/mosquitto.conf 2>/dev/null; then
sudo bash -c 'cat >> /etc/mosquitto/mosquitto.conf <<EOF
listener 1883 0.0.0.0
allow_anonymous false
password_file /etc/mosquitto/pwfile
EOF
'
fi

#install paho-mqtt
sudo apt-get install python3-paho-mqtt -y

#install flask
sudo apt-get install python3-flask -y

#start server
cd "$(dirname "$0")"  # Move to the directory where the script is located
python3 server_notice.py &
python3 server_download.py &
wait