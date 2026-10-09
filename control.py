"""
Acciones de control del bot. Lo usa el formulario "Controlar el bot" de GitHub,
pero también funciona en tu PC.

Uso:
  python control.py pausar
  python control.py reanudar
  python control.py vender_y_pausar
  python control.py cambiar_umbrales --umbral-compra 0.6 --umbral-venta 0.45
  python control.py reiniciar_simulacion [--capital 200] [--simbolo ETHEUR]
"""
import argparse
import json
import os
import re
import sys

import bot
import config
from datos import descargar_velas

ACCIONES = ["pausar", "reanudar", "vender_y_pausar", "cambiar_umbrales", "reiniciar_simulacion"]


def numero(texto, nombre, minimo, maximo):
    if texto in (None, ""):
        return None
    try:
        valor = float(texto.replace(",", "."))
    except ValueError:
        sys.exit(f"'{texto}' no es un número válido para {nombre}.")
    if not minimo <= valor <= maximo:
        sys.exit(f"{nombre} debe estar entre {minimo} y {maximo} (has puesto {valor}).")
    return valor


def main():
    parser = argparse.ArgumentParser(description="Controla el bot simulado.")
    parser.add_argument("accion", choices=ACCIONES)
    parser.add_argument("--umbral-compra", default="")
    parser.add_argument("--umbral-venta", default="")
    parser.add_argument("--capital", default="")
    parser.add_argument("--simbolo", default="")
    args = parser.parse_args()

    if args.accion == "reiniciar_simulacion":
        cambios = {"PAUSADO": False}
        capital = numero(args.capital, "El capital", 10, 1_000_000)
        if capital is not None:
            cambios["CAPITAL_INICIAL"] = capital
        simbolo = args.simbolo.strip().upper()
        if simbolo:
            if not re.fullmatch(r"[A-Z0-9]{2,10}EUR", simbolo):
                sys.exit(f"'{simbolo}' no parece un par en euros válido (ejemplos: BTCEUR, ETHEUR).")
            cambios["SIMBOLO"] = simbolo
        previo = None
        if os.path.exists(bot.RUTA_ESTADO):
            with open(bot.RUTA_ESTADO, encoding="utf-8") as archivo:
                previo = json.load(archivo)
        carpeta = bot.archivar(previo)
        config.aplicar_ajustes(cambios)
        estado, cerebro, cartera = bot.crear_estado(
            f"Simulación reiniciada a mano" + (f"; la anterior se guardó en {carpeta}" if carpeta else ""))
        bot.ciclo(estado, cerebro, cartera)
        bot.guardar(estado, cerebro, cartera)
        print("Simulación reiniciada.")
        return

    estado, cerebro, cartera = bot.cargar_o_crear()

    if args.accion == "pausar":
        config.aplicar_ajustes({"PAUSADO": True})
        bot.anotar_evento(estado, "Bot pausado: sigue aprendiendo, pero no opera")
    elif args.accion == "reanudar":
        config.aplicar_ajustes({"PAUSADO": False})
        estado["ultima_tendencia_t"] = None  # que revise la regla de tendencia en la próxima ejecución
        bot.anotar_evento(estado, "Bot reanudado: vuelve a operar")
    elif args.accion == "vender_y_pausar":
        if cartera.en_posicion:
            vela = descargar_velas(config.SIMBOLO, config.INTERVALO, 1)[-1]
            operacion = cartera.vender(vela["cierre"], bot.fecha_de(vela))
            bot.anotar_operacion(operacion)
            estado["compra_t"] = None
            bot.anotar_evento(estado, f"Venta manual a {vela['cierre']:,.2f} € "
                                      f"({operacion['resultado']:+.2f} €) y pausa")
        else:
            bot.anotar_evento(estado, "Pausa (no tenía nada que vender)")
        config.aplicar_ajustes({"PAUSADO": True})
    elif args.accion == "cambiar_umbrales":
        compra = numero(args.umbral_compra, "El umbral de compra", 0.01, 0.99)
        venta = numero(args.umbral_venta, "El umbral de venta", 0.01, 0.99)
        compra = config.UMBRAL_COMPRA if compra is None else compra
        venta = config.UMBRAL_VENTA if venta is None else venta
        if venta >= compra:
            sys.exit("El umbral de venta tiene que ser menor que el de compra.")
        config.aplicar_ajustes({"UMBRAL_COMPRA": compra, "UMBRAL_VENTA": venta})
        nota = "" if config.ESTRATEGIA != "tendencia" else " (solo afectan si la IA decide; ahora decide la tendencia)"
        bot.anotar_evento(estado, f"Umbrales cambiados: compra {compra:.0%}, venta {venta:.0%}{nota}")

    bot.guardar(estado, cerebro, cartera)
    print(f"Hecho: {args.accion}.")


if __name__ == "__main__":
    main()
