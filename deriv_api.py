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
        print("🔌 Conectando a Deriv...")

        url = "wss://ws.derivws.com/websockets/v3?app_id=1089"

        self.ws = websocket.WebSocket()
        self.ws.connect(url)

        # Autorizar
        self.ws.send(json.dumps({
            "authorize": self.token
        }))

        response = json.loads(self.ws.recv())

        if "error" in response:
            print("❌ Error autorización:", response)
            return False

        self.balance = response["authorize"]["balance"]

        print(f"✅ Conectado a Deriv | Balance: {self.balance}")
        return True

    except Exception as e:
        print("❌ Error conexión:", e)
        return False

    # =========================
    # 💰 BALANCE
    # =========================
    def get_balance(self):
        try:
            self.ws.send(json.dumps({
                "balance": 1
            }))

            response = json.loads(self.ws.recv())

            if "balance" in response:
                self.balance = response["balance"]["balance"]

            return self.balance

        except:
            return self.balance

    # =========================
    # 📊 VELAS REALES (CLAVE)
    # =========================
    def get_candles(self, symbol, count=50, timeframe=60):
        try:
            self.ws.send(json.dumps({
                "ticks_history": symbol,
                "adjust_start_time": 1,
                "count": count,
                "end": "latest",
                "granularity": timeframe,
                "style": "candles"
            }))

            response = json.loads(self.ws.recv())

            if "error" in response:
                print("❌ Error velas:", response)
                return None

            return response.get("candles", [])

        except Exception as e:
            print("❌ Error get_candles:", e)
            return None

    # =========================
    # 💸 COMPRA
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
            print("📦 COMPRA:", result)

            if "error" in result:
                return "error"

            contract_id = result["buy"]["contract_id"]

            # esperar resultado
            time.sleep(65)

            self.ws.send(json.dumps({
                "proposal_open_contract": 1,
                "contract_id": contract_id
            }))

            result2 = json.loads(self.ws.recv())

            if "proposal_open_contract" in result2:
                profit = result2["proposal_open_contract"]["profit"]

                if profit > 0:
                    self.balance += profit
                    return "win"
                else:
                    self.balance += profit
                    return "loss"

            return "error"

        except Exception as e:
            print("❌ Error operación:", e)
            return "error"
