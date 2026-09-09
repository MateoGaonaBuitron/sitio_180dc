"""
build.py — Genera el sitio estático del Portal de Transparencia 180DC PUCP.
Diseño: editorial financial report.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from helpers import cargar_mes, fmt_soles, InformeMes  # noqa: E402
from config_mes import NARRATIVA  # noqa: E402

OUT_DIR = ROOT / "site"
DATA_DIR = ROOT / "data"

# =============================================================================
# CONFIGURACIÓN DE CICLOS  ← lo único que cambia al pasar de ciclo
# =============================================================================
# Para empezar un ciclo nuevo: AGREGA un bloque nuevo al final de CICLOS (no
# borres el anterior — el portal conserva el histórico) y apunta CICLO_ACTIVO
# al ciclo nuevo. Ver README.md, sección 5.
#
# El "slug" es el nombre del archivo web y debe ser ÚNICO en todo el portal.
# Si un mes se repite en un ciclo posterior (ej. otro Marzo), usa un slug con
# el ciclo al final: "marzo-2027-1".
CICLOS = [
    {
        "ciclo": "2026-1",
        "meses": [
            {"mes": "Marzo", "slug": "marzo", "xlsx": "transacciones_marzo.xlsx"},
            {"mes": "Abril", "slug": "abril", "xlsx": "transacciones_abril.xlsx"},
            {"mes": "Mayo", "slug": "mayo", "xlsx": "transacciones_mayo.xlsx"},
            {"mes": "Junio", "slug": "junio", "xlsx": "transacciones_junio.xlsx"},
            {"mes": "Julio", "slug": "julio", "xlsx": "transacciones_julio.xlsx"},
        ],
    },
    {
        "ciclo": "2026-2",
        "meses": [
            {"mes": "Agosto", "slug": "agosto", "xlsx": "transacciones_agosto.xlsx"},
            {"mes": "Septiembre (prueba)", "slug": "septiembre-prueba", "prueba": True},
        ],
    },
]

# Ciclo que el portal muestra como vigente (cabecera, saldo actual del inicio).
CICLO_ACTIVO = "2026-2"

import re
import math

_MD_BOLD = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)

# Mes a abreviatura corta para fechas
_MES_ABREV = {
    "01": "Ene", "02": "Feb", "03": "Mar", "04": "Abr", "05": "May",
    "06": "Jun", "07": "Jul", "08": "Ago", "09": "Set", "10": "Oct",
    "11": "Nov", "12": "Dic",
}

def esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def md(s):
    return _MD_BOLD.sub(r"<strong>\1</strong>", esc(s))

def fmt_fecha_corta(fecha_str):
    """'24/03/2026' -> '24 Mar' · '13/03/2026 - 18/03/2026' -> '13–18 Mar'"""
    if not fecha_str:
        return ""
    s = str(fecha_str).strip()
    # rango
    if "-" in s and s.count("/") >= 4:
        parts = [p.strip() for p in s.split("-")]
        try:
            d1, m1, _ = parts[0].split("/")
            d2, m2, _ = parts[1].split("/")
            if m1 == m2:
                return f"{int(d1)}–{int(d2)} {_MES_ABREV.get(m1, m1)}"
            return f"{int(d1)} {_MES_ABREV.get(m1, m1)}–{int(d2)} {_MES_ABREV.get(m2, m2)}"
        except Exception:
            return s
    # individual
    parts = s.split("/")
    if len(parts) == 3:
        d, m, _ = parts
        return f"{int(d)} {_MES_ABREV.get(m, m)}"
    return s


def svg_donut(labels, values, colores, total_label, size=240):
    if not values or sum(values) == 0:
        return '<div class="chart-empty">Sin datos para mostrar</div>'
    total = sum(values)
    cx, cy = size/2, size/2
    r_out, r_in = size*0.42, size*0.42*0.66
    paths = []
    start = -math.pi/2
    for v, c in zip(values, colores):
        frac = v/total
        end = start + frac * 2*math.pi
        x1, y1 = cx + r_out*math.cos(start), cy + r_out*math.sin(start)
        x2, y2 = cx + r_out*math.cos(end),   cy + r_out*math.sin(end)
        x3, y3 = cx + r_in*math.cos(end),    cy + r_in*math.sin(end)
        x4, y4 = cx + r_in*math.cos(start),  cy + r_in*math.sin(start)
        large = 1 if frac > 0.5 else 0
        d = (f"M {x1:.2f} {y1:.2f} "
             f"A {r_out:.2f} {r_out:.2f} 0 {large} 1 {x2:.2f} {y2:.2f} "
             f"L {x3:.2f} {y3:.2f} "
             f"A {r_in:.2f} {r_in:.2f} 0 {large} 0 {x4:.2f} {y4:.2f} Z")
        paths.append(f'<path d="{d}" fill="{c}"/>')
        start = end
    legend_rows = []
    for lbl, v, c in zip(labels, values, colores):
        pct = v/total*100
        legend_rows.append(
            f'<li>'
            f'<span class="dot" style="background:{c}"></span>'
            f'<span class="lbl">{esc(lbl)}</span>'
            f'<span class="pct">{pct:.0f}%</span>'
            f'<span class="val">{fmt_soles(v)}</span>'
            f'</li>'
        )
    return (
        f'<div class="donut-block">'
        f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" preserveAspectRatio="xMidYMid meet">'
        f'{"".join(paths)}'
        f'<text x="{cx}" y="{cy-6}" text-anchor="middle" font-size="10" letter-spacing="1" fill="#9CA3AF">TOTAL</text>'
        f'<text x="{cx}" y="{cy+14}" text-anchor="middle" font-size="18" font-weight="700" fill="#0A0A0A">{total_label}</text>'
        f'</svg>'
        f'<ul class="donut-legend">{"".join(legend_rows)}</ul>'
        f'</div>'
    )


def svg_barras(labels, values, colores, width=420, height=240):
    pad_l, pad_r, pad_t, pad_b = 48, 12, 24, 44
    w = width - pad_l - pad_r
    h = height - pad_t - pad_b
    max_v = max(values) if values else 1
    if max_v == 0:
        max_v = 1
    step_candidates = [10, 20, 50, 100, 200, 500, 1000, 2000]
    step = next((s for s in step_candidates if max_v/s <= 5), max_v)
    nice = math.ceil(max_v / step) * step
    n = len(values)
    bw = w / n * 0.45
    gap = w / n
    bars = []
    labels_x = []
    for i, (lbl, v, c) in enumerate(zip(labels, values, colores)):
        x = pad_l + gap*i + (gap - bw)/2
        bh = (v / nice) * h if nice > 0 else 0
        y = pad_t + h - bh
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" fill="{c}"/>'
            f'<text x="{x + bw/2:.1f}" y="{y - 8:.1f}" text-anchor="middle" '
            f'font-size="11" font-weight="700" fill="#0A0A0A">{fmt_soles(v)}</text>'
        )
        labels_x.append(
            f'<text x="{x + bw/2:.1f}" y="{pad_t + h + 24:.1f}" text-anchor="middle" '
            f'font-size="11" fill="#6B7280" font-weight="500" letter-spacing="0.3">{esc(lbl)}</text>'
        )
    yticks = []
    # Marcas cada "step" (no en cuartos): así siempre quedan cifras redondas.
    for k in range(int(round(nice / step)) + 1):
        val = step * k
        y = pad_t + h - (val/nice)*h
        yticks.append(
            f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l+w}" y2="{y:.1f}" '
            f'stroke="#F3F4F6"/>'
            f'<text x="{pad_l-8}" y="{y+3:.1f}" text-anchor="end" font-size="10" fill="#9CA3AF">{val:.0f}</text>'
        )
    # eje base
    yticks.append(f'<line x1="{pad_l}" y1="{pad_t+h:.1f}" x2="{pad_l+w}" y2="{pad_t+h:.1f}" stroke="#D1D5DB"/>')
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" preserveAspectRatio="xMidYMid meet">'
        f'<text x="{pad_l-32}" y="{pad_t-8}" font-size="10" fill="#9CA3AF" letter-spacing="1">S/</text>'
        f'{"".join(yticks)}{"".join(bars)}{"".join(labels_x)}'
        f'</svg>'
    )


def brand_mark(asset_prefix="."):
    """Logo 180DC desde imagen."""
    return (
        f'<img class="brand-mark" src="{asset_prefix}/assets/180.jpg" '
        f'width="28" height="28" alt="180DC PUCP">'
    )


def nav_html(meses, slug_actual=None):
    """Navegación de una página de mes: los meses de SU ciclo."""
    items = ['<a href="../index.html">Inicio</a>']
    for m in meses:
        cls = ' class="active"' if m["slug"] == slug_actual else ""
        items.append(f'<a href="{m["slug"]}.html"{cls}>{m["mes"]}</a>')
    return f'<nav class="main-nav">{"".join(items)}</nav>'


def nav_home(meses):
    """Navegación del índice: los meses del ciclo vigente."""
    items = ['<a class="active" href="index.html">Inicio</a>']
    for m in meses:
        items.append(f'<a href="meses/{m["slug"]}.html">{m["mes"]}</a>')
    return f'<nav class="main-nav">{"".join(items)}</nav>'


def layout(titulo, body, ciclo, meses_nav, slug_actual=None, asset_prefix="."):
    nav = (nav_home(meses_nav) if slug_actual is None
           else nav_html(meses_nav, slug_actual))
    home_href = "index.html" if slug_actual is None else "../index.html"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(titulo)}</title>
<link rel="icon" type="image/jpeg" href="{asset_prefix}/assets/180.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset_prefix}/assets/style.css">
</head>
<body>
  <header class="site-header">
    <div class="header-inner wrap">
      <a class="brand" href="{home_href}">
        {brand_mark(asset_prefix)}
        <div class="brand-text">
          <span class="brand-name">180DC PUCP</span>
          <span class="brand-sub">Transparencia financiera</span>
        </div>
      </a>
      {nav}
      <div class="header-status">
        <span class="status-dot"></span>
        <span>Ciclo {ciclo}</span>
      </div>
    </div>
  </header>
  <main class="wrap">
    {body}
  </main>
  <footer>
    <div class="wrap footer-inner">
      <div>
        <p class="footer-title">180 Degrees Consulting PUCP</p>
        <p class="footer-sub">Portal de Transparencia Financiera · Ciclo {ciclo}</p>
      </div>
      <div class="footer-meta">
        <p>Información derivada del Registro de Transacciones mensual.</p>
        <p>Consultas: área financiera.</p>
      </div>
    </div>
  </footer>
</body>
</html>
"""


