sudo apt-get update
sudo apt-get install mosquitto -y

sudo mosquitto_passwd -b /etc/mosquitto/pwfile mose mose
# 아래 명령은 mosquitto.conf 파일의 "끝에" 내용을 추가합니다.
sudo bash -c 'cat >> /etc/mosquitto/mosquitto.conf <<EOF
listener 1883 0.0.0.0
allow_anonymous false
password_file /etc/mosquitto/pwfile
EOF
'

# mosquitto 재시작
sudo systemctl restart mosquitto
