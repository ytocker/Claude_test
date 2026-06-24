"""
BALLOON CARAVAN — store "bazaar landing" concept (selection sheet prototype).

A drifting caravan of hot-air market balloons climbs a golden-hour -> indigo
twilight sky. Seven striped macaw-red/cream envelopes, each carrying a hanging
wicker market-stall basket, float in a loose staggered zig-zag column; gold
pennants + drifting coins string the caravan together; far cloud-isles below
give depth. Pip flies between them as the caravan-master vendor. Stars emerge at
the indigo apex so tapping a stall would dissolve into the constellation jewel
store. The "festival in the sky" cousin of the cloud-platform bazaar — balloons
instead of clouds.

Authoring follows the locked SS=4 supersample pipeline: everything is drawn on
a 360*SS x 640*SS device canvas (curves, gores, ropes, basket weave, gem domes,
glyphs all oversized) then ONE pygame.transform.smoothscale down to 360x640.
The downscale is what turns oversized geometry into crisp anti-aliased edges.

All primitives + palette anchors are reused from
docs/store_redesign/constellation_hi/render_hi.py so the explorations look like
the real store. Both build targets safe: pure pygame, no numpy, no
desktop/browser-only API.
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

# Reuse the locked constellation primitives so the bazaar reads as the same
# store DNA (one gold, one bezel, one glass dome, one coin, one wordmark).
from docs.store_redesign.constellation_hi.render_hi import (
    SS, DW, DH, m, mf, font,
    vgrad, vgrad_stops, gold_a_fill, soft_glow, drop_shadow,
    gradient_text, plain_text, facet_gem, cabochon, cabochon_glass,
    coin_glyph, bevel_rim, top_sheen, gold_rule, title_wordmark,
    _glyph_base, _stamp_bold,
    GOLD, GOLD_PALE, GOLD_DEEP, GOLD_A_TOP, GOLD_A_BOT, GOLD_A_COIN_RIM,
    RARITY, CARD_RING_BRIGHT,
)


# ── concept palette: golden-hour low -> indigo+gold nebula apex ────────────────
# The sky is the whole stage here (not the constellation's flat night). A warm
# horizon glow at the foot rises through amber/rose into a deep indigo apex where
# the jewel-store stars emerge — the visual promise that entering a stall climbs
# into the night-jewel store.
SKY_STOPS = [
    (0.00, (18, 14, 52)),     # indigo apex (where the stars live)
    (0.16, (32, 22, 72)),     # violet
    (0.40, (78, 44, 96)),     # plum dusk
    (0.62, (158, 86, 96)),    # rose band
    (0.80, (224, 140, 84)),   # warm amber
    (1.00, (255, 196, 110)),  # golden-hour horizon glow
]
HORIZON_GLOW = (255, 206, 140)
APEX_NEBULA = (96, 78, 178)

# Balloon envelope = macaw-red body + warm cream gore stripes, gold-rimmed.
BALLOON_RED_HI = (236, 96, 78)
BALLOON_RED = (206, 58, 52)
BALLOON_RED_LO = (138, 30, 38)
BALLOON_CREAM_HI = (255, 244, 218)
BALLOON_CREAM = (246, 224, 176)
BALLOON_CREAM_LO = (196, 158, 110)
# PARCELS hero envelope runs a hotter mystery-red so it reads as the prize.
HERO_RED_HI = (255, 120, 96)
HERO_RED = (236, 64, 64)
HERO_RED_LO = (150, 24, 30)
MYSTERY = {"gem": (244, 96, 96), "glow": (236, 64, 64), "deep": (120, 22, 26)}

WICKER_HI = (208, 158, 96)
WICKER = (168, 116, 64)
WICKER_LO = (104, 66, 32)
ROPE = (228, 206, 150)
ROPE_LO = (150, 120, 64)

BALANCE = 14250


# ── stalls -> balloons ────────────────────────────────────────────────────────
# Each stall maps a store group to a real preview thumbnail. SHADES falls back to
# a clear shades icon (skin_shades_round) so it never shows the bare base parrot
# that group[0] (NO SHADES) would. PARCELS is the glowing red mystery hero,
# anchored bottom/foreground; its envelope runs the hotter mystery-red.
STALLS = [
    {"label": "COSTUMES", "group": "costume"},
    {"label": "PARROTS",  "group": "parrot"},
    {"label": "ANIMALS",  "group": "animal"},
    {"label": "SHOES",    "group": "shoes"},
    {"label": "HATS",     "group": "hats"},
    {"label": "SHADES",   "group": "shades", "fallback": "skin_shades_round"},
    {"label": "PARCELS",  "group": "parcels", "hero": True},
]


def _stall_sid(stall):
    from game import store_catalog
    ids = store_catalog.ids_of_group(stall["group"])
    sid = ids[0] if ids else None
    if stall.get("fallback") and (sid is None or sid == "skin_shades_none"):
        sid = stall["fallback"]
    return sid


# Preview thumbnail for a stall's dome, contained (letterboxed) inside the box so
# aspect-extreme items (flip-flops, party hat) never clip the dome rim.
_thumb_cache = {}


def stall_thumb(stall, box_px):
    sid = _stall_sid(stall)
    key = (sid, box_px)
    out = _thumb_cache.get(key)
    if out is not None:
        return out
    src = None
    if sid is not None:
        src = parrot.get_skin_icon(sid)
        if src is None:
            # SHADES/base groups: fall back to a clear icon, never a bare parrot.
            fb = stall.get("fallback")
            if fb is not None:
                src = parrot.get_skin_icon(fb) or parrot.get_skin_frame(fb, 1, 0.0)
            else:
                src = parrot.get_skin_frame(sid, 1, 0.0)
    if src is None:
        out = pygame.Surface((1, 1), pygame.SRCALPHA)
        _thumb_cache[key] = out
        return out
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    # CONTAIN, not cover — extreme aspects are letterboxed within the dome.
    s = box_px / max(sw, sh)
    scaled = pygame.transform.smoothscale(
        src, (max(1, int(sw * s)), max(1, int(sh * s))))
    lift = scaled.copy()
    lift.fill((46, 46, 46, 0), special_flags=pygame.BLEND_RGB_ADD)  # punch value
    _thumb_cache[key] = lift
    return lift


# =============================================================================
# Atmosphere
# =============================================================================
def _sky_grad(w, h, stops):
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


_stars = None


def _build_stars():
    """Stars emerge ONLY in the indigo apex (top band) and fade out before the
    warm horizon — the visual promise of climbing into the night-jewel store."""
    global _stars
    rnd = random.Random(71)
    stars = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for n, rmin, rmax, amin, amax in ((130, 0.4, 0.9, 26, 80),
                                      (46, 0.9, 1.5, 60, 130),
                                      (15, 1.3, 2.3, 110, 200)):
        for _ in range(n):
            x = rnd.randint(0, DW)
            # bias high: more stars near the apex, none past the rose band
            fy = rnd.random() ** 2.2
            y = int(fy * DH * 0.46)
            fade = 1.0 - (y / (DH * 0.46))
            if fade <= 0.05:
                continue
            r = m(rnd.uniform(rmin, rmax))
            a = int(rnd.randint(amin, amax) * fade)
            tint = rnd.choice([(255, 252, 240), (220, 226, 255), (255, 238, 206)])
            pygame.draw.circle(stars, (*tint, a), (x, y), max(1, int(r)))
    for _ in range(10):
        x = rnd.randint(m(20), DW - m(20))
        y = rnd.randint(m(16), int(DH * 0.30))
        fade = 1.0 - (y / (DH * 0.30))
        L = m(rnd.uniform(3, 6))
        a = int(rnd.randint(120, 200) * max(0.2, fade))
        col = (255, 246, 214, a)
        pygame.draw.line(stars, col, (x - L, y), (x + L, y), max(1, m(0.7)))
        pygame.draw.line(stars, col, (x, y - L), (x, y + L), max(1, m(0.7)))
        soft_glow(stars, x, y, m(3), (255, 244, 210), int(70 * max(0.2, fade)),
                  layers=4)
    _stars = stars


def _cloud_isle(surf, cx, cy, w, h, warm, alpha):
    """A far flat-bottomed cloud-isle: stacked translucent lobes lit warm on top,
    cool plum underneath — the depth bed the caravan floats above."""
    isle = pygame.Surface((w + m(40), h + m(40)), pygame.SRCALPHA)
    ox, oy = m(20), m(20)
    rnd = random.Random(int(cx * 7 + cy))
    lobes = []
    n = 5
    for i in range(n):
        lx = ox + int(w * (i + 0.5) / n) + rnd.randint(-m(8), m(8))
        lr = int(h * rnd.uniform(0.5, 0.9))
        ly = oy + h - lr + rnd.randint(-m(4), m(4))
        lobes.append((lx, ly, lr))
    # plum shadow underside
    for lx, ly, lr in lobes:
        pygame.draw.circle(isle, (58, 36, 70, alpha), (lx, ly + m(5)), lr)
    # warm-lit body
    for lx, ly, lr in lobes:
        pygame.draw.circle(isle, (*warm, alpha), (lx, ly), lr)
    # flat base haze
    base = pygame.Surface((w + m(40), m(18)), pygame.SRCALPHA)
    for yy in range(m(18)):
        a = int(alpha * 0.7 * (1 - yy / m(18)))
        pygame.draw.line(base, (*warm, a), (0, yy), (w + m(40), yy))
    isle.blit(base, (0, oy + h - m(2)))
    # top sheen kiss
    for lx, ly, lr in lobes:
        soft_glow(isle, lx - int(lr * 0.3), ly - int(lr * 0.4),
                  int(lr * 0.5), (255, 230, 190), int(alpha * 0.5), layers=5)
    surf.blit(isle, (cx - ox - w // 2, cy - oy - h // 2))


def draw_bg(surf):
    surf.blit(_sky_grad(DW, DH, SKY_STOPS), (0, 0))
    # indigo apex nebula bloom — soft violet so the emerging stars sit in cloud.
    soft_glow(surf, int(DW * 0.5), int(DH * 0.10), m(220), APEX_NEBULA, 46,
              layers=10)
    soft_glow(surf, int(DW * 0.66), int(DH * 0.04), m(150), (120, 96, 200), 34,
              layers=8)
    # golden-hour horizon glow welling up from the foot.
    soft_glow(surf, int(DW * 0.42), int(DH * 1.0), m(300), HORIZON_GLOW, 70,
              layers=12)
    surf.blit(_stars, (0, 0), special_flags=pygame.BLEND_ADD)
    # far cloud-isles below for depth (small, hazy, low-contrast, warm-lit).
    _cloud_isle(surf, int(DW * 0.18), int(DH * 0.72), m(120), m(30),
                (206, 144, 126), 42)
    _cloud_isle(surf, int(DW * 0.84), int(DH * 0.80), m(150), m(36),
                (222, 156, 122), 52)
    _cloud_isle(surf, int(DW * 0.50), int(DH * 0.97), m(240), m(54),
                (236, 168, 124), 66)
    # gentle top + bottom vignette so the chrome (header, hint) reads.
    vig = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for y in range(DH):
        f = y / DH
        a = 0
        if f < 0.16:
            a = int(120 * (1 - f / 0.16) ** 1.4)
        elif f > 0.90:
            a = int(70 * ((f - 0.90) / 0.10) ** 1.4)
        if a > 0:
            pygame.draw.line(vig, (10, 8, 30, a), (0, y), (DW, y))
    surf.blit(vig, (0, 0))


# =============================================================================
# Balloon caravan element: envelope + ropes + wicker stall + pennants
# =============================================================================
def _gore_shade(t, lit, lo_red, hi_red, lo_cream, hi_cream, stripe):
    """Per-column volumetric shade across a balloon's width. t in [0,1] left->right,
    lit is the top-left light term in [0,1]. Alternating macaw-red/cream gores."""
    if stripe:
        base_lo, base_hi = lo_cream, hi_cream
    else:
        base_lo, base_hi = lo_red, hi_red
    return lerp_color(base_lo, base_hi, lit)


def draw_balloon(surf, cx, cy, rw, rh, hero=False, gores=8):
    """Round volumetric hot-air balloon: smooth-shaded vertical gores (one
    top-left light), a gold rim-light, a teardrop base nipple, an AO/contact
    shadow on the basket below. Authored oversized; the downscale resolves the
    gore seams crisp."""
    hi_r = HERO_RED_HI if hero else BALLOON_RED_HI
    md_r = HERO_RED if hero else BALLOON_RED
    lo_r = HERO_RED_LO if hero else BALLOON_RED_LO

    # ── soft cast aura (kept tight + low so the golden-hour sky survives behind
    # the caravan; only the hero balloon glows hot enough to read as the prize).
    if hero:
        soft_glow(surf, cx, cy, int(rw * 0.62), HERO_RED, 48, layers=10)
        soft_glow(surf, cx, cy, int(rw * 0.36), (255, 150, 120), 30, layers=7)

    top = cy - rh * 0.56
    bot = cy + rh * 0.50
    # silhouette half-width as a function of vertical position (teardrop: round
    # crown, tapering to a small mouth at the base).
    def half_w(yy):
        # yy normalized 0 (top) .. 1 (base mouth)
        if yy < 0.86:
            # near-circular crown
            s = math.sin(math.pi * (yy / 0.86) * 0.5 + 0.0)
            # ellipse-ish: widest near 0.42
            ang = (yy / 0.86) * math.pi
            return (rw * 0.5) * math.sin(ang) ** 0.62
        else:
            # taper the mouth in
            f = (yy - 0.86) / 0.14
            return (rw * 0.5) * (1 - f) * 0.30 + rw * 0.06

    H_px = bot - top
    # ── contact shadow on the basket zone (drawn first, beneath) ──
    # (basket drawn later; a soft AO under the mouth grounds the load.)

    # ── per-pixel TRUE-SPHERE gore fill ──
    # Shade by a real surface normal (z = sqrt(1 - x^2 - y^2) over the bulb), lit
    # by one top-left key. That Lambert term is what makes the bulb read round &
    # volumetric instead of a flat striped lozenge. Authored at SS, downscaled to
    # a crisp dome. Gore membership is by angular column so seams curve with the
    # surface. Width-scan still clamps the fill to the teardrop silhouette.
    lx, ly, lz = -0.52, -0.46, 0.72                 # top-left key (normalized-ish)
    lmag = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / lmag, ly / lmag, lz / lmag
    col_n = max(40, int(rw))
    body = pygame.Surface((int(rw) + m(8), int(H_px) + m(8)), pygame.SRCALPHA)
    bx, by = m(4), m(4)
    Rsphere = rw * 0.5
    for ix in range(col_n):
        u = ix / (col_n - 1)            # 0..1 left->right
        px = u * rw
        dxn = abs(px - rw * 0.5)
        ytop = ybot = None
        steps = 70
        for s in range(steps + 1):
            yy = s / steps
            if half_w(yy) >= dxn:
                if ytop is None:
                    ytop = yy
                ybot = yy
        if ytop is None:
            continue
        y0 = by + ytop * H_px
        y1 = by + ybot * H_px
        sx = (px - rw * 0.5) / Rsphere              # -1..1 across the bulb
        for sy in range(int(y0), int(y1) + 1):
            vy = (sy - by) / H_px                    # 0 top .. 1 base
            # sphere-y maps the crown (vy~0.05..0.62) onto -1..1; below that the
            # surface rolls under so we clamp to a deepening base term.
            syf = (vy - 0.34) / 0.34                 # -1 crown .. +1 equator-ish
            r2 = sx * sx + syf * syf
            if r2 < 0.985:
                nz = math.sqrt(1.0 - r2)
            else:
                # near/over the limb: ease nz to 0 smoothly so the terminator
                # doesn't read as a noisy ring at the bulb edge.
                nz = 0.0
            lam = sx * lx + syf * ly + nz * lz       # Lambert
            lam = max(0.0, lam)
            # base falls off below the equator regardless (gravity-lit teardrop).
            base_fall = 1.0 - max(0.0, (vy - 0.55)) * 0.7
            f = max(0.0, min(1.0, (0.18 + lam * 0.95) * base_fall))
            # gore membership by angular position around the bulb so seams curve.
            ang = (math.atan2(sx, max(0.05, nz if r2 < 1 else 0.2)) / (math.pi))
            g = ((u) * gores)
            stripe = (int(g) % 2 == 1)
            if stripe:
                col = lerp_color(BALLOON_CREAM_LO, BALLOON_CREAM_HI, f)
                col = lerp_color(col, BALLOON_CREAM, 0.12)
            else:
                col = lerp_color(lo_r, md_r, min(1.0, f * 1.5))
                if f > 0.7:
                    col = lerp_color(col, hi_r, (f - 0.7) / 0.3 * 0.6)
            body.set_at((bx + ix, sy), (*col, 255))
    surf.blit(body, (int(cx - rw * 0.5 - bx), int(top - by)))

    # ── gore seams: faint dark hairlines along each gore boundary ──
    seam = pygame.Surface((int(rw) + m(8), int(H_px) + m(8)), pygame.SRCALPHA)
    for gidx in range(1, gores):
        u = gidx / gores
        # trace the seam down the silhouette
        pts = []
        for s in range(0, 61):
            yy = s / 60
            hw = half_w(yy)
            px = rw * 0.5 + (u - 0.5) * 2 * hw
            pts.append((bx + px, by + yy * H_px))
        if len(pts) > 1:
            pygame.draw.lines(seam, (60, 18, 18, 70), False, pts, max(1, m(0.6)))
    surf.blit(seam, (int(cx - rw * 0.5 - bx), int(top - by)))

    # ── gold rim-light hugging the upper-left silhouette ──
    rim = pygame.Surface((int(rw) + m(12), int(H_px) + m(12)), pygame.SRCALPHA)
    rb = m(6)
    rim_pts = []
    for s in range(0, 61):
        yy = s / 60
        hw = half_w(yy)
        rim_pts.append((rb + rw * 0.5 - hw, rb + yy * H_px))
    if len(rim_pts) > 1:
        for wth, al in ((m(2.2), 70), (m(1.2), 150), (m(0.6), 220)):
            pygame.draw.lines(rim, (255, 232, 168, al), False, rim_pts,
                              max(1, int(wth)))
    # dark contact keyline on the lower-right silhouette so the bulb is defined.
    dk_pts = []
    for s in range(0, 61):
        yy = s / 60
        hw = half_w(yy)
        dk_pts.append((rb + rw * 0.5 + hw, rb + yy * H_px))
    if len(dk_pts) > 1:
        pygame.draw.lines(rim, (70, 14, 18, 150), False, dk_pts, max(1, m(1.0)))
    surf.blit(rim, (int(cx - rw * 0.5 - rb), int(top - rb)))

    # ── crown specular: a soft ELONGATED sheen following the bulb curvature
    # (an arc-shaped translucent kiss), not a hard dot. Drawn as a small cluster
    # of feathered glows along the upper-left curve so it reads as a glossy
    # reflection of the sky, masked to the bulb.
    spec = pygame.Surface((int(rw) + m(8), int(H_px) + m(8)), pygame.SRCALPHA)
    scx, scy = rw * 0.5 + m(4), m(4)
    for k in range(5):
        t = k / 4
        ang = math.radians(208 + t * 44)            # upper-left arc
        rr = rw * 0.34
        gx = scx + rr * math.cos(ang)
        gy = scy + H_px * 0.30 + rr * math.sin(ang) * 0.9
        soft_glow(spec, int(gx), int(gy), int(rw * (0.10 - t * 0.012)),
                  (255, 250, 232), int(60 - t * 8), layers=5)
    # mask to the bulb silhouette so the sheen never bleeds past the rim
    smask = pygame.Surface(spec.get_size(), pygame.SRCALPHA)
    sil_pts = []
    for s in range(0, 71):
        yy = s / 70
        sil_pts.append((scx - half_w(yy), m(4) + yy * H_px))
    for s in range(70, -1, -1):
        yy = s / 70
        sil_pts.append((scx + half_w(yy), m(4) + yy * H_px))
    if len(sil_pts) > 2:
        pygame.draw.polygon(smask, (255, 255, 255, 255), sil_pts)
    spec.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(spec, (int(cx - rw * 0.5 - m(4)), int(top - m(4))),
              special_flags=pygame.BLEND_ADD)

    # ── base mouth ring + load bar (where ropes gather) ──
    mouth_y = top + H_px * 0.99
    mw = half_w(0.995) * 2
    ring = pygame.Rect(int(cx - mw * 0.62), int(mouth_y - m(2)),
                       int(mw * 1.24), m(7))
    pygame.draw.ellipse(surf, lerp_color(lo_r, NEAR_BLACK, 0.3), ring)
    pygame.draw.ellipse(surf, (255, 226, 150), ring, max(1, m(1)))
    return mouth_y, mw


def draw_pennant_string(surf, x0, y0, x1, y1, n=6):
    """A swag of gold/cream triangular pennants between two caravan anchors,
    hung on a fine catenary thread."""
    # catenary-ish sag
    def pt(t):
        x = x0 + (x1 - x0) * t
        sag = math.sin(math.pi * t) * m(10)
        y = y0 + (y1 - y0) * t + sag
        return x, y
    thread = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pts = [pt(i / 24) for i in range(25)]
    pygame.draw.lines(thread, (230, 206, 150, 150), False, pts, max(1, m(0.8)))
    surf.blit(thread, (0, 0))
    cols = [(244, 196, 96), (246, 226, 170), (224, 96, 78)]
    for i in range(n):
        t = (i + 0.5) / n
        ax, ay = pt(t - 0.5 / n)
        bx, by = pt(t + 0.5 / n)
        mx, my = (ax + bx) / 2, (ay + by) / 2 + m(10)
        c = cols[i % len(cols)]
        pygame.draw.polygon(surf, lerp_color(c, NEAR_BLACK, 0.25),
                            [(ax, ay + m(1)), (bx, by + m(1)), (mx, my + m(1))])
        pygame.draw.polygon(surf, c, [(ax, ay), (bx, by), (mx, my)])
        # lit kiss top-left of each pennant
        pygame.draw.line(surf, (255, 244, 210),
                         (ax, ay), (mx, my), max(1, m(0.6)))


def draw_basket(surf, cx, top_y, bw, bh, mouth_y, mw, label, stall, hero=False):
    """The hanging wicker market-stall basket: 4 ropes gathering from the balloon
    mouth to a load ring, a woven wicker box, a glass cabochon holding the
    category preview thumbnail, and a bold gold-keyline category label on an
    awning sign. Real AO under the basket grounds it."""
    # ── ropes from mouth ring to the basket top corners ──
    lx = cx - bw * 0.42
    rx = cx + bw * 0.42
    rope_top = [(cx - mw * 0.34, mouth_y), (cx - mw * 0.12, mouth_y),
                (cx + mw * 0.12, mouth_y), (cx + mw * 0.34, mouth_y)]
    rope_bot = [(lx, top_y), (cx - bw * 0.14, top_y),
                (cx + bw * 0.14, top_y), (rx, top_y)]
    for (ax, ay), (bx, by) in zip(rope_top, rope_bot):
        pygame.draw.line(surf, ROPE_LO, (ax, ay + m(1)), (bx, by + m(1)),
                         max(1, m(1.6)))
        pygame.draw.line(surf, ROPE, (ax, ay), (bx, by), max(1, m(1.0)))

    box = pygame.Rect(int(cx - bw * 0.5), int(top_y), int(bw), int(bh))
    rad = m(4)
    # ── ground/AO shadow beneath the basket ──
    ao = pygame.Surface((box.w + m(40), m(22)), pygame.SRCALPHA)
    for k in range(m(11), 0, -1):
        a = int(90 * (k / m(11)))
        pygame.draw.ellipse(ao, (10, 6, 20, a),
                            (m(20) - k, m(11) - k // 2,
                             box.w + 2 * k, m(11) + k))
    surf.blit(ao, (box.x - m(20), box.bottom - m(2)))

    # ── wicker body: a warm gradient box + woven cross-hatch ──
    surf.blit(vgrad(box.w, box.h, rad, WICKER_HI, WICKER_LO, 255, gamma=1.1),
              box.topleft)
    weave = pygame.Surface(box.size, pygame.SRCALPHA)
    step = m(5)
    for yy in range(0, box.h, step):
        for xx in range(0, box.w, step * 2):
            ox = (step if (yy // step) % 2 else 0)
            pygame.draw.line(weave, (90, 56, 26, 150),
                             (xx + ox, yy), (xx + ox + step, yy + step),
                             max(1, m(0.7)))
            pygame.draw.line(weave, (220, 174, 110, 120),
                             (xx + ox + step, yy), (xx + ox, yy + step),
                             max(1, m(0.7)))
    wm = pygame.Surface(box.size, pygame.SRCALPHA)
    pygame.draw.rect(wm, (255, 255, 255, 255), wm.get_rect(), border_radius=rad)
    weave.blit(wm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(weave, box.topleft)
    # rim hoops top + bottom
    pygame.draw.rect(surf, (224, 178, 110), (box.x, box.y, box.w, m(5)),
                     border_top_left_radius=rad, border_top_right_radius=rad)
    pygame.draw.rect(surf, (120, 78, 38), (box.x, box.bottom - m(5), box.w, m(5)),
                     border_bottom_left_radius=rad, border_bottom_right_radius=rad)
    # defined edges: dark keyline under bright top-left bevel
    pygame.draw.rect(surf, (40, 22, 8), box, width=max(1, m(1.4)),
                     border_radius=rad)
    bevel_rim(surf, box, rad, (40, 22, 8), (255, 226, 160, 220), w=max(1, m(1.2)))

    # ── glass cabochon stall window holding the preview thumbnail ──
    disc_r = int(min(bw, bh) * 0.40)
    dcx = cx
    dcy = box.y + int(bh * 0.40)
    pal = MYSTERY if hero else RARITY["legendary"]
    soft_glow(surf, dcx, dcy, disc_r + m(3), pal["glow"], 40, layers=8)
    # a touch airier glass so the small previews read inside the dome.
    cabochon(surf, dcx, dcy, disc_r, glass_lo=(46, 40, 70), glass_hi=(16, 14, 32),
             ring=pal["gem"], ring_a=55)
    thumb = stall_thumb(stall, int(disc_r * 1.5))
    if thumb.get_width() > 2:
        tr = thumb.get_rect(center=(dcx, dcy))
        # top-left rim light so the preview reads as the lit hero under glass
        sil = thumb.copy()
        sil.fill((255, 248, 220, 255), special_flags=pygame.BLEND_RGBA_MULT)
        off = max(1, m(0.6))
        cut = thumb.copy()
        cut.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
        rim = pygame.Surface(thumb.get_size(), pygame.SRCALPHA)
        rim.blit(sil, (-off, -off))
        rim.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        rim.set_alpha(170)
        surf.blit(rim, tr.topleft, special_flags=pygame.BLEND_ADD)
        surf.blit(thumb, tr.topleft)
    cabochon_glass(surf, dcx, dcy, disc_r, tint=pal["gem"])
    if hero:
        # PARCELS hero: a bold mystery '?' set over the parcel preview glass.
        _qmark(surf, dcx, dcy, disc_r)

    # ── awning category sign across the basket front ──
    _awning_label(surf, label, cx, box.bottom - int(bh * 0.20), bw, hero)


def _qmark(surf, cx, cy, r):
    """A glowing red mystery '?' for the PARCELS hero, drawn from the stroke +
    glow primitives (no raster asset)."""
    f = font(int(r / SS * 1.5))
    base = _stamp_bold(_glyph_base("?", f, 0), m(1.4))
    rr = base.get_rect(center=(cx, cy))
    out = base.copy()
    out.fill((120, 18, 22, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for ang in range(0, 360, 30):
        dx = int(round(m(1.4) * math.cos(math.radians(ang))))
        dy = int(round(m(1.4) * math.sin(math.radians(ang))))
        surf.blit(out, (rr.x + dx, rr.y + dy))
    body = base.copy()
    body.fill((255, 226, 180, 255), special_flags=pygame.BLEND_RGBA_MULT)
    soft_glow(surf, cx, cy, int(r * 0.5), (255, 90, 80), 90, layers=7)
    surf.blit(body, rr.topleft)


def _awning_label(surf, txt, cx, cy, bw, hero=False):
    """A scalloped awning sign carrying the bold gold-keyline category label —
    the stall's shop sign, with defined edges (dark keyline under bright bevel)."""
    f = font(11)
    tw = _glyph_base(txt, f, m(0.6)).get_width()
    pad = m(11)
    w = min(int(bw * 1.06), tw + pad * 2)
    h = m(20)
    r = pygame.Rect(int(cx - w / 2), int(cy - h / 2), w, h)
    rad = m(5)
    drop_shadow(surf, r, rad, blur=m(3), alpha=110, dy=m(2))
    # red+cream striped awning body
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    stripe_w = m(8)
    for sx in range(0, w, stripe_w):
        on = (sx // stripe_w) % 2 == 0
        c = (216, 70, 64) if (on ^ hero) else (250, 238, 214)
        pygame.draw.rect(body, c, (sx, 0, stripe_w, h))
    bm = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(bm, (255, 255, 255, 255), bm.get_rect(), border_radius=rad)
    body.blit(bm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, r.topleft)
    top_sheen(surf, r, rad, m(8), peak=54)
    # scalloped lower edge
    sc = m(4)
    n = max(3, w // (sc * 2))
    for i in range(n):
        ax = r.x + int(w * i / n)
        bx = r.x + int(w * (i + 1) / n)
        mx = (ax + bx) // 2
        pygame.draw.polygon(surf, (150, 36, 36),
                            [(ax, r.bottom), (bx, r.bottom), (mx, r.bottom + sc)])
    pygame.draw.rect(surf, (40, 14, 12), r, width=max(1, m(1.4)),
                     border_radius=rad)
    bevel_rim(surf, r, rad, (40, 14, 12), (255, 230, 180, 220), w=max(1, m(1.0)))
    # bold gold-keyline label
    gradient_text(surf, txt, f, r.center, (255, 248, 214), (244, 188, 84),
                  tracking=m(0.6), weight=m(1.0), keyline=(56, 22, 8), kw=m(1.0),
                  shadow=False)


def draw_caravan_balloon(surf, cx, cy, scale, label, stall, hero=False):
    """One full caravan unit: striped envelope + ropes + wicker stall + sign."""
    rw = int(150 * scale * SS / 1.0 / SS * SS)  # keep readable; logical width
    rw = m(int(96 * scale))
    rh = m(int(104 * scale))
    mouth_y, mw = draw_balloon(surf, cx, cy, rw, rh, hero=hero)
    bw = m(int(66 * scale))
    bh = m(int(50 * scale))
    gap = m(int(16 * scale))
    top_y = mouth_y + gap
    draw_basket(surf, cx, top_y, bw, bh, mouth_y, mw, label, stall, hero=hero)


# =============================================================================
# Pip — the flying caravan-master vendor
# =============================================================================
def draw_pip(surf, cx, cy, scale):
    """Pip the macaw flies between the stalls as the caravan-master, with a soft
    warm aura and a coin he's ferrying. Drawn clear of every label."""
    src = parrot.get_parrot(1, 0.0)
    bb = src.get_bounding_rect()
    if bb.width > 0:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    box = m(int(58 * scale))
    s = box / max(sw, sh)
    img = pygame.transform.smoothscale(src, (max(1, int(sw * s)),
                                             max(1, int(sh * s))))
    soft_glow(surf, cx, cy, int(box * 0.7), (255, 224, 170), 60, layers=9)
    r = img.get_rect(center=(cx, cy))
    # contact/cast shadow drop
    sh_img = img.copy()
    sh_img.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sh_img.set_alpha(70)
    surf.blit(sh_img, (r.x + m(3), r.y + m(5)))
    surf.blit(img, r.topleft)
    # a coin he's ferrying, lower-right of his beak, clear of labels
    coin_glyph(surf, r.right - m(2), r.bottom - m(4), m(8))


# =============================================================================
# Header
# =============================================================================
def draw_header(surf):
    # darkening band behind the title lane for legibility over the bright apex.
    band = pygame.Surface((DW, m(108)), pygame.SRCALPHA)
    for y in range(m(108)):
        a = int(110 * (1 - y / m(108)) ** 1.2)
        pygame.draw.line(band, (16, 12, 40, a), (0, y), (DW, y))
    surf.blit(band, (0, 0))
    pygame.draw.rect(surf, (*GOLD, 60), (m(3), m(3), DW - m(6), DH - m(6)),
                     width=max(1, m(1)), border_radius=m(12))
    title_wordmark(surf, "STORE", (DW // 2, m(28)), 31, tracking=m(4))
    _balance_capsule(surf, DW // 2, m(72))


def _balance_capsule(surf, cx, y):
    """Recessed gold balance capsule with the REAL in-game coin + gradient-gold
    number + a 'TAP A STALL' hint beneath. Defined edges throughout."""
    val = f"{BALANCE:,}"
    vf = font(23)
    vw = _glyph_base(val, vf, 0).get_width() + m(2)
    coin_d, gapc, padl, padr = m(26), m(16), m(14), m(20)
    w = padl + coin_d + gapc + vw + padr
    h = m(42)
    cap = pygame.Rect(cx - w // 2, y - h // 2, w, h)
    drop_shadow(surf, cap, h // 2, blur=m(6), alpha=130, dy=m(3))
    surf.blit(vgrad(cap.w, cap.h, h // 2, (58, 42, 22), (22, 15, 8), 255,
                    gamma=1.1), cap.topleft)
    top_sheen(surf, cap, h // 2, m(15), peak=50)
    pygame.draw.rect(surf, (0, 0, 0, 200), cap, width=max(1, m(1.8)),
                     border_radius=h // 2)
    bevel_rim(surf, cap, h // 2, lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD_PALE, 240), w=max(1, m(1.8)))
    x = cap.x + padl
    soft_glow(surf, x + coin_d // 2, y, int(coin_d * 0.40), (255, 206, 92), 42,
              layers=6)
    coin_glyph(surf, x + coin_d // 2, y, coin_d // 2)
    x += coin_d + gapc
    gradient_text(surf, val, vf, (x + vw // 2, y), GOLD_A_TOP, GOLD_A_BOT,
                  weight=m(1.0), keyline=(96, 56, 12), kw=m(1.2), shadow=True)
    # the wayfinding hint
    plain_text(surf, "TAP A STALL", font(11), (cx, y + h // 2 + m(13)),
               (255, 236, 196), shadow_a=150, tracking=m(2), weight=m(0.8),
               keyline=(20, 14, 8), kw=m(0.8))


# =============================================================================
# Compose
# =============================================================================
# Staggered zig-zag column so all 7 read at 360px, none overlap, all tap targets
# >=88px short-axis. Author in logical px; flow through m(). PARCELS is the
# bottom/foreground hero anchor (largest, hottest).
#  layout: (logical cx, logical cy, scale, stall index)
LAYOUT = [
    (96,  164, 0.66, 0),   # COSTUMES  (upper-left, far/small)
    (262, 176, 0.68, 1),   # PARROTS   (upper-right)
    (92,  300, 0.74, 2),   # ANIMALS   (mid-left)
    (266, 312, 0.76, 3),   # SHOES     (mid-right)
    (94,  440, 0.78, 4),   # HATS      (lower-left, nearer)
    (268, 450, 0.80, 5),   # SHADES    (lower-right)
    (180, 506, 0.90, 6),   # PARCELS   (bottom-center hero, largest/foreground)
]


def render_device():
    surf = pygame.Surface((DW, DH))
    draw_bg(surf)

    # pennant swags stringing the caravan together (drawn behind the balloons).
    swags = [(0, 1), (2, 3), (4, 5)]
    for ai, bi in swags:
        ax, ay, asc, _ = LAYOUT[ai]
        bx, by, bsc, _ = LAYOUT[bi]
        draw_pennant_string(surf, m(ax), m(ay - 56 * asc),
                            m(bx), m(by - 56 * bsc), n=5)

    # drifting coins threading the caravan (depth sparkle between units).
    rnd = random.Random(9)
    coin_spots = [(186, 232), (78, 350), (300, 372), (170, 490), (250, 540),
                  (96, 200)]
    for cxL, cyL in coin_spots:
        coin_glyph(surf, m(cxL), m(cyL), m(rnd.uniform(5.5, 7.5)))

    draw_header(surf)

    # draw caravan back-to-front (top/far units first so nearer ones overlap
    # cleanly; PARCELS hero last on top).
    for cxL, cyL, sc, si in LAYOUT:
        stall = STALLS[si]
        draw_caravan_balloon(surf, m(cxL), m(cyL), sc, stall["label"], stall,
                             hero=stall.get("hero", False))

    # Pip flies in the open central lane between the stalls, clear of labels.
    draw_pip(surf, m(182), m(372), 1.0)

    return surf


def downscale(device_surf, scale=1):
    return pygame.transform.smoothscale(device_surf, (W * scale, H * scale))


def main():
    _build_stars()
    dev = render_device()
    pygame.image.save(downscale(dev, 1), os.path.join(_HERE, "round_1.png"))
    pygame.image.save(downscale(dev, 2), os.path.join(_HERE, "round_1@2x.png"))
    print("SS =", SS, "device =", DW, "x", DH)
    print("saved round_1.png (360x640) + round_1@2x.png (720x1280)")


if __name__ == "__main__":
    main()
