"""DESIGN EXPLORATION — extend Pip's snow accumulation past today's max
(face still readable) all the way to FULLY COVERED, for the predawn snow
squall whiteout. Throwaway sheet tool; touches NO game code.

The shipped look is snow_fx.py's W2 "sculpted blanket": per-column depth
following the bird's top silhouette, drawn as 3 vertical-line layers
(off-white body + bright crest + cool-blue under-edge), with a head cap
`if xf > 0.60: d = min(d, 7.0 + hi*11*(1-headfrac))` that deliberately
keeps the face readable. We extend PAST that cap.

We add a single `extra` knob in [0,1] that drives accumulation beyond the
shipped peak (load>=1.0): it (a) lifts the head cap so snow creeps over
crown->face->beak, (b) deepens the pile, and (c) widens coverage forward.
extra=0 reproduces the shipped peak; extra=1.0 is fully covered. Each of
the 5 versions reuses this column scaffold but applies a DISTINCT finish so
the visibility spectrum (camouflage in the whiteout) spans medium..hidden.

The technique stays numpy-free / pure pygame so it ports straight into
snow_fx.py later.

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_snow_fullcover
Output: docs/snow_full_cover/round_1.png
"""
from __future__ import annotations

import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((360, 640))

import game.entities as E
from game.entities import Bird
from game import parrot, snow_fx, biome
from game.draw import make_gradient_surface

OUT_DIR = os.path.join(ROOT, "docs", "snow_full_cover")
os.makedirs(OUT_DIR, exist_ok=True)

# Palette (cohesive with shipped snow_fx).
WHITE = (255, 255, 255)
OFF = (236, 244, 252)
BLUE = (188, 206, 230)
SHADOW = (150, 168, 198)
GLAZE = (172, 214, 238)          # V4 glassy cyan-blue sheen

ZOOM = 6                         # sprite is 64x60; render big for detail


# ── shared extended column scaffold (numpy-free, snow_fx-portable) ───────────
def _columns(extra, *, cap_lift, depth_gain, front_reach,
             cornice=1.6, lump=0.0, noise_amp=2.4):
    """Yield (x, y0, y1, d) snow bands per column for the FULLY-COVERED
    extension. `extra` in [0,1] continues past the shipped peak (load=1.0):

      cap_lift   - how far the head cap is released (snow climbs the face)
      depth_gain - how much deeper the pile grows beyond shipped MAXD
      front_reach- how far coverage pushes toward the beak (front columns)

    extra=0 ~ shipped peak; extra=1 ~ buried. Each version passes its own
    gains so the same scaffold yields different finishes."""
    top, x_min, w, h = snow_fx._topline(snow_fx._REF_FRAME)
    if x_min < 0:
        return []
    taper_w = 13.0
    out = []
    for x in range(w):
        yt = top[x]
        if yt < 0:
            continue
        xf = x / w
        # Coverage spreads forward as `extra` grows. At extra=0 this matches
        # the shipped _cov(xf, load=1.0); `extra` then lowers the rear-first
        # onset threshold so front (beak) columns reach full coverage too.
        thr = 0.55 * xf * (1.0 - front_reach * extra)
        load = 1.0
        cov = 0.0 if load <= thr else min(1.0, (load - thr) / (1.0 - thr))
        if cov <= 0.0:
            continue
        rear = 1.0 - xf
        bulge = math.exp(-((xf - 0.40) / 0.26) ** 2)
        d = snow_fx.MAXD * cov * (0.50 + 0.45 * rear + 0.45 * bulge)
        d *= (1.0 + depth_gain * extra)                  # whole pile thickens
        if xf > 0.60:
            # Shipped cap: d = min(d, 7.0 + hi*11*(1-headfrac)) at peak (hi=1).
            # We RAISE the ceiling by cap_lift*extra so snow climbs crown->
            # face->beak. The (1-headfrac) bias keeps the very beak-tip the
            # last thing buried, so silhouette stays parrot-shaped longest.
            headfrac = (xf - 0.60) / 0.40
            base_cap = 7.0 + 11.0 * (1.0 - headfrac)
            cap = base_cap + cap_lift * extra * (13.0 + 9.0 * (1.0 - headfrac))
            d = min(d, cap)
        te = snow_fx._smooth((x - x_min) / taper_w)
        d *= te
        if d < 0.6:
            continue
        over = cornice * rear * te
        if lump:
            over += lump * (0.5 + 0.5 * math.sin(x * 0.9)) * (0.35 + rear) * te
        nb = (math.sin(x * 1.26) + math.sin(x * 0.34)) * 0.25 + 0.5
        y0 = yt - over
        y1 = yt + d + (nb - 0.5) * noise_amp
        out.append((x, y0, y1, y1 - y0))
    return out


