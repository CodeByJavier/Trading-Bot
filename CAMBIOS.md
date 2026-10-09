# Registro de cambios del modelo

Cada vez que cambiemos cómo piensa el bot (indicadores, cerebro, umbrales por defecto...),
subimos `VERSION_MODELO` en `config.py` y lo apuntamos aquí con el motivo y lo que esperamos.
Así, en el `INFORME_APRENDIZAJE.md` y en `datos_bot/diario.jsonl` se puede comparar cada versión.

Reglas:
- Un solo cambio por versión, para saber qué ha funcionado y qué no.
- Como mínimo 3 semanas (~500 predicciones) entre cambios.
- Antes de subir un cambio, probarlo en el laboratorio (`python laboratorio.py`): debe funcionar
  en el tramo B (validación) y año a año, no solo en el tramo usado para elegirlo.

## 2.1 (09/10/2026)

**La IA aprende de 4 criptomonedas y el capital ficticio sube a 1.000 €.**

- La IA estudia Bitcoin, Ethereum, BNB y XRP (velas de 1 h, 24 h vista, precio + Fear & Greed).
  Sigue en prácticas y se la evalúa solo prediciendo Bitcoin, frente al adivino ingenuo de Bitcoin.
- Capital ficticio: 1.000 € (antes 200 €). Con 1 € por orden, una compra + venta necesita subir un
  0,4 % para cubrir costes (antes 1,2 %). Eso cambia la pregunta de la IA, así que se volvió a probar.
- Motivo (ver `laboratorio/MULTIMERCADO.md`, con 1.000 €): prediciendo Bitcoin, la habilidad pasa de
  +9,2 % (solo Bitcoin + Fear & Greed, la v2.0) a +20,9 % (4 criptos + Fear & Greed) en el tramo B,
  con z = 6,0. Fue también la mejor en el tramo A (+15,2 %).
- Quién decide no cambia: la tendencia sobre Bitcoin. Repartir el dinero entre 4 criptos salió mejor
  en total, pero solo por la burbuja de BNB en 2021; sin 2021, solo Bitcoin gana (+127 % frente a +78 %).
  La mezcla con bolsa y euro/dólar es la más estable, pero rinde menos.

## 2.0 (09/10/2026)

**Decide una regla de tendencia; la IA pasa a estar "en prácticas".**

- Quién decide: regla de tendencia con velas diarias. Dentro si el cierre diario supera la media de
  50 días en un 3 %; fuera si cae un 3 % por debajo. Se revisa una vez al día.
- La IA: velas de 1 h, predice a 24 h vista y añade el índice Fear & Greed. Sigue aprendiendo y se la
  evalúa cada hora, pero no compra ni vende.
- Motivo (ver `laboratorio/RESULTADOS.md`):
  - Ninguna variante con IA decidiendo ganó dinero: las comisiones de 1 € se comían lo que acertaba.
    Con 24 h vista + Fear & Greed la IA SÍ predice mejor que el adivino (habilidad +8 a +11 %, z ≈ 3 en
    ambos tramos), pero esa ventaja no basta para operar con beneficio.
  - La tendencia de 50 días fue la mejor en el tramo A y en el tramo B (validación) perdió −4 % frente
    a −27 % de comprar y mantener. Año a año (2021–2026) gana a mantener en el total encadenado y con
    caídas máximas mucho menores. Las variantes de 50/100 días también lo hacen (robustez).
- Qué esperamos: NO gana siempre. En años bajistas pierde menos que mantener; en años muy alcistas
  puede ganar menos. Unas 10 operaciones al año.
- Aviso honesto: el margen del 3 % se probó como variante y luego se eligió; la versión sin margen
  también ganó a mantener, así que la conclusión no depende solo de esa cifra.
- Siguiente hipótesis: dar un papel a la IA (por ejemplo, como filtro de la tendencia) solo si en el
  laboratorio mejora a la tendencia sola Y en directo mantiene habilidad con z ≥ 2 durante 90 días.

## 1.0 (09/10/2026)

Versión inicial.
- 9 indicadores (cambios de precio, medias, RSI, volatilidad, volumen, tamaño de vela).
- Cerebro: regresión logística con aprendizaje online (tasa 0,01).
- Pregunta que intenta responder: "¿subirá más de lo que cuestan las comisiones en las próximas 4 horas?".
- Compra con probabilidad ≥ 58 %, vende por debajo de 47 %.
- Backtest abril–octubre 2026: bot −0,7 % frente a comprar y mantener +13,2 %.
