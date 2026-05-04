import json
import time
import websocket
import os
import threading

class DerivBot:
    def __init__(self):
        self.TOKEN = os.getenv("DERIV_TOKEN")

        # ✅ APP ID (CRÍTICO)
        self.APP_ID = os.getenv("DERIV_APP_ID", "1089")

        self.ws = None
        self.connected = False
        self.last_response = None
        self.lock = threading.Lock()

    # =========================
    # 🔌 CONEXIÓN
    # =========================
    def conectar(self):
        try:
            if not self.TOKEN:
                print("❌ FALTA EL TOKEN DE DERIV")
                return False

            url = f"wss://ws.derivws.com/websockets/v3?app_id={self.APP_ID}"
            print(f"🔌 Conectando a {url}")

            self.ws = websocket.WebSocketApp(
                url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )

            self.thread = threading.Thread(target=self.ws.run_forever)
            self.thread.daemon = True
            self.thread.start()

            # Espera conexión
            for _ in range(10):
                if self.connected:
                    break
                time.sleep(1)

            if not self.connected:
                print("❌ No se pudo conectar en 10 segundos")
                return False

            print("✅ Conectado y autorizado")
            return True

        except Exception as e:
            print(f"❌ Error al conectar: {e}")
            return False

    def _on_open(self, ws):
        print("🔓 Conexión abierta → Autorizando...")
        ws.send(json.dumps({
            "authorize": self.TOKEN
        }))

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)

            # Guardar última respuesta
            with self.lock:
                self.last_response = data

            # Autorización
            if "authorize" in data:
                print("✅ Autorización exitosa")
                self.connected = True

            # Error global
            if "error" in data:
                print(f"❌ ERROR DERIV: {data['error']}")
                self.connected = False

        except Exception as e:
            print(f"⚠️ Error procesando mensaje: {e}")

    def _on_error(self, ws, error):
        print(f"❌ Error conexión: {error}")
        self.connected = False

    def _on_close(self, ws, code, msg):
        print(f"🔌 Conexión cerrada | {code} | {msg}")
        self.connected = False

    # =========================
    # 📊 VELAS (ARREGLADO)
    # =========================
    def get_candles(self, activo, cantidad=50, intervalo=60):
        try:
            if not self.connected:
                return []

            request = {
                "ticks_history": activo,
                "count": cantidad,
                "end": "latest",
                "style": "candles",
                "granularity": intervalo
            }

            self.ws.send(json.dumps(request))

            for _ in range(20):
                time.sleep(0.3)
                with self.lock:
                    data = self.last_response

                if data and "candles" in data:
                    return data["candles"]

            print("⚠️ No llegaron velas")
            return []

        except Exception as e:
            print(f"❌ Error velas: {e}")
            return []

    # =========================
    # 💸 COMPRA (MEJORADO)
    # =========================
    def comprar(self, activo, tipo, monto):
        try:
            if not self.connected:
                return None

            request = {
                "buy": 1,
                "price": monto,
                "parameters": {
                    "amount": monto,
                    "basis": "stake",
                    "contract_type": tipo.upper(),
                    "currency": "USD",
                    "symbol": activo,
                    "duration": 1,
                    "duration_unit": "m"
                }
            }

            self.ws.send(json.dumps(request))

            for _ in range(30):
                time.sleep(0.3)
                with self.lock:
                    data = self.last_response

                if data and "buy" in data:
                    contract_id = data["buy"]["contract_id"]
                    print(f"✅ Compra OK | ID: {contract_id}")
                    return contract_id

            print("❌ Compra no confirmada")
            return None

        except Exception as e:
            print(f"❌ Error compra: {e}")
            return None

    # =========================
    # 📈 RESULTADO (MEJORADO)
    # =========================
    def check_result(self, contract_id):
        try:
            if not self.connected:
                return 0.0

            request = {
                "proposal_open_contract": 1,
                "contract_id": contract_id,
                "subscribe": 1
            }

            self.ws.send(json.dumps(request))

            for _ in range(120):
                time.sleep(0.5)
                with self.lock:
                    data = self.last_response

                if data and "proposal_open_contract" in data:
                    contract = data["proposal_open_contract"]

                    if contract.get("is_sold"):
                        profit = float(contract.get("profit", 0))
                        print(f"🏁 Resultado: {profit}")
                        return round(profit, 2)

            print("⚠️ No llegó resultado")
            return 0.0

        except Exception as e:
            print(f"❌ Error resultado: {e}")
            return 0.0

    # =========================
    # 🔌 CERRAR
    # =========================
    def cerrar(self):
        try:
            if self.ws:
                self.ws.close()
            self.connected = False
            print("🔌 Cerrado correctamente")
        except Exception as e:
            print(f"⚠️ Error al cerrar: {e}")
