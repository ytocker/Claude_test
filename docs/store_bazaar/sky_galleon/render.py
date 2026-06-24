"""
SKY-GALLEON MARKET — store "bazaar landing" concept (FLOATING SKY-BAZAAR line).

A flying game's shop deserves a flying merchant: a grand wooden trading galleon
cruising a golden-hour -> indigo twilight sky, held aloft by a great gold-rimmed
canvas envelope above and trailing cloud-wisps below. The 7 category stalls are
striped market booths arrayed along the deck + rigging; tapping one dissolves
into the constellation jewel store at the indigo apex (where the stars emerge).

Same SS=4 supersample pipeline as the constellation store: author everything at
logical 360x640, render onto a 360*SS x 640*SS device surface (every plank,
rope, awning fold, glyph oversized), then ONE smoothscale down so geometry
resolves razor-crisp with no per-shape AA tricks. All metrics flow through m().

Booth previews are the REAL in-game category thumbnails (store_catalog +
parrot.get_skin_icon / get_skin_frame), set inside the same glass cabochon dome
the jewel store uses — so the bazaar promises exactly the goods it sells.

Both build targets safe: pure pygame, no numpy, no desktop/browser-only API.
"""
import os
import sys
import math
import random

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
from game import parrot
from game import store_catalog

# Reuse the constellation store's locked primitive kit + palette anchors so the
# bazaar shares the exact glass dome, gold ramp, type finish + coin the player
# already trusts — the landing and the jewel store are ONE product.
from docs.store_redesign.constellation_hi.render_hi import (
    SS, DW, DH, m, mf, font, _glyph_base, _stamp_bold,
    vgrad, vgrad_stops, multistop_v, lerp_stops,
    gold_a_fill, soft_glow, drop_shadow, contact_shadow,
    gradient_text, plain_text, coin_glyph, bevel_rim, top_sheen,
    gold_rule, title_wordmark, gloss_sweep,
    cabochon, cabochon_glass,
    GOLD, GOLD_PALE, GOLD_DEEP, GOLD_A_TOP, GOLD_A_BOT,
    GOLD_A_STOPS, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT,
    GOLD_A_NUM, GOLD_A_COIN_RIM, CARD_RING_BRIGHT,
    CABO_LO, CABO_HI,
)


# =============================================================================
# Concept palette — golden-hour warm low -> indigo + gold-nebula apex
# =============================================================================
# The vertical sky is the whole mood: a low warm sun band burning amber at the
# horizon, cooling up through rose + violet into the deep indigo apex where the
# jewel store's stars live. The galleon floats across the warm middle so its lit
# wood reads against cool sky above + warm haze below.
SKY_STOPS = [
    (0.00, (14, 12, 44)),     # indigo apex (stars emerge here)
    (0.16, (26, 20, 66)),     # deep violet
    (0.34, (58, 38, 92)),     # twilight violet
    (0.52, (124, 70, 110)),   # rose-magenta band
    (0.70, (206, 116, 92)),   # warm coral
    (0.84, (244, 168, 86)),   # golden-hour amber
    (1.00, (255, 214, 120)),  # low sun haze
]
SUN_CORE = (255, 240, 196)
SUN_GLOW = (255, 188, 110)
NEBULA = (118, 92, 188)        # gold-flecked violet bloom at the apex

# Macaw-red + cream — the Skybit booth-awning livery (the parrot's own reds).
AWN_RED_HI = (228, 78, 66)
AWN_RED_LO = (158, 38, 38)
AWN_CREAM = (248, 240, 220)
AWN_CREAM_LO = (220, 206, 178)

# Lit wood for the hull / deck / masts (one light, top-left).
WOOD_HI = (158, 104, 56)
WOOD_MID = (118, 72, 38)
WOOD_LO = (74, 42, 22)
WOOD_DK = (44, 24, 14)
DECK_HI = (176, 130, 78)
DECK_LO = (104, 70, 40)

# Canvas envelope (the balloon holding the ship up) — warm cream sail panels
# stitched in gold, catching the low sun on its left flank.
ENV_HI = (250, 234, 196)
ENV_MID = (226, 188, 138)
ENV_LO = (170, 120, 80)
ENV_SHADE = (120, 78, 56)


# =============================================================================
# 7 stalls -> 7 booths. Group -> label + the REAL preview thumbnail id.
# =============================================================================
STALLS = [
    ("costume", "COSTUMES"),
    ("parrot",  "PARROTS"),
    ("animal",  "ANIMALS"),
    ("shoes",   "SHOES"),
    ("hats",    "HATS"),
    ("shades",  "SHADES"),
    ("parcels", "PARCELS"),
]
BALANCE = 14250

# Vertical layout anchors (logical px). The ship's deck spans the mid-screen;
# the hull crown is HULL_TOP so the booths rest ON the deck, with hull planks +
# the keel reading clearly below the lowest booth row.
HULL_TOP = 470
MYSTERY_GLOW = (244, 120, 90)


def _preview_id(group):
    """First catalog id of a group = the booth's preview good. SHADES head is
    'NO SHADES' (no icon, bare eyes), so step to the first id that actually owns
    a shades icon — the booth must never show a bare base parrot."""
    ids = store_catalog.ids_of_group(group)
    sid = ids[0]
    if group == "shades":
        for cand in ids:
            if parrot.get_skin_icon(cand) is not None:
                return cand
    return sid


# ── preview thumbnail (icon-first; fills the dome; flat goods angled) ─────────
_thumb_cache = {}

# Genuinely-flat product shots (a thin bar at 0°/90°) get a slight in-plane
# rotation so they occupy 2D area in the dome instead of reading as a 1px smear.
# Keyed by group so it tracks whichever id the booth surfaces.
_ANGLE_GROUPS = {"shoes": -24, "shades": -20}


def _preview_surface(sid, box_px, group=None):
    """The category's REAL product shot, sized so its LONGER axis fills ~86% of
    the dome (was a timid big-letterbox contain that left SHOES a thin smear and
    SHADES a tiny rectangle). Genuinely-flat goods are angled ~20-25 deg so they
    claim area. Icon first; else the in-game frame. Nothing is cropped."""
    key = (sid, box_px, group)
    out = _thumb_cache.get(key)
    if out is not None:
        return out
    src = parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    ang = _ANGLE_GROUPS.get(group, 0)
    if ang:
        src = pygame.transform.rotate(src, ang)
        bb = src.get_bounding_rect()
        if bb.width > 0 and bb.height > 0:
            src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    # fill the longer axis to box_px (caller passes ~0.86 of the dome diameter);
    # short-axis margin is fine, but the good now reads at a glance.
    s = box_px / max(sw, sh)
    scaled = pygame.transform.smoothscale(
        src, (max(1, int(sw * s)), max(1, int(sh * s))))
    # flat additive lift so the skin separates from the dark dome (same trick as
    # the jewel store) without inventing detail.
    lift = scaled.copy()
    lift.fill((34, 34, 34, 0), special_flags=pygame.BLEND_RGB_ADD)
    _thumb_cache[key] = lift
    return lift