def _blur(s, downs):
    w, h = s.get_size()
    if w < downs * 2 or h < downs * 2:
        return s
    sm = pygame.transform.smoothscale(s, (w // downs, h // downs))
    return pygame.transform.smoothscale(sm, (w, h))


def _native_size():
    _, _, w, h = snow_fx._topline(snow_fx._REF_FRAME)
    return w, h


# ── V1 · Smooth dome (snowman) ───────────────────────────────────────────────
# A rounded soft white dome envelops the whole bird: clear parrot-shaped
# mound, eye glint + beak tip peek through. MEDIUM read.
def v1_smooth_dome(extra):
    w, h = _native_size()
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    cols = _columns(extra, cap_lift=1.0, depth_gain=0.95, front_reach=0.85,
                    cornice=1.2, noise_amp=1.0)
    if not cols:
        return None
    # Smooth body fill from the columns (low noise = rounded surface).
    for x, y0, y1, d in cols:
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.20)), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.22)), (x, int(y1)), 1)
    ov = _blur(ov, 2)                                    # smooth the surface
    # A unifying dome cap: a big soft white ellipse over the whole top,
    # giving the rounded snowman read; then re-clip to silhouette below.
    if extra > 0.3:
        xs = [c[0] for c in cols]
        cx = sum(xs) / len(xs)
        top_y = min(c[1] for c in cols)
        amt = (extra - 0.3) / 0.7
        dome = pygame.Surface((w, h), pygame.SRCALPHA)
        rx = (max(xs) - min(xs)) * 0.5 * (0.85 + 0.15 * amt)
        ry = (max(c[2] for c in cols) - top_y) * 0.5 * (0.7 + 0.4 * amt)
        pygame.draw.ellipse(dome, (*OFF, int(150 * amt)),
                            (int(cx - rx), int(top_y - ry * 0.25),
                             int(rx * 2), int(ry * 2)))
        dome = _blur(dome, 3)
        ov.blit(dome, (0, 0))
    return _clip_to_body(ov, extra, front_reach=0.85, cap_lift=1.0)


# ── V2 · Chunky caked drift ──────────────────────────────────────────────────
# Heavy lumpy sculpted clumps + a wind cornice over the crown. LOWER read:
# bumpy white mass, only a small eye peek.
def v2_chunky_drift(extra):
    w, h = _native_size()
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    cols = _columns(extra, cap_lift=1.05, depth_gain=1.15, front_reach=0.8,
                    cornice=3.0, lump=3.2, noise_amp=3.4)
    if not cols:
        return None
    for x, y0, y1, d in cols:
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.16)), 1)
        pygame.draw.line(ov, (*SHADOW, 255), (x, int(y1 - d * 0.34)), (x, int(y1)), 1)
    # Caked clumps: stamp opaque blobs at lump peaks for a chunky surface.
    for x, y0, y1, d in cols:
        lump = 0.5 + 0.5 * math.sin(x * 0.9)
        if lump > 0.78 and d > 4.0:
            r = max(2, int(2.0 + 2.5 * lump))
            _stamp(ov, x, y0 + d * 0.18, r, OFF, 255)
            _stamp(ov, x, y0 + d * 0.10, max(1, r - 1), WHITE, 220)
    ov = _blur(ov, 1)
    return _clip_to_body(ov, extra, front_reach=0.8, cap_lift=1.05)


