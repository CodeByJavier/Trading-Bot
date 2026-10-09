# Resultados del laboratorio

Generado: 09/10/2026 16:02 · Moneda: BTCEUR · Capital ficticio: 200 € al empezar cada tramo

## Cómo leer esto

- **Tramo A** (01/06/2024 → 01/08/2025): se usa para **elegir** la mejor idea.
- **Tramo B** (01/08/2025 → 09/10/2026): **validación**. Lo que la idea elegida consigue aquí es la estimación honesta de cómo le iría en el futuro.
- Cada tramo empieza con el mismo dinero ficticio; el cerebro sí conserva lo aprendido.
- **Caída máxima**: la peor bajada desde un máximo. Mide el riesgo (cuánto llegarías a perder por el camino).
- **IA: habilidad**: mejor que 0 % = predice mejor que el adivino ingenuo; z ≥ 2 = muy improbable que sea suerte.
- Todo con dinero ficticio y precios reales. Se prueban varias ideas a la vez, así que alguna puede salir bien por azar en un tramo: por eso cuentan el tramo B y la comprobación año a año.

## Tramo A (elegir)

| Experimento | Bot | Comprar y mantener | ¿Gana a mantener? | Caída máx. bot / mantener | Operaciones | Comisiones | Tiempo dentro | IA: habilidad (z) |
|---|---:|---:|:---:|---:|---:|---:|---:|---|
| v1.0 actual (1 h, 4 h vista) | **-13.1 %** | +61.0 % | ❌ | 13 % / 35 % | 22 | 22.00 € | 0 % | +4.7 % (z +3.0) ✅ |
| v1.0 con comisión del 0,1 % | **-15.0 %** | +62.2 % | ❌ | 21 % / 35 % | 228 | 40.96 € | 5 % | +2.7 % (z +3.2) ✅ |
| 1 h, 24 h vista + Fear & Greed | **-92.9 %** | +61.0 % | ❌ | 93 % / 35 % | 180 | 180.00 € | 8 % | +11.5 % (z +3.1) ✅ |
| Diario, 5 días vista | **+0.2 %** | +60.7 % | ❌ | 20 % / 32 % | 16 | 16.00 € | 6 % | +1.9 % (z +0.6) 🟡 |
| Diario + Fear & Greed | **-17.2 %** | +60.7 % | ❌ | 30 % / 32 % | 16 | 16.00 € | 8 % | +1.9 % (z +0.6) 🟡 |
| Diario + Fear & Greed + futuros | **-17.8 %** | +60.7 % | ❌ | 30 % / 32 % | 18 | 18.00 € | 9 % | +1.9 % (z +0.6) 🟡 |
| Tendencia 50 días (sin IA) | **+37.5 %** | +60.7 % | ❌ | 23 % / 32 % | 27 | 27.00 € | 58 % | — (sin IA) |
| Tendencia 50 días + IA con Fear & Greed | **-5.1 %** | +60.7 % | ❌ | 5 % / 32 % | 2 | 2.00 € | 0 % | +1.9 % (z +0.6) 🟡 |
| Tendencia 50 días, margen 3 % | **+40.3 %** | +60.7 % | ❌ | 20 % / 32 % | 11 | 11.00 € | 61 % | — (sin IA) |
| 1 h, 24 h vista + Fear & Greed, mínimo 24 h dentro | **-51.5 %** | +61.0 % | ❌ | 54 % / 35 % | 114 | 114.00 € | 15 % | +11.5 % (z +3.1) ✅ |
| Ídem con comisión del 0,1 % | **+7.3 %** | +62.2 % | ❌ | 25 % / 35 % | 247 | 48.24 € | 40 % | +9.8 % (z +3.1) ✅ |

## Tramo B (validar)

| Experimento | Bot | Comprar y mantener | ¿Gana a mantener? | Caída máx. bot / mantener | Operaciones | Comisiones | Tiempo dentro | IA: habilidad (z) |
|---|---:|---:|:---:|---:|---:|---:|---:|---|
| v1.0 actual (1 h, 4 h vista) | **-9.5 %** | -27.7 % | ✅ | 10 % / 53 % | 14 | 14.00 € | 0 % | +2.5 % (z +1.6) 🟡 |
| v1.0 con comisión del 0,1 % | **-3.7 %** | -26.9 % | ✅ | 22 % / 52 % | 136 | 24.55 € | 2 % | +1.9 % (z +2.4) ✅ |
| 1 h, 24 h vista + Fear & Greed | **-73.8 %** | -27.7 % | ❌ | 74 % / 53 % | 138 | 138.00 € | 5 % | +8.1 % (z +2.6) ✅ |
| Diario, 5 días vista | **-12.2 %** | -26.6 % | ✅ | 21 % / 52 % | 4 | 4.00 € | 2 % | -1.5 % (z -0.7) ⚪ |
| Diario + Fear & Greed | **-12.7 %** | -26.6 % | ✅ | 22 % / 52 % | 8 | 8.00 € | 4 % | -1.6 % (z -0.7) ⚪ |
| Diario + Fear & Greed + futuros | **-17.7 %** | -26.6 % | ✅ | 26 % / 52 % | 6 | 6.00 € | 3 % | -1.5 % (z -0.6) ⚪ |
| Tendencia 50 días (sin IA) | **-12.0 %** | -26.6 % | ✅ | 37 % / 52 % | 27 | 27.00 € | 47 % | — (sin IA) |
| Tendencia 50 días + IA con Fear & Greed | **-3.0 %** | -26.6 % | ✅ | 3 % / 52 % | 2 | 2.00 € | 0 % | -1.6 % (z -0.7) ⚪ |
| Tendencia 50 días, margen 3 % | **-4.1 %** | -26.6 % | ✅ | 33 % / 52 % | 9 | 9.00 € | 48 % | — (sin IA) |
| 1 h, 24 h vista + Fear & Greed, mínimo 24 h dentro | **-62.5 %** | -27.7 % | ❌ | 63 % / 53 % | 98 | 98.00 € | 13 % | +8.1 % (z +2.6) ✅ |
| Ídem con comisión del 0,1 % | **-30.6 %** | -26.9 % | ❌ | 31 % / 52 % | 202 | 35.19 € | 36 % | +9.1 % (z +3.1) ✅ |

