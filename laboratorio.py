"""
Laboratorio: prueba ideas con la historia real SIN tocar el bot en vivo.

Cómo evita engañarse a sí mismo:
  1. Recorre la historia vela a vela: en cada momento decide con lo que sabía entonces
     y solo después ve qué pasó (igual que en directo).
  2. Divide el periodo en dos tramos:
       - Tramo A: para comparar ideas y elegir la mejor.
       - Tramo B: para VALIDAR la elegida. Su resultado en B es la estimación honesta.
     Si una idea solo funciona en A, era casualidad.
  3. Usa siempre los mismos umbrales (no los ajusta para que salga bonito).

Uso:
  python laboratorio.py          ejecuta todos los experimentos y escribe laboratorio/RESULTADOS.md

Para probar una idea nueva, añádela a EXPERIMENTOS (abajo) y vuelve a ejecutarlo.
"""
import json
import os
import time
from datetime import datetime, timezone

import aprendizaje
import config
import fuentes
import indicadores
from cerebro import Cerebro
from datos import descargar_velas
from simulador import Cartera, decidir, respetar_permanencia

CARPETA = os.path.join(config.CARPETA_PROYECTO, "laboratorio")
CACHE = os.path.join(CARPETA, "cache")
RUTA_RESULTADOS = os.path.join(CARPETA, "RESULTADOS.md")

APRENDER_DESDE = "2023-12-01"  # (velas por hora) historia previa para que el cerebro aprenda
OPERAR_DESDE = "2024-06-01"    # desde aquí opera con dinero ficticio
CORTE = "2025-08-01"           # tramo A (elegir) | tramo B (validar)

COSTES = {
    "trade_republic": {"nombre": "1 € por orden", "fija": 1.0, "pct": 0.0, "spread": 0.001},
    "porcentaje": {"nombre": "0,1 % por orden", "fija": 0.0, "pct": 0.001, "spread": 0.0005},
}

# Receta de partida de los experimentos: la v1.0 original. Es fija para que los resultados
# no cambien aunque se modifique config.py.
BASE = {
    "intervalo": "1h", "horizonte": 4, "indicadores": ["precio"], "estrategia": "ia",
    "tendencia_velas": 50, "tendencia_margen": 0.0, "permanencia": 0,
    "umbral_compra": 0.58, "umbral_venta": 0.47, "tasa": 0.01, "capital": 200.0, "costes": "trade_republic",
}

# Cada experimento cambia algo respecto a BASE. Añade aquí tus ideas.
EXPERIMENTOS = [
    ("v1.0 actual (1 h, 4 h vista)", {}),
    ("v1.0 con comisión del 0,1 %", {"costes": "porcentaje"}),
    ("1 h, 24 h vista + Fear & Greed", {"horizonte": 24, "indicadores": ["precio", "sentimiento"]}),
    ("Diario, 5 días vista", {"intervalo": "1d", "horizonte": 5}),
    ("Diario + Fear & Greed", {"intervalo": "1d", "horizonte": 5, "indicadores": ["precio", "sentimiento"]}),
    ("Diario + Fear & Greed + futuros", {"intervalo": "1d", "horizonte": 5,
                                         "indicadores": ["precio", "sentimiento", "futuros"]}),
    ("Tendencia 50 días (sin IA)", {"intervalo": "1d", "estrategia": "tendencia"}),
    ("Tendencia 50 días + IA con Fear & Greed", {"intervalo": "1d", "horizonte": 5, "estrategia": "tendencia_ia",
                                                 "indicadores": ["precio", "sentimiento"]}),
    ("Tendencia 50 días, margen 3 %", {"intervalo": "1d", "estrategia": "tendencia", "tendencia_margen": 0.03}),
    ("1 h, 24 h vista + Fear & Greed, mínimo 24 h dentro",
     {"horizonte": 24, "indicadores": ["precio", "sentimiento"], "permanencia": 24}),
    ("Ídem con comisión del 0,1 %",
     {"horizonte": 24, "indicadores": ["precio", "sentimiento"], "permanencia": 24, "costes": "porcentaje"}),
]

# Variantes para comprobar si una idea es robusta (no se usan para elegir la mejor):
# si solo funciona con una cifra concreta, probablemente sea casualidad.
ROBUSTEZ = [
    ("Tendencia 20 días", {"intervalo": "1d", "estrategia": "tendencia", "tendencia_velas": 20}),
    ("Tendencia 100 días", {"intervalo": "1d", "estrategia": "tendencia", "tendencia_velas": 100}),
    ("Tendencia 200 días", {"intervalo": "1d", "estrategia": "tendencia", "tendencia_velas": 200}),
]
ANOS_DESDE = 2021  # comprobación año a año con velas diarias


