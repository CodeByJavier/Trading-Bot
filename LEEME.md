# Bot de trading simulado con IA propia

Un bot que opera con **dinero ficticio** sobre precios reales de Bitcoin y tiene una **IA propia
que aprende sola**. No se conecta a ningún banco ni bróker y no puede gastar dinero de verdad.
Funciona gratis en GitHub las 24 horas, con un panel web que puedes mirar desde el móvil.

## Cómo funciona (versión 2.1)

1. **Datos:** precios reales de Binance (o Coinbase si Binance no responde) y el índice
   **Fear & Greed** del mercado cripto. Gratis y sin cuenta.
2. **Quién decide: la regla de tendencia.** Una vez al día mira si el precio de cierre está por encima
   de su media de 50 días. Si la supera en un 3 %, compra; si cae un 3 % por debajo, vende.
   Es lo único que en el laboratorio se comportó mejor que comprar y mantener de forma consistente.
3. **La IA, en prácticas:** cada hora estima la probabilidad de que el precio suba lo suficiente para
   pagar las comisiones en las próximas 24 h (con 9 indicadores de precio + Fear & Greed). Aprende de
   **Bitcoin, Ethereum, BNB y XRP** a la vez, pero se la evalúa con Bitcoin. Comprueba sus aciertos y se
   corrige sola, pero **no compra ni vende** hasta que demuestre que mejora los resultados.
4. **Dinero ficticio:** 1.000 € (en `config.py`, `CAPITAL_INICIAL`).

Más detalles del porqué en [CAMBIOS.md](CAMBIOS.md) y [laboratorio/RESULTADOS.md](laboratorio/RESULTADOS.md).

## Ponerlo en marcha en GitHub (una sola vez)