# =============================================================================
# Componente: fila de transacción
# =============================================================================
def render_fila(*, titulo, monto, fecha, categoria, descripcion, tipo,
                badge_txt=None):
    """tipo: 'in' | 'op' | 'inv'"""
    signo = "+" if tipo == "in" else "−"
    monto_cls = {"in": "in", "op": "op", "inv": "inv"}[tipo]
    badge_html = ""
    if badge_txt:
        badge_html = f'<span class="row-badge {monto_cls}">{esc(badge_txt)}</span>'
    fecha_corta = fmt_fecha_corta(fecha)
    meta_parts = []
    if badge_html:
        meta_parts.append(badge_html)
    if fecha_corta:
        meta_parts.append(f'<span class="row-meta-item">{esc(fecha_corta)}</span>')
    if categoria:
        meta_parts.append(f'<span class="row-meta-item">{esc(categoria)}</span>')
    meta_html = ('<div class="row-meta">'
                 + '<span class="row-sep"></span>'.join(meta_parts)
                 + '</div>') if meta_parts else ""
    return f"""
    <article class="tx-row tx-{monto_cls}">
      <div class="tx-main">
        <div class="tx-head">
          <h4 class="tx-title">{esc(titulo)}</h4>
          <div class="tx-monto {monto_cls}">{signo} {fmt_soles(monto)}</div>
        </div>
        {meta_html}
        <p class="tx-desc">{esc(descripcion)}</p>
      </div>
    </article>
    """


