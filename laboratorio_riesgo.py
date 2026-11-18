"""
¿Cuánto dinero meter en cada compra? ¿Mejoran la regla de tendencia el funding o el Fear & Greed?

Prueba, sobre la regla del bot (media de 50 días ±3 %, velas diarias de Bitcoin en euros, 1.000 €,
1 € por orden y 0,1 % de spread), varias formas de decidir el TAMAÑO de cada compra y dos filtros
con datos de mercado. Sin mirar al futuro: cada día decide con lo que se sabía al cierre.

Reglas fijadas ANTES de ver los resultados:
  - Entre los CANDIDATOS se elige el de mejor ratio de Sharpe en el tramo A (jun 2024 – jul 2025).
  - Se valida en el tramo B (ago 2025 – hoy) y año a año desde 2021: solo merece la pena si en B
    también mejora a la versión actual (Sharpe más alto o caída claramente menor sin ganar menos).
  - Los ILUSTRATIVOS no se eligen: enseñan qué pasa al cambiar una cifra (robustez) o al invertir menos.

Uso:  python laboratorio_riesgo.py   -> laboratorio/RIESGO.md
"""
import math
import os
import time
from datetime import datetime

import indicadores
import laboratorio as lab
import riesgo

CAPITAL, FIJA, SPREAD = 1000.0, 1.0, 0.001
DIAS_TENDENCIA, MARGEN = 50, 0.03
DIAS_VOL = 30                 # volatilidad de los últimos 30 días
FUNDING_ALTO = 0.0003         # 0,03 % cada 8 h (el triple de lo normal): muchos apostando a subidas con préstamo
CODICIA_EXTREMA = 75          # Fear & Greed por encima de 75 = "codicia extrema" según alternative.me
REAJUSTE_DIAS, REAJUSTE_BANDA = 7, 0.25
RUTA = os.path.join(lab.CARPETA, "RIESGO.md")

CANDIDATOS = [
    ("Actual: todo el dinero en cada compra", {}),
    ("Tamaño según volatilidad (objetivo 40 % anual)", {"tam": ("vol", 0.40)}),
    ("Ídem, reajustando cada semana", {"tam": ("vol", 0.40), "reajuste": True}),
    ("Riesgo fijo: perder como mucho un 2 % hasta la salida", {"tam": ("riesgo", 0.02)}),
    ("Filtro funding: no compra si los futuros están muy apalancados", {"filtro": "funding"}),
    ("Filtro Fear & Greed: no compra con codicia extrema", {"filtro": "fng"}),
]
ILUSTRATIVOS = [
    ("Siempre la mitad del dinero (50 %)", {"tam": ("fijo", 0.5)}),
    ("Volatilidad, objetivo 30 %", {"tam": ("vol", 0.30)}),
    ("Volatilidad, objetivo 50 %", {"tam": ("vol", 0.50)}),
    ("Riesgo fijo del 1 %", {"tam": ("riesgo", 0.01)}),
    ("Riesgo fijo del 3 %", {"tam": ("riesgo", 0.03)}),
]


def _vol_anual(c, i):
    r = [math.log(c[k] / c[k - 1]) for k in range(i - DIAS_VOL + 1, i + 1)]
    m = sum(r) / len(r)
    return math.sqrt(sum((x - m) ** 2 for x in r) / (len(r) - 1) * 365)


def _fraccion(receta, velas, c, i):
    tipo, valor = receta.get("tam", ("fijo", 1.0))
    if tipo == "fijo":
        return valor
    if tipo == "vol":
        return min(1.0, valor / _vol_anual(c, i))
    # riesgo: cuánto caería el precio hasta el nivel de salida de hoy (media × 0,97)
    salida = indicadores.media(velas, i, DIAS_TENDENCIA) * (1 - MARGEN)
    return min(1.0, valor / max(0.01, 1 - salida / c[i]))


def _filtro_ok(receta, vela):
    filtro = receta.get("filtro")
    if filtro == "funding":
        return vela.get("funding_medio") is None or vela["funding_medio"] <= FUNDING_ALTO
    if filtro == "fng":
        return vela.get("fng") is None or vela["fng"] <= CODICIA_EXTREMA
    return True