# ── V3 · Soft powder puff ────────────────────────────────────────────────────
# Fluffy, fuzzy-edged fresh powder, soft alpha falloff. STRONG camouflage:
# nearly dissolves into the whiteout, just a faint eye glint.
def v3_powder_puff(extra):
    w, h = _native_size()
    ov = pygame.Surface((w * 2, h * 2), pygame.SRCALPHA)   # 2x for soft stamps
    cols = _columns(extra, cap_lift=1.1, depth_gain=1.05, front_reach=0.92,
                    cornice=1.0, noise_amp=2.0)
    if not cols:
        return None
    for x, y0, y1, d in cols:
        n = max(2, int(d / 2.0) + 2)
        for i in range(n + 1):
            t = i / max(1, n)
            yy = (y0 + (y1 - y0) * t) * 2
            # Fuzzy: many overlapping low-alpha soft discs.
            col = WHITE if t < 0.4 else (OFF if t < 0.75 else BLUE)
            _stamp(ov, x * 2, yy, 4.2, col, 120)
    ov = _blur(ov, 4)                                       # heavy fuzz
    ov = pygame.transform.smoothscale(ov, (w, h))
    return _clip_to_body(ov, extra, front_reach=0.92, cap_lift=1.1)


# ── V4 · Icy glaze / frost ───────────────────────────────────────────────────
# Snow + a bluish glassy glaze + sparkles; Pip's red shows faintly THROUGH
# the ice (frozen-in look), eye + beak visible. MEDIUM-HIGH read.
def v4_icy_glaze(extra):
    w, h = _native_size()
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    cols = _columns(extra, cap_lift=0.95, depth_gain=0.7, front_reach=0.95,
                    cornice=1.0, noise_amp=1.6)
    if not cols:
        return None
    # Thinner, translucent snow so the red shows through the ice.
    for x, y0, y1, d in cols:
        pygame.draw.line(ov, (*OFF, 200), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.18)), 1)
        pygame.draw.line(ov, (*GLAZE, 150), (x, int(y0 + d * 0.3)),
                         (x, int(y1)), 1)
        pygame.draw.line(ov, (*BLUE, 220), (x, int(y1 - d * 0.22)), (x, int(y1)), 1)
    ov = _blur(ov, 1)
    # Glassy sparkles (4-point glints) deterministically scattered.
    for x, y0, y1, d in cols:
        g = (math.sin(x * 12.99) * 4375.5) % 1.0
        if g > 0.9 and d > 2.0:
            sx, sy = x, int(y0 + d * 0.3)
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                pygame.draw.line(ov, (*WHITE, 235), (sx, sy), (sx + dx, sy + dy), 1)
    return _clip_to_body(ov, extra, front_reach=0.95, cap_lift=0.95,
                         glaze_red=True)


# ── V5 · Layered ridge blanket (extends shipped W2) ──────────────────────────
# Continuous connected sculpted blanket tail->back->nape->crown->over-face
# with defined ridge layers. HIGHEST read: eye + beak + thin red sliver peek.
def v5_ridge_blanket(extra):
    w, h = _native_size()
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    cols = _columns(extra, cap_lift=0.9, depth_gain=0.85, front_reach=0.78,
                    cornice=1.8, noise_amp=2.4)
    if not cols:
        return None
    # Shipped W2 fill...
    for x, y0, y1, d in cols:
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.18)), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.26)), (x, int(y1)), 1)
    # ...plus defined ridge lines: bright crest + blue shadow at two interior
    # depths, so the blanket reads as sculpted overlapping drifts not a slab.
    for ridge in (0.42, 0.7):
        for x, y0, y1, d in cols:
            ry = y0 + d * ridge + math.sin(x * 0.55) * 1.2
            pygame.draw.line(ov, (*WHITE, 200), (x, int(ry - 1)), (x, int(ry)), 1)
            pygame.draw.line(ov, (*SHADOW, 170), (x, int(ry + 0.5)),
                             (x, int(ry + 1.5)), 1)
    return _clip_to_body(ov, extra, front_reach=0.78, cap_lift=0.9)


