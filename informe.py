"""
Genera una página HTML con la gráfica del bot frente a "comprar y mantener".
Se abre con doble clic en cualquier navegador.
"""
import html


def _grafica_svg(serie_bot, serie_ref, ancho=900, alto=320, margen=50):
    puntos = len(serie_bot)
    if puntos < 2:
        return "<p>Aún no hay datos suficientes para la gráfica.</p>"
    paso = max(1, puntos // 600)
    indices = list(range(0, puntos, paso))
    if indices[-1] != puntos - 1:
        indices.append(puntos - 1)

    todos = [serie_bot[i] for i in indices] + [serie_ref[i] for i in indices]
    minimo, maximo = min(todos), max(todos)
    if maximo - minimo < 1e-9:
        maximo = minimo + 1

    def x(i):
        return margen + (ancho - 2 * margen) * i / (puntos - 1)

    def y(v):
        return alto - margen + (margen * 2 - alto) * (v - minimo) / (maximo - minimo)

    def linea(serie, clase):
        pts = " ".join(f"{x(i):.1f},{y(serie[i]):.1f}" for i in indices)
        return f'<polyline class="{clase}" points="{pts}" />'

    etiquetas = ""
    for k in range(5):
        v = minimo + (maximo - minimo) * k / 4
        etiquetas += (f'<text x="{margen - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{v:.0f} €</text>'
                      f'<line class="rejilla" x1="{margen}" x2="{ancho - margen}" '
                      f'y1="{y(v):.1f}" y2="{y(v):.1f}" />')

    return (f'<svg viewBox="0 0 {ancho} {alto}" role="img">{etiquetas}'
            f'{linea(serie_ref, "ref")}{linea(serie_bot, "bot")}</svg>')


def generar_informe(ruta, titulo, serie_bot, serie_ref, resumen, aprendido, operaciones):
    filas_resumen = "".join(
        f"<tr><th>{html.escape(k)}</th><td>{html.escape(str(v))}</td></tr>" for k, v in resumen)
    filas_aprendido = "".join(
        f"<tr><td>{html.escape(n)}</td><td>{w:+.3f}</td><td>{html.escape(o)}</td></tr>"
        for n, w, o in aprendido)
    filas_ops = ""
    for op in reversed(operaciones[-100:]):
        resultado = "" if op["resultado"] is None else f'{op["resultado"]:+.2f} €'
        clase = "" if op["resultado"] is None else ("gana" if op["resultado"] >= 0 else "pierde")
        filas_ops += (f'<tr><td>{html.escape(op["fecha"])}</td><td>{op["tipo"]}</td>'
                      f'<td>{op["precio"]:,.2f} €</td><td>{op["comision"]:.2f} €</td>'
                      f'<td class="{clase}">{resultado}</td></tr>')

    pagina = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titulo)}</title>
<style>
:root {{ --fondo:#fafaf9; --texto:#1c1917; --suave:#78716c; --borde:#e7e5e4;
        --bot:#2563eb; --ref:#a8a29e; --gana:#15803d; --pierde:#b91c1c; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --fondo:#1c1917; --texto:#f5f5f4; --suave:#a8a29e; --borde:#44403c;
          --bot:#60a5fa; --ref:#78716c; --gana:#4ade80; --pierde:#f87171; }} }}
body {{ background:var(--fondo); color:var(--texto); font-family:system-ui,sans-serif;
       max-width:960px; margin:0 auto; padding:24px 16px; line-height:1.5; }}
h1 {{ font-size:1.5rem; margin:0 0 4px; }} h2 {{ font-size:1.1rem; margin-top:32px; }}
.nota {{ color:var(--suave); font-size:.9rem; }}
svg {{ width:100%; height:auto; }} svg text {{ fill:var(--suave); font-size:11px; }}
.rejilla {{ stroke:var(--borde); }} polyline {{ fill:none; stroke-width:2; }}
.bot {{ stroke:var(--bot); }} .ref {{ stroke:var(--ref); stroke-dasharray:4 3; }}
.leyenda span {{ margin-right:16px; }} .leyenda b {{ display:inline-block; width:14px; height:3px;
  vertical-align:middle; margin-right:6px; }}
table {{ border-collapse:collapse; width:100%; font-size:.9rem; }}
th, td {{ text-align:left; padding:6px 8px; border-bottom:1px solid var(--borde); }}
.gana {{ color:var(--gana); }} .pierde {{ color:var(--pierde); }}
.tabla {{ overflow-x:auto; }}
</style></head><body>
<h1>{html.escape(titulo)}</h1>
<p class="nota">Simulación con dinero ficticio y precios reales. No es asesoramiento financiero.</p>
<p class="leyenda"><span><b style="background:var(--bot)"></b>Bot</span>
<span><b style="background:var(--ref)"></b>Comprar y mantener (referencia)</span></p>
{_grafica_svg(serie_bot, serie_ref)}
<h2>Resumen</h2><div class="tabla"><table>{filas_resumen}</table></div>
<h2>Lo que ha aprendido el cerebro</h2>
<p class="nota">Peso positivo: si el indicador sube, cree que el precio subirá. Cuanto mayor el número, más se fía.</p>
<div class="tabla"><table><tr><th>Indicador</th><th>Peso</th><th>Interpretación</th></tr>{filas_aprendido}</table></div>
<h2>Operaciones (más recientes primero)</h2>
<div class="tabla"><table><tr><th>Fecha</th><th>Tipo</th><th>Precio</th><th>Comisión</th><th>Resultado</th></tr>
{filas_ops or '<tr><td colspan="5">Todavía no ha operado.</td></tr>'}</table></div>
</body></html>"""
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(pagina)
