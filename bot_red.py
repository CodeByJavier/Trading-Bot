"""
Red neuronal multimercado EN VIVO, con su propio dinero ficticio (aparte del bot principal).

Cada vez que se ejecuta (GitHub lo hace cada hora):
  1. Si ha cerrado un día nuevo, la red aprende de él y prevé los próximos 5 días de cada mercado.
  2. Una vez por semana reparte la cartera según su confianza (solo toca mercados abiertos).
  3. Cada hora anota cuánto vale la cartera con los últimos precios (para ver el movimiento diario).
  4. Guarda todo en datos_red/, publica docs/red.json para el panel y escribe INFORME_RED.md.

La primera vez estudia toda la historia disponible (desde 2020) antes de empezar.

Uso:  python bot_red.py --una-vez
"""
import json
import os
import sys
from datetime import datetime, timezone

import config
import fuentes
import mercados as M
from datos import descargar_velas
from estratega import DIA_MS, HORA_MS, CarteraMulti, Datos, Estratega, habilidad

RUTA_ESTADO = os.path.join(config.CARPETA_RED, "estado.json")
RUTA_PANEL = os.path.join(config.CARPETA_PANEL, "red.json")
RUTA_INFORME = os.path.join(config.CARPETA_PROYECTO, "INFORME_RED.md")
VELAS_DIARIAS = 560      # historia diaria que se descarga en cada ejecución (indicadores + repaso)
MAX_EVALUACIONES = 4000


def _fecha(t_ms):
    return datetime.fromtimestamp(t_ms / 1000).strftime("%d/%m/%Y %H:%M")


def _evento(estado, texto):
    estado.setdefault("eventos", []).append({"fecha": datetime.now().strftime("%d/%m/%Y %H:%M"), "texto": texto})


def _datos(cantidad):
    series = M.descargar(config.RED_MERCADOS, "1d", cantidad)
    try:
        fng = fuentes.miedo_codicia(cantidad + 20)
    except ConnectionError as error:
        print(f"  (aviso) Sin Fear & Greed ({error}).")
        fng = {}
    return Datos(series, "1d", fng)


def precios_actuales(datos):
    """Último precio de cada mercado: el de la última hora en Binance y el último cierre en bolsa."""
    ahora = int(datetime.now(timezone.utc).timestamp() * 1000)
    precios = {}
    for clave in config.RED_MERCADOS:
        _, _, fuente, codigo = M.MERCADOS[clave]
        if fuente == "binance":
            try:
                vela = descargar_velas(codigo, "1h", 1)[-1]
                precios[clave] = 1 / vela["cierre"] if clave == "USD" else vela["cierre"]
                continue
            except (ConnectionError, IndexError):
                pass
        p = datos.precio(clave, ahora)
        if p:
            precios[clave] = p
    return precios


def crear():
    print("Red neuronal: primera vez, estudia toda la historia diaria disponible...")
    datos = _datos(2400)
    est = Estratega(config.RED_MERCADOS, "1d", config.RED_HORIZONTE, config.RED_CAPITAL,
                    config.COMISION_FIJA, config.SPREAD, banda=config.RED_BANDA)
    desde = int(datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)  # antes casi no hay mercados
    momentos = M.rejilla(datos.series, "1d", desde)
    for t in momentos[:-1]:
        est.paso_de_tiempo(datos, t, operar=False)
    ultimo_ano = [e for e in est.evaluaciones if e["t"] >= momentos[-1] - 365 * DIA_MS]
    previo = habilidad(ultimo_ano, config.RED_HORIZONTE)
    est.evaluaciones = []
    print(f"  {est.red.lecciones} lecciones aprendidas.")
    estado = {
        "version": config.RED_VERSION, "mercados": config.RED_MERCADOS,
        "creado": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "ultimo_t": momentos[-2], "ultima_revision_t": None,
        "historial": [], "eventos": [], "preentrenamiento": previo, "referencia": None,
    }
    cartera = CarteraMulti(config.RED_CAPITAL, config.COMISION_FIJA, config.SPREAD)
    _evento(estado, f"Red neuronal v{config.RED_VERSION} creada con {config.RED_CAPITAL:.0f} € ficticios en "
                    f"{len(config.RED_MERCADOS)} mercados ({est.red.lecciones} lecciones de preentrenamiento)")
    return estado, est, cartera, datos


