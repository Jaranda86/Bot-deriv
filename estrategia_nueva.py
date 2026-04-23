# ==============================================
# ESTRATEGIA NUEVA - SIN PANDA, SOLO PYTHON PURO
# ==============================================

class EstrategiaAvanzada:
    def __init__(self):
        pass

    def calcular_rsi(self, precios, periodo=14):
        """Calcula el RSI manualmente"""
        if len(precios) < periodo + 1:
            return 50  # Valor neutral si no hay datos

        deltas = []
        for i in range(1, len(precios)):
            deltas.append(precios[i] - precios[i-1])

        gains = []
        losses = []
        for delta in deltas[-periodo:]:
            if delta > 0:
                gains.append(delta)
                losses.append(0)
            elif delta < 0:
                gains.append(0)
                losses.append(-delta)
            else:
                gains.append(0)
                losses.append(0)

        avg_gain = sum(gains) / periodo
        avg_loss = sum(losses) / periodo

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calcular_media(self, precios, periodo):
        """Calcula Media Móvil Simple"""
        if len(precios) < periodo:
            return precios[-1] if precios else 0
        return sum(precios[-periodo:]) / periodo

    def calcular_senal(self, velas):
        """
        Recibe lista de velas: [{'close':..., 'high':..., 'low':...}, ...]
        Retorna: señal ('call'/'put'), confianza, info
        """
        
        # Extraer precios de cierre
        try:
            precios = [float(v['close']) for v in velas]
        except Exception as e:
            print(f"Error leyendo velas: {e}")
            return None, 0, "Error datos"

        if len(precios) < 30:
            return None, 0, "Pocos datos"

        # --- CALCULOS TECNICOS ---
        rsi = self.calcular_rsi(precios, 14)
        ma9 = self.calcular_media(precios, 9)
        ma21 = self.calcular_media(precios, 21)
        precio_actual = precios[-1]

        señal = None
        confianza = 0

        # 🟢 CONDICIONES PARA COMPRA (CALL)
        # Precio arriba de la media rapida + RSI bajo + Tendencia alcista
        if precio_actual > ma9 and rsi < 40 and ma9 > ma21:
            señal = "call"
            confianza = 85 + (40 - rsi)
            if confianza > 98: confianza = 98

        # 🔴 CONDICIONES PARA VENTA (PUT)
        # Precio abajo de la media rapida + RSI alto + Tendencia bajista
        elif precio_actual < ma9 and rsi > 60 and ma9 < ma21:
            señal = "put"
            confianza = 85 + (rsi - 60)
            if confianza > 98: confianza = 98

        info = f"RSI:{rsi:.1f} | MA9:{ma9:.4f} | MA21:{ma21:.4f}"
        return señal, round(confianza, 1), info
