"""
Muestra cómo va la simulación en directo y genera un informe con gráfica.

Uso:  python estado.py
"""
import json
import os

import config
from cerebro import Cerebro
from informe import generar_informe
from simulador import Cartera

RUTA_ESTADO = os.path.join(config.CARPETA_DATOS, "estado.json")


def main():
    if not os.path.exists(RUTA_ESTADO):
        print("Todavía no hay simulación. Arráncala con: python bot.py")
        return
    with open(RUTA_ESTADO, encoding="utf-8") as archivo:
        estado = json.load(archivo)
    cerebro = Cerebro.desde_dict(estado["cerebro"])
    cartera = Cartera.desde_dict(estado["cartera"])
    historial = estado["historial"]
    if not historial:
        print("El bot aún no ha procesado ninguna vela. Déjalo funcionando un rato.")
        return

    capital = config.CAPITAL_INICIAL
    ultimo = historial[-1]
    ventas = [op for op in cartera.operaciones if op["tipo"] == "VENTA"]
    acierto = cerebro.tasa_acierto()
    resumen = [
        ("Simulación iniciada", estado["creado"]),
        ("Última vela procesada", ultimo["fecha"]),
        ("Velas procesadas en directo", len(historial)),
        ("Precio actual", f'{ultimo["precio"]:,.2f} €'),
        ("Valor del bot", f'{ultimo["bot"]:.2f} € ({(ultimo["bot"] / capital - 1) * 100:+.1f} %)'),
        ("Comprar y mantener", f'{ultimo["referencia"]:.2f} € '
                               f'({(ultimo["referencia"] / capital - 1) * 100:+.1f} %)'),
        ("Posición", "DENTRO (tiene cripto)" if cartera.en_posicion else "FUERA (todo en euros)"),
        ("Operaciones", len(cartera.operaciones)),
        ("Ventas con ganancia", f'{sum(1 for op in ventas if op["resultado"] > 0)} de {len(ventas)}'),
        ("Comisiones pagadas", f"{cartera.comisiones_pagadas:.2f} €"),
        ("Lecciones aprendidas", cerebro.lecciones),
        ("Aciertos recientes", "-" if acierto is None else f"{acierto * 100:.1f} %"),
        ("Aciertos respondiendo siempre lo mismo",
         "-" if acierto is None else f"{cerebro.acierto_sin_pensar() * 100:.1f} %"),
    ]
    for clave, valor in resumen:
        print(f"  {clave:<40} {valor}")
    print("\n  Lo que más pesa en sus decisiones:")
    for nombre, peso, opinion in cerebro.lo_aprendido()[:4]:
        print(f"    {nombre:<36} {peso:+.3f}  ({opinion})")

    ruta = os.path.join(config.CARPETA_DATOS, "informe_bot.html")
    generar_informe(ruta, f"Bot simulado {estado['simbolo']}",
                    [p["bot"] for p in historial], [p["referencia"] for p in historial],
                    resumen, cerebro.lo_aprendido(), cartera.operaciones)
    print(f"\n  Informe con gráfica: {os.path.abspath(ruta)}")


if __name__ == "__main__":
    main()
