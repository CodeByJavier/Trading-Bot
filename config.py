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
INTERVALO = "1h"          # velas con las que aprende la IA: "15m", "1h", "1d"

# --- Dinero ficticio -----------------------------------------------------
CAPITAL_INICIAL = 1000.0  # euros ficticios con los que empieza

# --- Costes (imitan a un bróker tipo Trade Republic: 1 € por orden) -------
COMISION_FIJA = 1.0       # euros por cada compra o venta
COMISION_PORCENTAJE = 0.0 # parte del importe (0.001 = 0,1 %)
SPREAD = 0.001            # diferencia estimada entre precio de compra y venta (0,1 %)

# --- Versión ---------------------------------------------------------------
# Súbela cada vez que cambies cómo piensa o decide el bot y apúntalo en CAMBIOS.md.
# Al cambiarla, el bot guarda la simulación anterior en datos_bot/archivo/ y empieza otra.
VERSION_MODELO = "2.1"

# --- Reglas de decisión (quién decide comprar y vender) ---------------------
# "tendencia":    regla clásica: dentro si el precio diario supera su media de TENDENCIA_VELAS días
# "ia":           la IA decide según su probabilidad (UMBRAL_COMPRA / UMBRAL_VENTA)
# "tendencia_ia": solo compra con tendencia alcista Y la IA de acuerdo
# v2.0 usa "tendencia": en el laboratorio fue lo único que se comportó mejor que comprar y
# mantener de forma consistente (ver laboratorio/RESULTADOS.md y CAMBIOS.md).
ESTRATEGIA = "tendencia"
TENDENCIA_INTERVALO = "1d"  # la regla de tendencia se revisa con velas diarias (una vez al día)
TENDENCIA_VELAS = 50        # media de 50 días
TENDENCIA_MARGEN = 0.03     # entra al superar la media un 3 % y sale al caer un 3 % por debajo
PERMANENCIA_MINIMA = 0      # velas mínimas dentro tras comprar (solo estrategia "ia")
UMBRAL_COMPRA = 0.58        # (estrategias con IA) compra si cree que subirá con probabilidad >= 58 %
UMBRAL_VENTA = 0.47         # (estrategias con IA) vende si esa probabilidad baja de 47 %
PAUSADO = False             # en pausa sigue aprendiendo, pero no opera

# --- Cerebro (la IA propia, "en prácticas" mientras ESTRATEGIA sea "tendencia") ----
HORIZONTE = 24                 # cuántas velas hacia el futuro intenta adivinar (24 h)
TASA_APRENDIZAJE = 0.01        # cuánto corrige su forma de pensar tras cada lección
VELAS_PREENTRENAMIENTO = 3000  # historia que estudia antes de empezar

# Qué mira el cerebro. Grupos: "precio", "sentimiento" (Fear & Greed),
# "futuros" (funding rate) y "tendencia" (distancia a la media larga)
INDICADORES = ["precio", "sentimiento"]

# De qué mercados aprende la IA (todos en euros y en Binance). El bot solo opera con SIMBOLO,
# pero la IA estudia también los demás: en el laboratorio así predijo Bitcoin el doble de bien.
MERCADOS_IA = ["BTCEUR", "ETHEUR", "BNBEUR", "XRPEUR"]

# --- Red neuronal multimercado (simulación aparte, con su propio dinero ficticio) ----------
# Una red neuronal mira a la vez criptomonedas, el dólar y la bolsa, y reparte la cartera según
# su confianza. En el laboratorio (laboratorio/RED.md) lo hizo peor que comprar y mantener: está
# en marcha para verla en directo y compararla con el bot principal.
RED_ACTIVA = True
RED_VERSION = "1.0"
RED_MERCADOS = ["BTC", "ETH", "BNB", "XRP", "SOL", "USD", "SP500", "IBEX"]  # ver mercados.py
RED_CAPITAL = 1000.0
RED_HORIZONTE = 5          # predice 5 días vista
RED_CADA_DIAS = 7          # revisa el reparto una vez por semana (aprende todos los días)
RED_BANDA = 0.15           # solo cambia una posición si se desvía más de un 15 % de lo que quiere

# --- Archivos ------------------------------------------------------------
CARPETA_DATOS = os.path.join(CARPETA_PROYECTO, "datos_bot")
CARPETA_PANEL = os.path.join(CARPETA_PROYECTO, "docs")
CARPETA_RED = os.path.join(CARPETA_PROYECTO, "datos_red")
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
