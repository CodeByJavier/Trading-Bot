"""
Configuración del bot. Cambia aquí los valores por defecto.

Algunos ajustes (marcados abajo) también se pueden cambiar desde el panel de
control de GitHub; esos cambios se guardan en ajustes.json y tienen prioridad.
"""
import json
import os

CARPETA_PROYECTO = os.path.dirname(os.path.abspath(__file__))

# --- Mercado -------------------------------------------------------------
SIMBOLO = "BTCEUR"        # par a operar (Bitcoin en euros). Otros: "ETHEUR", "SOLEUR"
INTERVALO = "1h"          # duración de cada vela: "15m", "1h", "1d"

# --- Dinero ficticio -----------------------------------------------------
CAPITAL_INICIAL = 200.0   # euros ficticios con los que empieza

# --- Costes (imitan a un bróker tipo Trade Republic: 1 € por orden) -------
COMISION_FIJA = 1.0       # euros por cada compra o venta
COMISION_PORCENTAJE = 0.0 # parte del importe (0.001 = 0,1 %)
SPREAD = 0.001            # diferencia estimada entre precio de compra y venta (0,1 %)

# --- Cerebro (la IA propia) ----------------------------------------------
VERSION_MODELO = "1.0"         # súbela cada vez que cambies cómo piensa el bot (y apúntalo en CAMBIOS.md)
HORIZONTE = 4                 # cuántas velas hacia el futuro intenta adivinar
TASA_APRENDIZAJE = 0.01        # cuánto corrige su forma de pensar tras cada lección
VELAS_PREENTRENAMIENTO = 3000  # historia que estudia antes de empezar a operar

# --- Reglas de decisión --------------------------------------------------
UMBRAL_COMPRA = 0.58      # compra si cree que subirá con probabilidad >= 58 %
UMBRAL_VENTA = 0.47       # vende si esa probabilidad baja de 47 %
PAUSADO = False           # en pausa sigue aprendiendo, pero no opera

# --- Backtest (prueba con el pasado) -------------------------------------
VELAS_BACKTEST = 5000
VELAS_CALENTAMIENTO = 1000  # velas que solo usa para aprender antes de operar

# --- Archivos ------------------------------------------------------------
CARPETA_DATOS = os.path.join(CARPETA_PROYECTO, "datos_bot")
CARPETA_PANEL = os.path.join(CARPETA_PROYECTO, "docs")
RUTA_AJUSTES = os.path.join(CARPETA_PROYECTO, "ajustes.json")

# Ajustes que el panel de control puede cambiar (se guardan en ajustes.json)
AJUSTABLES = ("SIMBOLO", "CAPITAL_INICIAL", "UMBRAL_COMPRA", "UMBRAL_VENTA", "PAUSADO")


def _recalcular():
    global MOVIMIENTO_MINIMO
    # Subida mínima para que una compra+venta compense sus costes
    MOVIMIENTO_MINIMO = 2 * COMISION_FIJA / CAPITAL_INICIAL + 2 * COMISION_PORCENTAJE + 2 * SPREAD


def aplicar_ajustes(cambios, guardar=True):
    """Cambia ajustes en memoria y, si `guardar`, los apunta en ajustes.json."""
    cambios = {k: v for k, v in cambios.items() if k in AJUSTABLES}
    globals().update(cambios)
    _recalcular()
    if guardar:
        actuales = {}
        if os.path.exists(RUTA_AJUSTES):
            with open(RUTA_AJUSTES, encoding="utf-8") as archivo:
                actuales = json.load(archivo)
        actuales.update(cambios)
        with open(RUTA_AJUSTES, "w", encoding="utf-8") as archivo:
            json.dump(actuales, archivo, indent=2, ensure_ascii=False)
            archivo.write("\n")


if os.path.exists(RUTA_AJUSTES):
    with open(RUTA_AJUSTES, encoding="utf-8") as _archivo:
        aplicar_ajustes(json.load(_archivo), guardar=False)
else:
    _recalcular()
