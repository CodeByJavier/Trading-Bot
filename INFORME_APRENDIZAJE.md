# Informe de aprendizaje del bot

Actualizado: 09/10/2026 15:25 · Moneda: BTCEUR · Versión del modelo: 1.0 · Simulación iniciada: 09/10/2026 15:25

## ⏳ Veredicto: Pocos datos todavía

Hace falta al menos una semana de predicciones para opinar.

## ¿Cómo se mide?

Antes de conocer cada resultado se guardan dos predicciones de *"¿subirá lo suficiente para pagar las comisiones?"*: la del cerebro y la de un **adivino ingenuo**, que siempre responde el porcentaje de subidas recientes.

- **Habilidad**: cuánto menos se equivoca el cerebro que el adivino (error cuadrático medio). Mayor que 0 % = mejor que el adivino; 0 % o menos = no aporta nada.
- **z**: lo segura que es esa mejora. Por encima de 2, es muy improbable que sea suerte.

| Periodo | Predicciones | Aciertos cerebro | Aciertos adivino | Habilidad | z | Veredicto |
|---|---:|---:|---:|---:|---:|---|
| Últimos 7 días | 1 | 100.0 % | 100.0 % | -777.2 % | +0.00 | Pocos datos todavía |
| Últimos 30 días | 1 | 100.0 % | 100.0 % | -777.2 % | +0.00 | Pocos datos todavía |
| Desde el inicio (en directo) | 1 | 100.0 % | 100.0 % | -777.2 % | +0.00 | Pocos datos todavía |
| Preentrenamiento (historia previa) | 2400 | 95.0 % | 95.3 % | -5.1 % | -0.72 | No supera al adivino |

## Resultado de la cartera ficticia

- Bot: **200.00 €** (+0.0 %)
- Comprar y mantener: **197.60 €** (-1.2 %)
- Operaciones: 0 · Comisiones pagadas: 0.00 €

## Evolución por semanas

Una semana sola es poco para juzgar: lo importante es la tendencia de varias semanas seguidas.

| Semana del | Versión | Predicciones | Habilidad | z | Veredicto | Bot al final | Referencia al final |
|---|---|---:|---:|---:|---|---:|---:|
| 05/10/2026 | 1.0 | 1 | -777.2 % | +0.00 | Pocos datos todavía | - | - |

## Lo que ha aprendido (pesos del cerebro)

Si un peso cambia mucho de signo de una semana a otra, el cerebro está persiguiendo ruido.

| Indicador | Peso al empezar el diario | Peso ahora |
|---|---:|---:|
| Cambio última vela | - | -0.040 |
| Cambio últimas 4 velas | - | -0.036 |
| Cambio últimas 24 velas | - | +0.107 |
| Distancia a la media de 24 velas | - | +0.067 |
| Distancia a la media de 96 velas | - | -0.157 |
| RSI 14 (fuerza compradora) | - | +0.157 |
| Volatilidad 24 velas | - | +0.279 |
| Volumen relativo | - | +0.086 |
| Tamaño de la última vela | - | +0.041 |

## ¿Cuándo revisar y retocar?

- **Próxima revisión recomendada: 30/10/2026**. Llevamos 1 predicciones evaluadas en directo.
- No toques nada antes de 3 semanas (~500 predicciones): con menos datos cualquier conclusión es ruido.
- Después, revisa **una vez al mes**. Cambia **una sola cosa** cada vez, sube `VERSION_MODELO` en `config.py` y apunta el cambio en `CAMBIOS.md`.
- Si tras 2-3 meses ninguna versión llega a "Aprende algo útil", lo más probable es que no haya patrón aprovechable con estos indicadores: es un resultado válido, no un fallo.

## Para revisar con Claude

Pídele a Claude que lea este archivo, `datos_bot/diario.jsonl` y `CAMBIOS.md` del repositorio (antes, `git pull`). Con eso tiene la historia completa para proponer el siguiente retoque.
