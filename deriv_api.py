import websocket
import json
import os
import time

class DerivBot:

    def __init__(self):
        self.ws = None
        self.token = os.getenv("DERIV_TOKEN")

    # =========================
    # CONEXIÓN
    # =========================

    def conectar(self):
        try:
            print("🔌 Conectando a Deriv...")

            url = "wss://ws.derivws.com/websockets/v3?app_id=1089"
            self.ws = websocket.create_connection(url)

            print("✅ WebSocket abierto")

            self.ws.send(json.dumps({
                "authorize": self.token
            }))

            response = json.loads(self.ws.recv())
            print("📩 Respuesta:", response)

            if "error" in response:
                print("❌ Error autorización:", response["error"])
                return False

            print("✅ AUTORIZADO")
            return True

        except Exception as e:
            print("❌ Error conexión:", e)
            return False

    # =========================
    # VELAS REALES
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

        except Exception as e:
            print("❌ Error velas:", e)

        return []

    # =========================
    # COMPRA
    # =========================

    def comprar(self, par, tipo, monto):

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
            print("🟢 COMPRA:", result)

            if "buy" in result:
                return result["buy"]["contract_id"]

        except Exception as e:
            print("❌ Error compra:", e)

        return None

    # =========================
    # RESULTADO
    # =========================

    def check_result(self, contract_id):

        try:
            self.ws.send(json.dumps({
                "proposal_open_contract": 1,
                "contract_id": contract_id
            }))

            while True:
                result = json.loads(self.ws.recv())

                if "proposal_open_contract" in result:
                    contrato = result["proposal_open_contract"]

                    if contrato["is_sold"]:
                        return contrato["profit"]

        except Exception as e:
            print("❌ Error resultado:", e)

        return 0
