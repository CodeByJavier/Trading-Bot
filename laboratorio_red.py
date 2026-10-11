"""
Laboratorio de la red neuronal multimercado (no toca el bot en vivo).

Recorre la historia paso a paso: en cada momento la red decide con lo que sabía entonces y solo
después ve qué pasó. Las carteras de cada tramo empiezan con el mismo dinero ficticio; la red
sigue aprendiendo de forma continua (no se reinicia).

Compara con:
  - Comprar y mantener repartido a partes iguales entre los mismos mercados.
  - Comprar y mantener solo Bitcoin.
  - El bot v2.1 (regla de tendencia en Bitcoin).

Uso:  python laboratorio_red.py   -> laboratorio/RED.md
"""
import json
import os
import time
from datetime import datetime

import fuentes
import laboratorio as lab
import mercados as M
from estratega import CarteraMulti, Datos, Estratega, habilidad

CAPITAL = 1000.0
FIJA, SPREAD = 1.0, 0.001
RUTA = os.path.join(lab.CARPETA, "RED.md")
VARIANTES = [
    ("Una vez al día · 8 mercados", {"intervalo": "1d", "horizonte": 5, "claves": list(M.MERCADOS), "repaso": 16}),
    ("Cada hora · criptos + dólar", {"intervalo": "1h", "horizonte": 24, "claves": M.CON_VELAS_HORARIAS, "repaso": 2}),
    # Anti-comisiones (decidido antes de ver el resultado): revisa el reparto una vez por semana
    # y solo toca una posición si se desvía más de un 15 %
    ("Semanal · 8 mercados", {"intervalo": "1d", "horizonte": 5, "claves": list(M.MERCADOS), "repaso": 16,
                              "cada": 7, "banda": 0.15}),
]
ANOS = list(range(2021, datetime.now().year + 1))


def _cache(nombre, funcion):
    return lab._con_cache(nombre, 12, funcion)


def _p(v):
    return "—" if v is None else f"{v * 100:+.1f} %"


def _mantener_repartido(precios, mercados):
    """Compra a partes iguales al principio y no toca nada más."""
    disponibles = [m for m in mercados if precios.get(m)]
    parte = CAPITAL / len(disponibles)
    return {m: (parte - FIJA) / (precios[m] * (1 + SPREAD)) for m in disponibles}


def _valor_mantener(unidades, precios):
    return sum(q * precios[m] * (1 - SPREAD) - FIJA for m, q in unidades.items())