1. Crea una cuenta gratuita en [github.com](https://github.com) si no tienes.
2. Crea un repositorio nuevo: botón **New**, nombre `bot-trading`, marcado como **Public**
   (las páginas web gratis de GitHub necesitan que sea público; solo contiene datos ficticios),
   **sin** README ni nada más.
3. Sube este proyecto (Claude te ayuda con este paso) con:
   `git remote add origin https://github.com/TU_USUARIO/bot-trading.git` y `git push -u origin main`.
4. En el repositorio: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
   ⚠ Si se queda en *Deploy from a branch*, la web da **error 404** (el panel lo publica el bot, no la rama).
5. Pestaña **Actions** → si te lo pide, pulsa *I understand my workflows, go ahead and enable them*.
   Luego elige **Bot cada hora → Run workflow** para la primera ejecución (tarda 1-2 minutos).
6. Tu panel estará en `https://TU_USUARIO.github.io/bot-trading/`.

A partir de ahí, GitHub ejecuta el bot cada hora aunque tu ordenador esté apagado.

## Controlar el bot

En el panel, pulsa **Abrir controles** → **Run workflow**, elige la acción y confirma:

| Acción | Qué hace |
|---|---|
| `pausar` | Deja de operar, pero sigue aprendiendo. |
| `reanudar` | Vuelve a operar. |
| `vender_y_pausar` | Vende lo que tenga al precio actual y se pausa. |
| `cambiar_umbrales` | Cambia cuánta seguridad necesita la IA (solo influye si la IA decide). |
| `reiniciar_simulacion` | Empieza de cero; opcionalmente con otro capital o moneda (`ETHEUR`...). |

Solo tú puedes usar los controles, porque requieren tu sesión de GitHub.
Otros ajustes (estrategia, comisiones, media de la tendencia...) se cambian editando `config.py`.
Si cambias cómo piensa o decide el bot, sube `VERSION_MODELO`: la simulación anterior se guarda en
`datos_bot/archivo/` y empieza una nueva.

## Usarlo en tu ordenador (opcional)

| Comando | Qué hace |
|---|---|
| `python laboratorio.py` | Prueba ideas con la historia real (unos 2 minutos). Ver abajo. |
| `python multimercado.py` | Compara criptomonedas, euro/dólar y bolsa (unos 5 minutos) → `laboratorio/MULTIMERCADO.md`. |
| `python bot.py` | Simulación en directo en tu PC (Ctrl+C para parar). |
| `python estado.py` | Resumen en la terminal + `datos_bot/informe_bot.html`. |
| `python control.py pausar` | Las mismas acciones de control, en local. |

Ojo: si el bot ya funciona en GitHub, ejecuta antes `git pull` para traer su estado y
no mezcles las dos simulaciones.

## ¿Está aprendiendo de verdad?

Antes de conocer cada resultado, el bot guarda su predicción y la de un **adivino ingenuo** que
siempre dice "lo que suele pasar". Si el cerebro no se equivoca menos que el adivino, no aprende nada útil.

- **`INFORME_APRENDIZAJE.md`**: el veredicto (✅ aprende, 🟡 indicios, ⚪ no supera al adivino,
  🔴 peor), tabla por periodos y por semanas, evolución de los pesos y cuándo revisar.
  Se actualiza cada hora y se lee directamente en GitHub.
- **`datos_bot/diario.jsonl`**: una línea por día con todas las métricas y los pesos del cerebro.
- **`CAMBIOS.md`**: qué se cambió en cada versión del modelo y por qué.

**Ritmo de revisión:** la IA predice a 24 h vista, así que hace falta **un mes** para tener
unas 30 predicciones independientes. No tocar nada antes; después, revisar una vez al mes y cambiar
una sola cosa cada vez (subiendo `VERSION_MODELO`).
Para revisarlo con Claude: `git pull` y pedirle que lea esos tres archivos.

## Cómo leer los resultados

- **Comprar y mantener:** lo que habrías ganado comprando al principio y no tocando nada.
  **Es la referencia a batir.** Si el bot no la supera, no aporta nada.
- **Aciertos vs. "respondiendo siempre lo mismo":** casi nunca hay subidas que cubran
  costes, así que decir siempre "no" ya acierta mucho. El cerebro solo es útil si supera
  esa cifra.
- **Hacen falta semanas o meses** de datos para sacar conclusiones. Una semana buena es suerte.

## El laboratorio: probar ideas sin tocar el bot

`python laboratorio.py` prueba varias ideas con la historia real y escribe
[laboratorio/RESULTADOS.md](laboratorio/RESULTADOS.md). Para no engañarse:

- Recorre la historia vela a vela: decide con lo que sabía en cada momento y solo después ve qué pasó.
- **Tramo A** (jun 2024 – jul 2025) para elegir la mejor idea; **tramo B** (ago 2025 – hoy) para
  validarla. Lo que consigue en B es la estimación honesta.
- **Año a año** desde 2021 (con velas diarias), para ver mercados alcistas y bajistas.
- Variantes de la misma idea (robustez): si solo funciona con una cifra concreta, es casualidad.

Para probar una idea tuya, añádela a la lista `EXPERIMENTOS` de `laboratorio.py` (o pídeselo a Claude).

**Resumen a 09/10/2026:** la IA decidiendo no ganó dinero en ninguna variante (las comisiones se
comen su pequeña ventaja). La regla de tendencia de 50 días perdió −4 % en el tramo B frente a −27 %
de mantener, y de 2021 a 2026 gana a mantener en el total con caídas mucho menores. **No gana
siempre**: en años bajistas también pierde (menos) y en años muy alcistas puede ganar menos.

## Cosas a vigilar

- GitHub desactiva las tareas programadas de repositorios sin actividad durante 60 días.
  El bot guarda su estado cada hora, lo que cuenta como actividad. Si el panel avisa de que no
  se actualiza, revisa la pestaña Actions.
- GitHub a veces retrasa unos minutos las tareas programadas. No pasa nada: al ejecutarse,
  el bot aprende de todas las velas que se haya perdido.

---

Esto es un proyecto de aprendizaje. No es asesoramiento financiero.
