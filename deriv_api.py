import websocket
import json
import time
import os

class DerivBot:
    def __init__(self):
        self.token = os.getenv("DERIV_TOKEN")
        self.ws = None
        self.balance = 0

    # =========================
    # 🔌 CONEXIÓN
    # =========================
    def connect(self):
        try:
            self.ws = websocket.create_connection(
                "wss://ws.derivws.com/websockets/v3?app_id=1089"
            )

            self.ws.send(json.dumps({
                "authorize": self.token
            }))

            response = json.loads(self.ws.recv())

            if "error" in response:
                print("❌ Error autorización:", response)
                return False

            self.balance = response["authorize"]["balance"]
            print("✅ Conectado a Deriv")
            print("💰 Balance inicial:", self.balance)

            return True

        except Exception as e:
            print("❌ Error conexión:", e)
            return False

    # =========================
    # 💰 BALANCE
    # =========================
    def get_balance(self):
        try:
            self.ws.send(json.dumps({"balance": 1}))
            response = json.loads(self.ws.recv())

            self.balance = response["balance"]["balance"]
            return self.balance

        except:
            return self.balance

    # =========================
    # 📊 VELAS (CANDLES)
    # =========================
    def get_candles(self, symbol):
        try:
            self.ws.send(json.dumps({
                "ticks_history": symbol,
                "style": "candles",
                "granularity": 60,
                "count": 50
            }))

            data = json.loads(self.ws.recv())

            if "error" in data:
                print("❌ Error velas:", data)
                return []

            return data["candles"]

        except Exception as e:
            print("❌ Error get_candles:", e)
            return []

    # =========================
    # 🚀 OPERAR REAL
    # =========================
    def comprar(self, symbol, tipo, monto=1):
        try:
            contrato = "CALL" if tipo == "call" else "PUT"

            # 1️⃣ PEDIR PROPUESTA
            self.ws.send(json.dumps({
                "proposal": 1,
                "amount": monto,
                "basis": "stake",
                "contract_type": contrato,
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

            # 2️⃣ COMPRAR
            self.ws.send(json.dumps({
                "buy": proposal_id,
                "price": monto
            }))

            buy = json.loads(self.ws.recv())

            if "error" in buy:
                print("❌ Error compra:", buy)
                return None

            contract_id = buy["buy"]["contract_id"]
            print("📄 Contract ID:", contract_id)

            # 3️⃣ ESPERAR RESULTADO
            time.sleep(6)

            self.ws.send(json.dumps({
                "proposal_open_contract": 1,
                "contract_id": contract_id
            }))

            result = json.loads(self.ws.recv())

            if "error" in result:
                print("❌ Error resultado:", result)
                return None

            contract = result.get("proposal_open_contract", {})
            profit = contract.get("profit", 0)

            print(f"📊 Resultado: {profit}")

            # actualizar balance
            self.get_balance()

            if profit > 0:
                return "win"
            else:
                return "loss"

        except Exception as e:
            print("❌ Error operar:", e)
            return None