def simular(nombre, conf, segmentos):
    print(f"\n{nombre}: descargando datos...")
    cantidad = 4000 if conf["intervalo"] == "1d" else int((time.time() * 1000 - lab._ms(lab.APRENDER_DESDE)) / 3600000)
    series = M.descargar(conf["claves"], conf["intervalo"], cantidad, cache=_cache)
    fng = _cache("miedo_codicia", lambda: fuentes.miedo_codicia(0))
    datos = Datos(series, conf["intervalo"], fng)
    est = Estratega(conf["claves"], conf["intervalo"], conf["horizonte"], CAPITAL, FIJA, SPREAD, repaso=conf["repaso"],
                    banda=conf.get("banda", 0.05))
    cada = conf.get("cada", 1)
    momentos = M.rejilla(series, conf["intervalo"])
    carteras, mantener, registros = {}, {}, {s: [] for s, _, _ in segmentos}
    print(f"  {len(momentos)} momentos de decisión; la red aprende desde el primero...")
    inicio = time.time()
    for k, t in enumerate(momentos):
        activos = [(s, a, b) for s, a, b in segmentos if a <= t < b]
        resultado = est.paso_de_tiempo(datos, t, operar=False)
        if not activos:
            continue
        precios = resultado["precios"]
        abiertos = {m for m in conf["claves"] if datos.abierto(m, t)}
        for s, _, _ in activos:
            if s not in carteras:
                carteras[s] = CarteraMulti(CAPITAL, FIJA, SPREAD)
                mantener[s] = (_mantener_repartido(precios, conf["claves"]), precios.get("BTC"))
            cartera = carteras[s]
            if k % cada == 0 or not cartera.operaciones:
                cartera.rebalancear(resultado["objetivo"], precios, abiertos, str(t), t, est.banda)
            unidades, btc0 = mantener[s]
            registros[s].append({"t": t, "bot": cartera.valor(precios), "rep": _valor_mantener(unidades, precios),
                                 "btc": CAPITAL * precios["BTC"] / btc0 if btc0 else None,
                                 "invertido": sum(cartera.pesos(precios).values())})
        if k % 2000 == 0 and k:
            print(f"    {k}/{len(momentos)} ({time.time() - inicio:.0f} s)")

    filas = {}
    for s, a, b in segmentos:
        reg = registros[s]
        if not reg:
            continue
        cartera = carteras[s]
        valores = [CAPITAL] + [r["bot"] for r in reg]
        ia = habilidad([e for e in est.evaluaciones if a <= e["t"] < b], conf["horizonte"])
        filas[s] = {
            "bot": reg[-1]["bot"] / CAPITAL - 1, "repartido": reg[-1]["rep"] / CAPITAL - 1,
            "btc": reg[-1]["btc"] / CAPITAL - 1 if reg[-1]["btc"] else None,
            "caida_bot": lab._caida_maxima(valores),
            "caida_rep": lab._caida_maxima([CAPITAL] + [r["rep"] for r in reg]),
            "operaciones": len(cartera.operaciones), "comisiones": cartera.comisiones_pagadas,
            "invertido": sum(r["invertido"] for r in reg) / len(reg),
            "ic": sum(v["ic"] for v in ia.values()) / len(ia) if ia else None,
            "ic_mercados": ia,
        }
    print(f"  listo en {time.time() - inicio:.0f} s")
    return filas


def tendencia_btc(segmentos):
    velas = M.descargar(["BTC"], "1d", 4000, cache=_cache)["BTC"]
    receta = dict(lab.BASE, intervalo="1d", estrategia="tendencia", tendencia_velas=50, tendencia_margen=0.03,
                  capital=CAPITAL, costes=lab.COSTES["trade_republic"])
    filas = {}
    for s, a, b in segmentos:
        res = lab.probar(velas, receta, a, reinicios=[b])
        m = lab.medir(res, receta, a, b)
        if m:
            filas[s] = m
    return filas


