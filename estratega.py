"""
Estratega multimercado: la red neuronal decide cómo repartir la cartera entre todos los mercados.

En cada momento de decisión (cada día o cada hora):
  1. Aprende: comprueba las predicciones que hizo hace HORIZONTE pasos con lo que pasó de verdad,
     y repasa también algunos momentos pasados al azar (todos ya conocidos).
  2. Predice cuánto subirá cada mercado, mirando a la vez los indicadores de TODOS los mercados.
  3. Reparte según su confianza: más peso donde la subida prevista supera con holgura las
     comisiones, nada donde no, y el resto en euros.
  4. Solo opera si el cambio merece la pena (banda) y si ese mercado está abierto (precio reciente).

Lo usan igual el laboratorio (con la historia) y el bot en vivo.
"""
import bisect
import math
import random
from datetime import datetime, timezone

import indicadores
from red import Red

DIA_MS = 86400000
HORA_MS = 3600000
LISTA = indicadores.expandir(["precio"])
HISTORIA = indicadores.historia_necesaria(LISTA)
RASGOS_POR_MERCADO = len(LISTA) + 2  # + "tiene datos" + "antigüedad del último precio (días)"


def _dia(t_ms):
    return datetime.fromtimestamp(t_ms / 1000, timezone.utc).strftime("%Y-%m-%d")


class Datos:
    """Velas de todos los mercados y Fear & Greed, con consultas "¿qué se sabía en el momento t?"."""

    def __init__(self, series, intervalo, fng=None):
        self.series = series
        self.intervalo = intervalo
        self.paso = DIA_MS if intervalo == "1d" else HORA_MS
        self.cierres = {m: [v["cierre_t"] for v in velas] for m, velas in series.items()}
        self.fng = fng or {}
        self._cache = {}

    def indice(self, m, t):
        if m not in self.series:
            return -1
        return bisect.bisect_right(self.cierres[m], t) - 1

    def precio(self, m, t):
        j = self.indice(m, t)
        return self.series[m][j]["cierre"] if j >= 0 else None

    def abierto(self, m, t):
        """¿Hay un precio reciente (se puede operar)? La bolsa no lo tiene de noche ni en fin de semana."""
        j = self.indice(m, t)
        return j >= HISTORIA - 1 and t - self.series[m][j]["cierre_t"] <= self.paso + 60000

    def _rasgos(self, m, j):
        clave = (m, j)
        if clave not in self._cache:
            self._cache[clave] = indicadores.caracteristicas(self.series[m], j, LISTA)
        return self._cache[clave]

    def entrada(self, claves, t):
        x = []
        for m in claves:
            j = self.indice(m, t)
            if j >= HISTORIA - 1:
                edad = min(5.0, (t - self.series[m][j]["cierre_t"]) / DIA_MS)
                x += self._rasgos(m, j) + [1.0, edad]
            else:
                x += [0.0] * RASGOS_POR_MERCADO
        ahora = self.fng.get(_dia(t - DIA_MS))
        antes = self.fng.get(_dia(t - 8 * DIA_MS))
        x += [0.0 if ahora is None else ahora / 100 - 0.5,
              0.0 if ahora is None or antes is None else (ahora - antes) / 100]
        return x


