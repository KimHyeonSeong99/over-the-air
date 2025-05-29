import os
import paho.mqtt.client as Client

broker_ip = "127.0.0.1"
broker_port = 1883
os.makedirs('firmware', exist_ok=True)  # Ensure firmware directory exists

def publish_message(broker_address, topic, message,port):
    client = Client()
    client.username_pw_set("mose", "mose")
    client.connect(broker_address, port)
    client.loop_start()  # Start the loop to process network events
    client.publish(topic, message)
    client.loop_stop()  # Stop the loop after publishing
    client.disconnect()

def publish_notion(broker_address, topic, port=1883):
    # Read firmware list once
    if os.path.exists('firmware_list.txt'):
        with open('firmware_list.txt', 'r') as file:
            firmware_list = file.read().splitlines()
    else:
        firmware_list = []

    for file_name in os.listdir('firmware'):
        if file_name.endswith(".bin") and file_name not in firmware_list:
            publish_message(broker_address, topic, file_name, port)
            firmware_list.append(file_name)

    # Write updated firmware list back to file
    with open('firmware_list.txt', 'w') as file:
        file.write('\n'.join(firmware_list))


if __name__ == "__main__":
    while True:  # Fixed infinite loop
        publish_notion(broker_ip, 'ota/update', 12011)
