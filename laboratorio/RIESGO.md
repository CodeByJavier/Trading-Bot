# ¿Cuánto meter en cada compra? Tamaño de posición y filtros de mercado

Generado: 18/11/2026 20:44 · Bitcoin en euros, velas diarias · 1000 € ficticios al empezar cada tramo · 1 € por orden y 0,1 % de spread · la regla de entrada y salida es siempre la del bot (media de 50 días ±3 %).

## Cómo leer esto

- **Sharpe**: ganancia por cada unidad de riesgo (anualizado). Cuanto más alto, mejor. Es el criterio para elegir, fijado antes de ver los resultados.
- **Caída máx.**: la peor bajada desde un máximo. **Peor día**: la mayor pérdida en un día.
- **Invertido**: qué parte del dinero estuvo de media dentro de Bitcoin (el resto, en efectivo sin intereses).
- Tamaño **según volatilidad**: invierte objetivo ÷ volatilidad de los últimos 30 días (máximo el 100 %). Si Bitcoin está muy nervioso, compra menos.
- **Riesgo fijo**: compra lo justo para que, si el precio cae hasta el nivel de salida de ese día (media × 0,97), se pierda ese % del dinero. Ojo: el bot vende al cierre del día, así que puede perder algo más.
- **Filtro funding**: no compra si en los futuros de Bitcoin la mayoría paga más de un 0.03 % cada 8 h por apostar a subidas (media de 3 días). **Filtro Fear & Greed**: no compra si el índice está por encima de 75.

## Tramo A (elegir)

| Variante | Resultado | Sharpe | Caída máx. | Peor día | Volatilidad | Invertido | Operaciones |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Comprar y mantener** | +61.8 % | +1,11 | 32 % | 9.2 % | 47 % | 100 % | 1 |
| Actual: todo el dinero en cada compra | +46.5 % | +1,22 | 18 % | 6.5 % | 31 % | 61 % | 11 |
| Tamaño según volatilidad (objetivo 40 % anual) | +37.6 % | +1,19 | 15 % | 5.1 % | 26 % | 50 % | 11 |
| Ídem, reajustando cada semana | +33.1 % | +1,06 | 15 % | 5.1 % | 26 % | 53 % | 14 |
| Riesgo fijo: perder como mucho un 2 % hasta la salida | +14.4 % | +1,11 | 7 % | 2.2 % | 11 % | 19 % | 11 |
| Filtro funding: no compra si los futuros están muy apalancados | +46.5 % | +1,22 | 18 % | 6.5 % | 31 % | 61 % | 11 |
| Filtro Fear & Greed: no compra con codicia extrema | +46.5 % | +1,22 | 18 % | 6.5 % | 31 % | 61 % | 11 |
| Siempre la mitad del dinero (50 %) *(ilustrativo)* | +24.1 % | +1,17 | 10 % | 3.2 % | 17 % | 33 % | 11 |
| Volatilidad, objetivo 30 % *(ilustrativo)* | +29.5 % | +1,19 | 12 % | 3.8 % | 20 % | 40 % | 11 |
| Volatilidad, objetivo 50 % *(ilustrativo)* | +44.5 % | +1,21 | 18 % | 6.4 % | 30 % | 58 % | 11 |
| Riesgo fijo del 1 % *(ilustrativo)* | +6.7 % | +1,00 | 4 % | 1.2 % | 6 % | 10 % | 11 |
| Riesgo fijo del 3 % *(ilustrativo)* | +21.7 % | +1,15 | 9 % | 3.0 % | 16 % | 28 % | 11 |

## Tramo B (validar)

| Variante | Resultado | Sharpe | Caída máx. | Peor día | Volatilidad | Invertido | Operaciones |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Comprar y mantener** | -40.0 % | -0,73 | 52 % | 13.8 % | 42 % | 100 % | 1 |
| Actual: todo el dinero en cada compra | -4.5 % | -0,01 | 31 % | 6.2 % | 26 % | 49 % | 10 |
| Tamaño según volatilidad (objetivo 40 % anual) | -4.3 % | -0,02 | 30 % | 6.2 % | 25 % | 46 % | 10 |
| Ídem, reajustando cada semana | -4.3 % | -0,02 | 30 % | 6.2 % | 25 % | 46 % | 10 |
| Riesgo fijo: perder como mucho un 2 % hasta la salida | -0.9 % | -0,05 | 10 % | 1.9 % | 8 % | 15 % | 10 |
| Filtro funding: no compra si los futuros están muy apalancados | -4.5 % | -0,01 | 31 % | 6.2 % | 26 % | 49 % | 10 |
| Filtro Fear & Greed: no compra con codicia extrema | -4.5 % | -0,01 | 31 % | 6.2 % | 26 % | 49 % | 10 |
| Siempre la mitad del dinero (50 %) *(ilustrativo)* | -2.1 % | -0,06 | 17 % | 3.2 % | 13 % | 25 % | 10 |
| Volatilidad, objetivo 30 % *(ilustrativo)* | -4.6 % | -0,04 | 29 % | 6.2 % | 23 % | 42 % | 10 |
| Volatilidad, objetivo 50 % *(ilustrativo)* | -4.5 % | -0,01 | 31 % | 6.2 % | 26 % | 49 % | 10 |
| Riesgo fijo del 1 % *(ilustrativo)* | -0.9 % | -0,15 | 6 % | 0.9 % | 4 % | 8 % | 10 |
| Riesgo fijo del 3 % *(ilustrativo)* | -1.1 % | -0,01 | 15 % | 2.8 % | 12 % | 22 % | 10 |

