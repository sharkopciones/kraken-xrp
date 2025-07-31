import logging
logging.basicConfig(level=logging.INFO)

from flask import Flask, request, jsonify
import os
import time
import hmac
import hashlib
import base64
import requests

app = Flask(__name__)

API_KEY = os.getenv("KRAKEN_API_KEY")
API_SECRET = os.getenv("KRAKEN_API_SECRET")
KRAKEN_URL = "https://futures.kraken.com/derivatives/api/v3/sendorder"

def sign_request(data_str, nonce):
    message = nonce + data_str
    signature = hmac.new(base64.b64decode(API_SECRET), message.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()

@app.route('/webhook', methods=['POST'])
def webhook():
    logging.info("Se activó el endpoint /webhook")

    try:
        payload = request.get_json(force=True)
        if payload:
            logging.info(f"Alerta recibida: {payload}")
        else:
            logging.warning("⚠️ El payload está vacío o mal formado")
    except Exception as e:
        logging.error(f"❌ Error al procesar el JSON: {e}")

    return jsonify({"status": "ok"})

    side = payload.get("action")  # "buy" o "sell"
    size = str(payload.get("size", 1))
    symbol = payload.get("market", "pi_xrpusd")
    order_type = "mkt"

    nonce = str(int(time.time() * 1000))
    data_str = f"orderType={order_type}&side={side}&size={size}&symbol={symbol}"

    headers = {
        "APIKey": API_KEY,
        "Nonce": nonce,
        "Authent": sign_request(data_str, nonce),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(KRAKEN_URL, headers=headers, data=data_str)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
