"""Genera los banners SVG (claro y oscuro) del perfil de GitHub con las imágenes incrustadas."""
import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "profile" / "assets"

NAVY = "#002B66"
ORANGE = "#FD7705"
BLUE = "#0A4BB5"


def data_uri(name):
    return "data:image/png;base64," + base64.b64encode((ASSETS / name).read_bytes()).decode()


THEMES = {
    "light": dict(
        bg1="#FFFFFF", bg2="#EEF3FB", border="#DCE4F2", title=NAVY, text="#4A5568",
        chip_bg="#FFFFFF", chip_border="#DCE4F2", chip_text=NAVY, wave1=NAVY, wave2=ORANGE,
        glow=BLUE, glow_op="0.10", wordmark="wordmark.png", bubble=BLUE, halo="#FFFFFF", halo_op="0",
    ),
    "dark": dict(
        bg1="#0B1A33", bg2="#07101F", border="#1E2D4A", title="#FFFFFF", text="#A9B6CC",
        chip_bg="#0F2140", chip_border="#24395E", chip_text="#E6ECF5", wave1=BLUE, wave2=ORANGE,
        glow="#3E7BEA", glow_op="0.30", wordmark="wordmark-light.png", bubble="#7FA8F0", halo="#DCE7FA", halo_op="0.75",
    ),
}

CHIPS = ["Presupuesto cerrado en 24 h", "Tu web en 2–3 semanas", "Sin permanencia"]
FONT = "'Archivo','Inter','Segoe UI',system-ui,-apple-system,Helvetica,Arial,sans-serif"


def chip_row(t, x, y):
    out, cx = [], x
    for label in CHIPS:
        w = 52 + len(label) * 9.4
        out.append(
            f'<g transform="translate({cx:.0f},{y})">'
            f'<rect width="{w:.0f}" height="38" rx="19" fill="{t["chip_bg"]}" stroke="{t["chip_border"]}"/>'
            f'<circle cx="20" cy="19" r="4.5" fill="{ORANGE}"/>'
            f'<text x="{(w + 18) / 2:.0f}" y="24.5" text-anchor="middle" font-size="15" font-weight="600" '
            f'fill="{t["chip_text"]}">{label}</text></g>'
        )
        cx += w + 12
    return "\n    ".join(out)


def bubbles(t):
    specs = [(1010, 7, 0), (1060, 5, 1.6), (1105, 9, 3.1), (985, 4, 4.4), (1135, 6, 2.2)]
    return "\n    ".join(
        f'<circle class="bubble" cx="{x}" cy="300" r="{r}" fill="none" stroke="{t["bubble"]}" '
        f'stroke-width="2" style="animation-delay:{d}s"/>'
        for x, r, d in specs
    )


def build(name, t):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="400" viewBox="0 0 1280 400" role="img" aria-label="LogiQD — Páginas web que traen clientes a tu negocio">
  <title>LogiQD — Páginas web que traen clientes a tu negocio</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{t['bg1']}"/><stop offset="1" stop-color="{t['bg2']}"/>
    </linearGradient>
    <radialGradient id="glow"><stop offset="0" stop-color="{t['glow']}" stop-opacity="{t['glow_op']}"/><stop offset="1" stop-color="{t['glow']}" stop-opacity="0"/></radialGradient>
    <filter id="halo" x="-10%" y="-10%" width="120%" height="120%">
      <feMorphology in="SourceAlpha" operator="dilate" radius="2.5" result="d"/>
      <feFlood flood-color="{t['halo']}" flood-opacity="{t['halo_op']}"/>
      <feComposite in2="d" operator="in" result="h0"/><feGaussianBlur in="h0" stdDeviation="0.6" result="h"/>
      <feMerge><feMergeNode in="h"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="card"><rect x="1" y="1" width="1278" height="398" rx="24"/></clipPath>
    <style>
      text {{ font-family: {FONT}; }}
      .whale {{ animation: swim 6s ease-in-out infinite; transform-origin: 1000px 190px; }}
      .bubble {{ opacity: 0; animation: rise 5.5s ease-in infinite; }}
      .wave {{ animation: drift 14s linear infinite; }}
      .wave.slow {{ animation-duration: 22s; }}
      @keyframes swim {{ 0%,100% {{ transform: translateY(0) rotate(-1.5deg); }} 50% {{ transform: translateY(-12px) rotate(1.5deg); }} }}
      @keyframes rise {{ 0% {{ opacity: 0; transform: translateY(0); }} 15% {{ opacity: .55; }} 100% {{ opacity: 0; transform: translateY(-230px); }} }}
      @keyframes drift {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-640px); }} }}
      @media (prefers-reduced-motion: reduce) {{ .whale, .bubble, .wave {{ animation: none; }} .bubble {{ opacity: .4; }} }}
    </style>
  </defs>
  <g clip-path="url(#card)">
    <rect width="1280" height="400" fill="url(#bg)"/>
    <circle cx="1000" cy="190" r="260" fill="url(#glow)"/>
    <path class="wave slow" d="M0 352 Q80 330 160 352 T320 352 T480 352 T640 352 T800 352 T960 352 T1120 352 T1280 352 T1440 352 T1600 352 T1760 352 T1920 352 V400 H0 Z" fill="{t['wave1']}" opacity="0.07"/>
    <path class="wave" d="M0 372 Q80 352 160 372 T320 372 T480 372 T640 372 T800 372 T960 372 T1120 372 T1280 372 T1440 372 T1600 372 T1760 372 T1920 372" fill="none" stroke="{t['wave2']}" stroke-width="3" opacity="0.45"/>
    {bubbles(t)}
    <image class="whale" filter="url(#halo)" href="{data_uri('whale.png')}" x="760" y="62" width="480" height="244"/>
    <image href="{data_uri(t['wordmark'])}" x="72" y="70" width="400" height="86"/>
    <text x="74" y="208" font-size="36" font-weight="800" fill="{t['title']}">Páginas web que traen clientes</text>
    <text x="74" y="250" font-size="36" font-weight="800" fill="{t['title']}">a tu <tspan fill="{ORANGE}">negocio</tspan>.</text>
    <text x="74" y="288" font-size="17.5" fill="{t['text']}">Webs, tiendas online, automatización e IA para negocios de Barcelona y alrededores.</text>
    {chip_row(t, 72, 312)}
  </g>
  <rect x="1" y="1" width="1278" height="398" rx="24" fill="none" stroke="{t['border']}" stroke-width="2"/>
</svg>
"""
    (ASSETS / f"banner-{name}.svg").write_text(svg, encoding="utf-8")


for name, theme in THEMES.items():
    build(name, theme)