class CarteraMulti:
    """Dinero ficticio repartido entre varios mercados, con 1 € por orden y spread."""

    def __init__(self, capital, comision_fija=1.0, spread=0.001):
        self.capital_inicial = capital
        self.efectivo = capital
        self.unidades = {}
        self.coste = {}  # euros invertidos en cada posición (para el resultado al vender)
        self.fija, self.spread = comision_fija, spread
        self.operaciones = []
        self.comisiones_pagadas = 0.0

    def valor_bruto(self, precios):
        return self.efectivo + sum(q * precios[m] for m, q in self.unidades.items() if q > 0 and m in precios)

    def valor(self, precios):
        """Lo que valdría si se vendiera todo ahora (con comisiones y spread)."""
        return self.efectivo + sum(q * precios[m] * (1 - self.spread) - self.fija
                                   for m, q in self.unidades.items() if q > 0 and m in precios)

    def pesos(self, precios):
        total = self.valor_bruto(precios)
        return {m: q * precios[m] / total for m, q in self.unidades.items() if q > 0 and m in precios}

    def _vender(self, m, cantidad, precio, fecha, t):
        cantidad = min(cantidad, self.unidades[m])
        bruto = cantidad * precio * (1 - self.spread)
        neto = bruto - self.fija
        parte = cantidad / self.unidades[m]
        coste = self.coste[m] * parte
        self.unidades[m] -= cantidad
        self.coste[m] -= coste
        if self.unidades[m] <= 1e-12:
            self.unidades.pop(m)
            self.coste.pop(m)
        self.efectivo += neto
        self.comisiones_pagadas += self.fija
        op = {"tipo": "VENTA", "mercado": m, "fecha": fecha, "t": t, "precio": precio, "cantidad": cantidad,
              "euros": neto, "comision": self.fija, "resultado": neto - coste}
        self.operaciones.append(op)
        return op

    def _comprar(self, m, importe, precio, fecha, t):
        cantidad = (importe - self.fija) / (precio * (1 + self.spread))
        self.unidades[m] = self.unidades.get(m, 0.0) + cantidad
        self.coste[m] = self.coste.get(m, 0.0) + importe
        self.efectivo -= importe
        self.comisiones_pagadas += self.fija
        op = {"tipo": "COMPRA", "mercado": m, "fecha": fecha, "t": t, "precio": precio, "cantidad": cantidad,
              "euros": importe, "comision": self.fija, "resultado": None}
        self.operaciones.append(op)
        return op

    def rebalancear(self, objetivo, precios, abiertos, fecha, t, banda=0.05):
        """Acerca la cartera a los pesos objetivo. Solo toca mercados abiertos y cambios mayores que la banda."""
        total = self.valor_bruto(precios)
        actuales = self.pesos(precios)
        hechas = []
        for m in list(self.unidades):  # primero vender, para tener euros
            if m not in abiertos:
                continue
            w, w_obj = actuales.get(m, 0.0), objetivo.get(m, 0.0)
            if w_obj == 0 or w - w_obj > banda:
                cantidad = self.unidades[m] if w_obj == 0 else (w - w_obj) * total / precios[m]
                hechas.append(self._vender(m, cantidad, precios[m], fecha, t))
        actuales = self.pesos(precios)
        for m, w_obj in sorted(objetivo.items(), key=lambda par: -par[1]):
            if m not in abiertos:
                continue
            falta = w_obj - actuales.get(m, 0.0)
            if falta > banda:
                importe = min(falta * total, self.efectivo)
                if importe >= 10 * self.fija:
                    hechas.append(self._comprar(m, importe, precios[m], fecha, t))
        return hechas

    def a_dict(self):
        return dict(self.__dict__)

    @classmethod
    def desde_dict(cls, datos):
        cartera = cls(datos["capital_inicial"])
        cartera.__dict__.update(datos)
        return cartera


