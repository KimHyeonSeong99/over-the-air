import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Encrypt file data using AES
def encrypt_file_aes(file_data, aes_key):
    block_size = algorithms.AES.block_size

    # Apply PKCS7 padding
    padder = PKCS7(block_size).padder()
    padded_data = padder.update(file_data) + padder.finalize()

    # Generate a 16-byte IV
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    cipher_text = encryptor.update(padded_data) + encryptor.finalize()
    return iv, cipher_text

# Decrypt AES-encrypted data
def decrypt_file_aes(cipher_text, aes_key, iv):
    block_size = algorithms.AES.block_size

    try:
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(cipher_text) + decryptor.finalize()

        # Remove PKCS7 padding
        unpadder = PKCS7(block_size).unpadder()
        decrypted_text = unpadder.update(padded_data) + unpadder.finalize()
        return decrypted_text
    except Exception as e:
        raise ValueError(f'Decryption failed: {e}')

# Generate RSA key pair and save to files
def rsa_key_generation(key_name: str, private_key_pw: str = 'private'):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )
    public_key = private_key.public_key()

    # Serialize private key to PEM format (with encryption)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(private_key_pw.encode())
    )

    # Serialize public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Create key storage directory
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'key')
    os.makedirs(key_path, exist_ok=True)

    # Save private key to file
    private_key_path = os.path.join(key_path, f"{key_name}_private.pem")
    with open(private_key_path, 'wb') as key_file:
        key_file.write(private_pem)

    # Save public key to file
    public_key_path = os.path.join(key_path, f"{key_name}_public.pem")
    with open(public_key_path, 'wb') as key_file:
        key_file.write(public_pem)

# Encrypt file data using RSA public key
def encrypt_file_rsa(file_data, public_key_path):
    with open(public_key_path, 'rb') as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    encrypted_file = public_key.encrypt(
        file_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_file

# Decrypt data encrypted with RSA using private key
def decrypt_file_rsa(encrypted_data, private_key_path):
    with open(private_key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=b'private',
            backend=default_backend()
        )
    decrypted_file = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_file

# Compute SHA-256 hash of a file
def compute_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

# Sign file data using RSA private key
def sign_file(file_data, private_key_path):
    with open(private_key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=b'private',
            backend=default_backend()
        )

    signature = private_key.sign(
        file_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

# Verify signature using RSA public key
def verify_sign(signature, file_data, public_key_path):
    with open(public_key_path, 'rb') as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    try:
        public_key.verify(
            signature,
            file_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

if __name__ == "__main__":
    rsa_key_generation()