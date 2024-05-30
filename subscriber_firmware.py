import paho.mqtt.client as mqtt
import hashlib
import json
import requests
import os
import cv2
import numpy as np
from PIL import Image
import base64
import io
import time
from tkinter import *
from tkinter import messagebox
import someip

timelist = {'Now':0,'10min':600,'1hour':3600,'1day':86400,'1week':604800}
Sub_Topic = "updates/firmware" 
userId = "Alice"
userPw = "mose"
brokerIp = "203.246.114.226"
port = 1883


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(Sub_Topic)

def compute_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def update_choice():
    OTA_UI = Tk()
    later_time = StringVar()
    OTA_UI.title("Choice update")
    window_width = OTA_UI.winfo_screenwidth()
    window_height = OTA_UI.winfo_screenheight()
    app_width = 500
    app_height = 300
    width_center = int((window_width - app_width)/2)
    height_center = int((window_height - app_height)/2)
    OTA_UI.geometry(f"{app_width}x{app_height}+{width_center}+{height_center}")
    information = Label(OTA_UI,text = 'Do you want to update new firmware?\nclick the button what you want',font = ('bold'))
    
    def event_PB():
        if later_time.get() == 'Now':
            messagebox.showinfo("Notice","You choice Now, Start install firmware!")
            OTA_UI.destroy()

        elif later_time.get() == '':
            messagebox.showinfo("Notice","You choice Now, Start install firmware!")
        else:
            messagebox.showinfo("Notice",f"You choice Later, Notice update after {later_time.get()} later!")
            OTA_UI.destroy()
            
    button_Submit = Button(OTA_UI,text = 'Submit',command = event_PB)
    Later_time0 = Radiobutton(OTA_UI, text = 'Now', value = 'Now', variable = later_time)
    Later_time1 = Radiobutton(OTA_UI, text = '10min', value = '10min', variable = later_time)
    Later_time2 = Radiobutton(OTA_UI, text = '1hour', value = '1hour', variable = later_time)
    Later_time3 = Radiobutton(OTA_UI, text = '1day', value = '1day', variable = later_time)
    Later_time4 = Radiobutton(OTA_UI, text = '1week', value = '1week', variable = later_time)
    information.pack()
    button_Submit.pack()
    Later_time0.pack()
    Later_time1.pack()
    Later_time2.pack()
    Later_time3.pack()
    Later_time4.pack()
    OTA_UI.mainloop()
    return timelist.get(later_time.get())

# subscriber callback
def on_message(client, userdata, msg):

    try:
        with open("/home/avees/OTA/version.json","r") as versionlist:
            version = json.load(versionlist)    
    except:
        pass

    payload = json.loads(msg.payload)
    FileName = payload['FileName']
    FirmwareData = payload['Firmware']
    FirmwareVersion = payload['Version']
    if float(version[FileName]) < float(FirmwareVersion):
        flag = 1
        while(flag):
            flag = update_choice()
            time.sleep(flag)

        try:
            firmwareDirectory = '/home/avees/OTA/tmp'
            firmwarePath = os.path.join(firmwareDirectory, FileName)
            with open(firmwarePath,"w") as stream:
                stream.write(FirmwareData) 
            time.sleep(1)
            print(f"Firmware downloaded and saved to {firmwareDirectory}")
        except Exception as e:
            print(f"Error downloading the firmware: {e}")
            print(f"firmwareDirectory: {firmwareDirectory}")
            print(f"firmwarePath: {firmwarePath}")

        app = someip.Application(0x1234)  # 이 값은 서비스 ID로 실제 사용하는 ID로 대체해야 합니다.
                
        service_id = 0x5678  # 수신측에서 사용하는 서비스 ID

        # 파일을 열고 내용을 읽음
        with open(firmwareDirectory, 'rb') as file:
                file_data = file.read()               
            # 데이터를 패킷으로 분할하여 전송
        chunk_size = 1024  # 한 번에 전송할 데이터의 크기
        num_chunks = (len(file_data) + chunk_size - 1) // chunk_size  # 파일을 패킷으로 나눔
        
        message = someip.Packet(0xFFFF, service_id, someip.MsgType.NOTIFY, someip.ReturnCode.E_OK, FileName)
        app.send_message(message)

        for i in range(num_chunks):
            chunk_data = file_data[i * chunk_size: (i + 1) * chunk_size]
            message = someip.Packet(0xFFFF, service_id, someip.MsgType.NOTIFY, someip.ReturnCode.E_OK, chunk_data)
            app.send_message(message)

        version[FileName] = FirmwareVersion
        with open("/home/avees/OTA/version.json","w") as versionlist:
            versionlist.write(json.dumps(version))
    else:
        print("new firmware version is old version, pass the update")
    print("Ready for a new update")



client = mqtt.Client()
client.username_pw_set(userId, userPw)
client.on_connect = on_connect
client.on_message = on_message

client.connect(brokerIp, port, 60)

client.loop_forever()

import os

# 서비스 ID 설정
SERVICE_ID = 0x1234
METHOD_ID = 0x5678
PAYLOAD_MAX_SIZE = 1024  # 메시지의 최대 크기 (바이트 단위)

# 서비스 디스커버리 클라이언트 생성
sd_client = ServiceDiscoveryClient()

# vSomeIP Tester 생성
tester = SomeIpTester()

def send_file(file_path):
    # 파일 읽기
    with open(file_path, 'rb') as file:
        file_data = file.read()

    # 파일 크기 확인
    file_size = os.path.getsize(file_path)

    # 파일을 보낼 수 있는 패킷 수 계산
    num_packets = (file_size + PAYLOAD_MAX_SIZE - 1) // PAYLOAD_MAX_SIZE

    # 파일을 패킷으로 나누어 전송
    for i in range(num_packets):
        # 현재 패킷의 시작 및 끝 오프셋 계산
        start_offset = i * PAYLOAD_MAX_SIZE
        end_offset = min((i + 1) * PAYLOAD_MAX_SIZE, file_size)

        # 현재 패킷의 데이터 추출
        packet_data = file_data[start_offset:end_offset]

        # vSomeIP 메시지 생성
        payload = packet_data
        response = tester.send_request(SERVICE_ID, METHOD_ID, payload)

        # 응답 확인
        if not response:
            print("No response received for packet {}.".format(i + 1))
            return False

    print("File successfully sent.")
    return True


file_path = 'example.txt'

send_file(file_path)

