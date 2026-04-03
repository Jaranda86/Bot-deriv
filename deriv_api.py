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
            if not self.token:
                print("❌ Token no encontrado")
                return False

            self.ws = websocket.create_connection(
                "wss://ws.derivws.com/websockets/v3?app_id=1089"
            )

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

    def operar(self, symbol, action):
        try:
            print(f"🚀 Ejecutando {action.upper()} en {symbol}")

            # Enviar orden
            self.ws.send(json.dumps({
                "buy": 1,
                "price": 1,
                "parameters": {
                    "amount": 1,  # monto en USD (demo)
                    "basis": "stake",
                    "contract_type": "CALL" if action == "call" else "PUT",
                    "currency": "USD",
                    "duration": 1,
                    "duration_unit": "m",
                    "symbol": symbol
                }
            }))

            response = json.loads(self.ws.recv())

            if "error" in response:
                print("❌ Error operación:", response)
                return False

            contract_id = response["buy"]["contract_id"]
            print(f"📄 Contract ID: {contract_id}")

            # Esperar resultado (1 minuto + margen)
            time.sleep(65)

            # Consultar resultado real
            self.ws.send(json.dumps({
                "proposal_open_contract": 1,
                "contract_id": contract_id
            }))

            result = json.loads(self.ws.recv())

            contract = result.get("proposal_open_contract", {})

            profit = contract.get("profit", 0)
            status = contract.get("status", "")

            print(f"📊 Resultado: {status} | Profit: {profit}")

            if profit > 0:
                return True
            else:
                return False

        except Exception as e:
            print("❌ Error operar:", e)
            return False
