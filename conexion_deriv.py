import asyncio
import os
from deriv_api import DerivAPI

class DerivBot:

    def __init__(self):
        self.token = os.getenv("DERIV_TOKEN")
        self.app_id = 1089
        self.api = None

    async def conectar(self):
        try:
            self.api = DerivAPI()
            await self.api.connect({"app_id": self.app_id})
            auth = await self.api.authorize({"token": self.token})
            
            if "error" in auth:
                print("❌ ERROR AUTORIZACIÓN:", auth['error']['message'])
                return False
                
            print("✅ Conectado y Autorizado OK (Librería Oficial)")
            return True
        except Exception as e:
            print("❌ ERROR CONEXIÓN:", str(e))
            return False

    def cerrar(self):
        try:
            if self.api:
                asyncio.create_task(self.api.disconnect())
        except:
            pass

    async def get_candles(self, symbol):
        try:
            response = await self.api.ticks_history({
                "ticks_history": symbol,
                "adjust_start_time": 1,
                "count": 50,
                "end": "latest",
                "granularity": 60,
                "style": "candles"
            })
            return response.get("candles", [])
        except Exception as e:
            print("❌ ERROR VELAS:", str(e))
            return []

    # ==================================
    # ✅ COMPRAR USANDO LA LIBRERÍA
    # ==================================
    async def comprar(self, par, tipo, monto=1):
        try:
            accion = "CALL" if tipo.lower() == "call" else "PUT"
            print(f"📤 ENVIANDO ORDEN: {par} | {accion} | ${monto}")

            # PASO 1: PROPUESTA
            prop = await self.api.proposal({
                "proposal": 1,
                "amount": monto,
                "basis": "stake",
                "contract_type": accion,
                "currency": "USD",
                "duration": 1,
                "duration_unit": "m",
                "symbol": par
            })

            if "error" in prop:
                print(f"💥 ERROR PROPUESTA: {prop['error']['message']}")
                return None

            if "proposal" not in prop:
                print("⚠️ No hay proposal")
                return None

            proposal_id = prop["proposal"].get("id")
            
            # PASO 2: COMPRA
            orden = await self.api.buy({
                "buy": proposal_id,
                "price": monto
            })

            print(f"📥 RESPUESTA COMPRA: {orden}")

            if "error" in orden:
                print(f"💥 ERROR COMPRA: {orden['error']['message']}")
                return None

            if "buy" in orden and "contract_id" in orden["buy"]:
                contract_id = orden["buy"]["contract_id"]
                print(f"✅ ORDEN EXITOSA! ID: {contract_id}")
                return contract_id
            else:
                print("⚠️ Sin contract_id")
                return None

        except Exception as e:
            print(f"💥 ERROR EN FUNCIÓN COMPRAR: {str(e)}")
            return None

    async def check_result(self, contract_id):
        try:
            while True:
                result = await self.api.proposal_open_contract({
                    "proposal_open_contract": 1,
                    "contract_id": contract_id
                })

                if "proposal_open_contract" in result:
                    contract = result["proposal_open_contract"]
                    if contract.get("is_sold", False):
                        profit = float(contract.get("profit", 0))
                        print(f"🏁 RESULTADO: Profit = {profit}")
                        return profit
                await asyncio.sleep(1)
        except Exception as e:
            print("❌ ERROR ESPERANDO RESULTADO:", str(e))
            return 0
