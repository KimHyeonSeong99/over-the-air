#!/bin/bash
cd "$(dirname "$0")"  # sh 파일이 있는 디렉토리로 이동
sudo ip link set can0 up type can bitrate 1000000
python3 central_gateway.py
sudo ip link set can0 down