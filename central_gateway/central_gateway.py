import os
import can
import paho.mqtt.client as mqtt
import time
import requests

program_dir = os.path.dirname(os.path.abspath(__file__))

def send_ota_file(can_bus, filepath, block_size=7*256):
    with open(filepath, "rb") as f:
        data = f.read()

    total_blocks = (len(data) + block_size - 1) // block_size
    seq = 0

    # 다운로드 요청 및 응답 대기
    while True:
        msg = can.Message(arbitration_id=0x34, data=[0x00, 0x07], is_extended_id=False)
        can_bus.send(msg)
        while True:
            response = can_bus.recv()
            if response and response.arbitration_id == 0x74:
                break  # 원하는 ID가 나올 때까지 반복
        if response.data == b"\x00\x07":
            break
        else:
            time.sleep(0.1)

    for block_idx in range(total_blocks):
        block = data[block_idx * block_size : min((block_idx + 1) * block_size, len(data))]
        while True:
            for i in range(0, len(block), 7):
                chunk = block[i:i+7]
                msg_data = [seq % 256] + list(chunk)
                msg = can.Message(arbitration_id=0x36, data=msg_data, is_extended_id=False)
                can_bus.send(msg)
            if block_idx != total_blocks - 1:
                while True:
                    response = can_bus.recv()
                    if response and response.arbitration_id == 0x76:
                        break  # 원하는 ID가 나올 때까지 반복
                if response.data == b"\x10":
                    seq += 1
                    break
                elif response.data == b"\x11":
                    time.sleep(0.1)
            else:
                while True:
                    msg = can.Message(arbitration_id=0x37, data=[0x00], is_extended_id=False)
                    can_bus.send(msg)
                    response = can_bus.recv()
                    if response and response.arbitration_id == 0x77:
                        break  # 원하는 ID가 나올 때까지 반복
                if response.data == b"\x10":
                    print("Firmware update completed successfully.")
                    return
                elif response.data == b"\x11":
                    time.sleep(0.1)
                break

def download_file_from_server(server_url, filename, save_path):
    response = requests.get(f"{server_url}/{filename}", stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    else:
        print(f"Failed to download file: {filename}")
        return False

def on_message(client, userdata, message):
    # 메시지에서 파일명 추출 (예: payload가 파일명)
    filename = message.payload.decode().strip()
    server_url = "http://server_ip:port/files"  # 파일 서버의 URL (폴더 경로까지)
    local_path = os.path.join(program_dir,"files/firmware.bin")
    if download_file_from_server(server_url, filename, local_path):
        send_ota_file(can_bus, local_path)
    
if __name__ == "__main__":
    can_bus = can.interface.Bus(channel='can0', bustype='socketcan')
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("mqtt_broker_ip", 1883, 60)
    client.subscribe("ota/firmware")
    client.loop_forever()
