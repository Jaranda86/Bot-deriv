import websocket
import json
import time
import os

class DerivBot:
    def __init__(self):
        self.token = os.getenv("DERIV_TOKEN")
        self.ws = None

    def connect(self):
        try:
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

    def comprar(self, par, tipo, monto=10):
        try:
            accion = "CALL" if tipo == "call" else "PUT"

            self.ws.send(json.dumps({
                "buy": 1,
                "price": monto,
                "parameters": {
                    "amount": monto,
                    "basis": "stake",
                    "contract_type": accion,
                    "currency": "USD",
                    "duration": 1,
                    "duration_unit": "m",
                    "symbol": par
                }
            }))

            result = json.loads(self.ws.recv())
            print("📦 RESPUESTA COMPRA:", result)

            return result

        except Exception as e:
            print("❌ Error compra:", e)
            return None
