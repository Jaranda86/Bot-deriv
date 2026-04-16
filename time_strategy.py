from enum import Enum

class Estrategia(Enum):
    R_10 = "R_10"
    R_25 = "R_25"
    R_50 = "R_50"
    NINGUNA = "PAUSAR"

class TipoActivo(Enum):
    TIPO_A = "LIQUIDEZ"
    TIPO_B = "VOLATIL"
    TIPO_C = "LENTO"

def obtener_estrategia(hora_actual, tipo_activo):
    """
    MODO SUPERVIVENCIA EXTREMA v3.0
    """
    
    # ==============================================
    # 🚫 09:00 - 11:00 | CERRADO
    # ==============================================
    if 9 <= hora_actual < 11:
        return [Estrategia.NINGUNA]

    # ==============================================
    # ✅ 11:00 - 14:00 | ÚNICO HORARIO PERMITIDO
    # ==============================================
    elif 11 <= hora_actual < 14:
        # SOLO R_50, LOS DEMÁS PROHIBIDOS
        if tipo_activo == TipoActivo.TIPO_B: # R_50
            return [Estrategia.R_50]
        else:
            return [Estrategia.NINGUNA] # R_10 y R_25 APAGADOS

    # ==============================================
    # ❌ 14:00 EN ADELANTE | CERRADO COMPLETO
    # ==============================================
    else: 
        return [Estrategia.NINGUNA]
