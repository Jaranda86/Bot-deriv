import websocket
import json
import os
import time


class DerivBot:
    def __init__(self):
        self.ws = None
        self.token = os.getenv("DERIV_TOKEN")
        self.app_id = "1089"

    def conectar(self):
    try:
        print("🔌 Conectando a Deriv...")

        if not self.token:
            print("❌ TOKEN NO DEFINIDO")
            return False

        url = f"wss://ws.derivws.com/websockets/v3?app_id={self.app_id}"

        self.ws = websocket.create_connection(url, timeout=10)

        print("✅ WebSocket abierto")

        self.ws.send(json.dumps({
            "authorize": self.token
        }))

        res = json.loads(self.ws.recv())

        print("📩 Respuesta:", res)

        if "error" in res:
            print("❌ Error autorización:", res["error"])
            return False

        print("✅ AUTORIZADO")
        return True

    except Exception as e:
        print("❌ ERROR CONEXIÓN:", e)
        return False

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

            res = json.loads(self.ws.recv())

            if "candles" in res:
                return res["candles"]

            return []

        except Exception as e:
            print("❌ Error velas:", e)
            return []

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

            res = json.loads(self.ws.recv())

            if "error" in res:
                print("❌ Error compra:", res["error"])
                return None

            return res["buy"]["contract_id"]

        except Exception as e:
            print("❌ Error comprar:", e)
            return None

    # =========================
    def check_result(self, contract_id):
        try:
            self.ws.send(json.dumps({
                "proposal_open_contract": 1,
                "contract_id": contract_id
            }))

            while True:
                res = json.loads(self.ws.recv())

                if "proposal_open_contract" in res:
                    contract = res["proposal_open_contract"]

                    if contract["is_sold"]:
                        return contract["profit"]

                time.sleep(2)

        except Exception as e:
            print("❌ Error resultado:", e)
            return 0
