from enum import Enum

class Estrategia(Enum):
    R_10 = "R_10"
    R_25 = "R_25"
    R_50 = "R_50"
    NINGUNA = "PAUSAR"

class TipoActivo(Enum):
    TIPO_A = "LIQUIDEZ"   # Tendencia clara
    TIPO_B = "VOLATIL"    # Movimientos fuertes
    TIPO_C = "LENTO"      # Rango / Lento

def obtener_estrategia(hora_actual, tipo_activo):
    """
    LÓGICA ULTRA CAUTELOSA v2.0
    Basada en resultados del día 15/04
    """
    
    # ==============================================
    # 🚫 09:00 - 11:00 | ZONA LETAL
    # Resultado: Perdidas fuertes en todas las estrategias
    # ACCIÓN: NO OPERAR NADA
    # ==============================================
    if 9 <= hora_actual < 11:
        return [Estrategia.NINGUNA]

    # ==============================================
    # ✅ 11:00 - 14:00 | MEJOR HORARIO
    # Resultado: R_50 funcionó excelente, R_25 regular
    # ACCIÓN: Priorizar R_50, permitir R_25, PROHIBIR R_10
    # ==============================================
    elif 11 <= hora_actual < 14:
        if tipo_activo == TipoActivo.TIPO_B: # Activos volátiles
            return [Estrategia.R_50]
        else: # Activos normales
            return [Estrategia.R_25]

    # ==============================================
    # ⚠️ 14:00 - 17:00 | ZONA DE RIESGO
    # Resultado: R_10 y R_25 fallaron mucho
    # ACCIÓN: SOLO R_50 o PAUSAR
    # ==============================================
    elif 14 <= hora_actual < 17:
        if tipo_activo == TipoActivo.TIPO_B:
            return [Estrategia.R_50] # Único que resiste volatilidad
        else:
            return [Estrategia.NINGUNA] # Mejor no arriesgar

    # ==============================================
    # ❌ 17:00 EN ADELANTE | ZONA PROHIBIDA
    # Resultado: Desastre total con R_10 y R_25
    # ACCIÓN: CERRADO COMPLETO
    # ==============================================
    else: 
        return [Estrategia.NINGUNA]
