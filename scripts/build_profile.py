"""Genera las secciones SVG del perfil de GitHub de LogiQD con el estilo de logiqd.me.

Cada SVG lleva incrustadas las fuentes (Poppins e Inter, recortadas a los caracteres que usa),
el logo y las imágenes, para que GitHub lo muestre igual en cualquier ordenador.

Uso:  pip install fonttools brotli && python3 scripts/build_profile.py
"""
import base64
import html
import io
import pathlib

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "scripts" / "fonts"
BRAND = ROOT / "scripts" / "brand"
OUT = ROOT / "profile" / "assets"

W = 800

# Colores de logiqd.me (Tailwind orange / slate) y del logo.
ORANGE = "#F97316"
ORANGE_DARK = "#EA580C"
ORANGE_TEXT = "#C2410C"
NIGHT = "#070B18"

THEMES = {
    "light": dict(
        heading="#0F172A", body="#475569", muted="#64748B", card="#FFFFFF", card_border="#E2E8F0",
        soft="#F8FAFC", soft_border="#EEF2F7", eyebrow=ORANGE_DARK, divider="#E2E8F0", line="#FED7AA",
        hero_bg="#FFFFFF", grid="#0F172A", grid_op=0.045, glow_a="#FDBA74", glow_a_op=0.45,
        glow_b="#C7D2FE", glow_b_op=0.45, badge_bg="#FFF7ED", badge_border="#FED7AA", badge_text=ORANGE_TEXT,
        ghost_bg="#FFFFFF", ghost_border="#E2E8F0", ghost_text="#0F172A", logo="Logo_Principal.svg",
    ),
    "dark": dict(
        heading="#F0F6FC", body="#9198A1", muted="#8B949E", card="#151B23", card_border="#3D444D",
        soft="#151B23", soft_border="#3D444D", eyebrow="#FB923C", divider="#3D444D", line="#7C2D12",
        hero_bg=NIGHT, grid="#FFFFFF", grid_op=0.05, glow_a=ORANGE, glow_a_op=0.20,
        glow_b="#0867C8", glow_b_op=0.25, badge_bg="#2A1608", badge_border="#7C2D12", badge_text="#FDBA74",
        ghost_bg="#111827", ghost_border="#334155", ghost_text="#F1F5F9", logo="Logo_Principal_oscuro.svg",
    ),
}
# Las secciones oscuras de la web se ven igual en los dos temas.
NIGHT_THEME = dict(THEMES["dark"], heading="#FFFFFF", body="#CBD5E1", muted="#94A3B8")

# ---------------------------------------------------------------- fuentes

_INTER = FONTS / "Inter-Variable.woff2"
FONT_FILES = {
    "p800": (FONTS / "Poppins-ExtraBold.woff2", None),
    "p700": (FONTS / "Poppins-Bold.woff2", None),
    "i400": (_INTER, 400),
    "i500": (_INTER, 500),
    "i600": (_INTER, 600),
}
FALLBACK = {
    "p": "Poppins,Inter,'Segoe UI',system-ui,-apple-system,Arial,sans-serif",
    "i": "Inter,'Segoe UI',system-ui,-apple-system,Arial,sans-serif",
}
_fonts = {}


def font_bytes(key):
    if key not in _fonts:
        path, wght = FONT_FILES[key]
        f = TTFont(path)
        if wght is not None:
            f = instancer.instantiateVariableFont(f, {"wght": wght})
        f.flavor = None
        buf = io.BytesIO()
        f.save(buf)
        _fonts[key] = buf.getvalue()
    return _fonts[key]


_metrics = {}


def text_width(s, key, size, spacing=0.0):
    if key not in _metrics:
        f = TTFont(io.BytesIO(font_bytes(key)))
        _metrics[key] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
    cmap, hmtx, upm = _metrics[key]
    units = sum(hmtx[cmap[ord(c)]][0] for c in s if ord(c) in cmap)
    return units * size / upm + spacing * max(len(s) - 1, 0)


def wrap(s, key, size, maxw):
    lines, cur = [], ""
    for word in s.split():
        test = f"{cur} {word}".strip()
        if cur and text_width(test, key, size) > maxw:
            lines.append(cur)
            cur = word
        else:
            cur = test
    return lines + [cur] if cur else lines


def font_face(key, chars):
    f = TTFont(io.BytesIO(font_bytes(key)))
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    sub = subset.Subsetter(opts)
    sub.populate(text="".join(sorted(chars)) + " ")
    sub.subset(f)
    buf = io.BytesIO()
    f.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:'LQ-{key}';src:url(data:font/woff2;base64,{b64}) format('woff2');}}"


