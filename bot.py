"""
Bot de trading SIMULADO: precios reales, dinero ficticio.

Cada vez que se ejecuta (GitHub lo hace cada hora):
  1. La IA aprende de las velas nuevas (comprueba las predicciones que hizo hace HORIZONTE velas).
  2. Quien decide (config.ESTRATEGIA) compra, vende o espera con el dinero ficticio:
       - "tendencia": la regla de la media de 50 días, revisada una vez al día con velas diarias.
       - "ia" / "tendencia_ia": la IA participa en la decisión.
  3. Guarda todo en datos_bot/ y actualiza el panel (docs/datos.json) y el informe de aprendizaje.

La primera vez (o al cambiar VERSION_MODELO) la IA estudia los últimos meses antes de empezar.

Uso:
  python bot.py            se queda funcionando en tu PC (Ctrl+C para parar)
  python bot.py --una-vez  procesa las velas nuevas y termina (lo usa GitHub cada hora)
"""
import csv
import json
import os
import shutil
import sys
import time
from datetime import datetime

import aprendizaje
import config
import fuentes
import indicadores
from cerebro import Cerebro
from datos import descargar_velas
from indicadores import HISTORIA_NECESARIA, NOMBRES, caracteristicas
from panel import exportar_panel
from simulador import Cartera, decidir, respetar_permanencia, valor_comprar_y_mantener

RUTA_ESTADO = os.path.join(config.CARPETA_DATOS, "estado.json")
RUTA_OPERACIONES = os.path.join(config.CARPETA_DATOS, "operaciones.csv")
CARPETA_ARCHIVO = os.path.join(config.CARPETA_DATOS, "archivo")
VELAS_POR_CICLO = HISTORIA_NECESARIA + config.HORIZONTE + 200
MINUTOS = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "6h": 360, "1d": 1440}


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


def velas_ia(cantidad):
    """Velas con las que aprende la IA, con los datos externos que necesiten sus indicadores."""
    velas = descargar_velas(config.SIMBOLO, config.INTERVALO, cantidad)
    fng = tasas = None
    if indicadores.necesita(config.INDICADORES, "sentimiento"):
        try:
            fng = fuentes.miedo_codicia(fuentes.dias_necesarios(velas))
        except ConnectionError as error:
            print(f"  (aviso) Sin datos de Fear & Greed ({error}); esos indicadores valdrán 0 esta vez.")
    if indicadores.necesita(config.INDICADORES, "futuros"):
        try:
            tasas = fuentes.funding(velas[0]["t"] - 3 * fuentes.DIA_MS)
        except ConnectionError as error:
            print(f"  (aviso) Sin datos de funding ({error}); esos indicadores valdrán 0 esta vez.")
    return fuentes.enriquecer(velas, fng, tasas)


def archivar(estado_previo=None):
    """Mueve la simulación actual a datos_bot/archivo/ (no se borra nada). Devuelve la carpeta."""
    archivos = [r for r in (RUTA_ESTADO, RUTA_OPERACIONES, aprendizaje.RUTA_DIARIO) if os.path.exists(r)]
    if not archivos:
        return None
    version = (estado_previo or {}).get("version", "1.0")
    destino = os.path.join(CARPETA_ARCHIVO, f"v{version}_{datetime.now().strftime('%Y-%m-%d_%H%M')}")
    os.makedirs(destino, exist_ok=True)
    for ruta in archivos:
        shutil.move(ruta, os.path.join(destino, os.path.basename(ruta)))
    return os.path.relpath(destino, config.CARPETA_PROYECTO).replace("\\", "/")


def crear_estado(motivo=None):
    print(f"Nueva simulación v{config.VERSION_MODELO}: la IA estudia {config.VELAS_PREENTRENAMIENTO} velas de "
          f"{config.SIMBOLO} ({config.INTERVALO})...")
    velas = velas_ia(config.VELAS_PREENTRENAMIENTO)
    cerebro = Cerebro(NOMBRES, config.TASA_APRENDIZAJE)
    h = config.HORIZONTE
    evaluaciones = []
    # Hasta la penúltima vela: la última la procesa el primer ciclo (así ninguna lección se repite)
    for i in range(HISTORIA_NECESARIA - 1 + h, len(velas) - 1):
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
        "version": config.VERSION_MODELO,
        "simbolo": config.SIMBOLO,
        "intervalo": config.INTERVALO,
        "nombres": NOMBRES,
        "creado": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "precio_inicio": velas[-1]["cierre"],
        "ultimo_t": velas[-2]["t"],
        "ultima_tendencia_t": None,
        "compra_t": None,
        "historial": [],
        "eventos": [],
        "evaluaciones": [],
        "preentrenamiento": resumen_previo,
    }
    if motivo:
        anotar_evento(estado, motivo)
    anotar_evento(estado, f"Simulación v{config.VERSION_MODELO} creada con {config.CAPITAL_INICIAL:.0f} € ficticios "
                          f"en {config.SIMBOLO}. Decide: {config.ESTRATEGIA}. "
                          f"La IA empieza con {cerebro.lecciones} lecciones de preentrenamiento")
    return estado, cerebro, cartera