def simular(velas, receta, desde, hasta):
    """Cartera nueva de 1.000 € entre `desde` y `hasta`. Devuelve métricas del tramo."""
    c = [v["cierre"] for v in velas]
    efectivo, cantidad, dia_compra = CAPITAL, 0.0, None
    ops = comisiones = 0
    valores, expuesto = [CAPITAL], []

    def mover(euros, precio):  # euros > 0 compra, < 0 vende; devuelve unidades compradas/vendidas
        nonlocal efectivo, ops, comisiones
        ops += 1
        comisiones += FIJA
        if euros > 0:
            efectivo -= euros
            return (euros - FIJA) / (precio * (1 + SPREAD))
        unidades = -euros / (precio * (1 - SPREAD))
        efectivo += -euros - FIJA
        return -unidades

    for i in range(len(velas)):
        if not desde <= velas[i]["t"] < hasta or i < DIAS_TENDENCIA + DIAS_VOL:
            continue
        p = c[i]
        dentro = cantidad > 0
        quiere = indicadores.tendencia_alcista(velas, i, DIAS_TENDENCIA, MARGEN, dentro)
        if quiere and not dentro and _filtro_ok(receta, velas[i]):
            gasto = min(efectivo, _fraccion(receta, velas, c, i) * efectivo)
            if gasto > 2 * FIJA:
                cantidad += mover(gasto, p)
                dia_compra = i
        elif not quiere and dentro:
            efectivo += cantidad * p * (1 - SPREAD) - FIJA
            ops += 1
            comisiones += FIJA
            cantidad = 0.0
        elif dentro and receta.get("reajuste") and (i - dia_compra) % REAJUSTE_DIAS == 0:
            total = efectivo + cantidad * p * (1 - SPREAD)
            objetivo = _fraccion(receta, velas, c, i) * total
            actual = cantidad * p
            euros = min(objetivo - actual, efectivo) if objetivo > actual else objetivo - actual
            if abs(objetivo - actual) > REAJUSTE_BANDA * actual and abs(euros) > 20 * FIJA:
                cantidad += mover(euros, p)
        valor = efectivo + (cantidad * p * (1 - SPREAD) - FIJA if cantidad > 0 else 0.0)
        valores.append(valor)
        expuesto.append(cantidad * p / valor if valor > 0 else 0)

    m = riesgo.metricas(valores, horas_por_punto=24)
    return dict(m, operaciones=ops, comisiones=comisiones,
                expuesto=sum(expuesto) / len(expuesto) if expuesto else 0)


def mantener(velas, desde, hasta):
    v = [x for x in velas if desde <= x["t"] < hasta]
    cantidad = (CAPITAL - FIJA) / (v[0]["cierre"] * (1 + SPREAD))
    return riesgo.metricas([CAPITAL] + [cantidad * x["cierre"] * (1 - SPREAD) - FIJA for x in v],
                           horas_por_punto=24)


def _p(x):
    return f"{x * 100:+.1f} %"


def _s(x):
    return "—" if x is None else f"{x:+.2f}".replace(".", ",")


