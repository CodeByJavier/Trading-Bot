"""
Laboratorio multimercado: ¿mejora el bot si mira varias criptomonedas, el euro/dólar y la bolsa?

Tres experimentos (no tocan el bot en vivo):
  1. IA que aprende de varios mercados a la vez: ¿predice mejor Bitcoin (y cada mercado)
     que aprendiendo de uno solo?
  2. Regla de tendencia en cada mercado, y repartiendo el dinero entre varios
     (con 1 € por orden y con 0,1 %).
  3. ¿Se mueven juntos? Correlaciones y qué hacen los demás cuando Bitcoin se desploma.

Uso:  python multimercado.py      -> laboratorio/MULTIMERCADO.md
"""
import json
import math
import os
import time
import urllib.parse
from collections import deque
from datetime import datetime, timezone

import aprendizaje
import indicadores
import laboratorio as lab
from cerebro import Cerebro
from datos import _pedir, descargar_velas

RUTA = os.path.join(lab.CARPETA, "MULTIMERCADO.md")
URL_YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{codigo}?interval=1d&range=10y"

# nombre -> (tipo, fuente, código)
MERCADOS = {
    "Bitcoin": ("cripto", "binance", "BTCEUR"),
    "Ethereum": ("cripto", "binance", "ETHEUR"),
    "BNB": ("cripto", "binance", "BNBEUR"),
    "XRP": ("cripto", "binance", "XRPEUR"),
    "Euro/dólar": ("divisa", "binance", "EURUSDT"),
    "S&P 500": ("acciones", "yahoo", "SPY"),
    "IBEX 35": ("acciones", "yahoo", "^IBEX"),
}
CRIPTOS = ["Bitcoin", "Ethereum", "BNB", "XRP"]
VEINTICUATRO_SIETE = CRIPTOS + ["Euro/dólar"]  # cotizan 24 h: tienen velas de 1 hora en Binance
TODOS = list(MERCADOS)
MINIMO = 2 * 1.0 / 200 + 2 * 0.001  # subida que cubre comisiones (1 € por orden sobre 200 € + spread)
ANOS = list(range(2021, datetime.now().year + 1))


# ------------------------------------------------------------------ datos
def _yahoo(codigo):
    resultado = _pedir(URL_YAHOO.format(codigo=urllib.parse.quote(codigo)))["chart"]["result"][0]
    cotizaciones = resultado["indicators"]["quote"][0]
    velas = []
    for k, segundos in enumerate(resultado["timestamp"]):
        cierre = cotizaciones["close"][k]
        if cierre is None:
            continue
        t = segundos * 1000
        velas.append({"t": t, "apertura": cotizaciones["open"][k] or cierre,
                      "maximo": cotizaciones["high"][k] or cierre, "minimo": cotizaciones["low"][k] or cierre,
                      "cierre": cierre, "volumen": cotizaciones["volume"][k] or 0, "cierre_t": t + 8 * 3600000})
    return velas


def cargar(nombre, intervalo):
    _, fuente, codigo = MERCADOS[nombre]
    clave = f"mm_{codigo.replace('^', '')}_{intervalo}"
    if fuente == "yahoo":
        return lab._con_cache(clave, 12, lambda: _yahoo(codigo)) if intervalo == "1d" else None
    if intervalo == "1d":
        cantidad = 4000
    else:
        cantidad = int((time.time() * 1000 - lab._ms(lab.APRENDER_DESDE)) / 3600000)
    return lab._con_cache(clave, 12, lambda: descargar_velas(codigo, intervalo, cantidad))


# ------------------------------------------------------------------ experimento 1: IA multimercado
def _caracteristicas_de(velas, h):
    lista = indicadores.expandir(["precio"])
    inicio = indicadores.historia_necesaria(lista) - 1
    return [indicadores.caracteristicas(velas, j, lista) if j >= inicio else None
            for j in range(len(velas) - h)], inicio


