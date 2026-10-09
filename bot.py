"""
Bot de trading SIMULADO: precios reales, dinero ficticio.

- La primera vez estudia los últimos meses de precios (preentrenamiento).
- Después, cada vez que cierra una vela: aprende de lo que pasó, decide y
  "opera" con dinero ficticio.
- Guarda todo en datos_bot/ y actualiza el panel (docs/datos.json).

Uso:
  python bot.py            se queda funcionando en tu PC (Ctrl+C para parar)
  python bot.py --una-vez  procesa las velas nuevas y termina (lo usa GitHub cada hora)
"""
import csv
import json
import os
import sys
import time
from datetime import datetime

import aprendizaje
import config
from cerebro import Cerebro
from datos import descargar_velas
from indicadores import HISTORIA_NECESARIA, NOMBRES, caracteristicas
from panel import exportar_panel
from simulador import Cartera, decidir, valor_comprar_y_mantener

RUTA_ESTADO = os.path.join(config.CARPETA_DATOS, "estado.json")
RUTA_OPERACIONES = os.path.join(config.CARPETA_DATOS, "operaciones.csv")
VELAS_POR_CICLO = HISTORIA_NECESARIA + config.HORIZONTE + 200


def fecha_de(vela):
    return datetime.fromtimestamp((vela["cierre_t"] + 1) / 1000).strftime("%d/%m/%Y %H:%M")


def cubre_costes(precio_antes, precio_despues):
    return precio_despues / precio_antes - 1 > config.MOVIMIENTO_MINIMO


def anotar_evento(estado, texto):
    estado.setdefault("eventos", []).append(
        {"fecha": datetime.now().strftime("%d/%m/%Y %H:%M"), "texto": texto})


def guardar(estado, cerebro, cartera):
    os.makedirs(config.CARPETA_DATOS, exist_ok=True)
    estado["cerebro"] = cerebro.a_dict()
    estado["cartera"] = cartera.a_dict()
    temporal = RUTA_ESTADO + ".tmp"
    with open(temporal, "w", encoding="utf-8") as archivo:
        json.dump(estado, archivo)
    os.replace(temporal, RUTA_ESTADO)
    aprendizaje.escribir_informe(estado, cerebro, cartera)
    exportar_panel(estado, cerebro, cartera)


def anotar_operacion(op):
    nuevo = not os.path.exists(RUTA_OPERACIONES)
    with open(RUTA_OPERACIONES, "a", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo, delimiter=";")
        if nuevo:
            escritor.writerow(["fecha", "tipo", "precio", "cantidad", "euros", "comision", "resultado"])
        escritor.writerow([op["fecha"], op["tipo"], f'{op["precio"]:.2f}', f'{op["cantidad"]:.8f}',
                           f'{op["euros"]:.2f}', f'{op["comision"]:.2f}',
                           "" if op["resultado"] is None else f'{op["resultado"]:.2f}'])


def crear_estado():
    print(f"Primera vez: estudiando {config.VELAS_PREENTRENAMIENTO} velas de "
          f"{config.SIMBOLO} ({config.INTERVALO})...")
    velas = descargar_velas(config.SIMBOLO, config.INTERVALO, config.VELAS_PREENTRENAMIENTO)
    cerebro = Cerebro(NOMBRES, config.TASA_APRENDIZAJE)
    h = config.HORIZONTE
    evaluaciones = []
    for i in range(HISTORIA_NECESARIA - 1 + h, len(velas)):
        j = i - h
        subio = cubre_costes(velas[j]["cierre"], velas[i]["cierre"])
        prediccion, ingenua = cerebro.aprender(caracteristicas(velas, j), subio)
        evaluaciones.append({"p": prediccion, "n": ingenua, "y": int(subio)})
    # Las 500 primeras lecciones son de "arranque en frío": no cuentan para evaluar
    resumen_previo = aprendizaje.resumir(evaluaciones[500:])
    print(f"Preentrenamiento listo: {cerebro.lecciones} lecciones aprendidas.")
    if resumen_previo:
        print(f"Con la historia previa: habilidad {resumen_previo['habilidad'] * 100:+.1f} % frente al "
              f"adivino ingenuo -> {aprendizaje.VEREDICTOS[resumen_previo['veredicto']][1]}\n")

    cartera = Cartera(config.CAPITAL_INICIAL, config.COMISION_FIJA,
                      config.COMISION_PORCENTAJE, config.SPREAD)
    estado = {
        "simbolo": config.SIMBOLO,
        "intervalo": config.INTERVALO,
        "creado": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "precio_inicio": velas[-1]["cierre"],
        "ultimo_t": velas[-2]["t"],  # la última vela se procesa en el primer ciclo
        "historial": [],
        "eventos": [],
        "evaluaciones": [],
        "preentrenamiento": resumen_previo,
    }
    anotar_evento(estado, f"Simulación creada con {config.CAPITAL_INICIAL:.0f} € ficticios "
                          f"en {config.SIMBOLO} ({cerebro.lecciones} lecciones de preentrenamiento)")
    return estado, cerebro, cartera


