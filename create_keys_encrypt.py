""" Create PUB/PRIV keys and encrypt config file """
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

PEM_PRIV = PRIVATE_KEY.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

with open('C:\\SwitchDomain\\private_key.pem', 'wb') as priv_key:
    priv_key.write(PEM_PRIV)
    priv_key.close()

PUBLIC_KEY = PRIVATE_KEY.public_key()
PEM_PUB = PUBLIC_KEY.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

with open('C:\\SwitchDomain\\public_key.pem', 'wb') as pub_key:
    pub_key.write(PEM_PUB)
    pub_key.close()

with open('C:\\SwitchDomain\\config.ini', 'rb') as config_file:
    config_data = config_file.read()
    config_file.close()

ENCRYPT_CONFIG = PUBLIC_KEY.encrypt(
    config_data,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

with open('C:\\SwitchDomain\\config.encrypted', 'wb') as encrypted_data:
    encrypted_data.write(ENCRYPT_CONFIG)
    encrypted_data.close()
