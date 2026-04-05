import websocket
import json
import time


class DerivBot:
    def __init__(self):
        self.token = "TU_TOKEN_DERIV"  # 🔴 PONÉ TU TOKEN
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

            print("✅ Conectado a Deriv")
            return True

        except Exception as e:
            print("❌ Error conexión:", e)
            return False

    # =========================
    # 📊 OBTENER VELAS REALES
    # =========================
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
            print("❌ Error obteniendo velas:", e)
            return None

    # =========================
    # 💰 COMPRAR
    # =========================
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

            print("📦 RESPUESTA COMPRA:", result)

            # simulación básica resultado
            if "buy" in result:
                return "win" if result["buy"]["balance_after"] > self.balance else "loss"

            return "loss"

        except Exception as e:
            print("❌ Error compra:", e)
            return "loss"