# ---------------------------------------------------------------- iconos (Lucide)

ICONS = {
    "monitor": '<rect width="20" height="14" x="2" y="3" rx="2"/><path d="M8 21h8M12 17v4"/>',
    "bag": '<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/>',
    "palette": '<circle cx="13.5" cy="6.5" r=".5"/><circle cx="17.5" cy="10.5" r=".5"/><circle cx="8.5" cy="7.5" r=".5"/>'
    '<circle cx="6.5" cy="12.5" r=".5"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.93 0 1.65-.75 1.65-1.69 0-.44-.18-.83-.44-1.12'
    '-.29-.29-.44-.65-.44-1.13a1.64 1.64 0 0 1 1.67-1.67h2c3.05 0 5.55-2.5 5.55-5.55C21.97 6.01 17.46 2 12 2z"/>',
    "zap": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3'
    'l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M18 17V9M13 17V5M8 17v-3"/>',
    "layout": '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/>'
    '<rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
    "sparkles": '<path d="M9.94 15.5A2 2 0 0 0 8.5 14.06l-6.14-1.58a.5.5 0 0 1 0-.96L8.5 9.94A2 2 0 0 0 9.94 8.5l1.58-6.14a.5.5 0 0 1 .96 0'
    'L14.06 8.5A2 2 0 0 0 15.5 9.94l6.14 1.58a.5.5 0 0 1 0 .96L15.5 14.06a2 2 0 0 0-1.44 1.44l-1.58 6.14a.5.5 0 0 1-.96 0z"/>',
    "arrow": '<path d="M5 12h14M12 5l7 7-7 7"/>',
}


def icon(name, x, y, size, color="#FFFFFF", width=2):
    s = size / 24
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s:.4f})" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


# ---------------------------------------------------------------- lienzo


class Canvas:
    def __init__(self, height, label):
        self.h = height
        self.label = label
        self.parts = []
        self.chars = {}
        self.css = []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, key, size, fill, anchor="start", spacing=0.0, extra=""):
        self.chars.setdefault(key, set()).update(s)
        ls = f' letter-spacing="{spacing}"' if spacing else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="\'LQ-{key}\',{FALLBACK[key[0]]}" font-size="{size}" '
                 f'fill="{fill}" text-anchor="{anchor}"{ls} {extra}>{html.escape(s)}</text>')

    def rich(self, x, y, runs, key, size, anchor="start", spacing=0.0, extra=""):
        """Texto con tramos de distinto color: runs = [(texto, color), ...]."""
        for s, _ in runs:
            self.chars.setdefault(key, set()).update(s)
        spans = "".join(f'<tspan fill="{c}">{html.escape(s)}</tspan>' for s, c in runs)
        ls = f' letter-spacing="{spacing}"' if spacing else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="\'LQ-{key}\',{FALLBACK[key[0]]}" font-size="{size}" '
                 f'text-anchor="{anchor}"{ls} {extra}>{spans}</text>')

    def save(self, name):
        faces = "".join(font_face(k, v) for k, v in self.chars.items())
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{self.h}" viewBox="0 0 {W} {self.h}" '
               f'role="img" aria-label="{html.escape(self.label)}">\n<title>{html.escape(self.label)}</title>\n'
               f'<defs>\n<style>{faces}\n{"".join(self.css)}</style>\n{SHARED_DEFS}\n</defs>\n'
               + "\n".join(self.parts) + "\n</svg>\n")
        (OUT / name).write_text(svg, encoding="utf-8")
        print(f"{name}: {len(svg) / 1024:.0f} KB")


SHARED_DEFS = f"""<linearGradient id="orange" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FB923C"/><stop offset="1" stop-color="{ORANGE_DARK}"/></linearGradient>
<linearGradient id="orangeText" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{ORANGE}"/><stop offset="1" stop-color="{ORANGE_DARK}"/></linearGradient>
<filter id="shadow" x="-10%" y="-10%" width="120%" height="140%"><feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#0F172A" flood-opacity="0.06"/></filter>
<filter id="btnShadow" x="-20%" y="-30%" width="140%" height="190%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="{ORANGE}" flood-opacity="0.35"/></filter>"""

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def grid(c, x, y, w, h, color, op, step=44):
    lines = [f'<path d="M{x + i} {y}V{y + h}"/>' for i in range(step, w, step)]
    lines += [f'<path d="M{x} {y + j}H{x + w}"/>' for j in range(step, h, step)]
    c.add(f'<g stroke="{color}" stroke-opacity="{op}" stroke-width="1">{"".join(lines)}</g>')


