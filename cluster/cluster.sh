#!/bin/bash

sudo apt-get update
sudo apt-get install python3-can -y

cd "$(dirname "$0")"  # sh 파일이 있는 디렉토리로 이동
sudo ip link set can0 up type can bitrate 1000000
python3 cluster.py
sudo ip link set can0 down