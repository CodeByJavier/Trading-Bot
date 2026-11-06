"""
¿Habría ganado más un bot más activo? Prueba varias estrategias activas con Bitcoin (velas de 1 h)
en el último mes real y en CADA periodo de 4 semanas desde 2024, con 1.000 € y 1 € por operación.

Todas deciden al cierre de cada hora con lo que se sabía entonces (sin mirar al futuro), salvo
"El adivino", que hace trampa a propósito: sabe el futuro, para mostrar qué es "lo que se podría
haber ganado" visto a posteriori.

Uso:  python laboratorio_activo.py   -> laboratorio/ACTIVO.md
"""
import os
import time
from datetime import datetime, timezone

import laboratorio as lab
from datos import descargar_velas

CAPITAL, FIJA, SPREAD = 1000.0, 1.0, 0.001
HORA = 3600000
RUTA = os.path.join(lab.CARPETA, "ACTIVO.md")
INICIO_BOT = "2026-10-10"


def _media(c, i, n):
    return sum(c[i - n + 1: i + 1]) / n


def _rsi(c, i, n=14):
    sub = baj = 0.0
    for k in range(i - n + 1, i + 1):
        d = c[k] - c[k - 1]
        sub, baj = (sub + d, baj) if d > 0 else (sub, baj - d)
    return 50.0 if sub + baj == 0 else 100 * sub / (sub + baj)


# Cada estrategia: función(cierres, i, dentro) -> True si quiere estar dentro tras la vela i
ESTRATEGIAS = {
    "Media de 24 h (muy activa)": lambda c, i, d: c[i] > _media(c, i, 24),
    "Cruce de medias 12 h / 48 h": lambda c, i, d: _media(c, i, 12) > _media(c, i, 48),
    "Ruptura de máximos de 3 días": lambda c, i, d: (c[i] >= max(c[i - 72:i])) if not d else (c[i] > min(c[i - 24:i])),
    "Rebote (RSI bajo 30, vende sobre 55)": lambda c, i, d: (_rsi(c, i) < 30) if not d else (_rsi(c, i) < 55),
    "Media de 7 días": lambda c, i, d: c[i] > _media(c, i, 168),
    "Bot actual (media de 50 días ±3 %)": None,  # se calcula con velas diarias, como en vivo
}


def simular(cierres, tiempos, desde, hasta, quiere):
    """Cartera de 1.000 € que entra y sale según `quiere`. Devuelve (rentabilidad, operaciones)."""
    euros, cantidad, ops = CAPITAL, 0.0, 0
    indices = [i for i, t in enumerate(tiempos) if desde <= t < hasta and i >= 1200]
    for i in indices:
        dentro = cantidad > 0
        q = quiere(i, dentro)
        if q and not dentro and euros > 2 * FIJA:
            cantidad = (euros - FIJA) / (cierres[i] * (1 + SPREAD)); euros = 0.0; ops += 1
        elif not q and dentro:
            euros = cantidad * cierres[i] * (1 - SPREAD) - FIJA; cantidad = 0.0; ops += 1
    final = euros + (cantidad * cierres[indices[-1]] * (1 - SPREAD) - FIJA if cantidad else 0.0)
    return final / CAPITAL - 1, ops