def cargar():
    if not os.path.exists(RUTA_ESTADO):
        return crear()
    with open(RUTA_ESTADO, encoding="utf-8") as archivo:
        estado = json.load(archivo)
    if (estado["version"], estado["mercados"]) != (config.RED_VERSION, config.RED_MERCADOS):
        destino = os.path.join(config.CARPETA_RED, "archivo", f"v{estado['version']}_{datetime.now():%Y-%m-%d_%H%M}")
        os.makedirs(destino, exist_ok=True)
        os.replace(RUTA_ESTADO, os.path.join(destino, "estado.json"))
        estado_nuevo, est, cartera, datos = crear()
        _evento(estado_nuevo, f"Nueva versión de la red: la simulación anterior se guardó en {destino}")
        return estado_nuevo, est, cartera, datos
    est = Estratega.desde_dict(estado.pop("estratega"))
    cartera = CarteraMulti.desde_dict(estado.pop("cartera"))
    return estado, est, cartera, _datos(VELAS_DIARIAS)


def avanzar(estado, est, cartera, datos):
    """Procesa los días nuevos y anota el valor actual. Devuelve True si cambió algo."""
    cambio = False
    nuevos = [t for t in M.rejilla(datos.series, "1d") if t > estado["ultimo_t"]]
    for t in nuevos:
        resultado = est.paso_de_tiempo(datos, t, operar=False)
        estado["ultimo_t"] = t
        cambio = True
        if t != nuevos[-1]:
            continue  # días atrasados: sirven para aprender, no para operar con precios pasados
        estado["objetivo"] = resultado["objetivo"]
        revision = estado.get("ultima_revision_t")
        if not config.PAUSADO and (revision is None or t - revision >= config.RED_CADA_DIAS * DIA_MS):
            abiertos = {m for m in est.claves if datos.abierto(m, t)}
            ops = cartera.rebalancear(resultado["objetivo"], resultado["precios"], abiertos, _fecha(t), t, est.banda)
            estado["ultima_revision_t"] = t
            if ops:
                resumen = ", ".join(f"{'compra' if o['tipo'] == 'COMPRA' else 'venta'} {M.nombre(o['mercado'])}"
                                    for o in ops)
                _evento(estado, f"Revisión semanal: {resumen}")
            else:
                _evento(estado, "Revisión semanal: sin cambios (no vio nada que compense las comisiones)")
    est.evaluaciones = est.evaluaciones[-MAX_EVALUACIONES:]

    precios = precios_actuales(datos)
    if estado.get("referencia") is None and len(precios) == len(est.claves):
        parte = config.RED_CAPITAL / len(precios)
        estado["referencia"] = {m: (parte - config.COMISION_FIJA) / (p * (1 + config.SPREAD)) for m, p in precios.items()}
    hora = int(datetime.now(timezone.utc).timestamp() * 1000) // HORA_MS * HORA_MS
    if not estado["historial"] or estado["historial"][-1]["t"] < hora:
        referencia = estado.get("referencia") or {}
        estado["historial"].append({
            "t": hora, "fecha": _fecha(hora),
            "valor": cartera.valor(precios),
            "referencia": sum(q * precios[m] * (1 - config.SPREAD) - config.COMISION_FIJA
                              for m, q in referencia.items() if m in precios) or config.RED_CAPITAL,
            "invertido": sum(cartera.pesos(precios).values())})
        cambio = True
    estado["precios"] = precios
    return cambio


