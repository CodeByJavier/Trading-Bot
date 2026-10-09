"""
Mide si el cerebro aprende algo útil y lo deja por escrito.

Cada vez que el bot aprende de un resultado, antes guarda dos predicciones hechas
SIN conocer el resultado:
  - la del cerebro
  - la de un "adivino ingenuo" que siempre dice lo que suele pasar
Si el cerebro no se equivoca menos que el adivino, no está aprendiendo nada útil.

Archivos que genera (los puedes leer tú y también Claude):
  - INFORME_APRENDIZAJE.md   informe legible con el veredicto
  - datos_bot/diario.jsonl   una línea por día con métricas y pesos del cerebro
"""
import json
import math
import os
from datetime import datetime, timedelta

import config

# Predicciones independientes mínimas para opinar. Como cada predicción mira HORIZONTE velas
# hacia delante y se solapan, cuentan como total / HORIZONTE.
MINIMO_INDEPENDIENTES = 30
RUTA_DIARIO = os.path.join(config.CARPETA_DATOS, "diario.jsonl")
RUTA_INFORME = os.path.join(config.CARPETA_PROYECTO, "INFORME_APRENDIZAJE.md")

VEREDICTOS = {
    "pocos_datos": ("⏳", "Pocos datos todavía", "Aún no hay suficientes predicciones independientes (unas 30) para opinar."),
    "aprende": ("✅", "Aprende algo útil", "Se equivoca menos que el adivino ingenuo y es muy improbable que sea suerte."),
    "indicios": ("🟡", "Indicios, sin confirmar", "Va algo mejor que el adivino ingenuo, pero todavía podría ser suerte."),
    "no_aprende": ("⚪", "No supera al adivino", "Sus predicciones no son mejores que decir siempre lo que suele pasar."),
    "peor": ("🔴", "Peor que el adivino", "Se equivoca más que el adivino ingenuo: lo que aprende le confunde."),
}


def dia_de(t):
    return datetime.fromtimestamp(t / 1000).strftime("%Y-%m-%d")


def resumir(evaluaciones, horizonte=None):
    """Métricas de un grupo de predicciones ya evaluadas ({p, n, y})."""
    horizonte = horizonte or config.HORIZONTE
    total = len(evaluaciones)
    if total == 0:
        return None
    aciertos = sum((e["p"] >= 0.5) == bool(e["y"]) for e in evaluaciones) / total
    aciertos_ingenuo = sum((e["n"] >= 0.5) == bool(e["y"]) for e in evaluaciones) / total
    errores = [(e["p"] - e["y"]) ** 2 for e in evaluaciones]
    errores_ingenuo = [(e["n"] - e["y"]) ** 2 for e in evaluaciones]
    brier, brier_ingenuo = sum(errores) / total, sum(errores_ingenuo) / total
    habilidad = 1 - brier / brier_ingenuo if brier_ingenuo > 0 else 0.0

    # ¿La mejora es real o suerte? Las predicciones se solapan (miran `horizonte`
    # velas hacia delante), así que cuentan como total/horizonte muestras independientes.
    mejoras = [a - b for a, b in zip(errores_ingenuo, errores)]
    media = sum(mejoras) / total
    varianza = sum((m - media) ** 2 for m in mejoras) / max(1, total - 1)
    error_tipico = math.sqrt(varianza / max(1.0, total / horizonte))
    z = media / error_tipico if error_tipico > 0 else 0.0

    if total / horizonte < MINIMO_INDEPENDIENTES:
        veredicto = "pocos_datos"
    elif z >= 2:
        veredicto = "aprende"
    elif z > 0:
        veredicto = "indicios"
    elif z > -2:
        veredicto = "no_aprende"
    else:
        veredicto = "peor"
    return {"n": total, "aciertos": round(aciertos, 4), "aciertos_ingenuo": round(aciertos_ingenuo, 4),
            "brier": round(brier, 5), "brier_ingenuo": round(brier_ingenuo, 5),
            "habilidad": round(habilidad, 4), "z": round(z, 2), "veredicto": veredicto}


def periodos(estado):
    """Resúmenes por periodo, del más reciente al más largo."""
    evaluaciones = estado.get("evaluaciones", [])
    resultado = []
    if evaluaciones:
        fin = evaluaciones[-1]["t"]
        for nombre, dias in (("Últimos 30 días", 30), ("Últimos 90 días", 90)):
            grupo = [e for e in evaluaciones if e["t"] > fin - dias * 86400000]
            resultado.append((nombre, resumir(grupo)))
        resultado.append(("Desde el inicio (en directo)", resumir(evaluaciones)))
    resultado.append(("Preentrenamiento (historia previa)", estado.get("preentrenamiento")))
    return [(nombre, r) for nombre, r in resultado if r]


