# Informe de aprendizaje del bot

Actualizado: 10/10/2026 02:17 · Moneda: BTCEUR · Versión del modelo: 2.1 · Simulación iniciada: 10/10/2026 01:09

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
| Últimos 30 días | 2 | 0.0 % | 0.0 % | -34.5 % | -2.51 | Pocos datos todavía |
| Últimos 90 días | 2 | 0.0 % | 0.0 % | -34.5 % | -2.51 | Pocos datos todavía |
| Desde el inicio (en directo) | 2 | 0.0 % | 0.0 % | -34.5 % | -2.51 | Pocos datos todavía |
| Preentrenamiento (historia previa) | 2379 | 72.6 % | 56.2 % | +24.1 % | +3.44 | Aprende algo útil |

## Resultado de la cartera ficticia

- Bot: **996.20 €** (-0.4 %)
- Comprar y mantener: **996.20 €** (-0.4 %)
- Operaciones: 1 · Comisiones pagadas: 1.00 €

## Evolución por semanas

Una semana sola es poco para juzgar: lo importante es la tendencia de varias semanas seguidas.

| Semana del | Versión | Predicciones | Habilidad | z | Veredicto | Bot al final | Referencia al final |
|---|---|---:|---:|---:|---|---:|---:|
| 05/10/2026 | 2.1 | 2 | -34.5 % | -2.51 | Pocos datos todavía | - | - |

## Lo que ha aprendido (pesos del cerebro)

Si un peso cambia mucho de signo de una semana a otra, el cerebro está persiguiendo ruido.

| Indicador | Peso al empezar el diario | Peso ahora |
|---|---:|---:|
| Cambio última vela | - | -0.089 |
| Cambio últimas 4 velas | - | -0.054 |
| Cambio últimas 24 velas | - | -0.341 |
| Distancia a la media de 24 velas | - | +0.174 |
| Distancia a la media de 96 velas | - | -1.428 |
| RSI 14 (fuerza compradora) | - | +0.233 |
| Volatilidad 24 velas | - | +0.426 |
| Volumen relativo | - | +0.134 |
| Tamaño de la última vela | - | +0.163 |
| Fear & Greed (miedo/codicia) | - | -1.397 |
| Cambio del Fear & Greed en 7 días | - | -0.250 |

## ¿Cuándo revisar y retocar?

- **Próxima revisión recomendada: 09/11/2026**. Llevamos 2 predicciones evaluadas en directo.
- No toques nada antes de 30 días: con menos datos cualquier conclusión es ruido.
- Después, revisa **una vez al mes**. Cambia **una sola cosa** cada vez, sube `VERSION_MODELO` en `config.py` y apunta el cambio en `CAMBIOS.md`.
- Si tras 2-3 meses ninguna versión llega a "Aprende algo útil", lo más probable es que no haya patrón aprovechable con estos indicadores: es un resultado válido, no un fallo.

## Para revisar con Claude

Pídele a Claude que lea este archivo, `datos_bot/diario.jsonl` y `CAMBIOS.md` del repositorio (antes, `git pull`). Con eso tiene la historia completa para proponer el siguiente retoque.