## Robustez: variantes de la regla de tendencia

No se usan para elegir. Sirven para ver si la idea funciona en general o solo con una cifra concreta.

| Variante | Tramo A bot | Tramo B bot | Comprar y mantener A / B | Operaciones A+B |
|---|---:|---:|---:|---:|
| Tendencia 20 días | +20.5 % | -23.1 % | +60.7 % / -26.6 % | 92 |
| Tendencia 100 días | +41.3 % | -16.8 % | +60.7 % / -26.6 % | 38 |
| Tendencia 200 días | -5.2 % | -0.3 % | +60.7 % / -26.6 % | 26 |

## Año a año (velas diarias, 2021–2026)

Cada año empieza con el mismo dinero ficticio. El último año está incompleto.

| Estrategia | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | Todo encadenado | Años que gana a mantener |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| **Comprar y mantener** | +67.1 % | -64.1 % | +146.1 % | +122.8 % | -19.5 % | -4.7 % | **+152.6 %** | — |
| Diario, 5 días vista | -7.8 % | -27.7 % | -2.2 % | +13.5 % | -13.0 % | -11.8 % | **-43.1 %** | 2/6 |
| Diario + Fear & Greed | -12.4 % | -38.2 % | -2.4 % | +18.4 % | -40.6 % | +1.1 % | **-62.5 %** | 2/6 |
| Diario + Fear & Greed + futuros | +21.5 % | -24.1 % | +0.7 % | +6.8 % | -34.1 % | -11.8 % | **-42.4 %** | 1/6 |
| Tendencia 50 días (sin IA) | +133.3 % | -50.9 % | +72.3 % | +69.6 % | -11.9 % | +3.4 % | **+204.9 %** | 4/6 |
| Tendencia 50 días + IA con Fear & Greed | +35.9 % | -7.5 % | +0.0 % | +0.0 % | -8.0 % | +0.0 % | **+15.7 %** | 3/6 |
| Tendencia 50 días, margen 3 % | +167.7 % | -33.9 % | +85.2 % | +78.9 % | -21.0 % | +10.8 % | **+413.0 %** | 3/6 |
| Tendencia 20 días | -1.6 % | -62.7 % | +9.5 % | +50.3 % | -31.0 % | +2.3 % | **-57.4 %** | 2/6 |
| Tendencia 100 días | +85.6 % | -45.5 % | +63.5 % | +58.8 % | -13.9 % | +8.0 % | **+144.1 %** | 4/6 |
| Tendencia 200 días | -7.8 % | -5.7 % | +46.5 % | +84.9 % | -34.5 % | +15.3 % | **+77.7 %** | 2/6 |

| Caída máxima | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|
| **Comprar y mantener** | 52 % | 64 % | 18 % | 27 % | 32 % | 39 % |
| Diario, 5 días vista | 50 % | 31 % | 2 % | 2 % | 21 % | 21 % |
| Diario + Fear & Greed | 53 % | 40 % | 2 % | 4 % | 41 % | 9 % |
| Diario + Fear & Greed + futuros | 44 % | 31 % | 4 % | 10 % | 36 % | 21 % |
| Tendencia 50 días (sin IA) | 26 % | 51 % | 29 % | 31 % | 20 % | 26 % |
| Tendencia 50 días + IA con Fear & Greed | 25 % | 8 % | 0 % | 0 % | 8 % | 0 % |
| Tendencia 50 días, margen 3 % | 24 % | 34 % | 19 % | 28 % | 21 % | 22 % |
| Tendencia 20 días | 62 % | 65 % | 30 % | 37 % | 34 % | 23 % |
| Tendencia 100 días | 35 % | 48 % | 27 % | 39 % | 26 % | 13 % |
| Tendencia 200 días | 58 % | 6 % | 21 % | 25 % | 41 % | 6 % |

## Veredicto

La mejor idea en el tramo A fue **Tendencia 50 días, margen 3 %** (+40.3 %).

En el tramo B, que no se usó para elegirla, consiguió **-4.1 %** frente a -26.6 % de comprar y mantener, con una caída máxima del 33 % (mantener: 52 %).

- ¿Gana dinero en el tramo B? ❌ No
- ¿Gana a comprar y mantener en el tramo B? ✅ Sí
- ¿Su IA aprende algo útil (z ≥ 2)? — no usa IA
