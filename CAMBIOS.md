# Registro de cambios del modelo

Cada vez que cambiemos cómo piensa el bot (indicadores, cerebro, umbrales por defecto...),
subimos `VERSION_MODELO` en `config.py` y lo apuntamos aquí con el motivo y lo que esperamos.
Así, en el `INFORME_APRENDIZAJE.md` y en `datos_bot/diario.jsonl` se puede comparar cada versión.

Reglas:
- Un solo cambio por versión, para saber qué ha funcionado y qué no.
- Como mínimo 3 semanas (~500 predicciones) entre cambios.
- Antes de subir un cambio, compararlo con `python backtest.py`, sin fiarse solo de eso.

## 1.0 (09/10/2026)

Versión inicial.
- 9 indicadores (cambios de precio, medias, RSI, volatilidad, volumen, tamaño de vela).
- Cerebro: regresión logística con aprendizaje online (tasa 0,01).
- Pregunta que intenta responder: "¿subirá más de lo que cuestan las comisiones en las próximas 4 horas?".
- Compra con probabilidad ≥ 58 %, vende por debajo de 47 %.
- Backtest abril–octubre 2026: bot −0,7 % frente a comprar y mantener +13,2 %.