def ia_varios(series, cache, entrenar, h):
    """Una sola IA aprende, en orden temporal, de todos los mercados de `entrenar`.

    La predicción ingenua se calcula POR MERCADO (porcentaje de subidas recientes de ese mercado),
    para no darle ventaja a la IA por mezclar mercados con costumbres distintas.
    """
    eventos = []
    for m in entrenar:
        x, inicio = cache[m]
        eventos += [(series[m][i]["cierre_t"], m, i) for i in range(inicio + h, len(series[m]))]
    eventos.sort()
    cerebro = Cerebro(indicadores.nombres(["precio"]), 0.01)
    recientes = {m: deque(maxlen=500) for m in entrenar}
    evaluaciones = {m: [] for m in entrenar}
    desde = lab._ms(lab.OPERAR_DESDE)
    for _, m, i in eventos:
        v, j = series[m], i - h
        subio = v[i]["cierre"] / v[j]["cierre"] - 1 > MINIMO
        prediccion, _ = cerebro.aprender(cache[m][0][j], subio)
        r = recientes[m]
        ingenua = sum(r) / len(r) if r else 0.5
        r.append(int(subio))
        if v[j]["t"] >= desde:
            evaluaciones[m].append({"t": v[j]["t"], "p": prediccion, "n": ingenua, "y": int(subio)})
    corte = lab._ms(lab.CORTE)
    return {m: {"A": aprendizaje.resumir([e for e in ev if e["t"] < corte], h),
                "B": aprendizaje.resumir([e for e in ev if e["t"] >= corte], h)}
            for m, ev in evaluaciones.items()}


# ------------------------------------------------------------------ experimento 2: tendencia
def tendencia_por_anos(velas, capital, costes):
    receta = dict(lab.BASE, intervalo="1d", estrategia="tendencia", tendencia_velas=50,
                  tendencia_margen=0.03, capital=capital, costes=costes)
    ahora = int(time.time() * 1000)
    limites = [lab._ms(f"{a}-01-01") for a in ANOS] + [ahora]
    resultado = lab.probar(velas, receta, limites[0], reinicios=limites[1:-1])
    return resultado, receta, limites


def cartera(mercados, series, costes):
    """Reparte 200 € a partes iguales entre `mercados`; cada año vuelve a empezar con 200 €."""
    capital = 200.0 / len(mercados)
    partes = {m: tendencia_por_anos(series[m], capital, costes) for m in mercados}
    limites = next(iter(partes.values()))[2]
    anual = {}
    for k, ano in enumerate(ANOS):
        desde, hasta = limites[k], limites[k + 1]
        eventos = []
        for m, (res, receta, _) in partes.items():
            registros = [r for r in res["registros"] if desde <= r["t"] < hasta]
            if not registros:
                continue
            p0 = registros[0]["precio"]
            eventos += [(r["t"], m, r["valor"], lab._mantener(capital, costes, p0, r["precio"])) for r in registros]
        eventos.sort()
        bot = {m: capital for m in mercados}
        mantener = {m: capital for m in mercados}
        serie_bot, serie_mantener = [200.0], [200.0]
        for _, m, valor, ref in eventos:
            bot[m], mantener[m] = valor, ref
            serie_bot.append(sum(bot.values()))
            serie_mantener.append(sum(mantener.values()))
        anual[ano] = {"bot": serie_bot[-1] / 200 - 1, "mantener": serie_mantener[-1] / 200 - 1,
                      "caida_bot": lab._caida_maxima(serie_bot), "caida_mantener": lab._caida_maxima(serie_mantener),
                      "operaciones": sum(1 for m, (res, _, _) in partes.items()
                                         for o in res["operaciones"] if desde <= o["t"] < hasta)}
    return anual


# ------------------------------------------------------------------ experimento 3: correlaciones
def _cierres_por_dia(velas):
    return {datetime.fromtimestamp(v["t"] / 1000, timezone.utc).strftime("%Y-%m-%d"): v["cierre"]
            for v in velas if v["t"] >= lab._ms(f"{ANOS[0]}-01-01")}


def _rendimientos_comunes(a, b):
    dias = sorted(set(a) & set(b))
    ra = [a[d2] / a[d1] - 1 for d1, d2 in zip(dias, dias[1:])]
    rb = [b[d2] / b[d1] - 1 for d1, d2 in zip(dias, dias[1:])]
    return ra, rb, dias[1:]


def _correlacion(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return cov / math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))


