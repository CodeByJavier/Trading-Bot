"""
Descarga precios reales desde APIs públicas y gratuitas (sin cuenta ni clave).
Usa Binance y, si no responde (por ejemplo, desde servidores de EE. UU.), Coinbase.
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

URL_BINANCE = "https://data-api.binance.vision/api/v3/klines"
URL_COINBASE = "https://api.exchange.coinbase.com/products/{producto}/candles"
SEGUNDOS_COINBASE = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "6h": 21600, "1d": 86400}


def _pedir(url, intentos=4):
    ultimo_error = None
    for intento in range(intentos):
        try:
            peticion = urllib.request.Request(url, headers={"User-Agent": "bot-trading-simulado"})
            with urllib.request.urlopen(peticion, timeout=20) as respuesta:
                return json.load(respuesta)
        except urllib.error.HTTPError as error:
            if 400 <= error.code < 500 and error.code != 429:
                raise ConnectionError(f"la API respondió {error.code} {error.reason}")
            ultimo_error = error
        except Exception as error:
            ultimo_error = error
        espera = 2 ** intento
        print(f"  (aviso) fallo al descargar datos: {ultimo_error}. Reintento en {espera} s...")
        time.sleep(espera)
    raise ConnectionError(f"No se pudieron descargar los datos de mercado ({ultimo_error}).")


def _solo_cerradas(velas, cantidad):
    ahora = int(time.time() * 1000)
    cerradas = sorted((v for v in velas.values() if v["cierre_t"] < ahora), key=lambda v: v["t"])
    return cerradas[-cantidad:]


def _binance(simbolo, intervalo, cantidad):
    velas = {}
    fin = None
    while len(velas) < cantidad + 1:
        parametros = {"symbol": simbolo, "interval": intervalo,
                      "limit": min(1000, cantidad + 1 - len(velas))}
        if fin is not None:
            parametros["endTime"] = fin
        lote = _pedir(URL_BINANCE + "?" + urllib.parse.urlencode(parametros))
        if not lote:
            break
        for k in lote:
            velas[k[0]] = {"t": k[0], "apertura": float(k[1]), "maximo": float(k[2]),
                           "minimo": float(k[3]), "cierre": float(k[4]),
                           "volumen": float(k[5]), "cierre_t": k[6]}
        fin = lote[0][0] - 1
        if len(lote) < parametros["limit"]:
            break
    return _solo_cerradas(velas, cantidad)


def _coinbase(simbolo, intervalo, cantidad):
    if intervalo not in SEGUNDOS_COINBASE:
        raise ConnectionError(f"Coinbase no ofrece velas de {intervalo}.")
    segundos = SEGUNDOS_COINBASE[intervalo]
    producto = f"{simbolo[:-3]}-{simbolo[-3:]}"
    url = URL_COINBASE.format(producto=producto)
    velas = {}
    fin = int(time.time()) // segundos * segundos + segundos
    while len(velas) < cantidad + 1:
        inicio = fin - 300 * segundos
        parametros = {"granularity": segundos,
                      "start": datetime.fromtimestamp(inicio, timezone.utc).isoformat(),
                      "end": datetime.fromtimestamp(fin, timezone.utc).isoformat()}
        lote = _pedir(url + "?" + urllib.parse.urlencode(parametros))
        if not lote:
            break
        for k in lote:  # [tiempo, mínimo, máximo, apertura, cierre, volumen]
            t = k[0] * 1000
            velas[t] = {"t": t, "apertura": float(k[3]), "maximo": float(k[2]),
                        "minimo": float(k[1]), "cierre": float(k[4]),
                        "volumen": float(k[5]), "cierre_t": t + segundos * 1000 - 1}
        fin = inicio
        time.sleep(0.2)  # Coinbase limita las peticiones por segundo
    return _solo_cerradas(velas, cantidad)


def descargar_velas(simbolo, intervalo, cantidad):
    """Devuelve las últimas `cantidad` velas ya cerradas, de la más antigua a la más reciente."""
    try:
        return _binance(simbolo, intervalo, cantidad)
    except ConnectionError as error:
        print(f"  (aviso) Binance no disponible ({error}); uso Coinbase.")
        return _coinbase(simbolo, intervalo, cantidad)
