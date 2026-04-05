import websocket
import json
import os
import time

class DerivBot:
    def __init__(self):
        self.ws = None
        self.token = os.getenv("DERIV_TOKEN")
        self.balance = 0

    def connect(self):
        try:
            print("🔌 Conectando a Deriv...")

            url = "wss://ws.derivws.com/websockets/v3?app_id=1089"
            self.ws = websocket.create_connection(url)

            # Autorizar
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

    def get_balance(self):
        try:
            self.ws.send(json.dumps({
                "balance": 1
            }))

            response = json.loads(self.ws.recv())

            if "balance" in response:
                self.balance = response["balance"]["balance"]
                return self.balance

        except:
            return None

    def get_candles(self, symbol):
        try:
            self.ws.send(json.dumps({
                "ticks_history": symbol,
                "adjust_start_time": 1,
                "count": 50,
                "end": "latest",
                "granularity": 60,
                "style": "candles"
            }))

            response = json.loads(self.ws.recv())

            if "candles" in response:
                return response["candles"]

        except Exception as e:
            print("❌ Error velas:", e)

        return []

    def comprar(self, par, tipo, monto=1):
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

            print("📦 COMPRA:", result)

            if "buy" in result:
                return "ok"

        except Exception as e:
            print("❌ Error compra:", e)

        return "error"
