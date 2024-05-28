import paho.mqtt.client as mqtt
import json
import hashlib
import os, time, cv2
import numpy as np
import base64

Sub_Topic = "updates"
userId = "Alice"
userPw = "mose"
brokerIp = "203.246.114.226"
port = 1883
target_list = []

global update_firmware_path, latest_version, file_list
update_firmware_path = 'C:/Users/user/OTA/update_img/'
latest_version = dict()
file_list = dict()

def check_new_firmware():
    diff = []
    remove_dict_list =[]
    remove_file_list=[]
    now_file_list = os.listdir(update_firmware_path)
    for firmware in now_file_list:
        if firmware not in file_list:
            diff.append(firmware)
            file_list[firmware] = dict()
            file_list[firmware]['FileName'] = firmware.split('-')[-1]
            file_list[firmware]['Target'] = firmware.split('-')[0]
            file_list[firmware]['Version'] = firmware.split('-')[1]
            if file_list[firmware]['Target'] not in target_list:
                target_list.append(file_list[firmware]['Target'])
            try:
                if float(file_list[firmware]['Version']) >= float(latest_version[file_list[firmware]['Target']]):
                    latest_version[file_list[firmware]['Target']] = file_list[firmware]['Version']            
                else:
                    remove_list.append(firmware)
            except:
                latest_version[file_list[firmware]['Target']] = file_list[firmware]['Version']

    for file in file_list:
        if file not in now_file_list:
            remove_dict_list.append(file)

    for file in remove_dict_list:
        del(file_list[file])
    
    if diff:
        remove_list=[]
        for firmware in diff:
            try:
                if float(file_list[firmware]['Version']) >= float(latest_version[file_list[firmware]['Target']]):
                    latest_version[file_list[firmware]['Target']] = file_list[firmware]['Version']            
                else:
                    remove_list.append(firmware)
            except:
                latest_version[file_list[firmware]['Target']] = file_list[firmware]['Version']
        for firmware in remove_list:
            diff.remove(firmware)

    if diff:
        print('='*30)
        for target in target_list:
            print('latest', target,'Version:',latest_version[target])
            print('='*30)
        print("need to update about: ", diff)
    return diff

def compute_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def make_message(FilePath):
    
    message = dict()
    with open (FilePath,"rb") as stream:
        img_bin = stream.read()
        encoded_img = base64.b64encode(img_bin)

    message['FileName'] = FilePath.split('/')[-1].split('-')[-1]
    message['image'] = encoded_img.decode()
    jf = json.dumps(message,indent='\t')
    return jf

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Error: Connection fail, Return code =" ,rc)

def on_disconnect(client,userdata,flags,rc = 0):
    print(str(rc),end='/')

def on_publish(client,userdata,mid):
    print("In on_pub call back mid = ", mid,end='/')

client = mqtt.Client()

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

while True:
     
    publish_list = []
    publish_list = check_new_firmware()

    if publish_list:
        for FileName in publish_list:
            client.connect(brokerIp, 1883)
            FilePath = update_firmware_path + FileName
            client.loop_start()

            client.publish('updates/image', make_message(FilePath), 2, retain= True)
            client.loop_stop()
            print("Success sending file:",FileName)
            client.disconnect()
    
    time.sleep(1.0)
