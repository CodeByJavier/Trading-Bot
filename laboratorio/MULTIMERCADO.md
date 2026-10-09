# Laboratorio multimercado

Generado: 09/10/2026 22:11. Todo con dinero ficticio y precios reales. Capital: **1000 €** y 1 € por orden, así que una compra + venta necesita subir un 0.4 % para cubrir costes.

Mercados: **Bitcoin**, **Ethereum**, **BNB**, **XRP**, **Euro/dólar**, **S&P 500**, **IBEX 35**. El euro/dólar sale del par EUR/USDT de Binance (sigue al euro/dólar y cotiza 24 h). Las acciones son el ETF SPY (S&P 500) y el índice IBEX 35, con velas diarias de Yahoo Finance. Cada mercado se mide en su propia moneda (sin cambio de divisa).

## 1. ¿Aprende mejor la IA si estudia varios mercados a la vez?

Una sola IA aprende de todos los mercados de la variante, en orden temporal. Se mide su **habilidad** (cuánto mejor predice que el adivino ingenuo de ese mismo mercado) en el tramo A (2024-06-01 → 2025-08-01) y en el tramo B (2025-08-01 → hoy). z ≥ 2 = muy improbable que sea suerte.

### Velas de 1 hora, predice 24 h vista

**Habilidad prediciendo Bitcoin según de qué aprende:**

| Aprende de | Tramo A | Tramo B |
|---|---:|---:|
| Solo Bitcoin | +6.9 % (z +2.8) ✅ | +5.7 % (z +2.4) ✅ |
| Solo Bitcoin + Fear & Greed | +10.1 % (z +3.2) ✅ | +9.2 % (z +3.1) ✅ |
| 4 criptomonedas | +10.2 % (z +3.5) ✅ | +12.6 % (z +4.3) ✅ |
| 4 criptomonedas + Fear & Greed | +15.2 % (z +4.1) ✅ | +20.9 % (z +6.0) ✅ |
| 4 criptos + euro/dólar | +9.2 % (z +2.8) ✅ | +11.7 % (z +4.0) ✅ |

**Habilidad en cada mercado (4 criptos + euro/dólar):**

| Mercado | Tramo A | Tramo B |
|---|---:|---:|
| Bitcoin | +9.2 % (z +2.8) ✅ | +11.7 % (z +4.0) ✅ |
| Ethereum | +17.0 % (z +4.8) ✅ | +14.5 % (z +4.2) ✅ |
| BNB | +8.8 % (z +2.7) ✅ | +6.8 % (z +2.0) 🟡 |
| XRP | +17.5 % (z +4.9) ✅ | +16.0 % (z +4.3) ✅ |
| Euro/dólar | -11.8 % (z -2.4) 🔴 | -31.6 % (z -4.1) 🔴 |

### Velas diarias, predice 5 velas vista (en acciones, 5 sesiones)

**Habilidad prediciendo Bitcoin según de qué aprende:**

| Aprende de | Tramo A | Tramo B |
|---|---:|---:|
| Solo Bitcoin | +1.0 % (z +0.4) 🟡 | -1.8 % (z -0.9) ⚪ |
| 4 criptomonedas | -1.5 % (z -0.4) ⚪ | +0.9 % (z +0.3) 🟡 |
| Todo: criptos + euro/dólar + acciones | -0.1 % (z -0.0) ⚪ | +1.7 % (z +0.5) 🟡 |

**Habilidad en cada mercado (Todo: criptos + euro/dólar + acciones):**

| Mercado | Tramo A | Tramo B |
|---|---:|---:|
| Bitcoin | -0.1 % (z -0.0) ⚪ | +1.7 % (z +0.5) 🟡 |
| Ethereum | +2.1 % (z +0.5) 🟡 | +1.8 % (z +0.5) 🟡 |
| BNB | +5.2 % (z +1.5) 🟡 | +0.8 % (z +0.2) 🟡 |
| XRP | +5.1 % (z +0.9) 🟡 | +4.7 % (z +1.3) 🟡 |
| Euro/dólar | -10.0 % (z -1.6) ⚪ | -16.7 % (z -2.4) 🔴 |
| S&P 500 | +1.4 % (z +0.3) 🟡 | +2.1 % (z +0.4) 🟡 |
| IBEX 35 | -2.7 % (z -0.4) ⚪ | -6.1 % (z -0.7) ⚪ |

## 2. Regla de tendencia (50 días, margen 3 %) en cada mercado

Cada mercado por separado con 1000 € ficticios y 1 € por orden; cada año vuelve a empezar. En acciones, "50 días" son 50 sesiones de bolsa (unas 10 semanas).

