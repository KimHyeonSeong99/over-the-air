from base_encrypt import rsa_key_generation
from propose_encrypte import generate_ecu_unique_key, read_key
import os
import hashlib
from typing import Tuple  # Add this import

def generate_master_key() -> Tuple[bytes, bytes]:
    master_key = os.urandom(1024)
    master_key_hash = hashlib.sha256(master_key).digest()

    return master_key, master_key_hash

if __name__ == "__main__":
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'key')
    os.makedirs(key_path, exist_ok=True)
    rsa_key_generation("central_gateway")
    rsa_key_generation("server")
    rsa_key_generation("ecu")
    generated_master_key, generated_master_key_hash = generate_master_key()
    with open(os.path.join(key_path, "master_key.pem"), "wb") as f:
        f.write(generated_master_key)
    with open(os.path.join(key_path, "master_key.hash"), "wb") as f:
        f.write(generated_master_key_hash)
    master_key = read_key(key_name = os.path.join(key_path, "master_key"))
    ecu_unique_key = generate_ecu_unique_key(master_key = master_key, ecu_id = b"ECU_ID")
    ecu_unique_key_hash = hashlib.sha256(ecu_unique_key).digest()
    with open(os.path.join(key_path, "ecu_unique_key.pem"), "wb") as f:
        f.write(ecu_unique_key)
    with open(os.path.join(key_path, "ecu_unique_key.hash"), "wb") as f:
        f.write(ecu_unique_key_hash)