def exportar(estado, est, cartera, datos):
    precios = estado.get("precios", {})
    ahora = int(datetime.now(timezone.utc).timestamp() * 1000)
    pesos = cartera.pesos(precios) if precios else {}
    hab = habilidad(est.evaluaciones, est.horizonte)
    mercados = []
    for m in est.claves:
        p = precios.get(m)
        ayer, semana = datos.precio(m, ahora - DIA_MS), datos.precio(m, ahora - 7 * DIA_MS)
        mercados.append({
            "clave": m, "nombre": M.nombre(m), "tipo": M.MERCADOS[m][1], "precio": p,
            "cambio_24h": p / ayer - 1 if p and ayer else None, "cambio_7d": p / semana - 1 if p and semana else None,
            "peso": pesos.get(m, 0.0), "objetivo": estado.get("objetivo", {}).get(m, 0.0),
            "prediccion": est.ultima_prediccion.get(m), "abierto": datos.abierto(m, estado["ultimo_t"]),
            "habilidad": hab.get(m),
        })
    revision = estado.get("ultima_revision_t")
    historial = estado["historial"]
    datos_panel = {
        "version": config.RED_VERSION, "creado": estado["creado"],
        "actualizado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "capital": config.RED_CAPITAL, "pausado": config.PAUSADO,
        "valor": historial[-1]["valor"] if historial else config.RED_CAPITAL,
        "referencia": historial[-1]["referencia"] if historial else config.RED_CAPITAL,
        "efectivo": cartera.efectivo, "invertido": sum(pesos.values()),
        "comisiones": cartera.comisiones_pagadas, "umbral": est.umbral, "horizonte": est.horizonte,
        "cada_dias": config.RED_CADA_DIAS, "lecciones": est.red.lecciones,
        "proxima_revision": _fecha(revision + config.RED_CADA_DIAS * DIA_MS) if revision else "en el próximo cierre diario",
        "mercados": mercados,
        "historial": [{"f": h["fecha"], "v": round(h["valor"], 2), "r": round(h["referencia"], 2)} for h in historial[-3000:]],
        "operaciones": [dict(o, nombre=M.nombre(o["mercado"])) for o in cartera.operaciones[-200:]],
        "eventos": estado.get("eventos", [])[-50:],
        "preentrenamiento": estado.get("preentrenamiento"),
    }
    os.makedirs(config.CARPETA_PANEL, exist_ok=True)
    with open(RUTA_PANEL, "w", encoding="utf-8") as archivo:
        json.dump(datos_panel, archivo, ensure_ascii=False)
    return datos_panel


def escribir_informe(d):
    def ic_texto(h):
        return "—" if not h else f"{h['ic']:+.3f} (z {h['z']:+.1f}) · dirección {h['acierto'] * 100:.0f} % · {h['n']} predicciones"
    acierta = [m for m in d["mercados"] if m["habilidad"] and m["habilidad"]["z"] >= 2]
    md = ["# Informe de la red neuronal multimercado", "",
          f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')} · Versión {d['version']} · Creada: {d['creado']}", "",
          f"**Cartera:** {d['valor']:.2f} € (empezó con {d['capital']:.0f} €) · comprar y mantener repartido: "
          f"{d['referencia']:.2f} € · invertido {d['invertido'] * 100:.0f} % · comisiones {d['comisiones']:.0f} €", "",
          "**¿Acierta la dirección?** " + (
              "Sí en " + ", ".join(m["nombre"] for m in acierta) + " (z ≥ 2)." if acierta else
              "Todavía en ningún mercado (hace falta z ≥ 2; en el laboratorio no lo consiguió)."), "",
          "IC = correlación entre lo que prevé y lo que pasa (0 = azar). Sus predicciones miran "
          f"{d['horizonte']} días vista, así que hacen falta meses para juzgarla.", "",
          "| Mercado | Peso ahora | Prevé (5 días) | IC en directo |", "|---|---:|---:|---|"]
    for m in d["mercados"]:
        prevision = "—" if m["prediccion"] is None else f"{m['prediccion'] * 100:+.1f} %"
        md.append(f"| {m['nombre']} | {m['peso'] * 100:.0f} % | {prevision} | {ic_texto(m['habilidad'])} |")
    pre = d.get("preentrenamiento") or {}
    if pre:
        md += ["", "**Con la historia previa (último año antes de empezar):** " + ", ".join(
            f"{M.nombre(m)} IC {v['ic']:+.3f}" for m, v in pre.items())]
    md.append("")
    with open(RUTA_INFORME, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(md))


def guardar(estado, est, cartera, datos):
    os.makedirs(config.CARPETA_RED, exist_ok=True)
    completo = dict(estado, estratega=est.a_dict(), cartera=cartera.a_dict())
    temporal = RUTA_ESTADO + ".tmp"
    with open(temporal, "w", encoding="utf-8") as archivo:
        json.dump(completo, archivo)
    os.replace(temporal, RUTA_ESTADO)
    escribir_informe(exportar(estado, est, cartera, datos))


def main():
    if not config.RED_ACTIVA:
        print("La red neuronal está desactivada (config.RED_ACTIVA).")
        return
    estado, est, cartera, datos = cargar()
    if avanzar(estado, est, cartera, datos) or "--forzar" in sys.argv:
        guardar(estado, est, cartera, datos)
        h = estado["historial"][-1]
        print(f"Red neuronal: cartera {h['valor']:.2f} € | mantener repartido {h['referencia']:.2f} € | "
              f"invertido {h['invertido'] * 100:.0f} % | operaciones {len(cartera.operaciones)}")
    else:
        print("Red neuronal: nada nuevo.")


if __name__ == "__main__":
    main()
