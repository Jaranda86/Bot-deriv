import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

MIN_OPERACIONES_PARA_ENTRENAR = 100

class ModeloIA:

    def __init__(self):
        self.historial = []
        self.modelo = None
        self.scaler = None
        self.usando_ia = False

    def construir_features(self, rsi, macd, senal_macd, hist, dir_vela, score,
                           bb_pos, stoch_k, stoch_d, ema_tend, ema_diff):

        return [
            rsi, macd, senal_macd, hist,
            dir_vela, score,
            bb_pos, stoch_k, stoch_d,
            ema_tend, abs(ema_diff)
        ]

    def registrar_resultado(self, features, gano):
        self.historial.append((features, 1 if gano else 0))

        if len(self.historial) >= MIN_OPERACIONES_PARA_ENTRENAR:
            self.entrenar()

    def entrenar(self):
        X = np.array([x[0] for x in self.historial])
        y = np.array([x[1] for x in self.historial])

        self.scaler = StandardScaler()
        X = self.scaler.fit_transform(X)

        self.modelo = RandomForestClassifier(
            n_estimators=200,
            max_depth=4,
            min_samples_leaf=5
        )

        self.modelo.fit(X, y)
        self.usando_ia = True

    def predecir_confianza(self, features):
        if not self.usando_ia:
            return None

        X = self.scaler.transform([features])
        return max(self.modelo.predict_proba(X)[0])