def pill_button(c, x, y, label, primary, t, size=16, h=46, arrow=False, anchor="start"):
    tw = text_width(label, "i600", size)
    w = tw + 48 + (26 if arrow else 0)
    if anchor == "end":
        x -= w
    elif anchor == "middle":
        x -= w / 2
    if primary:
        c.add(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h / 2}" fill="url(#orange)" filter="url(#btnShadow)"/>')
        color = "#FFFFFF"
    else:
        c.add(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{t["ghost_bg"]}" '
              f'stroke="{t["ghost_border"]}"/>')
        color = t["ghost_text"]
    c.text(x + 24, y + h / 2 + size * 0.36, label, "i600", size, color)
    if arrow:
        c.add(icon("arrow", x + 24 + tw + 8, y + h / 2 - 9, 18, color, 2.2))
    return w


def eyebrow(c, x, y, label, color, anchor="middle"):
    c.text(x, y, label.upper(), "i600", 13, color, anchor, spacing=2)


# ---------------------------------------------------------------- secciones
#
# Todas las secciones son paneles con su propio fondo: así se leen bien con el tema claro y el oscuro
# de GitHub (y en la app del móvil). El texto largo va en el README, no en imágenes.


def panel(c, t, glows=(), dark=False):
    h = c.h
    bg = NIGHT if dark else t["hero_bg"]
    c.add(f'<clipPath id="panel"><rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="24"/></clipPath>')
    for i, (color, op, *_rest) in enumerate(glows):
        c.add(f'<radialGradient id="g{i}"><stop offset="0" stop-color="{color}" stop-opacity="{op}"/>'
              f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
    c.add('<g clip-path="url(#panel)">')
    c.add(f'<rect width="{W}" height="{h}" fill="{bg}"/>')
    grid(c, 0, 0, W, h, "#FFFFFF" if dark else t["grid"], 0.045 if dark else t["grid_op"])
    for i, (_c, _o, cx, cy, rx, ry) in enumerate(glows):
        c.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#g{i})"/>')
    c.add("</g>")
    border = "#1E293B" if dark else t["card_border"]
    c.add(f'<rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="24" fill="none" stroke="{border}" stroke-width="2"/>')


ROTATING = ["restaurante", "barbería", "clínica", "tienda", "academia", "negocio"]


def hero(theme, static=False):
    t = THEMES[theme]
    c = Canvas(580, "LogiQD — Páginas web que traen clientes a tu negocio")
    n = len(ROTATING)
    if not static:
        slot = 100 / n
        c.css.append(
            f".w{{opacity:0;animation:word {n * 2.2}s infinite}}"
            f"@keyframes word{{0%{{opacity:0;transform:translateY(22px)}}{slot * 0.12:.2f}%{{opacity:1;transform:translateY(0)}}"
            f"{slot * 0.85:.2f}%{{opacity:1;transform:translateY(0)}}{slot:.2f}%{{opacity:0;transform:translateY(-22px)}}"
            f"100%{{opacity:0}}}}"
            "@media (prefers-reduced-motion: reduce){.w{animation:none;opacity:0}.w.last{opacity:1}}"
        )
    panel(c, t, [(t["glow_a"], t["glow_a_op"], W - 30, 30, 340, 260), (t["glow_b"], t["glow_b_op"], 30, c.h - 40, 320, 230)])

    c.add(f'<image href="{data_uri(BRAND / t["logo"], "image/svg+xml")}" x="30" y="22" width="84" height="57"/>')
    pill_button(c, W - 30, 28, "Pedir presupuesto", True, t, size=15, h=42, anchor="end")

    badge = "Presupuesto cerrado en 24 h · Web lista en 2–3 semanas"
    bw = text_width(badge, "i500", 16) + 54
    c.add(f'<rect x="{(W - bw) / 2:.1f}" y="108" width="{bw:.1f}" height="38" rx="19" fill="{t["badge_bg"]}" '
          f'stroke="{t["badge_border"]}"/>')
    c.add(f'<circle cx="{(W - bw) / 2 + 22:.1f}" cy="127" r="4" fill="{ORANGE}"/>')
    c.text((W - bw) / 2 + 35, 132.8, badge, "i500", 16, t["badge_text"])

    for i, line in enumerate(["Páginas web que traen", "clientes a tu"]):
        c.text(W / 2, 214 + i * 62, line, "p800", 56, t["heading"], "middle", spacing=-1.5)
    if static:
        c.text(W / 2, 338, ROTATING[-1], "p800", 56, "url(#orangeText)", "middle", spacing=-1.5)
    else:
        for i, word in enumerate(ROTATING):
            last = " last" if i == n - 1 else ""
            c.text(W / 2, 338, word, "p800", 56, "url(#orangeText)", "middle", spacing=-1.5,
                   extra=f'class="w{last}" style="animation-delay:{i * 2.2}s"')

    sub = "Diseñamos tu web, hacemos que te encuentren en Google y nos ocupamos de todo lo técnico."
    for i, line in enumerate(wrap(sub, "i400", 21, 640)):
        c.text(W / 2, 392 + i * 31, line, "i400", 21, t["body"], "middle")

    b1 = text_width("Pedir presupuesto gratis", "i600", 18) + 48 + 26
    b2 = text_width("Ver qué hacemos", "i600", 18) + 48
    x0 = (W - (b1 + 14 + b2)) / 2
    pill_button(c, x0, 448, "Pedir presupuesto gratis", True, t, size=18, h=54, arrow=True)
    pill_button(c, x0 + b1 + 14, 448, "Ver qué hacemos", False, t, size=18, h=54)

    trust = ["Precio cerrado", "Sin permanencia", "Nos ocupamos de todo"]
    widths = [text_width(s, "i500", 17) + 16 for s in trust]
    gap = 40
    x = (W - sum(widths) - gap * (len(trust) - 1)) / 2
    for i, (s, w) in enumerate(zip(trust, widths)):
        c.add(f'<circle cx="{x + 3:.1f}" cy="539" r="4" fill="{ORANGE}"/>')
        c.text(x + 15, 545, s, "i500", 17, t["heading"])
        if i < len(trust) - 1:
            c.add(f'<path d="M{x + w + gap / 2:.1f} 527v24" stroke="{t["divider"]}"/>')
        x += w + gap
    c.save(f"hero-{theme}{'-static' if static else ''}.svg")


SECTORS = ["Restaurantes", "Barberías", "Fisioterapeutas", "Academias", "Tiendas", "Talleres", "Peluquerías",
           "Centros de estética", "Cafeterías", "Inmobiliarias", "Gestorías", "Clínicas"]


def stats(theme, static=False):
    t = THEMES[theme]
    c = Canvas(250, "24 h para darte un presupuesto cerrado · 2–3 semanas por web · 100 % pensada para el móvil")
    panel(c, t)
    items = [("24 h", "laborables para darte", "un presupuesto cerrado"),
             ("2–3 sem.", "es lo que tarda", "normalmente una web"),
             ("100 %", "pensada para verse", "bien en el móvil")]
    col = W / 3
    for i, (big, l1, l2) in enumerate(items):
        cx = col * i + col / 2
        c.text(cx, 76, big, "p800", 46, t["heading"], "middle", spacing=-1)
        c.text(cx, 110, l1, "i500", 17, t["muted"], "middle")
        c.text(cx, 134, l2, "i500", 17, t["muted"], "middle")
        if i:
            c.add(f'<path d="M{col * i:.1f} 36v108" stroke="{t["divider"]}"/>')

    by, bh = 172, 56
    seq, x = [], 0.0
    for s in SECTORS:
        seq.append((x, "/"))
        seq.append((x + 20, s))
        x += 20 + text_width(s, "i600", 17) + 32
    period = x
    if not static:
        c.css.append(f".marquee{{animation:marquee 30s linear infinite}}"
                     f"@keyframes marquee{{to{{transform:translateX(-{period:.1f}px)}}}}" + REDUCED)
    c.add(f'<clipPath id="band"><rect x="24" y="{by}" width="{W - 48}" height="{bh}" rx="14"/></clipPath>')
    c.add(f'<rect x="24" y="{by}" width="{W - 48}" height="{bh}" rx="14" fill="#0F172A" stroke="#1E293B"/>')
    c.add('<g clip-path="url(#band)"><g class="marquee">')
    for rep in range(3):
        for dx, s in seq:
            color = "#475569" if s == "/" else "#E2E8F0"
            c.text(44 + rep * period + dx, by + 34, s, "i600", 17, color)
    c.add("</g></g>")
    c.save(f"stats-{theme}{'-static' if static else ''}.svg")


def restaurant():
    t = NIGHT_THEME
    c = Canvas(690, "Restaurant OS: ¿tienes un restaurante? Hemos hecho un sistema entero para ti")
    panel(c, t, [(ORANGE, 0.26, 0, c.h, 380, 300), ("#0867C8", 0.22, W, 0, 360, 260)], dark=True)
    label = "RESTAURANT OS"
    lw = text_width(label, "i600", 14, 1.8) + 48
    c.add(f'<rect x="{(W - lw) / 2:.1f}" y="38" width="{lw:.1f}" height="34" rx="17" fill="#FFFFFF" fill-opacity="0.06" '
          f'stroke="#FFFFFF" stroke-opacity="0.18"/>')
    c.add(f'<circle cx="{(W - lw) / 2 + 18:.1f}" cy="55" r="4" fill="{ORANGE}"/>')
    c.text((W - lw) / 2 + 30, 60, label, "i600", 14, "#FFFFFF", spacing=1.8)
    o = "#FB923C"
    lines = [[("¿Tienes un restaurante?", "#FFFFFF")],
             [("Hemos hecho ", "#FFFFFF"), ("un sistema entero", o)],
             [("para ti", "#FFFFFF")]]
    for i, runs in enumerate(lines):
        c.rich(W / 2, 128 + i * 50, runs, "p800", 42, "middle", spacing=-1.2)
    c.text(W / 2, 272, "Piden desde la mesa con un QR · Cocina y barra en pantalla · Reservas", "i500", 18, "#CBD5E1", "middle")

    iw = 640
    ih = iw * 9 / 16
    ix, iy = (W - iw) / 2, 300
    c.add(f'<clipPath id="shot"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih:.1f}" rx="18"/></clipPath>')
    c.add(f'<image href="{data_uri(BRAND / "restaurant-os-demo.jpg", "image/jpeg")}" x="{ix}" y="{iy}" width="{iw}" '
          f'height="{ih:.1f}" clip-path="url(#shot)" preserveAspectRatio="xMidYMid slice"/>')
    c.add(f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih:.1f}" rx="18" fill="none" stroke="#FFFFFF" stroke-opacity="0.15"/>')
    cx, cy = W / 2, iy + ih / 2
    c.add(f'<circle cx="{cx}" cy="{cy:.1f}" r="32" fill="#FFFFFF"/><path d="M{cx - 9} {cy - 14:.1f}l24 14-24 14z" fill="#0F172A"/>')
    c.save("restaurant-os.svg")


def cta():
    t = NIGHT_THEME
    c = Canvas(400, "¿Tienes un negocio? Cuéntanos qué necesitas y te decimos cómo hacerlo.")
    panel(c, t, [(ORANGE, 0.20, W / 2, 0, 380, 190)], dark=True)
    eyebrow(c, W / 2, 64, "¿Tienes un negocio?", "#FB923C")
    c.text(W / 2, 124, "Cuéntanos qué necesitas", "p800", 46, "#FFFFFF", "middle", spacing=-1.2)
    c.text(W / 2, 178, "y te decimos cómo hacerlo", "p800", 46, "#FFFFFF", "middle", spacing=-1.2)
    c.text(W / 2, 226, "Te respondemos en 24 h laborables con un precio cerrado.", "i400", 20, "#94A3B8", "middle")
    b1 = text_width("Pedir presupuesto", "i600", 18) + 48
    b2 = text_width("Ver servicios", "i600", 18) + 48
    x0 = (W - (b1 + 14 + b2)) / 2
    pill_button(c, x0, 262, "Pedir presupuesto", True, t, size=18, h=54)
    pill_button(c, x0 + b1 + 14, 262, "Ver servicios", False, t, size=18, h=54)
    c.text(W / 2, 360, "Sin compromiso · Sin permanencia · Respuesta en 24 h", "i400", 16, "#94A3B8", "middle")
    c.save("cta.svg")


def tile(name, inner, size=96):
    """Icono suelto (cuadrado naranja con el símbolo en blanco), para las tarjetas del README."""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 48 48">'
           f'<defs><linearGradient id="o" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FB923C"/>'
           f'<stop offset="1" stop-color="{ORANGE_DARK}"/></linearGradient></defs>'
           f'<rect width="48" height="48" rx="13" fill="url(#o)"/>{inner}</svg>\n')
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


ICON_TILES = ["monitor", "bag", "palette", "zap", "wrench", "chart", "layout", "sparkles"]


def tiles():
    for name in ICON_TILES:
        tile(f"icon-{name}", icon(name, 12, 12, 24))
    for i in range(1, 6):
        c = Canvas(0, "")  # solo para recoger los glifos
        c.text(24, 31, f"{i:02d}", "p700", 17, "#FFFFFF", "middle")
        face = font_face("p700", c.chars["p700"])
        tile(f"step-{i}", f"<style>{face}</style>{c.parts[0]}")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for th in THEMES:
        hero(th)
        hero(th, static=True)
        stats(th)
        stats(th, static=True)
    restaurant()
    cta()
    tiles()
