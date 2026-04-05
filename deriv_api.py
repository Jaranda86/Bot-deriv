import websocket
import json
import os
import time


class DerivBot:
    def __init__(self):
        self.ws = None
        self.token = os.getenv("DERIV_TOKEN")
        self.app_id = "1089"  # oficial Deriv

    # =========================
    # 🔌 CONEXIÓN
    # =========================
    def conectar(self):
        try:
            print("🔌 Intentando conectar a Deriv...")
            print("TOKEN:", self.token)

            if not self.token:
                print("❌ TOKEN NO DEFINIDO")
                return False

            url = f"wss://ws.derivws.com/websockets/v3?app_id={self.app_id}"

            self.ws = websocket.create_connection(url)

            self.ws.send(json.dumps({
                "authorize": self.token
            }))

            response = json.loads(self.ws.recv())

            if "error" in response:
                print("❌ Error autorización:", response["error"])
                return False

            print("✅ Conectado a Deriv correctamente")
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
                "adjust_start_time": 1,
                "count": count,
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
    # 💰 COMPRAR OPERACIÓN
    # =========================
    def comprar(self, par, tipo, monto):
        try:
            accion = "CALL" if tipo == "call" else "PUT"

            print(f"💰 Enviando orden: {par} {accion} ${monto}")

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

            if "error" in result:
                print("❌ Error compra:", result["error"])
                return None

            contract_id = result["buy"]["contract_id"]
            print("✅ Compra realizada ID:", contract_id)

            return contract_id

        except Exception as e:
            print("❌ Error comprar:", e)
            return None

    # =========================
    # 📈 RESULTADO OPERACIÓN
    # =========================
    def check_result(self, contract_id):
        try:
            self.ws.send(json.dumps({
                "proposal_open_contract": 1,
                "contract_id": contract_id
            }))

            while True:
                response = json.loads(self.ws.recv())

                if "proposal_open_contract" in response:
                    contract = response["proposal_open_contract"]

                    if contract["is_sold"]:
                        profit = contract["profit"]
                        print(f"📊 Resultado contrato: {profit}")
                        return profit

                time.sleep(2)

        except Exception as e:
            print("❌ Error resultado:", e)
            return 0
