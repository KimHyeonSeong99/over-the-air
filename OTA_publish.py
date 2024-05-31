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

path = {"firmware": "C:/Users/user/OTA/update_firm/"," image": "C:/Users/user/OTA/update_img/"}
version_json = "C:/Users/user/OTA/version.json"

global file_list
file_list = dict()

def check_new_firmware(path):
    try:
        with open(version_json,"r") as json_file:
            version = json.load(json_file)
    except FileNotFoundError as e:
        print(e)

    diff = []
    remove_dict_list =[]
    remove_list=[]
    now_file_list = os.listdir(path)
    for firmware in now_file_list:
        if firmware not in file_list:
            diff.append(firmware)
            file_list[firmware] = dict()
            file_list[firmware]['FileName'] = firmware.split('-')[-1]
            file_list[firmware]['Version'] = firmware.split('-')[1]
            
            try:
                if float(file_list[firmware]['Version']) >= float(version[file_list[firmware]['FileName']]):
                    version[file_list[firmware]['FileName']] = file_list[firmware]['Version']            
                else:
                    remove_list.append(firmware)
            except:
                version[file_list[firmware]['FileName']] = file_list[firmware]['Version']

    for file in file_list:
        if file not in now_file_list:
            remove_dict_list.append(file)
    
    for file in remove_list:
        diff.remove(file)

    for file in remove_dict_list:
        del file_list[file]
    
    if diff:
        remove_list=[]
        for firmware in diff:
            try:
                if float(file_list[firmware]['Version']) > float(version[file_list[firmware]['FileName']]):
                    version[file_list[firmware]['FileName']] = file_list[firmware]['Version']            
                else:
                    remove_list.append(firmware)
            except:
                version[file_list[firmware]['FileName']] = file_list[firmware]['Version']
        for firmware in remove_list:
            diff.remove(firmware)

    if diff:
        print('='*30)
        print("Latest version")
        print('='*30)
        for key in version.keys():
            print(key + ": " + version[key])
        print('='*30)
        print("need to update about: ", diff)
        with open(version_json,"w") as version_file:
            version_file.write(json.dumps(version))

    return diff

def compute_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def make_message(FilePath):
    FileName = os.path.basename(FilePath)
    split_file_name = FileName.split('-')
    message = dict()
    message['FileName'] = split_file_name[-1]
    message['Version'] = split_file_name[1]
    message['Target'] = split_file_name[0]
    try:
        if message['Target'] == 'image':
            with open (FilePath ,"rb") as stream:
                img_bin = stream.read()
                encoded_img = base64.b64encode(img_bin)
            message['image'] = encoded_img.decode()
        else:
            with open(FilePath,'r',encoding='utf-8') as file:
                message['firmware']=file.read()

        
        print('='*30)
        print("File name: " + message['FileName'])
        print("File version: " + message['Version'])
        print("File version: " + message['Target'])
        print('='*30)
        return message
    
    except FileNotFoundError as e:
        print("Error:" + e)

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

    for key in path.keys(): 
        publish_list = []
        publish_list = check_new_firmware(path[key])

        if publish_list:
            for FileName in publish_list:
                client.connect(brokerIp, 1883)
                FilePath = path[key] + FileName
                client.loop_start()
                message = make_message(FilePath)
                client.publish('updates/' + message['FileName'], json.dumps(message), 2, retain= True)
                client.loop_stop()
                print("Success sending file:(updates/" + message['FileName']+ ")",FileName)
                client.disconnect()
        
        time.sleep(1.0)