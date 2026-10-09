"""
Datos externos al precio, gratuitos y sin cuenta:
  - Fear & Greed (alternative.me): sentimiento diario del mercado cripto, 0 = miedo extremo, 100 = codicia extrema.
  - Funding rate (futuros perpetuos de Binance): positivo = la mayoría apuesta a subidas y paga por ello.

enriquecer() los añade a cada vela SIN mirar al futuro:
  - Fear & Greed: se usa el valor del día anterior al cierre de la vela (ya publicado seguro).
  - Funding: el último cobro anterior al cierre de la vela.
"""
import bisect
from datetime import datetime, timezone

from datos import _pedir

URL_FNG = "https://api.alternative.me/fng/?limit={dias}&format=json"
URL_FUNDING = "https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=1000&startTime={desde}"
DIA_MS = 86400000


def _dia(t_ms):
    return datetime.fromtimestamp(t_ms / 1000, timezone.utc).strftime("%Y-%m-%d")


def miedo_codicia(dias=0):
    """{día UTC 'AAAA-MM-DD': valor 0-100}. dias=0 descarga toda la historia (desde 2018)."""
    datos = _pedir(URL_FNG.format(dias=dias))["data"]
    return {_dia(int(d["timestamp"]) * 1000): int(d["value"]) for d in datos}


def funding(desde_ms):
    """Lista ordenada de (momento en ms, funding rate) desde `desde_ms`."""
    resultado = {}
    while True:
        lote = _pedir(URL_FUNDING.format(desde=desde_ms))
        for f in lote:
            resultado[int(f["fundingTime"])] = float(f["fundingRate"])
        if len(lote) < 1000:
            break
        desde_ms = int(lote[-1]["fundingTime"]) + 1
    return sorted(resultado.items())


def enriquecer(velas, fng=None, tasas=None):
    """Añade a cada vela los campos fng, fng_7, funding y funding_medio (si hay datos)."""
    if fng is not None:
        for v in velas:
            v["fng"] = fng.get(_dia(v["cierre_t"] - DIA_MS))
            v["fng_7"] = fng.get(_dia(v["cierre_t"] - 8 * DIA_MS))
    if tasas:
        momentos = [t for t, _ in tasas]
        for v in velas:
            k = bisect.bisect_right(momentos, v["cierre_t"])
            if k == 0:
                v["funding"] = v["funding_medio"] = None
                continue
            v["funding"] = tasas[k - 1][1]
            ultimas = [r for _, r in tasas[max(0, k - 9): k]]  # 9 cobros = 3 días
            v["funding_medio"] = sum(ultimas) / len(ultimas)
    return velas


def dias_necesarios(velas):
    """Cuántos días de Fear & Greed hacen falta para cubrir estas velas."""
    if not velas:
        return 0
    return (velas[-1]["cierre_t"] - velas[0]["t"]) // DIA_MS + 10