# ── helpers ──────────────────────────────────────────────────────────────────
def _stamp(layer, x, y, r, color, alpha):
    d = max(2, int(r * 2))
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(s, (*color, alpha), (d // 2, d // 2), max(1, d // 2 - 1))
    layer.blit(s, (int(x - d / 2), int(y - d / 2)))


def _clip_to_body(ov, extra, *, front_reach, cap_lift, glaze_red=False):
    """Allow snow to extend a little BELOW the top silhouette only where the
    bird's body actually is — masks stray blur outside Pip and, at high
    extra, lets a translucent skim run down the front so he's fully enclosed
    rather than just top-capped. Returns the overlay unchanged for the simple
    cases; the bird sprite under it provides the lower body."""
    # The overlay is meant to sit on top of the bird sprite; lower-body
    # enclosure at full cover is approximated by an extra soft front skim.
    if extra < 0.55:
        return ov
    top, x_min, w, h = snow_fx._topline(snow_fx._REF_FRAME)
    skim = pygame.Surface((w, h), pygame.SRCALPHA)
    amt = (extra - 0.55) / 0.45
    for x in range(w):
        yt = top[x]
        if yt < 0:
            continue
        xf = x / w
        # Front/lower skim: faint snow clinging down the body face so the
        # silhouette fills with white at full cover (keeps red from dominating).
        depth = (8.0 + 14.0 * amt) * (0.4 + 0.6 * (1.0 - abs(xf - 0.45) * 1.4))
        if depth < 1.0:
            continue
        a = int(110 * amt) if not glaze_red else int(70 * amt)
        col = OFF if not glaze_red else GLAZE
        pygame.draw.line(skim, (*col, a), (x, yt + 2), (x, int(yt + depth)), 1)
    skim = _blur(skim, 2)
    ov.blit(skim, (0, 0))
    return ov


# ── parcel snow: extend the shipped cap to fully covered too ──────────────────
def parcel_overlay(mode, extra, version):
    """Snow cap on the parcel that thickens with `extra` so the parcel stays
    VISIBLE but snow-covered. Reuses snow_fx's parcel column technique,
    deepened past PARCEL_MAXD; finish loosely matches the body version."""
    top, x_min, w, h = snow_fx._parcel_topline(mode)
    if x_min < 0:
        return None
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    taper_w = 4.0
    depth = snow_fx.PARCEL_MAXD * (1.0 + 1.4 * extra)
    for x in range(w):
        yt = top[x]
        if yt < 0:
            continue
        rear = 1.0 - x / w
        te = snow_fx._smooth((x - x_min) / taper_w)
        d = depth * (0.65 + 0.5 * rear) * te
        if d < 0.6:
            continue
        nb = math.sin(x * 1.7) * 0.25 + 0.5
        y0 = yt - 0.6 * te
        y1 = yt + d + (nb - 0.5) * 1.4
        if version == 4:        # icy glaze parcel
            pygame.draw.line(ov, (*OFF, 210), (x, int(y0)), (x, int(y1)), 1)
            pygame.draw.line(ov, (*GLAZE, 150), (x, int(y0 + d * 0.4)),
                             (x, int(y1)), 1)
        else:
            pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.22)), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.3)), (x, int(y1)), 1)
    return ov


# ── compose one Pip cell: bird sprite + body overlay + parcel + parcel snow ──
def render_cell(version_fn, extra, version_idx, *, glaze_red=False):
    """Build a native-size cell with Pip + extended snow, then scale up.
    Mirrors Bird.draw's compositing order (sprite, body snow, parcel,
    parcel snow) without touching game code."""
    nw, nh = _native_size()
    pad = 6
    cw, ch = nw + pad * 2, nh + pad * 2 + 14   # +room for the lower parcel
    cell = pygame.Surface((cw, ch), pygame.SRCALPHA)
    spr = parrot._get_frames()[snow_fx._REF_FRAME]
    bx, by = pad, pad
    # Parcel sits PARCEL_Y_OFFSET below the bird centre; bird sprite centre
    # is at (nw/2, nh/2) within its frame box.
    parcel = parrot.get_parcel("normal")
    pw, ph = parcel.get_size()
    pcx = bx + nw / 2
    pcy = by + nh / 2 + 12
    # Frozen-in red look (V4): tint the visible red faintly cyan AFTER snow.
    cell.blit(spr, (bx, by))
    # Parcel under the snow line (drawn before body snow so body snow can
    # overlap its top edge, matching how Pip's body sits in front).
    cell.blit(parcel, (int(pcx - pw / 2), int(pcy - ph / 2)))
    pov = parcel_overlay("normal", extra, version_idx)
    if pov is not None:
        cell.blit(pov, (int(pcx - pw / 2), int(pcy - ph / 2)))
    # Body snow overlay on top.
    ov = version_fn(extra)
    if ov is not None:
        cell.blit(ov, (bx, by))
    return pygame.transform.scale(cell, (cw * ZOOM, ch * ZOOM)), (cw, ch)


