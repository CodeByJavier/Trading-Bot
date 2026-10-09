"""
Prueba el bot con los últimos meses de precios reales, hora a hora, como si
estuviera funcionando en directo: primero decide y solo después ve lo que pasó.

Uso:  python backtest.py
"""
import os
from datetime import datetime

import aprendizaje
import config
from cerebro import Cerebro
from datos import descargar_velas
from indicadores import HISTORIA_NECESARIA, NOMBRES, caracteristicas
from informe import generar_informe
from simulador import Cartera, decidir, valor_comprar_y_mantener


def fecha_de(vela):
    return datetime.fromtimestamp((vela["cierre_t"] + 1) / 1000).strftime("%d/%m/%Y %H:%M")


def main():
    print(f"Descargando {config.VELAS_BACKTEST} velas de {config.SIMBOLO} ({config.INTERVALO})...")
    velas = descargar_velas(config.SIMBOLO, config.INTERVALO, config.VELAS_BACKTEST)
    h = config.HORIZONTE
    inicio = HISTORIA_NECESARIA - 1
    inicio_operar = inicio + config.VELAS_CALENTAMIENTO
    if len(velas) <= inicio_operar + h:
        print("No hay suficientes velas. Sube VELAS_BACKTEST o baja VELAS_CALENTAMIENTO.")
        return

    cerebro = Cerebro(NOMBRES, config.TASA_APRENDIZAJE)
    cartera = Cartera(config.CAPITAL_INICIAL, config.COMISION_FIJA,
                      config.COMISION_PORCENTAJE, config.SPREAD)
    precio_inicio = velas[inicio_operar]["cierre"]
    serie_bot, serie_ref = [], []
    evaluaciones = []

    for i in range(inicio, len(velas)):
        # 1) Aprender de lo que pasó con la predicción de hace `h` velas
        j = i - h
        if j >= inicio:
            subio = velas[i]["cierre"] / velas[j]["cierre"] - 1 > config.MOVIMIENTO_MINIMO
            prediccion, ingenua = cerebro.aprender(caracteristicas(velas, j), subio)
            if j >= inicio_operar:
                evaluaciones.append({"p": prediccion, "n": ingenua, "y": int(subio)})

        if i < inicio_operar:
            continue  # calentamiento: solo estudia, no opera

        # 2) Predecir y decidir con la información disponible en ese momento
        precio = velas[i]["cierre"]
        probabilidad = cerebro.predecir(caracteristicas(velas, i))
        accion = decidir(probabilidad, cartera.en_posicion,
                         config.UMBRAL_COMPRA, config.UMBRAL_VENTA)
        if accion == "comprar":
            cartera.comprar(precio, fecha_de(velas[i]))
        elif accion == "vender":
            cartera.vender(precio, fecha_de(velas[i]))

        serie_bot.append(cartera.valor(precio))
        serie_ref.append(valor_comprar_y_mantener(config.CAPITAL_INICIAL, precio_inicio, precio,
                                                  config.COMISION_FIJA, config.SPREAD))

    final_bot, final_ref = serie_bot[-1], serie_ref[-1]
    ventas = [op for op in cartera.operaciones if op["tipo"] == "VENTA"]
    ganadoras = sum(1 for op in ventas if op["resultado"] > 0)
    capital = config.CAPITAL_INICIAL
    medida = aprendizaje.resumir(evaluaciones)

    resumen = [
        ("Periodo probado", f"{fecha_de(velas[inicio_operar])} a {fecha_de(velas[-1])}"),
        ("Capital inicial (ficticio)", f"{capital:.2f} €"),
        ("Valor final del bot", f"{final_bot:.2f} € ({(final_bot / capital - 1) * 100:+.1f} %)"),
        ("Comprar y mantener", f"{final_ref:.2f} € ({(final_ref / capital - 1) * 100:+.1f} %)"),
        ("No hacer nada", f"{capital:.2f} € (+0.0 %)"),
        ("Operaciones (compras + ventas)", len(cartera.operaciones)),
        ("Ventas con ganancia", f"{ganadoras} de {len(ventas)}"),
        ("Comisiones pagadas", f"{cartera.comisiones_pagadas:.2f} €"),
        ("Subida mínima para cubrir costes", f"{config.MOVIMIENTO_MINIMO * 100:.2f} %"),
        ("Versión del modelo", config.VERSION_MODELO),
        ("Aciertos cerebro / adivino ingenuo",
         f"{medida['aciertos'] * 100:.1f} % / {medida['aciertos_ingenuo'] * 100:.1f} %"),
        ("Habilidad frente al adivino (z)", f"{medida['habilidad'] * 100:+.1f} % (z = {medida['z']:+.2f})"),
        ("¿Aprende?", aprendizaje.VEREDICTOS[medida["veredicto"]][1]),
    ]

    print()
    for clave, valor in resumen:
        print(f"  {clave:<42} {valor}")
    print()
    if final_bot > final_ref and final_bot > capital:
        print("  El bot ha ganado a la referencia EN ESTE PERIODO. Puede ser suerte:")
        print("  pruébalo en directo durante semanas antes de sacar conclusiones.")
    else:
        print("  El bot NO ha superado a la referencia en este periodo.")

    os.makedirs(config.CARPETA_DATOS, exist_ok=True)
    ruta = os.path.join(config.CARPETA_DATOS, "informe_backtest.html")
    generar_informe(ruta, f"Backtest {config.SIMBOLO}", serie_bot, serie_ref, resumen,
                    cerebro.lo_aprendido(), cartera.operaciones)
    print(f"\n  Informe con gráfica: {os.path.abspath(ruta)}")


if __name__ == "__main__":
    main()