def veredicto(estado):
    """Devuelve (clave del veredicto, periodos). Se basa en los últimos 90 días en directo:
    menos da demasiados vaivenes y el total tarda mucho en reflejar mejoras."""
    lineas = periodos(estado)
    principal = next((r for nombre, r in lineas if nombre == "Últimos 90 días"), None)
    return (principal["veredicto"] if principal else "pocos_datos"), lineas


def actualizar_diario(estado, cerebro, cartera):
    """Al cambiar de día, añade al diario una línea con el resumen del día anterior.

    Se guía por las predicciones ya evaluadas (no por la última vela), así el día
    se cierra cuando ya se conoce el resultado de todas sus predicciones.
    """
    if not estado["historial"] or not estado.get("evaluaciones"):
        return
    hoy = dia_de(estado["evaluaciones"][-1]["t"])
    dia = estado.get("dia_diario")
    if dia is None:
        estado["dia_diario"] = hoy
        return
    if dia == hoy:
        return

    del_dia = [h for h in estado["historial"] if dia_de(h["t"]) == dia]
    fecha_ops = datetime.strptime(dia, "%Y-%m-%d").strftime("%d/%m/%Y")
    entrada = {
        "fecha": dia,
        "version": config.VERSION_MODELO,
        "pausado": config.PAUSADO,
        "umbrales": [config.UMBRAL_COMPRA, config.UMBRAL_VENTA],
        "lecciones": cerebro.lecciones,
        "dia": resumir([e for e in estado.get("evaluaciones", []) if dia_de(e["t"]) == dia]),
        "acumulado": resumir(estado.get("evaluaciones", [])),
        "valor_bot": round(del_dia[-1]["bot"], 2) if del_dia else None,
        "valor_referencia": round(del_dia[-1]["referencia"], 2) if del_dia else None,
        "operaciones": sum(1 for o in cartera.operaciones if o["fecha"].startswith(fecha_ops)),
        "pesos": {n: round(w, 4) for n, w in zip(cerebro.nombres, cerebro.pesos)},
        "sesgo": round(cerebro.sesgo, 4),
    }
    os.makedirs(config.CARPETA_DATOS, exist_ok=True)
    with open(RUTA_DIARIO, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(entrada, ensure_ascii=False) + "\n")
    estado["dia_diario"] = hoy


def leer_diario():
    if not os.path.exists(RUTA_DIARIO):
        return []
    with open(RUTA_DIARIO, encoding="utf-8") as archivo:
        return [json.loads(linea) for linea in archivo if linea.strip()]


def _pct(v):
    return "-" if v is None else f"{v * 100:.1f} %"