def cargar_o_crear():
    """Devuelve (estado, cerebro, cartera), o None si el estado no encaja con config.py."""
    if not os.path.exists(RUTA_ESTADO):
        return crear_estado()
    with open(RUTA_ESTADO, encoding="utf-8") as archivo:
        estado = json.load(archivo)
    if (estado["simbolo"], estado["intervalo"]) != (config.SIMBOLO, config.INTERVALO):
        print(f"El estado guardado es de {estado['simbolo']} {estado['intervalo']}, pero la "
              f"configuración dice {config.SIMBOLO} {config.INTERVALO}.\nUsa 'reiniciar_simulacion' "
              f"en el panel de control o borra la carpeta datos_bot para empezar de cero.")
        return None
    return estado, Cerebro.desde_dict(estado["cerebro"]), Cartera.desde_dict(estado["cartera"])


def ciclo(estado, cerebro, cartera):
    """Procesa las velas nuevas. Devuelve True si había alguna."""
    velas = descargar_velas(config.SIMBOLO, config.INTERVALO, VELAS_POR_CICLO)
    nuevas = [i for i, v in enumerate(velas) if v["t"] > estado["ultimo_t"]]
    if not nuevas:
        return False

    h = config.HORIZONTE
    for i in nuevas:
        j = i - h
        if j >= HISTORIA_NECESARIA - 1:
            subio = cubre_costes(velas[j]["cierre"], velas[i]["cierre"])
            prediccion, ingenua = cerebro.aprender(caracteristicas(velas, j), subio)
            estado.setdefault("evaluaciones", []).append(
                {"t": velas[j]["t"], "p": round(prediccion, 4), "n": round(ingenua, 4),
                 "y": int(subio), "v": config.VERSION_MODELO})
        estado["ultimo_t"] = velas[i]["t"]

    # Solo opera con la vela más reciente (si estuvo parado, las velas
    # antiguas sirven para aprender, no para operar con precios pasados).
    i = nuevas[-1]
    vela = velas[i]
    precio = vela["cierre"]
    probabilidad = cerebro.predecir(caracteristicas(velas, i))
    operacion = None
    if not config.PAUSADO:
        accion = decidir(probabilidad, cartera.en_posicion, config.UMBRAL_COMPRA, config.UMBRAL_VENTA)
        if accion == "comprar":
            operacion = cartera.comprar(precio, fecha_de(vela))
        elif accion == "vender":
            operacion = cartera.vender(precio, fecha_de(vela))
    if operacion:
        anotar_operacion(operacion)

    valor = cartera.valor(precio)
    referencia = valor_comprar_y_mantener(config.CAPITAL_INICIAL, estado["precio_inicio"], precio,
                                          config.COMISION_FIJA, config.SPREAD)
    estado["historial"].append({"t": vela["t"], "fecha": fecha_de(vela), "precio": precio,
                                "bot": valor, "referencia": referencia, "prob": probabilidad})
    aprendizaje.actualizar_diario(estado, cerebro, cartera)

    acierto = cerebro.tasa_acierto()
    texto_op = f"  >>> {operacion['tipo']} a {precio:,.2f} €" if operacion else ""
    pausa = "  (EN PAUSA)" if config.PAUSADO else ""
    print(f"[{fecha_de(vela)}] precio {precio:,.2f} € | prob. de cubrir costes {probabilidad * 100:4.1f} % | "
          f"{'DENTRO' if cartera.en_posicion else 'fuera '} | bot {valor:7.2f} € | "
          f"comprar y mantener {referencia:7.2f} € | aciertos {acierto * 100:.0f} % "
          f"(sin pensar {cerebro.acierto_sin_pensar() * 100:.0f} %){texto_op}{pausa}")
    return True


def main():
    cargado = cargar_o_crear()
    if cargado is None:
        sys.exit(1)
    estado, cerebro, cartera = cargado

    if "--una-vez" in sys.argv:
        if not ciclo(estado, cerebro, cartera):
            print("No hay velas nuevas todavía.")
        guardar(estado, cerebro, cartera)
        return

    print(f"Simulación iniciada el {estado['creado']} ({cerebro.lecciones} lecciones aprendidas).")
    print("Bot en marcha con DINERO FICTICIO. Revisa el mercado cada minuto; Ctrl+C para parar.\n")
    try:
        while True:
            try:
                if ciclo(estado, cerebro, cartera):
                    guardar(estado, cerebro, cartera)
            except ConnectionError as error:
                print(f"  (aviso) {error} Lo intento de nuevo en un minuto.")
            time.sleep(60)
    except KeyboardInterrupt:
        guardar(estado, cerebro, cartera)
        print("\nBot detenido. Todo guardado; al volver a abrirlo seguirá donde lo dejó.")


if __name__ == "__main__":
    main()
