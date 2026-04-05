import websocket
import json
import time
import os

class DerivBot:
    def __init__(self):
        self.token = os.getenv("DERIV_TOKEN")
        self.ws = None

    def conectar(self):
        try:
            print("🔌 Conectando a Deriv...")
            url = "wss://ws.derivws.com/websockets/v3?app_id=1089"

            self.ws = websocket.create_connection(url)

            self.ws.send(json.dumps({
                "authorize": self.token
            }))

            response = json.loads(self.ws.recv())

            if "error" in response:
                print("❌ Error conexión:", response)
                return False

            print("✅ Conectado a Deriv")
            return True

        except Exception as e:
            print("❌ Error conexión Deriv:", e)
            return False

    # =========================
    # 📊 OBTENER VELAS REALES
    # =========================
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

            return []

        except Exception as e:
            print("❌ Error velas:", e)
            return []

    # =========================
    # 💰 COMPRAR REAL
    # =========================
    def comprar(self, par, tipo, monto):
        try:
            accion = "CALL" if tipo == "call" else "PUT"

            print(f"💰 EJECUTANDO {par} {accion} con monto: {monto}")

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
            print("📊 RESPUESTA COMPRA:", result)

            if "buy" in result:
                return result["buy"]["contract_id"]

            return None

        except Exception as e:
            print("❌ Error comprar:", e)
            return None

    # =========================
    # 📈 RESULTADO REAL
    # =========================
    def check_result(self, contract_id):
        try:
            self.ws.send(json.dumps({
                "proposal_open_contract": 1,
                "contract_id": contract_id
            }))

            result = json.loads(self.ws.recv())

            if "proposal_open_contract" in result:
                return result["proposal_open_contract"]["profit"]

            return 0

        except Exception as e:
            print("❌ Error resultado:", e)
            return 0
