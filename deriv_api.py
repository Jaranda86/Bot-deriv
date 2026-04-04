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
                print("❌ Error autorización:", response["error"]["message"])
                return False

            print("✅ Conectado a Deriv")
            return True

        except Exception as e:
            print("❌ Error conexión:", e)
            return False

    def get_balance(self):
        try:
            self.ws.send(json.dumps({"balance": 1}))
            response = json.loads(self.ws.recv())
            return response["balance"]["balance"]
        except:
            return 0

    def comprar(self, symbol, tipo):
        try:
            # 1. pedir propuesta
            self.ws.send(json.dumps({
                "proposal": 1,
                "amount": 1,
                "basis": "stake",
                "contract_type": tipo,
                "currency": "USD",
                "duration": 5,
                "duration_unit": "t",
                "symbol": symbol
            }))

            proposal = json.loads(self.ws.recv())

            if "error" in proposal:
                print("❌ Error proposal:", proposal)
                return None

            proposal_id = proposal["proposal"]["id"]

            # 2. comprar
            self.ws.send(json.dumps({
                "buy": proposal_id,
                "price": 1
            }))

            buy = json.loads(self.ws.recv())
            print("📩 RESPUESTA COMPRA:", buy)

            if "error" in buy:
                print("❌ Error compra:", buy)
                return None

            contract_id = buy["buy"]["contract_id"]

            # 3. esperar resultado
            time.sleep(6)

            self.ws.send(json.dumps({
                "proposal_open_contract": 1,
                "contract_id": contract_id
            }))

            result = json.loads(self.ws.recv())

            if "error" in result:
                print("❌ Error resultado:", result)
                return None

            profit = result["proposal_open_contract"]["profit"]

            return profit

        except Exception as e:
            print("❌ Error operación:", e)
            return None