## Año a año (2021–2026, el último incompleto)

Resultado del año / caída máxima del año.

| Variante | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | Todo encadenado | Años con mejor Sharpe que la actual |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| **Comprar y mantener** | +68.2 % / 52 % | -63.5 % / 64 % | +147.5 % / 18 % | +124.1 % / 27 % | -18.8 % / 32 % | -22.1 % / 38 % | +115.2 % | — |
| Actual: todo el dinero en cada compra | +171.3 % / 24 % | -31.3 % / 32 % | +89.9 % / 18 % | +85.2 % / 26 % | -17.3 % / 20 % | +8.1 % / 21 % | +486.2 % | — |
| Tamaño según volatilidad (objetivo 40 % anual) | +97.6 % / 17 % | -24.1 % / 24 % | +82.7 % / 16 % | +76.6 % / 22 % | -18.7 % / 19 % | +8.3 % / 20 % | +326.1 % | 3/6 |
| Ídem, reajustando cada semana | +71.6 % / 14 % | -27.6 % / 28 % | +78.3 % / 17 % | +73.0 % / 21 % | -20.2 % / 20 % | +8.3 % / 20 % | +231.1 % | 2/6 |
| Riesgo fijo: perder como mucho un 2 % hasta la salida | +17.8 % / 7 % | -11.0 % / 11 % | +18.4 % / 6 % | +27.0 % / 9 % | -5.9 % / 6 % | +3.0 % / 6 % | +52.6 % | 1/6 |
| Filtro funding: no compra si los futuros están muy apalancados | +140.9 % / 21 % | -31.3 % / 32 % | +89.9 % / 18 % | +83.7 % / 26 % | -17.3 % / 20 % | +8.1 % / 21 % | +416.2 % | 0/6 |
| Filtro Fear & Greed: no compra con codicia extrema | +140.9 % / 21 % | -31.3 % / 32 % | +89.9 % / 18 % | +85.2 % / 26 % | -17.3 % / 20 % | +8.1 % / 21 % | +420.4 % | 0/6 |
| Siempre la mitad del dinero (50 %) | +73.7 % / 14 % | -17.0 % / 17 % | +40.6 % / 10 % | +42.1 % / 15 % | -9.2 % / 11 % | +4.2 % / 11 % | +172.5 % | 0/6 |
| Volatilidad, objetivo 30 % | +69.8 % / 14 % | -20.9 % / 21 % | +81.5 % / 14 % | +56.9 % / 18 % | -16.7 % / 17 % | +7.9 % / 18 % | +243.2 % | 2/6 |
| Volatilidad, objetivo 50 % | +127.7 % / 21 % | -27.1 % / 27 % | +84.9 % / 18 % | +86.5 % / 26 % | -18.5 % / 19 % | +8.1 % / 21 % | +403.8 % | 2/6 |
| Riesgo fijo del 1 % | +8.3 % / 4 % | -6.0 % / 6 % | +8.5 % / 3 % | +12.8 % / 5 % | -3.5 % / 3 % | +1.2 % / 3 % | +21.7 % | 0/6 |
| Riesgo fijo del 3 % | +27.8 % / 9 % | -15.8 % / 16 % | +28.7 % / 8 % | +41.5 % / 13 % | -8.3 % / 8 % | +4.7 % / 9 % | +87.9 % | 2/6 |

## Veredicto

La mejor en el tramo A (por Sharpe) fue **Actual: todo el dinero en cada compra**: +46.5 %, Sharpe +1,22, caída máxima 18 %.

En el tramo B, que no se usó para elegir: -4.5 %, Sharpe -0,01, caída máxima 31 % (la versión actual: -4.5 %, Sharpe -0,01, caída 31 %).

- ¿Mejora el Sharpe de la versión actual en el tramo B? ❌ No
- Recuerda: el Sharpe de un año o año y medio tiene mucho margen de error; lo que cuenta es que la mejora se repita en B y en la mayoría de los años.
