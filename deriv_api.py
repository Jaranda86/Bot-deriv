import websocket
import json
import threading
import time

class DerivAPI:
    def __init__(self, token, app_id):
        self.token = token
        self.app_id = app_id
        self.ws = None
        self.connected = False
        self.last = None
        self.lock = threading.Lock()

    def conectar(self):
        url = f"wss://ws.derivws.com/websockets/v3?app_id={self.app_id}"

        self.ws = websocket.WebSocketApp(
            url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_close=self.on_close,
            on_error=self.on_error
        )

        t = threading.Thread(target=self.ws.run_forever)
        t.daemon = True
        t.start()

        for _ in range(10):
            if self.connected:
                return True
            time.sleep(1)

        return False

    def on_open(self, ws):
        ws.send(json.dumps({"authorize": self.token}))

    def on_message(self, ws, msg):
        data = json.loads(msg)
        with self.lock:
            self.last = data

        if "authorize" in data:
            self.connected = True

        if "error" in data:
            print("❌", data["error"])
            self.connected = False

    def on_close(self, ws, a, b):
        print("🔌 Conexión cerrada")
        self.connected = False

    def on_error(self, ws, e):
        print("❌ Error:", e)
        self.connected = False

    def get_velas(self, symbol, count=50):
        self.ws.send(json.dumps({
            "ticks_history": symbol,
            "count": count,
            "end": "latest",
            "style": "candles",
            "granularity": 60
        }))

        for _ in range(20):
            time.sleep(0.3)
            with self.lock:
                if self.last and "candles" in self.last:
                    return self.last["candles"]
        return []

    def comprar(self, symbol, tipo, monto):
        self.ws.send(json.dumps({
            "buy": 1,
            "price": monto,
            "parameters": {
                "amount": monto,
                "basis": "stake",
                "contract_type": tipo.upper(),
                "currency": "USD",
                "symbol": symbol,
                "duration": 1,
                "duration_unit": "m"
            }
        }))

        for _ in range(20):
            time.sleep(0.3)
            with self.lock:
                if self.last and "buy" in self.last:
                    return self.last["buy"]["contract_id"]
        return None

    def resultado(self, contract_id):
        self.ws.send(json.dumps({
            "proposal_open_contract": 1,
            "contract_id": contract_id,
            "subscribe": 1
        }))

        for _ in range(120):
            time.sleep(0.5)
            with self.lock:
                if self.last and "proposal_open_contract" in self.last:
                    c = self.last["proposal_open_contract"]
                    if c.get("is_sold"):
                        return float(c.get("profit", 0))
        return 0
