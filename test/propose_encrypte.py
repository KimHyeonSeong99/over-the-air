import hashlib
import os

# Generate a salt
# Active on the Central gateway side
def generate_salt() -> bytes:
    salt = os.urandom(16)  # Generate a random 16-byte salt
    return salt

# Read the key from the memory
# Active on the Server and ECU both sides
def read_key(key_name: str) -> bytes:
    if key_name:
        key_name = key_name.strip()
        key_path = '.'.join([key_name, 'pem'])
        key_hash_path = '.'.join([key_name, 'hash'])
    else:
        raise ValueError("File name must be provided.")

    if not os.path.exists(key_path):
        raise FileNotFoundError(f"Key file {key_path} does not exist.")

    with open(key_path, 'rb') as file:
        key = file.read()
    with open(key_hash_path, 'rb') as file:
        key_hash = file.read()

    if generate_hash(key) != key_hash:
        raise ValueError("Key does not match the key hash!")
    return key

# Generate the unique key of the ECU for generating an encrypt key for firmware update
# Active on the server side
def generate_ecu_unique_key(master_key: bytes, ecu_id: bytes) -> bytes:
    ecu_unique_key = hashlib.pbkdf2_hmac(
        hash_name = 'sha256',
        password = master_key,
        salt = ecu_id,
        iterations = 1000,
        dklen = 128
    )
    return ecu_unique_key

# Generate the encrypt key for firmware update
# Active on the Server and ECU both sides
def generate_one_time_key(ecu_unique_key: bytes, salt: bytes) -> bytes:
    one_time_key = hashlib.pbkdf2_hmac(
        hash_name = 'sha256',
        password = ecu_unique_key,
        salt = salt,
        iterations = 10,
        dklen = 128
    )
    return one_time_key

# Generate hash for the data
# Active on the Server and ECU both sides
def generate_hash(data: bytes) -> bytes:
    if not data:
        raise ValueError("Data must not be empty.")
    return hashlib.sha256(data).digest()

# Generate the encrypted data
# Active on the Server and ECU both sides
def generate_encrypted_data(data: bytes, key: bytes) -> bytes:
    if not data:
        raise ValueError("Data must not be empty.")
    if not key:
        raise ValueError("Key must not be empty.")

    # Simple XOR encryption for demonstration purposes
    return bytes([b ^ k for b, k in zip(data, key)])