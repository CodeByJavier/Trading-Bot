"""
Convierte el historial de precios (y otros datos) en números que el cerebro puede estudiar.
Cada indicador usa solo información del pasado (nunca del futuro).

Los indicadores se agrupan para poder combinarlos en config.py o en el laboratorio:
  - "precio":       los 9 indicadores originales, sacados solo del precio y el volumen
  - "sentimiento":  índice Fear & Greed (miedo/codicia del mercado cripto)
  - "futuros":      funding rate de los futuros perpetuos (quién apuesta a subidas o bajadas)
  - "tendencia":    distancia a la media larga (TENDENCIA_VELAS)
"""
import math

import config


def _cierres(velas, i, n):
    return [v["cierre"] for v in velas[i - n + 1: i + 1]]


def _cambio(n):
    def calcular(velas, i):
        return velas[i]["cierre"] / velas[i - n]["cierre"] - 1
    return calcular


def _distancia_media(n):
    def calcular(velas, i):
        return velas[i]["cierre"] / (sum(_cierres(velas, i, n)) / n) - 1
    return calcular


def _rsi(velas, i, n=14):
    subidas = bajadas = 0.0
    for k in range(i - n + 1, i + 1):
        diferencia = velas[k]["cierre"] - velas[k - 1]["cierre"]
        if diferencia > 0:
            subidas += diferencia
        else:
            bajadas -= diferencia
    return 0.0 if subidas + bajadas == 0 else subidas / (subidas + bajadas) - 0.5


def _volatilidad(velas, i, n=24):
    rendimientos = [velas[k]["cierre"] / velas[k - 1]["cierre"] - 1 for k in range(i - n + 1, i + 1)]
    media = sum(rendimientos) / n
    return math.sqrt(sum((r - media) ** 2 for r in rendimientos) / n)


def _volumen_relativo(velas, i, n=24):
    media = sum(v["volumen"] for v in velas[i - n + 1: i + 1]) / n
    return velas[i]["volumen"] / media - 1 if media > 0 else 0.0


def _tamano_vela(velas, i):
    return (velas[i]["maximo"] - velas[i]["minimo"]) / velas[i]["cierre"]


def _miedo_codicia(velas, i):
    valor = velas[i].get("fng")
    return 0.0 if valor is None else valor / 100 - 0.5


def _miedo_codicia_cambio(velas, i):
    ahora, antes = velas[i].get("fng"), velas[i].get("fng_7")
    return 0.0 if ahora is None or antes is None else (ahora - antes) / 100


def _funding(velas, i):
    valor = velas[i].get("funding")
    return 0.0 if valor is None else valor * 1000


def _funding_medio(velas, i):
    valor = velas[i].get("funding_medio")
    return 0.0 if valor is None else valor * 1000


def _distancia_media_larga(velas, i):
    return _distancia_media(config.TENDENCIA_VELAS)(velas, i)


# clave -> (nombre legible, función, velas de historia que necesita)
CATALOGO = {
    "cambio_1": ("Cambio última vela", _cambio(1), 2),
    "cambio_4": ("Cambio últimas 4 velas", _cambio(4), 5),
    "cambio_24": ("Cambio últimas 24 velas", _cambio(24), 25),
    "media_24": ("Distancia a la media de 24 velas", _distancia_media(24), 24),
    "media_96": ("Distancia a la media de 96 velas", _distancia_media(96), 96),
    "rsi_14": ("RSI 14 (fuerza compradora)", _rsi, 15),
    "volatilidad_24": ("Volatilidad 24 velas", _volatilidad, 25),
    "volumen": ("Volumen relativo", _volumen_relativo, 24),
    "tamano_vela": ("Tamaño de la última vela", _tamano_vela, 1),
    "miedo_codicia": ("Fear & Greed (miedo/codicia)", _miedo_codicia, 1),
    "miedo_codicia_cambio": ("Cambio del Fear & Greed en 7 días", _miedo_codicia_cambio, 1),
    "funding": ("Funding rate de futuros", _funding, 1),
    "funding_medio": ("Funding rate medio 3 días", _funding_medio, 1),
    "media_larga": ("Distancia a la media larga", _distancia_media_larga, None),
}

GRUPOS = {
    "precio": ["cambio_1", "cambio_4", "cambio_24", "media_24", "media_96",
               "rsi_14", "volatilidad_24", "volumen", "tamano_vela"],
    "sentimiento": ["miedo_codicia", "miedo_codicia_cambio"],
    "futuros": ["funding", "funding_medio"],
    "tendencia": ["media_larga"],
}


def expandir(lista=None):
    """Convierte una lista de grupos y/o indicadores en la lista de claves de indicadores."""
    claves = []
    for elemento in (config.INDICADORES if lista is None else lista):
        for clave in GRUPOS.get(elemento, [elemento]):
            if clave not in CATALOGO:
                raise ValueError(f"Indicador desconocido: {clave}")
            if clave not in claves:
                claves.append(clave)
    return claves


def nombres(lista=None):
    return [CATALOGO[clave][0] for clave in expandir(lista)]


def necesita(lista, grupo):
    """¿La lista usa algún indicador del grupo? (para saber qué datos externos descargar)"""
    claves = expandir(lista)
    return any(clave in claves for clave in GRUPOS[grupo])


def historia_necesaria(lista=None, tendencia_velas=None):
    tendencia_velas = tendencia_velas or config.TENDENCIA_VELAS
    maximo = max(tendencia_velas if CATALOGO[c][2] is None else CATALOGO[c][2] for c in expandir(lista))
    return max(maximo, tendencia_velas) + 1


def caracteristicas(velas, i, lista=None):
    """Indicadores en el momento de la vela i (usa solo las velas 0..i)."""
    return [CATALOGO[clave][1](velas, i) for clave in expandir(lista)]


def media(velas, i, n):
    return sum(_cierres(velas, i, n)) / n


def tendencia_alcista(velas, i, n=None, margen=None, en_posicion=False):
    """Regla clásica: el precio está por encima de su media de n velas.

    Con `margen` (por ejemplo 0.03 = 3 %) hace falta superar la media en ese porcentaje
    para entrar, y caer por debajo en ese porcentaje para salir. Así no compra y vende
    cada vez que el precio roza la media (cada operación cuesta comisión).
    """
    n = n or config.TENDENCIA_VELAS
    margen = config.TENDENCIA_MARGEN if margen is None else margen
    referencia = media(velas, i, n) * ((1 - margen) if en_posicion else (1 + margen))
    return velas[i]["cierre"] > referencia


# Valores para el bot en vivo (según config.py)
NOMBRES = nombres()
HISTORIA_NECESARIA = historia_necesaria()
