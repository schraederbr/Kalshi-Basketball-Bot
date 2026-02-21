from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import requests
import datetime

class kalshi:
    def __init__(self, key_id = "f34865f7-b2ba-4235-ba21-df0bfdc727a3", key_file="private.key"):
        self.key_id = key_id
        self.private_key = self.load_private_key(key_file)

    def load_private_key(self, file_path):
        with open(file_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,  # or provide a password if your key is encrypted
                backend=default_backend()
            )
        return private_key
    


    def sign(self, timestamp, method, path):
        path_without_query = path.split('?')[0]

        message = f"{timestamp}{method}{path_without_query}".encode('utf-8')

        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=hashes.SHA256().digest_size,
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')


    def send(self, path, method = "GET", url_base = 'https://api.elections.kalshi.com'):
        timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
        method = "GET"
        signature = self.sign(timestamp, method, path)
        headers = {
            'KALSHI-ACCESS-KEY': self.key_id,
            'KALSHI-ACCESS-SIGNATURE': signature,
            'KALSHI-ACCESS-TIMESTAMP': timestamp
        }
        response = requests.get(url_base + path, headers=headers)
        return response

k = kalshi()

balance_response = k.send(path = "/trade-api/v2/portfolio/balance").json()

print(f"Your balance: ${balance_response['balance'] / 100:.2f}")



