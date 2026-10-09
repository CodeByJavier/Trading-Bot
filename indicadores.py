"""
Convierte el historial de precios en números que el cerebro puede estudiar.
Cada indicador usa solo información del pasado (nunca del futuro).
"""
import math

NOMBRES = [
    "Cambio última vela",
    "Cambio últimas 4 velas",
    "Cambio últimas 24 velas",
    "Distancia a la media de 24 velas",
    "Distancia a la media de 96 velas",
    "RSI 14 (fuerza compradora)",
    "Volatilidad 24 velas",
    "Volumen relativo",
    "Tamaño de la última vela",
]

HISTORIA_NECESARIA = 97  # velas mínimas para poder calcular todo


def caracteristicas(velas, i):
    """Indicadores en el momento de la vela i (usa las velas 0..i)."""
    ventana = velas[i - HISTORIA_NECESARIA + 1: i + 1]
    c = [v["cierre"] for v in ventana]
    actual = c[-1]

    def cambio(n):
        return actual / c[-1 - n] - 1

    media24 = sum(c[-24:]) / 24
    media96 = sum(c[-96:]) / 96

    rendimientos = [c[k] / c[k - 1] - 1 for k in range(len(c) - 24, len(c))]
    r_medio = sum(rendimientos) / len(rendimientos)
    volatilidad = math.sqrt(sum((r - r_medio) ** 2 for r in rendimientos) / len(rendimientos))

    subidas = bajadas = 0.0
    for k in range(len(c) - 14, len(c)):
        diferencia = c[k] - c[k - 1]
        if diferencia > 0:
            subidas += diferencia
        else:
            bajadas -= diferencia
    rsi = 0.5 if subidas + bajadas == 0 else subidas / (subidas + bajadas)

    volumenes = [v["volumen"] for v in ventana[-24:]]
    volumen_medio = sum(volumenes) / len(volumenes)
    volumen_relativo = volumenes[-1] / volumen_medio - 1 if volumen_medio > 0 else 0.0

    ultima = ventana[-1]
    tamano_vela = (ultima["maximo"] - ultima["minimo"]) / actual

    return [
        cambio(1),
        cambio(4),
        cambio(24),
        actual / media24 - 1,
        actual / media96 - 1,
        rsi - 0.5,
        volatilidad,
        volumen_relativo,
        tamano_vela,
    ]