def receta_actual():
    """La receta que usa ahora el bot en vivo, sacada de config.py."""
    return {
        "intervalo": config.INTERVALO, "horizonte": config.HORIZONTE, "indicadores": list(config.INDICADORES),
        "estrategia": config.ESTRATEGIA, "tendencia_velas": config.TENDENCIA_VELAS,
        "tendencia_margen": config.TENDENCIA_MARGEN, "permanencia": config.PERMANENCIA_MINIMA,
        "umbral_compra": config.UMBRAL_COMPRA, "umbral_venta": config.UMBRAL_VENTA,
        "tasa": config.TASA_APRENDIZAJE, "capital": config.CAPITAL_INICIAL,
        "costes": {"nombre": "config.py", "fija": config.COMISION_FIJA,
                   "pct": config.COMISION_PORCENTAJE, "spread": config.SPREAD},
    }


def _ms(fecha):
    return int(datetime.strptime(fecha, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)


def _fecha(t_ms):
    return datetime.fromtimestamp(t_ms / 1000).strftime("%d/%m/%Y %H:%M")


# ------------------------------------------------------------------ datos
def _con_cache(nombre, horas, descargar):
    os.makedirs(CACHE, exist_ok=True)
    ruta = os.path.join(CACHE, nombre + ".json")
    if os.path.exists(ruta) and time.time() - os.path.getmtime(ruta) < horas * 3600:
        with open(ruta, encoding="utf-8") as archivo:
            return json.load(archivo)
    datos = descargar()
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo)
    return datos


def cargar_datos(intervalo):
    """Velas desde APRENDER_DESDE (o todas las diarias desde 2020) con Fear & Greed y funding."""
    minutos = {"15m": 15, "1h": 60, "4h": 240, "1d": 1440}[intervalo]
    if intervalo == "1d":
        cantidad = 4000  # toda la historia disponible
    else:
        cantidad = int((time.time() * 1000 - _ms(APRENDER_DESDE)) / 60000 / minutos)
    print(f"  Datos {config.SIMBOLO} {intervalo}...")
    velas = _con_cache(f"velas_{config.SIMBOLO}_{intervalo}", 6,
                       lambda: descargar_velas(config.SIMBOLO, intervalo, cantidad))
    fng = _con_cache("miedo_codicia", 6, lambda: fuentes.miedo_codicia(0))
    tasas = _con_cache("funding", 6, lambda: fuentes.funding(_ms("2019-09-01")))
    return fuentes.enriquecer(velas, fng, [tuple(t) for t in tasas])


