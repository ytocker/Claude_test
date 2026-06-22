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


def gradient_text(surf, txt, font_obj, center, top, bot,
                  outline=None, ox=None, shadow=True, tracking=0, glow=None):
    """Gradient-filled type with optional outline, soft glow + drop shadow."""
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
        base = font_obj.render(txt, True, WHITE)
    w, hh = base.get_size()
    grad = pygame.Surface((w, hh), pygame.SRCALPHA)
    for y in range(hh):
        pygame.draw.line(grad, lerp_color(top, bot, y / max(1, hh - 1)),
                         (0, y), (w, y))
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    r = base.get_rect(center=center)
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
        for dx, dy in ((-p, 0), (p, 0), (0, -p), (0, p),
                       (-p, -p), (p, -p), (-p, p), (p, p)):
            surf.blit(out, (r.x + dx, r.y + dy))
    if shadow:
        sh = base.copy()
        sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(150)
        surf.blit(sh, (r.x + m(0.5), r.y + m(1.5)))
    surf.blit(grad, r.topleft)
    return r


def plain_text(surf, txt, font_obj, center, color, shadow_a=150, tracking=0):
    if tracking:
        widths = [font_obj.size(ch)[0] for ch in txt]
        total = sum(widths) + tracking * (len(txt) - 1)
        hh = font_obj.get_height()
        img = pygame.Surface((max(1, total), hh), pygame.SRCALPHA)
        x = 0
        for ch, wch in zip(txt, widths):
            img.blit(font_obj.render(ch, True, color), (x, 0))
            x += wch + tracking
    else:
        img = font_obj.render(txt, True, color)
    r = img.get_rect(center=center)
    if shadow_a:
        sh = img.copy()
        sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow_a)
        surf.blit(sh, (r.x, r.y + m(1)))
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
    pygame.draw.circle(face, (*rim, 235), (c, c), r, max(1, m(0.8)))
    pygame.draw.circle(face, (255, 244, 200, 120), (c, c), r - edge, max(1, int(m(0.6))))
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
        out = pygame.transform.smoothscale(
            src, (max(1, int(sw * s)), max(1, int(sh * s))))
        _thumb_cache[key] = out
    return out


