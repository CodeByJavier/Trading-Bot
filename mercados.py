"""
Datos de todos los mercados de la cartera, en EUROS y alineados en el tiempo.

- Criptomonedas: pares en euros de Binance.
- Dólar: el par EUR/USDT de Binance, invertido (tener dólares gana cuando el dólar sube frente al euro).
- Bolsa: S&P 500 (ETF SPY, en dólares → se convierte a euros cada día) e IBEX 35 (en euros),
  velas diarias de Yahoo Finance. Solo cotizan entre semana y en horario de bolsa.

Todas las velas llevan "cierre_t": el momento en que esa vela ya es definitiva. Una decisión
tomada en el momento T solo puede usar velas con cierre_t <= T (nunca mira al futuro).
"""
import bisect
import urllib.parse

from datos import _pedir, descargar_velas

URL_YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{codigo}?interval=1d&range={rango}"
HORA_MS = 3600000
DIA_MS = 86400000

# clave -> (nombre, tipo, fuente, código)
MERCADOS = {
    "BTC": ("Bitcoin", "cripto", "binance", "BTCEUR"),
    "ETH": ("Ethereum", "cripto", "binance", "ETHEUR"),
    "BNB": ("BNB", "cripto", "binance", "BNBEUR"),
    "XRP": ("XRP", "cripto", "binance", "XRPEUR"),
    "SOL": ("Solana", "cripto", "binance", "SOLEUR"),
    "USD": ("Dólar", "divisa", "binance", "EURUSDT"),
    "SP500": ("S&P 500", "bolsa", "yahoo", "SPY"),
    "IBEX": ("IBEX 35", "bolsa", "yahoo", "^IBEX"),
}
CON_VELAS_HORARIAS = ["BTC", "ETH", "BNB", "XRP", "SOL", "USD"]  # cotizan 24 h en Binance


def nombre(clave):
    return MERCADOS[clave][0]


def _yahoo(codigo, rango="10y"):
    resultado = _pedir(URL_YAHOO.format(codigo=urllib.parse.quote(codigo), rango=rango))["chart"]["result"][0]
    q = resultado["indicators"]["quote"][0]
    velas = []
    for k, segundos in enumerate(resultado["timestamp"]):
        cierre = q["close"][k]
        if cierre is None:
            continue
        t = segundos * 1000
        velas.append({"t": t, "apertura": q["open"][k] or cierre, "maximo": q["high"][k] or cierre,
                      "minimo": q["low"][k] or cierre, "cierre": cierre, "volumen": q["volume"][k] or 0,
                      # la sesión dura < 9 h: a partir de entonces la vela del día es definitiva
                      "cierre_t": t + 9 * HORA_MS})
    return velas


def _invertir(velas):
    """EUR/USD -> valor en euros de 1 dólar."""
    return [dict(v, apertura=1 / v["apertura"], cierre=1 / v["cierre"],
                 maximo=1 / v["minimo"], minimo=1 / v["maximo"]) for v in velas]


def _a_euros(velas, dolar):
    """Convierte velas en dólares a euros con el valor del dólar de ese día."""
    momentos = [v["cierre_t"] for v in dolar]
    resultado = []
    for v in velas:
        k = bisect.bisect_right(momentos, v["cierre_t"]) - 1
        if k < 0:
            continue
        f = dolar[k]["cierre"]
        resultado.append(dict(v, apertura=v["apertura"] * f, maximo=v["maximo"] * f,
                              minimo=v["minimo"] * f, cierre=v["cierre"] * f))
    return resultado


def descargar(claves, intervalo, cantidad, cache=None, aviso=print):
    """Velas en euros de cada mercado. Si un mercado falla, se omite (y se avisa).

    `cache(nombre, funcion)` permite al laboratorio guardar las descargas.
    """
    cache = cache or (lambda nombre_cache, funcion: funcion())
    brutas = {}
    necesarias = set(claves) | ({"USD"} if "SP500" in claves else set())
    for clave in necesarias:
        _, _, fuente, codigo = MERCADOS[clave]
        try:
            if fuente == "binance":
                brutas[clave] = cache(f"red_{codigo}_{intervalo}",
                                      lambda c=codigo: descargar_velas(c, intervalo, cantidad))
            elif intervalo == "1d":
                rango = "10y" if cantidad > 700 else "2y"
                brutas[clave] = cache(f"red_{codigo.replace('^', '')}_1d_{rango}",
                                      lambda c=codigo, r=rango: _yahoo(c, r))
        except (ConnectionError, KeyError, TypeError, IndexError) as error:
            aviso(f"  (aviso) Sin datos de {nombre(clave)} ({error}); esta vez no se tendrá en cuenta.")
    series = {}
    if "USD" in brutas:
        brutas["USD"] = _invertir(brutas["USD"])
    for clave in claves:
        if clave not in brutas:
            continue
        if clave == "SP500":
            if "USD" not in brutas:
                aviso("  (aviso) Sin el valor del dólar no se puede pasar el S&P 500 a euros.")
                continue
            series[clave] = _a_euros(brutas[clave], brutas["USD"])
        else:
            series[clave] = brutas[clave]
    return series


def rejilla(series, intervalo, desde_t=None):
    """Momentos de decisión: el cierre de cada día (00:00 UTC) o de cada hora."""
    paso = DIA_MS if intervalo == "1d" else HORA_MS
    inicio = min(v[0]["cierre_t"] for v in series.values() if v)
    fin = max(v[-1]["cierre_t"] for v in series.values() if v)
    t = (inicio // paso + 1) * paso
    if desde_t:
        t = max(t, desde_t // paso * paso)
    momentos = []
    while t <= fin + 1:
        momentos.append(t)
        t += paso
    return momentos


def indices(series, momentos):
    """Para cada mercado y momento: índice de la última vela ya definitiva (o -1)."""
    resultado = {}
    for clave, velas in series.items():
        cierres = [v["cierre_t"] for v in velas]
        resultado[clave] = [bisect.bisect_right(cierres, t) - 1 for t in momentos]
    return resultado