# ------------------------------------------------------------------ motor
def probar(velas, receta, operar_desde_t, reinicios=()):
    """Simula la receta vela a vela. Devuelve registros, evaluaciones, operaciones y cerebro.

    En cada momento de `reinicios` la cartera vuelve a empezar con el capital inicial
    (el cerebro conserva lo aprendido). Así cada tramo se mide en igualdad de condiciones.
    """
    anterior_tendencia = config.TENDENCIA_VELAS
    config.TENDENCIA_VELAS = receta["tendencia_velas"]
    try:
        lista = indicadores.expandir(receta["indicadores"])
        h = receta["horizonte"]
        costes = receta["costes"]
        capital = receta["capital"]
        minimo = 2 * costes["fija"] / capital + 2 * costes["pct"] + 2 * costes["spread"]
        usa_ia = receta["estrategia"] != "tendencia"

        inicio = indicadores.historia_necesaria(lista, receta["tendencia_velas"]) - 1
        inicio_operar = next(i for i, v in enumerate(velas) if v["t"] >= operar_desde_t)
        if inicio_operar < inicio + h + 50:
            raise ValueError("No hay historia suficiente antes de empezar a operar.")

        cerebro = Cerebro(indicadores.nombres(lista), receta["tasa"])
        cartera = Cartera(capital, costes["fija"], costes["pct"], costes["spread"])
        registros, evaluaciones, operaciones = [], [], []
        reinicios = sorted(reinicios)
        compra_i = None

        for i in range(inicio, len(velas)):
            j = i - h
            if usa_ia and j >= inicio:
                subio = velas[i]["cierre"] / velas[j]["cierre"] - 1 > minimo
                prediccion, ingenua = cerebro.aprender(indicadores.caracteristicas(velas, j, lista), subio)
                if j >= inicio_operar:
                    evaluaciones.append({"t": velas[j]["t"], "p": prediccion, "n": ingenua, "y": int(subio)})
            if i < inicio_operar:
                continue

            vela = velas[i]
            while reinicios and vela["t"] >= reinicios[0]:
                reinicios.pop(0)
                cartera = Cartera(capital, costes["fija"], costes["pct"], costes["spread"])
                compra_i = None
            precio = vela["cierre"]
            probabilidad = cerebro.predecir(indicadores.caracteristicas(velas, i, lista)) if usa_ia else None
            alcista = indicadores.tendencia_alcista(velas, i, receta["tendencia_velas"],
                                                    receta["tendencia_margen"], cartera.en_posicion)
            accion = decidir(probabilidad, cartera.en_posicion, receta["umbral_compra"], receta["umbral_venta"],
                             receta["estrategia"], alcista)
            accion = respetar_permanencia(accion, None if compra_i is None else i - compra_i,
                                          receta.get("permanencia", 0))
            operacion = None
            if accion == "comprar":
                operacion = cartera.comprar(precio, _fecha(vela["cierre_t"] + 1))
            elif accion == "vender":
                operacion = cartera.vender(precio, _fecha(vela["cierre_t"] + 1))
            if operacion:
                operaciones.append(dict(operacion, t=vela["t"]))
                compra_i = i if operacion["tipo"] == "COMPRA" else None
            registros.append({"t": vela["t"], "precio": precio, "valor": cartera.valor(precio),
                              "dentro": cartera.en_posicion, "prob": probabilidad})
        return {"registros": registros, "evaluaciones": evaluaciones, "operaciones": operaciones,
                "cerebro": cerebro, "cartera": cartera}
    finally:
        config.TENDENCIA_VELAS = anterior_tendencia


def _mantener(capital, costes, precio_inicio, precio_fin):
    """Valor de comprar al principio y no tocar nada, con las mismas comisiones."""
    cantidad = (capital - costes["fija"]) * (1 - costes["pct"]) / (precio_inicio * (1 + costes["spread"]))
    return cantidad * precio_fin * (1 - costes["spread"]) * (1 - costes["pct"]) - costes["fija"]


def _caida_maxima(serie):
    pico, caida = serie[0], 0.0
    for v in serie:
        pico = max(pico, v)
        caida = max(caida, (pico - v) / pico if pico > 0 else 0)
    return caida


def medir(resultado, receta, desde_t, hasta_t):
    """Métricas de un tramo [desde, hasta) que empezó con la cartera reiniciada (ver probar)."""
    dentro = [r for r in resultado["registros"] if desde_t <= r["t"] < hasta_t]
    if not dentro:
        return None
    capital = valor_inicio = receta["capital"]
    precio_inicio = dentro[0]["precio"]
    referencia = [_mantener(capital, receta["costes"], precio_inicio, r["precio"]) for r in dentro]
    valores = [valor_inicio] + [r["valor"] for r in dentro]
    operaciones = [o for o in resultado["operaciones"] if desde_t <= o["t"] < hasta_t]
    evaluaciones = [e for e in resultado["evaluaciones"] if desde_t <= e["t"] < hasta_t]
    return {
        "desde": _fecha(dentro[0]["t"])[:10], "hasta": _fecha(dentro[-1]["t"])[:10],
        "bot": valores[-1] / valor_inicio - 1,
        "mantener": referencia[-1] / capital - 1,
        "caida_bot": _caida_maxima(valores),
        "caida_mantener": _caida_maxima([capital] + referencia),
        "operaciones": len(operaciones),
        "comisiones": sum(o["comision"] for o in operaciones),
        "tiempo_dentro": sum(r["dentro"] for r in dentro) / len(dentro),
        "ia": aprendizaje.resumir(evaluaciones, receta["horizonte"]) if evaluaciones else None,
    }


# ------------------------------------------------------------------ informe
def _p(v):
    return f"{v * 100:+.1f} %"


