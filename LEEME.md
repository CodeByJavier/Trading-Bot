# Bot de trading simulado con IA propia

Un bot que **aprende solo** a partir de precios reales de Bitcoin, pero que opera con
**dinero ficticio**. No se conecta a ningún banco ni bróker y no puede gastar dinero de verdad.
Funciona gratis en GitHub las 24 horas, con un panel web que puedes mirar desde el móvil.

## Cómo funciona

1. **Datos:** descarga precios reales de la API pública de Binance (o de Coinbase, si Binance
   no responde). Gratis y sin cuenta.
2. **Indicadores:** convierte el precio en 9 números (tendencia, RSI, volatilidad, volumen...).
3. **Cerebro:** una pequeña IA propia (regresión logística) estima la probabilidad de que
   el precio suba **lo suficiente para pagar las comisiones** en las próximas 4 horas.
4. **Decisión:** si esa probabilidad es alta, compra; si baja, vende.
5. **Aprendizaje:** 4 horas después comprueba si acertó y corrige sus pesos.

## Ponerlo en marcha en GitHub (una sola vez)

1. Crea una cuenta gratuita en [github.com](https://github.com) si no tienes.
2. Crea un repositorio nuevo: botón **New**, nombre `bot-trading`, marcado como **Public**
   (las páginas web gratis de GitHub necesitan que sea público; solo contiene datos ficticios),
   **sin** README ni nada más.
3. Sube este proyecto (Claude te ayuda con este paso) con:
   `git remote add origin https://github.com/TU_USUARIO/bot-trading.git` y `git push -u origin main`.
4. En el repositorio: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
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
| `cambiar_umbrales` | Cambia cuánta seguridad necesita para comprar o vender. |
| `reiniciar_simulacion` | Empieza de cero; opcionalmente con otro capital o moneda (`ETHEUR`...). |

Solo tú puedes usar los controles, porque requieren tu sesión de GitHub.
Otros ajustes (comisiones, horizonte...) se cambian editando `config.py` en GitHub.

## Usarlo en tu ordenador (opcional)

| Comando | Qué hace |
|---|---|
| `python backtest.py` | Prueba el bot con los últimos ~6 meses de precios, en un minuto. |
| `python bot.py` | Simulación en directo en tu PC (Ctrl+C para parar). |
| `python estado.py` | Resumen en la terminal + `datos_bot/informe_bot.html`. |
| `python control.py pausar` | Las mismas acciones de control, en local. |

Ojo: si el bot ya funciona en GitHub, ejecuta antes `git pull` para traer su estado y
no mezcles las dos simulaciones.

## Cómo leer los resultados

- **Comprar y mantener:** lo que habrías ganado comprando al principio y no tocando nada.
  **Es la referencia a batir.** Si el bot no la supera, no aporta nada.
- **Aciertos vs. "respondiendo siempre lo mismo":** casi nunca hay subidas que cubran
  costes, así que decir siempre "no" ya acierta mucho. El cerebro solo es útil si supera
  esa cifra.
- **Hacen falta semanas o meses** de datos para sacar conclusiones. Una semana buena es suerte.

## Resultado del backtest (09/10/2026)

Con 200 € ficticios y 1 € de comisión por orden, de abril a octubre de 2026:
bot **−0,7 %** (8 operaciones) frente a comprar y mantener **+13,2 %**.
La primera versión (sin tener en cuenta comisiones) perdió un **94 %** en comisiones.

Cuidado con cambiar ajustes hasta que el backtest salga bien: eso solo encuentra la
configuración que encaja con el pasado ("sobreajuste"). La prueba de verdad es en directo.

## Cosas a vigilar

- GitHub desactiva las tareas programadas de repositorios sin actividad durante 60 días.
  El bot guarda su estado cada hora, lo que cuenta como actividad. Si el panel avisa de que no
  se actualiza, revisa la pestaña Actions.
- GitHub a veces retrasa unos minutos las tareas programadas. No pasa nada: al ejecutarse,
  el bot aprende de todas las velas que se haya perdido.

---

Esto es un proyecto de aprendizaje. No es asesoramiento financiero.
