import json
import time
import websocket
import os

class DerivBot:
    def __init__(self):
        # TOKEN DE TU CUENTA DERIV (ASEGÚRATE DE QUE ESTÉ EN LAS VARIABLES DE ENTORNO)
        self.TOKEN = os.getenv("DERIV_TOKEN")
        self.ws = None
        self.connected = False

    def conectar(self):
        """Establece conexión con el servidor de Deriv"""
        try:
            if not self.TOKEN:
                print("❌ FALTA EL TOKEN DE DERIV")
                return False

            print("🔌 Conectando a wss://ws.derivws.com/websockets/v3")
            self.ws = websocket.WebSocketApp(
                "wss://ws.derivws.com/websockets/v3",
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )

            # Ejecutar en un hilo para no bloquear
            import threading
            self.thread = threading.Thread(target=self.ws.run_forever)
            self.thread.daemon = True
            self.thread.start()

            # Esperar hasta 10 segundos a que se conecte
            tiempo_espera = 10
            for _ in range(tiempo_espera):
                if self.connected:
                    break
                time.sleep(1)

            if not self.connected:
                print("❌ No se pudo establecer conexión después de 10 segundos")
                return False

            print("✅ Conexión establecida y autorizada")
            return True

        except Exception as e:
            print(f"❌ Error al conectar: {e}")
            return False

    def _on_open(self, ws):
        """Se ejecuta al abrir la conexión"""
        print("🔓 Conexión abierta, enviando autorización...")
        ws.send(json.dumps({"authorize": self.TOKEN}))

    def _on_message(self, ws, mensaje):
        """Procesa los mensajes recibidos"""
        datos = json.loads(mensaje)
        
        if "authorize" in datos:
            if datos["authorize"]:
                print("✅ Autorización exitosa")
                self.connected = True
            else:
                print(f"❌ Error de autorización: {datos.get('message', 'Unknown')}")
                self.connected = False

    def _on_error(self, ws, error):
        print(f"❌ Error en la conexión: {error}")
        self.connected = False

    def _on_close(self, ws, close_code, close_reason):
        print(f"🔌 Conexión cerrada | Código: {close_code} | Razón: {close_reason}")
        self.connected = False

    def get_candles(self, activo, cantidad=50, intervalo=60):
        """Obtiene velas del activo especificado"""
        try:
            if not self.connected:
                print("⚠️ No hay conexión para pedir velas")
                return []

            print(f"📥 Solicitando {cantidad} velas de {activo}...")
            solicitud = {
                "ticks_history": activo,
                "count": cantidad,
                "end": "latest",
                "style": "candles",
                "granularity": intervalo
            }

            # Enviar solicitud
            self.ws.send(json.dumps(solicitud))

            # Esperar respuesta
            tiempo_maximo = 5
            inicio = time.time()
            while time.time() - inicio < tiempo_maximo:
                # Capturar el mensaje (se hace mediante una variable temporal)
                respuesta = None
                def guardar_respuesta(ws, msg):
                    nonlocal respuesta
                    datos = json.loads(msg)
                    if "candles" in datos:
                        respuesta = datos["candles"]

                # Asignar función temporal
                funcion_original = self._on_message
                self._on_message = guardar_respuesta

                time.sleep(0.2)

                # Restaurar función original
                self._on_message = funcion_original

                if respuesta is not None:
                    print(f"✅ Recibidas {len(respuesta)} velas de {activo}")
                    return respuesta

            print(f"⚠️ No se recibieron velas de {activo} después de {tiempo_maximo}s")
            return []

        except Exception as e:
            print(f"❌ Error al obtener velas: {e}")
            return []

    def comprar(self, activo, tipo, monto):
        """Realiza una compra en Deriv"""
        try:
            if not self.connected:
                print("⚠️ No hay conexión para realizar compra")
                return None

            print(f"💸 Comprando {tipo.upper()} en {activo} por {monto} USD...")
            solicitud = {
                "buy": 1,
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

            self.ws.send(json.dumps(solicitud))

            # Esperar respuesta
            tiempo_maximo = 10
            inicio = time.time()
            contract_id = None

            def capturar_compra(ws, msg):
                nonlocal contract_id
                datos = json.loads(msg)
                if "buy" in datos:
                    contract_id = datos["buy"]["contract_id"]
                    print(f"✅ Compra realizada | ID: {contract_id}")

            funcion_original = self._on_message
            self._on_message = capturar_compra

            while time.time() - inicio < tiempo_maximo and contract_id is None:
                time.sleep(0.2)

            self._on_message = funcion_original

            if contract_id:
                return contract_id
            else:
                print("❌ No se pudo realizar la compra")
                return None

        except Exception as e:
            print(f"❌ Error al comprar: {e}")
            return None

    def check_result(self, contract_id):
        """Verifica el resultado de una operación"""
        try:
            if not self.connected:
                print("⚠️ No hay conexión para verificar resultado")
                return 0.0

            print(f"🔍 Verificando resultado de contrato {contract_id}...")
            solicitud = {
                "proposal_open_contract": 1,
                "contract_id": contract_id
            }

            resultado = None
            tiempo_maximo = 60
            inicio = time.time()

            def capturar_resultado(ws, msg):
                nonlocal resultado
                datos = json.loads(msg)
                if "proposal_open_contract" in datos:
                    contrato = datos["proposal_open_contract"]
                    if contrato["is_sold"]:
                        resultado = round(float(contrato["profit"]), 2)
                        print(f"🏁 Operación finalizada | Ganancia/Pérdida: {resultado} USD")

            funcion_original = self._on_message
            self._on_message = capturar_resultado

            while time.time() - inicio < tiempo_maximo and resultado is None:
                time.sleep(0.5)

            self._on_message = funcion_original

            if resultado is not None:
                return resultado
            else:
                print("⚠️ No se pudo obtener el resultado a tiempo")
                return 0.0

        except Exception as e:
            print(f"❌ Error al verificar resultado: {e}")
            return 0.0

    def cerrar(self):
        """Cierra la conexión"""
        try:
            if self.ws:
                self.ws.close()
            self.connected = False
            print("🔌 Conexión cerrada correctamente")
        except Exception as e:
            print(f"⚠️ Error al cerrar conexión: {e}")
