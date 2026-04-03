import websocket
import json
import time
import os

class DerivBot:
    def __init__(self):
        self.ws = None
        self.token = os.getenv("DERIV_TOKEN")

    # ==============================
    # 🔌 CONECTAR
    # ==============================
    def connect(self):
        try:
            if not self.token:
                print("❌ Token no encontrado")
                return False

            self.ws = websocket.create_connection("wss://ws.derivws.com/websockets/v3?app_id=1089")

            # autorizar
            auth_data = {
                "authorize": self.token
            }

            self.ws.send(json.dumps(auth_data))
            response = json.loads(self.ws.recv())

            if "error" in response:
                print("❌ Error autorización:", response["error"])
                return False

            print("✅ Conectado a Deriv DEMO")
            return True

        except Exception as e:
            print("❌ Error conexión:", e)
            return False

    # ==============================
    # 📊 COMPRAR
    # ==============================
    def comprar(self, par, direccion, monto):

        try:
            contract_type = "CALL" if direccion == "call" else "PUT"

            proposal = {
                "proposal": 1,
                "amount": monto,
                "basis": "stake",
                "contract_type": contract_type,
                "currency": "USD",
                "duration": 1,
                "duration_unit": "m",
                "symbol": par
            }

            self.ws.send(json.dumps(proposal))
            proposal_response = json.loads(self.ws.recv())

            if "error" in proposal_response:
                print("❌ Error proposal:", proposal_response["error"])
                return None

            proposal_id = proposal_response["proposal"]["id"]

            buy = {
                "buy": proposal_id,
                "price": monto
            }

            self.ws.send(json.dumps(buy))
            buy_response = json.loads(self.ws.recv())

            if "error" in buy_response:
                print("❌ Error compra:", buy_response["error"])
                return None

            contract_id = buy_response["buy"]["contract_id"]

            print(f"📈 Trade ejecutado ({direccion.upper()} en {par})")

            # ==============================
            # ⏳ ESPERAR RESULTADO
            # ==============================

            while True:
                proposal_open = {
                    "proposal_open_contract": 1,
                    "contract_id": contract_id
                }

                self.ws.send(json.dumps(proposal_open))
                result = json.loads(self.ws.recv())

                if "proposal_open_contract" in result:
                    poc = result["proposal_open_contract"]

                    if poc["is_sold"]:
                        profit = poc["profit"]

                        if profit > 0:
                            return "win"
                        else:
                            return "loss"

                time.sleep(2)

        except Exception as e:
            print("❌ Error en compra:", e)
            return None
