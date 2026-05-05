import json
import os
import numpy as np
from sklearn.linear_model import LogisticRegression

DATA_FILE = "data.json"

class IA:
    def __init__(self):
        self.model = LogisticRegression()
        self.X = []
        self.y = []
        self.cargar()

    def cargar(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.X = data["X"]
                self.y = data["y"]

            if len(self.X) > 10:
                self.model.fit(self.X, self.y)

    def guardar(self):
        with open(DATA_FILE, "w") as f:
            json.dump({"X": self.X, "y": self.y}, f)

    def features(self, closes):
        ema9 = np.mean(closes[-9:])
        ema21 = np.mean(closes[-21:])
        rsi = self.calc_rsi(closes)

        return [
            closes[-1],
            ema9,
            ema21,
            ema9 - ema21,
            rsi,
            closes[-1] - closes[-5]
        ]

    def calc_rsi(self, data, period=14):
        gains, losses = [], []
        for i in range(1, len(data)):
            d = data[i] - data[i-1]
            if d > 0:
                gains.append(d)
            else:
                losses.append(abs(d))

        if not gains or not losses:
            return 50

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def predecir(self, closes):
        if len(self.X) < 10:
            return 0.5

        f = np.array(self.features(closes)).reshape(1, -1)
        return self.model.predict_proba(f)[0][1]

    def aprender(self, closes, resultado):
        f = self.features(closes)
        self.X.append(f)
        self.y.append(1 if resultado > 0 else 0)

        if len(self.X) > 200:
            self.X = self.X[-200:]
            self.y = self.y[-200:]

        self.model.fit(self.X, self.y)
        self.guardar()
