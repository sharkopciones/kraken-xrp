import hmac
import hashlib
import base64
import time
import os
import logging
from urllib.parse import urlencode

# Cargar claves desde variables de entorno
API_KEY = os.getenv("KRAKEN_API_KEY")
API_SECRET = os.getenv("KRAKEN_API_SECRET")

def sign_request(data_str, nonce):
    # Construir mensaje a firmar
    message = nonce + data_str
    secret = base64.b64decode(API_SECRET)
    signature = hmac.new(secret, message.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()

def send_order(symbol, side, size):
    nonce = str(int(time.time() * 1000))
    data = {
        "orderType": "mkt",
        "side": side,
        "size": size,
        "symbol": symbol,
        "nonce": nonce
    }
    data_str = urlencode({
        "orderType": "mkt",
        "side": side,
        "size": size,
        "symbol": symbol
    })

    # Firma HMAC
    authent = sign_request(data_str, nonce)

    # Logs de depuración
    logging.info(f"Nonce usado: {nonce}")
    logging.info(f"Data string: {data_str}")
    logging.info(f"Firma generada: {authent}")

    headers = {
        "APIKey": API_KEY,
        "Authent": authent,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Enviar orden
    response = requests.post(
        "https://futures.kraken.com/derivatives/api/v3/sendorder",
        headers=headers,
        data=urlencode(data)
    )

    logging.info(f"Respuesta Kraken: {response.text}")
    return response.json()
