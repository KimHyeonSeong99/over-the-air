import paho.mqtt.client as mqtt
import json
import os, time


Sub_Topic = "updates/firmware"
userId = "Alice"
userPw = "mose"
brokerIp = "203.246.114.226"
port = 1883
target_list = []

global update_firmware_path, latest_version, file_list
update_firmware_path = 'C:/Users/user/OTA/update_firm/'
latest_version = dict()
file_list = dict()

def check_new_firmware():
    diff = []
    remove_dict_list =[]
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

def make_json(FilePath):
    firmware = dict()
    FileName = FilePath.split('/')[-1]
    NamePart = FileName.split('-')
    try:
        with open(FilePath,'r',encoding='utf-8') as file:
            Content=file.readlines()
        Content = [line.strip() for line in Content]
        firmware['FileName'] = NamePart[-1]
        firmware['Version'] = NamePart[1]
        print("="*100)
        print(json.dumps(firmware,indent='\t'))
        print("="*100)
        with open(FilePath,'r',encoding='utf-8') as file:
            firmware['Firmware']=file.read()

        return json.dumps(firmware)

    except FileNotFoundError:
        pass

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

            client.publish(Sub_Topic, make_json(FilePath), 2, retain= True)
            client.loop_stop()
            print("Success sending file:",FileName)
            client.disconnect()
    
    time.sleep(1.0)
