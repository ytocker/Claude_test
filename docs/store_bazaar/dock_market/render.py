"""
STORE BAZAAR — concept #4: GOLDEN-HOUR DOCK MARKET (selection-sheet prototype).

A tropical harbor market at golden hour. Seven category stalls line a wooden
boardwalk that runs in two tiers — a larger front row and a smaller back jetty —
split by a strip of sun-glittering gold water, with palms framing the edges,
distant moored boats for depth, and Pip the scarlet macaw selling from a
dockside cart. PARCELS is the glowing-red mystery hero crate stacked on a moored
boat. The low golden-hour sun rakes light in from the top-left.

DOCS-ONLY mockup. Not wired into the game. The whole frame is authored
resolution-independently at SS=4 (1440x2560 device) and ONE smoothscale brings
it down to 360x640 — the downscale is what turns oversized geometry into crisp
anti-aliased edges, exactly like the constellation hi-res store sheet whose
primitive kit this reuses.

Round 2 polish: planks read as solid lit wood (top-left light, plank seams, AO
under every stall) instead of a flat disc of raking light; the water is a sparse
tasteful specular shimmer, not noise; the sky eases UP from the warm golden-hour
low (255,196,112) to the indigo+gold jewel-store nebula near the top so entering
a stall dissolves cohesively; previews are letterboxed inside the dome so
aspect-extreme items (flip-flops, party hat) never clip; SHADES falls back to a
real sunglasses item icon instead of a bare parrot.

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
_KIT = os.path.join(_ROOT, "docs", "store_redesign", "constellation_hi")
for p in (_ROOT, _KIT):
    if p not in sys.path:
        sys.path.insert(0, p)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from game.draw import (lerp_color, NEAR_BLACK, WHITE,
                       get_sky_surface_biome, draw_mountains, draw_cloud)
from game import biome
from game import parrot
from game import store_catalog

# Reuse the constellation hi-res primitive kit verbatim — the SAME gold/gem UI
# so the bazaar leads seamlessly into the jewel store.
from render_hi import (
    m, mf, font, SS, DW, DH,
    vgrad, vgrad_stops, gold_a_fill, soft_glow, drop_shadow,
    gradient_text, plain_text, facet_gem, cabochon, cabochon_glass,
    coin_glyph, bevel_rim, top_sheen, gold_rule, title_wordmark, downscale,
    GOLD, GOLD_PALE, GOLD_DEEP, RARITY, MYSTERY,
    GOLD_A_STOPS, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, GOLD_A_NUM,
    gloss_sweep, contact_shadow, _glyph_base, _stamp_bold,
)


# ── golden-hour palette (the real biome keyframe) ─────────────────────────────
GH_PHASE = 0.23125                       # the GOLDEN HOUR biome keyframe exactly
PAL = biome.palette_for_phase(GH_PHASE)
PHASE_BUCKET = biome.phase_bucket(GH_PHASE)

# Warm golden-hour anchors. The signature low is (255,196,112) per the brief;
# the upper frame eases to the constellation indigo+gold nebula so the bazaar
# dissolves cohesively into the jewel store.
GH_LOW = (255, 196, 112)                 # the warm golden-hour low (brief anchor)
SKY_HI = PAL["sky_bot"]                   # (255,210,160) peachy upper
HORIZON = PAL["horizon"]                  # (255,220,140) hot horizon band
NEBULA_TOP = (16, 16, 52)                # indigo jewel-store ceiling
NEBULA_MID = (40, 30, 84)                # violet bloom toward mid sky
NEBULA_GLOW = (96, 78, 190)              # the constellation central bloom

WATER_GOLD = (246, 192, 96)             # gold water body
WATER_HOT = (255, 232, 168)             # hot far-shore highlight
WATER_DEEP = (146, 92, 36)              # shaded trough between glints
AWNING_RED = (170, 34, 18)              # macaw-red awning
AWNING_RED_HI = (218, 82, 46)
CREAM = (248, 240, 218)
WOOD_HI = (212, 156, 96)                 # sunlit plank crown
WOOD_MID = (162, 110, 64)
WOOD_DK = (92, 58, 32)
WOOD_SEAM = (58, 36, 18)
PALM_TRUNK = (120, 82, 48)
PALM_TRUNK_HI = (176, 128, 78)
FROND_DK = (36, 90, 54)
FROND_MID = (64, 136, 72)
FROND_HI = (134, 198, 98)
# the night/jewel accent that seeds the dissolve into the constellation store
JEWEL_INDIGO = (26, 22, 66)
JEWEL_INDIGO_DEEP = (10, 10, 36)
# the glowing-red mystery accent (the constellation store's MYSTERY hue)
MYST_RED = MYSTERY["gem"]                 # (244, 96, 96)
MYST_GLOW = MYSTERY["glow"]               # (236, 64, 64)
MYST_DEEP = MYSTERY["deep"]               # (120, 22, 26)

BALANCE = 14250

# top-left sun direction (everything lit from up-left). Logical sun anchor.
SUN_X = int(DW * 0.20)


# ── stall manifest: 7 categories -> group key + preview id ────────────────────
STALL_GROUPS = [
    ("COSTUMES", "costume"),
    ("PARROTS",  "parrot"),
    ("ANIMALS",  "animal"),
    ("SHOES",    "shoes"),
    ("HATS",     "hats"),
    ("SHADES",   "shades"),
    ("PARCELS",  "parcels"),
]


def _preview_id(group):
    """The representative item for a stall. For SHADES the catalog's first entry
    is `skin_shades_none` (a bare parrot, no glasses) which has no icon and reads
    as 'no item' — so fall back to the first shades entry that DOES carry a real
    icon, giving a clear sunglasses preview."""
    ids = store_catalog.ids_of_group(group)
    if not ids:
        return None
    sid = ids[0]
    if group == "shades" and parrot.get_skin_icon(sid) is None:
        for alt in ids[1:]:
            if parrot.get_skin_icon(alt) is not None:
                return alt
    return sid


def _fit_box(src, box_px, scale=1.0):
    """Bounding-box `src` and fit its LONGER side to box_px*scale (letterboxed,
    aspect kept) — so aspect-extreme items stay contained, never clipped."""
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    s = box_px * scale / max(sw, sh)
    return pygame.transform.smoothscale(
        src, (max(1, int(sw * s)), max(1, int(sh * s))))


def _preview_icon(sid, box_px):
    """Default stall thumbnail: the item icon (or skin frame), fit + contrast-
    lifted so it reads as the lit hero under the awning."""
    src = parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)
    lift = _fit_box(src, box_px).copy()
    lift.fill((30, 30, 30, 0), special_flags=pygame.BLEND_RGB_ADD)
    return lift


def _preview_crossed_shoes(sid, box_px):
    """SHOES reads as a thin beige stick when shown flat: build a clear PAIR by
    angling one flip-flop 3/4 and crossing a mirrored second behind it, scaled up
    so it reads unmistakably as footwear."""
    icon = (parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0))
    one = _fit_box(icon, int(box_px * 0.78))
    a = pygame.transform.rotate(one, 26)             # front flop, tilted 3/4
    b = pygame.transform.rotate(pygame.transform.flip(one, True, False), -22)
    out = pygame.Surface((box_px, box_px), pygame.SRCALPHA)
    # back flop offset up-left, front flop down-right => a crossed pair
    out.blit(b, b.get_rect(center=(int(box_px * 0.42), int(box_px * 0.40))))
    out.blit(a, a.get_rect(center=(int(box_px * 0.58), int(box_px * 0.58))))
    out.fill((30, 30, 30, 0), special_flags=pygame.BLEND_RGB_ADD)
    return out


def _preview_bust(sid, box_px, head_frac=0.62):
    """PARROTS reads as a clean head-ON bust: crop the upper `head_frac` of the
    skin frame's bounding box (the head + chest) and scale it up so the macaw's
    face — not its whole flying body — fills the dome (distinct from COSTUMES)."""
    src = parrot.get_skin_frame(sid, 1, 0.0)
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        # keep the TOP portion (head + breast); the parrot frame faces right.
        crop = pygame.Rect(bb.x, bb.y, bb.width, int(bb.height * head_frac))
        src = src.subsurface(crop).copy()
    lift = _fit_box(src, box_px, scale=1.12).copy()
    lift.fill((34, 34, 34, 0), special_flags=pygame.BLEND_RGB_ADD)
    return lift


def _rim_lit(img, color=(255, 246, 214), alpha=175):
    """Crisp top-left contour highlight so a thumbnail pops off the dark dome."""
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


# =============================================================================
# Backdrop — indigo->gold sky, low sun, mountains, clouds, glitter water
# =============================================================================
WATER_TOP = m(222)                        # logical y where the water band begins
WATER_BOT = m(283)                        # ...and ends (the near-deck waterline)


def draw_sky(surf):
    """The golden-hour harbor sky: warm at the low horizon (the brief's
    (255,196,112)) easing UP to the constellation indigo+gold nebula so entering
    a stall dissolves into the jewel store. The biome golden-hour sky cache seeds
    the warm lower band; an authored indigo gradient + a soft violet bloom take
    over the upper frame; the low sun blooms top-left."""
    horizon_y = WATER_TOP
    # authored sky: a single smooth ramp from the indigo jewel-store ceiling down
    # through a warm dusk into the golden-hour horizon — tuned so there is no
    # mauve mid-band and no violet ring (the dissolve into the night souk is the
    # ceiling colour, the market sits in warm gold).
    sky = vgrad_stops(DW, horizon_y, 0,
                      [(0.00, NEBULA_TOP),
                       (0.22, (44, 32, 86)),
                       (0.44, (108, 70, 92)),
                       (0.62, (196, 120, 92)),
                       (0.80, (248, 176, 110)),
                       (1.00, GH_LOW)], 255, gamma=1.02)
    surf.blit(sky, (0, 0))
    # the constellation central violet bloom near the top so the jewel-store
    # nebula is already present above the market line — kept restrained + high so
    # it never rings into a rainbow halo behind the wordmark.
    soft_glow(surf, int(DW * 0.5), int(horizon_y * 0.16), m(180),
              NEBULA_GLOW, 26, layers=14)
    # a sparse high starfield in the indigo ceiling only (fades out before the
    # warm band) — the jewel-store sky bleeding through the dusk.
    _draw_high_stars(surf, horizon_y)

    # the low golden-hour sun, raking from the upper-left. Dimmed + shrunk +
    # biased UP and LEFT (the rake direction) so it never blows to white behind
    # the capsule — the STORE title gold must own the brightest value on screen.
    sun_x = SUN_X
    sun_y = int(horizon_y * 0.36)
    soft_glow(surf, sun_x, sun_y, m(50), (250, 188, 108), 26, layers=14)
    soft_glow(surf, sun_x, sun_y, m(20), (255, 214, 150), 48, layers=10)
    disc = pygame.Surface((m(40), m(40)), pygame.SRCALPHA)
    pygame.draw.circle(disc, (255, 226, 178, 215), (m(20), m(20)), m(14))
    surf.blit(disc, (sun_x - m(20), sun_y - m(20)))

    # distant tropical islands in the warm haze — drawn onto a SHORT strip just
    # above the waterline + clipped, so they read as low hazy islands instead of
    # tall peaks whose pale auto-tinted back layer washes the sky white. Warm
    # silhouette colours keep them in golden-hour key.
    isl_h = m(46)
    isl = pygame.Surface((DW, isl_h), pygame.SRCALPHA)
    draw_mountains(isl, scroll=140, ground_y=isl_h, w=DW,
                   far_color=lerp_color(PAL["mtn_far"], (150, 96, 70), 0.5),
                   near_color=lerp_color(PAL["mtn_near"], (120, 74, 52), 0.45))
    isl.set_alpha(200)
    surf.blit(isl, (0, horizon_y - isl_h))

    # two small clouds catching the low light, pushed to the upper CORNERS (clear
    # of the wordmark) + dimmed so they read as distant haze, not a white bloom
    # behind the title.
    cl = pygame.Surface((DW, horizon_y), pygame.SRCALPHA)
    for x, y, sc, v in ((m(40), m(116), SS * 0.5, 2),
                        (m(316), m(96), SS * 0.42, 3)):
        draw_cloud(cl, x, y, scale=sc, variant=v)
    cl.set_alpha(120)
    surf.blit(cl, (0, 0))


def _draw_high_stars(surf, horizon_y):
    """A sparse starfield confined to the indigo ceiling, alpha-faded to zero
    before the warm horizon band — the jewel-store night bleeding through dusk."""
    rng = random.Random(91)
    fade_y = int(horizon_y * 0.42)            # stars gone by here
    for _ in range(70):
        x = rng.randint(0, DW)
        y = rng.randint(0, fade_y)
        f = 1.0 - y / max(1, fade_y)
        a = int(rng.randint(40, 150) * f)
        if a <= 0:
            continue
        r = max(1, m(rng.uniform(0.4, 1.2)))
        tint = rng.choice([(255, 252, 240), (214, 222, 255), (255, 238, 206)])
        pygame.draw.circle(surf, (*tint, a), (x, y), r)


def draw_water(surf):
    """The glittering gold harbor band splitting the two tiers. The SIGNATURE is
    a SPARSE specular shimmer: a hot reflection column straight under the sun, a
    few rows of clean horizontal gold dashes brightest in that column and
    thinning to the dark flanks, plus moored-boat + jetty-post reflections.
    Sparse + large so it reads premium, not noisy, at 360px."""
    band_h = WATER_BOT - WATER_TOP
    # base water gradient: hot gold at the far shore deepening toward the viewer
    water = vgrad_stops(DW, band_h, 0,
                        [(0.00, WATER_HOT),
                         (0.30, WATER_GOLD),
                         (1.00, WATER_DEEP)], 255, gamma=1.06)
    surf.blit(water, (0, WATER_TOP))

    # the reflection path straight under the sun (classic sun-on-water shimmer).
    # Authored as a SOFT warm vertical smear (a feathered amber column, brightest
    # on the sun's x, fading to the flanks) — NO hatching, NO white — so it reads
    # as a gentle glow path the bright dashes then sparkle along.
    # built once as a single feathered surface (a soft bell across x, fading down)
    # then set_alpha + NORMAL blit — additive stacking of per-row lines whitened
    # into a hard block, so this is one translucent overlay instead.
    col_w = m(84)
    colsurf = pygame.Surface((col_w, band_h), pygame.SRCALPHA)
    for sx in range(col_w):
        hx = abs(sx - col_w / 2) / (col_w / 2)
        edge = max(0.0, (1 - hx ** 2)) ** 1.6
        for yy in range(band_h):
            fy = 1.0 - yy / band_h
            a = int(96 * edge * (0.25 + 0.75 * fy))
            if a > 0:
                colsurf.set_at((sx, yy),
                               (*lerp_color(WATER_GOLD, (255, 236, 184), 0.7), a))
    surf.blit(colsurf, (SUN_X - col_w // 2, WATER_TOP))

    # SIGNATURE specular glitter — sparse, large, brightest in the sun column,
    # thinning toward the dark flanks. Seeded so the layout is stable. Authored
    # as clean horizontal dashes (+ a hot 4-point star on the very brightest) so
    # it reads as raked sun-glitter, never blobby noise.
    rng = random.Random(404)
    rows = [WATER_TOP + int(band_h * f) for f in (0.22, 0.44, 0.66, 0.86)]
    for ri, ry in enumerate(rows):
        depth = (ry - WATER_TOP) / max(1, band_h)
        count = 5 + ri                              # more glints in the near rows
        for c in range(count):
            x = int((c + rng.uniform(0.25, 0.75)) * DW / count)
            x += int(rng.uniform(-m(6), m(6)))
            x = max(m(10), min(DW - m(10), x))
            dist_sun = abs(x - SUN_X) / (DW * 0.5)
            bright = max(0.10, 1.0 - dist_sun)
            ln = m(4.0 + depth * 9.0) * rng.uniform(0.85, 1.2)
            a = int(238 * bright)
            col = lerp_color((255, 228, 156), (255, 252, 236), bright)
            y = ry + int(rng.uniform(-m(2), m(2)))
            # NO underglow — the elongated additive underglows clustered near the
            # sun column into a pale block. Clean dashes alone read as shimmer.
            dash = pygame.Surface((int(ln * 2) + m(2), m(3)), pygame.SRCALPHA)
            pygame.draw.line(dash, (*col, a), (0, m(1)), (int(ln * 2), m(1)),
                             max(1, m(1.6)))
            surf.blit(dash, (x - int(ln), y - m(1)), special_flags=pygame.BLEND_ADD)
            # a hot 4-point star kiss on the very brightest glints (the sparkle)
            if bright > 0.74:
                L = int(ln * 0.9)
                pygame.draw.line(surf, (255, 255, 248, 210), (x - L, y), (x + L, y),
                                 max(1, m(0.8)))
                pygame.draw.line(surf, (255, 255, 248, 165), (x, y - m(3)),
                                 (x, y + m(3)), max(1, m(0.8)))

    # ── a CLEAR dark waterline edge top AND bottom so the channel-of-water idea
    # lands (the brief's framed strip). Top: a dark shoreline shadow under the
    # back jetty, then a hot sunlit lip. Bottom: a dark contact shadow where the
    # near deck meets the water. ──────────────────────────────────────────────
    # far (top) shoreline: a dark band, then a hot sunlit lip on top of it
    pygame.draw.line(surf, (84, 50, 24), (0, WATER_TOP - m(1)),
                     (DW, WATER_TOP - m(1)), max(1, m(2.2)))
    pygame.draw.line(surf, (255, 248, 208, 240), (0, WATER_TOP + m(1)),
                     (DW, WATER_TOP + m(1)), max(1, m(1.8)))
    # near (bottom) waterline: a firm dark edge so the strip closes cleanly
    pygame.draw.line(surf, (62, 36, 16), (0, WATER_BOT - m(1)),
                     (DW, WATER_BOT - m(1)), max(1, m(2.4)))
    pygame.draw.line(surf, (255, 222, 150, 110), (0, WATER_BOT - m(3)),
                     (DW, WATER_BOT - m(3)), max(1, m(1.0)))


def draw_distant_boats(surf):
    """A couple of small moored boats on the far water for depth — simple hull +
    mast silhouettes catching the low sun, with broken reflections. Sparse so
    they add depth without clutter. Drawn on the water band, behind the front
    tier. The right-hand boat is the PARCELS mystery boat (drawn separately)."""
    band_h = WATER_BOT - WATER_TOP
    # READABLE dark silhouettes against the gold water: a deep umber hull + a
    # proper triangular sail, kept clear of the bright sun column (right of it)
    # so they read as little anchored boats, not blobs in the glitter.
    for bx, scale in ((int(DW * 0.46), 0.92), (int(DW * 0.66), 0.66)):
        by = WATER_TOP + int(band_h * 0.30)
        _moored_boat(surf, bx, by, scale, hull=(78, 46, 24),
                     hull_hi=(150, 100, 56), sail=(96, 58, 34))


def _moored_boat(surf, cx, wl_y, scale, hull, hull_hi, sail=None,
                 reflect=True):
    """A small moored boat: a curved hull sitting on the waterline `wl_y`, a thin
    mast, an optional triangular sail, and (on water) a broken reflection."""
    cx, wl_y = int(cx), int(wl_y)
    hw = int(m(34) * scale)
    hh = int(m(13) * scale)
    # hull as a filled lens (two arcs)
    hull_poly = [(cx - hw, wl_y)]
    for i in range(13):
        t = i / 12
        hx = int(cx - hw + 2 * hw * t)
        hy = int(wl_y + hh * math.sin(math.pi * t) * 0.9)
        hull_poly.append((hx, hy))
    hull_poly.append((cx + hw, wl_y))
    pygame.draw.polygon(surf, hull, hull_poly)
    # lit upper deck line (top-left light) + a warm gunwale strip
    pygame.draw.line(surf, hull_hi, (cx - hw, wl_y), (cx + hw, wl_y),
                     max(1, int(m(2.0) * scale)))
    pygame.draw.line(surf, lerp_color(hull_hi, WHITE, 0.3),
                     (int(cx - hw * 0.7), wl_y - m(1)),
                     (int(cx + hw * 0.2), wl_y - m(1)), max(1, m(1.0)))
    # mast
    mast_h = int(m(30) * scale)
    mast_x = int(cx - hw * 0.1)
    pygame.draw.line(surf, (74, 50, 28), (mast_x, wl_y),
                     (mast_x, wl_y - mast_h), max(1, int(m(1.6) * scale)))
    if sail is not None:
        # a proper triangular silhouette sail so the boat READS as a boat against
        # the gold water (dark canvas, a warm sun-kiss on its lit mast edge).
        sailp = [(mast_x + m(1), wl_y - mast_h),
                 (int(mast_x + hw * 0.62), wl_y - m(3)),
                 (mast_x + m(1), wl_y - m(3))]
        pygame.draw.polygon(surf, sail, sailp)
        # warm sun-kiss on the sail's lit (mast) edge
        pygame.draw.line(surf, (210, 150, 96), sailp[0], sailp[2],
                         max(1, m(1.2)))
    # broken reflection under the hull — kept dim + warm so it reads as a few
    # ripple dashes, never a muddy smear.
    if not reflect:
        return
    for k in range(3):
        ry = int(wl_y + m(3) + k * m(3) * scale)
        jit = int(math.sin(k * 1.7 + cx) * m(2))
        a = int(70 * (1 - k / 3))
        pygame.draw.line(surf, (88, 54, 26, a), (int(cx - hw * 0.5) + jit, ry),
                         (int(cx + hw * 0.4) + jit, ry), max(1, int(m(1.4) * scale)))


# =============================================================================
# Boardwalk decks (the two tiers) + palms + dock posts
# =============================================================================
def _plank_deck(surf, rect, plank_h, light, mid, dark, perspective=True):
    """A wooden boardwalk deck: horizontal planks receding in perspective with a
    lit top crown (top-left light), dark seams, a thin lit lip below each seam,
    and a few grain streaks. Authored oversized so seams downscale to crisp
    hairlines. Light biased toward the left (the sun side)."""
    # base body: a left-lit gradient (warmer/brighter at the sunlit left)
    deck = vgrad_stops(rect.w, rect.h, 0,
                       [(0.0, light), (0.5, mid), (1.0, dark)], 255, gamma=1.06)
    # rake a left->right horizontal darkening so the deck is lit from the sun side
    shade = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for x in range(0, rect.w, max(1, m(2))):
        a = int(60 * (x / max(1, rect.w)) ** 1.2)
        pygame.draw.line(shade, (40, 24, 10, a), (x, 0), (x, rect.h), max(1, m(2)))
    deck.blit(shade, (0, 0))
    surf.blit(deck, rect.topleft)

    rng = random.Random(7 + rect.y)
    y = rect.y
    while y < rect.bottom:
        f = (y - rect.y) / max(1, rect.h)
        ph = int(plank_h * (0.7 + f * 0.95)) if perspective else plank_h
        # dark seam groove
        pygame.draw.line(surf, WOOD_SEAM, (rect.x, y), (rect.right, y),
                         max(1, m(1.4)))
        # a thin lit lip just below the seam (the plank crown catching the sun)
        pygame.draw.line(surf, (*lerp_color(light, WHITE, 0.35), 190),
                         (rect.x, y + max(1, m(1.0))),
                         (rect.right, y + max(1, m(1.0))), max(1, m(1.0)))
        # grain streaks
        for _ in range(3):
            gx = rng.randint(rect.x, rect.right - m(20))
            gw = rng.randint(m(18), m(64))
            ga = rng.randint(22, 56)
            pygame.draw.line(surf, (60, 36, 18, ga),
                             (gx, y + ph // 2), (gx + gw, y + ph // 2),
                             max(1, m(0.8)))
        y += ph
    # staggered board butt-joints (vertical seams) for a real deck read
    rng2 = random.Random(99 + rect.y)
    for _ in range(9):
        vx = rng2.randint(rect.x + m(20), rect.right - m(20))
        vy = rng2.randint(rect.y, rect.bottom - m(10))
        pygame.draw.line(surf, (50, 30, 16, 130), (vx, vy), (vx, vy + m(16)),
                         max(1, m(0.9)))
    # lit front crown of the deck
    pygame.draw.line(surf, (*lerp_color(light, WHITE, 0.45), 230),
                     (rect.x, rect.y), (rect.right, rect.y), max(1, m(1.6)))


def draw_back_jetty(surf):
    """The upper boardwalk tier (back jetty) the 3 back stalls sit on — a thin
    lit deck just behind the water with support posts dropping into the harbor.
    A cooler contact-AO shelf is laid just ABOVE + behind it so the whole tier
    reads as further back + in lower light, not floating in the warm haze."""
    deck = pygame.Rect(m(14), m(206), DW - m(28), m(16))
    # cool contact-AO shelf BEHIND the jetty: a soft cool-indigo band the back
    # stalls' feet sit against, separating the tier from the warm horizon haze.
    shelf = pygame.Surface((DW, m(30)), pygame.SRCALPHA)
    for yy in range(m(30)):
        f = yy / m(30)
        a = int(96 * (f ** 1.3))                     # darkest right at the deck
        pygame.draw.line(shelf, (40, 36, 70, a), (0, yy), (DW, yy))
    surf.blit(shelf, (0, deck.y - m(28)))
    _plank_deck(surf, deck, m(7), WOOD_HI, WOOD_MID, WOOD_DK, perspective=False)
    # a cool shadow directly under the jetty front edge (where it meets the lip)
    underao = pygame.Surface((DW, m(8)), pygame.SRCALPHA)
    for yy in range(m(8)):
        underao.fill((28, 26, 52, int(120 * (1 - yy / m(8)))), (0, yy, DW, 1))
    surf.blit(underao, (0, deck.bottom))
    # dark contact line under the jetty (where it meets the water lip)
    pygame.draw.line(surf, (44, 26, 12), (deck.x, deck.bottom),
                     (deck.right, deck.bottom), max(1, m(1.6)))
    # support posts dropping into the harbor with broken reflections
    for px in range(m(40), DW - m(30), m(58)):
        pygame.draw.line(surf, (80, 50, 28), (px, deck.bottom - m(2)),
                         (px, deck.bottom + m(18)), max(1, m(3.0)))
        pygame.draw.line(surf, (*PALM_TRUNK_HI, 150), (px - m(1), deck.bottom - m(2)),
                         (px - m(1), deck.bottom + m(12)), max(1, m(1.0)))
        for ry in range(deck.bottom + m(18), WATER_BOT - m(4), m(4)):
            jit = int(math.sin(ry * 0.6 + px) * m(1.4))
            pygame.draw.line(surf, (60, 36, 18, 90), (px + jit, ry),
                             (px + jit, ry + m(2)), max(1, m(2.2)))


def draw_front_boardwalk(surf):
    """The lower, larger boardwalk tier the 4 front stalls + Pip's cart sit on —
    fills the bottom of the frame and reads as the floor the player stands on.
    A warm sun-rake from the upper-left tints the LEFT planks (sun side) — kept
    as a soft directional warm wash, NOT a circular spotlight disc."""
    deck = pygame.Rect(0, WATER_BOT, DW, DH - WATER_BOT)
    _plank_deck(surf, deck, m(10), lerp_color(WOOD_HI, (236, 198, 150), 0.32),
                WOOD_MID, WOOD_DK)
    # the contact shadow where the front deck meets the water (AO at the seam)
    seam = pygame.Surface((DW, m(10)), pygame.SRCALPHA)
    for yy in range(m(10)):
        seam.fill((30, 16, 6, int(150 * (1 - yy / m(10)))), (0, yy, DW, 1))
    surf.blit(seam, (0, WATER_BOT))
    # directional warm sun-rake biased to the upper-LEFT (sun side) — a soft
    # gradient wedge, feathered, so the near deck warms toward the sun without a
    # hard spotlight pool.
    rake = pygame.Surface((DW, deck.h), pygame.SRCALPHA)
    for y in range(0, deck.h, max(1, m(2))):
        fy = 1.0 - y / deck.h
        for x in range(0, DW, max(1, m(6))):
            fx = 1.0 - x / DW
            a = int(40 * (fx ** 1.4) * (fy ** 0.8))
            if a > 0:
                pygame.draw.rect(rake, (255, 200, 122, a), (x, y, m(6), m(2)))
    surf.blit(rake, deck.topleft, special_flags=pygame.BLEND_ADD)


def _deck_ao(surf, cx, top_y, w, depth=None, alpha=150):
    """A soft elliptical ambient-occlusion shadow on the planks directly under a
    stall/cart so it sits ON the deck rather than floating. Top-left light => the
    shadow pools slightly down-right."""
    depth = depth if depth is not None else m(16)
    ao = pygame.Surface((w + m(28), depth), pygame.SRCALPHA)
    for i in range(depth, 0, -1):
        a = int(alpha * (i / depth) ** 1.6)
        rw = int((w + m(28)) * (i / depth))
        rh = int(depth * (i / depth))
        if rw <= 0 or rh <= 0:
            continue
        e = pygame.Surface((rw, rh), pygame.SRCALPHA)
        pygame.draw.ellipse(e, (18, 9, 3, a), e.get_rect())
        ao.blit(e, ((w + m(28) - rw) // 2 + m(4), (depth - rh) // 2),
                special_flags=pygame.BLEND_RGBA_MAX)
    surf.blit(ao, (cx - (w + m(28)) // 2, top_y - depth // 2))


def draw_palm(surf, x_base, y_base, height, lean, flip=False, behind=False):
    """A coconut palm framing an edge: a curved gradient trunk with ring scars +
    a crown of layered fronds. `lean` curves the trunk outward; `behind` mutes it
    into the haze so the back-edge palms read as further away."""
    seg = 14
    pts_l, pts_r = [], []
    trunk_w_base = m(11) if not behind else m(7)
    sway = lean
    top_x = x_base + sway
    top_y = y_base - height
    for i in range(seg + 1):
        t = i / seg
        cx = x_base + sway * (t * t)
        cy = y_base - height * t
        w_here = trunk_w_base * (1.0 - 0.45 * t)
        pts_l.append((cx - w_here / 2, cy))
        pts_r.append((cx + w_here / 2, cy))
    trunk_poly = pts_l + pts_r[::-1]
    tcol = lerp_color(PALM_TRUNK, (54, 38, 24), 0.4) if behind else PALM_TRUNK
    pygame.draw.polygon(surf, tcol, trunk_poly)
    if not behind:
        pygame.draw.lines(surf, lerp_color(PALM_TRUNK_HI, WHITE, 0.1), False,
                          pts_l, max(1, m(1.6)))
    for i in range(2, seg, 2):
        a, b = pts_l[i], pts_r[i]
        pygame.draw.line(surf, (70, 46, 26), a, b, max(1, m(1.0)))
    cxr, cyr = top_x, top_y
    if not behind:
        soft_glow(surf, int(cxr), int(cyr), m(18), (120, 200, 120), 26, layers=6)
    n_fronds = 9
    for k in range(n_fronds):
        ang = math.radians(-150 + (300 / (n_fronds - 1)) * k)
        flen = height * (0.42 if not behind else 0.32) * (0.8 + 0.4 * abs(math.cos(ang)))
        ex = cxr + math.cos(ang) * flen
        ey = cyr + math.sin(ang) * flen * 0.55 + flen * 0.22
        midx = (cxr + ex) / 2 + math.cos(ang + math.pi / 2) * flen * 0.10
        midy = (cyr + ey) / 2 - flen * 0.12
        wfr = m(7) if not behind else m(4)
        perp = (math.cos(ang + math.pi / 2), math.sin(ang + math.pi / 2))
        leaf = [
            (cxr, cyr),
            (midx + perp[0] * wfr, midy + perp[1] * wfr),
            (ex, ey),
            (midx - perp[0] * wfr, midy - perp[1] * wfr),
        ]
        shade = FROND_DK if (k % 2 == 0) else FROND_MID
        if behind:
            shade = lerp_color(shade, (52, 62, 52), 0.5)
        pygame.draw.polygon(surf, shade, leaf)
        if not behind:
            pygame.draw.line(surf, lerp_color(FROND_HI, WHITE, 0.1),
                             (cxr, cyr), (ex, ey), max(1, m(1.0)))
    if not behind:
        for dx, dy in ((-m(4), m(3)), (m(3), m(5)), (0, m(8))):
            pygame.draw.circle(surf, (74, 52, 30),
                               (int(cxr + dx), int(cyr + dy)), m(3))
            pygame.draw.circle(surf, (110, 82, 50),
                               (int(cxr + dx - m(0.8)), int(cyr + dy - m(0.8))),
                               max(1, m(1.2)))


# =============================================================================
# Stall — the shared awning-tile template (vary sign + preview only)
# =============================================================================
def draw_stall(surf, label, sid, cx, top_y, w, h, front=True, glint=0,
               group=None):
    """One category stall: a striped macaw-red awning over a driftwood counter, a
    glass-dome preview well holding the category's representative item, and a
    thick gold-keyline category sign. `front` stalls are larger + brighter than
    the back-jetty stalls. Lit from the top-left; a deck AO grounds it. `glint`
    nudges this dome's specular kiss so the 6 domes don't share one stamped tell
    (all still top-left lit). `group` picks a category-legible preview build
    (crossed shoes / parrot bust) so the thumbnail reads as the CATEGORY."""
    rect = pygame.Rect(cx - w // 2, top_y, w, h)
    rad = m(10)

    # AO on the deck under the stall so it reads as sitting ON the planks
    _deck_ao(surf, rect.centerx, rect.bottom - m(2), w, depth=m(18), alpha=150)

    # ── post legs ──────────────────────────────────────────────────────────────
    leg_col = (104, 68, 38)
    for lx in (rect.x + m(8), rect.right - m(8)):
        pygame.draw.line(surf, leg_col, (lx, rect.y + m(20)),
                         (lx, rect.bottom), max(1, m(3.2)))
        pygame.draw.line(surf, (*PALM_TRUNK_HI, 150), (lx - m(1), rect.y + m(20)),
                         (lx - m(1), rect.bottom), max(1, m(1.0)))

    # ── counter / backboard the preview sits on ───────────────────────────────
    board = pygame.Rect(rect.x, rect.y + m(20), w, h - m(20))
    surf.blit(vgrad_stops(board.w, board.h, rad,
                          [(0.0, lerp_color(WOOD_HI, CREAM, 0.28)),
                           (1.0, WOOD_DK)], 250, gamma=1.1), board.topleft)
    top_sheen(surf, board, rad, m(12), peak=46)
    contact_shadow(surf, board, rad, m(5), alpha=95)
    pygame.draw.rect(surf, (40, 22, 10), board, width=max(1, m(1.6)),
                     border_radius=rad)
    bevel_rim(surf, board, rad, (60, 38, 16), (*GOLD_PALE, 205),
              w=max(1, m(1.2)))

    # ── preview well (the constellation glass cabochon) + thumbnail ───────────
    # A warm-amber well (not the night store's near-black) so previews read in
    # the golden-hour light.
    disc_r = m(24) if front else m(20)
    disc_cy = board.y + (m(34) if front else m(30))
    soft_glow(surf, board.centerx, disc_cy, disc_r + m(4), (255, 204, 124),
              40, layers=8)
    cabochon(surf, board.centerx, disc_cy, disc_r, (96, 66, 36), (40, 24, 10))
    if sid is not None:
        # category-legible preview build: SHOES => a crossed PAIR; PARROTS => a
        # head-on bust; COSTUMES => the costume scaled up + shifted so the HAT
        # breaks the dome rim (the category reads, not the bird); everything else
        # => the default letterboxed icon, contained in the dome.
        box = int(disc_r * 1.55)
        if group == "shoes":
            thumb, ty = _preview_crossed_shoes(sid, box), disc_cy
        elif group == "parrot":
            thumb, ty = _preview_bust(sid, box), disc_cy
        elif group == "costume":
            thumb = _preview_icon(sid, int(box * 1.18))
            ty = disc_cy - int(disc_r * 0.18)        # lift so the hat pokes up
        else:
            thumb, ty = _preview_icon(sid, box), disc_cy
        tr = thumb.get_rect(center=(board.centerx, ty))
        surf.blit(_rim_lit(thumb), tr.topleft, special_flags=pygame.BLEND_ADD)
        surf.blit(thumb, tr.topleft)
    cabochon_glass(surf, board.centerx, disc_cy, disc_r, tint=GOLD_PALE)
    # a small per-dome specular kiss, varied in position + size off `glint`, so
    # the row's glass highlights don't all sit in the identical stamped spot
    # (all still biased to the top-left lit quadrant).
    gv = [(-0.42, -0.40, 0.20), (-0.30, -0.50, 0.16), (-0.50, -0.28, 0.18),
          (-0.36, -0.44, 0.22), (-0.46, -0.36, 0.15), (-0.28, -0.46, 0.19)]
    gx, gy, gs = gv[glint % len(gv)]
    soft_glow(surf, int(board.centerx + disc_r * gx),
              int(disc_cy + disc_r * gy), int(disc_r * gs),
              (255, 250, 232), 150, layers=5)
    # a legendary tier gem set on the dome's upper-right rim (the jewel-store DNA)
    g45 = disc_r * 0.7071
    gpal = RARITY["legendary"]
    facet_gem(surf, int(board.centerx + g45), int(disc_cy - g45),
              m(6 if front else 5), gpal["gem"], gpal["deep"])

    # ── category sign: a gold-keyline plaque with thick crisp type ────────────
    sign_y = board.bottom - (m(15) if front else m(13))
    sf = font(12 if front else 10)
    label_w = _glyph_base(label, sf, m(0.6)).get_width()
    plaque = pygame.Rect(0, 0, label_w + m(20), m(21 if front else 18))
    plaque.center = (board.centerx, sign_y)
    surf.blit(gold_a_fill(plaque.w, plaque.h, plaque.h // 2), plaque.topleft)
    gloss_sweep(surf, plaque, plaque.h // 2, peak=64)
    pygame.draw.rect(surf, GOLD_A_RIM_DARK, plaque, width=max(1, m(1.6)),
                     border_radius=plaque.h // 2)
    bevel_rim(surf, plaque, plaque.h // 2, GOLD_A_RIM_DARK,
              (*GOLD_A_RIM_BRIGHT, 235), w=max(1, m(1.1)))
    plain_text(surf, label, sf, plaque.center, GOLD_A_NUM, shadow_a=0,
               tracking=m(0.6), weight=m(0.9))

    # ── striped awning on top (drawn LAST so it overhangs the counter) ────────
    _awning(surf, rect.x - m(3), rect.y, w + m(6),
            m(24) if front else m(19), front=front)


def _awning(surf, x, y, w, h, front=True):
    """A scalloped striped awning in macaw red + cream — the shared bazaar
    signature across all 7 stalls. A lit top ridge, a shaded valance, and a
    gold trim along the scallop crest. Lit from the top-left."""
    n_stripe = 5
    sw = w / n_stripe
    scallop = int(h * 0.5)
    top = y
    # solid back board behind the awning
    pygame.draw.rect(surf, (58, 14, 6), (x, top - m(4), w, m(5)))
    for i in range(n_stripe):
        sx = x + i * sw
        red = (i % 2 == 0)
        c_top = AWNING_RED_HI if red else lerp_color(CREAM, WHITE, 0.25)
        c_bot = AWNING_RED if red else CREAM
        stripe = vgrad_stops(int(sw) + 2, h, 0,
                             [(0.0, c_top), (1.0, c_bot)], 255, gamma=1.05)
        surf.blit(stripe, (int(sx), top))
        # scallop: a filled half-disc hanging off the bottom of each stripe
        scal = pygame.Surface((int(sw) + 2, scallop * 2 + m(4)), pygame.SRCALPHA)
        pygame.draw.ellipse(scal, (*c_bot, 255),
                            (0, -scallop, int(sw) + 2, scallop * 2))
        surf.blit(scal, (int(sx), top + h - m(1)))
        # a soft shade on the scallop underside so the valance reads dimensional
        sh = pygame.Surface((int(sw) + 2, scallop), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 60), (0, -scallop // 2, int(sw) + 2, scallop))
        surf.blit(sh, (int(sx), top + h + scallop // 2 - m(1)))
    # lit top ridge + dark seams between stripes
    pygame.draw.line(surf, (255, 234, 196, 230), (x, top), (x + w, top),
                     max(1, m(1.8)))
    for i in range(1, n_stripe):
        sx = x + i * sw
        pygame.draw.line(surf, (40, 12, 6, 150), (sx, top), (sx, top + h),
                         max(1, m(0.8)))
    # a thin gold valance trim along the scallop crest
    pygame.draw.line(surf, (*GOLD, 210), (x, top + h), (x + w, top + h),
                     max(1, m(1.4)))


# =============================================================================
# PARCELS — the gold-banded crimson MYSTERY CHEST on the dock (the hero)
# =============================================================================
def draw_parcels_chest(surf, cx, base_y):
    """PARCELS as the mystery hero: a gold-banded crimson treasure chest seated
    on the boardwalk (like Pip's cart — no half-drawn boat). Gold straps + corner
    bosses + a domed lid + a big gold '?' so it reads as a TREASURE chest that
    separates from the awning-reds and echoes the jewel-store gold. A warm
    crimson/gold halo (never white) marks it the hero; the gold PARCELS plaque
    sits clearly BELOW, clear of the chest."""
    cx, base_y = int(cx), int(base_y)
    cw, lid_h, body_h = m(56), m(22), m(34)
    chest = pygame.Rect(int(cx - cw / 2), base_y - body_h, cw, body_h)

    # AO on the planks so the chest sits ON the deck (a flat straight-edged pool)
    _deck_ao(surf, cx, base_y + m(2), int(cw * 1.5), depth=m(18), alpha=165)

    # warm hero halo — additive glow on the pale planks blows to a WHITE disc, so
    # instead lay a NON-additive radial 'spotlight': a darkened crimson seat that
    # the chest sits in (giving the warm gold a ground to read against), then a
    # restrained additive gold rim ring. Reads as 'prize on a spotlit dais', not
    # a white blob.
    glow_cy = base_y - body_h + m(4)
    seat_r = m(56)
    seat = pygame.Surface((seat_r * 2, seat_r * 2), pygame.SRCALPHA)
    for i in range(seat_r, 0, -1):
        f = i / seat_r
        # warm dusk crimson that DARKENS the bright deck near the rim, warming in
        col = lerp_color((150, 70, 50), (96, 40, 44), f)
        a = int(120 * (f ** 1.4))
        pygame.draw.circle(seat, (*col, a), (seat_r, seat_r), i)
    surf.blit(seat, (cx - seat_r, glow_cy - seat_r))
    # a soft additive crimson bloom kept LOW so it tints rather than whitens
    soft_glow(surf, cx, glow_cy - m(6), m(34), (210, 70, 54), 26, layers=12)
    # a single thin gold accent ring (the jewel-store gold echo)
    ring = pygame.Surface((seat_r * 2, seat_r * 2), pygame.SRCALPHA)
    pygame.draw.circle(ring, (*GOLD, 130), (seat_r, seat_r), m(46), max(1, m(1.6)))
    surf.blit(ring, (cx - seat_r, glow_cy - seat_r))

    # ── chest body: crimson planks with a lit top-left face ───────────────────
    surf.blit(vgrad_stops(chest.w, chest.h, m(4),
                          [(0.0, (206, 64, 50)), (1.0, MYST_DEEP)], 255,
                          gamma=1.1), chest.topleft)
    top_sheen(surf, chest, m(4), m(10), peak=46)
    contact_shadow(surf, chest, m(4), m(4), alpha=95)
    # vertical plank seams on the body
    for k in range(1, 4):
        sx = chest.x + chest.w * k // 4
        pygame.draw.line(surf, (96, 18, 18, 170), (sx, chest.y + m(2)),
                         (sx, chest.bottom - m(2)), max(1, m(1.0)))
    pygame.draw.rect(surf, (54, 10, 12), chest, width=max(1, m(1.8)),
                     border_radius=m(4))

    # ── domed lid (a half-rounded crimson cap) ────────────────────────────────
    lid = pygame.Rect(chest.x - m(2), chest.y - lid_h + m(2), chest.w + m(4), lid_h)
    lidsurf = pygame.Surface((lid.w, lid.h), pygame.SRCALPHA)
    for y in range(lid.h):
        f = y / max(1, lid.h - 1)
        col = lerp_color((222, 84, 64), (150, 30, 30), f)
        # round the top corners by skipping the outer pixels near the crown
        inset = int((lid.w * 0.5) * (1 - math.sin(math.pi * 0.5 * (1 - f))) * 0.32)
        pygame.draw.line(lidsurf, col, (inset, y), (lid.w - inset, y))
    surf.blit(lidsurf, lid.topleft)
    pygame.draw.line(surf, (255, 196, 170, 210), (lid.x + m(6), lid.y + m(2)),
                     (lid.right - m(6), lid.y + m(2)), max(1, m(1.4)))

    # ── GOLD bands: two horizontal straps + a central vertical strap + lock ────
    gold_strap = GOLD
    gold_dk = lerp_color(GOLD, NEAR_BLACK, 0.45)
    for sy in (lid.bottom - m(2), chest.centery + m(2)):
        strap = pygame.Rect(chest.x - m(1), int(sy - m(3)), chest.w + m(2), m(6))
        surf.blit(vgrad_stops(strap.w, strap.h, m(1),
                              [(0.0, GOLD_PALE), (1.0, gold_dk)], 255),
                  strap.topleft)
        pygame.draw.rect(surf, gold_dk, strap, width=max(1, m(0.8)))
    # central vertical strap behind the lock
    vstrap = pygame.Rect(int(cx - m(4)), lid.y + m(4), m(8), base_y - lid.y - m(6))
    surf.blit(vgrad_stops(vstrap.w, vstrap.h, m(1),
                          [(0.0, GOLD_PALE), (1.0, gold_dk)], 255), vstrap.topleft)
    pygame.draw.rect(surf, gold_dk, vstrap, width=max(1, m(0.8)))
    # corner bosses (gold rivets) at the four chest corners
    for bx, by in ((chest.x + m(3), chest.y + m(3)),
                   (chest.right - m(3), chest.y + m(3)),
                   (chest.x + m(3), chest.bottom - m(3)),
                   (chest.right - m(3), chest.bottom - m(3))):
        pygame.draw.circle(surf, gold_dk, (bx, by), m(2.4))
        pygame.draw.circle(surf, GOLD_PALE, (bx - m(0.6), by - m(0.6)), m(1.2))

    # ── the big gold '?' on a dark lock plate (the mystery tell) ──────────────
    plate = pygame.Rect(0, 0, m(20), m(22))
    plate.center = (cx, chest.centery + m(1))
    surf.blit(vgrad_stops(plate.w, plate.h, m(3),
                          [(0.0, gold_strap), (1.0, gold_dk)], 255), plate.topleft)
    pygame.draw.rect(surf, (40, 22, 4), plate, width=max(1, m(1.2)),
                     border_radius=m(3))
    bevel_rim(surf, plate, m(3), (40, 22, 4), (*GOLD_PALE, 220), w=max(1, m(0.9)))
    qf = font(15)
    plain_text(surf, "?", qf, plate.center, (52, 28, 4), shadow_a=0,
               weight=m(1.2))
    # a hot specular kiss on the lid's upper-left (top-left light), kept warm
    soft_glow(surf, lid.x + m(8), lid.y + m(4), m(4), (255, 220, 188), 130,
              layers=6)

    # ── PARCELS gold-keyline plaque clearly BELOW the chest ───────────────────
    sf = font(11)
    label_w = _glyph_base("PARCELS", sf, m(0.6)).get_width()
    plaque = pygame.Rect(0, 0, label_w + m(20), m(19))
    plaque.center = (cx, base_y + m(16))
    surf.blit(gold_a_fill(plaque.w, plaque.h, plaque.h // 2), plaque.topleft)
    gloss_sweep(surf, plaque, plaque.h // 2, peak=64)
    pygame.draw.rect(surf, GOLD_A_RIM_DARK, plaque, width=max(1, m(1.6)),
                     border_radius=plaque.h // 2)
    bevel_rim(surf, plaque, plaque.h // 2, GOLD_A_RIM_DARK,
              (*GOLD_A_RIM_BRIGHT, 235), w=max(1, m(1.1)))
    plain_text(surf, "PARCELS", sf, plaque.center, GOLD_A_NUM, shadow_a=0,
               tracking=m(0.6), weight=m(0.9))


# =============================================================================
# Foreground dressing — one coiled dock rope (bottom-left anchor)
# =============================================================================
def draw_coiled_rope(surf, cx, base_y):
    """A single coiled mooring rope on the planks (bottom-left), the one small
    foreground prop that balances the PARCELS chest on the right. Warm hemp
    tone, top-left lit, a flat straight-edged contact shadow so it sits ON the
    deck without fighting the plank grid."""
    cx, base_y = int(cx), int(base_y)
    rope_lo = (150, 112, 64)
    rope_hi = (206, 168, 110)
    rope_dk = (96, 66, 32)
    # flat contact shadow (a low ellipse, wide + shallow — reads as a deck line)
    sh = pygame.Surface((m(72), m(12)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (24, 12, 4, 130), sh.get_rect())
    surf.blit(sh, (cx - m(36), base_y - m(4)))
    # concentric coils, drawn outer -> inner so each loop overlaps the last
    for i, rr in enumerate((m(28), m(21), m(14), m(8))):
        col = lerp_color(rope_dk, rope_hi, i / 3)
        ring = pygame.Surface((rr * 2 + m(6), rr + m(6)), pygame.SRCALPHA)
        rc = (rr + m(3), (rr + m(6)) // 2)
        pygame.draw.ellipse(ring, (*rope_dk, 255),
                            (0, 0, rr * 2 + m(4), rr + m(4)), max(1, m(3.0)))
        pygame.draw.ellipse(ring, (*col, 255),
                            (m(1), m(0.6), rr * 2 + m(2), rr + m(2)), max(1, m(2.2)))
        # a top-left lit arc on each coil
        pygame.draw.arc(ring, (*rope_hi, 220),
                        (m(1), m(0.6), rr * 2 + m(2), rr + m(2)),
                        math.radians(120), math.radians(210), max(1, m(1.6)))
        surf.blit(ring, (cx - rc[0], base_y - rc[1]))
    # the loose tail snaking off to the left
    pygame.draw.lines(surf, rope_dk, False,
                      [(cx - m(26), base_y), (cx - m(40), base_y + m(3)),
                       (cx - m(52), base_y - m(1))], max(1, m(3.4)))
    pygame.draw.lines(surf, rope_hi, False,
                      [(cx - m(26), base_y - m(1)), (cx - m(40), base_y + m(2)),
                       (cx - m(52), base_y - m(2))], max(1, m(1.6)))


# =============================================================================
# Pip at the dockside cart
# =============================================================================
def draw_pip_cart(surf, cx, base_y):
    """Pip the scarlet macaw tending a small wooden dockside cart, a coin spinning
    above the cart with a soft aura, set lower-centre clear of the stall labels."""
    # AO on the planks under the whole cart
    _deck_ao(surf, cx, base_y + m(8), m(120), depth=m(22), alpha=160)

    # ── the cart: a two-wheel barrow with a crate of goods ────────────────────
    cw, ch = m(100), m(36)
    cart = pygame.Rect(int(cx - cw / 2), int(base_y - ch), cw, ch)
    surf.blit(vgrad_stops(cart.w, cart.h, m(5),
                          [(0.0, lerp_color(WOOD_HI, CREAM, 0.22)),
                           (1.0, WOOD_DK)], 252, gamma=1.1), cart.topleft)
    top_sheen(surf, cart, m(5), m(10), peak=48)
    contact_shadow(surf, cart, m(5), m(4), alpha=90)
    pygame.draw.rect(surf, (44, 24, 10), cart, width=max(1, m(1.6)),
                     border_radius=m(5))
    bevel_rim(surf, cart, m(5), (60, 36, 16), (*GOLD_PALE, 205), w=max(1, m(1.1)))
    for k in range(1, 4):
        ly = cart.y + cart.h * k // 4
        pygame.draw.line(surf, (50, 30, 14, 150), (cart.x + m(2), ly),
                         (cart.right - m(2), ly), max(1, m(0.8)))
    # wheels
    for wx in (cart.x + m(22), cart.right - m(22)):
        pygame.draw.circle(surf, (40, 24, 12), (wx, cart.bottom + m(6)), m(11))
        pygame.draw.circle(surf, (152, 112, 68), (wx, cart.bottom + m(6)), m(11),
                           max(1, m(2)))
        pygame.draw.circle(surf, (90, 60, 32), (wx, cart.bottom + m(6)), m(3))
        for sp in range(0, 360, 45):
            ex = wx + math.cos(math.radians(sp)) * m(9)
            ey = cart.bottom + m(6) + math.sin(math.radians(sp)) * m(9)
            pygame.draw.line(surf, (110, 76, 42), (wx, cart.bottom + m(6)),
                             (ex, ey), max(1, m(1.2)))
    # a crated good on the cart + a tiny red sack
    pygame.draw.rect(surf, (120, 30, 16), (cart.right - m(28), cart.y - m(11),
                     m(20), m(13)), border_radius=m(2))
    pygame.draw.rect(surf, (40, 12, 6), (cart.right - m(28), cart.y - m(11),
                     m(20), m(13)), width=max(1, m(1)), border_radius=m(2))

    # ── coin spinning above the cart with a soft aura ─────────────────────────
    coin_cx, coin_cy = int(cx + m(36)), int(base_y - ch - m(34))
    soft_glow(surf, coin_cx, coin_cy, m(16), (255, 212, 112), 80, layers=10)
    coin_glyph(surf, coin_cx, coin_cy, m(12))
    pygame.draw.line(surf, (255, 255, 242, 220), (coin_cx + m(10), coin_cy - m(9)),
                     (coin_cx + m(16), coin_cy - m(15)), max(1, m(1)))

    # ── Pip himself: the real parrot frame, scaled, beside the cart ───────────
    bird = parrot.get_parrot(1, 0.0)
    bw, bh = bird.get_size()
    target_h = m(84)
    s = target_h / bh
    bird = pygame.transform.smoothscale(bird, (int(bw * s), int(bh * s)))
    br = bird.get_rect()
    br.midbottom = (int(cx - m(34)), int(base_y - ch + m(12)))
    # soft aura behind Pip so he reads as the warmly-lit merchant — restrained +
    # warm so it never reads as a white oval behind him.
    soft_glow(surf, br.centerx, br.centery, m(30), (255, 188, 104), 20, layers=10)
    # a warm rim light on Pip from the low sun (top-left)
    rim = bird.copy()
    rim.fill((255, 222, 152, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(rim, (br.x - m(2), br.y - m(2)), special_flags=pygame.BLEND_ADD)
    surf.blit(bird, br.topleft)


# =============================================================================
# Header — wordmark + balance capsule + hint
# =============================================================================
def draw_header(surf):
    # a soft warm darkening band so the gold wordmark + capsule read on the sky
    band = pygame.Surface((DW, m(100)), pygame.SRCALPHA)
    for y in range(m(100)):
        a = int(120 * (1 - y / m(100)) ** 1.2)
        pygame.draw.line(band, (28, 20, 56, a), (0, y), (DW, y))
    surf.blit(band, (0, 0))
    # screen frame hairline (warm gold)
    pygame.draw.rect(surf, (*GOLD, 70), (m(3), m(3), DW - m(6), DH - m(6)),
                     width=max(1, m(1)), border_radius=m(12))
    # Skybit gold-on-red STORE wordmark
    title_wordmark(surf, "STORE", (DW // 2, m(27)), 30, tracking=m(4))
    balance_capsule(surf, DW // 2, m(66))
    plain_text(surf, "TAP A STALL TO BROWSE", font(9),
               (DW // 2, m(89)), (255, 236, 192), shadow_a=150,
               tracking=m(1.2), weight=m(0.6), keyline=(70, 32, 12), kw=m(0.6))


def balance_capsule(surf, cx, y):
    """The constellation store's recessed gold balance capsule with the REAL
    in-game coin + a gradient-gold number, retuned a touch warmer for the dock."""
    val = f"{BALANCE:,}"
    vf = font(22)
    vw = _glyph_base(val, vf, 0).get_width() + m(2)
    coin_d, gapc, padl, padr = m(26), m(16), m(14), m(20)
    w = padl + coin_d + gapc + vw + padr
    h = m(40)
    cap = pygame.Rect(cx - w // 2, y - h // 2, w, h)
    drop_shadow(surf, cap, h // 2, blur=m(6), alpha=140, dy=m(3))
    surf.blit(vgrad(cap.w, cap.h, h // 2, (74, 48, 22), (32, 18, 8), 255, gamma=1.1),
              cap.topleft)
    top_sheen(surf, cap, h // 2, m(14), peak=52)
    contact_shadow(surf, cap, h // 2, m(5), alpha=115)
    pygame.draw.rect(surf, (0, 0, 0, 205), cap, width=max(1, m(1.8)),
                     border_radius=h // 2)
    bevel_rim(surf, cap, h // 2, lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD_PALE, 245), w=max(1, m(1.8)))
    x = cap.x + padl
    soft_glow(surf, x + coin_d // 2, y, int(coin_d * 0.40), (255, 206, 92), 42,
              layers=6)
    coin_glyph(surf, x + coin_d // 2, y, coin_d // 2)
    x += coin_d + gapc
    gradient_text(surf, val, vf, (x + vw // 2, y), GOLD_A_STOPS[0][1],
                  GOLD_A_STOPS[-1][1], weight=m(1.0), keyline=(96, 56, 12),
                  kw=m(1.2), shadow=True)


# =============================================================================
# Compose
# =============================================================================
def render_device():
    surf = pygame.Surface((DW, DH))
    draw_sky(surf)

    # ── BACK ROW: 3 stalls on the far jetty (≥80px tall), seated ABOVE the
    # water so the glitter band reads clearly between the two tiers. ────────────
    draw_back_jetty(surf)
    back = [("COSTUMES", "costume"), ("HATS", "hats"), ("SHADES", "shades")]
    back_w = m(96)
    back_xs = [int(DW * f) for f in (0.205, 0.50, 0.795)]
    for i, ((label, group), bx) in enumerate(zip(back, back_xs)):
        draw_stall(surf, label, _preview_id(group), bx, m(122), back_w, m(84),
                   front=False, glint=i, group=group)

    # back-edge palms (hazy) framing the jetty so depth reads
    draw_palm(surf, m(12), m(210), m(112), -m(22), flip=False, behind=True)
    draw_palm(surf, DW - m(12), m(210), m(112), m(22), flip=True, behind=True)

    # ── the signature glitter water between the tiers + moored boats ──────────
    draw_water(surf)
    draw_distant_boats(surf)

    # ── near boardwalk fills the lower frame ──────────────────────────────────
    draw_front_boardwalk(surf)

    # front-edge palms framing the lower corners (full, lit)
    draw_palm(surf, m(4), DH - m(4), m(238), -m(50), flip=False)
    draw_palm(surf, DW - m(4), DH - m(4), m(238), m(50), flip=True)

    # ── FRONT ROW: 3 larger stalls (PARROTS / ANIMALS / SHOES). PARCELS is the
    # mystery CHEST on the dock (drawn later), not a stall. ────────────────────
    front = [("PARROTS", "parrot"), ("ANIMALS", "animal"), ("SHOES", "shoes")]
    front_w = m(96)
    front_xs = [int(DW * f) for f in (0.20, 0.50, 0.80)]
    for i, ((label, group), fx) in enumerate(zip(front, front_xs)):
        draw_stall(surf, label, _preview_id(group), fx, m(300), front_w, m(98),
                   front=True, glint=i + 3, group=group)

    # ── ONE foreground anchor bottom-LEFT (a coiled dock rope) to balance the
    # PARCELS chest on the right. ──────────────────────────────────────────────
    draw_coiled_rope(surf, int(DW * 0.165), DH - m(34))

    # ── PARCELS mystery chest on the dock, lower-right — pulled LEFT off the edge
    # so its hero halo no longer reads as a glitch bleeding off-frame; its own
    # clear zone, deliberately apart from the stall grid + Pip. ────────────────
    draw_parcels_chest(surf, int(DW * 0.70), DH - m(96))

    # ── Pip at his dockside cart, lower-LEFT of centre on the near boardwalk so
    # he reads clear of the PARCELS chest. ─────────────────────────────────────
    draw_pip_cart(surf, int(DW * 0.40), DH - m(50))

    draw_header(surf)
    return surf


def main():
    dev = render_device()
    pygame.image.save(downscale(dev, 1), os.path.join(_HERE, "round_2.png"))
    pygame.image.save(downscale(dev, 2), os.path.join(_HERE, "round_2@2x.png"))
    print("SS =", SS, "device =", DW, "x", DH)
    print("saved round_2.png + round_2@2x.png")


if __name__ == "__main__":
    main()