# ------------------------------------------------------------------ informe
def _p(v):
    return "—" if v is None else f"{v * 100:+.1f} %"


def _habilidad(r):
    if not r:
        return "—"
    return f"{r['habilidad'] * 100:+.1f} % (z {r['z']:+.1f}) {aprendizaje.VEREDICTOS[r['veredicto']][0]}"


def main():
    print("Laboratorio multimercado (no toca el bot en vivo)\n")
    md = ["# Laboratorio multimercado", "",
          f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}. Todo con dinero ficticio y precios reales.", "",
          "Mercados: " + ", ".join(f"**{m}**" for m in TODOS) + ". El euro/dólar sale del par EUR/USDT de Binance "
          "(sigue al euro/dólar y cotiza 24 h). Las acciones son el ETF SPY (S&P 500) y el índice IBEX 35, "
          "con velas diarias de Yahoo Finance. Cada mercado se mide en su propia moneda (sin cambio de divisa).", ""]

    # ---------- 1. IA multimercado
    print("Experimento 1: IA que aprende de varios mercados")
    md += ["## 1. ¿Aprende mejor la IA si estudia varios mercados a la vez?", "",
           "Una sola IA aprende de todos los mercados de la variante, en orden temporal. Se mide su "
           "**habilidad** (cuánto mejor predice que el adivino ingenuo de ese mismo mercado) en el "
           f"tramo A ({lab.OPERAR_DESDE} → {lab.CORTE}) y en el tramo B ({lab.CORTE} → hoy). "
           "z ≥ 2 = muy improbable que sea suerte.", ""]
    for intervalo, h, variantes, texto in [
        ("1h", 24, [("Solo Bitcoin", ["Bitcoin"]), ("4 criptomonedas", CRIPTOS),
                    ("4 criptos + euro/dólar", VEINTICUATRO_SIETE)],
         "Velas de 1 hora, predice 24 h vista"),
        ("1d", 5, [("Solo Bitcoin", ["Bitcoin"]), ("4 criptomonedas", CRIPTOS),
                   ("Todo: criptos + euro/dólar + acciones", TODOS)],
         "Velas diarias, predice 5 velas vista (en acciones, 5 sesiones)")]:
        mercados = sorted({m for _, lista in variantes for m in lista}, key=TODOS.index)
        series = {m: cargar(m, intervalo) for m in mercados}
        cache = {m: _caracteristicas_de(series[m], h) for m in mercados}
        resultados = {}
        for nombre, lista in variantes:
            print(f"  [{intervalo}] {nombre}...")
            resultados[nombre] = ia_varios(series, cache, lista, h)
        md += [f"### {texto}", "", "**Habilidad prediciendo Bitcoin según de qué aprende:**", "",
               "| Aprende de | Tramo A | Tramo B |", "|---|---:|---:|"]
        for nombre, _ in variantes:
            r = resultados[nombre]["Bitcoin"]
            md.append(f"| {nombre} | {_habilidad(r['A'])} | {_habilidad(r['B'])} |")
        ultima = variantes[-1][0]
        md += ["", f"**Habilidad en cada mercado ({ultima}):**", "",
               "| Mercado | Tramo A | Tramo B |", "|---|---:|---:|"]
        for m, r in resultados[ultima].items():
            md.append(f"| {m} | {_habilidad(r['A'])} | {_habilidad(r['B'])} |")
        md.append("")

    # ---------- 2. Tendencia en varios mercados
    print("Experimento 2: regla de tendencia en varios mercados")
    diarias = {m: cargar(m, "1d") for m in TODOS}
    tr, pct = lab.COSTES["trade_republic"], lab.COSTES["porcentaje"]
    md += ["## 2. Regla de tendencia (50 días, margen 3 %) en cada mercado", "",
           "Cada mercado por separado con 200 € ficticios y 1 € por orden; cada año vuelve a empezar. "
           "En acciones, \"50 días\" son 50 sesiones de bolsa (unas 10 semanas).", "",
           "| Mercado | Tendencia 2021–hoy | Comprar y mantener | Años que gana a mantener | Caída máx. media tendencia / mantener |",
           "|---|---:|---:|:---:|---:|"]
    for m in TODOS:
        res, receta, limites = tendencia_por_anos(diarias[m], 200.0, tr)
        anos = [lab.medir(res, receta, limites[k], limites[k + 1]) for k in range(len(ANOS))]
        anos = [a for a in anos if a]
        bot = lab._encadenar(a["bot"] for a in anos)
        mantener = lab._encadenar(a["mantener"] for a in anos)
        gana = sum(a["bot"] > a["mantener"] for a in anos)
        cb = sum(a["caida_bot"] for a in anos) / len(anos)
        cm = sum(a["caida_mantener"] for a in anos) / len(anos)
        md.append(f"| {m} | **{_p(bot)}** | {_p(mantener)} | {gana}/{len(anos)} | {cb * 100:.0f} % / {cm * 100:.0f} % |")
        print(f"  {m}: tendencia {_p(bot)} vs mantener {_p(mantener)}")

    carteras = [("Solo Bitcoin (200 €)", ["Bitcoin"]),
                ("4 criptos (50 € cada una)", CRIPTOS),
                ("Mezcla: Bitcoin + Ethereum + euro/dólar + S&P 500 + IBEX (40 € cada uno)",
                 ["Bitcoin", "Ethereum", "Euro/dólar", "S&P 500", "IBEX 35"])]
    md += ["", "### Repartiendo los 200 € entre varios mercados (regla de tendencia en cada uno)", "",
           "| Cartera | Comisión | " + " | ".join(str(a) for a in ANOS) +
           " | Todo encadenado | Peor caída de un año |", "|---|---|" + "---:|" * len(ANOS) + "---:|---:|"]
    for nombre, lista in carteras:
        for etiqueta, costes in (("1 €", tr), ("0,1 %", pct)):
            anual = cartera(lista, diarias, costes)
            fila_bot = " | ".join(_p(anual[a]["bot"]) for a in ANOS)
            md.append(f"| {nombre} | {etiqueta} | {fila_bot} | **{_p(lab._encadenar(anual[a]['bot'] for a in ANOS))}** | "
                      f"{max(anual[a]['caida_bot'] for a in ANOS) * 100:.0f} % |")
            print(f"  {nombre} ({etiqueta}): {_p(lab._encadenar(anual[a]['bot'] for a in ANOS))}")
        anual = cartera(lista, diarias, tr)
        md.append(f"| ↳ misma cartera, comprar y mantener | 1 € | " +
                  " | ".join(_p(anual[a]["mantener"]) for a in ANOS) +
                  f" | {_p(lab._encadenar(anual[a]['mantener'] for a in ANOS))} | "
                  f"{max(anual[a]['caida_mantener'] for a in ANOS) * 100:.0f} % |")

    # ---------- 3. Correlaciones
    print("Experimento 3: ¿se mueven juntos?")
    cierres = {m: _cierres_por_dia(diarias[m]) for m in TODOS}
    md += ["", f"## 3. ¿Se mueven juntos? (rendimientos diarios {ANOS[0]}–hoy)", "",
           "Correlación: +1 = se mueven igual; 0 = no tienen relación; −1 = van al revés. "
           "Para diversificar sirven los mercados con correlación baja.", "",
           "| | " + " | ".join(TODOS) + " |", "|---|" + "---:|" * len(TODOS)]
    for a in TODOS:
        fila = []
        for b in TODOS:
            ra, rb, _ = _rendimientos_comunes(cierres[a], cierres[b])
            fila.append(f"{_correlacion(ra, rb):+.2f}")
        md.append(f"| **{a}** | " + " | ".join(fila) + " |")
    md += ["", "**Cuando Bitcoin cae más de un 5 % en un día, ¿qué hacen los demás ese mismo día?**", "",
           "| Mercado | Días comparados | Rendimiento medio ese día |", "|---|---:|---:|"]
    for m in TODOS[1:]:
        rbtc, rm, _ = _rendimientos_comunes(cierres["Bitcoin"], cierres[m])
        caidas = [y for x, y in zip(rbtc, rm) if x < -0.05]
        if caidas:
            md.append(f"| {m} | {len(caidas)} | {_p(sum(caidas) / len(caidas))} |")
    md.append("")

    with open(RUTA, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(md))
    print(f"\nInforme: {RUTA}")


if __name__ == "__main__":
    main()
