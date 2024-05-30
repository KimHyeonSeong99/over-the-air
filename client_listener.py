
import os
import socket
file_path = '/home/sea/sea-me-hackathon-2023/Cluster/src/'

def receive_file(server_host, server_port, buffer_size=4096):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((server_host, server_port))
        server_socket.listen(1)
        print(f"Server listening on {server_host}:{server_port}")
        
        conn, addr = server_socket.accept()
        file_name = conn.recv()
        with conn:
            print(f"Connected by {addr}")
            with open(file_path + file_name, "wb") as f:
                while True:
                    data = conn.recv(buffer_size)
                    if not data:
                        break
                    f.write(data)
            print("File received successfully.")


server_host = "0.0.0.0"  # Listen on all interfaces
server_port = 12345

while True:
    receive_file(server_host, server_port)
    os.chdir('/home/sea/sea-me-hackathon-2023/Cluster/src/')
    os.system("make -j6")