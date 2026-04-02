import time
from deriv_api import DerivBot
from indicadores import analizar_indicadores, decision_final

# ================= CONFIG =================
PARES = ["R_100", "R_50", "R_75"]
TIEMPO_ESPERA = 10  # segundos entre ciclos
MAX_PERDIDAS_CONSEC = 3
TIEMPO_PAUSA = 60  # segundos en modo defensa

# ================= VARIABLES =================
perdidas_consecutivas = 0
modo_defensa = False
tiempo_reanudacion = 0

# ================= FUNCION ANALISIS =================
def analizar_par(bot, par):
    global perdidas_consecutivas, modo_defensa, tiempo_reanudacion

    try:
        print(f"\n🔍 Analizando {par}...")

        # Obtener datos del mercado
        velas = bot.obtener_velas(par)

        if velas is None:
            print(f"⚠️ No hay datos de {par}")
            return

        # Analizar indicadores
        decision, puntuacion, detalles = analizar_indicadores(velas)

        print(f"📊 {par} | puntuación: {puntuacion}")

        if decision is None:
            print("❌ Sin señal clara")
            return

        # Confirmar decisión final
        decision, puntuacion = decision_final(puntuacion)

        if decision is None:
            print("⛔ Señal filtrada")
            return

        print(f"🚀 Señal: {decision.upper()} en {par}")

        # Enviar a Telegram
        bot.enviar_telegram(f"📈 {par} → {decision.upper()} | Score: {puntuacion}")

        # Ejecutar operación
        resultado = bot.operar(par, decision)

        if resultado:
            print("✅ GANADA")
            perdidas_consecutivas = 0
        else:
            print("❌ PERDIDA")
            perdidas_consecutivas += 1

        # Activar modo defensa
        if perdidas_consecutivas >= MAX_PERDIDAS_CONSEC:
            modo_defensa = True
            tiempo_reanudacion = time.time() + TIEMPO_PAUSA
            print("🛑 MODO DEFENSA ACTIVADO")

    except Exception as e:
        print(f"⚠️ Error en {par}: {e}")


# ================= BOT PRINCIPAL =================
def bot():
    global modo_defensa, tiempo_reanudacion

    bot = DerivBot()

    if not bot.connect():
        print("❌ Error conexión con Deriv")
        return

    print("🏦 BOT HEDGE FUND INICIADO 🚀")

    while True:
        try:
            # Modo defensa activo
            if modo_defensa:
                if time.time() < tiempo_reanudacion:
                    print("🛑 En pausa por seguridad...")
                    time.sleep(10)
                    continue
                else:
                    print("✅ Reanudando operaciones")
                    modo_defensa = False

            # Analizar todos los pares
            for par in PARES:
                analizar_par(bot, par)
                time.sleep(2)

            # Espera entre ciclos
            time.sleep(TIEMPO_ESPERA)

        except Exception as e:
            print(f"⚠️ Error general: {e}")
            time.sleep(5)


# ================= INICIO =================
if __name__ == "__main__":
    bot()
