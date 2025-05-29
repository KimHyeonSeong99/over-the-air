from flask import Flask, request, send_file
import os
import zipfile  # 추가된 모듈
from make_encrypted_file import compute_file_hash_with_unique_key
import paho.mqtt.client as Client

broker_ip = "127.0.0.1"
broker_port = 1883

def publish_message(broker_address, topic, message,port):
    client = Client()
    client.username_pw_set("mose", "mose")
    client.connect(broker_address, port)
    client.loop_start()  # Start the loop to process network events
    client.publish(topic, message)
    client.loop_stop()  # Stop the loop after publishing
    client.disconnect()

app = Flask(__name__)

@app.route("/get_update", methods=["GET"])
def get_update():
    update_file_name = request.args.get("filename")
    
    # Check for missing parameters
    if not update_file_name:
        return "Missing required parameters", 400

    # Ensure paths are sanitized
    update_file_name = os.path.basename(update_file_name)

    os.makedirs(f"./updates", exist_ok=True)
    with open(f"./updates/{update_file_name}", "wb") as f:
        with open(f"firmware/{update_file_name}", "rb") as original_file:
            f.write(original_file.read())
    file_path = f"./updates/{update_file_name}"
    zip_path = f"./updates/update_package.zip"

    try:
        # ZIP 파일 생성
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(file_path, arcname=f"{update_file_name}")

        # ZIP 파일 전송
        return send_file(zip_path, as_attachment=True)
    except FileNotFoundError:
        # 파일이 없으면 404 응답
        return "Update file not found", 404

def publish_notion(broker_address, firmware_dir_path, topic, port=1883):
    # Read firmware list once
    if os.path.exists('firmware_list.txt'):
        with open('firmware_list.txt', 'r') as file:
            firmware_list = file.read().splitlines()
    else:
        firmware_list = []

    for file_name in os.listdir(firmware_dir_path):
        if file_name.endswith(".bin") and file_name not in firmware_list:
            publish_message(broker_address, topic, file_name, port)
            firmware_list.append(file_name)

    # Write updated firmware list back to file
    with open('firmware_list.txt', 'w') as file:
        file.write('\n'.join(firmware_list))

if __name__ == "__main__":
    app.run(ssl_context=('key/server_cert.pem', 'key/server_key.pem'), host='0.0.0.0', port=5000)
    while True:  # Fixed infinite loop
        publish_notion(broker_ip, 'firmware', 'ota/update', 12011)