def main():
    ahora = int(time.time() * 1000)
    tramos = [("A", lab._ms(lab.OPERAR_DESDE), lab._ms(lab.CORTE)), ("B", lab._ms(lab.CORTE), ahora)]
    anos = [(str(a), lab._ms(f"{a}-01-01"), lab._ms(f"{a + 1}-01-01") if a < ANOS[-1] else ahora) for a in ANOS]
    resultados = {}
    for nombre, conf in VARIANTES:
        segmentos = tramos + (anos if conf["intervalo"] == "1d" else [])
        resultados[nombre] = simular(nombre, conf, segmentos)
    tendencia = tendencia_btc(tramos + anos)

    md = ["# Laboratorio: red neuronal multimercado", "",
          f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}. Capital ficticio {CAPITAL:.0f} € al empezar "
          "cada tramo, 1 € por orden y 0,1 % de spread. Todo en euros. La red aprende de forma continua; "
          "las carteras de cada tramo empiezan de cero.", "",
          f"- **Tramo A** ({lab.OPERAR_DESDE} → {lab.CORTE}): para elegir la frecuencia.",
          f"- **Tramo B** ({lab.CORTE} → hoy): validación. Es la estimación honesta.",
          "- **IC**: correlación entre lo que la red prevé y lo que pasa (media de los mercados). "
          "0 = no acierta más que el azar; 0,05-0,10 ya es mucho en mercados financieros.", ""]
    for tramo in ("A", "B"):
        md += [f"## Tramo {tramo}", "",
               "| Estrategia | Resultado | Caída máx. | Operaciones | Comisiones | Invertido de media | IC de la red |",
               "|---|---:|---:|---:|---:|---:|---:|"]
        for nombre, filas in resultados.items():
            f = filas.get(tramo)
            if f:
                md.append(f"| **Red: {nombre}** | **{_p(f['bot'])}** | {f['caida_bot'] * 100:.0f} % | {f['operaciones']} | "
                          f"{f['comisiones']:.0f} € | {f['invertido'] * 100:.0f} % | "
                          f"{'—' if f['ic'] is None else f'{f['ic']:+.3f}'} |")
        for nombre, filas in resultados.items():
            f = filas.get(tramo)
            if f:
                md.append(f"| Comprar y mantener repartido ({nombre.split('·')[1].strip()}) | {_p(f['repartido'])} | "
                          f"{f['caida_rep'] * 100:.0f} % | — | — | 100 % | — |")
        f = next(iter(resultados.values())).get(tramo)
        md.append(f"| Comprar y mantener solo Bitcoin | {_p(f['btc'])} | — | 1 | 1 € | 100 % | — |")
        t = tendencia.get(tramo)
        if t:
            md.append(f"| Bot v2.1 (tendencia en Bitcoin) | {_p(t['bot'])} | {t['caida_bot'] * 100:.0f} % | "
                      f"{t['operaciones']} | {t['comisiones']:.0f} € | {t['tiempo_dentro'] * 100:.0f} % | — |")
        md.append("")

    md += ["## ¿Acierta la red en cada mercado? (tramo B)", "",
           "| Mercado | " + " | ".join(n for n, _ in VARIANTES) + " |", "|---|" + "---:|" * len(VARIANTES)]
    for clave in M.MERCADOS:
        fila = []
        for nombre, _ in VARIANTES:
            ic = resultados[nombre].get("B", {}).get("ic_mercados", {}).get(clave)
            fila.append("—" if not ic else f"IC {ic['ic']:+.3f} (z {ic['z']:+.1f}), dirección {ic['acierto'] * 100:.0f} %")
        md.append(f"| {M.nombre(clave)} | " + " | ".join(fila) + " |")

    diaria = resultados[VARIANTES[-1][0]]
    md += ["", f"## Año a año (red: {VARIANTES[-1][0]})", "",
           "| | " + " | ".join(str(a) for a in ANOS) + " | Todo encadenado |", "|---|" + "---:|" * (len(ANOS) + 1)]
    for etiqueta, clave, fuente in (("**Red neuronal**", "bot", diaria), ("Comprar y mantener repartido", "repartido", diaria),
                                    ("Solo Bitcoin", "btc", diaria)):
        valores = [fuente.get(str(a), {}).get(clave) for a in ANOS]
        md.append(f"| {etiqueta} | " + " | ".join(_p(v) for v in valores) +
                  f" | **{_p(lab._encadenar(v for v in valores if v is not None))}** |")
    valores = [tendencia.get(str(a), {}).get("bot") for a in ANOS]
    md.append("| Bot v2.1 (tendencia en Bitcoin) | " + " | ".join(_p(v) for v in valores) +
              f" | **{_p(lab._encadenar(v for v in valores if v is not None))}** |")
    md += ["", "| Caída máxima | " + " | ".join(str(a) for a in ANOS) + " |", "|---|" + "---:|" * len(ANOS)]
    for etiqueta, clave in (("**Red neuronal**", "caida_bot"), ("Comprar y mantener repartido", "caida_rep")):
        md.append(f"| {etiqueta} | " + " | ".join(
            "—" if str(a) not in diaria else f"{diaria[str(a)][clave] * 100:.0f} %" for a in ANOS) + " |")
    md.append("")

    os.makedirs(lab.CARPETA, exist_ok=True)
    with open(RUTA, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(md))
    with open(os.path.join(lab.CARPETA, "red.json"), "w", encoding="utf-8") as archivo:
        json.dump({"resultados": resultados, "tendencia": tendencia}, archivo, ensure_ascii=False, indent=1, default=str)
    print(f"\nInforme: {RUTA}")


if __name__ == "__main__":
    main()