def main():
    print("Descargando velas de 1 hora de Bitcoin...")
    cantidad = int((time.time() * 1000 - lab._ms("2023-10-01")) / HORA)
    velas = descargar_velas("BTCEUR", "1h", cantidad)
    cierres = [v["cierre"] for v in velas]
    tiempos = [v["cierre_t"] + 1 for v in velas]  # momento de la decisión: cierre de la vela

    # Bot actual: tendencia con cierres diarios (00:00 UTC), mantenida durante el día
    diario = {}
    for i, t in enumerate(tiempos):
        if t % 86400000 == 0:
            diario[t] = i
    dias = sorted(diario)
    estado_tendencia = {}
    dentro = False
    for k, t in enumerate(dias):
        if k >= 50:
            m = sum(cierres[diario[x]] for x in dias[k - 49: k + 1]) / 50
            p = cierres[diario[t]]
            dentro = p > m * (0.97 if dentro else 1.03)
        estado_tendencia[t] = dentro
    tendencia_por_hora = []
    ultimo = False
    for t in tiempos:
        ultimo = estado_tendencia.get(t, ultimo)
        tendencia_por_hora.append(ultimo)

    funciones = {}
    for nombre, regla in ESTRATEGIAS.items():
        if regla is None:
            funciones[nombre] = lambda i, d: tendencia_por_hora[i]
        else:
            funciones[nombre] = (lambda r: lambda i, d: r(cierres, i, d))(regla)
    funciones["Comprar y mantener"] = lambda i, d: True
    # El adivino: sabe si dentro de 24 h el precio estará más de un 0,4 % arriba (imposible en la realidad)
    funciones["🔮 El adivino (sabe el futuro: imposible)"] = (
        lambda i, d: i + 24 < len(cierres) and cierres[i + 24] > cierres[i] * 1.004)

    ahora = tiempos[-1] + 1
    inicio_bot = lab._ms(INICIO_BOT)
    md = ["# ¿Habría ganado más un bot más activo?", "",
          f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}. Bitcoin en euros, velas de 1 hora, "
          f"{CAPITAL:.0f} € ficticios, 1 € por operación y 0,1 % de spread. Cada estrategia decide al cierre de cada "
          "hora con lo que se sabía entonces. \"El adivino\" hace trampa (conoce el futuro) para mostrar lo que "
          "parece \"que se podría haber ganado\" mirando la gráfica a posteriori.", "",
          f"## El último mes real (desde el {INICIO_BOT}, cuando arrancó el bot)", "",
          "| Estrategia | Resultado | Operaciones |", "|---|---:|---:|"]
    filas_mes = []
    for nombre, f in funciones.items():
        r, ops = simular(cierres, tiempos, inicio_bot, ahora, f)
        filas_mes.append((r, nombre, ops))
    for r, nombre, ops in sorted(filas_mes, reverse=True):
        md.append(f"| {nombre} | **{r * 100:+.1f} %** ({CAPITAL * r:+.0f} €) | {ops} |")

    # Todos los periodos de 4 semanas desde 2024 (empezando cada semana)
    ventanas = []
    t = lab._ms("2024-01-01")
    while t + 28 * 86400000 <= ahora:
        ventanas.append((t, t + 28 * 86400000))
        t += 7 * 86400000
    md += ["", f"## Cada periodo de 4 semanas desde enero de 2024 ({len(ventanas)} periodos)", "",
           "Un solo mes no demuestra nada: puede salir bien por suerte. Aquí cada estrategia se repite en todos "
           "los periodos de 4 semanas (uno nuevo cada semana).", "",
           "| Estrategia | Mes típico (mediana) | Mejor mes | Peor mes | Meses que gana a mantener | Operaciones al mes |",
           "|---|---:|---:|---:|---:|---:|"]
    mantener = [simular(cierres, tiempos, a, b, funciones["Comprar y mantener"])[0] for a, b in ventanas]
    for nombre, f in funciones.items():
        res = [simular(cierres, tiempos, a, b, f) for a, b in ventanas]
        rs = sorted(r for r, _ in res)
        gana = sum(r > m for (r, _), m in zip(res, mantener))
        ops = sum(o for _, o in res) / len(res)
        md.append(f"| {nombre} | {rs[len(rs) // 2] * 100:+.1f} % | {rs[-1] * 100:+.1f} % | {rs[0] * 100:+.1f} % | "
                  f"{gana}/{len(res)} ({gana / len(res) * 100:.0f} %) | {ops:.0f} |")
        print(f"  {nombre}: mediana {rs[len(rs) // 2] * 100:+.1f} %, gana a mantener {gana}/{len(res)}")
    md.append("")
    with open(RUTA, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(md))
    print(f"Informe: {RUTA}")


if __name__ == "__main__":
    main()