# =============================================================================
# Página mes
# =============================================================================
def render_mes(info: InformeMes, slug: str, narrativa: dict, xlsx_filename: str,
               meses_ciclo: list) -> str:
    # delta de saldo
    delta = info.saldo_final - info.saldo_inicial
    delta_sign = "+" if delta >= 0 else "−"
    delta_cls = "up" if delta >= 0 else "down"

    # ---- Hero saldo
    hero_saldo = f"""
    <section class="hero-saldo">
      <div class="hero-saldo-main">
        <p class="eyebrow">Saldo final del mes</p>
        <div class="hero-saldo-num">{fmt_soles(info.saldo_final)}</div>
        <p class="hero-saldo-delta {delta_cls}">
          <span class="arrow">{'↑' if delta >= 0 else '↓'}</span>
          {delta_sign} {fmt_soles(abs(delta))} vs. saldo inicial
        </p>
      </div>
      <div class="hero-saldo-calc">
        <p class="eyebrow">Cálculo</p>
        <dl class="calc-list">
          <div><dt>Saldo inicial</dt><dd>{fmt_soles(info.saldo_inicial)}</dd></div>
          {"" if info.ingresos == 0 else f'<div class="op"><dt><span class="op-sign verde">+</span> Ingresos</dt><dd>{fmt_soles(info.ingresos)}</dd></div>'}
          <div class="op"><dt><span class="op-sign rojo">−</span> Egresos operativos</dt><dd>{fmt_soles(info.egresos_op)}</dd></div>
          {"" if info.inversion == 0 else f'<div class="op"><dt><span class="op-sign ambar">−</span> Inversión IME</dt><dd>{fmt_soles(info.inversion)}</dd></div>'}
          <div class="total"><dt>Saldo final</dt><dd>{fmt_soles(info.saldo_final)}</dd></div>
        </dl>
      </div>
    </section>
    """

    # ---- Stat strip
    stat_items = [f'''<div class="stat">
        <span class="stat-label">Saldo inicial</span>
        <span class="stat-value">{fmt_soles(info.saldo_inicial)}</span>
      </div>''']
    if info.ingresos > 0 or narrativa.get("prueba"):
        stat_items.append(f'''<div class="stat">
        <span class="stat-label">Ingresos</span>
        <span class="stat-value verde">{fmt_soles(info.ingresos)}</span>
      </div>''')
    stat_items.append(f'''<div class="stat">
        <span class="stat-label">Egresos operativos</span>
        <span class="stat-value rojo">{fmt_soles(info.egresos_op)}</span>
      </div>''')
    if info.inversion > 0:
        stat_items.append(f'''<div class="stat">
        <span class="stat-label">Inversión IME</span>
        <span class="stat-value ambar">{fmt_soles(info.inversion)}</span>
      </div>''')
    deuda = narrativa.get("deuda")
    if deuda:
        stat_items.append(f'''<div class="stat">
        <span class="stat-label">Deuda pendiente</span>
        <span class="stat-value ambar">{fmt_soles(deuda["monto"])}</span>
      </div>''')
    stat_strip = f"""
    <div class="stat-strip">
      {''.join(stat_items)}
    </div>
    """

    # ---- Ingresos
    fuentes = narrativa.get("fuentes_ingresos", [])
    filas_ingreso = []
    for f in fuentes:
        filas_ingreso.append(render_fila(
            titulo=f['nombre'],
            monto=f['monto'],
            fecha=f.get('fecha', ''),
            categoria=f.get('categoria_ui', ''),
            descripcion=f.get('detalle', ''),
            tipo='in',
            badge_txt='Ingreso',
        ))
    if not filas_ingreso:
        filas_ingreso.append('<p class="muted">No se registran ingresos en el mes.</p>')

    # ---- Egresos
    egresos_cfg = sorted(narrativa.get("egresos", []), key=lambda e: e["monto"], reverse=True)
    filas_egreso = []
    for e in egresos_cfg:
        tipo = 'inv' if e.get('es_inversion') else 'op'
        badge = 'Inversión IME' if e.get('es_inversion') else 'Operativo'
        filas_egreso.append(render_fila(
            titulo=e['titulo'],
            monto=e['monto'],
            fecha=e.get('fecha', ''),
            categoria=e.get('categoria_ui', ''),
            descripcion=e.get('para_que', ''),
            tipo=tipo,
            badge_txt=badge,
        ))
    if not filas_egreso:
        filas_egreso.append('<p class="muted">No se registran egresos en el mes.</p>')

    # ---- Subtotal headers
    egresos_total = info.egresos_op + info.inversion

    # ---- Pasivo (préstamo pendiente de reposición)
    deuda_html = ""
    if deuda:
        deuda_html = f"""
    <section class="section">
      <div class="section-head">
        <div>
          <p class="section-eyebrow">Pasivo</p>
          <h3 class="section-title-big">Préstamo pendiente</h3>
        </div>
        <div class="section-total" style="color:var(--ambar)">
          <span class="total-label">Deuda</span>
          <span class="total-value" style="color:var(--ambar)">{fmt_soles(deuda["monto"])}</span>
        </div>
      </div>
      <div class="info-box">
        <strong>{esc(deuda["titulo"])}</strong>
        {md(deuda["detalle"])}
      </div>
    </section>
    """

    # ---- Charts
    dist = {}
    for e in egresos_cfg:
        c = e.get("categoria_ui", "Otros")
        dist[c] = dist.get(c, 0) + e["monto"]
    dist_items = sorted(dist.items(), key=lambda x: x[1], reverse=True)
    dist_labels = [k for k,_ in dist_items]
    dist_data = [v for _,v in dist_items]
    paleta = ["#7AB929", "#1F2937", "#F59E0B", "#3B82F6", "#DC2626", "#8B5CF6", "#6B7280"]
    color_list = [paleta[i % len(paleta)] for i in range(len(dist_labels))]
    donut_svg = svg_donut(dist_labels, dist_data, color_list,
                          fmt_soles(sum(dist_data)) if dist_data else "S/ 0")

    cmp_labels = ["Ingresos", "Egresos op.", "Inversión"]
    cmp_values = [info.ingresos, info.egresos_op, info.inversion]
    cmp_colors = ["#7AB929", "#DC2626", "#F59E0B"]
    barras_svg = svg_barras(cmp_labels, cmp_values, cmp_colors)

    # ---- Análisis (pull-quote style)
    nota = narrativa.get("nota_cierre", "")
    cierre_html = ""
    if nota:
        cierre_html = f"""
        <section class="analisis-section">
          <p class="section-eyebrow">Análisis</p>
          <h3 class="section-title-big">Comentario del mes</h3>
          <blockquote class="pullquote">{md(nota)}</blockquote>
        </section>
        """

    # ---- Descarga
    descarga_html = f"""
    <div class="descarga">
      <div class="descarga-info">
        <p class="eyebrow">Archivo fuente</p>
        <h4>Registro de Transacciones — {info.mes} {info.ciclo}</h4>
        <p>Verifica línea por línea. Los datos del informe se generan
           automáticamente a partir de este archivo.</p>
      </div>
      <a class="btn-descarga" href="../downloads/{esc(xlsx_filename)}" download>
        <span>Descargar Excel</span>
        <span class="btn-arrow">↓</span>
      </a>
    </div>
    """
    if narrativa.get("prueba"):
        descarga_html = '<p class="muted">Reporte de prueba sin movimientos. No corresponde a un registro contable real ni tiene Excel descargable.</p>'

    # ---- Info box inversión
    info_box_inv = ""
    if info.inversion > 0:
        info_box_inv = """
        <div class="info-box">
          <strong>Inversión IME</strong>
          Compras de bienes durables que permanecen como activo de la
          agrupación (polos institucionales, photochecks, equipamiento)
          y se reutilizan en ciclos siguientes. Se reporta separada del
          gasto operativo para no distorsionar el resultado del mes.
        </div>
        """

    body = f"""
    <div class="breadcrumb">
      <a href="../index.html">Inicio</a>
      <span class="bc-sep">/</span>
      <span>{info.mes} {info.ciclo}</span>
    </div>

    <header class="page-hero">
      <p class="eyebrow">Ciclo {info.ciclo} · Reporte mensual</p>
      <h1 class="page-title">{info.mes}</h1>
      <p class="page-meta">
        Responsable de actualización: <strong>{esc(info.responsable)}</strong>
        <span class="meta-sep">·</span>
        Última actualización: <strong>{esc(info.actualizacion)}</strong>
      </p>
    </header>

    {hero_saldo}
    {stat_strip}

    {"" if info.ingresos == 0 and not narrativa.get("prueba") else f'''<section class="section">
      <div class="section-head">
        <div>
          <p class="section-eyebrow">Movimientos</p>
          <h3 class="section-title-big">Ingresos del mes</h3>
        </div>
        <div class="section-total verde">
          <span class="total-label">Total</span>
          <span class="total-value">+ {fmt_soles(info.ingresos)}</span>
        </div>
      </div>
      <div class="tx-list">{"".join(filas_ingreso)}</div>
    </section>'''}

    <section class="section">
      <div class="section-head">
        <div>
          <p class="section-eyebrow">Movimientos</p>
          <h3 class="section-title-big">Egresos del mes</h3>
        </div>
        <div class="section-total rojo">
          <span class="total-label">Total</span>
          <span class="total-value">− {fmt_soles(egresos_total)}</span>
        </div>
      </div>
      {info_box_inv}
      <div class="tx-list">{''.join(filas_egreso)}</div>
    </section>

    {deuda_html}

    <section class="section">
      <p class="section-eyebrow">Visualización</p>
      <h3 class="section-title-big">Distribución del gasto</h3>
      <div class="chart-grid">
        <div class="chart-block">
          <h4 class="chart-title">Egresos por categoría</h4>
          {donut_svg}
        </div>
        <div class="chart-block">
          <h4 class="chart-title">Comparativo del mes</h4>
          {barras_svg}
        </div>
      </div>
    </section>

    {cierre_html}

    <section class="section">
      <p class="section-eyebrow">Verificación</p>
      <h3 class="section-title-big">Datos abiertos</h3>
      {descarga_html}
    </section>
    """
    return layout(f"{info.mes} {info.ciclo} · 180DC PUCP", body,
                  ciclo=info.ciclo, meses_nav=meses_ciclo,
                  slug_actual=slug, asset_prefix="..")


