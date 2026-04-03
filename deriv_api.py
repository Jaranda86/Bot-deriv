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
            self.ws = websocket.create_connection(
                "wss://ws.derivws.com/websockets/v3?app_id=1089"
            )

            self.ws.send(json.dumps({
                "authorize": self.token
            }))

            res = json.loads(self.ws.recv())

            if "error" in res:
                print("❌ Error token:", res)
                return False

            print("✅ Conectado a Deriv")
            return True

        except Exception as e:
            print("❌ Error conexión:", e)
            return False

    def operar(self, symbol, action):
        try:
            tipo = "CALL" if action == "call" else "PUT"

            # 🔹 PASO 1: PEDIR PROPUESTA
            self.ws.send(json.dumps({
                "proposal": 1,
                "amount": 1,
                "basis": "stake",
                "contract_type": tipo,
                "currency": "USD",
                "duration": 1,
                "duration_unit": "m",
                "symbol": symbol
            }))

            proposal = json.loads(self.ws.recv())

            if "error" in proposal:
                print("❌ Error proposal:", proposal)
                return False

            proposal_id = proposal["proposal"]["id"]

            # 🔹 PASO 2: COMPRAR CONTRATO REAL
            self.ws.send(json.dumps({
                "buy": proposal_id,
                "price": 1
            }))

            buy = json.loads(self.ws.recv())

            if "error" in buy:
                print("❌ Error compra:", buy)
                return False

            contract_id = buy["buy"]["contract_id"]

            print(f"📄 Contract ID: {contract_id}")

            # 🔹 ESPERAR RESULTADO
            time.sleep(65)

            self.ws.send(json.dumps({
                "proposal_open_contract": 1,
                "contract_id": contract_id
            }))

            result = json.loads(self.ws.recv())

            contract = result.get("proposal_open_contract", {})
            profit = contract.get("profit", 0)

            print(f"📊 Profit: {profit}")

            return profit > 0

        except Exception as e:
            print("❌ Error operar:", e)
            return False
