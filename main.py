from collections import OrderedDict

def send_order(symbol, side, size):
    nonce = str(int(time.time() * 1000))

    # Orden estricto de campos
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
logging.info(f"Body enviado: {data_str}")

    response = requests.post(
        "https://futures.kraken.com/derivatives/api/v3/sendorder",
        headers=headers,
        data=data_str
    )

    logging.info(f"Nonce: {nonce}")
    logging.info(f"Data string firmada: {data_str}")
    logging.info(f"Firma generada: {authent}")
    logging.info(f"Respuesta completa de Kraken: {response.text}")
    return response.json()
