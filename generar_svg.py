"""Genera los SVG del perfil de GitHub (banner, texto animado y separador).

Uso:  python generar_svg.py assets
      python generar_svg.py assets --marcadores   (crea también los marcadores de los widgets)
"""
import math
import sys
from pathlib import Path

import numpy as np
import contourpy
from pyproj import Geod

OUT = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "assets")
OUT.mkdir(parents=True, exist_ok=True)

# ── Paleta (violeta: ingeniería + 8M) ──────────────────────────────────────
BG0, BG1 = "#0E0B1F", "#1E1240"      # noche índigo → violeta profundo
INK = "#F5F3FF"                       # texto principal
LAV = "#DDD6FE"                       # lavanda clara
VIO = "#A78BFA"                       # violeta medio
VIO_D = "#8B5CF6"                     # violeta (sirve en tema claro y oscuro)
MAG = "#E879F9"                       # magenta acento
CORREO = "katerinli2017@gmail.com"
GOLD = "#FCD34D"                      # vértices geodésicos
SANS = "'Segoe UI', 'Inter', 'Helvetica Neue', Arial, sans-serif"
MONO = "'Cascadia Code', 'Consolas', 'DejaVu Sans Mono', 'Courier New', monospace"

# ── Georreferenciación del banner ──────────────────────────────────────────
# 100 px = 1 minuto de arco en ambos ejes (a 4,7°N eso da casi un cuadrado).
# Anclada al punto de origen de EPSG:9377 (4°N, 73°W): x = 600 → 73°00'W, y = 300 → 4°00'N
LON0 = -(73 + 6 / 60)    # x = 0
LAT0 = 4 + 3 / 60        # y = 0
def px_to_lonlat(x, y):
    return LON0 + x / 100 / 60, LAT0 - y / 100 / 60

GEOD = Geod(ellps="GRS80")   # MAGNA-SIRGAS usa GRS80

def dms(v, pos, neg):
    h = pos if v >= 0 else neg
    v = abs(v)
    d = int(v); m = int((v - d) * 60); s = (v - d - m / 60) * 3600
    return f"{d}°{m:02d}'{s:04.1f}\" {h}".replace(".", ",")

def miles(v, dec=0):
    s = f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")
    return s


# Metros por píxel en horizontal (para la barra de escala)
_, _, d100 = GEOD.inv(*px_to_lonlat(0, 200), *px_to_lonlat(100, 200))
PX_PER_KM = 100 / (d100 / 1000)


# ── Relieve sintético y curvas de nivel ────────────────────────────────────
def campo(xs, ys, cerros):
    X, Y = np.meshgrid(xs, ys)
    Z = np.zeros_like(X, dtype=float)
    for cx, cy, sx, sy, amp, rot in cerros:
        c, s = math.cos(rot), math.sin(rot)
        dx, dy = X - cx, Y - cy
        u, v = dx * c + dy * s, -dx * s + dy * c
        Z += amp * np.exp(-(u ** 2 / (2 * sx ** 2) + v ** 2 / (2 * sy ** 2)))
    Z += 0.06 * np.sin(X / 37.0) * np.cos(Y / 29.0)   # rugosidad suave
    return Z

def curvas(cerros, x0, x1, y0, y1, niveles, paso=4):
    xs = np.arange(x0, x1 + paso, paso)
    ys = np.arange(y0, y1 + paso, paso)
    Z = campo(xs, ys, cerros)
    gen = contourpy.contour_generator(xs, ys, Z)
    out = []
    for lv in niveles:
        for line in gen.lines(lv):
            if len(line) < 6:
                continue
            out.append((lv, chaikin(line, 2)))
    return out

def chaikin(pts, it):
    pts = np.asarray(pts)
    closed = np.allclose(pts[0], pts[-1])
    for _ in range(it):
        a = pts[:-1]; b = pts[1:]
        q = 0.75 * a + 0.25 * b
        r = 0.25 * a + 0.75 * b
        new = np.empty((len(q) * 2, 2)); new[0::2] = q; new[1::2] = r
        if closed:
            new = np.vstack([new, new[:1]])
        else:
            new = np.vstack([pts[:1], new, pts[-1:]])
        pts = new
    return pts

def path_d(pts):
    p = [f"{x:.1f},{y:.1f}" for x, y in pts[::2]]
    if not np.allclose(pts[0], pts[-1]):
        p.append(f"{pts[-1][0]:.1f},{pts[-1][1]:.1f}")
    return "M" + " L".join(p)