class Estratega:
    def __init__(self, claves, intervalo, horizonte, capital=1000.0, comision_fija=1.0, spread=0.001,
                 ocultas=24, tasa=0.01, repaso=16, ventana_repaso=400, peso_maximo=0.5, banda=0.05, semilla=7):
        self.claves = list(claves)
        self.intervalo = intervalo
        self.horizonte = horizonte
        self.paso = DIA_MS if intervalo == "1d" else HORA_MS
        self.red = Red(len(claves) * RASGOS_POR_MERCADO + 2, len(claves), ocultas, tasa, semilla=semilla)
        self.sigma = {m: [0, 0.0] for m in claves}  # nº de rendimientos vistos, suma de cuadrados
        self.repaso, self.ventana_repaso = repaso, ventana_repaso
        self.peso_maximo, self.banda = peso_maximo, banda
        # Subida mínima prevista para que compense comprar y vender una posición de ~1/4 de la cartera
        self.umbral = 2 * spread + 2 * comision_fija / (0.25 * capital)
        self.plenitud = 2 * self.umbral  # exceso previsto con el que invertiría el 100 %
        self.semilla = semilla
        self.pendientes = []
        self.evaluaciones = []
        self.ultima_prediccion = {}

    # ---------------------------------------------------------------- utilidades
    def _sigma(self, m):
        n, suma = self.sigma[m]
        return math.sqrt(suma / n) if n >= 20 else None

    def _objetivos(self, datos, t_inicio, t_fin, precios_inicio=None):
        """Rendimiento (log) de cada mercado entre dos momentos, en desviaciones típicas."""
        objetivos, mascara, reales = [], [], {}
        for m in self.claves:
            p0 = precios_inicio.get(m) if precios_inicio is not None else datos.precio(m, t_inicio)
            p1 = datos.precio(m, t_fin)
            s = self._sigma(m)
            if p0 and p1 and datos.indice(m, t_inicio) >= HISTORIA - 1:
                r = math.log(p1 / p0)
                reales[m] = r
                if s:
                    objetivos.append(r / s)
                    mascara.append(1)
                    continue
            objetivos.append(0.0)
            mascara.append(0)
        return objetivos, mascara, reales

    # ---------------------------------------------------------------- un paso
    def paso_de_tiempo(self, datos, t, cartera=None, operar=True, fecha=None):
        h_ms = self.horizonte * self.paso
        # 1) Aprender de las predicciones cuyo resultado ya se conoce
        quedan = []
        for p in self.pendientes:
            if p["t"] + h_ms > t:
                quedan.append(p)
                continue
            _, _, reales = self._objetivos(datos, p["t"], p["t"] + h_ms, p["precios"])
            for m, r in reales.items():
                self.sigma[m][0] += 1
                self.sigma[m][1] += r * r
                if m in p["prediccion"]:
                    self.evaluaciones.append({"t": p["t"], "m": m, "p": p["prediccion"][m], "r": r})
            objetivos, mascara, _ = self._objetivos(datos, p["t"], p["t"] + h_ms, p["precios"])
            self.red.observar(p["x"])
            self.red.entrenar(p["x"], objetivos, mascara)
            # Repaso: momentos pasados al azar, cuyo resultado ya se sabía en t
            azar = random.Random(self.semilla + self.red.lecciones)
            for _ in range(self.repaso):
                atras = azar.randint(self.horizonte, self.horizonte + self.ventana_repaso)
                t_r = p["t"] + h_ms - atras * self.paso
                objetivos_r, mascara_r, _ = self._objetivos(datos, t_r, t_r + h_ms)
                if sum(mascara_r):
                    self.red.entrenar(datos.entrada(self.claves, t_r), objetivos_r, mascara_r)
        self.pendientes = quedan

        # 2) Predecir
        x = datos.entrada(self.claves, t)
        salidas = self.red.predecir(x)
        prediccion = {}
        for m, z in zip(self.claves, salidas):
            s = self._sigma(m)
            if s and datos.indice(m, t) >= HISTORIA - 1:
                prediccion[m] = z * s
        precios = {m: datos.precio(m, t) for m in self.claves if datos.precio(m, t)}
        self.pendientes.append({"t": t, "x": x, "precios": precios, "prediccion": prediccion})
        self.ultima_prediccion = prediccion

        # 3) Repartir y operar
        objetivo = self.repartir(prediccion)
        operaciones = []
        if cartera is not None and operar:
            abiertos = {m for m in self.claves if datos.abierto(m, t)}
            operaciones = cartera.rebalancear(objetivo, precios, abiertos, fecha or _dia(t), t, self.banda)
        return {"prediccion": prediccion, "objetivo": objetivo, "operaciones": operaciones, "precios": precios}

    def repartir(self, prediccion):
        """Pesos objetivo según la confianza: exceso previsto sobre las comisiones."""
        exceso = {m: r - self.umbral for m, r in prediccion.items() if r > self.umbral}
        total = sum(exceso.values())
        if total <= 0:
            return {}
        invertido = min(1.0, total / self.plenitud)
        return {m: min(self.peso_maximo, invertido * e / total) for m, e in exceso.items()}

    # ---------------------------------------------------------------- guardar
    def a_dict(self):
        datos = dict(self.__dict__)
        datos["red"] = self.red.a_dict()
        return datos

    @classmethod
    def desde_dict(cls, datos):
        estratega = cls(datos["claves"], datos["intervalo"], datos["horizonte"])
        estratega.__dict__.update({k: v for k, v in datos.items() if k != "red"})
        estratega.red = Red.desde_dict(datos["red"])
        return estratega


def habilidad(evaluaciones, horizonte, claves=None):
    """Por mercado: correlación entre lo previsto y lo que pasó (IC) y su z.

    IC > 0 = sus previsiones van en la buena dirección más de lo que daría el azar.
    Como las predicciones se solapan, cuentan como n / horizonte independientes.
    """
    grupos = {}
    for e in evaluaciones:
        grupos.setdefault(e["m"], []).append(e)
    resultado = {}
    for m, lista in grupos.items():
        if claves and m not in claves:
            continue
        n = len(lista)
        if n < 10:
            continue
        ps, rs = [e["p"] for e in lista], [e["r"] for e in lista]
        mp, mr = sum(ps) / n, sum(rs) / n
        vp = sum((p - mp) ** 2 for p in ps)
        vr = sum((r - mr) ** 2 for r in rs)
        ic = sum((p - mp) * (r - mr) for p, r in zip(ps, rs)) / math.sqrt(vp * vr) if vp > 0 and vr > 0 else 0.0
        independientes = max(1.0, n / horizonte)
        resultado[m] = {"n": n, "ic": ic, "z": ic * math.sqrt(independientes),
                        "acierto": sum((p > 0) == (r > 0) for p, r in zip(ps, rs)) / n}
    return resultado
