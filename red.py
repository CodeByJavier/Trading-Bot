"""
Red neuronal propia (sin librerías): una capa oculta que conecta TODOS los mercados.

  entradas (indicadores de todos los mercados + Fear & Greed)
      -> capa oculta (neuronas tanh: aquí se mezcla la información de unos mercados con otros)
      -> una salida por mercado (cuánto cree que subirá, en desviaciones típicas)

Aprende online: cada vez que se conoce lo que pasó, corrige sus pesos un poco (descenso de gradiente).
"""
import math
import random


class Red:
    def __init__(self, entradas, salidas, ocultas=24, tasa=0.01, regularizacion=1e-4, semilla=7):
        azar = random.Random(semilla)
        self.entradas, self.salidas, self.ocultas = entradas, salidas, ocultas
        self.tasa, self.regularizacion = tasa, regularizacion
        self.w1 = [[azar.gauss(0, 1 / math.sqrt(entradas)) for _ in range(entradas)] for _ in range(ocultas)]
        self.b1 = [0.0] * ocultas
        self.w2 = [[azar.gauss(0, 0.1 / math.sqrt(ocultas)) for _ in range(ocultas)] for _ in range(salidas)]
        self.b2 = [0.0] * salidas
        # Media y varianza de cada entrada, para ponerlas todas en la misma escala
        self.media = [0.0] * entradas
        self.m2 = [0.0] * entradas
        self.vistos = 0
        self.lecciones = 0

    def _normalizar(self, x):
        if self.vistos < 2:
            return [0.0] * len(x)
        z = []
        for valor, media, m2 in zip(x, self.media, self.m2):
            desviacion = math.sqrt(m2 / (self.vistos - 1))
            v = (valor - media) / desviacion if desviacion > 1e-12 else 0.0
            z.append(max(-5.0, min(5.0, v)))
        return z

    def _adelante(self, z):
        ocultas = [math.tanh(b + sum(w * zi for w, zi in zip(fila, z))) for fila, b in zip(self.w1, self.b1)]
        salidas = [b + sum(w * h for w, h in zip(fila, ocultas)) for fila, b in zip(self.w2, self.b2)]
        return ocultas, salidas

    def predecir(self, x):
        return self._adelante(self._normalizar(x))[1]

    def observar(self, x):
        """Actualiza la escala de las entradas (solo con datos ya conocidos)."""
        self.vistos += 1
        for k, valor in enumerate(x):
            delta = valor - self.media[k]
            self.media[k] += delta / self.vistos
            self.m2[k] += delta * (valor - self.media[k])

    def entrenar(self, x, objetivos, mascara):
        """Un paso de aprendizaje. `mascara[o]` = 0 si no se sabe el resultado de esa salida."""
        z = self._normalizar(x)
        ocultas, salidas = self._adelante(z)
        errores = [(s - max(-4.0, min(4.0, o))) * m for s, o, m in zip(salidas, objetivos, mascara)]
        if not any(errores):
            return 0.0
        # Error que llega a cada neurona oculta (antes de tocar los pesos de salida)
        delta_oculta = [(1 - h * h) * sum(e * self.w2[o][j] for o, e in enumerate(errores) if e)
                        for j, h in enumerate(ocultas)]
        tasa, reg = self.tasa, self.regularizacion
        for o, e in enumerate(errores):
            if e:
                fila = self.w2[o]
                for j, h in enumerate(ocultas):
                    fila[j] -= tasa * (e * h + reg * fila[j])
                self.b2[o] -= tasa * e
        for j, d in enumerate(delta_oculta):
            if d:
                fila = self.w1[j]
                for k, zk in enumerate(z):
                    if zk:
                        fila[k] -= tasa * (d * zk + reg * fila[k])
                self.b1[j] -= tasa * d
        self.lecciones += 1
        return sum(e * e for e in errores) / max(1, sum(mascara))

    def importancia_entradas(self):
        """Cuánto pesa cada entrada en la red (suma de |pesos| hacia la capa oculta)."""
        return [sum(abs(self.w1[j][k]) for j in range(self.ocultas)) for k in range(self.entradas)]

    def a_dict(self):
        return dict(self.__dict__)

    @classmethod
    def desde_dict(cls, datos):
        red = cls(datos["entradas"], datos["salidas"], datos["ocultas"])
        red.__dict__.update(datos)
        return red
