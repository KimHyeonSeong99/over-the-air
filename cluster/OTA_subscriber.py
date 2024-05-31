import paho.mqtt.client as mqtt
import json, io
import os, cv2, base64
import time
from tkinter import *
from tkinter import messagebox
import socket
import numpy as np

timelist = {'Now':0,'10min':600,'1hour':3600,'1day':86400,'1week':604800}
Sub_Topic = "updates/" 
userId = "Alice"
userPw = "mose"
brokerIp = "203.246.114.226"
port = 1883
server_host = "remote_host_ip_or_domain"
server_port = 12345
tmpDirectory = "C:/Users/user/OTA/tmp/"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    with open(tmpDirectory + 'version.json', 'r') as version_json:
        version = json.load(version_json)
    for key in version.keys():
        client.subscribe(Sub_Topic+ key)

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

def send_file(server_host, server_port, file_path, buffer_size=4096):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_host, server_port))
        print(f"Connected to server {server_host}:{server_port}")
        client_socket.sendall(file_path.split('/')[-1])
        with open(file_path, "rb") as f:
            while (data := f.read(buffer_size)):
                client_socket.sendall(data)
        print("File sent successfully.")

# subscriber callback
def on_message(client, userdata, msg):

    try:
        versionPath = os.path.join(tmpDirectory,"version.json")
        with open(versionPath,"r") as versionlist:
            version = json.load(versionlist) 
    except:
        version = dict()

    payload = json.loads(msg.payload)
    FileName = payload['FileName']
    FileVersion = payload['Version']
    FileTarget = payload['Target']
    if float(version[FileName]) < float(FileVersion):
        if FileTarget == 'firmware':
            try:
                FileData = payload['firmware']
            except:
                print('Error: wrong target!')
            try:
                firmwarePath = os.path.join(tmpDirectory, FileName)
                with open(firmwarePath,"w") as stream:
                    stream.write(FileData) 
                time.sleep(1)
                print(f"Firmware downloaded and saved to {tmpDirectory}")
            except Exception as e:
                print(f"Error downloading the firmware: {e}")
                print(f"firmwareDirectory: {tmpDirectory}")
                print(f"firmwarePath: {firmwarePath}")
        else:
            ImageData = payload['image'].encode()
            decode_img = base64.b64decode(ImageData)
            img_out = Image.open(io.BytesIO(decode_img))
            img_array = np.array(img_out)
            img = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
            cv2.imwrite(firmwarePath, img)

        flag = 1
        while(flag):
            flag = update_choice()
            time.sleep(flag)
        send_file(server_host, server_port, firmwarePath)
        version[FileName] = FileVersion
        with open(versionPath,"w") as versionlist:
            versionlist.write(json.dumps(version))

    else:
        print("="*50)
        print("File name: " + FileName)
        print("File version: " + FileVersion)
        print("Latest version: " + version[FileName])
        print("new firmware version is old version, pass the update")
        print("="*50)


    print("Ready for a new update")


client = mqtt.Client()
client.username_pw_set(userId, userPw)
client.on_connect = on_connect
client.on_message = on_message

client.connect(brokerIp, port, 60)

client.loop_forever()





