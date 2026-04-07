import websocket
import json
import os
import time

class DerivBot:

    def __init__(self):
        self.token = os.getenv("DERIV_TOKEN")
        self.ws = None

    def conectar(self):
        try:
            time.sleep(0.5)
            self.ws = websocket.create_connection(
                "wss://ws.derivws.com/websockets/v3?app_id=1089",
                timeout=30
            )
            self.ws.send(json.dumps({"authorize": self.token}))
            response = json.loads(self.ws.recv())
            if "error" in response:
                print("❌ ERROR AUTORIZACIÓN:", response['error']['message'])
                return False
            print("✅ Conectado y Autorizado OK")
            return True
        except Exception as e:
            print("❌ ERROR CONEXIÓN:", str(e))
            return False

    def cerrar(self):
        try:
            if self.ws:
                self.ws.close()
        except:
            pass

    def get_candles(self, symbol):
        try:
            self.ws.send(json.dumps({
                "ticks_history": symbol,
                "adjust_start_time": 1,
                "count": 50,
                "end": "latest",
                "granularity": 60,
                "style": "candles"
            }))
            response = json.loads(self.ws.recv())
            return response.get("candles", [])
        except Exception as e:
            print("❌ ERROR VELAS:", str(e))
            return []

    # ==================================
    # ✅ MÉTODO NUEVO: PROPOSAL + BUY
    # ==================================
    def comprar(self, par, tipo, monto=1):
        try:
            accion = "CALL" if tipo.lower() == "call" else "PUT"
            print(f"📤 ENVIANDO ORDEN: {par} | {accion} | ${monto}")

            # PASO 1: PEDIR PROPUESTA (COTIZACIÓN)
            propuesta = {
                "proposal": 1,
                "amount": monto,
                "basis": "stake",
                "contract_type": accion,
                "currency": "USD",
                "duration": 1,
                "duration_unit": "m",
                "symbol": par
            }

            self.ws.send(json.dumps(propuesta))
            res_prop = json.loads(self.ws.recv())

            if "error" in res_prop:
                print(f"💥 ERROR PROPUESTA: {res_prop['error']['message']}")
                return None

            if "proposal" not in res_prop:
                print("⚠️ No llegó proposal")
                return None

            proposal_id = res_prop["proposal"].get("id")
            if not proposal_id:
                print("⚠️ No vino ID")
                return None

            # PASO 2: COMPRAR USANDO EL ID
            orden = {
                "buy": proposal_id,
                "price": monto
            }

            self.ws.send(json.dumps(orden))
            result = json.loads(self.ws.recv())

            print(f"📥 RESPUESTA FINAL: {json.dumps(result, indent=2)}")

            if "error" in result:
                print(f"💥 ERROR COMPRA: {result['error']['message']}")
                return None

            if "buy" in result and "contract_id" in result["buy"]:
                contract_id = result["buy"]["contract_id"]
                print(f"✅ ORDEN EXITOSA! ID: {contract_id}")
                return contract_id
            else:
                print("⚠️ Respuesta sin contract_id")
                return None

        except Exception as e:
            print(f"💥 ERROR EN FUNCIÓN COMPRAR: {str(e)}")
            return None

    def check_result(self, contract_id):
        try:
            self.ws.send(json.dumps({
                "proposal_open_contract": 1,
                "contract_id": contract_id
            }))
            while True:
                result = json.loads(self.ws.recv())
                if "proposal_open_contract" in result:
                    contract = result["proposal_open_contract"]
                    if contract.get("is_sold", False):
                        profit = float(contract.get("profit", 0))
                        print(f"🏁 RESULTADO: Profit = {profit}")
                        return profit
        except Exception as e:
            print("❌ ERROR ESPERANDO RESULTADO:", str(e))
            return 0
