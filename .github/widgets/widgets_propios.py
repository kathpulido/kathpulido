"""Widgets propios del perfil: perfil de actividad y logros.

Reemplazan servicios públicos que se pausan seguido. Solo usa la librería
estándar de Python y la API GraphQL de GitHub con el GITHUB_TOKEN de la acción.

Uso en la acción:   python .github/widgets/widgets_propios.py
Prueba sin red:     python .github/widgets/widgets_propios.py --demo
"""
import datetime as dt
import json
import math
import os
import random
import sys
import urllib.request
from pathlib import Path

SALIDA = Path("profile")
BG0, BG1 = "#0E0B1F", "#1E1240"
INK, LAV, VIO, VIO_D, MAG, GOLD = "#F5F3FF", "#DDD6FE", "#A78BFA", "#8B5CF6", "#E879F9", "#FCD34D"
SANS = "'Segoe UI', 'Inter', 'Helvetica Neue', Arial, sans-serif"
MONO = "'Cascadia Code', 'Consolas', 'DejaVu Sans Mono', monospace"
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

CONSULTA = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      totalCount
      nodes { stargazerCount }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def consultar(usuario, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": CONSULTA, "variables": {"login": usuario}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "widgets-perfil"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        datos = json.load(r)
    if "errors" in datos:
        raise SystemExit(f"Error de la API: {datos['errors']}")
    u = datos["data"]["user"]
    cc = u["contributionsCollection"]
    dias = [(d["date"], d["contributionCount"])
            for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    return {
        "dias": dias,
        "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        "contribuciones": cc["contributionCalendar"]["totalContributions"],
        "repositorios": u["repositories"]["totalCount"],
        "estrellas": sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
        "seguidores": u["followers"]["totalCount"],
        "pull_requests": u["pullRequests"]["totalCount"],
        "issues": u["issues"]["totalCount"],
    }


def demo():
    random.seed(4)
    hoy = dt.date.today()
    dias = [((hoy - dt.timedelta(days=i)).isoformat(), max(0, int(random.gauss(2, 3))))
            for i in range(365, -1, -1)]
    return {"dias": dias, "commits": 120, "contribuciones": 260, "repositorios": 7,
            "estrellas": 3, "seguidores": 12, "pull_requests": 4, "issues": 2}


def fecha_corta(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d.day} {MESES[d.month - 1]}"


def miles(n):
    return f"{n:,}".replace(",", " ")


# ── Perfil de actividad (como un perfil topográfico) ───────────────────────
def actividad(datos, n=31):
    dias = datos["dias"][-n:]
    W, H = 880, 280
    x0, x1, y0, y1 = 64, W - 28, 70, H - 52
    vals = [c for _, c in dias]
    vmax = max(vals) if max(vals) > 0 else 1
    paso = max(1, math.ceil(vmax / 4))
    techo = paso * 4

    def X(i): return x0 + (x1 - x0) * i / (len(dias) - 1)
    def Y(v): return y1 - (y1 - y0) * v / techo

    pts = [(X(i), Y(v)) for i, v in enumerate(vals)]
    # curva suave (Catmull-Rom → Bézier), recortada para no bajar de la base
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, min(y1, p1[1] + (p2[1] - p0[1]) / 6))
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, min(y1, p2[1] - (p3[1] - p1[1]) / 6))
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    area = d + f" L{x1:.1f},{y1:.1f} L{x0:.1f},{y1:.1f} Z"

    imax = vals.index(max(vals))
    total = sum(vals)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="Perfil de actividad: {total} contribuciones en los últimos {n} días">',
         f"""<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>
  <linearGradient id="relleno" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{VIO_D}" stop-opacity=".55"/><stop offset="1" stop-color="{VIO_D}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="trazo" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{VIO}"/><stop offset="1" stop-color="{MAG}"/></linearGradient>
  <clipPath id="revela"><rect x="0" y="0" width="{W}" height="{H}"/></clipPath>
</defs>
<style>
  .t {{ font:600 17px {SANS}; fill:{LAV}; }}
  .st {{ font:500 11.5px {MONO}; fill:{VIO}; }}
  .eje {{ font:500 10.5px {MONO}; fill:{VIO}; }}
  .linea {{ stroke-dasharray:1; stroke-dashoffset:0; animation:dibujo 2.2s ease-out both; }}
  .area, .pt {{ animation:aparece .8s ease-out both; animation-delay:1.4s; }}
  @keyframes dibujo {{ from {{ stroke-dashoffset:1; }} to {{ stroke-dashoffset:0; }} }}
  @keyframes aparece {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation:none !important; }} }}
</style>""",
         f'<rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>',
         f'<text class="t" x="24" y="34">Perfil de actividad</text>',
         f'<text class="st" x="24" y="54">Últimos {n} días · {total} contribuciones · máximo {vals[imax]} el {fecha_corta(dias[imax][0])}</text>']
    # retícula y cotas
    for k in range(5):
        v = paso * k
        y = Y(v)
        s.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{LAV}" stroke-opacity="{.22 if k == 0 else .08}"/>')
        s.append(f'<text class="eje" x="{x0 - 10}" y="{y + 3.5:.1f}" text-anchor="end">{v}</text>')
    for i in range(0, len(dias), 5):
        x = X(i)
        s.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y1 + 5}" stroke="{LAV}" stroke-opacity=".06"/>')
        s.append(f'<text class="eje" x="{x:.1f}" y="{y1 + 20}" text-anchor="middle">{fecha_corta(dias[i][0])}</text>')
    s.append(f'<path class="area" d="{area}" fill="url(#relleno)"/>')
    s.append(f'<path class="linea" pathLength="1" d="{d}" fill="none" stroke="url(#trazo)" stroke-width="2.6" stroke-linecap="round"/>')
    for i, (x, y) in enumerate(pts):
        if vals[i]:
            s.append(f'<circle class="pt" cx="{x:.1f}" cy="{y:.1f}" r="{4 if i == imax else 2.6}" fill="{GOLD if i == imax else MAG}"/>')
    # marca de cota máxima, como un vértice
    xm, ym = pts[imax]
    s.append(f'<g class="pt"><path d="M{xm:.1f} {ym - 22:.1f} l7 12 h-14 z" fill="none" stroke="{GOLD}" stroke-width="1.5"/>'
             f'<line x1="{xm:.1f}" y1="{ym - 10:.1f}" x2="{xm:.1f}" y2="{ym - 5:.1f}" stroke="{GOLD}" stroke-width="1.2"/></g>')
    s.append("</svg>")
    return "\n".join(s)