# =============================================================================
# Página índice
# =============================================================================
def render_index(ciclos_render: list[dict]) -> str:
    """ciclos_render: [{"ciclo", "meses", "infos"}], del más antiguo al más nuevo.

    El resumen de cifras corresponde al ciclo vigente que ya tenga meses
    publicados; los ciclos anteriores se listan debajo como histórico.
    """
    con_datos = [c for c in ciclos_render if c["infos"]]
    if not con_datos:
        raise SystemExit("No hay ningún mes publicable: revisa data/ y CICLOS.")
    actual = con_datos[-1]
    anteriores = con_datos[:-1]
    infos = actual["infos"]
    ciclo_actual = actual["ciclo"]

    total_ing = sum(i.ingresos for i in infos)
    total_eg = sum(i.egresos_op for i in infos)
    total_inv = sum(i.inversion for i in infos)
    saldo_inicio = infos[0].saldo_inicial
    saldo_actual = infos[-1].saldo_final
    delta_ciclo = saldo_actual - saldo_inicio
    delta_sign = "+" if delta_ciclo >= 0 else "−"
    delta_cls = "up" if delta_ciclo >= 0 else "down"

    # ---- Hero
    hero = f"""
    <section class="index-hero">
      <p class="eyebrow">180 Degrees Consulting PUCP</p>
      <h1 class="hero-title">Reporte de transparencia financiera</h1>
      <p class="hero-lead">
        Movimiento financiero detallado de la agrupación durante el ciclo
        académico {ciclo_actual}. Cada transacción cuenta con su descripción y el
        archivo fuente está disponible para verificación.
      </p>
      <div class="hero-saldo-strip">
        <div>
          <p class="eyebrow">Saldo actual</p>
          <div class="hero-saldo-big">{fmt_soles(saldo_actual)}</div>
          <p class="hero-saldo-delta {delta_cls}">
            <span class="arrow">{'↑' if delta_ciclo >= 0 else '↓'}</span>
            {delta_sign} {fmt_soles(abs(delta_ciclo))} desde el inicio del ciclo
          </p>
        </div>
      </div>
    </section>
    """

    # ---- Stat strip
    stat_strip = f"""
    <div class="stat-strip stat-strip-index">
      <div class="stat">
        <span class="stat-label">Saldo de inicio</span>
        <span class="stat-value">{fmt_soles(saldo_inicio)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Ingresos acumulados</span>
        <span class="stat-value verde">{fmt_soles(total_ing)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Egresos operativos</span>
        <span class="stat-value rojo">{fmt_soles(total_eg)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Inversión IME</span>
        <span class="stat-value ambar">{fmt_soles(total_inv)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Meses reportados</span>
        <span class="stat-value">{len(infos)}</span>
      </div>
    </div>
    """

    # ---- Month cards
    def _cards(meses, lista):
      out = []
      for idx, (info, cfg) in enumerate(zip(lista, meses), 1):
        delta_mes = info.saldo_final - info.saldo_inicial
        d_sign = "+" if delta_mes >= 0 else "−"
        d_cls = "up" if delta_mes >= 0 else "down"
        out.append(f"""
        <a class="mes-card" href="meses/{cfg['slug']}.html">
          <div class="mes-card-head">
            <div>
              <p class="eyebrow">Mes {idx:02d} · {info.ciclo}</p>
              <h3 class="mes-card-title">{info.mes}</h3>
            </div>
            <span class="mes-arrow">→</span>
          </div>
          <div class="mes-card-saldo">
            <p class="eyebrow">Saldo final</p>
            <div class="mes-saldo-num">{fmt_soles(info.saldo_final)}</div>
            <p class="mes-delta {d_cls}">
              <span class="arrow">{'↑' if delta_mes >= 0 else '↓'}</span>
              {d_sign} {fmt_soles(abs(delta_mes))}
            </p>
          </div>
          <div class="mes-card-stats">
            <div>
              <span>Ingresos</span>
              <b class="verde">+ {fmt_soles(info.ingresos)}</b>
            </div>
            <div>
              <span>Egresos op.</span>
              <b class="rojo">− {fmt_soles(info.egresos_op)}</b>
            </div>
            <div>
              <span>Inversión</span>
              <b class="ambar">− {fmt_soles(info.inversion)}</b>
            </div>
          </div>
        </a>
        """)
      return "".join(out)

    cards = _cards(actual["meses"], infos)

    # ---- Histórico: ciclos anteriores
    historico = ""
    for c in reversed(anteriores):
        historico += f"""
    <section class="section">
      <div class="section-head">
        <div>
          <p class="section-eyebrow">Histórico</p>
          <h3 class="section-title-big">Ciclo {c["ciclo"]}</h3>
        </div>
        <div class="section-total">
          <span class="total-label">Saldo de cierre</span>
          <span class="total-value">{fmt_soles(c["infos"][-1].saldo_final)}</span>
        </div>
      </div>
      <div class="meses-grid">{_cards(c["meses"], c["infos"])}</div>
    </section>
    """

    body = f"""
    {hero}
    {stat_strip}

    <section class="section">
      <div class="section-head">
        <div>
          <p class="section-eyebrow">Reportes</p>
          <h3 class="section-title-big">Informes mensuales · Ciclo {ciclo_actual}</h3>
        </div>
      </div>
      <div class="meses-grid">{cards}</div>
    </section>

    {historico}

    <section class="section two-col">
      <div>
        <p class="section-eyebrow">Marco contable</p>
        <h3 class="section-title-big">Metodología</h3>
        <p class="prose">
          Los montos provienen directamente del <em>Registro de Transacciones</em>
          mensual que mantiene el área financiera. Cada movimiento del archivo
          contable original tiene su correlativo en el portal, y el archivo
          fuente de cada mes está disponible para descarga, lo cual permite
          verificación línea por línea.
        </p>
        <p class="prose">
          Para consultas adicionales o detalle complementario, comunícate con
          el área financiera de la agrupación.
        </p>
      </div>
      <div>
        <p class="section-eyebrow">Definiciones</p>
        <h3 class="section-title-big">Conceptos clave</h3>
        <dl class="def-list">
          <div>
            <dt>Ingresos</dt>
            <dd>Fondos que entran a caja en el mes (membresías, donaciones, recaudaciones, patrocinios).</dd>
          </div>
          <div>
            <dt>Egresos operativos</dt>
            <dd>Consumibles del mes: bocaditos, transporte, ITF, capacitaciones, integración.</dd>
          </div>
          <div>
            <dt>Inversión IME</dt>
            <dd>Inventario / material reutilizable. Bienes durables que permanecen como activo de la agrupación.</dd>
          </div>
          <div>
            <dt>Saldo final</dt>
            <dd>Saldo inicial + Ingresos − Egresos operativos − Inversión.</dd>
          </div>
        </dl>
      </div>
    </section>
    """
    return layout("180DC PUCP · Transparencia Financiera", body,
                  ciclo=ciclo_actual, meses_nav=actual["meses"],
                  slug_actual=None, asset_prefix=".")


