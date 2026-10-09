"""
Exporta el estado del bot a docs/datos.json, que es lo que lee el panel web.
"""
import json
import os
from datetime import datetime, timezone

import aprendizaje
import config


NOMBRES_MERCADOS = {"BTCEUR": "Bitcoin", "ETHEUR": "Ethereum", "BNBEUR": "BNB", "XRPEUR": "XRP",
                    "SOLEUR": "Solana", "ADAEUR": "Cardano", "EURUSDT": "Euro/dólar"}


def nombre_mercado(simbolo):
    return NOMBRES_MERCADOS.get(simbolo, simbolo[:-3])


def _duracion(velas, intervalo):
    minutos = {"15m": 15, "1h": 60, "4h": 240, "1d": 1440}.get(intervalo, 60) * velas
    if intervalo == "1d":
        dias = minutos // 1440
        return f"{dias} día" + ("s" if dias != 1 else "")
    horas = minutos / 60
    return f"{horas:g} hora" + ("s" if horas != 1 else "")


def exportar_panel(estado, cerebro, cartera):
    clave, lineas = aprendizaje.veredicto(estado)
    icono, titulo, explicacion = aprendizaje.VEREDICTOS[clave]
    historial = estado["historial"]
    ultimo = historial[-1] if historial else None
    acierto = cerebro.tasa_acierto()
    sin_pensar = cerebro.acierto_sin_pensar()
    datos = {
        "actualizado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo": os.environ.get("GITHUB_REPOSITORY"),
        "simbolo": estado["simbolo"],
        "intervalo": estado["intervalo"],
        "creado": estado["creado"],
        "pausado": config.PAUSADO,
        "capital_inicial": config.CAPITAL_INICIAL,
        "umbral_compra": config.UMBRAL_COMPRA,
        "umbral_venta": config.UMBRAL_VENTA,
        "movimiento_minimo": config.MOVIMIENTO_MINIMO,
        "horizonte": config.HORIZONTE,
        "comision_fija": config.COMISION_FIJA,
        "en_posicion": cartera.en_posicion,
        "comisiones": round(cartera.comisiones_pagadas, 2),
        "lecciones": cerebro.lecciones,
        "aciertos": None if acierto is None else round(acierto, 4),
        "aciertos_sin_pensar": None if sin_pensar is None else round(sin_pensar, 4),
        "ultimo": ultimo,
        "historial": [{"f": p["fecha"], "b": round(p["bot"], 2), "r": round(p["referencia"], 2),
                       "p": round(p["precio"], 2)} for p in historial[-3000:]],
        "operaciones": cartera.operaciones[-200:],
        "aprendido": [{"nombre": n, "peso": round(w, 4), "opinion": o}
                      for n, w, o in cerebro.lo_aprendido()],
        "eventos": estado.get("eventos", [])[-50:],
        "version": config.VERSION_MODELO,
        "estrategia": config.ESTRATEGIA,
        "ia_decide": config.ESTRATEGIA in ("ia", "tendencia_ia"),
        "tendencia": estado.get("tendencia"),
        "horizonte_texto": _duracion(config.HORIZONTE, estado["intervalo"]),
        "mercados_ia": [nombre_mercado(m) for m in estado.get("mercados_ia", [estado["simbolo"]])],
        "aprendizaje": {"veredicto": clave, "icono": icono, "titulo": titulo, "explicacion": explicacion,
                        "periodos": [dict(r, nombre=nombre) for nombre, r in lineas]},
    }
    os.makedirs(config.CARPETA_PANEL, exist_ok=True)
    ruta = os.path.join(config.CARPETA_PANEL, "datos.json")
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False)
    return ruta
