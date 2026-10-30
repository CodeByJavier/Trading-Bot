# Informe de aprendizaje del bot

Actualizado: 31/10/2026 00:01 · Moneda: BTCEUR · Versión del modelo: 2.1 · Simulación iniciada: 10/10/2026 01:09

## ⏳ Veredicto: Pocos datos todavía

Aún no hay suficientes predicciones independientes (unas 30) para opinar.

**Quién decide ahora:** la regla de tendencia (media de 50 días, margen 3 %). La IA está **en prácticas**: aprende y se la evalúa, pero no compra ni vende hasta que demuestre que mejora los resultados.

**De qué aprende la IA:** BTCEUR, ETHEUR, BNBEUR, XRPEUR. Se la evalúa prediciendo BTCEUR, el mercado que opera el bot.

## ¿Cómo se mide?

Antes de conocer cada resultado se guardan dos predicciones de *"¿subirá lo suficiente para pagar las comisiones?"*: la del cerebro y la de un **adivino ingenuo**, que siempre responde el porcentaje de subidas recientes.

- **Habilidad**: cuánto menos se equivoca el cerebro que el adivino (error cuadrático medio). Mayor que 0 % = mejor que el adivino; 0 % o menos = no aporta nada.
- **z**: lo segura que es esa mejora. Por encima de 2, es muy improbable que sea suerte.

| Periodo | Predicciones | Aciertos cerebro | Aciertos adivino | Habilidad | z | Veredicto |
|---|---:|---:|---:|---:|---:|---|
| Últimos 30 días | 505 | 66.7 % | 64.2 % | +1.2 % | +0.07 | Pocos datos todavía |
| Últimos 90 días | 505 | 66.7 % | 64.2 % | +1.2 % | +0.07 | Pocos datos todavía |
| Desde el inicio (en directo) | 505 | 66.7 % | 64.2 % | +1.2 % | +0.07 | Pocos datos todavía |
| Preentrenamiento (historia previa) | 2379 | 72.6 % | 56.2 % | +24.1 % | +3.44 | Aprende algo útil |

## Resultado de la cartera ficticia

- Bot: **934.10 €** (-6.6 %)
- Comprar y mantener: **904.04 €** (-9.6 %)
- Operaciones: 4 · Comisiones pagadas: 4.00 €

## Evolución por semanas

Una semana sola es poco para juzgar: lo importante es la tendencia de varias semanas seguidas.

| Semana del | Versión | Predicciones | Habilidad | z | Veredicto | Bot al final | Referencia al final |
|---|---|---:|---:|---:|---|---:|---:|
| 05/10/2026 | 2.1 | 72 | -13.6 % | -0.41 | Pocos datos todavía | 1007.05 € | 1007.05 € |
| 12/10/2026 | 2.1 | 168 | +12.6 % | +0.49 | Pocos datos todavía | 977.31 € | 978.75 € |
| 19/10/2026 | 2.1 | 169 | -16.0 % | -0.35 | Pocos datos todavía | 966.70 € | 968.12 € |
| 26/10/2026 | 2.1 | 96 | +18.1 % | +0.70 | Pocos datos todavía | 950.27 € | 951.67 € |

## Lo que ha aprendido (pesos del cerebro)

Si un peso cambia mucho de signo de una semana a otra, el cerebro está persiguiendo ruido.

| Indicador | Peso al empezar el diario | Peso ahora |
|---|---:|---:|
| Cambio última vela | -0.120 | +0.093 |
| Cambio últimas 4 velas | -0.100 | +0.171 |
| Cambio últimas 24 velas | -0.261 | +0.017 |
| Distancia a la media de 24 velas | +0.134 | +0.368 |
| Distancia a la media de 96 velas | -1.542 | -1.235 |
| RSI 14 (fuerza compradora) | +0.118 | +0.173 |
| Volatilidad 24 velas | +0.306 | -0.116 |
| Volumen relativo | +0.095 | -0.117 |
| Tamaño de la última vela | +0.072 | -0.017 |
| Fear & Greed (miedo/codicia) | -1.276 | -1.376 |
| Cambio del Fear & Greed en 7 días | -0.411 | -0.020 |

## ¿Cuándo revisar y retocar?

- **Próxima revisión recomendada: 09/11/2026**. Llevamos 505 predicciones evaluadas en directo.
- No toques nada antes de 30 días: con menos datos cualquier conclusión es ruido.
- Después, revisa **una vez al mes**. Cambia **una sola cosa** cada vez, sube `VERSION_MODELO` en `config.py` y apunta el cambio en `CAMBIOS.md`.
- Si tras 2-3 meses ninguna versión llega a "Aprende algo útil", lo más probable es que no haya patrón aprovechable con estos indicadores: es un resultado válido, no un fallo.

## Para revisar con Claude

Pídele a Claude que lea este archivo, `datos_bot/diario.jsonl` y `CAMBIOS.md` del repositorio (antes, `git pull`). Con eso tiene la historia completa para proponer el siguiente retoque.
