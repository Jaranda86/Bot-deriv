import websocket
import json
import time


class DerivBot:
    def __init__(self):
        self.token = "TU_TOKEN_DERIV"
        self.ws = None
        self.balance = 0

    def connect(self):
        try:
            self.ws = websocket.create_connection("wss://ws.binaryws.com/websockets/v3")

            self.ws.send(json.dumps({
                "authorize": self.token
            }))

            response = json.loads(self.ws.recv())

            if "error" in response:
                print("❌ Error autorización:", response)
                return False

            self.balance = response["authorize"]["balance"]
            print("✅ Conectado a Deriv | Balance:", self.balance)
            return True

        except Exception as e:
            print("❌ Error conexión:", e)
            return False

    def get_balance(self):
        try:
            self.ws.send(json.dumps({"balance": 1}))
            response = json.loads(self.ws.recv())

            if "balance" in response:
                self.balance = response["balance"]["balance"]
                return self.balance

        except:
            pass

        return self.balance

    def get_candles(self, symbol, count=50):
        try:
            self.ws.send(json.dumps({
                "ticks_history": symbol,
                "end": "latest",
                "count": count,
                "style": "candles",
                "granularity": 60
            }))

            response = json.loads(self.ws.recv())

            if "error" in response:
                print("❌ Error velas:", response)
                return None

            return response["candles"]

        except Exception as e:
            print("❌ Error velas:", e)
            return None

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
            print("📦 Compra:", result)

            time.sleep(65)  # esperar resultado real

            nuevo_balance = self.get_balance()

            if nuevo_balance > self.balance:
                self.balance = nuevo_balance
                return "win"
            else:
                self.balance = nuevo_balance
                return "loss"

        except Exception as e:
            print("❌ Error compra:", e)
            return "loss"