def rotulo_curva(pts, texto, frac=0.35):
    """Rótulo de cota sobre la curva, alineado con su tangente y siempre legible."""
    n = len(pts)
    i = max(2, min(n - 3, int(n * frac)))
    (x0, y0), (x1, y1) = pts[i - 2], pts[i + 2]
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    x, y = pts[i]
    return x, y, ang


# ═══════════════════════════════════════════════════════════════════════════
# 1. BANNER
# ═══════════════════════════════════════════════════════════════════════════
def banner():
    W, H = 1200, 340
    cerros = [
        (935, 205, 125, 85, 1.00, -0.5),
        (1120, 70, 70, 60, 0.80, 0.3),
        (790, 320, 70, 55, 0.50, 0.0),
        (1030, 140, 60, 40, 0.35, 0.9),   # collado entre los dos cerros
    ]
    niveles = np.arange(0.10, 1.25, 0.075)          # equidistancia 20 m
    def cota(lv): return int(round(2600 + (lv - 0.10) / 0.075 * 20))
    lineas = curvas(cerros, 470, W + 10, -10, H + 10, niveles)

    # vértices geodésicos: cimas de los dos cerros principales
    v1, v2 = (935, 205), (1120, 70)
    lon1, lat1 = px_to_lonlat(*v1); lon2, lat2 = px_to_lonlat(*v2)
    az, _, dist = GEOD.inv(lon1, lat1, lon2, lat2)
    az = az % 360
    azd = int(az); azm = int((az - azd) * 60); azs = (az - azd - azm / 60) * 3600
    az_txt = f"Az {azd}°{azm:02d}'{azs:02.0f}\""
    d_txt = f"{miles(dist, 2)} m"

    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
             f'aria-labelledby="t d">')
    s.append('<title id="t">Deysa Katherine Pulido Valenzuela — Ingeniera Catastral y Geodesta</title>')
    s.append('<desc id="d">Banner con curvas de nivel, retícula de coordenadas, dos vértices geodésicos '
             'unidos por una línea con su azimut y distancia, flecha de norte y barra de escala.</desc>')
    s.append(f"""<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/>
  </linearGradient>
  <linearGradient id="nombre" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{VIO}"/><stop offset="1" stop-color="{MAG}"/>
  </linearGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0.38" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.62" stop-color="#fff" stop-opacity="1"/>
  </linearGradient>
  <mask id="mfade"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
  <clipPath id="marco"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <pattern id="minor" width="20" height="20" patternUnits="userSpaceOnUse">
    <path d="M20 0 L0 0 0 20" fill="none" stroke="{LAV}" stroke-opacity="0.05" stroke-width="1"/>
  </pattern>
</defs>
<style>
  .c  {{ fill:none; stroke:{VIO}; stroke-opacity:.55; stroke-width:1; stroke-linejoin:round;
         stroke-dasharray:1; stroke-dashoffset:0; animation:draw 2.6s cubic-bezier(.3,.7,.3,1) both; }}
  .ci {{ stroke:{LAV}; stroke-opacity:.85; stroke-width:1.8; }}
  .cota {{ font:500 10px {MONO}; fill:{LAV}; paint-order:stroke; stroke:#1A1038; stroke-width:4px; }}
  .lbl {{ font:500 11px {MONO}; fill:{VIO}; letter-spacing:.5px; paint-order:stroke; stroke:#160F33; stroke-width:4px; }}
  .pulse {{ transform-box:fill-box; transform-origin:center; animation:pulse 2.4s ease-out infinite; }}
  .linea {{ stroke-dasharray:6 5; animation:march 1.2s linear infinite; }}
  .aparece {{ animation:fadein 1s ease-out both; }}
  .surge {{ animation:fade 1s ease-out both; }}
  @keyframes draw {{ from {{ stroke-dashoffset:1; }} to {{ stroke-dashoffset:0; }} }}
  @keyframes pulse {{ 0% {{ transform:scale(.4); opacity:.9; }} 100% {{ transform:scale(2.6); opacity:0; }} }}
  @keyframes march {{ to {{ stroke-dashoffset:-22; }} }}
  @keyframes fade {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
  @keyframes fadein {{ from {{ opacity:0; transform:translateY(6px); }} to {{ opacity:1; transform:none; }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation:none !important; }} }}
</style>""")
    s.append('<g clip-path="url(#marco)">')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#minor)"/>')

    # retícula principal cada minuto de arco
    for x in range(100, W, 100):
        s.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="{LAV}" stroke-opacity=".10"/>')
    for y in range(100, H, 100):
        s.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LAV}" stroke-opacity=".10"/>')

    # curvas de nivel (se dibujan solas al cargar)
    s.append('<g mask="url(#mfade)">')
    for k, (lv, pts) in enumerate(lineas):
        c = cota(lv)
        idx = c % 100 == 0
        delay = 0.15 + 0.05 * k
        s.append(f'<path class="c{" ci" if idx else ""}" pathLength="1" style="animation-delay:{delay:.2f}s" d="{path_d(pts)}"/>')
    # cotas sobre curvas índice (una por curva, la más larga)
    puestos = set()
    for lv, pts in sorted(lineas, key=lambda t: -len(t[1])):
        c = cota(lv)
        if c % 100 or c in puestos or len(pts) < 60:
            continue
        x, y, ang = rotulo_curva(pts, str(c), 0.30)
        if not (640 < x < W - 60 and 40 < y < H - 30):
            x, y, ang = rotulo_curva(pts, str(c), 0.62)
            if not (640 < x < W - 60 and 40 < y < H - 30):
                continue
        puestos.add(c)
        s.append(f'<text class="cota surge" style="animation-delay:2.4s" text-anchor="middle" dominant-baseline="central" '
                 f'transform="translate({x:.1f},{y:.1f}) rotate({ang:.1f})">{c}</text>')
    s.append('</g>')

    # rótulos de la retícula (longitud arriba, latitud a la derecha)
    for x in range(100, W, 200):
        lon, _ = px_to_lonlat(x, 0)
        d = abs(lon); g = int(d); m = round((d - g) * 60)
        if m == 60: g, m = g + 1, 0
        s.append(f'<text class="lbl" x="{x + 4}" y="16" opacity=".75">{g}°{m:02d}\'W</text>')
    for y in range(100, H, 100):
        _, lat = px_to_lonlat(0, y)
        g = int(lat); m = round((lat - g) * 60)
        s.append(f'<text class="lbl" x="{W - 8}" y="{y - 5}" text-anchor="end" opacity=".75">{g}°{m:02d}\'N</text>')

    # línea entre vértices con azimut y distancia geodésica (GRS80)
    s.append(f'<line class="linea" x1="{v1[0]}" y1="{v1[1]}" x2="{v2[0]}" y2="{v2[1]}" stroke="{GOLD}" stroke-width="1.6" stroke-opacity=".9"/>')
    mx, my = (v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2
    ang = math.degrees(math.atan2(v2[1] - v1[1], v2[0] - v1[0]))
    s.append(f'<g transform="translate({mx:.1f},{my:.1f}) rotate({ang:.1f})"><g class="surge" style="animation-delay:2.8s">'
             f'<text y="-8" text-anchor="middle" style="font:600 11px {MONO}; fill:{GOLD}; paint-order:stroke; stroke:#160F33; stroke-width:4px">{az_txt}</text>'
             f'<text y="17" text-anchor="middle" style="font:500 11px {MONO}; fill:{GOLD}; paint-order:stroke; stroke:#160F33; stroke-width:4px">{d_txt}</text></g></g>')

    def vertice(x, y, nombre, dx, anchor):
        return (f'<circle class="pulse" cx="{x}" cy="{y}" r="9" fill="none" stroke="{GOLD}" stroke-width="1.5"/>'
                f'<path d="M{x} {y - 11} L{x + 10} {y + 7} L{x - 10} {y + 7} Z" fill="{BG0}" stroke="{GOLD}" stroke-width="1.8"/>'
                f'<circle cx="{x}" cy="{y + 1}" r="2.6" fill="{GOLD}"/>'
                f'<text x="{x + dx}" y="{y + 4}" text-anchor="{anchor}" style="font:700 11px {MONO}; fill:{GOLD}">{nombre}</text>')
    s.append(vertice(*v1, "GPS-01", -16, "end"))
    s.append(vertice(*v2, "GPS-02", -16, "end"))

    # flecha de norte
    nx, ny = 1150, 268
    s.append(f'<g transform="translate({nx},{ny})" opacity=".95"><circle cy="-10" r="30" fill="#140D2E" fill-opacity=".85"/>'
             f'<path d="M0 -30 L9 6 L0 0 Z" fill="{LAV}"/><path d="M0 -30 L-9 6 L0 0 Z" fill="none" stroke="{LAV}" stroke-width="1.2"/>'
             f'<text y="-36" text-anchor="middle" style="font:700 12px {SANS}; fill:{LAV}">N</text></g>')

    # barra de escala 0–1–2 km
    bx, by, seg = 900, 312, PX_PER_KM / 2
    for i in range(4):
        fill = LAV if i % 2 == 0 else "none"
        s.append(f'<rect x="{bx + i * seg:.1f}" y="{by}" width="{seg:.1f}" height="5" fill="{fill}" stroke="{LAV}" stroke-width=".8"/>')
    for i, t in [(0, "0"), (2, "1"), (4, "2 km")]:
        s.append(f'<text x="{bx + i * seg:.1f}" y="{by + 18}" text-anchor="{"start" if i == 4 else "middle"}" '
                 f'style="font:500 10px {MONO}; fill:{LAV}">{t}</text>')

    # bloque de texto a la izquierda
    s.append(f'<rect width="640" height="{H}" fill="url(#bg)" opacity=".0"/>')
    s.append(f'<g class="aparece">'
             f'<text x="56" y="74" style="font:600 12.5px {MONO}; fill:{VIO}; letter-spacing:3px">PERFIL PROFESIONAL</text>'
             f'<text x="54" y="138" style="font:700 52px {SANS}; fill:{INK}; letter-spacing:-.5px">Deysa Katherine</text>'
             f'<text x="54" y="196" style="font:700 52px {SANS}; fill:url(#nombre); letter-spacing:-.5px">Pulido Valenzuela</text>'
             f'<text x="56" y="240" style="font:500 25px {SANS}; fill:{LAV}">Ingeniera Catastral y Geodesta</text></g>')
    s.append(f'<g class="aparece" style="animation-delay:.4s">'
             f'<line x1="56" y1="264" x2="104" y2="264" stroke="{MAG}" stroke-width="2"/>'
             f'<g transform="translate(57,284)" fill="none" stroke="{VIO}" stroke-width="1.5" stroke-linejoin="round">'
             f'<rect width="20" height="14" rx="2"/><path d="M1 1.5 L10 8 L19 1.5"/></g>'
             f'<text x="88" y="296" style="font:500 15px {MONO}; fill:{LAV}">{CORREO}</text></g>')
    s.append('</g>')
    s.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{VIO}" stroke-opacity=".35"/>')
    s.append('</svg>')
    (OUT / "banner.svg").write_text("\n".join(s), encoding="utf-8")
    return {"az": az_txt, "dist": d_txt}


# ═══════════════════════════════════════════════════════════════════════════
# 2. LÍNEA QUE SE ESCRIBE SOLA (SMIL, funciona dentro de <img>)
# ═══════════════════════════════════════════════════════════════════════════
FRASES = [
    "Ingeniera Catastral y Geodesta.",
    "Geodesia · Catastro · Información geográfica",
    "Coordenadas, linderos y bases de datos espaciales.",
    "Las mujeres también medimos el mundo.",
]

def escribiendo():
    W, H = 1000, 56
    fs = 21
    cw = fs * 0.6                    # ancho de carácter monoespaciado
    x0 = 46
    per = 4.4                        # segundos por frase
    T = per * len(FRASES)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{" / ".join(FRASES)}">',
         f'<style>.f{{font:600 {fs}px {MONO}; fill:{VIO_D};}} @media (prefers-reduced-motion: reduce){{animate{{display:none}}}}</style>',
         f'<text x="18" y="35" style="font:700 {fs + 2}px {MONO}; fill:#D946EF">›</text>']
    for i, f in enumerate(FRASES):
        w = len(f) * cw
        a = i * per / T; b = (i * per + 1.7) / T; c = (i * per + 3.9) / T; d = (i + 1) * per / T
        if i == 0:
            kt = f"0;{b:.4f};{c:.4f};{d:.4f};1"; vals = f"0;{w:.1f};{w:.1f};0;0"
            cx = f"{x0};{x0 + w:.1f};{x0 + w:.1f};{x0};{x0}"
        elif i == len(FRASES) - 1:
            kt = f"0;{a:.4f};{b:.4f};{c:.4f};1"; vals = f"0;0;{w:.1f};{w:.1f};0"
            cx = f"{x0};{x0};{x0 + w:.1f};{x0 + w:.1f};{x0}"
        else:
            kt = f"0;{a:.4f};{b:.4f};{c:.4f};{d:.4f};1"; vals = f"0;0;{w:.1f};{w:.1f};0;0"
            cx = None
        base_w = w if i == 0 else 0
        s.append(f'<clipPath id="k{i}"><rect x="{x0}" y="0" width="{base_w:.1f}" height="{H}">'
                 f'<animate attributeName="width" dur="{T}s" repeatCount="indefinite" keyTimes="{kt}" values="{vals}"/></rect></clipPath>')
        s.append(f'<text class="f" x="{x0}" y="35" textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#k{i})">{f}</text>')
    # cursor: sigue el ancho de la frase activa
    kts, xs = [0.0], [x0]
    for i, f in enumerate(FRASES):
        w = len(f) * cw
        for t, x in [(i * per, x0), (i * per + 1.7, x0 + w), (i * per + 3.9, x0 + w), ((i + 1) * per - 0.001, x0)]:
            if t / T > kts[-1]:
                kts.append(t / T); xs.append(x)
    kts.append(1.0); xs.append(x0)
    s.append(f'<rect x="{x0 + len(FRASES[0]) * cw + 3:.1f}" y="15" width="11" height="24" rx="1.5" fill="#D946EF">'
             f'<animate attributeName="x" dur="{T}s" repeatCount="indefinite" keyTimes="{";".join(f"{k:.4f}" for k in kts)}" '
             f'values="{";".join(f"{x + 3:.1f}" for x in xs)}"/>'
             f'<animate attributeName="opacity" dur="0.9s" repeatCount="indefinite" values="1;1;0;0" keyTimes="0;0.5;0.55;1"/></rect>')
    s.append('</svg>')
    (OUT / "escribiendo.svg").write_text("\n".join(s), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# 4. SEPARADOR: barra de escala
# ═══════════════════════════════════════════════════════════════════════════
def escala():
    W, H = 1000, 30
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Separador con forma de barra de escala">']
    seg, n = 44, 6
    bw = seg * n
    x0 = (W - bw) / 2
    s.append(f'<line x1="0" y1="11" x2="{x0 - 12}" y2="11" stroke="{VIO_D}" stroke-opacity=".35"/>')
    s.append(f'<line x1="{x0 + bw + 12}" y1="11" x2="{W}" y2="11" stroke="{VIO_D}" stroke-opacity=".35"/>')
    for t in range(0, int(x0 - 12), 25):
        s.append(f'<line x1="{t}" y1="8" x2="{t}" y2="14" stroke="{VIO_D}" stroke-opacity=".3"/>')
        s.append(f'<line x1="{W - t}" y1="8" x2="{W - t}" y2="14" stroke="{VIO_D}" stroke-opacity=".3"/>')
    for i in range(n):
        s.append(f'<rect x="{x0 + i * seg}" y="8" width="{seg}" height="6" fill="{VIO_D if i % 2 == 0 else "none"}" stroke="{VIO_D}" stroke-width="1"/>')
    for i in range(0, n + 1, 2):
        lab = f"{i * 50}" + (" m" if i == n else "")
        s.append(f'<text x="{x0 + i * seg}" y="27" text-anchor="middle" style="font:500 9.5px {MONO}; fill:{VIO_D}">{lab}</text>')
    s.append('</svg>')
    (OUT / "escala.svg").write_text("\n".join(s), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# 5. MARCADORES: se ven hasta que la acción genere los widgets reales
# ═══════════════════════════════════════════════════════════════════════════
MARCADORES = {
    "profile/stats.svg": (467, 195, "Estadísticas"),
    "profile/top-langs.svg": (300, 195, "Lenguajes"),
    "profile/streak.svg": (495, 195, "Racha"),
    "profile/snake-dark.svg": (880, 192, "Serpiente"),
    "profile/snake-light.svg": (880, 192, "Serpiente"),
    "profile-3d-contrib/profile-violeta.svg": (1280, 850, "Contribuciones en 3D"),
}

def marcadores(repo):
    for rel, (w, h, nombre) in MARCADORES.items():
        ft, fs = max(16, w // 24), max(11, w // 45)
        y1, y2 = h / 2 - fs * 0.7, h / 2 + ft * 0.5 + fs * 0.3
        f = repo / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="{BG0}" stroke="{VIO_D}" stroke-opacity=".5" stroke-dasharray="6 5"/>'
            f'<text x="{w / 2}" y="{y1:.0f}" text-anchor="middle" style="font:600 {ft}px {SANS}; fill:{LAV}">{nombre}</text>'
            f'<text x="{w / 2}" y="{y2:.0f}" text-anchor="middle" style="font:500 {fs}px {MONO}; fill:{VIO}">'
            f'<tspan x="{w / 2}">Aparece al ejecutar la acción</tspan>'
            f'<tspan x="{w / 2}" dy="1.35em">«Widgets del perfil»</tspan></text></svg>', encoding="utf-8")


if __name__ == "__main__":
    meta = banner()
    escribiendo()
    escala()
    if "--marcadores" in sys.argv:
        marcadores(OUT.parent)
    print(meta, "| px/km", round(PX_PER_KM, 2))
    for f in sorted(OUT.glob("*.svg")):
        print(f.name, f.stat().st_size, "bytes")
