from base_encrypt import *
from propose_encrypte import *
import os
import sys
import time
import matplotlib.pyplot as plt
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

data = os.urandom(1024)

key_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'key')
if not os.path.exists(key_dir):
    print(f"Key directory {key_dir} does not exist.")
    sys.exit(1)

# Load keys
master_key = read_key(key_name = os.path.join(key_dir, "master_key"))

def generate_update_packet(data: bytes, target: str, salt: bytes) -> bytes:
    if not data:
        raise ValueError("Data must not be empty.")
    if not target:
        raise ValueError("Target must not be empty.")

    digital_signature = sign_file(data, os.path.join(key_dir, "server_private.pem"))  # Sign the data with the server's private key
    data_bundle = digital_signature + data
    aes_key = os.urandom(32)  # Generate a 256-bit (32 bytes) AES key
    iv, encrypted_packet = encrypt_file_aes(data_bundle, aes_key)  # Encrypt the data using AES
    aes_token = encrypt_file_rsa(aes_key + iv, os.path.join(key_dir, "central_gateway_public.pem"))  # Combine AES key and IV for transmission

    ecu_unique_key = generate_ecu_unique_key(master_key=master_key, ecu_id=target.encode())
    one_time_key = generate_one_time_key(ecu_unique_key=ecu_unique_key, salt=salt)
    encrypted_data = generate_encrypted_data(data=data, key=one_time_key)
    authentication_head = generate_hash(data=encrypted_data)

    update_packet = aes_token + encrypted_packet + authentication_head

    return update_packet

def generate_base_update_packet(data: bytes, target: str) -> bytes:
    if not data:
        raise ValueError("Data must not be empty.")
    if not target:
        raise ValueError("Target must not be empty.")

    digital_signature = sign_file(data, os.path.join(key_dir, "server_private.pem"))  # Sign the data with the server's private key
    data_bundle = digital_signature + data
    aes_key = os.urandom(32)  # Generate a 256-bit (32 bytes) AES key
    iv, encrypted_packet = encrypt_file_aes(data_bundle, aes_key)  # Encrypt the data using AES
    aes_token = encrypt_file_rsa(aes_key + iv, os.path.join(key_dir, "central_gateway_public.pem"))  # Combine AES key and IV for transmission

    update_packet = aes_token +  encrypted_packet 

    return update_packet

def generate_double_update_packet(data: bytes, target: str) -> bytes:
    if not data:
        raise ValueError("Data must not be empty.")
    if not target:
        raise ValueError("Target must not be empty.")

    digital_signature = sign_file(data, os.path.join(key_dir, "server_private.pem"))  # Sign the data with the server's private key
    data_bundle = digital_signature + data
    aes_key = os.urandom(32)  # Generate a 256-bit (32 bytes) AES key
    iv, encrypted_packet = encrypt_file_aes(data_bundle, aes_key)  # Encrypt the data using AES
    aes_token = encrypt_file_rsa(aes_key + iv, os.path.join(key_dir, "central_gateway_public.pem"))  # Combine AES key and IV for transmission

    digital_signature = sign_file(data, os.path.join(key_dir, "server_private.pem"))  # Sign the data with the server's private key
    data_bundle = digital_signature + data
    ecu_aes_key = os.urandom(32)  # Generate a 256-bit (32 bytes) AES key
    ecu_iv, ecu_encrypted_packet = encrypt_file_aes(data_bundle, ecu_aes_key)  # Encrypt the data using AES
    ecu_aes_token = encrypt_file_rsa(ecu_aes_key + ecu_iv, os.path.join(key_dir, "ecu_public.pem"))

    update_packet = aes_token + ecu_aes_token + encrypted_packet + ecu_encrypted_packet

    return update_packet

def calculate_generation_time_propose():
    propose_time_list = []
    start_time = time.time()
    for i in tqdm(range(5000)):
        target = f"ECU_{i}"
        salt = generate_salt()
        _ = generate_update_packet(data=data, target=target, salt=salt)
        if i % 100 == 0:
            part_end_time = time.time()
            propose_time_list.append(part_end_time - start_time)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")

    return propose_time_list

def process_propose_packet(i):
    start = time.time()

    target = f"ECU_{i}"
    salt = generate_salt()
    _ = generate_update_packet(data=data, target=target, salt=salt)

    return time.time() - start  # 개별 처리 시간 반환

def calculate_generation_time_propose_parallel():
    total_start = time.time()
    
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        times = list(tqdm(executor.map(process_propose_packet, range(5000)), total=5000))

    total_time = time.time() - total_start
    print(f"\n[Propose] 전체 수행 시간: {total_time:.2f}초")
    print(f"[Propose] 평균 처리 시간: {sum(times)/len(times):.4f}초")

    return times

def calculate_generation_time_base():
    base_time_list = []
    start_time = time.time()
    for i in tqdm(range(5000)):
        target = f"ECU_{i}"
        _ = generate_base_update_packet(data=data, target=target)
        if i % 100 == 0:
            part_end_time = time.time()
            base_time_list.append(part_end_time - start_time)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds", end="\r")
    return base_time_list

def process_base_packet(i):
    start = time.time()

    target = f"ECU_{i}"
    _ = generate_base_update_packet(data=data, target=target)

    return time.time() - start  # 개별 처리 시간 반환

def calculate_generation_time_base_parallel():
    total_start = time.time()
    
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        times = list(tqdm(executor.map(process_base_packet, range(5000)), total=5000))

    total_time = time.time() - total_start
    print(f"\n[Base] 전체 수행 시간: {total_time:.2f}초")
    print(f"[Base] 평균 처리 시간: {sum(times)/len(times):.4f}초")

    return times

def calculate_generation_time_double():
    double_time_list = []
    start_time = time.time()
    for i in tqdm(range(5000)):
        target = f"ECU_{i}"
        _ = generate_double_update_packet(data=data, target=target)
        if i % 100 == 0:
            part_end_time = time.time()
            double_time_list.append(part_end_time - start_time)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds", end="\r")
    return double_time_list

def process_double_packet(i):
    start = time.time()

    target = f"ECU_{i}"
    _ = generate_double_update_packet(data=data, target=target)

    return time.time() - start  # 개별 처리 시간 반환

def calculate_generation_time_double_parallel():
    total_start = time.time()
    
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        times = list(tqdm(executor.map(process_double_packet, range(5000)), total=5000))

    total_time = time.time() - total_start
    print(f"\n[Double] 전체 수행 시간: {total_time:.2f}초")
    print(f"[Double] 평균 처리 시간: {sum(times)/len(times):.4f}초")

    return times

if __name__ == "__main__":
    
    propose_time_list = calculate_generation_time_propose()
    base_time_list = calculate_generation_time_base()
    double_time_list = calculate_generation_time_double()

    plt.figure(figsize=(10, 5))
    plt.plot(propose_time_list, label='Propose Update Packet Generation Time', color='blue')
    plt.plot(base_time_list, label='Base Update Packet Generation Time', color='orange')
    plt.plot(double_time_list, label = 'Double Update Packet Generation Time', color='green')
    plt.xlabel('Iteration')
    plt.ylabel('Time (seconds)')
    plt.title('Update Packet Generation Time Comparison')
    plt.legend()
    plt.grid()
    plt.show()
    
    _ = calculate_generation_time_propose_parallel()
    _ = calculate_generation_time_base_parallel()
    _ = calculate_generation_time_double_parallel()