def _fila(nombre, m):
    ia = m["ia"]
    texto_ia = "— (sin IA)" if ia is None else (
        f"{ia['habilidad'] * 100:+.1f} % (z {ia['z']:+.1f}) {aprendizaje.VEREDICTOS[ia['veredicto']][0]}")
    gana = "✅" if m["bot"] > m["mantener"] else "❌"
    return (f"| {nombre} | **{_p(m['bot'])}** | {_p(m['mantener'])} | {gana} | {m['caida_bot'] * 100:.0f} % / "
            f"{m['caida_mantener'] * 100:.0f} % | {m['operaciones']} | {m['comisiones']:.2f} € | "
            f"{m['tiempo_dentro'] * 100:.0f} % | {texto_ia} |")


CABECERA = ("| Experimento | Bot | Comprar y mantener | ¿Gana a mantener? | Caída máx. bot / mantener | "
            "Operaciones | Comisiones | Tiempo dentro | IA: habilidad (z) |\n"
            "|---|---:|---:|:---:|---:|---:|---:|---:|---|")


def _encadenar(rentabilidades):
    total = 1.0
    for r in rentabilidades:
        total *= 1 + r
    return total - 1


def escribir_informe(filas, robustez, anos):
    elegido = max(filas, key=lambda f: f["A"]["bot"])
    b = elegido["B"]
    rentable = b["bot"] > 0
    gana = b["bot"] > b["mantener"]
    aprende = b["ia"] is not None and b["ia"]["veredicto"] == "aprende"
    a0, b0 = filas[0]["A"], filas[0]["B"]

    md = [
        "# Resultados del laboratorio", "",
        f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} · Moneda: {config.SIMBOLO} · "
        f"Capital ficticio: {config.CAPITAL_INICIAL:.0f} € al empezar cada tramo", "",
        "## Cómo leer esto", "",
        f"- **Tramo A** ({a0['desde']} → {a0['hasta']}): se usa para **elegir** la mejor idea.",
        f"- **Tramo B** ({b0['desde']} → {b0['hasta']}): **validación**. Lo que la idea elegida "
        "consigue aquí es la estimación honesta de cómo le iría en el futuro.",
        "- Cada tramo empieza con el mismo dinero ficticio; el cerebro sí conserva lo aprendido.",
        "- **Caída máxima**: la peor bajada desde un máximo. Mide el riesgo (cuánto llegarías a perder por el camino).",
        "- **IA: habilidad**: mejor que 0 % = predice mejor que el adivino ingenuo; z ≥ 2 = muy improbable que sea suerte.",
        "- Todo con dinero ficticio y precios reales. Se prueban varias ideas a la vez, así que alguna puede "
        "salir bien por azar en un tramo: por eso cuentan el tramo B y la comprobación año a año.", "",
        "## Tramo A (elegir)", "", CABECERA,
    ]
    md += [_fila(f["nombre"], f["A"]) for f in filas]
    md += ["", "## Tramo B (validar)", "", CABECERA]
    md += [_fila(f["nombre"], f["B"]) for f in filas]

    if robustez:
        md += ["", "## Robustez: variantes de la regla de tendencia", "",
               "No se usan para elegir. Sirven para ver si la idea funciona en general o solo con una cifra concreta.",
               "", "| Variante | Tramo A bot | Tramo B bot | Comprar y mantener A / B | Operaciones A+B |",
               "|---|---:|---:|---:|---:|"]
        for f in robustez:
            md.append(f"| {f['nombre']} | {_p(f['A']['bot'])} | {_p(f['B']['bot'])} | "
                      f"{_p(f['A']['mantener'])} / {_p(f['B']['mantener'])} | "
                      f"{f['A']['operaciones'] + f['B']['operaciones']} |")

    if anos:
        primero = next(iter(anos.values()))
        lista_anos = sorted(primero.keys())
        mantener = {a: primero[a]["mantener"] for a in lista_anos}
        md += ["", f"## Año a año (velas diarias, {lista_anos[0]}–{lista_anos[-1]})", "",
               "Cada año empieza con el mismo dinero ficticio. El último año está incompleto.", "",
               "| Estrategia | " + " | ".join(str(a) for a in lista_anos) + " | Todo encadenado | Años que gana a mantener |",
               "|---|" + "---:|" * len(lista_anos) + "---:|:---:|",
               "| **Comprar y mantener** | " + " | ".join(_p(mantener[a]) for a in lista_anos) +
               f" | **{_p(_encadenar(mantener.values()))}** | — |"]
        for nombre, por_ano in anos.items():
            ganados = sum(por_ano[a]["bot"] > por_ano[a]["mantener"] for a in lista_anos)
            md.append(f"| {nombre} | " + " | ".join(_p(por_ano[a]["bot"]) for a in lista_anos) +
                      f" | **{_p(_encadenar(por_ano[a]['bot'] for a in lista_anos))}** | {ganados}/{len(lista_anos)} |")
        md += ["", "| Caída máxima | " + " | ".join(str(a) for a in lista_anos) + " |",
               "|---|" + "---:|" * len(lista_anos),
               "| **Comprar y mantener** | " + " | ".join(
                   f"{primero[a]['caida_mantener'] * 100:.0f} %" for a in lista_anos) + " |"]
        for nombre, por_ano in anos.items():
            md.append(f"| {nombre} | " + " | ".join(f"{por_ano[a]['caida_bot'] * 100:.0f} %" for a in lista_anos) + " |")

    md += ["", "## Veredicto", "",
           f"La mejor idea en el tramo A fue **{elegido['nombre']}** ({_p(elegido['A']['bot'])}).", "",
           f"En el tramo B, que no se usó para elegirla, consiguió **{_p(b['bot'])}** frente a "
           f"{_p(b['mantener'])} de comprar y mantener, con una caída máxima del {b['caida_bot'] * 100:.0f} % "
           f"(mantener: {b['caida_mantener'] * 100:.0f} %).", "",
           f"- ¿Gana dinero en el tramo B? {'✅ Sí' if rentable else '❌ No'}",
           f"- ¿Gana a comprar y mantener en el tramo B? {'✅ Sí' if gana else '❌ No'}",
           f"- ¿Su IA aprende algo útil (z ≥ 2)? "
           f"{'✅ Sí' if aprende else ('— no usa IA' if b['ia'] is None else '❌ No')}", ""]
    os.makedirs(CARPETA, exist_ok=True)
    with open(RUTA_RESULTADOS, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(md))
    with open(os.path.join(CARPETA, "resultados.json"), "w", encoding="utf-8") as archivo:
        json.dump({"tramos": [{"nombre": f["nombre"], "receta": f["receta"], "A": f["A"], "B": f["B"]}
                              for f in filas + robustez],
                   "anos": anos}, archivo, ensure_ascii=False, indent=1)
    return elegido


