import os
import time
import hmac
import hashlib
import base64
import logging
import requests
from flask import Flask, request, jsonify
from urllib.parse import urlencode
from collections import OrderedDict

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Cargar claves desde entorno
API_KEY = os.getenv("KRAKEN_API_KEY")
API_SECRET = os.getenv("KRAKEN_API_SECRET")

# Log de verificación
logging.info(f"API_SECRET length: {len(API_SECRET)} caracteres")

def sign_request(data_str, nonce):
    message = nonce + data_str
    secret = base64.b64decode(API_SECRET)
    signature = hmac.new(secret, message.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()

def send_order(symbol, side, size):
    nonce = str(int(time.time() * 1000))

    data = OrderedDict([
        ("orderType", "mkt"),
        ("side", side),
        ("size", size),
        ("symbol", symbol),
        ("nonce", nonce)
    ])

    data_str = urlencode(data)
    authent = sign_request(data_str, nonce)

    headers = {
        "APIKey": API_KEY,
        "Authent": authent,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    logging.info(f"Headers enviados: {headers}")
    logging.info(f"Body enviado (raw): {data_str}")

    # Enviar como bytes crudos (no recodificado)
    response = requests.post(
        "https://futures.kraken.com/derivatives/api/v3/sendorder",
        headers=headers,
        data=data_str.encode("utf-8")
    )

    logging.info(f"Respuesta completa de Kraken: {response.text}")
    return response.json()

# Configurar Flask
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    logging.info("Se activó el endpoint /webhook")
    payload = request.json
    logging.info(f"Alerta recibida: {payload}")

    action = payload.get("action")
    symbol = payload.get("market")
    size = payload.get("size")

    if not (action and symbol and size):
        return jsonify({"error": "Campos incompletos"}), 400

    side = "buy" if action == "buy" else "sell"
    result = send_order(symbol, side, size)
    logging.info(f"Respuesta JSON de Kraken: {result}")
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