# ── reference row via the REAL Bird.draw ─────────────────────────────────────
def render_reference(load):
    """The shipped render: set Bird.snow_load and call the real Bird.draw."""
    nw, nh = _native_size()
    pad = 6
    cw, ch = nw + pad * 2, nh + pad * 2 + 14
    cell = pygame.Surface((cw, ch), pygame.SRCALPHA)
    b = Bird()
    b.x = pad + nw / 2
    b.y = pad + nh / 2
    b.vy = 0  # tilt_deg is a read-only property derived from vy; 0 = level
    b.snow_load = load
    b.draw(cell, 0, 0)
    return pygame.transform.scale(cell, (cw * ZOOM, ch * ZOOM)), (cw, ch)


# ── backdrops ────────────────────────────────────────────────────────────────
def neutral_panel(w, h):
    return make_gradient_surface(w, h, [(0.0, (34, 40, 54)), (1.0, (22, 26, 36))])


def whiteout_panel(w, h):
    """Snowstorm whiteout: bright pale-grey gradient + scattered flakes, to
    judge how well Pip hides."""
    s = make_gradient_surface(w, h, [(0.0, (214, 224, 236)), (1.0, (188, 200, 218))])
    for i in range(int(w * h / 90)):
        x = (math.sin(i * 12.9898) * 43758.5) % 1.0 * w
        y = (math.sin(i * 78.233) * 12543.7) % 1.0 * h
        r = 1 + int((math.sin(i * 3.1) * 0.5 + 0.5) * 2)
        a = 120 + int((math.sin(i * 1.7) * 0.5 + 0.5) * 100)
        fl = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(fl, (255, 255, 255, a), (r, r), r)
        s.blit(fl, (int(x), int(y)))
    return s


def on_panel(cell, panel_fn):
    """Composite a transparent Pip cell onto a backdrop panel."""
    w, h = cell.get_size()
    panel = panel_fn(w, h)
    panel.blit(cell, (0, 0))
    return panel


# ── sheet layout ─────────────────────────────────────────────────────────────
VERSIONS = [
    ("V1 - Smooth dome (snowman)",
     "rounded soft white mound; MEDIUM read - eye glint + beak tip peek",
     v1_smooth_dome, 1, False),
    ("V2 - Chunky caked drift",
     "lumpy sculpted clumps + crown cornice; LOWER read - small eye peek",
     v2_chunky_drift, 2, False),
    ("V3 - Soft powder puff",
     "fuzzy fresh powder, soft falloff; STRONG camo - dissolves into whiteout",
     v3_powder_puff, 3, False),
    ("V4 - Icy glaze / frost",
     "snow + glassy cyan sheen + sparkles; MED-HIGH - red frozen-in, eye+beak",
     v4_icy_glaze, 4, True),
    ("V5 - Layered ridge blanket (extends W2)",
     "connected sculpted ridges over face; HIGHEST read - eye+beak+red sliver",
     v5_ridge_blanket, 5, False),
]

# Per-row extension progression. extra: 0 = shipped peak, 1 = fully covered.
EXT_STEPS = [
    ("current max", 0.0),
    ("mid extension", 0.5),
    ("FULLY COVERED", 1.0),
]


