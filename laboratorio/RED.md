# Laboratorio: red neuronal multimercado

Generado: 11/10/2026 08:34. Capital ficticio 1000 € al empezar cada tramo, 1 € por orden y 0,1 % de spread. Todo en euros. La red aprende de forma continua; las carteras de cada tramo empiezan de cero.

- **Tramo A** (2024-06-01 → 2025-08-01): para elegir la frecuencia.
- **Tramo B** (2025-08-01 → hoy): validación. Es la estimación honesta.
- **IC**: correlación entre lo que la red prevé y lo que pasa (media de los mercados). 0 = no acierta más que el azar; 0,05-0,10 ya es mucho en mercados financieros.

## Tramo A

| Estrategia | Resultado | Caída máx. | Operaciones | Comisiones | Invertido de media | IC de la red |
|---|---:|---:|---:|---:|---:|---:|
| **Red: Una vez al día · 8 mercados** | **-79.9 %** | 80 % | 1028 | 1028 € | 59 % | +0.007 |
| **Red: Cada hora · criptos + dólar** | **-98.2 %** | 98 % | 899 | 899 € | 3 % | -0.009 |
| **Red: Semanal · 8 mercados** | **+20.0 %** | 32 % | 133 | 133 € | 46 % | +0.007 |
| Comprar y mantener repartido (8 mercados) | +71.6 % | 38 % | — | — | 100 % | — |
| Comprar y mantener repartido (criptos + dólar) | +86.8 % | 47 % | — | — | 100 % | — |
| Comprar y mantener repartido (8 mercados) | +71.6 % | 38 % | — | — | 100 % | — |
| Comprar y mantener solo Bitcoin | +65.6 % | — | 1 | 1 € | 100 % | — |
| Bot v2.1 (tendencia en Bitcoin) | +46.5 % | 18 % | 11 | 11 € | 61 % | — |

## Tramo B

| Estrategia | Resultado | Caída máx. | Operaciones | Comisiones | Invertido de media | IC de la red |
|---|---:|---:|---:|---:|---:|---:|
| **Red: Una vez al día · 8 mercados** | **-96.5 %** | 96 % | 940 | 940 € | 52 % | +0.021 |
| **Red: Cada hora · criptos + dólar** | **-98.0 %** | 98 % | 885 | 885 € | 4 % | +0.004 |
| **Red: Semanal · 8 mercados** | **-14.1 %** | 45 % | 138 | 138 € | 51 % | +0.021 |
| Comprar y mantener repartido (8 mercados) | -12.7 % | 37 % | — | — | 100 % | — |
| Comprar y mantener repartido (criptos + dólar) | -25.7 % | 54 % | — | — | 100 % | — |
| Comprar y mantener repartido (8 mercados) | -12.7 % | 37 % | — | — | 100 % | — |
| Comprar y mantener solo Bitcoin | -27.0 % | — | 1 | 1 € | 100 % | — |
| Bot v2.1 (tendencia en Bitcoin) | +2.2 % | 31 % | 9 | 9 € | 49 % | — |

## ¿Acierta la red en cada mercado? (tramo B)

| Mercado | Una vez al día · 8 mercados | Cada hora · criptos + dólar | Semanal · 8 mercados |
|---|---:|---:|---:|
| Bitcoin | IC -0.008 (z -0.1), dirección 53 % | IC -0.001 (z -0.0), dirección 48 % | IC -0.008 (z -0.1), dirección 53 % |
| Ethereum | IC +0.050 (z +0.5), dirección 53 % | IC +0.019 (z +0.4), dirección 50 % | IC +0.050 (z +0.5), dirección 53 % |
| BNB | IC +0.032 (z +0.3), dirección 53 % | IC -0.007 (z -0.1), dirección 49 % | IC +0.032 (z +0.3), dirección 53 % |
| XRP | IC +0.143 (z +1.3), dirección 51 % | IC -0.023 (z -0.5), dirección 50 % | IC +0.143 (z +1.3), dirección 51 % |
| Solana | IC +0.000 (z +0.0), dirección 49 % | IC +0.010 (z +0.2), dirección 50 % | IC +0.000 (z +0.0), dirección 49 % |
| Dólar | IC -0.052 (z -0.5), dirección 48 % | IC +0.025 (z +0.5), dirección 50 % | IC -0.052 (z -0.5), dirección 48 % |
| S&P 500 | IC +0.028 (z +0.3), dirección 58 % | — | IC +0.028 (z +0.3), dirección 58 % |
| IBEX 35 | IC -0.026 (z -0.2), dirección 50 % | — | IC -0.026 (z -0.2), dirección 50 % |

## Año a año (red: Semanal · 8 mercados)

| | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | Todo encadenado |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Red neuronal** | +120.6 % | -25.3 % | +40.1 % | +66.7 % | -26.2 % | -2.6 % | **+176.6 %** |
| Comprar y mantener repartido | +321.6 % | -43.8 % | +156.4 % | +88.3 % | -8.0 % | -3.3 % | **+916.5 %** |
| Solo Bitcoin | +75.7 % | -61.8 % | +148.5 % | +131.7 % | -16.6 % | -0.4 % | **+220.7 %** |
| Bot v2.1 (tendencia en Bitcoin) | +171.3 % | -31.3 % | +89.9 % | +85.2 % | -17.3 % | +15.5 % | **+526.8 %** |

| Caída máxima | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|
| **Red neuronal** | 56 % | 44 % | 24 % | 28 % | 33 % | 36 % |
| Comprar y mantener repartido | 53 % | 44 % | 19 % | 22 % | 34 % | 29 % |
