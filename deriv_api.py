import websocket
import json
import os
import time

class DerivBot:
    def __init__(self):
        self.token = os.getenv("DERIV_TOKEN")
        self.ws = None

    def connect(self):
        try:
            if not self.token:
                print("❌ Token no encontrado")
                return False

            self.ws = websocket.create_connection("wss://ws.derivws.com/websockets/v3?app_id=1089")

            self.ws.send(json.dumps({
                "authorize": self.token
            }))

            response = json.loads(self.ws.recv())

            if "error" in response:
                print("❌ Error autorización:", response)
                return False

            print("✅ Conectado a Deriv")
            return True

        except Exception as e:
            print("❌ Error conexión:", e)
            return False

    def operar(self, symbol, action):
        try:
            self.ws.send(json.dumps({
                "buy": 1,
                "price": 1,
                "parameters": {
                    "amount": 1,
                    "basis": "stake",
                    "contract_type": "CALL" if action == "call" else "PUT",
                    "currency": "USD",
                    "duration": 1,
                    "duration_unit": "m",
                    "symbol": symbol
                }
            }))

            response = json.loads(self.ws.recv())

            if "error" in response:
                print("❌ Error operación:", response)
                return False

            time.sleep(60)

            return True  # simulación simple

        except Exception as e:
            print("❌ Error operar:", e)
            return False
