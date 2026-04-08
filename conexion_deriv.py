import websocket
import json
import os
import time
import sys

class DerivBot:

    def __init__(self):
        self.token = os.getenv("DERIV_TOKEN")
        self.ws = None
        self.autorizado = False

    def conectar(self):
        try:
            if self.ws and self.autorizado:
                print("✅ Ya conectado y autorizado", file=sys.stderr)
                return True

            print("🔌 INTENTANDO CONECTAR...", file=sys.stderr)
            self.ws = websocket.create_connection(
                "wss://ws.derivws.com/websockets/v3?app_id=1089",
                timeout=20
            )
            
            print("📤 ENVIANDO TOKEN...", file=sys.stderr)
            self.ws.send(json.dumps({"authorize": self.token}))
            response = json.loads(self.ws.recv())
            
            print(f"📥 RESPUESTA AUTORIZACIÓN: {response}", file=sys.stderr)

            if "error" in response:
                print(f"❌ ERROR: {response['error']['message']}", file=sys.stderr)
                if "rate limit" in response['error']['message']:
                    print("⏳ ESPERANDO 60 SEG POR LÍMITE...", file=sys.stderr)
                    time.sleep(60)
                return False
                
            print("✅ CONECTADO Y AUTORIZADO!", file=sys.stderr)
            self.autorizado = True
            return True
            
        except Exception as e:
            print(f"💥 ERROR CONEXIÓN: {str(e)}", file=sys.stderr)
            self.autorizado = False
            # Esperar un poco antes de volver a intentar
            print("⏳ ESPERANDO 10 SEG...", file=sys.stderr)
            time.sleep(10)
            return False

    def cerrar(self):
        try:
            if self.ws:
                self.ws.close()
                self.autorizado = False
        except:
            pass

    def get_candles(self, symbol):
        try:
            print("📥 PIDIENDO VELAS...", file=sys.stderr)
            self.ws.send(json.dumps({
                "ticks_history": symbol,
                "adjust_start_time": 1,
                "count": 20,
                "end": "latest",
                "granularity": 60,
                "style": "candles"
            }))
            response = json.loads(self.ws.recv())
            return response.get("candles", [])
        except Exception as e:
            print(f"❌ ERROR VELAS: {str(e)}", file=sys.stderr)
            self.autorizado = False
            return []

    def comprar(self, par, tipo, monto=0.35):
        try:
            accion = "CALL" if tipo.lower() == "call" else "PUT"
            print(f"📤 ENVIANDO ORDEN: {par} | {accion} | ${monto}", file=sys.stderr)

            orden = {
                "buy": 1,
                "price": float(monto),
                "parameters": {
                    "amount": float(monto),
                    "basis": "stake",
                    "contract_type": accion,
                    "currency": "USD",
                    "duration": 1,
                    "duration_unit": "m",
                    "symbol": par
                }
            }

            self.ws.send(json.dumps(orden))
            result = json.loads(self.ws.recv())
            
            print("="*60, file=sys.stderr)
            print("📥 RESPUESTA DERIV COMPLETA:", file=sys.stderr)
            print(json.dumps(result, indent=2), file=sys.stderr)
            print("="*60, file=sys.stderr)

            if "error" in result:
                print(f"💥 ERROR DERIV: {result['error']['message']}", file=sys.stderr)
                if "rate limit" in result['error']['message']:
                    print("⏳ ESPERANDO 60 SEG...", file=sys.stderr)
                    time.sleep(60)
                return None
                
            if "buy" in result:
                return result["buy"].get("contract_id")
            else:
                print("⚠️ NO HAY CONTRACT_ID", file=sys.stderr)
                return None

        except Exception as e:
            print(f"💥 ERROR EN COMPRAR: {str(e)}", file=sys.stderr)
            self.autorizado = False
            return None

    def check_result(self, contract_id):
        try:
            print("⌛ ESPERANDO RESULTADO (MAX 70 SEG)...", file=sys.stderr)
            start_time = time.time()
            
            self.ws.send(json.dumps({
                "proposal_open_contract": 1,
                "contract_id": contract_id
            }))

            while True:
                if time.time() - start_time > 70:
                    print("⏰ TIMEOUT - CERRANDO CONEXIÓN", file=sys.stderr)
                    self.cerrar()
                    return 0

                try:
                    result = json.loads(self.ws.recv())
                    if "proposal_open_contract" in result:
                        contract = result["proposal_open_contract"]
                        if contract.get("is_sold", False):
                            profit = float(contract.get("profit", 0))
                            print(f"🏁 RESULTADO LISTO! Profit = {profit}", file=sys.stderr)
                            return profit
                except Exception as e:
                    print(f"🔄 RECONECTANDO... {str(e)}", file=sys.stderr)
                    self.autorizado = False
                    time.sleep(2)
                    
                time.sleep(2)

        except Exception as e:
            print(f"❌ ERROR RESULTADO: {str(e)}", file=sys.stderr)
            self.autorizado = False
            return 0
