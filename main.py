import time
import datetime

from deriv_api import DerivAPI
from estrategia import señal_con_ia
from telegram_utils import enviar
from ia_model import IA
import config

def dentro_horario():
    h = datetime.datetime.now().hour
    return config.HORA_INICIO <= h < config.HORA_FIN

def run():
    enviar("🤖 BOT IA PRO INICIADO")

    api = None
    ia = IA()
    total = 0

    while True:
        if not dentro_horario():
            time.sleep(60)
            continue

        if not api:
            api = DerivAPI(config.DERIV_TOKEN, config.APP_ID)
            if not api.conectar():
                enviar("❌ Error conexión")
                time.sleep(30)
                api = None
                continue
            enviar("✅ Conectado")

        for par in config.PARES:
            velas = api.get_velas(par)

            if len(velas) < 30:
                continue

            s, conf = señal_con_ia(velas, ia)

            print(f"{par} → {s} {conf}")

            if s and conf >= config.CONF_MIN:
                enviar(f"🚀 {par} {s} {round(conf,2)}%")

                cid = api.comprar(par, s, config.MONTO)

                if cid:
                    profit = api.resultado(cid)
                    total += profit

                    if profit > 0:
                        enviar(f"✅ +{profit}")
                    else:
                        enviar(f"❌ {profit}")

                    ia.aprender(
                        [float(v["close"]) for v in velas],
                        profit
                    )

                    if total <= config.STOP_LOSS:
                        enviar("🛑 STOP LOSS")
                        return

                    if total >= config.TAKE_PROFIT:
                        enviar("🎯 TAKE PROFIT")
                        return

        time.sleep(60)

if __name__ == "__main__":
    run()
