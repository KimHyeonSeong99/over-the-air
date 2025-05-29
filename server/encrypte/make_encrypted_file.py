import hashlib
import os
import sys

program_dir = os.path.dirname(os.path.abspath(__file__))

def get_master_key():
    master_key_path = os.path.join(program_dir,'key/MASTERKEY.pem')
    try:
        with open(os.path.join(program_dir,'key/MASTERKEY_HASH.pem'),'rb') as hash:
            master_key_hash = hash.read().decode()
        if compute_file_hash(master_key_path) == master_key_hash:
            with open(master_key_path,'rb') as file:
                master_key = file.read()
        else:
            print("The master key has some problem! Stop processing now!")
            sys.exit()
    except FileNotFoundError as e:
        print(e)
        sys.exit()

    return master_key

def generate_encrypt_key(master_key: bytes, salt: int = 1, ecu_id: bytes = None, iterations_derived: int = 10000, iterations_encrypted: int = 100) -> bytes:
    derived_key = hashlib.pbkdf2_hmac(
        'sha256',
        master_key,
        ecu_id,
        iterations_derived,  
        dklen=4096
    )

    encrypt_key = hashlib.pbkdf2_hmac(
        'sha256',
        derived_key,
        str(salt).encode('utf-8'),
        iterations_encrypted,  
        dklen=4096
    )

    return encrypt_key.hex()
   
# Function to compute the SHA-256 hash of a file
def compute_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()

def compute_data_hash(data: bytes, chunk_size: int = 4096):
    sha256_hash = hashlib.sha256()
    for i in range(0, len(data), chunk_size):
        chunk = data[i:max(i + chunk_size,len(data))]  # 4096바이트씩 청크로 나누기
        sha256_hash.update(chunk)  # 각 청크를 업데이트
    return sha256_hash.hexdigest()

def xor_file_with_ecu_key(file_path, ecu_key, chunk_size=4096):
    encrypted_chunks = []

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            encrypted_chunk = bytes(chunk[i] ^ ecu_key[i % chunk_size] for i in range(len(chunk)))
            encrypted_chunks.append(encrypted_chunk)  # XOR된 블록 저장

    return encrypted_chunks

def compute_file_hash_with_unique_key(file_path, vehicle_salt, ecu_id):
    ecu_key = generate_encrypt_key(master_key=get_master_key(), salt = vehicle_salt, ecu_id=ecu_id).encode('utf-8')
    encrypted_chunks = xor_file_with_ecu_key(file_path, ecu_key)
    encrypted_data = b''.join(encrypted_chunks)  # Concatenate chunks into a single bytes object
    encrypted_hash = compute_data_hash(encrypted_data)

    return encrypted_hash.encode()
