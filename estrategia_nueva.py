import pandas as pd

class EstrategiaAvanzada:
    def __init__(self):
        pass

    def calcular_rsi(self, precios, periodo=14):
        """Calcula el RSI para ver sobrecompra/sobreventa"""
        deltas = [precios[i+1] - precios[i] for i in range(len(precios)-1)]
        gains = [x for x in deltas if x > 0]
        losses = [-x for x in deltas if x < 0]
        
        avg_gain = sum(gains[-periodo:]) / periodo if gains else 0
        avg_loss = sum(losses[-periodo:]) / periodo if losses else 1e-10
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calcular_media(self, precios, periodo):
        """Calcula Media Móvil Simple"""
        if len(precios) < periodo:
            return 0
        return sum(precios[-periodo:]) / periodo

    def calcular_senal(self, velas):
        """
        Recibe las velas y devuelve:
        - señal: 'call' o 'put' o None
        - confianza: 0 a 100
        - info: texto
        """
        
        # Extraemos precios de cierre
        try:
            precios = [float(v['close']) for v in velas]
        except:
            return None, 0, "Error datos"

        if len(precios) < 30:
            return None, 0, "Pocos datos"

        # --- CALCULOS TECNICOS ---
        rsi = self.calcular_rsi(precios, 14)
        ma9 = self.calcular_media(precios, 9)
        ma21 = self.calcular_media(precios, 21)
        precio_actual = precios[-1]

        # --- REGLAS DE ENTRADA ---
        señal = None
        confianza = 0

        # 🟢 CONDICIONES PARA COMPRA (CALL)
        # - Precio arriba de la media rapida
        # - RSI bajo (sobreventa)
        # - La media rapida cruza hacia arriba a la lenta
        if precio_actual > ma9 and rsi < 40 and ma9 > ma21:
            señal = "call"
            confianza = 85 + (50 - rsi) # Mas confianza si RSI muy bajo
            if confianza > 98: confianza = 98

        # 🔴 CONDICIONES PARA VENTA (PUT)
        elif precio_actual < ma9 and rsi > 60 and ma9 < ma21:
            señal = "put"
            confianza = 85 + (rsi - 50) # Mas confianza si RSI muy alto
            if confianza > 98: confianza = 98

        info = f"RSI:{rsi:.1f} | MA9:{ma9:.4f} | MA21:{ma21:.4f}"
        return señal, round(confianza, 1), info
