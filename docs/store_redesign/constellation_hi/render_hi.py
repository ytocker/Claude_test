"""
CONSTELLATION store — hi-resolution elevation (single-direction polish).

The amateur look of the v3 sheet is almost entirely aliasing + chunky 1px
shapes at 360x640. The fix is to author EVERYTHING resolution-independently
from a supersample factor SS, render the whole store onto a 360*SS x 640*SS
surface (every curve, bevel, hairline, gem facet, gradient row and glyph drawn
oversized), then ONE pygame.transform.smoothscale down to the 360x640 target.
The downscale is what turns oversized geometry into crisp anti-aliased edges —
no per-shape AA tricks needed, and type rendered at size*SS resolves razor
sharp.

All metrics flow through m(): a logical value times SS. Author in logical px,
draw in device px. Reuse the project palette + the Skybit night-jewel DNA from
concepts_v3 (glass cabochon, faceted rarity gem, gold constellation thread,
warm-gold balance capsule, unified chip, colourblind-safe 4-tier + mystery).

Both build targets safe: pure pygame, no numpy, no desktop/browser-only API.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from game.draw import lerp_color, NEAR_BLACK, WHITE
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE
from game import parrot
from game import store_catalog
from game.surprise_box_variants import _draw_qmark


# ── supersample ───────────────────────────────────────────────────────────────
SS = 4                       # 4x => 1440x2560 author canvas; the resolution lever
DW, DH = W * SS, H * SS       # device (supersample) dimensions


def m(v):
    """Logical px -> device px. Keeps geometry authored at 360x640 scale."""
    return int(round(v * SS))


def mf(v):
    return v * SS             # float variant for sub-pixel math


def font(size):
    """Project bold font at supersample size so glyph edges resolve crisp."""
    return _font(max(1, int(round(size * SS))), True)


def _stamp_bold(base, weight):
    """Faux-bold: composite the glyph onto itself at a RING of offsets one
    `weight` out (8 compass points) so strokes grow ~`weight` px evenly on all
    sides without filling counters solid. The project ships only the Bold ttf,
    so authored 'thicker' is this multi-stamp at SS where the fractional growth
    survives the downscale. Weights are small (≈1px target) on purpose."""
    # Callers express weight in logical px (m()); the visible thickening at the
    # downscaled target wants only ~0.5px, so the device ring radius is kept to
    # 1-2px regardless of SS.
    weight = max(0, min(m(0.5), int(round(weight * 0.42))))
    if weight <= 0:
        return base
    w, h = base.get_size()
    pad = weight + m(1)
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    ring = [(-weight, 0), (weight, 0), (0, -weight), (0, weight)]
    d = max(1, int(round(weight * 0.71)))
    ring += [(-d, -d), (d, -d), (-d, d), (d, d)]
    for dx, dy in ring:
        out.blit(base, (pad + dx, pad + dy))
    out.blit(base, (pad, pad))                     # center on top, crisp core
    return out


# ── catalog adapters ──────────────────────────────────────────────────────────
def _cost(sid):
    return store_catalog.cost(sid) if store_catalog.exists(sid) else 0


def _rarity(sid):
    return store_catalog.rarity(sid)


def _name(sid):
    return store_catalog.name(sid) if store_catalog.exists(sid) else "DEFAULT"


def _is_secret(sid):
    try:
        return store_catalog.is_secret(sid)
    except Exception:
        return sid == SECRET_ID


# ── sample set (spans all 4 tiers + equipped + masked secret) ─────────────────
SAMPLE_IDS = [
    "skin_bluegold",     # common
    "skin_owl",          # rare  -> EQUIPPED
    "skin_dragon",       # epic
    "skin_kitsune",      # legendary
    "skin_pharaoh",      # rare
    "skin_phoenix",      # epic
    "skin_aurora_stag",  # legendary
    "skin_ufo",          # secret (masked)
]
EQUIPPED_ID = "skin_owl"
SECRET_ID = "skin_ufo"
BALANCE = 14250
DETAIL_IDS = ["skin_bluegold", "skin_phoenix", "skin_ufo"]


# ── palette (CONSTELLATION DNA, retuned for depth) ────────────────────────────
# Richer multi-stop indigo->violet nebula instead of the flat 4-stop band.
BG_STOPS = [
    (0.00, (6, 7, 24)),
    (0.30, (11, 11, 40)),
    (0.55, (18, 16, 58)),
    (0.78, (26, 20, 72)),
    (1.00, (14, 12, 46)),
]
NEBULA_GLOW = (70, 60, 150)          # soft central violet bloom
GOLD = _GOLD_BRIGHT
GOLD_PALE = _GOLD_PALE
GOLD_DEEP = _GOLD_DEEP
TITLE_TOP = (255, 246, 200)
TITLE_BOT = (242, 182, 70)
TITLE_OUT = _RED_OUTLINE

RARITY = {
    "common":    {"gem": (214, 206, 230), "glow": (180, 174, 214), "deep": (78, 74, 112)},
    "rare":      {"gem": (108, 188, 252), "glow": (74, 158, 248),  "deep": (24, 78, 142)},
    "epic":      {"gem": (194, 122, 248), "glow": (172, 94, 244),  "deep": (80, 34, 126)},
    "legendary": {"gem": (255, 202, 104), "glow": (255, 168, 58),  "deep": (150, 92, 22)},
}
MYSTERY = {"gem": (226, 232, 244), "glow": (196, 214, 236), "deep": (90, 98, 124)}

CARD_T = (28, 30, 70)
CARD_B = (12, 13, 38)
CABO_LO = (22, 24, 50)
CABO_HI = (6, 7, 20)
CARD_RING_DEEP = (58, 48, 22)
CARD_RING_BRIGHT = (236, 202, 116)
NAME_COL = (246, 240, 216)
CREAM = (246, 244, 232)


# =============================================================================
# Low-level primitives — all SS-aware. They take device-px coords.
# =============================================================================

def vgrad(w, h, radius, top, bot, alpha=255, gamma=1.0):
    """Vertical gradient rounded-rect with per-row stops (no banding at SS)."""
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = (y / max(1, h - 1)) ** gamma
        c = lerp_color(top, bot, t)
        pygame.draw.line(body, (*c, alpha), (0, y), (w - 1, y))
    if radius > 0:
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return body


def multistop_v(w, h, stops, alpha=255):
    """Vertical multi-stop gradient (list of (t, color)); fills full surface."""
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
    """Additive feathered glow — many layers so the falloff is smooth at SS."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** 1.8)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


def drop_shadow(surf, rect, radius, blur, alpha, dy):
    """Multi-layer blurred outer shadow, offset down (top-left light source)."""
    for i in range(blur, 0, -1):
        a = int(alpha * (i / blur) ** 1.7 / blur * 2.4)
        if a <= 0:
            continue
        r = pygame.Rect(rect.x - i, rect.y - i + dy, rect.w + 2 * i, rect.h + 2 * i)
        s = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, a), s.get_rect(), border_radius=radius + i)
        surf.blit(s, r.topleft)


def _glyph_base(txt, font_obj, tracking):
    """White glyph master at SS, with optional letter tracking."""
    if tracking:
        widths = [font_obj.size(ch)[0] for ch in txt]
        total = sum(widths) + tracking * (len(txt) - 1)
        hh = font_obj.get_height()
        base = pygame.Surface((max(1, total), hh), pygame.SRCALPHA)
        x = 0
        for ch, wch in zip(txt, widths):
            base.blit(font_obj.render(ch, True, WHITE), (x, 0))
            x += wch + tracking
        return base
    return font_obj.render(txt, True, WHITE)