def cargar_o_crear():
    """Carga la simulación. Si la configuración cambió de forma incompatible, archiva la vieja y crea otra."""
    if not os.path.exists(RUTA_ESTADO):
        return crear_estado()
    with open(RUTA_ESTADO, encoding="utf-8") as archivo:
        estado = json.load(archivo)
    antes = (estado.get("version", "1.0"), estado["simbolo"], estado["intervalo"], estado["cerebro"]["nombres"])
    ahora = (config.VERSION_MODELO, config.SIMBOLO, config.INTERVALO, NOMBRES)
    if antes != ahora:
        carpeta = archivar(estado)
        print(f"La configuración cambió (v{antes[0]} {antes[1]} {antes[2]} -> v{ahora[0]} {ahora[1]} {ahora[2]}). "
              f"Simulación anterior guardada en {carpeta}.")
        return crear_estado(f"Nueva versión del bot (v{antes[0]} → v{ahora[0]}). "
                            f"La simulación anterior se guardó en {carpeta}")
    return estado, Cerebro.desde_dict(estado["cerebro"]), Cartera.desde_dict(estado["cartera"])


def revisar_tendencia(estado, cartera):
    """Mira la regla de tendencia con velas diarias. Devuelve (alcista, ¿hay vela diaria nueva?)."""
    n, margen = config.TENDENCIA_VELAS, config.TENDENCIA_MARGEN
    diarias = descargar_velas(config.SIMBOLO, config.TENDENCIA_INTERVALO, n + 2)
    i = len(diarias) - 1
    media = indicadores.media(diarias, i, n)
    alcista = indicadores.tendencia_alcista(diarias, i, n, margen, cartera.en_posicion)
    estado["tendencia"] = {
        "fecha": fecha_de(diarias[i]), "precio": diarias[i]["cierre"], "media": media, "dias": n,
        "margen": margen, "alcista": alcista, "entrar": media * (1 + margen), "salir": media * (1 - margen),
    }
    nueva = diarias[i]["t"] != estado.get("ultima_tendencia_t")
    estado["ultima_tendencia_t"] = diarias[i]["t"]
    return alcista, nueva


def ciclo(estado, cerebro, cartera):
    """Procesa las velas nuevas. Devuelve True si había alguna."""
    velas = velas_ia(VELAS_POR_CICLO)
    nuevas = [i for i, v in enumerate(velas) if v["t"] > estado["ultimo_t"]]
    if not nuevas:
        return False

    # 1) La IA aprende de cada vela nueva
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

    # 2) Decide (solo con la vela más reciente: si estuvo parado, las antiguas sirven para
    #    aprender, no para operar con precios pasados)
    i = nuevas[-1]
    vela = velas[i]
    precio = vela["cierre"]
    probabilidad = cerebro.predecir(caracteristicas(velas, i))
    accion = None
    if config.ESTRATEGIA == "ia":
        accion = decidir(probabilidad, cartera.en_posicion, config.UMBRAL_COMPRA, config.UMBRAL_VENTA, "ia")
        velas_dentro = None
        if estado.get("compra_t") is not None:
            velas_dentro = (vela["t"] - estado["compra_t"]) // (MINUTOS[config.INTERVALO] * 60000)
        accion = respetar_permanencia(accion, velas_dentro, config.PERMANENCIA_MINIMA)
    else:
        alcista, vela_diaria_nueva = revisar_tendencia(estado, cartera)
        if vela_diaria_nueva:  # la regla de tendencia solo se revisa una vez al día
            accion = decidir(probabilidad, cartera.en_posicion, config.UMBRAL_COMPRA, config.UMBRAL_VENTA,
                             config.ESTRATEGIA, alcista)

    operacion = None
    if not config.PAUSADO:
        if accion == "comprar":
            operacion = cartera.comprar(precio, fecha_de(vela))
        elif accion == "vender":
            operacion = cartera.vender(precio, fecha_de(vela))
    if operacion:
        anotar_operacion(operacion)
        estado["compra_t"] = vela["t"] if operacion["tipo"] == "COMPRA" else None

    valor = cartera.valor(precio)
    referencia = valor_comprar_y_mantener(config.CAPITAL_INICIAL, estado["precio_inicio"], precio,
                                          config.COMISION_FIJA, config.SPREAD)
    estado["historial"].append({"t": vela["t"], "fecha": fecha_de(vela), "precio": precio,
                                "bot": valor, "referencia": referencia, "prob": probabilidad})
    aprendizaje.actualizar_diario(estado, cerebro, cartera)

    acierto = cerebro.tasa_acierto()
    tendencia = estado.get("tendencia")
    texto_tendencia = "" if not tendencia else f" | tendencia {'ALCISTA' if tendencia['alcista'] else 'bajista'}"
    texto_op = f"  >>> {operacion['tipo']} a {precio:,.2f} €" if operacion else ""
    pausa = "  (EN PAUSA)" if config.PAUSADO else ""
    print(f"[{fecha_de(vela)}] precio {precio:,.2f} €{texto_tendencia} | IA {probabilidad * 100:4.1f} % | "
          f"{'DENTRO' if cartera.en_posicion else 'fuera '} | bot {valor:7.2f} € | "
          f"comprar y mantener {referencia:7.2f} € | aciertos IA {acierto * 100:.0f} % "
          f"(sin pensar {cerebro.acierto_sin_pensar() * 100:.0f} %){texto_op}{pausa}")
    return True


def main():
    estado, cerebro, cartera = cargar_o_crear()

    if "--una-vez" in sys.argv:
        if not ciclo(estado, cerebro, cartera):
            print("No hay velas nuevas todavía.")
        guardar(estado, cerebro, cartera)
        return

    print(f"Simulación v{estado.get('version', '1.0')} iniciada el {estado['creado']} "
          f"({cerebro.lecciones} lecciones aprendidas).")
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