def main():
    label_w = 232
    gap = 8
    pad_out = 18
    title_h = 76

    # Probe cell pixel size.
    _, (cw, ch) = render_reference(1.0)
    cell_w, cell_h = cw * ZOOM, ch * ZOOM

    # Reference row: 4 loads, single panel each.
    ref_loads = [0.0, 0.35, 0.70, 1.00]
    ref_cols = len(ref_loads)
    # Version rows: 2 progression cells + a final FULLY-COVERED cell shown on
    # TWO panels (dark + whiteout) side by side -> 4 cell-widths total.
    ver_cols = 4

    cols_max = max(ref_cols, ver_cols)
    row_h = cell_h + 30
    sheet_w = label_w + cols_max * (cell_w + gap) + pad_out * 2
    rows = 1 + len(VERSIONS)
    sheet_h = title_h + rows * (row_h + gap) + pad_out

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((14, 16, 24))

    fbig = pygame.font.SysFont("Arial", 26, bold=True)
    frow = pygame.font.SysFont("Arial", 17, bold=True)
    fnote = pygame.font.SysFont("Arial", 13)
    fcell = pygame.font.SysFont("Arial", 13, bold=True)

    GOLD = (240, 206, 120)
    WLBL = (228, 236, 248)
    DIM = (170, 184, 206)

    sheet.blit(fbig.render("Pip - snow FULL COVER extension  (predawn squall whiteout)",
                           True, GOLD), (pad_out, 14))
    sheet.blit(fnote.render(
        "Reference = shipped Bird.draw (stops at face-readable). V1-V5 extend "
        "PAST load=1.0 to fully covered; last cell on dark + whiteout panels.",
        True, DIM), (pad_out, 46))

    y = title_h

    def cell_label(txt, x, yy, col=WLBL):
        sheet.blit(fcell.render(txt, True, col), (x + 4, yy))

    # ── reference row ──
    sheet.blit(frow.render("CURRENT - shipped", True, GOLD), (pad_out, y + 14))
    sheet.blit(fnote.render("(stops here, face readable)", True, DIM),
               (pad_out, y + 36))
    cx = label_w + pad_out
    for i, ld in enumerate(ref_loads):
        cell, _ = render_reference(ld)
        panel = on_panel(cell, neutral_panel)
        sheet.blit(panel, (cx, y + 18))
        pygame.draw.rect(sheet, (90, 104, 130),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label(f"load {ld:.2f}", cx, y)
        cx += cell_w + gap
    y += row_h + gap + 16

    # ── version rows ──
    for name, note, fn, vidx, glaze in VERSIONS:
        # wrap the label
        sheet.blit(frow.render(name.split(" (")[0], True, GOLD), (pad_out, y + 12))
        if " (" in name:
            sheet.blit(fnote.render("(" + name.split(" (")[1], True, DIM),
                       (pad_out, y + 32))
        # note, wrapped to two lines
        words = note.split(" ")
        line1, line2 = "", ""
        for wword in words:
            if len(line1) < 30:
                line1 += wword + " "
            else:
                line2 += wword + " "
        sheet.blit(fnote.render(line1.strip(), True, DIM), (pad_out, y + 54))
        sheet.blit(fnote.render(line2.strip(), True, DIM), (pad_out, y + 70))

        cx = label_w + pad_out
        # first two progression steps (dark panel)
        for sname, extra in EXT_STEPS[:2]:
            cell, _ = render_cell(fn, extra, vidx, glaze_red=glaze)
            panel = on_panel(cell, neutral_panel)
            sheet.blit(panel, (cx, y + 18))
            pygame.draw.rect(sheet, (90, 104, 130),
                             (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
            cell_label(sname, cx, y)
            cx += cell_w + gap
        # fully covered on TWO panels
        full_cell, _ = render_cell(fn, 1.0, vidx, glaze_red=glaze)
        dark = on_panel(full_cell.copy(), neutral_panel)
        sheet.blit(dark, (cx, y + 18))
        pygame.draw.rect(sheet, (120, 140, 170),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label("FULLY COVERED / dark", cx, y, GOLD)
        cx += cell_w + gap
        white = on_panel(full_cell.copy(), whiteout_panel)
        sheet.blit(white, (cx, y + 18))
        pygame.draw.rect(sheet, (120, 140, 170),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label("FULLY COVERED / whiteout", cx, y, GOLD)

        y += row_h + gap + 22

    out = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