def gradient_text(surf, txt, font_obj, center, top, bot,
                  outline=None, ox=None, shadow=True, tracking=0, glow=None,
                  weight=None, keyline=None, kw=None):
    """Gradient-filled type, faux-bolded for weight, with a crisp dark keyline
    outline so body/title type reads heavy + sharp at the downscaled target.
    `weight` thickens strokes; `keyline` is a tight dark contour; `outline` is
    the wider coloured rim (e.g. the title's rust red)."""
    base = _glyph_base(txt, font_obj, tracking)
    if weight is None:
        weight = m(0.9)
    base = _stamp_bold(base, weight)
    w, hh = base.get_size()
    grad = pygame.Surface((w, hh), pygame.SRCALPHA)
    for y in range(hh):
        pygame.draw.line(grad, lerp_color(top, bot, y / max(1, hh - 1)),
                         (0, y), (w, y))
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    r = base.get_rect(center=center)
    if shadow:
        sh = base.copy()
        sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(150)
        surf.blit(sh, (r.x + m(0.5), r.y + m(2)))
    if glow:
        gs = base.copy()
        gs.fill((*glow, 255), special_flags=pygame.BLEND_RGBA_MULT)
        for off in (m(2), m(1)):
            for dx, dy in ((-off, 0), (off, 0), (0, -off), (0, off)):
                surf.blit(gs, (r.x + dx, r.y + dy), special_flags=pygame.BLEND_ADD)
    if outline:
        p = ox if ox is not None else m(1.5)
        out = base.copy()
        out.fill((*outline, 255), special_flags=pygame.BLEND_RGBA_MULT)
        for ang in range(0, 360, 30):
            dx = int(round(p * math.cos(math.radians(ang))))
            dy = int(round(p * math.sin(math.radians(ang))))
            surf.blit(out, (r.x + dx, r.y + dy))
    if keyline:
        p = kw if kw is not None else m(1)
        kl = base.copy()
        kl.fill((*keyline, 255), special_flags=pygame.BLEND_RGBA_MULT)
        for ang in range(0, 360, 45):
            dx = int(round(p * math.cos(math.radians(ang))))
            dy = int(round(p * math.sin(math.radians(ang))))
            surf.blit(kl, (r.x + dx, r.y + dy))
    surf.blit(grad, r.topleft)
    return r


def plain_text(surf, txt, font_obj, center, color, shadow_a=150, tracking=0,
               weight=None, keyline=None, kw=None):
    """Solid-colour type, faux-bolded for weight, with an optional crisp dark
    keyline so labels read heavy + sharp against the dark store ground."""
    base = _glyph_base(txt, font_obj, tracking)
    if weight is None:
        weight = m(0.8)
    base = _stamp_bold(base, weight)
    img = base.copy()
    img.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    r = img.get_rect(center=center)
    if shadow_a:
        sh = base.copy()
        sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow_a)
        surf.blit(sh, (r.x, r.y + m(1.5)))
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