# =============================================================================
# Main
# =============================================================================
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "meses").mkdir(exist_ok=True)
    downloads_dir = OUT_DIR / "downloads"
    downloads_dir.mkdir(exist_ok=True)

    import shutil

    # Los slugs son nombres de archivo web: no pueden repetirse entre ciclos.
    vistos = {}
    for c in CICLOS:
        for m in c["meses"]:
            if m["slug"] in vistos:
                raise SystemExit(
                    f'ERROR: el slug "{m["slug"]}" se repite en los ciclos '
                    f'{vistos[m["slug"]]} y {c["ciclo"]}. Ponle un slug distinto '
                    f'(ej. "{m["slug"]}-{c["ciclo"]}") en CICLOS.'
                )
            vistos[m["slug"]] = c["ciclo"]

    ciclos_render = []
    pendientes = []
    n_archivos = 0
    for c in CICLOS:
        meses_ok, infos = [], []
        for cfg in c["meses"]:
            if cfg.get("prueba"):
                from dataclasses import replace
                anterior = infos[-1] if infos else next(
                    x["infos"][-1] for x in reversed(ciclos_render) if x["infos"]
                )
                infos.append(replace(
                    anterior, mes=cfg["mes"], ciclo=c["ciclo"],
                    actualizacion="Versión de prueba", saldo_inicial=anterior.saldo_final,
                    ingresos=0.0, egresos_op=0.0, inversion=0.0,
                    df=anterior.df.iloc[:0].copy(),
                    df_ingresos=anterior.df_ingresos.iloc[:0].copy(),
                    df_egresos=anterior.df_egresos.iloc[:0].copy(),
                    df_inversion=anterior.df_inversion.iloc[:0].copy(),
                ))
                meses_ok.append(cfg)
                continue
            xlsx_path = DATA_DIR / cfg["xlsx"]
            if not xlsx_path.exists():
                # El mes está registrado pero su Excel todavía no llega:
                # se omite en vez de romper el build.
                pendientes.append((c["ciclo"], cfg["mes"], cfg["xlsx"]))
                continue
            shutil.copy2(xlsx_path, downloads_dir / cfg["xlsx"])
            n_archivos += 1
            infos.append(cargar_mes(str(xlsx_path), cfg["mes"], ciclo=c["ciclo"]))
            meses_ok.append(cfg)
        ciclos_render.append({"ciclo": c["ciclo"], "meses": meses_ok, "infos": infos})

    for c in ciclos_render:
        for cfg, info in zip(c["meses"], c["infos"]):
            html = render_mes(info, cfg["slug"], NARRATIVA.get(cfg["mes"], {}),
                              cfg.get("xlsx", ""), c["meses"])
            out = OUT_DIR / "meses" / f"{cfg['slug']}.html"
            out.write_text(html, encoding="utf-8")
            print(f"OK -> {out.relative_to(ROOT)}")

    (OUT_DIR / "index.html").write_text(render_index(ciclos_render), encoding="utf-8")
    print("OK -> site/index.html")
    print(f"OK -> site/downloads/  ({n_archivos} archivos)")

    # Limpieza: borra paginas y descargas que ya no corresponden a ningun mes
    # registrado (p. ej. un mes que se renombro o se quito de CICLOS).
    slugs_ok = {cfg["slug"] for c in ciclos_render for cfg in c["meses"]}
    xlsx_ok = {cfg["xlsx"] for c in ciclos_render for cfg in c["meses"] if "xlsx" in cfg}
    for f in (OUT_DIR / "meses").glob("*.html"):
        if f.stem not in slugs_ok:
            f.unlink()
            print(f"LIMPIEZA -> se elimino site/meses/{f.name} (ya no esta en CICLOS)")
    for f in downloads_dir.glob("*.xlsx"):
        if f.name not in xlsx_ok:
            f.unlink()
            print(f"LIMPIEZA -> se elimino site/downloads/{f.name} (ya no esta en CICLOS)")

    for ciclo, mes, xlsx in pendientes:
        print(f"AVISO: {mes} ({ciclo}) esta registrado pero falta data/{xlsx}. "
              f"Se omitio del sitio.")

    print("\n=== Cuadre ===")
    for c in ciclos_render:
        if not c["infos"]:
            continue
        print(f"-- Ciclo {c['ciclo']}")
        for info in c["infos"]:
            print(f"{info.mes:8s}  Ingresos: {fmt_soles(info.ingresos)}  "
                  f"Egresos op.: {fmt_soles(info.egresos_op)}  "
                  f"Inv: {fmt_soles(info.inversion)}  "
                  f"Saldo final: {fmt_soles(info.saldo_final)}")


if __name__ == "__main__":
    main()
