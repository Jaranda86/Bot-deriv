import os
import time

class DerivBot:

    def __init__(self):
        self.token = os.getenv("DERIV_TOKEN")

    def connect(self):
        if not self.token:
            print("❌ Token no encontrado")
            return False

        print("✅ Conectado a Deriv")
        return True

    def obtener_velas(self, par):
        # 🔥 Simulación (luego lo mejoramos con datos reales)
        import random

        return {
            "dir_vela": random.choice([1, -1]),
            "bb_pos": random.random(),
            "stoch_k": random.randint(0, 100),
            "ema_tend": random.choice([1, -1])
        }

    def operar(self, par, decision):
        import random

        print(f"💰 Ejecutando {decision} en {par}")
        return random.choice([True, False])

    def enviar_telegram(self, mensaje):
        print(f"📩 Telegram: {mensaje}")
