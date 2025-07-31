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
        if not payload:
            logging.warning("⚠️ El payload está vacío o mal formado")
            return jsonify({"status": "payload vacío"})

        logging.info(f"Alerta recibida: {payload}")

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

        # 🔍 Registro detallado para depuración
        logging.info(f"Respuesta completa de Kraken: {response.text}")

        try:
            kr = response.json()
            logging.info(f"Respuesta JSON de Kraken: {kr}")
            return jsonify(kr)
        except Exception as e:
            logging.error(f"❌ Error al parsear JSON de Kraken: {e}")
            return jsonify({"status": "error", "message": str(e)})

    except Exception as e:
        logging.error(f"❌ Error general en webhook: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