def _rim_light(img, color=(255, 248, 220), alpha=170):
    w, h = img.get_size()
    off = max(1, m(0.6))
    rim = pygame.Surface((w, h), pygame.SRCALPHA)
    sil = img.copy()
    sil.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rim.blit(sil, (-off, -off))
    cut = img.copy()
    cut.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rim.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    rim.set_alpha(alpha)
    return rim


def blit_preview(surf, sid, cx, cy, box_px, group=None):
    t = _preview_surface(sid, box_px, group)
    r = t.get_rect(center=(cx, cy))
    surf.blit(_rim_light(t), r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(t, r.topleft)


def _dome_floor(surf, cx, cy, R):
    """The cabochon well re-floored to the jewel store's near-black NAVY (CABO_LO/
    CABO_HI) so the sunset stops bleeding through behind a preview, PLUS a soft
    radial value-lift at the centre so dark previews (shades, parcels) don't
    vanish into the well. Drawn BEFORE the preview; the glass dome lands after."""
    cabochon(surf, cx, cy, R, CABO_LO, CABO_HI)
    lift = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    soft_glow(lift, R, R, int(R * 0.74), (70, 78, 120), 60, layers=10)
    lmask = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    pygame.draw.circle(lmask, (255, 255, 255, 255), (R, R), R - m(2))
    lift.blit(lmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(lift, (cx - R, cy - R), special_flags=pygame.BLEND_ADD)


# =============================================================================
# Atmosphere — sky gradient, low sun, apex nebula + emerging stars, cloud-isles
# =============================================================================
_bg_cache = None


def _stars(surf, seed, y_top, y_bot, count, rmin, rmax, amin, amax):
    """Stars only emerge in the upper indigo apex; density + brightness fall off
    toward the warm horizon where the sky is too bright to hold them."""
    rnd = random.Random(seed)
    span = y_bot - y_top
    for _ in range(count):
        f = rnd.random() ** 1.6                     # bias high (toward apex)
        y = int(y_top + f * span)
        x = rnd.randint(0, DW)
        fade = 1.0 - (y - y_top) / max(1, span)     # brighter higher up
        a = int(rnd.randint(amin, amax) * (0.25 + 0.75 * fade))
        if a <= 4:
            continue
        r = m(rnd.uniform(rmin, rmax))
        tint = rnd.choice([(255, 252, 240), (224, 220, 255), (255, 234, 196)])
        pygame.draw.circle(surf, (*tint, a), (x, y), max(1, int(r)))


def _cloud_isle(surf, cx, cy, w, h, warm, alpha):
    """A distant flat-bottomed cloud-isle (overlapping puffs) giving the sky
    depth + parallax. Warm-lit crown, cool shaded underside."""
    cloud = pygame.Surface((w + m(20), h + m(20)), pygame.SRCALPHA)
    ox, oy = m(10), m(10)
    rnd = random.Random(int(cx * 7 + cy))
    n = max(4, w // m(34))
    lobes = []
    for i in range(n):
        lx = ox + int(w * (i + 0.5) / n)
        rr = int(h * rnd.uniform(0.42, 0.62))
        ly = oy + h - rr - int(rnd.uniform(0, h * 0.12))
        lobes.append((lx, ly, rr))
    # cool shaded base
    base = lerp_color(warm, (70, 60, 110), 0.5)
    for lx, ly, rr in lobes:
        pygame.draw.circle(cloud, (*base, alpha), (lx, ly + m(3)), rr)
    pygame.draw.ellipse(cloud, (*base, alpha),
                        (ox, oy + h - m(8), w, m(16)))
    # warm-lit crown (top-left of each puff)
    for lx, ly, rr in lobes:
        hi = lerp_color(warm, WHITE, 0.4)
        pygame.draw.circle(cloud, (*hi, min(255, alpha + 30)),
                           (lx - int(rr * 0.22), ly - int(rr * 0.22)),
                           int(rr * 0.74))
    surf.blit(cloud, (cx - (w + m(20)) // 2, cy - (h + m(20)) // 2))


def _build_bg():
    global _bg_cache
    sky = pygame.Surface((DW, DH))
    sky.blit(multistop_v(DW, DH, SKY_STOPS), (0, 0))
    overlay = pygame.Surface((DW, DH), pygame.SRCALPHA)

    # apex nebula bloom — a gold-flecked violet glow under the star field
    soft_glow(overlay, int(DW * 0.5), int(DH * 0.10), m(220), NEBULA, 60, layers=12)
    soft_glow(overlay, int(DW * 0.30), int(DH * 0.06), m(120), (150, 120, 210), 40,
              layers=8)

    # emerging stars (apex only) + a few gold sparkles up high
    _stars(overlay, 91, 0, int(DH * 0.44), 150, 0.4, 1.0, 40, 150)
    _stars(overlay, 92, 0, int(DH * 0.30), 40, 0.9, 1.7, 110, 210)
    rnd = random.Random(404)
    for _ in range(10):
        x = rnd.randint(m(20), DW - m(20))
        y = rnd.randint(m(16), int(DH * 0.26))
        L = m(rnd.uniform(3, 5.5))
        a = rnd.randint(120, 210)
        col = (255, 244, 206, a)
        pygame.draw.line(overlay, col, (x - L, y), (x + L, y), max(1, m(0.7)))
        pygame.draw.line(overlay, col, (x, y - L), (x, y + L), max(1, m(0.7)))
        soft_glow(overlay, x, y, m(3), (255, 240, 200), 80, layers=4)

    # the low sun — a warm core + wide halo down near the golden-hour horizon
    sx, sy = int(DW * 0.74), int(DH * 0.88)
    soft_glow(overlay, sx, sy, m(220), SUN_GLOW, 70, layers=14)
    soft_glow(overlay, sx, sy, m(96), SUN_CORE, 150, layers=10)
    pygame.draw.circle(overlay, (*SUN_CORE, 210), (sx, sy), m(40))
    # light shafts fanning up off the sun
    for ang in range(-78, 0, 13):
        a = math.radians(ang)
        L = m(rnd.uniform(150, 240))
        ex, ey = sx + math.cos(a) * L, sy + math.sin(a) * L
        shaft = pygame.Surface((DW, DH), pygame.SRCALPHA)
        pygame.draw.line(shaft, (255, 220, 150, 26), (sx, sy), (int(ex), int(ey)),
                         m(rnd.uniform(3, 7)))
        overlay.blit(shaft, (0, 0))

    # distant cloud-isles for depth (small + hazy high, larger + warmer low)
    _cloud_isle(overlay, int(DW * 0.18), int(DH * 0.30), m(96), m(34),
                (150, 120, 180), 120)
    _cloud_isle(overlay, int(DW * 0.86), int(DH * 0.40), m(120), m(40),
                (210, 150, 150), 140)
    _cloud_isle(overlay, int(DW * 0.40), int(DH * 0.52), m(150), m(46),
                (236, 168, 128), 150)
    _cloud_isle(overlay, int(DW * 0.10), int(DH * 0.64), m(130), m(42),
                (244, 182, 120), 150)

    sky.blit(overlay, (0, 0))

    # subtle top + bottom vignette so the header chrome + ground read on a
    # controlled deep ground without killing the warm horizon glow.
    vig = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for y in range(DH):
        f = y / DH
        a = 0
        if f < 0.16:
            a = int(120 * (1 - f / 0.16) ** 1.4)
        pygame.draw.line(vig, (8, 8, 28, a), (0, y), (DW, y))
    sky.blit(vig, (0, 0))
    _bg_cache = sky


def draw_bg(surf):
    surf.blit(_bg_cache, (0, 0))


# =============================================================================
# The galleon — envelope (balloon), hull, masts, rigging, deck. All from
# gradient + polygon + line + glow. One light top-left; gold rim-lights; real
# AO/contact shadows. The deck is the stage the booths sit on.
# =============================================================================
def _poly_grad(surf, pts, top_col, bot_col, gamma=1.0):
    """Fill an arbitrary polygon with a vertical gradient by clipping a gradient
    block to a polygon mask. Lets the hull/envelope read as lit volumes, not
    flat shapes."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = int(min(xs)), int(min(ys))
    w = int(max(xs)) - x0 + 2
    h = int(max(ys)) - y0 + 2
    if w <= 0 or h <= 0:
        return
    block = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        t = (yy / max(1, h - 1)) ** gamma
        pygame.draw.line(block, (*lerp_color(top_col, bot_col, t), 255),
                         (0, yy), (w, yy))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(p[0] - x0, p[1] - y0) for p in pts])
    block.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(block, (x0, y0))


def draw_envelope(surf):
    """The great canvas balloon-envelope holding the ship aloft — rebuilt as a
    GORED dirigible (narrowed ~11% so it reads as an airship, not a wide tan
    blob): real cross-section panels with darker valley shading at each gore
    seam and a warm crown highlight down each panel so the curvature reads; a
    broad curve-following sheen (no white specular sticker) + a warm sunset
    bounce on the underside; two macaw-red accent bands + a gold cartouche so it
    looks intentional. Gold-bound rim, crown finial, soft cast shadow."""
    cx = m(180)
    cy = m(148)
    rw = m(124)                                     # half width (~11% narrower)
    rh = m(82)                                       # half height
    # soft cast shadow the envelope throws on the sky/deck beneath it
    sh = pygame.Surface((DW, DH), pygame.SRCALPHA)
    soft_glow(sh, cx + m(8), cy + rh + m(40), m(110), (10, 6, 24), 70, layers=10)
    surf.blit(sh, (0, 0))

    pad = m(20)
    body = pygame.Surface((rw * 2 + pad * 2, rh * 2 + pad * 2), pygame.SRCALPHA)
    bx, by = rw + pad, rh + pad
    hmask = pygame.Surface(body.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(hmask, (255, 255, 255, 255),
                        (bx - rw, by - rh, rw * 2, rh * 2))

    # base body: a smooth lit ellipse, left-lit (warm) -> right (shade)
    for i in range(rh * 2):
        t = i / (rh * 2)
        prof = math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2))     # ellipse half-width
        ww = rw * prof
        yy = by - rh + i
        col = lerp_color(ENV_MID, ENV_LO, t * 0.65)
        pygame.draw.line(body, (*col, 255), (bx - ww, yy), (bx + ww, yy))

    # GORED PANELS: divide the width into vertical gores. For each gore, paint a
    # warm crown highlight down its centre and a darker valley at its two seams,
    # all scaled by the ellipse half-width per row so the shading hugs the curve.
    GORES = 7
    for yy in range(int(by - rh), int(by + rh)):
        t = (yy - (by - rh)) / (rh * 2)
        half = rw * math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2))
        if half < 1:
            continue
        for g in range(GORES):
            gc = -1.0 + (g + 0.5) * 2.0 / GORES          # gore centre in [-1,1]
            # foreshorten: gores near the silhouette edge compress
            for sub in range(-3, 4):
                fx = gc + sub * (2.0 / GORES) / 7.0
                if abs(fx) >= 1:
                    continue
                x = bx + fx * half
                # distance from this gore's centre, normalised to gore half-width
                d = abs(sub) / 3.5
                # warm crown at centre, dark valley at the seam edges
                shade = lerp_color((255, 248, 222), (150, 96, 64), d ** 1.3)
                a = int(120 * (1 - d) + 60 * d)
                body.set_at((int(x), yy), (*shade, a))
        # the crisp gold seam lines between gores
        for g in range(1, GORES):
            fx = -1.0 + g * 2.0 / GORES
            x = bx + fx * half
            body.set_at((int(x), yy), (*lerp_color(GOLD_DEEP, GOLD, 0.45), 200))

    # broad curve-following SHEEN (top-left), a soft band hugging the upper arc —
    # replaces the round white blob; never an opaque sticker.
    sheen = pygame.Surface(body.get_size(), pygame.SRCALPHA)
    for k in range(m(7)):
        a = int(70 * (1 - k / m(7)))
        pygame.draw.arc(sheen, (255, 252, 236, a),
                        (bx - rw + m(8) + k, by - rh + m(6) + k,
                         rw * 2 - m(16) - 2 * k, rh * 2 - m(12) - 2 * k),
                        math.radians(118), math.radians(202), max(1, m(2)))
    body.blit(sheen, (0, 0))
    # warm SUNSET bounce on the underside (a low amber band lit from below-right)
    bounce = pygame.Surface(body.get_size(), pygame.SRCALPHA)
    soft_glow(bounce, int(bx + rw * 0.18), int(by + rh * 0.72), int(rw * 0.7),
              (255, 176, 110), 80, layers=12)
    bounce.blit(hmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    body.blit(bounce, (0, 0), special_flags=pygame.BLEND_ADD)

    # clip everything to the ellipse, then commit
    body.blit(hmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (cx - bx, cy - by))

    # two macaw-red accent bands hugging the body curvature (top + lower thirds)
    for fy in (-0.42, 0.46):
        ry = cy + rh * fy
        # band follows the ellipse: draw as a thin arc pair top + bottom edge
        bh2 = int(rh * 0.12)
        band = pygame.Surface((rw * 2 + m(8), rh * 2 + m(8)), pygame.SRCALPHA)
        bc = rw + m(4), rh + m(4)
        for yy in range(int(bc[1] + rh * fy - bh2), int(bc[1] + rh * fy + bh2)):
            tt = (yy - (bc[1] - rh)) / (rh * 2)
            if tt <= 0 or tt >= 1:
                continue
            half = rw * math.sqrt(max(0.0, 1 - (2 * tt - 1) ** 2))
            col = AWN_RED_HI if abs(yy - (bc[1] + rh * fy)) < bh2 * 0.5 else AWN_RED_LO
            pygame.draw.line(band, (*col, 200), (bc[0] - half, yy),
                             (bc[0] + half, yy))
        bmask = pygame.Surface(band.get_size(), pygame.SRCALPHA)
        pygame.draw.ellipse(bmask, (255, 255, 255, 255),
                            (bc[0] - rw, bc[1] - rh, rw * 2, rh * 2))
        band.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(band, (cx - bc[0], cy - bc[1]))

    # gold rim: dark keyline under a bright gold lip, brightest top-left arc
    pygame.draw.ellipse(surf, (40, 22, 10),
                        (cx - rw, cy - rh, rw * 2, rh * 2), max(1, m(3)))
    pygame.draw.ellipse(surf, (*GOLD, 220),
                        (cx - rw + m(1), cy - rh + m(1), rw * 2 - m(2), rh * 2 - m(2)),
                        max(1, m(2)))
    rim = pygame.Surface((rw * 2 + m(8), rh * 2 + m(8)), pygame.SRCALPHA)
    pygame.draw.arc(rim, (*GOLD_A_RIM_BRIGHT, 235),
                    (m(2), m(2), rw * 2, rh * 2),
                    math.radians(110), math.radians(245), max(1, m(2.4)))
    surf.blit(rim, (cx - rw - m(2), cy - rh - m(2)), special_flags=pygame.BLEND_ADD)

    # a small gold cartouche emblem on the flank (a coin-medallion crest) so the
    # canvas reads as a branded merchant balloon, not blank cloth.
    em_cx, em_cy = cx, cy + m(2)
    pygame.draw.circle(surf, (40, 24, 10), (em_cx, em_cy), m(15))
    pygame.draw.circle(surf, GOLD, (em_cx, em_cy), m(13))
    pygame.draw.circle(surf, lerp_color(GOLD, NEAR_BLACK, 0.35), (em_cx, em_cy),
                       m(13), max(1, m(1.4)))
    coin_glyph(surf, em_cx, em_cy, m(9))

    # gold nose-band + crown finial cap at the very top
    pygame.draw.circle(surf, (40, 24, 10), (cx, cy - rh), m(6))
    pygame.draw.circle(surf, GOLD, (cx, cy - rh), m(5))
    soft_glow(surf, cx, cy - rh - m(1), m(4), (255, 246, 210), 130, layers=6)

    # suspension ropes from the envelope's lower rim to the hull's gunwale
    rope = lerp_color(WOOD_LO, NEAR_BLACK, 0.2)
    anchors_top = [(cx - rw * 0.70, cy + rh * 0.78),
                   (cx - rw * 0.26, cy + rh * 0.98),
                   (cx + rw * 0.26, cy + rh * 0.98),
                   (cx + rw * 0.70, cy + rh * 0.78)]
    hull_top = m(HULL_TOP)
    anchors_bot = [(m(58), hull_top), (m(132), hull_top - m(4)),
                   (m(228), hull_top - m(4)), (m(302), hull_top)]
    for (ax, ay), (bx2, by2) in zip(anchors_top, anchors_bot):
        pygame.draw.line(surf, rope, (int(ax), int(ay)), (int(bx2), int(by2)),
                         max(1, m(1.6)))
        pygame.draw.line(surf, lerp_color(WOOD_MID, GOLD, 0.2),
                         (int(ax), int(ay)), (int(bx2), int(by2)), max(1, m(0.7)))


def draw_hull(surf):
    """The wooden trading hull: a lit curved hull body, a stern + bow rise, a
    gold gunwale rail, plank lines, portholes, and a deep contact shadow + cloud
    wisps trailing below so the ship reads as floating, not grounded."""
    # hull silhouette (a long shallow boat, bow right, stern left, both raised)
    top_y = m(HULL_TOP)
    deck_y = m(HULL_TOP + 14)
    hx0, hx1 = m(30), m(330)
    keel_y = m(HULL_TOP + 100)
    pts = [
        (hx0, top_y - m(10)),                # stern rail top
        (hx0 + m(8), deck_y),
        (hx0 + m(44), keel_y - m(18)),
        (m(180), keel_y),                    # keel low point
        (hx1 - m(52), keel_y - m(22)),
        (hx1 - m(4), deck_y),
        (hx1, top_y - m(16)),                # bow rail top (raised higher)
        (hx1 - m(22), top_y - m(2)),
        (hx0 + m(22), top_y - m(2)),
    ]
    # cast contact shadow under the hull (floating -> soft, offset down)
    sh = pygame.Surface((DW, DH), pygame.SRCALPHA)
    soft_glow(sh, m(176), keel_y + m(18), m(150), (8, 6, 22), 90, layers=12)
    surf.blit(sh, (0, 0))

    _poly_grad(surf, pts, WOOD_MID, WOOD_DK, gamma=1.2)
    # left-lit top-left highlight band along the hull crown
    hi = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pygame.draw.polygon(hi, (*WOOD_HI, 150),
                        [(hx0 + m(20), top_y - m(2)), (hx1 - m(20), top_y - m(2)),
                         (hx1 - m(20), top_y + m(10)), (hx0 + m(20), top_y + m(12))])
    surf.blit(hi, (0, 0))
    # horizontal plank seams curving with the hull
    for k in range(1, 6):
        fy = k / 6
        y = int(deck_y + (keel_y - deck_y) * fy)
        seam = pygame.Surface((DW, DH), pygame.SRCALPHA)
        x_in = hx0 + m(14) + int(m(30) * fy)
        x_out = hx1 - m(10) - int(m(34) * fy)
        dip = int(m(10) * math.sin(math.pi * fy))
        # deepened one value step: a darker seam valley under a brighter plank lip
        pygame.draw.line(seam, (24, 13, 7, 210), (x_in, y),
                         (x_out, y + dip), max(1, m(1.4)))
        pygame.draw.line(seam, (*WOOD_HI, 90), (x_in, y - m(1.4)),
                         (x_out, y - m(1.4) + dip), max(1, m(0.8)))
        surf.blit(seam, (0, 0))
    # round brass portholes with gold rims along the hull
    for fx in (0.28, 0.44, 0.60, 0.76):
        px = int(hx0 + (hx1 - hx0) * fx)
        py = int(deck_y + m(34))
        pygame.draw.circle(surf, (18, 12, 8), (px, py), m(8))
        pygame.draw.circle(surf, lerp_color(GOLD, (120, 170, 200), 0.4),
                           (px, py), m(7))
        pygame.draw.circle(surf, (40, 60, 80), (px, py), m(5))
        soft_glow(surf, px - m(2), py - m(2), m(3), (180, 220, 255), 120, layers=5)
        pygame.draw.circle(surf, (20, 12, 6), (px, py), m(8), max(1, m(1.4)))
    # gold gunwale rail capping the hull (dark keyline under bright lip)
    rail = [(hx0 + m(14), top_y - m(2)), (hx1 - m(14), top_y - m(2))]
    pygame.draw.line(surf, (40, 24, 10), (rail[0][0], top_y + m(2)),
                     (rail[1][0], top_y + m(2)), max(1, m(5)))
    grad_rail = vgrad_stops(rail[1][0] - rail[0][0], m(7), m(3), GOLD_A_STOPS, 255)
    surf.blit(grad_rail, (rail[0][0], top_y - m(4)))
    pygame.draw.line(surf, (*GOLD_A_RIM_BRIGHT, 200),
                     (rail[0][0], top_y - m(3)), (rail[1][0], top_y - m(3)),
                     max(1, m(1)))

    # cloud wisps trailing below the keel so the ship floats
    for fx, fy, ww in ((0.24, 0.04, 96), (0.52, 0.10, 130), (0.78, 0.05, 90)):
        _cloud_isle(surf, int(hx0 + (hx1 - hx0) * fx),
                    keel_y + m(26 + fy * 80), m(ww), m(28),
                    (236, 176, 130), 130)


def draw_masts_and_decor(surf, mast_xs, top_y):
    """Three masts rising from the deck (the awnings hang from these), a bow
    bowsprit + pennant, and a stern lantern — the dressing that makes the deck
    read as a working trading vessel before the booths land."""
    deck_y = m(HULL_TOP + 14)
    cap_y = m(206)
    for mx in mast_xs:
        # mast pole: lit wood column with a gold cap, rising from the deck up to
        # just under the balloon so the rigging band reads as the upper stalls' rail
        pole = pygame.Rect(mx - m(4), cap_y, m(8), deck_y - cap_y)
        surf.blit(vgrad(pole.w, pole.h, m(3),
                        WOOD_HI, WOOD_LO, 255, gamma=1.1), pole.topleft)
        pygame.draw.rect(surf, (30, 18, 10), pole, width=max(1, m(1)),
                         border_radius=m(3))
        pygame.draw.line(surf, (*WOOD_HI, 180), (mx - m(3), cap_y + m(2)),
                         (mx - m(3), deck_y - m(8)), max(1, m(1)))
        # gold mast-cap ball
        pygame.draw.circle(surf, (40, 24, 10), (mx, cap_y - m(2)), m(6))
        pygame.draw.circle(surf, GOLD, (mx, cap_y - m(2)), m(5))
        soft_glow(surf, mx - m(1), cap_y - m(4), m(3), (255, 244, 200), 120, layers=5)

    # rigging ropes between mast caps + down to bow/stern (the bazaar's lines)
    rope = lerp_color(WOOD_LO, NEAR_BLACK, 0.15)
    caps = [(mx, cap_y - m(2)) for mx in mast_xs]
    for (ax, ay), (bx, by) in zip(caps, caps[1:]):
        pygame.draw.line(surf, rope, (ax, ay), (bx, by), max(1, m(1.2)))
    pygame.draw.line(surf, rope, (m(30), top_y), caps[0], max(1, m(1.2)))
    pygame.draw.line(surf, rope, caps[-1], (m(330), top_y), max(1, m(1.2)))
    # a string of tiny pennant flags along the foremost rigging line
    pen_a, pen_b = (m(30), top_y), caps[0]
    for k in range(1, 7):
        t = k / 7
        px = int(pen_a[0] + (pen_b[0] - pen_a[0]) * t)
        py = int(pen_a[1] + (pen_b[1] - pen_a[1]) * t)
        col = AWN_RED_HI if k % 2 else AWN_CREAM
        pygame.draw.polygon(surf, col,
                            [(px, py), (px + m(7), py), (px + m(3), py + m(8))])
        pygame.draw.polygon(surf, (30, 18, 10),
                            [(px, py), (px + m(7), py), (px + m(3), py + m(8))],
                            max(1, m(0.6)))

    # bow bowsprit + flying pennant (far right)
    bsp = (m(312), top_y - m(10))
    tip = (m(348), top_y - m(34))
    pygame.draw.line(surf, WOOD_MID, bsp, tip, max(1, m(3)))
    pygame.draw.line(surf, (*WOOD_HI, 160), bsp, tip, max(1, m(1)))
    pygame.draw.polygon(surf, AWN_RED_HI,
                        [tip, (tip[0] - m(2), tip[1] - m(16)),
                         (tip[0] + m(20), tip[1] - m(6))])
    pygame.draw.polygon(surf, (90, 24, 24),
                        [tip, (tip[0] - m(2), tip[1] - m(16)),
                         (tip[0] + m(20), tip[1] - m(6))], max(1, m(0.7)))


# =============================================================================
# A booth = striped macaw-red/cream awning hung from a mast + the glass
# cabochon dome showing the category preview + a bold gold-keyline label.
# =============================================================================
def draw_awning(surf, cx, top_y, half_w, drop, hero=False):
    """A scalloped striped awning: alternating macaw-red + cream panels, a lit
    crown, a scalloped valance, a gold fringe rod, and a soft drop shadow under
    it onto the booth. PARCELS' hero awning is a touch taller + richer."""
    panels = 6
    # the awning is a trapezoid: a short ridge bar up top flaring to a wide
    # scalloped hem, like a real market stall canopy.
    ridge_w = int(half_w * 0.42)
    bw = half_w * 2
    # drop shadow behind the awning
    sh = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (6, 4, 16, 110),
                        [(cx - ridge_w, top_y + m(3)),
                         (cx + ridge_w, top_y + m(3)),
                         (cx + half_w + m(3), top_y + drop + m(6)),
                         (cx - half_w - m(3), top_y + drop + m(6))])
    surf.blit(sh, (0, 0))
    # each stripe panel is its own quad from a ridge slot to a hem slot
    for i in range(panels):
        rx0 = cx - ridge_w + 2 * ridge_w * i / panels
        rx1 = cx - ridge_w + 2 * ridge_w * (i + 1) / panels
        hx0 = cx - half_w + bw * i / panels
        hx1 = cx - half_w + bw * (i + 1) / panels
        red = (i % 2 == 0)
        top_c = AWN_RED_HI if red else AWN_CREAM
        bot_c = AWN_RED_LO if red else AWN_CREAM_LO
        _poly_grad(surf, [(rx0, top_y), (rx1, top_y),
                          (hx1, top_y + drop), (hx0, top_y + drop)],
                   top_c, bot_c, gamma=1.1)
    # scalloped hem: a row of little arcs hanging off the bottom edge
    for i in range(panels):
        hx0 = cx - half_w + bw * i / panels
        hx1 = cx - half_w + bw * (i + 1) / panels
        red = (i % 2 == 0)
        col = AWN_RED_LO if red else AWN_CREAM_LO
        mid = (hx0 + hx1) / 2
        dipd = m(8)
        pygame.draw.polygon(surf, col,
                            [(hx0, top_y + drop), (hx1, top_y + drop),
                             (mid, top_y + drop + dipd)])
    # lit crown highlight along the ridge (top-left light)
    pygame.draw.line(surf, (255, 240, 220, 200),
                     (cx - ridge_w, top_y + m(1)), (cx + ridge_w, top_y + m(1)),
                     max(1, m(1.4)))
    # the gold fringe rod the awning hangs from (dark keyline under bright lip)
    pygame.draw.line(surf, (40, 24, 10),
                     (cx - ridge_w - m(4), top_y), (cx + ridge_w + m(4), top_y),
                     max(1, m(4)))
    pygame.draw.line(surf, GOLD,
                     (cx - ridge_w - m(4), top_y - m(1)),
                     (cx + ridge_w + m(4), top_y - m(1)), max(1, m(1.4)))
    # dark contact keyline along the awning hem so it reads crisp on the booth
    pygame.draw.line(surf, (40, 18, 14),
                     (cx - half_w, top_y + drop), (cx + half_w, top_y + drop),
                     max(1, m(1)))


def _nameboard(surf, label, cx, by, hero=False):
    """A small wooden sign carrying the bold gold-keyline label (the canonical
    defined edge: dark keyline under a bright bevel)."""
    f = font(12 if hero else 10)
    lw = _glyph_base(label, f, m(0.5)).get_width() + m(2)
    nb = pygame.Rect(0, 0, lw + m(20), m(24 if hero else 22))
    nb.center = (cx, by)
    surf.blit(vgrad(nb.w, nb.h, m(6), (66, 40, 18), (34, 20, 10), 255),
              nb.topleft)
    pygame.draw.rect(surf, (20, 12, 6), nb, width=max(1, m(1.4)),
                     border_radius=m(6))
    bevel_rim(surf, nb, m(6), (60, 36, 14), (*GOLD, 190), w=max(1, m(1.1)))
    gradient_text(surf, label, f, nb.center, GOLD_A_TOP, GOLD_A_BOT,
                  tracking=m(0.5), weight=m(1.0), keyline=(20, 10, 4), kw=m(1.0),
                  shadow=True)
    return nb


def draw_booth(surf, cx, cy, group, label):
    """ONE market booth: a striped awning above, a navy glass cabochon dome
    holding the category's REAL preview good (longer axis filling ~86% of the
    dome), and a bold gold-keyline nameboard. The whole booth is one ≥88px tap
    target."""
    R = m(25)
    dome_cy = cy

    # booth backboard plank the dome + label sit on
    bw = int(R * 2.1)
    bh = int(R * 2.0)
    board = pygame.Rect(cx - bw // 2, dome_cy - int(R * 1.05), bw, bh + m(24))
    drop_shadow(surf, board, m(12), blur=m(7), alpha=120, dy=m(4))
    surf.blit(vgrad(board.w, board.h, m(12), DECK_HI, DECK_LO, 255, gamma=1.18),
              board.topleft)
    for k in range(1, 3):
        ly = board.y + board.h * k // 3
        pygame.draw.line(surf, (*WOOD_DK, 120), (board.x + m(3), ly),
                         (board.right - m(3), ly), max(1, m(0.8)))
    top_sheen(surf, board, m(12), m(14), peak=44)
    contact_shadow(surf, board, m(12), m(6), alpha=95)
    pygame.draw.rect(surf, (28, 16, 8), board, width=max(1, m(1.8)),
                     border_radius=m(12))
    bevel_rim(surf, board, m(12), (60, 36, 14), (*GOLD_PALE, 170), w=max(1, m(1.4)))

    draw_awning(surf, cx, board.y - m(16), int(R * 1.42), m(26))

    # navy glass dome (re-floored, centre value-lift) + the larger preview
    sid = _preview_id(group)
    soft_glow(surf, cx, dome_cy, R + m(4), (255, 226, 150), 40, layers=8)
    _dome_floor(surf, cx, dome_cy, R)
    blit_preview(surf, sid, cx, dome_cy, R * 1.72, group=group)   # ~86% of dome
    cabochon_glass(surf, cx, dome_cy, R, tint=(240, 234, 252))

    _nameboard(surf, label, cx, board.bottom - m(4))


def _wax_crate(surf, cx, cy, w, h):
    """A wax-sealed mystery CRATE silhouette (loot, not an inbox envelope): a
    lit wooden chest with iron-banded corners, a domed lid, a red wax seal +
    '?' so the eye reads 'surprise reward'. Borrows the surprise-box body
    language (dark frame, gradient fill, top sheen) but at SS crate scale."""
    body = pygame.Rect(cx - w // 2, cy - h // 2 + m(4), w, h - m(6))
    # dark outer frame
    pygame.draw.rect(surf, (28, 16, 8), body.inflate(m(4), m(4)),
                     border_radius=m(4))
    # crate body: lit wood gradient
    surf.blit(vgrad(body.w, body.h, m(4), (150, 102, 56), (78, 46, 24), 255,
                    gamma=1.15), body.topleft)
    # plank seams + a top sheen
    for k in (1, 2):
        ly = body.y + body.h * k // 3
        pygame.draw.line(surf, (40, 24, 12, 200), (body.x + m(3), ly),
                         (body.right - m(3), ly), max(1, m(1)))
    pygame.draw.line(surf, (220, 180, 130, 220), (body.x + m(4), body.y + m(3)),
                     (body.right - m(4), body.y + m(3)), max(1, m(1.4)))
    # domed lid arc
    lid = pygame.Rect(body.x - m(2), body.y - m(10), body.w + m(4), m(22))
    pygame.draw.rect(surf, (28, 16, 8), lid.inflate(m(3), m(2)),
                     border_top_left_radius=m(11), border_top_right_radius=m(11))
    surf.blit(vgrad(lid.w, lid.h, m(11), (168, 116, 64), (104, 64, 32), 255),
              lid.topleft)
    pygame.draw.line(surf, (230, 190, 140, 220), (lid.x + m(6), lid.y + m(3)),
                     (lid.right - m(6), lid.y + m(3)), max(1, m(1.2)))
    # iron corner bands (brass-lit) at the four corners + a centre vertical band
    band = lerp_color(WOOD_LO, (180, 160, 120), 0.5)
    for bx in (body.x + m(4), body.right - m(7)):
        pygame.draw.rect(surf, band, (bx, body.y, m(3), body.h))
        pygame.draw.rect(surf, (20, 12, 6), (bx, body.y, m(3), body.h),
                         max(1, m(0.6)))
    pygame.draw.rect(surf, band, (cx - m(2), body.y, m(4), body.h))
    pygame.draw.rect(surf, (20, 12, 6), (cx - m(2), body.y, m(4), body.h),
                     max(1, m(0.6)))
    # gold corner studs
    for sx in (body.x + m(5), body.right - m(5)):
        for sy in (body.y + m(4), body.bottom - m(4)):
            pygame.draw.circle(surf, GOLD, (sx, sy), m(2))
            pygame.draw.circle(surf, (40, 24, 10), (sx, sy), m(2), max(1, m(0.5)))
    # the red wax seal + '?' dead centre (the mystery tell)
    sr = m(13)
    soft_glow(surf, cx, cy + m(2), sr + m(2), (255, 120, 90), 90, layers=6)
    pygame.draw.circle(surf, (150, 26, 26), (cx, cy + m(2)), sr)
    pygame.draw.circle(surf, (214, 58, 52), (cx, cy + m(2)), sr - m(2))
    pygame.draw.circle(surf, (110, 16, 16), (cx, cy + m(2)), sr, max(1, m(1.2)))
    soft_glow(surf, cx - m(3), cy - m(2), m(3), (255, 200, 190), 120, layers=4)
    _draw_qmark(surf, cx, cy + m(2), m(15), (250, 236, 214), (90, 12, 12),
                thick=m(1.4))


def draw_parcels_hero(surf, cx, cy):
    """PARCELS — the differentiated mystery HERO. Not a 7th striped booth: a
    rope-lashed cargo dais with brass-cornered framing, a wax-sealed treasure
    crate on top, and a DEFINED red glow ring with a dark vignette behind it so
    the hero punches out of the sunset instead of muddying into it."""
    R = m(34)
    # dark vignette behind the hero so the red bloom reads as a defined ring
    vig = pygame.Surface((R * 5, R * 5), pygame.SRCALPHA)
    soft_glow(vig, R * 5 // 2, R * 5 // 2, int(R * 2.2), (6, 4, 16), 120, layers=12)
    surf.blit(vig, (cx - R * 5 // 2, cy - R * 5 // 2))
    # a tight, DEFINED red glow ring (bloom + a crisp inner ring stroke)
    ring = pygame.Surface((R * 4, R * 4), pygame.SRCALPHA)
    rc = R * 2
    soft_glow(ring, rc, rc, int(R * 1.5), (244, 96, 70), 110, layers=12)
    for k in range(3, 0, -1):
        pygame.draw.circle(ring, (255, 140, 110, int(110 * k / 3)), (rc, rc),
                           R + m(8) + k * m(2), max(1, m(2)))
    surf.blit(ring, (cx - rc, cy - rc), special_flags=pygame.BLEND_ADD)

    # the rope-lashed cargo dais (a wide low pallet the crate sits on)
    dais = pygame.Rect(cx - int(R * 1.5), cy + int(R * 0.62), int(R * 3), m(20))
    drop_shadow(surf, dais, m(6), blur=m(7), alpha=140, dy=m(4))
    surf.blit(vgrad(dais.w, dais.h, m(5), DECK_HI, DECK_LO, 255, gamma=1.2),
              dais.topleft)
    pygame.draw.rect(surf, (24, 14, 6), dais, width=max(1, m(1.6)),
                     border_radius=m(5))
    bevel_rim(surf, dais, m(5), (60, 36, 14), (*GOLD, 180), w=max(1, m(1.2)))
    # brass corner caps on the dais
    for dx in (dais.x + m(4), dais.right - m(4)):
        pygame.draw.circle(surf, GOLD, (dx, dais.y + m(4)), m(3))
        pygame.draw.circle(surf, (40, 24, 10), (dx, dais.y + m(4)), m(3),
                           max(1, m(0.6)))
    # rope lashing across the dais
    for rx in (cx - int(R * 0.7), cx + int(R * 0.7)):
        pygame.draw.line(surf, lerp_color(WOOD_MID, (200, 180, 140), 0.4),
                         (rx, dais.y - m(2)), (rx, dais.bottom + m(1)), max(1, m(2)))

    # the wax-sealed treasure crate, lifted so its lid clears the awning gap
    _wax_crate(surf, cx, cy + m(2), int(R * 1.7), int(R * 1.5))

    # hero nameboard
    _nameboard(surf, "PARCELS", cx, dais.bottom + m(16), hero=True)


# =============================================================================
# Pip the captain at the helm + a coin
# =============================================================================
def draw_captain(surf, cx, cy):
    """Pip as the airship captain on the stern poop-deck: a small lit deck shelf
    under his feet, the ship's wheel (helm) just to his right, Pip himself the
    real base parrot scaled with a restrained warm key-light, and a coin he
    presents — so he reads unmistakably as the merchant, NOT another booth dome
    (no glass cabochon around him)."""
    src = parrot.get_parrot(1, 0.0)
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    box = m(54)
    sw, sh = src.get_size()
    s = box / max(sw, sh)
    pip = pygame.transform.smoothscale(
        src, (max(1, int(sw * s)), max(1, int(sh * s))))

    # the stern poop-deck shelf Pip stands on (a short lit plank with a rail)
    shelf = pygame.Rect(cx - m(34), cy + m(20), m(80), m(16))
    surf.blit(vgrad(shelf.w, shelf.h, m(4), DECK_HI, DECK_LO, 255, gamma=1.2),
              shelf.topleft)
    pygame.draw.rect(surf, (28, 16, 8), shelf, width=max(1, m(1.4)),
                     border_radius=m(4))
    pygame.draw.line(surf, (*GOLD, 150), (shelf.x + m(3), shelf.y + m(1)),
                     (shelf.right - m(3), shelf.y + m(1)), max(1, m(1)))

    # ship's wheel (helm) to Pip's RIGHT so he stands AT it, not inside it
    wr = m(17)
    wcx, wcy = cx + m(30), cy + m(2)
    wheel = pygame.Surface((wr * 2 + m(10), wr * 2 + m(10)), pygame.SRCALPHA)
    wc = wr + m(5)
    pygame.draw.circle(wheel, (40, 24, 10), (wc, wc), wr, max(1, m(2.6)))
    pygame.draw.circle(wheel, lerp_color(WOOD_HI, GOLD, 0.35), (wc, wc), wr,
                       max(1, m(1.4)))
    for a in range(0, 360, 45):
        ax = wc + math.cos(math.radians(a)) * (wr + m(4))
        ay = wc + math.sin(math.radians(a)) * (wr + m(4))
        ix = wc + math.cos(math.radians(a)) * (wr - m(4))
        iy = wc + math.sin(math.radians(a)) * (wr - m(4))
        pygame.draw.line(wheel, lerp_color(WOOD_MID, GOLD, 0.35),
                         (ix, iy), (ax, ay), max(1, m(2)))
        pygame.draw.circle(wheel, GOLD, (int(ax), int(ay)), m(2))
    pygame.draw.circle(wheel, lerp_color(WOOD_HI, GOLD, 0.45), (wc, wc), m(4))
    surf.blit(wheel, (wcx - wc, wcy - wc))

    # a restrained warm key-light ABOVE Pip (a soft halo, kept low + tight so it
    # never blooms to the white disc that read as a booth dome).
    soft_glow(surf, cx, cy - m(4), m(26), (255, 220, 150), 34, layers=8)

    pr = pip.get_rect(center=(cx, cy - m(2)))
    sh = pip.copy()
    sh.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sh.set_alpha(120)
    surf.blit(sh, (pr.x + m(2), pr.y + m(4)))
    surf.blit(_rim_light(pip, alpha=150), pr.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(pip, pr.topleft)

    # a coin he presents, clear to his lower-left (away from the helm)
    coin_cx, coin_cy = cx - m(22), cy + m(12)
    soft_glow(surf, coin_cx, coin_cy, m(9), (255, 206, 92), 60, layers=6)
    coin_glyph(surf, coin_cx, coin_cy, m(8))


# =============================================================================
# Header — STORE wordmark + recessed gold balance capsule + TAP A STALL hint
# =============================================================================
def balance_capsule(surf, cx, y):
    val = f"{BALANCE:,}"
    vf = font(20)
    vw = _glyph_base(val, vf, 0).get_width() + m(2)
    coin_d, gapc, padl, padr = m(24), m(15), m(13), m(18)
    w = padl + coin_d + gapc + vw + padr
    h = m(38)
    cap = pygame.Rect(cx - w // 2, y - h // 2, w, h)
    drop_shadow(surf, cap, h // 2, blur=m(6), alpha=130, dy=m(3))
    surf.blit(vgrad(cap.w, cap.h, h // 2, (58, 42, 22), (22, 15, 8), 255, gamma=1.1),
              cap.topleft)
    top_sheen(surf, cap, h // 2, m(14), peak=50)
    contact_shadow(surf, cap, h // 2, m(5), alpha=110)
    pygame.draw.rect(surf, (0, 0, 0, 200), cap, width=max(1, m(1.6)),
                     border_radius=h // 2)
    bevel_rim(surf, cap, h // 2, lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD_PALE, 240), w=max(1, m(1.6)))
    x = cap.x + padl
    soft_glow(surf, x + coin_d // 2, y, int(coin_d * 0.40), (255, 206, 92), 42,
              layers=6)
    coin_glyph(surf, x + coin_d // 2, y, coin_d // 2)
    x += coin_d + gapc
    gradient_text(surf, val, vf, (x + vw // 2, y), GOLD_A_TOP, GOLD_A_BOT,
                  weight=m(0.9), keyline=(96, 56, 12), kw=m(1.1), shadow=True)


def draw_header(surf):
    # a soft warm darkening band only behind the title lane so the gold-on-red
    # wordmark + capsule read against the bright apex sky without a hard bar.
    band = pygame.Surface((DW, m(100)), pygame.SRCALPHA)
    for yy in range(m(100)):
        a = int(96 * (1 - yy / m(100)) ** 1.3)
        pygame.draw.line(band, (14, 12, 40, a), (0, yy), (DW, yy))
    surf.blit(band, (0, 0))
    pygame.draw.rect(surf, (*GOLD, 55), (m(3), m(3), DW - m(6), DH - m(6)),
                     width=max(1, m(1)), border_radius=m(12))
    title_wordmark(surf, "STORE", (DW // 2, m(26)), 30, tracking=m(4))
    balance_capsule(surf, DW // 2, m(64))
    # TAP A STALL hint just under the capsule
    plain_text(surf, "TAP A STALL", font(10), (DW // 2, m(90)),
               (250, 224, 168), shadow_a=150, tracking=m(2), weight=m(0.7),
               keyline=(20, 12, 6), kw=m(0.7))


# =============================================================================
# Compose
# =============================================================================
def render_device():
    surf = pygame.Surface((DW, DH))
    draw_bg(surf)

    # the galleon, back-to-front: envelope + suspension, masts/rigging, hull
    mast_xs = [m(86), m(180), m(274)]
    top_y = m(HULL_TOP)
    draw_envelope(surf)
    draw_masts_and_decor(surf, mast_xs, top_y)
    draw_hull(surf)

    # upper-rigging star-glints foreshadow the constellation jewel store the
    # stalls open into (a few gold sparkles on the top rigging band).
    for gx, gy in ((m(120), m(196)), (m(180), m(186)), (m(238), m(196)),
                   (m(96), m(214)), (m(262), m(214))):
        soft_glow(surf, gx, gy, m(3), (255, 240, 200), 110, layers=5)
        pygame.draw.line(surf, (255, 246, 214, 220), (gx - m(3), gy),
                         (gx + m(3), gy), max(1, m(0.7)))
        pygame.draw.line(surf, (255, 246, 214, 220), (gx, gy - m(3)),
                         (gx, gy + m(3)), max(1, m(0.7)))

    # 6 striped booths in two clean rows (grid nudged up to declutter the
    # foredeck) + the PARCELS mystery hero, each booth a ≥88px tap target with
    # generous padding so nothing overlaps at 360px. Row 1 hangs from the rigging
    # tier (centre booth raised on the mainmast); row 2 sits on the mid-deck.
    draw_booth(surf, m(72),  m(244), *STALLS[0])     # COSTUMES
    draw_booth(surf, m(180), m(232), *STALLS[1])     # PARROTS  (centre, raised)
    draw_booth(surf, m(288), m(244), *STALLS[2])     # ANIMALS
    draw_booth(surf, m(72),  m(334), *STALLS[3])     # SHOES
    draw_booth(surf, m(180), m(334), *STALLS[4])     # HATS
    draw_booth(surf, m(288), m(334), *STALLS[5])     # SHADES
    # PARCELS — the differentiated mystery hero crate, lifted so its nameboard
    # clears the gunwale.
    draw_parcels_hero(surf, m(180), m(424))

    # Pip the captain at the helm on the stern poop-deck, raised so his whole
    # silhouette clears the gunwale, clear of every label.
    draw_captain(surf, m(64), m(430))

    draw_header(surf)
    return surf


def downscale(device_surf, scale=1):
    return pygame.transform.smoothscale(device_surf, (W * scale, H * scale))


def main():
    _build_bg()
    dev = render_device()
    pygame.image.save(downscale(dev, 1), os.path.join(_HERE, "round_2.png"))
    pygame.image.save(downscale(dev, 2), os.path.join(_HERE, "round_2@2x.png"))
    print("SS =", SS, "device =", DW, "x", DH)
    print("saved round_2.png (360x640) + round_2@2x.png (720x1280)")


if __name__ == "__main__":
    main()
