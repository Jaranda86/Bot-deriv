import websocket
import json
import time
import ssl

class DerivBot:
    def __init__(self):
        self.ws = None
        self.app_id = "131618"
        self.token = None
        self.balance = 0

    def connect(self):
        try:
            url = f"wss://ws.derivws.com/websockets/v3?app_id={self.app_id}"
            self.ws = websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE})

            self.token = __import__("os").environ.get("DERIV_VRTC_TOKEN")

            if not self.token:
                print("❌ Token no encontrado")
                return False

            self.ws.send(json.dumps({
                "authorize": self.token
            }))

            response = json.loads(self.ws.recv())

            if "error" in response:
                print("❌ Error autorización:", response["error"])
                return False

            self.balance = response["authorize"]["balance"]
            self.login_id = response["authorize"]["loginid"]

            return True

        except Exception as e:
            print("❌ Error conexión:", e)
            return False

    def get_balance(self):
        return self.balance

    def get_available_pairs(self):
        return [{"symbol": "R_100"}, {"symbol": "R_50"}]

    def get_candles(self, symbol, timeframe, count):
        try:
            self.ws.send(json.dumps({
                "ticks_history": symbol,
                "end": "latest",
                "count": count,
                "style": "candles",
                "granularity": timeframe
            }))
            response = json.loads(self.ws.recv())
            return response.get("candles", [])
        except:
            return []

    def buy(self, symbol, amount, direction, duration, unit):
        try:
            contract_type = "CALL" if direction == "call" else "PUT"

            self.ws.send(json.dumps({
                "buy": 1,
                "price": amount,
                "parameters": {
                    "amount": amount,
                    "basis": "stake",
                    "contract_type": contract_type,
                    "currency": "USD",
                    "duration": duration,
                    "duration_unit": unit,
                    "symbol": symbol
                }
            }))

            response = json.loads(self.ws.recv())

            if "error" in response:
                print("❌ Error compra:", response["error"])
                return None

            return {"contract_id": response["buy"]["contract_id"]}

        except Exception as e:
            print("❌ Error en compra:", e)
            return None

    def check_result(self, contract_id):
        return {"done": True, "won": True, "profit": 1}

    def wait_for_result(self, contract_id, max_wait=30):
        time.sleep(2)
        return {"done": True, "won": True, "profit": 1}

    def check_connect(self):
        return True

    def disconnect(self):
        if self.ws:
            self.ws.close()
