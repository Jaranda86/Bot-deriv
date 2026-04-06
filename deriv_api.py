import websocket
import json
import os


class DerivBot:

    def __init__(self):
        self.token = os.getenv("DERIV_TOKEN")

    # =========================
    # CREAR NUEVA CONEXIÓN
    # =========================
    def nueva_conexion(self):
        try:
            ws = websocket.create_connection(
                "wss://ws.derivws.com/websockets/v3?app_id=1089"
            )

            ws.send(json.dumps({
                "authorize": self.token
            }))

            response = json.loads(ws.recv())

            if "error" in response:
                print("❌ Error autorización:", response)
                return None

            return ws

        except Exception as e:
            print("❌ Error conexión:", e)
            return None

    # =========================
    # VELAS
    # =========================
    def get_candles(self, symbol):
        ws = self.nueva_conexion()
        if not ws:
            return []

        try:
            ws.send(json.dumps({
                "ticks_history": symbol,
                "adjust_start_time": 1,
                "count": 50,
                "end": "latest",
                "granularity": 60,
                "style": "candles"
            }))

            response = json.loads(ws.recv())
            ws.close()

            if "candles" in response:
                return response["candles"]

        except Exception as e:
            print("❌ Error velas:", e)

        return []

    # =========================
    # COMPRAR
    # =========================
    def comprar(self, par, tipo, monto=1):
        ws = self.nueva_conexion()
        if not ws:
            return None

        try:
            accion = "CALL" if tipo == "call" else "PUT"

            ws.send(json.dumps({
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

            result = json.loads(ws.recv())
            ws.close()

            if "buy" in result:
                return result["buy"]["contract_id"]

        except Exception as e:
            print("❌ Error compra:", e)

        return None

    # =========================
    # RESULTADO
    # =========================
    def check_result(self, contract_id):
        ws = self.nueva_conexion()
        if not ws:
            return 0

        try:
            ws.send(json.dumps({
                "proposal_open_contract": 1,
                "contract_id": contract_id
            }))

            while True:
                result = json.loads(ws.recv())

                if "proposal_open_contract" in result:
                    contract = result["proposal_open_contract"]

                    if contract["is_sold"]:
                        ws.close()
                        return contract["profit"]

        except Exception as e:
            print("❌ Error resultado:", e)

        return 0
