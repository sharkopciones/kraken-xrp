def send_order(symbol, side, size):
    nonce = str(int(time.time() * 1000))
    
    # Construimos el payload completo
    data = {
        "orderType": "mkt",
        "side": side,
        "size": size,
        "symbol": symbol,
        "nonce": nonce
    }
    
    # urlencoded con TODOS los campos (incluyendo nonce)
    data_str = urlencode(data)
    
    # Firma HMAC usando el mismo data_str que se va a enviar
    authent = sign_request(data_str, nonce)
    
    # Logs de depuración
    logging.info(f"Nonce usado: {nonce}")
    logging.info(f"Data string firmada: {data_str}")
    logging.info(f"Firma generada: {authent}")
    
    headers = {
        "APIKey": API_KEY,
        "Authent": authent,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Enviar orden (mismo data_str)
    response = requests.post(
        "https://futures.kraken.com/derivatives/api/v3/sendorder",
        headers=headers,
        data=data_str
    )

    logging.info(f"Respuesta Kraken: {response.text}")
    return response.json()