def _preparar(base, cambios):
    receta = dict(base, **cambios)
    if isinstance(receta["costes"], str):
        receta["costes"] = COSTES[receta["costes"]]
    return receta


def main():
    print("Laboratorio: probando ideas con la historia real (no toca el bot en vivo)\n")
    base = BASE
    datos = {}
    ahora = int(time.time() * 1000)
    filas, robustez, anos = [], [], {}
    lista_anos = list(range(ANOS_DESDE, datetime.now().year + 1))
    todos = [(n, c, False) for n, c in EXPERIMENTOS] + [(n, c, True) for n, c in ROBUSTEZ]

    for numero, (nombre, cambios, es_robustez) in enumerate(todos, 1):
        receta = _preparar(base, cambios)
        if receta["intervalo"] not in datos:
            datos[receta["intervalo"]] = cargar_datos(receta["intervalo"])
        velas = datos[receta["intervalo"]]
        print(f"[{numero}/{len(todos)}] {nombre}...")
        resultado = probar(velas, receta, _ms(OPERAR_DESDE), reinicios=[_ms(CORTE)])
        a = medir(resultado, receta, _ms(OPERAR_DESDE), _ms(CORTE))
        b = medir(resultado, receta, _ms(CORTE), ahora)
        (robustez if es_robustez else filas).append({"nombre": nombre, "receta": receta, "A": a, "B": b})
        print(f"      A: bot {_p(a['bot'])} vs mantener {_p(a['mantener'])}   "
              f"B: bot {_p(b['bot'])} vs mantener {_p(b['mantener'])}   operaciones {a['operaciones']}+{b['operaciones']}")

        if receta["intervalo"] == "1d":
            limites = [_ms(f"{ano}-01-01") for ano in lista_anos] + [ahora]
            por_anos = probar(velas, receta, limites[0], reinicios=limites[1:-1])
            anos[nombre] = {ano: medir(por_anos, receta, limites[k], limites[k + 1])
                            for k, ano in enumerate(lista_anos)}

    elegido = escribir_informe(filas, robustez, anos)
    print(f"\nMejor en el tramo A: {elegido['nombre']}. En el tramo B (validación): "
          f"{_p(elegido['B']['bot'])} vs mantener {_p(elegido['B']['mantener'])}")
    print(f"Informe completo: {RUTA_RESULTADOS}")


if __name__ == "__main__":
    main()
