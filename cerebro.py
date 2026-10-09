"""
El cerebro del bot: una pequeña IA propia (regresión logística con aprendizaje online).

- predecir(): dice la probabilidad (0 a 1) de que el precio suba.
- aprender(): cuando ya se sabe qué pasó, corrige sus pesos para equivocarse menos.

Cada "peso" indica cuánto se fía de un indicador y en qué dirección.
"""
import math


def _sigmoide(s):
    s = max(-30.0, min(30.0, s))
    return 1.0 / (1.0 + math.exp(-s))


class Cerebro:
    def __init__(self, nombres, tasa_aprendizaje=0.01, regularizacion=0.0001):
        n = len(nombres)
        self.nombres = list(nombres)
        self.tasa = tasa_aprendizaje
        self.regularizacion = regularizacion
        self.pesos = [0.0] * n
        self.sesgo = 0.0
        # Media y varianza de cada indicador, para ponerlos todos en la misma escala
        self.media = [0.0] * n
        self.m2 = [0.0] * n
        self.vistos = 0
        self.lecciones = 0
        self.ultimos_aciertos = []    # 1 = acertó, 0 = falló
        self.ultimos_resultados = []  # 1 = el precio subió lo suficiente, 0 = no

    def _normalizar(self, x):
        if self.vistos < 2:
            return [0.0] * len(x)
        z = []
        for valor, media, m2 in zip(x, self.media, self.m2):
            desviacion = math.sqrt(m2 / (self.vistos - 1))
            v = (valor - media) / desviacion if desviacion > 1e-12 else 0.0
            z.append(max(-5.0, min(5.0, v)))
        return z

    def predecir(self, x):
        z = self._normalizar(x)
        return _sigmoide(self.sesgo + sum(w * zi for w, zi in zip(self.pesos, z)))

    def aprender(self, x, subio):
        """Aprende de un resultado ya conocido.

        Devuelve (predicción del cerebro, predicción ingenua), ambas hechas ANTES
        de ver el resultado, para poder evaluar honestamente si aprende algo.
        La predicción ingenua es "lo que suele pasar": el porcentaje de subidas recientes.
        """
        y = 1.0 if subio else 0.0
        prediccion = self.predecir(x)
        recientes = self.ultimos_resultados
        ingenua = sum(recientes) / len(recientes) if recientes else 0.5
        self.ultimos_aciertos.append(1 if (prediccion >= 0.5) == subio else 0)
        self.ultimos_aciertos = self.ultimos_aciertos[-500:]
        self.ultimos_resultados = (self.ultimos_resultados + [int(y)])[-500:]

        self.vistos += 1
        for k, valor in enumerate(x):
            delta = valor - self.media[k]
            self.media[k] += delta / self.vistos
            self.m2[k] += delta * (valor - self.media[k])

        z = self._normalizar(x)
        error = _sigmoide(self.sesgo + sum(w * zi for w, zi in zip(self.pesos, z))) - y
        for k in range(len(self.pesos)):
            self.pesos[k] -= self.tasa * (error * z[k] + self.regularizacion * self.pesos[k])
        self.sesgo -= self.tasa * error
        self.lecciones += 1
        return prediccion, ingenua

    def tasa_acierto(self):
        if not self.ultimos_aciertos:
            return None
        return sum(self.ultimos_aciertos) / len(self.ultimos_aciertos)

    def acierto_sin_pensar(self):
        """Aciertos que tendría respondiendo siempre lo mismo (la referencia a batir)."""
        if not self.ultimos_resultados:
            return None
        subidas = sum(self.ultimos_resultados) / len(self.ultimos_resultados)
        return max(subidas, 1 - subidas)

    def lo_aprendido(self):
        """Explica en texto qué indicadores pesan más en sus decisiones."""
        lineas = []
        orden = sorted(range(len(self.pesos)), key=lambda k: -abs(self.pesos[k]))
        for k in orden:
            w = self.pesos[k]
            if abs(w) < 0.01:
                opinion = "casi no le da importancia"
            elif w > 0:
                opinion = "cuando sube, cree que el precio subirá"
            else:
                opinion = "cuando sube, cree que el precio bajará"
            lineas.append((self.nombres[k], w, opinion))
        return lineas

    def a_dict(self):
        return dict(self.__dict__)

    @classmethod
    def desde_dict(cls, datos):
        cerebro = cls(datos["nombres"])
        cerebro.__dict__.update(datos)
        return cerebro