def main():
    print("Laboratorio de tamaño y filtros (no toca el bot en vivo)")
    velas = lab.cargar_datos("1d")
    ahora = int(time.time() * 1000)
    tramos = {"A": (lab._ms(lab.OPERAR_DESDE), lab._ms(lab.CORTE)), "B": (lab._ms(lab.CORTE), ahora)}
    anos = list(range(lab.ANOS_DESDE, datetime.now().year + 1))
    limites = [lab._ms(f"{a}-01-01") for a in anos] + [ahora]
    todos = [(n, r, True) for n, r in CANDIDATOS] + [(n, r, False) for n, r in ILUSTRATIVOS]

    filas = []
    for nombre, receta, candidato in todos:
        print(" ", nombre)
        filas.append({"nombre": nombre, "candidato": candidato,
                      **{t: simular(velas, receta, *rango) for t, rango in tramos.items()},
                      "anos": {a: simular(velas, receta, limites[k], limites[k + 1]) for k, a in enumerate(anos)}})
    ref = {t: mantener(velas, *rango) for t, rango in tramos.items()}
    ref_anos = {a: mantener(velas, limites[k], limites[k + 1]) for k, a in enumerate(anos)}

    actual = filas[0]
    elegido = max((f for f in filas if f["candidato"]), key=lambda f: f["A"]["sharpe"] or -99)
    md = ["# ¿Cuánto meter en cada compra? Tamaño de posición y filtros de mercado", "",
          f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} · Bitcoin en euros, velas diarias · "
          f"{CAPITAL:.0f} € ficticios al empezar cada tramo · 1 € por orden y 0,1 % de spread · "
          "la regla de entrada y salida es siempre la del bot (media de 50 días ±3 %).", "",
          "## Cómo leer esto", "",
          "- **Sharpe**: ganancia por cada unidad de riesgo (anualizado). Cuanto más alto, mejor. Es el criterio "
          "para elegir, fijado antes de ver los resultados.",
          "- **Caída máx.**: la peor bajada desde un máximo. **Peor día**: la mayor pérdida en un día.",
          "- **Invertido**: qué parte del dinero estuvo de media dentro de Bitcoin (el resto, en efectivo sin intereses).",
          f"- Tamaño **según volatilidad**: invierte objetivo ÷ volatilidad de los últimos {DIAS_VOL} días "
          "(máximo el 100 %). Si Bitcoin está muy nervioso, compra menos.",
          "- **Riesgo fijo**: compra lo justo para que, si el precio cae hasta el nivel de salida de ese día "
          "(media × 0,97), se pierda ese % del dinero. Ojo: el bot vende al cierre del día, así que puede perder algo más.",
          f"- **Filtro funding**: no compra si en los futuros de Bitcoin la mayoría paga más de un "
          f"{FUNDING_ALTO * 100:.2f} % cada 8 h por apostar a subidas (media de 3 días). "
          f"**Filtro Fear & Greed**: no compra si el índice está por encima de {CODICIA_EXTREMA}.", ""]
    for t, titulo in (("A", "Tramo A (elegir)"), ("B", "Tramo B (validar)")):
        r = ref[t]
        md += [f"## {titulo}", "",
               "| Variante | Resultado | Sharpe | Caída máx. | Peor día | Volatilidad | Invertido | Operaciones |",
               "|---|---:|---:|---:|---:|---:|---:|---:|",
               f"| **Comprar y mantener** | {_p(r['rentabilidad'])} | {_s(r['sharpe'])} | {r['caida_maxima'] * 100:.0f} % | "
               f"{r['peor_dia'] * 100:.1f} % | {r['volatilidad'] * 100:.0f} % | 100 % | 1 |"]
        for f in filas:
            m = f[t]
            marca = "" if f["candidato"] else " *(ilustrativo)*"
            md.append(f"| {f['nombre']}{marca} | {_p(m['rentabilidad'])} | {_s(m['sharpe'])} | "
                      f"{m['caida_maxima'] * 100:.0f} % | {m['peor_dia'] * 100:.1f} % | {m['volatilidad'] * 100:.0f} % | "
                      f"{m['expuesto'] * 100:.0f} % | {m['operaciones']} |")
        md.append("")

    md += [f"## Año a año ({anos[0]}–{anos[-1]}, el último incompleto)", "",
           "Resultado del año / caída máxima del año.", "",
           "| Variante | " + " | ".join(str(a) for a in anos) + " | Todo encadenado | Años con mejor Sharpe que la actual |",
           "|---|" + "---:|" * len(anos) + "---:|:---:|",
           "| **Comprar y mantener** | " + " | ".join(
               f"{_p(ref_anos[a]['rentabilidad'])} / {ref_anos[a]['caida_maxima'] * 100:.0f} %" for a in anos) +
           f" | {_p(math.prod(1 + ref_anos[a]['rentabilidad'] for a in anos) - 1)} | — |"]
    for f in filas:
        mejores = sum((f["anos"][a]["sharpe"] or -99) > (actual["anos"][a]["sharpe"] or -99) for a in anos)
        md.append(f"| {f['nombre']} | " + " | ".join(
            f"{_p(f['anos'][a]['rentabilidad'])} / {f['anos'][a]['caida_maxima'] * 100:.0f} %" for a in anos) +
            f" | {_p(math.prod(1 + f['anos'][a]['rentabilidad'] for a in anos) - 1)} | "
            f"{'—' if f is actual else f'{mejores}/{len(anos)}'} |")

    a, b, b0 = elegido["A"], elegido["B"], actual["B"]
    mejora_b = (b["sharpe"] or -99) > (b0["sharpe"] or -99)
    md += ["", "## Veredicto", "",
           f"La mejor en el tramo A (por Sharpe) fue **{elegido['nombre']}**: {_p(a['rentabilidad'])}, "
           f"Sharpe {_s(a['sharpe'])}, caída máxima {a['caida_maxima'] * 100:.0f} %.", "",
           f"En el tramo B, que no se usó para elegir: {_p(b['rentabilidad'])}, Sharpe {_s(b['sharpe'])}, caída máxima "
           f"{b['caida_maxima'] * 100:.0f} % (la versión actual: {_p(b0['rentabilidad'])}, Sharpe {_s(b0['sharpe'])}, "
           f"caída {b0['caida_maxima'] * 100:.0f} %).", "",
           f"- ¿Mejora el Sharpe de la versión actual en el tramo B? {'✅ Sí' if mejora_b else '❌ No'}",
           "- Recuerda: el Sharpe de un año o año y medio tiene mucho margen de error; lo que cuenta es que la "
           "mejora se repita en B y en la mayoría de los años.", ""]
    with open(RUTA, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(md))
    print(f"\nElegida en A: {elegido['nombre']} · B: {_p(b['rentabilidad'])} (Sharpe {_s(b['sharpe'])}) "
          f"vs actual {_p(b0['rentabilidad'])} (Sharpe {_s(b0['sharpe'])})\nInforme: {RUTA}")


if __name__ == "__main__":
    main()