def coin_glyph(surf, cx, cy, r, rim=GOLD_DEEP):
    """Beveled gold coin — radial face lit top-left + crisp rim + $ relief."""
    d = r * 2
    face = pygame.Surface((d + m(2), d + m(2)), pygame.SRCALPHA)
    c = r + m(1)
    edge = max(1, int(r * 0.10))
    for i in range(r, 0, -1):
        t = 1 - i / r
        # bright top-left to deep bottom-right body
        col = lerp_color((255, 233, 158), (196, 138, 36), t ** 0.85)
        pygame.draw.circle(face, (*col, 255), (c, c), i)
    # directional sheen: brighten the top-left arc
    sheen = pygame.Surface((d + m(2), d + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(sheen, (255, 248, 214, 150),
                       (c - r // 3, c - r // 3), int(r * 0.6))
    smask = pygame.Surface((d + m(2), d + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255), (c, c), r - edge)
    sheen.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    face.blit(sheen, (0, 0), special_flags=pygame.BLEND_ADD)
    # crisp double rim so the coin reads as a tactile object: dark contact
    # keyline outermost, bright gold inside it.
    pygame.draw.circle(face, (90, 56, 12, 255), (c, c), r, max(1, m(1.2)))
    pygame.draw.circle(face, (*rim, 240), (c, c), r - max(1, m(0.8)), max(1, m(1)))
    pygame.draw.circle(face, (255, 248, 206, 150), (c, c), r - edge, max(1, int(m(0.7))))
    if r >= m(5):
        sf = font(max(7, r * 0.95 / SS))
        sh = sf.render("$", True, (120, 80, 16))
        face.blit(sh, sh.get_rect(center=(c, c + m(1))))
        gl = sf.render("$", True, (255, 240, 188))
        face.blit(gl, gl.get_rect(center=(c, c - m(0.5))))
    surf.blit(face, face.get_rect(center=(cx, cy)))


def facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """Multi-facet rarity gem: a true cut with several value steps, a crisp
    girdle keyline, a dark seat well, and a hot specular pip. Drawn oversized;
    the downscale gives clean faceted edges."""
    # dark seat well so it reads on any ground
    seat = pygame.Surface((r * 2 + m(8), r * 2 + m(8)), pygame.SRCALPHA)
    sc = r + m(4)
    pygame.draw.circle(seat, (0, 0, 0, 170), (sc, sc), r + m(3))
    pygame.draw.circle(seat, (*GOLD_DEEP, 110), (sc, sc), r + m(3), max(1, m(0.8)))
    surf.blit(seat, (cx - sc, cy - sc))
    # crown facets around a small table
    top = (cx, cy - r)
    left = (cx - r, cy + int(r * 0.1))
    right = (cx + r, cy + int(r * 0.1))
    bot = (cx, cy + r)
    tbl_r = int(r * 0.42)
    tbl = [(cx, cy - tbl_r), (cx + tbl_r, cy),
           (cx, cy + tbl_r), (cx - tbl_r, cy)]
    if mystery:
        f1 = lerp_color((198, 216, 228), (216, 204, 226), 0.5)
        hi = lerp_color(f1, WHITE, 0.6)
        mid = f1
        sh = lerp_color(f1, deep, 0.45)
        dk = lerp_color(deep, NEAR_BLACK, 0.3)
        tbl_c = lerp_color(f1, WHITE, 0.35)
    else:
        hi = lerp_color(base, WHITE, 0.55)
        mid = base
        sh = lerp_color(base, deep, 0.5)
        dk = lerp_color(deep, NEAR_BLACK, 0.32)
        tbl_c = lerp_color(base, WHITE, 0.3)
    # outer crown facets (4) — lit top-left, dark bottom-right
    pygame.draw.polygon(surf, hi, [top, left, tbl[3], tbl[0]])
    pygame.draw.polygon(surf, mid, [top, right, tbl[1], tbl[0]])
    pygame.draw.polygon(surf, sh, [left, bot, tbl[2], tbl[3]])
    pygame.draw.polygon(surf, dk, [right, bot, tbl[2], tbl[1]])
    # table (flat top facet)
    pygame.draw.polygon(surf, tbl_c, tbl)
    # girdle + facet keylines
    klc = lerp_color(deep, NEAR_BLACK, 0.5)
    pygame.draw.polygon(surf, klc, [top, right, bot, left], width=max(1, m(0.6)))
    for p in (top, right, bot, left):
        pygame.draw.line(surf, (*klc, 200), p,
                         tbl[[top, right, bot, left].index(p)], max(1, m(0.5)))
    # hot specular pip upper-left of the table
    pr = max(1, int(r * 0.22))
    pip = pygame.Surface((pr * 2 + m(2), pr * 2 + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 250), (pr + m(1), pr + m(1)), pr)
    surf.blit(pip, (cx - pr - int(r * 0.28), cy - pr - int(r * 0.28)),
              special_flags=pygame.BLEND_ADD)


def cabochon(surf, cx, cy, r, glass_lo, glass_hi, ring=GOLD_DEEP, ring_a=120):
    """Glassmorphic domed cabochon well. Radial dark glass body, a 1px light
    edge, a darker refraction arc bottom-right, a bright crescent specular
    top-left, and a faint inner vignette so the thumbnail sits 'under glass'.
    Oversized + downscaled => a real polished dome, not a flat ring."""
    pad = m(4)
    disc = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
    # radial domed glass body
    for i in range(r, 0, -1):
        col = lerp_color(glass_lo, glass_hi, (i / r) ** 1.25)
        pygame.draw.circle(disc, (*col, 255), (c, c), i)
    # gentle inner vignette so contents settle into the well (kept subtle so
    # the rim doesn't read as a hard dark annulus around a bright ring).
    vig = pygame.Surface(disc.get_size(), pygame.SRCALPHA)
    for i in range(r, int(r * 0.78), -1):
        a = int(46 * (1 - (i - r * 0.78) / (r * 0.22)))
        pygame.draw.circle(vig, (0, 0, 0, max(0, a)), (c, c), i, max(1, m(0.6)))
    disc.blit(vig, (0, 0))
    surf.blit(disc, (cx - c, cy - c))


def cabochon_glass(surf, cx, cy, r, tint=(240, 234, 252)):
    """The translucent glass dome OVERLAY drawn ON TOP of the thumbnail:
    refraction arc bottom-right, crescent specular top-left, 1px light edge.
    Call after blitting the thumbnail so the macaw sits under the glass."""
    pad = m(4)
    over = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
    # darker refraction arc bottom-right (curved shadow inside the dome)
    arc = pygame.Surface(over.get_size(), pygame.SRCALPHA)
    for k in range(m(5)):
        a = int(60 * (1 - k / m(5)))
        pygame.draw.arc(arc, (10, 12, 30, a),
                        (c - r + k, c - r + k, (r - k) * 2, (r - k) * 2),
                        math.radians(250), math.radians(340), max(1, m(1)))
    amask = pygame.Surface(over.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(amask, (255, 255, 255, 255), (c, c), r - m(1))
    arc.blit(amask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    over.blit(arc, (0, 0))
    # bright crescent specular top-left: a soft disc minus an offset disc =>
    # a crescent that hugs the dome rim (the polished-glass tell). Kept low so
    # the glass reads translucent, not chrome.
    spec = pygame.Surface(over.get_size(), pygame.SRCALPHA)
    sr = int(r * 0.74)
    pygame.draw.circle(spec, (255, 255, 255, 80),
                       (c - int(r * 0.22), c - int(r * 0.22)), sr)
    # subtract a disc offset toward bottom-right so ONLY the top-left arc of the
    # specular survives — a true crescent hugging the lit rim, not a full ring.
    cut = pygame.Surface(over.get_size(), pygame.SRCALPHA)
    cut.fill((255, 255, 255, 255))
    pygame.draw.circle(cut, (0, 0, 0, 0),
                       (c + int(r * 0.18), c + int(r * 0.18)), int(r * 0.80))
    spec.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # keep it inside the dome
    smask = pygame.Surface(over.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255), (c, c), r - m(2))
    spec.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    over.blit(spec, (0, 0), special_flags=pygame.BLEND_ADD)
    # a soft top-left glass sheen bloom (broad, low) for the domed feel
    bloom = pygame.Surface(over.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(bloom, (255, 255, 255, 40),
                       (c - int(r * 0.34), c - int(r * 0.34)), int(r * 0.40))
    bmask = pygame.Surface(over.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(bmask, (255, 255, 255, 255), (c, c), r - m(2))
    bloom.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    over.blit(bloom, (0, 0), special_flags=pygame.BLEND_ADD)
    surf.blit(over, (cx - c, cy - c))
    # thin polished gold bezel: dark contact keyline (outer) + a fine warm-gold
    # rim. Restrained so the dome reads as glass set in gold, not a chrome ring.
    pygame.draw.circle(surf, (0, 0, 0, 180), (cx, cy), r, max(1, m(1.2)))
    pygame.draw.circle(surf, (168, 134, 64, 220), (cx, cy), r - m(0.8), max(1, m(1.1)))
    pygame.draw.circle(surf, (244, 214, 132, 150), (cx, cy), r - m(1.6), max(1, m(0.7)))
    # bright glass kiss on the upper-left rim arc only
    edge = pygame.Surface((r * 2 + m(4), r * 2 + m(4)), pygame.SRCALPHA)
    ec = r + m(2)
    pygame.draw.arc(edge, (255, 255, 255, 120),
                    (ec - r + m(1), ec - r + m(1), r * 2 - m(2), r * 2 - m(2)),
                    math.radians(110), math.radians(190), max(1, m(1)))
    surf.blit(edge, (cx - ec, cy - ec), special_flags=pygame.BLEND_ADD)


def gold_rule(surf, x0, x1, y, gold, peak=170, thick=None):
    """Hairline gold rule that fades to nothing at both ends."""
    thick = thick if thick is not None else max(1, m(1))
    w = x1 - x0
    line = pygame.Surface((w, thick + m(2)), pygame.SRCALPHA)
    for sx in range(w):
        hx = abs(sx - w / 2) / (w / 2)
        a = int(peak * (1.0 - hx ** 1.6))
        if a <= 0:
            continue
        for ty in range(thick):
            line.set_at((sx, m(1) + ty), (*gold, a))
    surf.blit(line, (x0, y - thick // 2))


def bevel_rim(surf, rect, radius, deep, bright, w):
    """Fine emboss: a dark outer keyline + a bright top-left inner stroke."""
    pygame.draw.rect(surf, deep, rect, width=w, border_radius=radius)
    inner = rect.inflate(-w, -w)
    br = bright if len(bright) == 4 else (*bright, 220)
    # bright stroke biased to top + left edges (the lit rim)
    hl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(hl, br, inner.move(-rect.x, -rect.y),
                     width=max(1, w // 2), border_radius=max(1, radius - w))
    grad = pygame.Surface(rect.size, pygame.SRCALPHA)
    for y in range(rect.h):
        a = int(255 * (1 - y / rect.h) ** 1.4)
        pygame.draw.line(grad, (255, 255, 255, a), (0, y), (rect.w, y))
    hl.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hl, rect.topleft)


def top_sheen(surf, rect, radius, h, peak=46):
    """Glossy top highlight across the upper portion of a panel."""
    sheen = pygame.Surface((rect.w, h), pygame.SRCALPHA)
    for y in range(h):
        pygame.draw.line(sheen, (255, 255, 255, int(peak * (1 - y / h) ** 1.3)),
                         (0, y), (rect.w, y))
    sm = pygame.Surface((rect.w, h), pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(),
                     border_top_left_radius=radius, border_top_right_radius=radius)
    sheen.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sheen, rect.topleft)


def contact_shadow(surf, rect, radius, depth, alpha=90):
    """Inner ambient-occlusion shadow hugging the bottom + right inner edges."""
    ao = pygame.Surface(rect.size, pygame.SRCALPHA)
    for i in range(depth):
        a = int(alpha * (1 - i / depth))
        pygame.draw.rect(ao, (0, 0, 0, a),
                         (i, i, rect.w - 2 * i, rect.h - 2 * i),
                         width=max(1, m(0.8)), border_radius=max(1, radius - i))
    # keep only bottom-right via a triangular mask
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(rect.w, 0), (rect.w, rect.h), (0, rect.h)])
    ao.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(ao, rect.topleft)


# ── thumbnail cache (rendered at SS box so it stays crisp) ────────────────────
_thumb_cache = {}


def _punch_contrast(img, boost=28):
    """Lift the skin's value separation from the dark dome WITHOUT inventing
    detail (AD note 4): a flat additive brighten across the silhouette so the
    macaw's mids/highlights gain range against the near-black well. Alpha is
    untouched (BLEND_RGB_ADD), so the silhouette edge stays clean."""
    out = img.copy()
    out.fill((boost, boost, boost, 0), special_flags=pygame.BLEND_RGB_ADD)
    return out


def _rim_light(img, color=(255, 248, 220), alpha=150, off=None):
    """Crisp top-left rim light so the silhouette pops off the dome: the alpha
    mask nudged up-left, minus the body, tinted bright = a contour highlight."""
    w, h = img.get_size()
    if off is None:
        off = max(1, m(0.6))
    rim = pygame.Surface((w, h), pygame.SRCALPHA)
    # silhouette tinted bright
    sil = img.copy()
    sil.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rim.blit(sil, (-off, -off))
    # subtract the body so only the protruding top-left edge survives
    cut = img.copy()
    cut.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rim.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    rim.set_alpha(alpha)
    return rim


def thumb(sid, box_px):
    key = (sid, box_px)
    out = _thumb_cache.get(key)
    if out is None:
        src = parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)
        bb = src.get_bounding_rect()
        if bb.width > 0 and bb.height > 0:
            src = src.subsurface(bb).copy()
        sw, sh = src.get_size()
        s = box_px / max(sw, sh)
        scaled = pygame.transform.smoothscale(
            src, (max(1, int(sw * s)), max(1, int(sh * s))))
        out = _punch_contrast(scaled)
        _thumb_cache[key] = out
    return out


def blit_thumb(surf, sid, cx, cy, box_px):
    """Place the (contrast-lifted) skin with a crisp top-left rim light so it
    reads as the lit hero inside the dome, not a flat sticker."""
    t = thumb(sid, box_px)
    r = t.get_rect(center=(cx, cy))
    surf.blit(_rim_light(t), r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(t, r.topleft)


# =============================================================================
# Layout metrics (logical px; flow through m())
# =============================================================================
CARD_W, CARD_H, GAP = 165, 99, 8
CARD_RAD = 17
R_DISC = 23
CY_DISC = 34
Y_NAME = 70
Y_CHIP = 86
GEM_R = 8
GRID_TOP = 146


# ── background: nebula + layered starfield + constellation lines ──────────────
_star_field = None
_const_lines = None


def _build_static_bg():
    global _star_field, _const_lines
    rnd = __import__("random").Random(70)
    stars = pygame.Surface((DW, DH), pygame.SRCALPHA)
    # three brightness/size strata for depth
    for n, rmin, rmax, amin, amax in ((180, 0.4, 0.9, 30, 90),
                                       (70, 0.9, 1.6, 70, 150),
                                       (24, 1.4, 2.6, 130, 220)):
        for _ in range(n):
            x = rnd.randint(0, DW)
            y = rnd.randint(0, DH)
            r = m(rnd.uniform(rmin, rmax))
            a = rnd.randint(amin, amax)
            tint = rnd.choice([(255, 252, 240), (220, 226, 255), (255, 240, 210)])
            pygame.draw.circle(stars, (*tint, a), (x, y), max(1, int(r)))
    # a handful of 4-point sparkles
    for _ in range(14):
        x = rnd.randint(m(20), DW - m(20))
        y = rnd.randint(m(20), DH - m(20))
        L = m(rnd.uniform(3, 6))
        a = rnd.randint(120, 210)
        col = (255, 246, 214, a)
        pygame.draw.line(stars, col, (x - L, y), (x + L, y), max(1, m(0.7)))
        pygame.draw.line(stars, col, (x, y - L), (x, y + L), max(1, m(0.7)))
        soft_glow(stars, x, y, m(3), (255, 244, 210), 80, layers=4)
    _star_field = stars

    # elegant constellation hairlines with node stars
    lines = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pts = [(40, 250), (96, 200), (152, 256), (216, 214), (300, 270),
           (60, 470), (140, 524), (250, 480), (322, 540),
           (300, 270), (250, 480)]
    chains = [pts[0:5], pts[5:9], [pts[4], pts[7]]]
    for chain in chains:
        for a, b in zip(chain, chain[1:]):
            pygame.draw.line(lines, (208, 182, 118, 40),
                             (m(a[0]), m(a[1])), (m(b[0]), m(b[1])), max(1, m(0.8)))
    seen = set()
    for px, py in pts:
        if (px, py) in seen:
            continue
        seen.add((px, py))
        soft_glow(lines, m(px), m(py), m(3), (255, 226, 160), 90, layers=4)
        pygame.draw.circle(lines, (255, 234, 180, 230), (m(px), m(py)), max(1, m(1.1)))
    _const_lines = lines


def draw_bg(surf):
    surf.blit(multistop_v(DW, DH, BG_STOPS), (0, 0))
    # soft central nebula bloom for real depth + a top vignette
    soft_glow(surf, DW // 2, int(DH * 0.42), m(200), NEBULA_GLOW, 60, layers=10)
    vig = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for y in range(DH):
        d = abs(y - DH * 0.5) / (DH * 0.5)
        a = int(70 * d ** 1.5)
        pygame.draw.line(vig, (0, 0, 6, a), (0, y), (DW, y))
    surf.blit(vig, (0, 0))
    surf.blit(_const_lines, (0, 0), special_flags=pygame.BLEND_ADD)
    surf.blit(_star_field, (0, 0), special_flags=pygame.BLEND_ADD)


# ── header ────────────────────────────────────────────────────────────────────
def title_wordmark(surf, txt, center, size, tracking):
    """Royal-Match-style gold BEVEL wordmark: ONE clean specular-swept gold fill
    with consistent stroke weight, a fine bright top emboss, a dark keyline for
    crisp delineation, and a single soft contact shadow. No chunky faux-3D
    extrude (that read amateur) — depth comes from the bevel + shadow only."""
    f = font(size)
    base = _glyph_base(txt, f, tracking)
    base = _stamp_bold(base, m(1.3))
    w, hh = base.get_size()
    r = base.get_rect(center=center)
    # soft contact shadow (single, blurred by multi-offset falloff)
    for k, a in ((m(3), 60), (m(2), 90), (m(1), 120)):
        sh = base.copy()
        sh.fill((6, 4, 14, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(a)
        surf.blit(sh, (r.x, r.y + k + m(2)))
    # NOTE: no additive offset-glow here. Offset additive copies of the glyph
    # accumulate in the inter-stroke gaps and read as pale blocks behind the
    # letters; the clean Royal-Match wordmark gets its depth from the contact
    # shadow + dark keyline + bevel crown instead.
    # crisp dark keyline contour so the gold edges read clean against the sky
    kl = base.copy()
    kl.fill((78, 40, 8, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for ang in range(0, 360, 30):
        dx = int(round(m(1.6) * math.cos(math.radians(ang))))
        dy = int(round(m(1.6) * math.sin(math.radians(ang))))
        surf.blit(kl, (r.x + dx, r.y + dy))
    # the gold body: a clean vertical gold gradient (consistent stroke weight,
    # no faux-3D extrude). Warm gold, NOT near-white, so the letterforms stay
    # legible; a single tight specular band sits in the upper third only.
    # The gold body. The gradient is mapped over the GLYPH's own vertical extent
    # (not the padded surface), so the bright crown sits at the true cap and the
    # deep amber at the true baseline — and the top stop is a warm gold, never
    # near-white, so the caps don't blow out to white blocks.
    bb = base.get_bounding_rect()
    top_y, gh = bb.y, max(1, bb.h)
    grad = pygame.Surface((w, hh), pygame.SRCALPHA)
    for y in range(hh):
        t = max(0.0, min(1.0, (y - top_y) / gh))
        if t < 0.5:
            c = lerp_color((252, 208, 116), (242, 180, 78), t / 0.5)
        else:
            c = lerp_color((242, 180, 78), (188, 118, 32), (t - 0.5) / 0.5)
        pygame.draw.line(grad, c, (0, y), (w, y))
    body = base.copy()
    body.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, r.topleft)
    # a single thin specular glint hugging just the cap edge (a few rows), low
    # alpha so it reads as a polished bevel crown, not a white cap.
    spec = pygame.Surface((w, hh), pygame.SRCALPHA)
    glint = max(1, int(gh * 0.07))
    for i in range(glint):
        a = int(40 * (1 - i / glint) ** 1.5)
        pygame.draw.line(spec, (255, 244, 206, a), (0, top_y + i), (w, top_y + i))
    sm = base.copy()
    sm.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
    spec.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(spec, r.topleft, special_flags=pygame.BLEND_ADD)
    return r


def draw_header(surf):
    # soft darkening band behind the title lane for legibility
    band = pygame.Surface((DW, m(112)), pygame.SRCALPHA)
    for y in range(m(112)):
        a = int(120 * (1 - y / m(112)) ** 1.2)
        pygame.draw.line(band, (16, 16, 48, a), (0, y), (DW, y))
    surf.blit(band, (0, 0))
    # screen frame hairline
    pygame.draw.rect(surf, (*GOLD, 60), (m(3), m(3), DW - m(6), DH - m(6)),
                     width=max(1, m(1)), border_radius=m(12))
    # TITLE — clean gold bevel wordmark. Baseline raised so the gap to the
    # balance capsule grows ~50% (AD note 2).
    title_wordmark(surf, "STORE", (DW // 2, m(28)), 31, tracking=m(4))
    balance_capsule(surf, DW // 2, m(74))
    tab_strip(surf, m(122))


def balance_capsule(surf, cx, y):
    """Jewel-grade recessed gold capsule. This is the money screen, so the
    NUMBER is large + loud (faux-bold gradient gold with a dark keyline); the
    coin sits in its own left cell with a guaranteed gap to the first digit
    (enforced at SS so it survives downscale); a crisp dark keyline + bright
    bevel make the capsule a clearly delineated object (user point 2)."""
    val = f"{BALANCE:,}"
    vf = font(25)                                  # larger/louder (AD note 2)
    vw = _glyph_base(val, vf, 0).get_width() + m(2)  # account for faux-bold
    coin_d, gapc, padl, padr = m(28), m(18), m(15), m(22)
    w = padl + coin_d + gapc + vw + padr
    h = m(44)
    cap = pygame.Rect(cx - w // 2, y - h // 2, w, h)
    drop_shadow(surf, cap, h // 2, blur=m(6), alpha=130, dy=m(3))
    surf.blit(vgrad(cap.w, cap.h, h // 2, (58, 42, 22), (22, 15, 8), 255, gamma=1.1),
              cap.topleft)
    top_sheen(surf, cap, h // 2, m(16), peak=50)
    # recessed inner well (contact shadow) + crisp double rim
    contact_shadow(surf, cap, h // 2, m(5), alpha=110)
    pygame.draw.rect(surf, (0, 0, 0, 200), cap, width=max(1, m(1.8)),
                     border_radius=h // 2)
    bevel_rim(surf, cap, h // 2, lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD_PALE, 240), w=max(1, m(1.8)))
    x = cap.x + padl
    soft_glow(surf, x + coin_d // 2, y, coin_d, (255, 206, 92), 120, layers=6)
    coin_glyph(surf, x + coin_d // 2, y, coin_d // 2)
    x += coin_d + gapc
    gradient_text(surf, val, vf, (x + vw // 2, y), (255, 250, 214), (240, 178, 66),
                  weight=m(1.0), keyline=(96, 56, 12), kw=m(1.2), shadow=True)


def tab_strip(surf, y):
    """ONE committed active state (AD note 5): a filled gold-tinted pill with
    dark bold text; inactive tabs clearly muted. Even cell spacing inside a
    recessed track with symmetric inner margins so PARCELS no longer hugs the
    right edge."""
    tabs = ("PARROTS", "ANIMALS", "COSTUMES", "PARCELS")
    active = 1
    f = font(12)
    th = m(32)
    edge = m(10)                                   # symmetric inner margin
    track_w = DW - m(2 * 14)                        # generous side gutters
    track = pygame.Rect((DW - track_w) // 2, y - th // 2, track_w, th)
    ts = pygame.Surface(track.size, pygame.SRCALPHA)
    pygame.draw.rect(ts, (8, 9, 22, 170), ts.get_rect(), border_radius=th // 2)
    surf.blit(ts, track.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 170), track, width=max(1, m(1.4)),
                     border_radius=th // 2)
    pygame.draw.rect(surf, (*GOLD, 80), track.inflate(-m(1.4), -m(1.4)),
                     width=max(1, m(1)), border_radius=th // 2)
    # equal-width cells so spacing is even end to end
    cell_w = (track_w - 2 * edge) / len(tabs)
    for i, t in enumerate(tabs):
        cxx = int(track.x + edge + cell_w * (i + 0.5))
        is_active = (i == active)
        if is_active:
            pw = int(cell_w) - m(4)
            pill = pygame.Rect(cxx - pw // 2, y - th // 2 + m(4), pw, th - m(8))
            surf.blit(vgrad(pill.w, pill.h, pill.h // 2,
                            (255, 214, 102), (200, 134, 34), 255, gamma=1.06),
                      pill.topleft)
            gloss_sweep(surf, pill, pill.h // 2, peak=110)
            pygame.draw.rect(surf, (92, 56, 12), pill, width=max(1, m(1.4)),
                             border_radius=pill.h // 2)
            bevel_rim(surf, pill, pill.h // 2, (92, 56, 12),
                      (*GOLD_PALE, 230), w=max(1, m(1.2)))
            plain_text(surf, t, f, (cxx, y), (52, 30, 6), shadow_a=0,
                       weight=m(0.9))
        else:
            plain_text(surf, t, f, (cxx, y), (138, 138, 162), shadow_a=140,
                       weight=m(0.6))


# ── chip family ───────────────────────────────────────────────────────────────
def gloss_sweep(surf, rect, radius, peak=120):
    """A diagonal specular sweep across the upper third — the wet-gloss tell
    that reads as polished metal/candy. Clipped to the chip's rounded body."""
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, int(rect.h * 0.5))
    for y in range(h):
        a = int(peak * (1 - y / h) ** 1.6)
        pygame.draw.line(sweep, (255, 255, 255, a), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)


def chip_body(surf, r, radius, top, bot, rim_dark, rim_bright, gloss=120,
              gamma=1.05):
    """One chip-body finish shared across the whole chip family: gradient fill,
    a diagonal gloss sweep, a crisp dark outer keyline AND a bright top-left
    bevel so every chip reads as a delineated tactile object (user point 2)."""
    drop_shadow(surf, r, radius, blur=m(4), alpha=110, dy=m(2))
    surf.blit(vgrad(r.w, r.h, radius, top, bot, 255, gamma=gamma), r.topleft)
    gloss_sweep(surf, r, radius, peak=gloss)
    contact_shadow(surf, r, radius, m(3), alpha=80)
    # dark contact keyline first so the bright bevel sits inside a defined edge
    pygame.draw.rect(surf, rim_dark, r, width=max(1, m(1.6)), border_radius=radius)
    bevel_rim(surf, r, radius, rim_dark, (*rim_bright, 235), w=max(1, m(1.5)))


# Two price-chip colour options the user can pick between. Option 1 is a single
# rich warm gold; option 2 is a brighter two-tone (champagne crown over amber).
PRICE_OPT = {
    # A — single rich warm gold, deep amber shade, dark-brown numerals.
    1: dict(top=(255, 206, 84), bot=(190, 124, 26),
            rim_dark=(92, 54, 10), rim_bright=(255, 238, 184),
            num=(54, 30, 4), coin_rim=(118, 72, 14)),
    # B — brighter champagne two-tone: a pale champagne crown over a saturated
    # amber base with a wider bright rim, for a more 'candy' premium feel.
    2: dict(top=(255, 244, 198), bot=(228, 158, 36),
            rim_dark=(116, 70, 12), rim_bright=(255, 252, 226),
            num=(86, 46, 6), coin_rim=(150, 92, 18), two_tone=True),
}


def price_chip(surf, cx, cy, text, h, variant=1, affordable=True):
    """Premium coin-price chip: rich separated gold body, crisp double rim,
    gloss sweep, a clean beveled coin glyph in its own cell, and dark
    high-contrast numerals (user point 3). Can't-afford uses a muted slate
    body + a small lock, sharing the same finish family."""
    opt = PRICE_OPT.get(variant, PRICE_OPT[1])
    coin_d = int(h * 0.66)
    pad = m(13)
    gapc = m(6)
    f = font(h * 0.50 / SS)
    nw = _glyph_base(text, f, 0).get_width() + m(2)  # account for faux-bold
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    if affordable:
        chip_body(surf, r, h // 2, opt["top"], opt["bot"],
                  opt["rim_dark"], opt["rim_bright"], gloss=130, gamma=1.08)
        if opt.get("two_tone"):
            # a defined champagne crown over the top ~46% so option B reads as a
            # distinct brighter two-tone, not a near-identical single gold.
            crown_h = int(r.h * 0.46)
            crown = pygame.Surface((r.w, crown_h), pygame.SRCALPHA)
            for yy in range(crown_h):
                a = int(150 * (1 - yy / crown_h) ** 1.2)
                pygame.draw.line(crown, (255, 250, 224, a), (0, yy), (r.w, yy))
            cm = pygame.Surface((r.w, crown_h), pygame.SRCALPHA)
            pygame.draw.rect(cm, (255, 255, 255, 255), (0, 0, r.w, h),
                             border_radius=h // 2)
            crown.blit(cm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surf.blit(crown, r.topleft)
        num_col = opt["num"]
        coin_rim = opt["coin_rim"]
    else:
        # can't-afford: a muted-but-still-legible slate body (one value step up
        # from before) with LIGHT numerals for contrast. The dimmed coin + cool
        # slate already read 'priced but locked', so no colliding lock glyph.
        chip_body(surf, r, h // 2, (96, 102, 124), (52, 56, 76),
                  (14, 16, 26), (168, 176, 198), gloss=80)
        num_col = (236, 240, 250)
        coin_rim = (78, 84, 104)
    x = r.x + pad
    coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2, rim=coin_rim)
    x += coin_d + gapc
    plain_text(surf, text, f, (x + nw // 2, cy), num_col, shadow_a=0,
               weight=m(1.0), keyline=(20, 24, 38) if not affordable else None,
               kw=m(0.7))
    return r


def status_chip(surf, cx, cy, text, h, kind="equip"):
    """EQUIP / EQUIPPED chips, same finish family as the price chip so the row
    reads as one product line."""
    if kind == "equipped":
        top, bot = (92, 214, 132), (30, 132, 70)
        rim_dark, rim_bright = (10, 60, 30), (190, 255, 214)
        num = (8, 40, 18)
    else:  # equip (owned, not active) — neutral cream-gold
        top, bot = (240, 236, 224), (176, 168, 148)
        rim_dark, rim_bright = (60, 52, 32), (255, 252, 244)
        num = (52, 40, 18)
    f = font(h * 0.48 / SS)
    nw = _glyph_base(text, f, 0).get_width() + m(2)
    pad = m(15)
    w = pad * 2 + nw
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    chip_body(surf, r, h // 2, top, bot, rim_dark, rim_bright, gloss=120)
    plain_text(surf, text, f, r.center, num, shadow_a=0, weight=m(0.9))
    return r


# The default price-chip colour used across the live store screen.
PRICE_VARIANT = 1


def state_chip(surf, sid, cx, cy, equipped, secret, h, variant=PRICE_VARIANT):
    if equipped:
        return status_chip(surf, cx, cy, "EQUIPPED", h, kind="equipped")
    price = _cost(sid)
    return price_chip(surf, cx, cy, f"{price:,}", h, variant=variant,
                      affordable=BALANCE >= price)


# ── card ──────────────────────────────────────────────────────────────────────
def fit_name(surf, name, cx, cy, max_w):
    sz = 16                                        # larger item name (user pt 1)
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 10:
        sz -= 1
        f = font(sz)
    # heavy + crisp: faux-bold + a dark keyline for strong contrast on the card
    plain_text(surf, name, f, (cx, cy), NAME_COL, shadow_a=170,
               weight=m(1.0), keyline=(8, 8, 20), kw=m(1.1))


def draw_const_thread(surf, rect, gx, gy, cx, cy, pal):
    """A deliberate brighter TAPERED thread (corner gem -> dome) with a node
    star (AD note 6): drawn as stacked lines of decreasing width so it reads
    as an intentional constellation link, not a stray hairline."""
    mid = (rect.centerx + m(16), cy - m(R_DISC) - m(4))
    thread = pygame.Surface(rect.size, pygame.SRCALPHA)
    a, b = (gx - rect.x, gy - rect.y), (mid[0] - rect.x, mid[1] - rect.y)
    for wth, al in ((m(2.0), 60), (m(1.2), 130), (m(0.6), 210)):
        pygame.draw.line(thread, (*pal["glow"], al), a, b, max(1, int(wth)))
    nx, ny = (a[0] + b[0]) // 2, (a[1] + b[1]) // 2
    soft_glow(thread, nx, ny, m(3.5), pal["gem"], 150, layers=5)
    pygame.draw.circle(thread, (255, 255, 255, 230), (nx, ny), max(1, m(1.4)))
    pygame.draw.circle(thread, (*pal["gem"], 255), (nx, ny), max(1, m(1.0)))
    surf.blit(thread, rect.topleft, special_flags=pygame.BLEND_ADD)


def draw_card(surf, sid, rect, equipped, variant=PRICE_VARIANT):
    secret = _is_secret(sid)
    pal = MYSTERY if secret else RARITY[_rarity(sid)]
    rad = m(CARD_RAD)
    # DEPTH STACK: soft multi-layer drop shadow (top-left light => offset down)
    drop_shadow(surf, rect, rad, blur=m(8), alpha=160, dy=m(4))
    # body gradient + glossy top sheen + bevel rim + bottom-right contact AO.
    # Sheen + rim authored brighter/wider so the GRID cards carry the same lit
    # tactile finish as detail.png (AD note 3 / user point 2).
    surf.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
              rect.topleft)
    top_sheen(surf, rect, rad, m(30), peak=62)
    contact_shadow(surf, rect, rad, m(7), alpha=95)
    # crisp dark outer keyline UNDER the bright bevel so the card edge is clearly
    # defined against the dark sky.
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(surf, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    cx, cy = rect.centerx, rect.y + m(CY_DISC)
    gx, gy = rect.right - m(17), rect.y + m(17)
    draw_const_thread(surf, rect, gx, gy, cx, cy, pal)

    # BAND A — cabochon (glass dome over thumbnail). A whisper-soft tier aura
    # behind the dome (NOT a hard ring) so the macaw stays the hero.
    soft_glow(surf, cx, cy, m(R_DISC + 3), pal["glow"], 32, layers=8)
    cabochon(surf, cx, cy, m(R_DISC), CABO_LO, CABO_HI,
             ring=pal["gem"], ring_a=50)
    if secret:
        _draw_qmark(surf, cx, cy, m(R_DISC + 6), CREAM, NEAR_BLACK, thick=m(2))
        name = "???"
    else:
        blit_thumb(surf, sid, cx, cy, m(R_DISC) * 1.5)
        name = _name(sid)
    cabochon_glass(surf, cx, cy, m(R_DISC), tint=pal["gem"])

    # corner GEM — seated with margin
    facet_gem(surf, gx, gy, m(GEM_R), pal["gem"], pal["deep"], mystery=secret)

    # gold map-rule under the name lane
    gold_rule(surf, rect.x + m(30), rect.right - m(30),
              rect.y + m(Y_NAME) + m(12), GOLD, peak=80)
    # BAND B — name
    fit_name(surf, name, rect.centerx, rect.y + m(Y_NAME), rect.w - m(26))
    # BAND C — chip
    state_chip(surf, sid, rect.centerx, rect.y + m(Y_CHIP), equipped, secret,
               m(23), variant=variant)

    if equipped:
        halo = pygame.Surface((rect.w + m(16), rect.h + m(16)), pygame.SRCALPHA)
        for k in range(5, 0, -1):
            pygame.draw.rect(halo, (*GOLD, int(22 * k / 5)),
                             (m(8) - k * m(1), m(8) - k * m(1),
                              rect.w + 2 * k * m(1), rect.h + 2 * k * m(1)),
                             width=max(1, m(1.4)), border_radius=rad + k * m(1))
        surf.blit(halo, (rect.x - m(8), rect.y - m(8)), special_flags=pygame.BLEND_ADD)
        pygame.draw.rect(surf, GOLD, rect, width=max(1, m(2)), border_radius=rad)


# ── page controls + back ──────────────────────────────────────────────────────
def draw_page_controls(surf, base_x):
    grid_bottom = m(GRID_TOP) + 4 * m(CARD_H) + 3 * m(GAP)
    cy = grid_bottom + m(15)
    plain_text(surf, "PAGE  1 / 3", font(12), (DW // 2, cy), GOLD_PALE,
               shadow_a=150, weight=m(0.8), keyline=(10, 10, 22), kw=m(0.8))
    # +15% tap targets (AD note 8): 34x24 -> ~39x28, crisp double rim
    aw, ah = m(39), m(28)
    for gx, glyph in ((base_x + m(20), "<"),
                      (base_x + m(CARD_W) * 2 + m(GAP) - m(20), ">")):
        r = pygame.Rect(0, 0, aw, ah)
        r.center = (gx, cy)
        drop_shadow(surf, r, m(13), blur=m(4), alpha=100, dy=m(2))
        surf.blit(vgrad(r.w, r.h, m(13), (58, 44, 24), (26, 19, 11), 255), r.topleft)
        top_sheen(surf, r, m(13), m(9), peak=56)
        pygame.draw.rect(surf, (12, 10, 4), r, width=max(1, m(1.4)),
                         border_radius=m(13))
        bevel_rim(surf, r, m(13), (60, 40, 12), (*GOLD_PALE, 220), w=max(1, m(1.2)))
        plain_text(surf, glyph, font(16), (gx, cy - m(1)), GOLD_PALE, shadow_a=0,
                   weight=m(0.9))


def draw_back(surf):
    # more bottom margin (AD note 8): center raised off the screen edge
    r = pygame.Rect(0, 0, m(172), m(38))
    r.center = (DW // 2, DH - m(30))
    drop_shadow(surf, r, m(19), blur=m(6), alpha=130, dy=m(3))
    surf.blit(vgrad(r.w, r.h, m(19), (34, 32, 70), (16, 16, 40), 250), r.topleft)
    top_sheen(surf, r, m(19), m(15), peak=50)
    contact_shadow(surf, r, m(19), m(4), alpha=85)
    pygame.draw.rect(surf, (4, 5, 16), r, width=max(1, m(1.8)), border_radius=m(19))
    bevel_rim(surf, r, m(19), lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD, 220), w=max(1, m(1.5)))
    # left chevron
    cxx = r.x + m(28)
    pygame.draw.lines(surf, GOLD_PALE, False,
                      [(cxx + m(5), r.centery - m(7)),
                       (cxx - m(3), r.centery),
                       (cxx + m(5), r.centery + m(7))], max(1, m(2.4)))
    plain_text(surf, "BACK", font(18), (r.centerx + m(8), r.centery),
               GOLD_PALE, shadow_a=170, weight=m(1.0), keyline=(40, 26, 6), kw=m(1.0))


# ── modal ─────────────────────────────────────────────────────────────────────
def draw_modal(surf, sid, variant=PRICE_VARIANT):
    # flatter, cleaner scrim so the panel pops (AD note 7): ~70% flat dim
    scrim = pygame.Surface((DW, DH), pygame.SRCALPHA)
    scrim.fill((3, 4, 10, 180))
    surf.blit(scrim, (0, 0))
    secret = _is_secret(sid)
    tier = _rarity(sid)
    pal = MYSTERY if secret else RARITY[tier]
    pw, ph = m(264), m(322)
    panel = pygame.Rect((DW - pw) // 2, (DH - ph) // 2, pw, ph)
    rad = m(20)
    drop_shadow(surf, panel, rad, blur=m(12), alpha=200, dy=m(7))
    surf.blit(vgrad(pw, ph, rad, (30, 30, 70), (12, 12, 36), 255, gamma=1.15),
              panel.topleft)
    top_sheen(surf, panel, rad, m(34), peak=58)
    contact_shadow(surf, panel, rad, m(8), alpha=95)
    pygame.draw.rect(surf, (3, 4, 14), panel, width=max(1, m(2)), border_radius=rad)
    bevel_rim(surf, panel, rad, lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD, 240), w=max(1, m(2.0)))
    cx = panel.centerx
    plain_text(surf, "CONFIRM PURCHASE", font(14), (cx, panel.y + m(28)),
               GOLD_PALE, shadow_a=150, tracking=m(1), weight=m(0.9),
               keyline=(10, 10, 24), kw=m(0.9))
    gold_rule(surf, panel.x + m(30), panel.right - m(30), panel.y + m(46), GOLD, peak=180)
    # STAGE — large cabochon dome
    disc_cy = panel.y + m(108)
    R = m(44)
    soft_glow(surf, cx, disc_cy, R + m(4), pal["glow"], 44, layers=8)
    cabochon(surf, cx, disc_cy, R, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=55)
    if secret:
        _draw_qmark(surf, cx, disc_cy, R + m(8), CREAM, NEAR_BLACK, thick=m(3))
        name = "???"
    else:
        blit_thumb(surf, sid, cx, disc_cy, R * 1.5)
        name = _name(sid)
    cabochon_glass(surf, cx, disc_cy, R, tint=pal["gem"])
    # seat the corner gem deliberately ON the dome rim (45° up-right) so it reads
    # as set into the bezel, not floating (AD note 7).
    grad45 = R * 0.7071
    facet_gem(surf, int(cx + grad45), int(disc_cy - grad45), m(10),
              pal["gem"], pal["deep"], mystery=secret)
    plain_text(surf, name, font(20), (cx, panel.y + m(182)), GOLD, shadow_a=160,
               weight=m(1.0), keyline=(60, 36, 8), kw=m(1.1))
    rword = "MYSTERY" if secret else tier.upper()
    plain_text(surf, rword, font(11), (cx, panel.y + m(203)), pal["gem"],
               shadow_a=130, tracking=m(1), weight=m(0.7))
    price = _cost(sid)
    price_chip(surf, cx, panel.y + m(232), f"{price:,}", m(32), variant=variant,
               affordable=True)
    # buttons
    bw, bh, gut = m(106), m(42), m(16)
    by = panel.bottom - m(34)
    nx = cx - (bw * 2 + gut) // 2
    cancel = pygame.Rect(nx, by - bh // 2, bw, bh)
    buy = pygame.Rect(nx + bw + gut, by - bh // 2, bw, bh)
    # CANCEL — one value step lighter than the panel so it reads as a secondary
    # control on the panel, not part of it (AD note 7).
    drop_shadow(surf, cancel, bh // 2, blur=m(3), alpha=100, dy=m(2))
    surf.blit(vgrad(bw, bh, bh // 2, (84, 80, 104), (52, 48, 70)), cancel.topleft)
    top_sheen(surf, cancel, bh // 2, m(14), peak=46)
    pygame.draw.rect(surf, (18, 18, 30), cancel, width=max(1, m(1.6)),
                     border_radius=bh // 2)
    bevel_rim(surf, cancel, bh // 2, (18, 18, 30), (188, 184, 204, 220),
              w=max(1, m(1.2)))
    plain_text(surf, "CANCEL", font(15), cancel.center, CREAM, shadow_a=130,
               weight=m(0.9), keyline=(14, 14, 26), kw=m(0.9))
    # BUY — primary CTA: outer glow + gradient gold body + gloss sweep + a subtle
    # inner top glow so it reads as the lit, pressable hero (AD note 7).
    bglow = pygame.Surface((bw + m(16), bh + m(16)), pygame.SRCALPHA)
    for k in range(6, 0, -1):
        pygame.draw.rect(bglow, (*GOLD, int(28 * k / 6)),
                         (m(8) - k * m(1.4), m(8) - k * m(1.4),
                          bw + 2 * k * m(1.4), bh + 2 * k * m(1.4)),
                         border_radius=bh // 2 + int(k * m(1.4)))
    surf.blit(bglow, (buy.x - m(8), buy.y - m(8)), special_flags=pygame.BLEND_ADD)
    drop_shadow(surf, buy, bh // 2, blur=m(3), alpha=100, dy=m(2))
    surf.blit(vgrad(bw, bh, bh // 2, (255, 218, 108), (200, 132, 32), gamma=1.06),
              buy.topleft)
    gloss_sweep(surf, buy, bh // 2, peak=150)
    # subtle inner glow: a soft bright bloom seated just inside the top edge
    inner = pygame.Surface((bw, bh), pygame.SRCALPHA)
    soft_glow(inner, bw // 2, int(bh * 0.32), int(bw * 0.42), (255, 250, 220),
              90, layers=6)
    im = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(im, (255, 255, 255, 255), im.get_rect(), border_radius=bh // 2)
    inner.blit(im, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(inner, buy.topleft, special_flags=pygame.BLEND_ADD)
    pygame.draw.rect(surf, (90, 54, 10), buy, width=max(1, m(1.6)),
                     border_radius=bh // 2)
    bevel_rim(surf, buy, bh // 2, (90, 54, 10), (*GOLD_PALE, 235), w=max(1, m(1.4)))
    plain_text(surf, "BUY", font(17), buy.center, (52, 30, 6), shadow_a=0,
               weight=m(1.0))


# =============================================================================
# Compose + downscale
# =============================================================================
def render_store_device():
    surf = pygame.Surface((DW, DH))
    draw_bg(surf)
    draw_header(surf)
    base_x = (DW - (m(CARD_W) * 2 + m(GAP))) // 2
    for idx, sid in enumerate(SAMPLE_IDS):
        x = base_x + (idx % 2) * (m(CARD_W) + m(GAP))
        y = m(GRID_TOP) + (idx // 2) * (m(CARD_H) + m(GAP))
        draw_card(surf, sid, pygame.Rect(x, y, m(CARD_W), m(CARD_H)),
                  sid == EQUIPPED_ID)
    draw_page_controls(surf, base_x)
    draw_back(surf)
    return surf


def downscale(device_surf, scale=1):
    """Smoothscale the SS surface to the final target (scale=1 => 360x640)."""
    tw, th = W * scale, H * scale
    return pygame.transform.smoothscale(device_surf, (tw, th))


def render_detail_device():
    """A close-inspection sheet: the 3 hero cards on top (dome / gem / thread /
    finish) PLUS a dedicated price-chip OPTIONS bay so the user can pick the
    cost-chip colour. Option A is the default used in the live screen."""
    ids = DETAIL_IDS
    pad = m(20)
    g = m(16)
    cols = len(ids)
    sw = m(CARD_W) * cols + g * (cols - 1) + pad * 2
    chip_bay = m(132)                              # extra height for the chip row
    sh = m(CARD_H) + pad * 2 + m(30) + chip_bay
    strip = pygame.Surface((sw, sh))
    strip.blit(multistop_v(sw, sh, BG_STOPS), (0, 0))
    soft_glow(strip, sw // 2, m(120), m(150), NEBULA_GLOW, 50, layers=8)
    plain_text(strip, "GLASS DOME  /  GEM FACETS  /  RIM-LIT SKIN  /  CONSTELLATION THREAD",
               font(11), (sw // 2, m(15)), GOLD_PALE, shadow_a=130, weight=m(0.8),
               keyline=(10, 10, 24), kw=m(0.7))
    for i, sid in enumerate(ids):
        x = pad + i * (m(CARD_W) + g)
        y = m(30) + pad
        draw_card(strip, sid, pygame.Rect(x, y, m(CARD_W), m(CARD_H)),
                  sid == EQUIPPED_ID)

    # ── price-chip colour options bay ────────────────────────────────────────
    by0 = m(30) + pad + m(CARD_H) + m(24)
    # a faint divider rule
    gold_rule(strip, pad, sw - pad, by0 - m(10), GOLD, peak=120, thick=m(1.2))
    plain_text(strip, "PRICE CHIP — PICK A COLOUR  (Option A is the default)",
               font(11), (sw // 2, by0 + m(4)), GOLD_PALE, shadow_a=130,
               weight=m(0.8), keyline=(10, 10, 24), kw=m(0.7))
    row_y = by0 + m(46)
    ch = m(28)
    col_l = sw // 3
    col_r = sw - sw // 3
    plain_text(strip, "OPTION A — RICH GOLD", font(10), (col_l, by0 + m(26)),
               (236, 214, 150), shadow_a=120, weight=m(0.7))
    plain_text(strip, "OPTION B — CHAMPAGNE TWO-TONE", font(10), (col_r, by0 + m(26)),
               (236, 214, 150), shadow_a=120, weight=m(0.7))
    # affordable + locked sample, both variants
    price_chip(strip, col_l, row_y, "1,200", ch, variant=1, affordable=True)
    price_chip(strip, col_l, row_y + m(40), "7,000", ch, variant=1, affordable=False)
    price_chip(strip, col_r, row_y, "1,200", ch, variant=2, affordable=True)
    price_chip(strip, col_r, row_y + m(40), "7,000", ch, variant=2, affordable=False)
    # the shared EQUIPPED / EQUIP finish (one family)
    status_chip(strip, sw // 2, row_y + m(40), "EQUIPPED", ch, kind="equipped")
    return strip


def main():
    _build_static_bg()
    # full store
    dev = render_store_device()
    pygame.image.save(downscale(dev, 1), os.path.join(_HERE, "store.png"))
    pygame.image.save(downscale(dev, 2), os.path.join(_HERE, "store@2x.png"))
    # modal (over the store)
    dev_m = render_store_device()
    draw_modal(dev_m, "skin_phoenix")
    pygame.image.save(downscale(dev_m, 1), os.path.join(_HERE, "modal.png"))
    pygame.image.save(downscale(dev_m, 2), os.path.join(_HERE, "modal@2x.png"))
    # detail zoom — keep more device resolution (downscale to 1.4x logical)
    dev_d = render_detail_device()
    dw, dh = dev_d.get_size()
    det = pygame.transform.smoothscale(dev_d, (int(dw / SS * 1.6), int(dh / SS * 1.6)))
    pygame.image.save(det, os.path.join(_HERE, "detail.png"))
    print("SS =", SS, "device =", DW, "x", DH)
    print("saved store.png / store@2x.png / modal.png / modal@2x.png / detail.png")


if __name__ == "__main__":
    main()