| Mercado | Tendencia 2021–hoy | Comprar y mantener | Años que gana a mantener | Caída máx. media tendencia / mantener |
|---|---:|---:|:---:|---:|
| Bitcoin | **+516.5 %** | +165.6 % | 4/6 | 23 % / 39 % |
| Ethereum | **+612.9 %** | +233.0 % | 3/6 | 34 % / 52 % |
| BNB | **+3749.0 %** | +1893.0 % | 4/6 | 30 % / 46 % |
| XRP | **+127.4 %** | +412.9 % | 3/6 | 41 % / 54 % |
| Euro/dólar | **+0.6 %** | -10.0 % | 3/6 | 4 % / 9 % |
| S&P 500 | **+50.6 %** | +107.2 % | 2/6 | 9 % / 13 % |
| IBEX 35 | **-2.2 %** | +118.8 % | 0/6 | 14 % / 12 % |

### Repartiendo los 1000 € entre varios mercados (regla de tendencia en cada uno)

| Cartera | Comisión | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | Todo encadenado | Peor caída de un año |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Solo Bitcoin (1000 €) | 1 € | +171.3 % | -31.3 % | +89.9 % | +85.2 % | -17.3 % | +13.6 % | **+516.5 %** | 32 % |
| Solo Bitcoin (1000 €) | 0,1 % | +171.4 % | -30.9 % | +90.3 % | +85.9 % | -16.8 % | +14.0 % | **+529.5 %** | 31 % |
| ↳ misma cartera, comprar y mantener | 1 € | +68.2 % | -63.5 % | +147.5 % | +124.1 % | -18.8 % | -3.9 % | +165.6 % | 64 % |
| 4 criptos (250 € cada una) | 1 € | +584.7 % | -23.2 % | +15.9 % | +94.2 % | +1.6 % | +1.3 % | **+1119.2 %** | 32 % |
| 4 criptos (250 € cada una) | 0,1 % | +588.5 % | -20.1 % | +19.9 % | +100.6 % | +4.7 % | +4.2 % | **+1343.9 %** | 32 % |
| ↳ misma cartera, comprar y mantener | 1 € | +529.4 % | -60.2 % | +82.5 % | +139.4 % | -16.8 % | -13.6 % | +686.5 % | 63 % |
| Mezcla: Bitcoin + Ethereum + euro/dólar + S&P 500 + IBEX (200 € cada uno) | 1 € | +98.7 % | -21.1 % | +20.0 % | +20.5 % | +10.4 % | +8.5 % | **+171.5 %** | 22 % |
| Mezcla: Bitcoin + Ethereum + euro/dólar + S&P 500 + IBEX (200 € cada uno) | 0,1 % | +102.0 % | -18.0 % | +23.5 % | +24.0 % | +12.9 % | +10.4 % | **+216.2 %** | 20 % |
| ↳ misma cartera, comprar y mantener | 1 € | +105.8 % | -33.2 % | +54.8 % | +40.0 % | +6.3 % | -1.0 % | +213.6 % | 38 % |

## 3. ¿Se mueven juntos? (rendimientos diarios 2021–hoy)

Correlación: +1 = se mueven igual; 0 = no tienen relación; −1 = van al revés. Para diversificar sirven los mercados con correlación baja.

| | Bitcoin | Ethereum | BNB | XRP | Euro/dólar | S&P 500 | IBEX 35 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Bitcoin** | +1.00 | +0.80 | +0.63 | +0.57 | +0.12 | +0.35 | +0.13 |
| **Ethereum** | +0.80 | +1.00 | +0.63 | +0.58 | +0.16 | +0.37 | +0.16 |
| **BNB** | +0.63 | +0.63 | +1.00 | +0.48 | +0.10 | +0.24 | +0.11 |
| **XRP** | +0.57 | +0.58 | +0.48 | +1.00 | +0.11 | +0.25 | +0.09 |
| **Euro/dólar** | +0.12 | +0.16 | +0.10 | +0.11 | +1.00 | +0.25 | +0.22 |
| **S&P 500** | +0.35 | +0.37 | +0.24 | +0.25 | +0.25 | +1.00 | +0.37 |
| **IBEX 35** | +0.13 | +0.16 | +0.11 | +0.09 | +0.22 | +0.37 | +1.00 |

**Cuando Bitcoin cae más de un 5 % en un día, ¿qué hacen los demás ese mismo día?**

| Mercado | Días comparados | Rendimiento medio ese día |
|---|---:|---:|
| Ethereum | 82 | -8.7 % |
| BNB | 82 | -7.7 % |
| XRP | 82 | -7.9 % |
| Euro/dólar | 82 | -0.1 % |
| S&P 500 | 80 | -0.9 % |
| IBEX 35 | 81 | -0.4 % |
