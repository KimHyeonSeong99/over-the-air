sudo apt-get update
sudo apt-get install mosquitto -y

sudo mosquitto_passwd -b /etc/mosquitto/pwfile mose mose
sudo bash -c 'cat >> /etc/mosquitto/mosquitto.conf <<EOF
listener 1883 127.0.0.1
allow_anonymous false
password_file /etc/mosquitto/pwfile
EOF
'

# mosquitto 재시작
sudo systemctl restart mosquitto
