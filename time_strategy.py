from enum import Enum

class Estrategia(Enum):
    R_10 = "R_10"
    R_25 = "R_25"
    R_50 = "R_50"
    NINGUNA = "PAUSAR"

class TipoActivo(Enum):
    TIPO_A = "LIQUIDEZ"   # EUR/USD, Indices
    TIPO_B = "VOLATIL"    # Oro, Cripto
    TIPO_C = "LENTO"      # Acciones

def obtener_estrategia(hora_actual, tipo_activo):
    """
    Lógica principal basada en horarios y activos.
    Retorna qué estrategias deben estar ACTIVAS.
    """
    
    # ==============================================
    # ZONA 1: MAÑANA (11:00 - 13:00)
    # ==============================================
    if 11 <= hora_actual < 14:
        if tipo_activo in [TipoActivo.TIPO_A, TipoActivo.TIPO_C]:
            return [Estrategia.R_10, Estrategia.R_25]
        elif tipo_activo == TipoActivo.TIPO_B:
            return [Estrategia.R_50]

    # ==============================================
    # ZONA 2: TARDE TEMPRANO (14:00 - 16:00)
    # ==============================================
    elif 14 <= hora_actual < 17:
        if tipo_activo == TipoActivo.TIPO_B:
            return [Estrategia.R_50]
        else:
            return [Estrategia.NINGUNA]

    # ==============================================
    # ZONA 3: TARDE TARDE / ALTO RIESGO (17:00 - 18:00)
    # ==============================================
    elif 17 <= hora_actual < 19:
        # REGLA DE ORO: R_25 PROHIBIDO
        if tipo_activo == TipoActivo.TIPO_B:
            return [Estrategia.R_50]
        else:
            return [Estrategia.NINGUNA] # OPCIÓN SEGURA: PAUSAR

    # ==============================================
    # ZONA 4: NOCHE (19:00 - 21:00)
    # ==============================================
    elif 19 <= hora_actual < 22:
        if tipo_activo in [TipoActivo.TIPO_A, TipoActivo.TIPO_C]:
            return [Estrategia.R_10]
        else:
            return [Estrategia.NINGUNA]

    # ==============================================
    # FUERA DE HORARIO DEFINIDO
    # ==============================================
    else:
        return [Estrategia.NINGUNA]

# ------------------------------
# CONFIGURACIÓN GLOBAL
# ------------------------------
MONTO_FIJO = 0.35  # No cambiar, valor mínimo
