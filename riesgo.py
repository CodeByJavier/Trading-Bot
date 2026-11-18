"""
Métricas de riesgo de una serie de valores horarios de una cartera (fórmulas estándar).

  - volatilidad: cuánto se mueve el valor, en % anual (desviación típica de los rendimientos × √horas del año)
  - caida_maxima: la peor bajada desde un máximo
  - sharpe: rentabilidad anual / volatilidad anual (sin tipo libre de riesgo). >1 bueno, <0 pierde dinero
  - var_dia: pérdida en un día malo (el peor de cada 20 días, VaR histórico al 95 %)
  - peor_dia: la mayor pérdida en 24 h observada

Con menos de una semana de datos las cifras anuales no significan nada: se marca "pocos_datos".
"""
import math

HORAS_ANO = 24 * 365


def metricas(valores, horas_por_punto=1):
    if len(valores) < 3 or any(v <= 0 for v in valores):
        return None
    rendimientos = [b / a - 1 for a, b in zip(valores, valores[1:])]
    n = len(rendimientos)
    media = sum(rendimientos) / n
    desviacion = math.sqrt(sum((r - media) ** 2 for r in rendimientos) / max(1, n - 1))
    puntos_ano = HORAS_ANO / horas_por_punto
    volatilidad = desviacion * math.sqrt(puntos_ano)
    sharpe = (media * puntos_ano) / volatilidad if volatilidad > 0 else None

    pico, caida = valores[0], 0.0
    for v in valores:
        pico = max(pico, v)
        caida = max(caida, (pico - v) / pico)

    paso_dia = max(1, round(24 / horas_por_punto))
    dias = sorted(valores[i] / valores[i - paso_dia] - 1 for i in range(paso_dia, len(valores)))
    var_dia = -dias[int(0.05 * (len(dias) - 1))] if len(dias) >= 20 else None
    peor_dia = -dias[0] if dias else None

    return {
        "rentabilidad": valores[-1] / valores[0] - 1,
        "volatilidad": volatilidad,
        "caida_maxima": caida,
        "sharpe": sharpe,
        "var_dia": var_dia,
        "peor_dia": peor_dia,
        "puntos": len(valores),
        "pocos_datos": len(valores) < 7 * 24 / horas_por_punto,
    }


def comparar(valores_estrategia, valores_referencia):
    """Métricas de la estrategia y de su referencia (comprar y mantener) sobre los mismos puntos."""
    return {"estrategia": metricas(valores_estrategia), "referencia": metricas(valores_referencia)}