# ── Logros: cada uno es un mojón con su categoría ──────────────────────────
NIVELES = ["C", "B", "A", "AA", "AAA", "S"]
COLOR_NIVEL = {"—": "#4C4566", "C": "#7C6FA8", "B": "#8B5CF6", "A": "#A78BFA",
               "AA": "#C084FC", "AAA": "#E879F9", "S": GOLD}
LOGROS = [  # clave, nombre, umbrales para C..S
    ("commits", "Commits del año", [1, 10, 50, 100, 300, 1000]),
    ("contribuciones", "Contribuciones", [1, 20, 100, 250, 500, 1500]),
    ("repositorios", "Repositorios", [1, 3, 10, 20, 35, 50]),
    ("estrellas", "Estrellas", [1, 5, 15, 50, 100, 500]),
    ("seguidores", "Seguidores", [1, 5, 15, 40, 100, 300]),
    ("pull_requests", "Pull requests", [1, 5, 15, 40, 100, 300]),
]


def nivel(valor, umbrales):
    n = "—"
    for etiqueta, u in zip(NIVELES, umbrales):
        if valor >= u:
            n = etiqueta
    return n


def logros(datos):
    w, h, gap = 136, 176, 10
    W = len(LOGROS) * w + (len(LOGROS) - 1) * gap + 32
    H = h + 20
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Logros de GitHub">',
         f"""<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient></defs>
<style>
  .n {{ font:600 12px {SANS}; fill:{LAV}; }}
  .v {{ font:600 11px {MONO}; fill:{VIO}; }}
  .lv {{ font:800 15px {SANS}; }}
  .m {{ animation:sube .6s cubic-bezier(.3,.8,.3,1.2) both; transform-box:fill-box; transform-origin:bottom; }}
  @keyframes sube {{ from {{ opacity:0; transform:translateY(10px) scale(.9); }} to {{ opacity:1; transform:none; }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation:none !important; }} }}
</style>""",
         f'<rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>']
    for k, (clave, nombre, umbrales) in enumerate(LOGROS):
        valor = datos[clave]
        nv = nivel(valor, umbrales)
        col = COLOR_NIVEL[nv]
        x = 16 + k * (w + gap)
        cx = x + w / 2
        s.append(f'<g class="m" style="animation-delay:{.12 * k:.2f}s">')
        s.append(f'<rect x="{x}" y="10" width="{w}" height="{h}" rx="12" fill="{col}" fill-opacity=".07" stroke="{col}" stroke-opacity=".35"/>')
        # mojón: base, cuerpo troncocónico y placa con el nivel
        s.append(f'<rect x="{cx - 34}" y="112" width="68" height="8" rx="2" fill="{col}" fill-opacity=".35"/>')
        s.append(f'<path d="M{cx - 24} 112 L{cx - 16} 66 L{cx + 16} 66 L{cx + 24} 112 Z" fill="{col}" fill-opacity=".22" stroke="{col}" stroke-width="1.4"/>')
        s.append(f'<circle cx="{cx}" cy="58" r="21" fill="{BG0}" stroke="{col}" stroke-width="2.2"/>')
        s.append(f'<circle cx="{cx}" cy="58" r="16" fill="none" stroke="{col}" stroke-opacity=".45" stroke-dasharray="2 3"/>')
        s.append(f'<text class="lv" x="{cx}" y="63.5" text-anchor="middle" style="fill:{col}; font-size:{15 if len(nv) < 3 else 12.5}px">{nv}</text>')
        if nv == "S":
            s.append(f'<path d="M{cx - 9} 30 l4 -7 l5 5 l5 -5 l4 7 z" fill="{GOLD}"/>')
        s.append(f'<text class="n" x="{cx}" y="146" text-anchor="middle">{nombre}</text>')
        s.append(f'<text class="v" x="{cx}" y="166" text-anchor="middle">{miles(valor)}</text>')
        s.append("</g>")
    s.append("</svg>")
    return "\n".join(s)


def main():
    if "--demo" in sys.argv:
        datos = demo()
    else:
        datos = consultar(os.environ["USUARIO"], os.environ["GITHUB_TOKEN"])
    SALIDA.mkdir(exist_ok=True)
    (SALIDA / "actividad.svg").write_text(actividad(datos), encoding="utf-8")
    (SALIDA / "logros.svg").write_text(logros(datos), encoding="utf-8")
    print({k: v for k, v in datos.items() if k != "dias"})


if __name__ == "__main__":
    main()