def escribir_informe(estado, cerebro, cartera):
    clave, lineas_periodos = veredicto(estado)
    icono, titulo, explicacion = VEREDICTOS[clave]
    diario = leer_diario()
    evaluaciones = estado.get("evaluaciones", [])
    creado = datetime.strptime(estado["creado"], "%d/%m/%Y %H:%M")
    minutos = {"15m": 15, "1h": 60, "4h": 240, "1d": 1440}.get(config.INTERVALO, 60)
    dias_minimos = math.ceil(MINIMO_INDEPENDIENTES * config.HORIZONTE * minutos / 1440)
    proxima = creado + timedelta(days=max(21, dias_minimos))
    while proxima < datetime.now():
        proxima += timedelta(days=30)

    md = [
        "# Informe de aprendizaje del bot",
        "",
        f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')} · Moneda: {estado['simbolo']} · "
        f"Versión del modelo: {config.VERSION_MODELO} · Simulación iniciada: {estado['creado']}",
        "",
        f"## {icono} Veredicto: {titulo}",
        "",
        explicacion,
        "",
        ("**Quién decide ahora:** la regla de tendencia (media de "
         f"{config.TENDENCIA_VELAS} días, margen {config.TENDENCIA_MARGEN * 100:.0f} %). La IA está **en prácticas**: "
         "aprende y se la evalúa, pero no compra ni vende hasta que demuestre que mejora los resultados."
         if config.ESTRATEGIA == "tendencia" else f"**Quién decide ahora:** estrategia `{config.ESTRATEGIA}`."),
        "",
        (f"**De qué aprende la IA:** {', '.join(estado.get('mercados_ia', [estado['simbolo']]))}. "
         f"Se la evalúa prediciendo {estado['simbolo']}, el mercado que opera el bot."),
        "",
        "## ¿Cómo se mide?",
        "",
        "Antes de conocer cada resultado se guardan dos predicciones de *\"¿subirá lo suficiente para pagar "
        "las comisiones?\"*: la del cerebro y la de un **adivino ingenuo**, que siempre responde el porcentaje "
        "de subidas recientes.",
        "",
        "- **Habilidad**: cuánto menos se equivoca el cerebro que el adivino (error cuadrático medio). "
        "Mayor que 0 % = mejor que el adivino; 0 % o menos = no aporta nada.",
        "- **z**: lo segura que es esa mejora. Por encima de 2, es muy improbable que sea suerte.",
        "",
        "| Periodo | Predicciones | Aciertos cerebro | Aciertos adivino | Habilidad | z | Veredicto |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for nombre, r in lineas_periodos:
        md.append(f"| {nombre} | {r['n']} | {_pct(r['aciertos'])} | {_pct(r['aciertos_ingenuo'])} | "
                  f"{r['habilidad'] * 100:+.1f} % | {r['z']:+.2f} | {VEREDICTOS[r['veredicto']][1]} |")

    historial = estado["historial"]
    if historial:
        u = historial[-1]
        capital = config.CAPITAL_INICIAL
        md += ["", "## Resultado de la cartera ficticia", "",
               f"- Bot: **{u['bot']:.2f} €** ({(u['bot'] / capital - 1) * 100:+.1f} %)",
               f"- Comprar y mantener: **{u['referencia']:.2f} €** ({(u['referencia'] / capital - 1) * 100:+.1f} %)",
               f"- Operaciones: {len(cartera.operaciones)} · Comisiones pagadas: {cartera.comisiones_pagadas:.2f} €"]

    md += ["", "## Evolución por semanas", "",
           "Una semana sola es poco para juzgar: lo importante es la tendencia de varias semanas seguidas.", ""]
    semanas = {}
    for e in evaluaciones:
        fecha = datetime.fromtimestamp(e["t"] / 1000)
        lunes = (fecha - timedelta(days=fecha.weekday())).strftime("%d/%m/%Y")
        semanas.setdefault(lunes, []).append(e)
    if semanas:
        md += ["| Semana del | Versión | Predicciones | Habilidad | z | Veredicto | Bot al final | Referencia al final |",
               "|---|---|---:|---:|---:|---|---:|---:|"]
        for lunes, grupo in list(semanas.items())[-12:]:
            r = resumir(grupo)
            ultimo_t = grupo[-1]["t"]
            valor = next((h for h in reversed(historial) if h["t"] <= ultimo_t), None)
            bot_final = f"{valor['bot']:.2f} €" if valor else "-"
            ref_final = f"{valor['referencia']:.2f} €" if valor else "-"
            versiones = ", ".join(sorted({e.get("v", "?") for e in grupo}))
            md.append(f"| {lunes} | {versiones} | {r['n']} | {r['habilidad'] * 100:+.1f} % | {r['z']:+.2f} | "
                      f"{VEREDICTOS[r['veredicto']][1]} | {bot_final} | {ref_final} |")
    else:
        md.append("Aparecerá en cuanto haya predicciones evaluadas (unas horas después de arrancar).")

    md += ["", "## Lo que ha aprendido (pesos del cerebro)", "",
           "Si un peso cambia mucho de signo de una semana a otra, el cerebro está persiguiendo ruido.", "",
           "| Indicador | Peso al empezar el diario | Peso ahora |", "|---|---:|---:|"]
    inicio = diario[0]["pesos"] if diario else {}
    for nombre, peso in zip(cerebro.nombres, cerebro.pesos):
        anterior = inicio.get(nombre)
        md.append(f"| {nombre} | {'-' if anterior is None else f'{anterior:+.3f}'} | {peso:+.3f} |")

    md += ["", "## ¿Cuándo revisar y retocar?", "",
           f"- **Próxima revisión recomendada: {proxima.strftime('%d/%m/%Y')}**. "
           f"Llevamos {len(evaluaciones)} predicciones evaluadas en directo.",
           f"- No toques nada antes de {max(21, dias_minimos)} días: con menos datos cualquier "
           "conclusión es ruido.",
           "- Después, revisa **una vez al mes**. Cambia **una sola cosa** cada vez, sube "
           "`VERSION_MODELO` en `config.py` y apunta el cambio en `CAMBIOS.md`.",
           "- Si tras 2-3 meses ninguna versión llega a \"Aprende algo útil\", lo más probable es que "
           "no haya patrón aprovechable con estos indicadores: es un resultado válido, no un fallo.",
           "", "## Para revisar con Claude", "",
           "Pídele a Claude que lea este archivo, `datos_bot/diario.jsonl` y `CAMBIOS.md` del repositorio "
           "(antes, `git pull`). Con eso tiene la historia completa para proponer el siguiente retoque.",
           ""]
    with open(RUTA_INFORME, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(md))
    return clave