# =============================================================================
# Layout metrics (logical px; flow through m())
# =============================================================================
CARD_W, CARD_H, GAP = 165, 99, 8
CARD_RAD = 17
R_DISC = 23
CY_DISC = 34
Y_NAME = 71
Y_CHIP = 89
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
def draw_header(surf):
    # soft darkening band behind the title lane for legibility
    band = pygame.Surface((DW, m(98)), pygame.SRCALPHA)
    for y in range(m(98)):
        a = int(120 * (1 - y / m(98)) ** 1.2)
        pygame.draw.line(band, (16, 16, 48, a), (0, y), (DW, y))
    surf.blit(band, (0, 0))
    # screen frame hairline
    pygame.draw.rect(surf, (*GOLD, 60), (m(3), m(3), DW - m(6), DH - m(6)),
                     width=max(1, m(1)), border_radius=m(12))
    # TITLE lane
    gradient_text(surf, "STORE", font(30), (DW // 2, m(30)),
                  TITLE_TOP, TITLE_BOT, outline=TITLE_OUT, tracking=m(3),
                  glow=(120, 96, 30))
    balance_capsule(surf, DW // 2, m(70))
    tab_strip(surf, m(118))


def balance_capsule(surf, cx, y):
    """Jewel-grade recessed gold capsule: coin in its own left cell with a real
    gap before gradient-gold digits; lit top sheen + dark inner contact rim."""
    val = f"{BALANCE:,}"
    vf = font(20)
    vw = vf.size(val)[0]
    coin_d, gapc, padl, padr = m(24), m(14), m(14), m(18)
    w = padl + coin_d + gapc + vw + padr
    h = m(38)
    cap = pygame.Rect(cx - w // 2, y - h // 2, w, h)
    drop_shadow(surf, cap, h // 2, blur=m(5), alpha=120, dy=m(3))
    surf.blit(vgrad(cap.w, cap.h, h // 2, (52, 38, 20), (22, 15, 8), 255, gamma=1.1),
              cap.topleft)
    top_sheen(surf, cap, h // 2, m(14), peak=44)
    # recessed inner well (contact shadow) + lit gold rim
    contact_shadow(surf, cap, h // 2, m(5), alpha=110)
    pygame.draw.rect(surf, (0, 0, 0, 150), cap.inflate(-m(2), -m(2)),
                     width=max(1, m(1)), border_radius=h // 2 - m(1))
    bevel_rim(surf, cap, h // 2, lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD_PALE, 230), w=max(1, m(1.4)))
    x = cap.x + padl
    soft_glow(surf, x + coin_d // 2, y, coin_d, (255, 206, 92), 110, layers=6)
    coin_glyph(surf, x + coin_d // 2, y, coin_d // 2)
    x += coin_d + gapc
    gradient_text(surf, val, vf, (x + vw // 2, y), (255, 248, 200), (236, 172, 64))


def tab_strip(surf, y):
    tabs = ("PARROTS", "ANIMALS", "COSTUMES", "PARCELS")
    active = 1
    f = font(12)
    pad, gap = m(12), m(8)
    widths = [f.size(t)[0] + 2 * pad for t in tabs]
    total = sum(widths) + gap * (len(tabs) - 1)
    while total > DW - m(16) and pad > m(5):
        pad -= m(1)
        gap = max(m(4), gap - m(1))
        widths = [f.size(t)[0] + 2 * pad for t in tabs]
        total = sum(widths) + gap * (len(tabs) - 1)
    x = (DW - total) // 2
    th = m(30)
    track = pygame.Rect(x - m(8), y - th // 2, total + m(16), th)
    ts = pygame.Surface(track.size, pygame.SRCALPHA)
    pygame.draw.rect(ts, (8, 9, 22, 150), ts.get_rect(), border_radius=th // 2)
    pygame.draw.rect(ts, (255, 255, 255, 18), (0, 0, track.w, th // 2),
                     border_top_left_radius=th // 2, border_top_right_radius=th // 2)
    surf.blit(ts, track.topleft)
    pygame.draw.rect(surf, (*GOLD, 70), track, width=max(1, m(1)), border_radius=th // 2)
    for i, t in enumerate(tabs):
        w = widths[i]
        cxx = x + w // 2
        is_active = (i == active)
        if is_active:
            pill = pygame.Rect(x + m(3), y - th // 2 + m(4), w - m(6), th - m(8))
            surf.blit(vgrad(pill.w, pill.h, pill.h // 2,
                            lerp_color(GOLD, WHITE, 0.15), GOLD_DEEP, 255),
                      pill.topleft)
            top_sheen(surf, pill, pill.h // 2, m(8), peak=70)
            pygame.draw.rect(surf, GOLD_PALE, pill, width=max(1, m(1)),
                             border_radius=pill.h // 2)
            plain_text(surf, t, f, (cxx, y), (44, 28, 8), shadow_a=0)
        else:
            plain_text(surf, t, f, (cxx, y), (196, 192, 212), shadow_a=120)
        x += w + gap


# ── chip family ───────────────────────────────────────────────────────────────
def chip(surf, cx, cy, text, fg, bg, rim, h, coin=False, lock=False):
    f = font(h * 0.52 / SS)
    timg = f.render(text, True, fg)
    coin_d = int(h * 0.64)
    pre = (coin_d + m(5)) if coin else (m(13) if lock else 0)
    pad = m(13)
    w = pre + timg.get_width() + pad * 2
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    drop_shadow(surf, r, h // 2, blur=m(3), alpha=90, dy=m(2))
    surf.blit(vgrad(w, h, h // 2, lerp_color(bg, WHITE, 0.22), bg, 255, gamma=1.1),
              r.topleft)
    top_sheen(surf, r, h // 2, h // 2, peak=56)
    contact_shadow(surf, r, h // 2, m(3), alpha=70)
    pygame.draw.rect(surf, rim, r, width=max(1, m(1)), border_radius=h // 2)
    x = r.x + pad
    if coin:
        coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2)
        x += coin_d + m(5)
    elif lock:
        bw, bh = m(9), m(7)
        rounded_body = pygame.Rect(x, cy - m(1), bw, bh)
        pygame.draw.rect(surf, fg, rounded_body, border_radius=m(2))
        pygame.draw.arc(surf, fg, (x + m(1), cy - m(7), bw - m(2), m(10)),
                        0.2, math.pi - 0.2, max(1, m(1.4)))
        x += m(13)
    surf.blit(timg, timg.get_rect(midleft=(x, cy)))
    return r


CHIP_COLORS = {
    "price": (GOLD_PALE, GOLD_DEEP, (*GOLD, 180)),
    "equip": (CREAM, (96, 74, 24), (*GOLD, 180)),
    "equipped": ((10, 32, 16), (88, 200, 116), (200, 255, 212)),
    "locked": ((158, 172, 196), (38, 44, 60), (96, 110, 138)),
}


def state_chip(surf, sid, cx, cy, equipped, secret, h):
    if equipped:
        fg, bg, rim = CHIP_COLORS["equipped"]
        return chip(surf, cx, cy, "EQUIPPED", fg, bg, rim, h=h)
    price = _cost(sid)
    if BALANCE >= price:
        fg, bg, rim = CHIP_COLORS["price"]
        return chip(surf, cx, cy, f"{price:,}", fg, bg, rim, h=h, coin=True)
    fg, bg, rim = CHIP_COLORS["locked"]
    return chip(surf, cx, cy, f"{price:,}", fg, bg, rim, h=h, lock=True)


# ── card ──────────────────────────────────────────────────────────────────────
def fit_name(surf, name, cx, cy, max_w):
    sz = 14
    f = font(sz)
    while f.size(name)[0] > max_w and sz > 9:
        sz -= 1
        f = font(sz)
    plain_text(surf, name, f, (cx, cy), NAME_COL, shadow_a=160)


def draw_card(surf, sid, rect, equipped):
    secret = _is_secret(sid)
    pal = MYSTERY if secret else RARITY[_rarity(sid)]
    rad = m(CARD_RAD)
    # DEPTH STACK: soft multi-layer drop shadow (top-left light => offset down)
    drop_shadow(surf, rect, rad, blur=m(7), alpha=150, dy=m(4))
    # body gradient + glossy top sheen + bevel rim + bottom-right contact AO
    surf.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
              rect.topleft)
    top_sheen(surf, rect, rad, m(20), peak=46)
    contact_shadow(surf, rect, rad, m(6), alpha=85)
    bevel_rim(surf, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 200),
              w=max(1, m(1.6)))

    cx, cy = rect.centerx, rect.y + m(CY_DISC)
    # constellation thread: corner gem -> cabochon top, with a node star
    gx, gy = rect.right - m(16), rect.y + m(16)
    mid = (rect.centerx + m(14), cy - m(R_DISC) - m(3))
    thread = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.line(thread, (*pal["glow"], 120),
                     (gx - rect.x, gy - rect.y), (mid[0] - rect.x, mid[1] - rect.y),
                     max(1, m(0.8)))
    nx, ny = (gx + mid[0]) // 2, (gy + mid[1]) // 2
    soft_glow(thread, nx - rect.x, ny - rect.y, m(2.5), pal["gem"], 110, layers=4)
    pygame.draw.circle(thread, (*pal["gem"], 230), (nx - rect.x, ny - rect.y),
                       max(1, m(1)))
    surf.blit(thread, rect.topleft, special_flags=pygame.BLEND_ADD)

    # BAND A — cabochon (glass dome over thumbnail). A whisper-soft tier aura
    # behind the dome (NOT a hard ring) so the macaw stays the hero.
    soft_glow(surf, cx, cy, m(R_DISC + 3), pal["glow"], 30, layers=8)
    cabochon(surf, cx, cy, m(R_DISC), CABO_LO, CABO_HI,
             ring=pal["gem"], ring_a=50)
    if secret:
        _draw_qmark(surf, cx, cy, m(R_DISC + 6), CREAM, NEAR_BLACK, thick=m(2))
        name = "???"
    else:
        t = thumb(sid, m(R_DISC) * 1.5)
        surf.blit(t, t.get_rect(center=(cx, cy)))
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
    state_chip(surf, sid, rect.centerx, rect.y + m(Y_CHIP), equipped, secret, m(22))

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
    cy = grid_bottom + m(16)
    plain_text(surf, "PAGE  1 / 3", font(12), (DW // 2, cy), GOLD_PALE, shadow_a=140)
    for gx, glyph in ((base_x + m(20), "<"),
                      (base_x + m(CARD_W) * 2 + m(GAP) - m(20), ">")):
        r = pygame.Rect(0, 0, m(34), m(24))
        r.center = (gx, cy)
        drop_shadow(surf, r, m(12), blur=m(3), alpha=90, dy=m(2))
        surf.blit(vgrad(r.w, r.h, m(12), (50, 38, 22), (26, 19, 11), 255), r.topleft)
        top_sheen(surf, r, m(12), m(7), peak=50)
        pygame.draw.rect(surf, (*GOLD, 200), r, width=max(1, m(1)), border_radius=m(12))
        plain_text(surf, glyph, font(15), (gx, cy - m(1)), GOLD_PALE, shadow_a=0)


def draw_back(surf):
    r = pygame.Rect(0, 0, m(168), m(36))
    r.center = (DW // 2, DH - m(24))
    drop_shadow(surf, r, m(18), blur=m(5), alpha=120, dy=m(3))
    surf.blit(vgrad(r.w, r.h, m(18), (32, 30, 66), (16, 16, 40), 250), r.topleft)
    top_sheen(surf, r, m(18), m(13), peak=42)
    contact_shadow(surf, r, m(18), m(4), alpha=80)
    bevel_rim(surf, r, m(18), lerp_color(GOLD, NEAR_BLACK, 0.45),
              (*GOLD, 200), w=max(1, m(1.2)))
    # left chevron
    cxx = r.x + m(26)
    pygame.draw.lines(surf, GOLD_PALE, False,
                      [(cxx + m(4), r.centery - m(6)),
                       (cxx - m(3), r.centery),
                       (cxx + m(4), r.centery + m(6))], max(1, m(2)))
    plain_text(surf, "BACK", font(17), (r.centerx + m(6), r.centery),
               GOLD_PALE, shadow_a=160)


# ── modal ─────────────────────────────────────────────────────────────────────
def draw_modal(surf, sid):
    scrim = pygame.Surface((DW, DH), pygame.SRCALPHA)
    scrim.fill((4, 4, 12, 190))
    surf.blit(scrim, (0, 0))
    secret = _is_secret(sid)
    tier = _rarity(sid)
    pal = MYSTERY if secret else RARITY[tier]
    pw, ph = m(264), m(322)
    panel = pygame.Rect((DW - pw) // 2, (DH - ph) // 2, pw, ph)
    rad = m(20)
    drop_shadow(surf, panel, rad, blur=m(10), alpha=185, dy=m(6))
    surf.blit(vgrad(pw, ph, rad, (28, 28, 66), (12, 12, 36), 255, gamma=1.15),
              panel.topleft)
    top_sheen(surf, panel, rad, m(26), peak=44)
    contact_shadow(surf, panel, rad, m(8), alpha=90)
    bevel_rim(surf, panel, rad, lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD, 230), w=max(1, m(1.8)))
    cx = panel.centerx
    plain_text(surf, "CONFIRM PURCHASE", font(13), (cx, panel.y + m(28)),
               GOLD_PALE, shadow_a=140, tracking=m(1))
    gold_rule(surf, panel.x + m(30), panel.right - m(30), panel.y + m(46), GOLD, peak=180)
    # STAGE — large cabochon dome
    disc_cy = panel.y + m(108)
    R = m(44)
    soft_glow(surf, cx, disc_cy, R + m(4), pal["glow"], 40, layers=8)
    cabochon(surf, cx, disc_cy, R, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=55)
    if secret:
        _draw_qmark(surf, cx, disc_cy, R + m(8), CREAM, NEAR_BLACK, thick=m(3))
        name = "???"
    else:
        t = thumb(sid, R * 1.5)
        surf.blit(t, t.get_rect(center=(cx, disc_cy)))
        name = _name(sid)
    cabochon_glass(surf, cx, disc_cy, R, tint=pal["gem"])
    facet_gem(surf, cx + m(42), disc_cy - m(40), m(9), pal["gem"], pal["deep"],
              mystery=secret)
    plain_text(surf, name, font(18), (cx, panel.y + m(182)), GOLD, shadow_a=150)
    rword = "MYSTERY" if secret else tier.upper()
    plain_text(surf, rword, font(11), (cx, panel.y + m(202)), pal["gem"],
               shadow_a=120, tracking=m(1))
    price = _cost(sid)
    fg, bg, rim = CHIP_COLORS["price"]
    chip(surf, cx, panel.y + m(230), f"{price:,}", fg, bg, rim, h=m(30), coin=True)
    # buttons
    bw, bh, gut = m(106), m(40), m(16)
    by = panel.bottom - m(32)
    nx = cx - (bw * 2 + gut) // 2
    cancel = pygame.Rect(nx, by - bh // 2, bw, bh)
    buy = pygame.Rect(nx + bw + gut, by - bh // 2, bw, bh)
    drop_shadow(surf, cancel, bh // 2, blur=m(3), alpha=90, dy=m(2))
    surf.blit(vgrad(bw, bh, bh // 2, (74, 66, 86), (44, 38, 58)), cancel.topleft)
    top_sheen(surf, cancel, bh // 2, bh // 2, peak=40)
    pygame.draw.rect(surf, (132, 122, 144), cancel, width=max(1, m(1)),
                     border_radius=bh // 2)
    plain_text(surf, "CANCEL", font(14), cancel.center, CREAM, shadow_a=120)
    bglow = pygame.Surface((bw + m(12), bh + m(12)), pygame.SRCALPHA)
    for k in range(5, 0, -1):
        pygame.draw.rect(bglow, (*GOLD, int(24 * k / 5)),
                         (m(6) - k * m(1), m(6) - k * m(1),
                          bw + 2 * k * m(1), bh + 2 * k * m(1)),
                         border_radius=bh // 2 + k * m(1))
    surf.blit(bglow, (buy.x - m(6), buy.y - m(6)), special_flags=pygame.BLEND_ADD)
    drop_shadow(surf, buy, bh // 2, blur=m(3), alpha=90, dy=m(2))
    surf.blit(vgrad(bw, bh, bh // 2, lerp_color(GOLD, WHITE, 0.22), GOLD_DEEP),
              buy.topleft)
    top_sheen(surf, buy, bh // 2, bh // 2, peak=80)
    pygame.draw.rect(surf, GOLD_PALE, buy, width=max(1, m(1)), border_radius=bh // 2)
    plain_text(surf, "BUY", font(15), buy.center, (40, 24, 8), shadow_a=0)


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
    """A 2-3 card detail strip at SS for close inspection of dome/gem/chip."""
    ids = DETAIL_IDS
    pad = m(20)
    g = m(16)
    cols = len(ids)
    sw = m(CARD_W) * cols + g * (cols - 1) + pad * 2
    sh = m(CARD_H) + pad * 2 + m(30)
    strip = pygame.Surface((sw, sh))
    strip.blit(multistop_v(sw, sh, BG_STOPS), (0, 0))
    soft_glow(strip, sw // 2, sh // 2, m(120), NEBULA_GLOW, 50, layers=8)
    plain_text(strip, "GLASS DOME  /  GEM FACETS  /  CHIP  /  CONSTELLATION THREAD",
               font(11), (sw // 2, m(15)), GOLD_PALE, shadow_a=120)
    for i, sid in enumerate(ids):
        x = pad + i * (m(CARD_W) + g)
        y = m(30) + pad
        draw_card(strip, sid, pygame.Rect(x, y, m(CARD_W), m(CARD_H)),
                  sid == EQUIPPED_ID)
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
