"""
CONSTELLATION store — RARITY element loop (gem badge + 4-tier+mystery language
+ constellation thread).

The whole point of the rarity read is that a player must rank an item in a
glance from a tiny grid corner. So the gem must be a REAL multi-facet cut
(crown facets + flat table + girdle keyline + dark seat well + one hot
specular pip), and the five tiers must separate by HUE AND VALUE — never hue
alone — so they survive a colourblind read. This sheet proves that: the five
gems large + SS-crisp on the shared night sky, a grayscale strip under them
(if two bars look the same in greyscale the colour read is a crutch), and the
tapered gold thread shown on a placeholder dark card corner where epic-violet
vs mystery-silver are most likely to muddy.

Pipeline is the locked SS=4 author-big / one-smoothscale-down lever from
constellation_hi/render_hi.py; the gem cut variants here are authored
resolution-independently and reuse the project palette + that file's facet/
thread DNA. Both build targets safe: pure pygame, no numpy, no desktop/
browser-only API.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color, NEAR_BLACK, WHITE
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP


# ── supersample (THE crispness lever — author big, one smoothscale down) ──────
SS = 4


def m(v):
    return int(round(v * SS))


def font(size):
    return _font(max(1, int(round(size * SS))), True)


# ── palette (locked CONSTELLATION DNA) ────────────────────────────────────────
BG_STOPS = [
    (0.00, (6, 7, 24)),
    (0.30, (11, 11, 40)),
    (0.55, (18, 16, 58)),
    (0.78, (26, 20, 72)),
    (1.00, (14, 12, 46)),
]
NEBULA_GLOW = (70, 60, 150)
GOLD = _GOLD_BRIGHT
GOLD_PALE = _GOLD_PALE
GOLD_DEEP = _GOLD_DEEP

# locked rarity reads — gem / glow / deep. Tuned so VALUE rises with tier:
# common is pale-but-low-chroma lilac-silver, rare a mid cyan, epic a darker
# saturated violet, legendary the brightest warm gold (the standout), and
# mystery a neutral silver that deliberately claims no tier slot.
RARITY = {
    "common":    {"gem": (214, 206, 230), "glow": (180, 174, 214), "deep": (78, 74, 112)},
    "rare":      {"gem": (108, 188, 252), "glow": (74, 158, 248),  "deep": (24, 78, 142)},
    "epic":      {"gem": (194, 122, 248), "glow": (172, 94, 244),  "deep": (80, 34, 126)},
    "legendary": {"gem": (255, 202, 104), "glow": (255, 168, 58),  "deep": (150, 92, 22)},
}
# mystery kept neutral-cool but a step DARKER in value than common's pale
# lilac so the two pale reads don't collapse to the same greyscale bar.
MYSTERY = {"gem": (198, 208, 224), "glow": (172, 190, 216), "deep": (74, 82, 108)}

TIERS = ["common", "rare", "epic", "legendary"]
ORDER = TIERS + ["mystery"]


def pal_of(key):
    return MYSTERY if key == "mystery" else RARITY[key]


CARD_T = (28, 30, 70)
CARD_B = (12, 13, 38)
CARD_RING_BRIGHT = (236, 202, 116)
DW = 360 * SS
DH = 640 * SS


# =============================================================================
# Low-level primitives (SS-aware, device-px coords) — lifted from render_hi DNA
# =============================================================================
def multistop_v(w, h, stops):
    surf = pygame.Surface((w, h))
    n = len(stops)
    for y in range(h):
        f = y / max(1, h - 1)
        seg = 0
        while seg < n - 2 and f > stops[seg + 1][0]:
            seg += 1
        t0, c0 = stops[seg]
        t1, c1 = stops[seg + 1]
        local = 0.0 if t1 == t0 else (f - t0) / (t1 - t0)
        pygame.draw.line(surf, lerp_color(c0, c1, max(0.0, min(1.0, local))),
                         (0, y), (w - 1, y))
    return surf


def soft_glow(surf, cx, cy, radius, color, peak_alpha, layers=8):
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** 1.8)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


def _glyph_base(txt, font_obj):
    return font_obj.render(txt, True, WHITE)


def plain_text(surf, txt, font_obj, center, color, shadow_a=150, keyline=None,
               kw=None, tracking=0):
    if tracking:
        widths = [font_obj.size(ch)[0] for ch in txt]
        total = sum(widths) + tracking * (len(txt) - 1)
        hh = font_obj.get_height()
        base = pygame.Surface((max(1, total), hh), pygame.SRCALPHA)
        x = 0
        for ch, wch in zip(txt, widths):
            base.blit(font_obj.render(ch, True, WHITE), (x, 0))
            x += wch + tracking
    else:
        base = _glyph_base(txt, font_obj)
    img = base.copy()
    img.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    r = img.get_rect(center=center)
    if shadow_a:
        sh = base.copy()
        sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow_a)
        surf.blit(sh, (r.x, r.y + m(1.4)))
    if keyline:
        p = kw if kw is not None else m(1)
        kl = base.copy()
        kl.fill((*keyline, 255), special_flags=pygame.BLEND_RGBA_MULT)
        for ang in range(0, 360, 45):
            dx = int(round(p * math.cos(math.radians(ang))))
            dy = int(round(p * math.sin(math.radians(ang))))
            surf.blit(kl, (r.x + dx, r.y + dy))
    surf.blit(img, r)
    return r


# =============================================================================
# GEM CUT VARIANTS
# Each variant is a self-contained recipe taking (surf, cx, cy, r, pal,
# mystery). They all honour the spec skeleton: dark seat well underneath, crown
# facets stepped in value off ONE top-left light, a flat table, a girdle
# keyline, and ONE hot specular pip upper-left. They differ in the CUT geometry
# (round brilliant / marquise rhombus / emerald step / kite shield) so the
# art-director can pick a silhouette. Value ramp is identical across cuts so
# the tiers stay readable whichever cut wins.
# =============================================================================
def _facet_tones(pal, mystery):
    """The shared 5-step value ramp off one top-left light. mystery is pushed
    cool-neutral (no tier hue) but keeps the same value staircase so it never
    out-reads a real tier."""
    deep = pal["deep"]
    if mystery:
        base = lerp_color((198, 216, 228), (216, 210, 226), 0.5)
    else:
        base = pal["gem"]
    return {
        "table": lerp_color(base, WHITE, 0.34),       # flat top, brightest
        "hi":    lerp_color(base, WHITE, 0.55),        # lit top-left crown
        "mid":   base,                                  # neutral crown
        "sh":    lerp_color(base, deep, 0.5),           # shaded crown
        "dk":    lerp_color(deep, NEAR_BLACK, 0.32),    # bottom-right, darkest
        "key":   lerp_color(deep, NEAR_BLACK, 0.5),     # girdle keyline
    }


def _seat(surf, cx, cy, r, extra=3):
    """Dark seat well + faint gold ring so the gem reads on ANY ground."""
    pad = r + m(extra + 2)
    seat = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    pygame.draw.circle(seat, (0, 0, 0, 175), (pad, pad), r + m(extra))
    pygame.draw.circle(seat, (*GOLD_DEEP, 115), (pad, pad), r + m(extra), max(1, m(0.8)))
    surf.blit(seat, (cx - pad, cy - pad))


def _pip(surf, cx, cy, r, ox, oy, rad_f=0.22):
    """The single hot specular pip — a tiny additive white disc upper-left."""
    pr = max(1, int(r * rad_f))
    pip = pygame.Surface((pr * 2 + m(2), pr * 2 + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 250), (pr + m(1), pr + m(1)), pr)
    surf.blit(pip, (cx + ox - pr - m(1), cy + oy - pr - m(1)),
              special_flags=pygame.BLEND_ADD)


def gem_round(surf, cx, cy, r, pal, mystery=False):
    """VARIANT A — round brilliant. The render_hi reference cut: 4 kite crown
    facets around a square table, on a round girdle. The 'expected' jewel."""
    t = _facet_tones(pal, mystery)
    _seat(surf, cx, cy, r)
    top = (cx, cy - r)
    left = (cx - r, cy + int(r * 0.1))
    right = (cx + r, cy + int(r * 0.1))
    bot = (cx, cy + r)
    tr = int(r * 0.42)
    tbl = [(cx, cy - tr), (cx + tr, cy), (cx, cy + tr), (cx - tr, cy)]
    pygame.draw.polygon(surf, t["hi"], [top, left, tbl[3], tbl[0]])
    pygame.draw.polygon(surf, t["mid"], [top, right, tbl[1], tbl[0]])
    pygame.draw.polygon(surf, t["sh"], [left, bot, tbl[2], tbl[3]])
    pygame.draw.polygon(surf, t["dk"], [right, bot, tbl[2], tbl[1]])
    pygame.draw.polygon(surf, t["table"], tbl)
    pygame.draw.polygon(surf, t["key"], [top, right, bot, left], width=max(1, m(0.6)))
    for i, p in enumerate((top, right, bot, left)):
        pygame.draw.line(surf, (*t["key"], 200), p, tbl[i], max(1, m(0.5)))
    _pip(surf, cx, cy, r, -int(r * 0.28), -int(r * 0.28))


def gem_brilliant8(surf, cx, cy, r, pal, mystery=False):
    """VARIANT B — true 8-facet brilliant. An octagonal girdle with 8 crown
    facets radiating to an octagonal table, value-stepped by clock position
    off the top-left light. The most 'scintillating' read — most facet edges,
    so it sells 'precious' hardest while staying legible at corner size."""
    t = _facet_tones(pal, mystery)
    _seat(surf, cx, cy, r)
    n = 8
    rot = -math.pi / 2 - math.pi / n          # flat-ish top, point up-left bias
    girdle = [(cx + r * math.cos(rot + 2 * math.pi * i / n),
               cy + r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
    tr = r * 0.46
    table = [(cx + tr * math.cos(rot + 2 * math.pi * i / n),
              cy + tr * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
    # light direction unit vector (top-left)
    lx, ly = -0.7071, -0.7071
    for i in range(n):
        a = girdle[i]
        b = girdle[(i + 1) % n]
        ta = table[i]
        tb = table[(i + 1) % n]
        # facet normal proxy: midpoint direction from centre
        mx = (a[0] + b[0]) / 2 - cx
        my = (a[1] + b[1]) / 2 - cy
        ml = math.hypot(mx, my) or 1
        d = (mx / ml) * lx + (my / ml) * ly      # -1..1 facing the light
        f = (d + 1) / 2                           # 0 dark .. 1 lit
        col = lerp_color(lerp_color(t["dk"], t["sh"], min(1.0, f * 2)),
                         t["hi"], max(0.0, (f - 0.5) * 2))
        pygame.draw.polygon(surf, col, [a, b, tb, ta])
    pygame.draw.polygon(surf, t["table"], table)
    pygame.draw.polygon(surf, t["key"], girdle, width=max(1, m(0.6)))
    for i in range(n):
        pygame.draw.line(surf, (*t["key"], 190), girdle[i], table[i], max(1, m(0.4)))
    _pip(surf, cx, cy, r, -int(r * 0.26), -int(r * 0.26))


def gem_marquise(surf, cx, cy, r, pal, mystery=False):
    """VARIANT C — marquise / rhombus. Pointed top + bottom, a tall lens with a
    central lozenge table and 4 long crown facets. A more 'jewel-cut' diamond
    silhouette that reads distinct from the round at a glance and gives the
    corner a directional accent."""
    t = _facet_tones(pal, mystery)
    _seat(surf, cx, cy, r)
    hh = int(r * 1.12)                            # taller than wide -> marquise
    ww = int(r * 0.78)
    top = (cx, cy - hh)
    bot = (cx, cy + hh)
    left = (cx - ww, cy)
    right = (cx + ww, cy)
    tx, ty = int(ww * 0.5), int(hh * 0.42)
    tbl = [(cx, cy - ty), (cx + tx, cy), (cx, cy + ty), (cx - tx, cy)]
    pygame.draw.polygon(surf, t["hi"], [top, left, tbl[3], tbl[0]])
    pygame.draw.polygon(surf, t["mid"], [top, right, tbl[1], tbl[0]])
    pygame.draw.polygon(surf, t["sh"], [left, bot, tbl[2], tbl[3]])
    pygame.draw.polygon(surf, t["dk"], [right, bot, tbl[2], tbl[1]])
    pygame.draw.polygon(surf, t["table"], tbl)
    pygame.draw.polygon(surf, t["key"], [top, right, bot, left], width=max(1, m(0.6)))
    for i, p in enumerate((top, right, bot, left)):
        pygame.draw.line(surf, (*t["key"], 200), p, tbl[i], max(1, m(0.5)))
    _pip(surf, cx, cy, r, -int(ww * 0.34), -int(hh * 0.30), rad_f=0.18)


def gem_emerald(surf, cx, cy, r, pal, mystery=False):
    """VARIANT D — emerald / step cut. Concentric rectangular steps with cut
    corners and a clipped girdle keyline. The flattest, most 'gemstone-slab'
    read; the stepped value bands give a clean architectural ramp that survives
    downscale especially well (few thin diagonals)."""
    t = _facet_tones(pal, mystery)
    _seat(surf, cx, cy, r)
    ww = int(r * 0.86)
    hh = int(r * 1.04)
    chamf = int(r * 0.30)

    def oct_pts(hw, hv, ch):
        return [(cx - hw + ch, cy - hv), (cx + hw - ch, cy - hv),
                (cx + hw, cy - hv + ch), (cx + hw, cy + hv - ch),
                (cx + hw - ch, cy + hv), (cx - hw + ch, cy + hv),
                (cx - hw, cy + hv - ch), (cx - hw, cy - hv + ch)]
    # outer body (mid), a step ring (shaded), then the bright table
    pygame.draw.polygon(surf, t["mid"], oct_pts(ww, hh, chamf))
    # bottom-right step darker, top-left lighter -> two half overlays
    outer = oct_pts(ww, hh, chamf)
    mid_ring = oct_pts(int(ww * 0.74), int(hh * 0.78), int(chamf * 0.7))
    # shade the lower-right band, light the upper-left band of the outer step
    pygame.draw.polygon(surf, t["dk"], [outer[2], outer[3], outer[4], outer[5],
                                        mid_ring[4], mid_ring[3]])
    pygame.draw.polygon(surf, t["hi"], [outer[7], outer[0], outer[1],
                                        mid_ring[1], mid_ring[0], mid_ring[7]])
    pygame.draw.polygon(surf, t["sh"], mid_ring)
    table = oct_pts(int(ww * 0.5), int(hh * 0.54), int(chamf * 0.5))
    pygame.draw.polygon(surf, t["table"], table)
    # crisp step keylines
    pygame.draw.polygon(surf, t["key"], outer, width=max(1, m(0.7)))
    pygame.draw.polygon(surf, (*t["key"], 200), mid_ring, width=max(1, m(0.5)))
    pygame.draw.polygon(surf, (*t["key"], 170), table, width=max(1, m(0.5)))
    _pip(surf, cx, cy, r, -int(ww * 0.32), -int(hh * 0.34), rad_f=0.17)


VARIANTS = [
    ("A  ROUND BRILLIANT", gem_round),
    ("B  8-FACET BRILLIANT", gem_brilliant8),
    ("C  MARQUISE", gem_marquise),
    ("D  EMERALD STEP", gem_emerald),
]


# =============================================================================
# Constellation thread (deliberate tapered gold link gem -> node star)
# =============================================================================
def draw_thread(surf, gx, gy, nx, ny, pal):
    """Tapered gold thread from the gem to a small node star — stacked lines of
    decreasing width + a haloed node, so it reads as an intentional link, never
    a stray hairline. Drawn additive over a clip surface so it glows."""
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for wth, al in ((m(2.4), 55), (m(1.4), 120), (m(0.7), 205)):
        pygame.draw.line(layer, (*pal["glow"], al), (gx, gy), (nx, ny),
                         max(1, int(wth)))
    soft_glow(layer, nx, ny, m(4), pal["gem"], 150, layers=6)
    pygame.draw.circle(layer, (255, 255, 255, 235), (nx, ny), max(1, m(1.5)))
    pygame.draw.circle(layer, (*pal["gem"], 255), (nx, ny), max(1, m(1.1)))
    # a 4-point twinkle on the node so it reads as a star, not a dot
    L = m(4)
    pygame.draw.line(layer, (*pal["gem"], 150), (nx - L, ny), (nx + L, ny), max(1, m(0.6)))
    pygame.draw.line(layer, (*pal["gem"], 150), (nx, ny - L), (nx, ny + L), max(1, m(0.6)))
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)


# =============================================================================
# Sheet composition
# =============================================================================
def draw_bg(surf, w, h):
    surf.blit(multistop_v(w, h, BG_STOPS), (0, 0))
    soft_glow(surf, w // 2, int(h * 0.42), m(220), NEBULA_GLOW, 55, layers=10)
    vig = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        d = abs(y - h * 0.5) / (h * 0.5)
        pygame.draw.line(vig, (0, 0, 6, int(70 * d ** 1.5)), (0, y), (w, y))
    surf.blit(vig, (0, 0))


def card_corner(surf, x, y, w, h):
    """A placeholder dark store-card corner (gradient body + gold bevel rim +
    dark keyline) so the gem + thread are judged where they actually live: the
    top-right corner of a night-blue card, where epic-violet vs mystery-silver
    are most at risk of muddying."""
    rad = m(17)
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        c = lerp_color(CARD_T, CARD_B, (yy / max(1, h - 1)) ** 1.15)
        pygame.draw.line(body, (*c, 252), (0, yy), (w, yy))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (x, y))
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    pygame.draw.rect(surf, (*CARD_RING_BRIGHT, 200), rect.inflate(-m(2), -m(2)),
                     width=max(1, m(1.4)), border_radius=rad - m(1))
    return rect


def grayscale_of(src):
    """Desaturate a surface by luma so the colourblind-safety claim is PROVEN,
    not asserted: if two tiers collapse to the same bar here, the colour read
    was a crutch. Coarse grid sampling is plenty for a proof strip."""
    w, h = src.get_size()
    gray = pygame.Surface((w, h))
    src.lock()
    step = max(1, SS)
    for gy in range(0, h, step):
        for gx in range(0, w, step):
            r, g, b = src.get_at((gx, gy))[:3]
            lum = int(0.299 * r + 0.587 * g + 0.114 * b)
            pygame.draw.rect(gray, (lum, lum, lum), (gx, gy, step, step))
    src.unlock()
    return gray


def render_device():
    pad = m(22)
    col_w = m(150)
    n = len(ORDER)
    sheet_w = pad * 2 + col_w * n
    title_h = m(40)
    gem_band = m(150)
    label_band = m(40)
    proof_h = m(96)
    thread_band = m(250)
    sheet_h = (title_h + gem_band + label_band + proof_h + m(34)
               + thread_band + pad)

    surf = pygame.Surface((sheet_w, sheet_h))
    draw_bg(surf, sheet_w, sheet_h)

    plain_text(surf, "RARITY  —  GEM  +  5 READS  +  CONSTELLATION THREAD",
               font(13), (sheet_w // 2, pad + m(4)), GOLD_PALE, shadow_a=140,
               tracking=m(1), keyline=(10, 10, 24), kw=m(0.8))

    # ── ROW 1: the five tier gems at large SS-crisp scale (round brilliant) ───
    # The gem row is rendered onto its OWN flat-ground strip so the greyscale
    # proof below samples clean gems against an even value — not the uneven
    # nebula bloom, which would corrupt the value-separation read. The same
    # strip is then desaturated for the proof.
    gem_cy = title_h + gem_band // 2 + m(6)
    gem_r = m(40)
    strip_x = pad
    strip_y = gem_cy - gem_r - m(8)
    strip_h = gem_r * 2 + m(34)
    strip_w = col_w * n
    row = pygame.Surface((strip_w, strip_h))
    row.fill((12, 13, 34))                          # flat neutral card-dark ground
    row_cy = strip_h // 2
    for i, key in enumerate(ORDER):
        rcx = col_w * i + col_w // 2
        pal = pal_of(key)
        soft_glow(row, rcx, row_cy, int(gem_r * 1.5), pal["glow"], 40, layers=8)
        gem_round(row, rcx, row_cy, gem_r, pal, mystery=(key == "mystery"))
    surf.blit(row, (strip_x, strip_y))

    # tier word labels (the LANGUAGE), gem-tinted so name + colour agree
    lab_y = title_h + gem_band + m(8)
    for i, key in enumerate(ORDER):
        cx = pad + col_w * i + col_w // 2
        pal = pal_of(key)
        word = "MYSTERY" if key == "mystery" else key.upper()
        plain_text(surf, word, font(15), (cx, lab_y), pal["gem"],
                   shadow_a=150, tracking=m(1), keyline=(8, 8, 20), kw=m(1.0))

    # ── ROW 2: grayscale proof strip (desaturate the gem row) ─────────────────
    proof_y = lab_y + label_band - m(2)
    plain_text(surf, "GRAYSCALE PROOF  (value separation — colourblind-safe)",
               font(10), (sheet_w // 2, proof_y - m(4)), (214, 218, 232),
               shadow_a=160, tracking=m(1), keyline=(8, 8, 20), kw=m(0.7))
    gray = grayscale_of(row)
    gp_y = proof_y + m(14)
    # frame + the desaturated gem row
    pygame.draw.rect(surf, (40, 42, 60), (strip_x - m(2), gp_y - m(2),
                     col_w * n + m(4), strip_h + m(4)), border_radius=m(6))
    surf.blit(gray, (strip_x, gp_y))
    pygame.draw.rect(surf, (90, 94, 116), (strip_x - m(2), gp_y - m(2),
                     col_w * n + m(4), strip_h + m(4)), width=max(1, m(1)),
                     border_radius=m(6))

    # ── ROW 3: thread on a placeholder card corner, 2–3 cut variants ──────────
    th_top = gp_y + strip_h + m(30)
    plain_text(surf, "CONSTELLATION THREAD + CUT VARIANTS  (on a dark card corner)",
               font(11), (sheet_w // 2, th_top), GOLD_PALE, shadow_a=130,
               tracking=m(1), keyline=(10, 10, 24), kw=m(0.7))
    # show the three cut alternatives, each on its own card corner, using the
    # most-at-risk tiers (epic violet, mystery silver) plus legendary to anchor.
    demo = [
        (gem_brilliant8, "epic",      "B  8-FACET"),
        (gem_marquise,   "mystery",   "C  MARQUISE"),
        (gem_emerald,    "legendary", "D  EMERALD"),
    ]
    corner_w = m(150)
    corner_h = m(110)
    cy0 = th_top + m(24)
    span = corner_w * len(demo) + m(16) * (len(demo) - 1)
    x0 = (sheet_w - span) // 2
    for i, (cutfn, key, lbl) in enumerate(demo):
        cx = x0 + i * (corner_w + m(16))
        rect = card_corner(surf, cx, cy0, corner_w, corner_h)
        pal = pal_of(key)
        # gem seated in the top-right corner with margin, node star down-left
        gx = rect.right - m(20)
        gy = rect.y + m(20)
        nx = rect.right - m(58)
        ny = rect.y + m(54)
        draw_thread(surf, gx, gy, nx, ny, pal)
        cutfn(surf, gx, gy, m(13), pal, mystery=(key == "mystery"))
        word = "MYSTERY" if key == "mystery" else key.upper()
        plain_text(surf, word, font(11), (rect.centerx, rect.bottom - m(20)),
                   pal["gem"], shadow_a=140, tracking=m(1),
                   keyline=(8, 8, 20), kw=m(0.8))
        plain_text(surf, lbl, font(9), (rect.centerx, rect.bottom - m(38)),
                   (190, 194, 212), shadow_a=110, tracking=m(1))

    # epic-vs-mystery side-by-side adjacency stress test, tiny corner size
    sty = cy0 + corner_h + m(20)
    plain_text(surf, "CORNER-SIZE ADJACENCY  epic / mystery / common  (must not muddy)",
               font(9), (sheet_w // 2, sty), (200, 204, 220), shadow_a=110,
               tracking=m(1))
    mini = [("epic", gem_round), ("mystery", gem_round), ("common", gem_round)]
    mx0 = sheet_w // 2 - m(64)
    for i, (key, fn) in enumerate(mini):
        cx = mx0 + i * m(64)
        pal = pal_of(key)
        # small dark swatch like a real grid corner
        sw = pygame.Surface((m(44), m(40)), pygame.SRCALPHA)
        for yy in range(m(40)):
            c = lerp_color(CARD_T, CARD_B, yy / m(40))
            pygame.draw.line(sw, (*c, 255), (0, yy), (m(44), yy))
        surf.blit(sw, (cx - m(22), sty + m(14)))
        fn(surf, cx, sty + m(34), m(8), pal, mystery=(key == "mystery"))
    return surf


def main():
    dev = render_device()
    w, h = dev.get_size()
    out = pygame.transform.smoothscale(dev, (w // SS, h // SS))
    path = os.path.join(_HERE, "round_1.png")
    pygame.image.save(out, path)
    print("saved", path, out.get_size())


if __name__ == "__main__":
    main()
