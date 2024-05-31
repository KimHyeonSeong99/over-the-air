import json
import os
import socket
import base64, cv2, io
from PIL import Image
import numpy as np

file_path = '/home/sea/sea-me-hackathon-2023/Cluster/src/'

def receive_file(server_host, server_port, buffer_size=4096):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((server_host, server_port))
        server_socket.listen(1)
        print(f"Server listening on {server_host}:{server_port}")
        
        conn, addr = server_socket.accept()
        with conn:
            message = ""
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(buffer_size).decode('utf-8')
                if not data:
                    break
                message += data
            message = json.loads(message)
            file_name = message['FileName']
            if file_name.split('.')[-1] == 'png':
                image = message['image']
                decode_img = base64.b64decode(image.encode())
                img_out = Image.open(io.BytesIO(decode_img))
                img_array = np.array(img_out)
                img = cv2.cvtColor(img_array,cv2.COLOR_BGR2RGB)
                cv2.imwrite(file_path + 'image/' + file_name, img)
            else:
                firmware = message['firmware']
                with open(file_path + file_name, "w") as f:
                    f.write(content)
            print("File received successfully.")


server_host = "192.168.1.170"  # Listen on all interfaces
server_port = 12345

while True:
    receive_file(server_host, server_port)
    os.chdir('/home/sea/sea-me-hackathon-2023/Cluster/src/')
    os.system("make -j6")
