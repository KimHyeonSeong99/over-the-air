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
import time  # Add this line to import the time module
import matplotlib.pyplot as plt


Sub_Topic = "updates/image" 
userId = "Alice"
userPw = "mose"
brokerIp = "203.246.114.226"
port = 1883

global Version
Version = dict()
Version['motor'] = 0.0
Version['light'] = 0.0
Version['UI'] = 0.0
Version['image'] = 0.0

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(Sub_Topic)

def compute_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

# subscriber callback
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    FileName = payload['FileName']
    ImageData = payload['image'].encode()
    decode_img = base64.b64decode(ImageData)
    img_out = Image.open(io.BytesIO(decode_img))
    img_array = np.array(img_out)
    img = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    firmwareDirectory = '/home/sea/OTA/tmp/'
    firmwarePath = os.path.join(firmwareDirectory, FileName)
    cv2.imwrite(firmwarePath, img)
    download_firmware = input("Do you want to download the new firmware?[y/n]: ")
    if download_firmware.lower() == 'y':
        try:
            firmwareDirectory = '/home/sea/sea-me-hackathon-2023/Cluster/src/image/'
            firmwarePath = os.path.join(firmwareDirectory, FileName)
            cv2.imwrite(firmwarePath, img)
            time.sleep(1)
            print(f"Firmware downloaded and saved to {firmwareDirectory}")
        except Exception as e:
            print(f"Error downloading the firmware: {e}")
            print(f"firmwareDirectory: {firmwareDirectory}")
            print(f"firmwarePath: {firmwarePath}")
    else:
        print("Deny downloading new firmware")
    

    print("Ready for a new update")



client = mqtt.Client()
client.username_pw_set(userId, userPw)
client.on_connect = on_connect
client.on_message = on_message

client.connect(brokerIp, port, 60)

client.loop_forever()

