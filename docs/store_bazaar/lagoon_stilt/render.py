"""
LAGOON STILT-MARKET — store "bazaar landing" selection-sheet prototype.

The most overtly scarlet-macaw-island take on the GOLDEN-HOUR DOCK MARKET
direction: a tropical over-water stilt-village market at golden hour. Seven
thatched-roof market huts perched on wooden stilts rise out of a glittering
gold lagoon, linked by little boardwalk planks, with palms + distant hazy
islets, Pip selling from the central stilt-jetty. The sky eases UP into the
indigo+gold jewel-store nebula so entering a stall dissolves cohesively into
the existing CONSTELLATION store.

Authored resolution-independently from SS=4: every hut, stilt, plank, water
glint and glyph is drawn oversized on a 1440x2560 device surface, then ONE
smoothscale down turns the geometry into crisp anti-aliased edges (the same
supersample pipeline as docs/store_redesign/constellation_hi/render_hi.py,
whose primitives this reuses for one shared visual DNA).

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

# Reuse the locked CONSTELLATION primitives so the bazaar shares one DNA with
# the stall screens it dissolves into.
import docs.store_redesign.constellation_hi.render_hi as C
from docs.store_redesign.constellation_hi.render_hi import (
    SS, DW, DH, m, mf, font, vgrad, vgrad_stops, gold_a_fill, soft_glow,
    drop_shadow, gradient_text, plain_text, coin_glyph, bevel_rim, top_sheen,
    gold_rule, title_wordmark, downscale, multistop_v, _glyph_base,
    GOLD, GOLD_PALE, GOLD_DEEP, GOLD_A_TOP, GOLD_A_BOT,
)


# =============================================================================
# Palette — golden-hour lagoon easing UP to the indigo+gold jewel nebula apex.
# Warm low sun rakes top-left. The apex stops are the CONSTELLATION BG anchors
# so the sky reads as the SAME sky the stall screens open into.
# =============================================================================
SKY_STOPS = [
    (0.00, (10, 11, 40)),        # nebula apex — CONSTELLATION indigo
    (0.16, (24, 22, 70)),        # indigo, first emerging stars live here
    (0.34, (62, 46, 104)),       # violet dusk band
    (0.50, (150, 96, 120)),      # warm rose haze (the sun's high glow)
    (0.66, (236, 150, 96)),      # golden-hour amber
    (0.78, (255, 196, 112)),     # the low sun core (brief anchor)
    (0.86, (255, 214, 140)),     # hottest band right above the water
]
# A warm SATURATED gold disc, not a blown-white core — the back row must read
# against sky, not glare, so the core stays a rich gold and the halo restrained.
SUN_CORE = (255, 210, 130)
SUN_HALO = (255, 176, 88)
SUN_AURA = (255, 150, 78)        # warm aura behind Pip on the jetty

# Lagoon water — gold sun-glitter band over a deep teal-violet bed so the warm
# top reflection sits on cool depth (the classic golden-hour-on-water read).
WATER_STOPS = [
    (0.00, (236, 176, 96)),      # horizon water catches the hot sun
    (0.18, (206, 142, 96)),
    (0.40, (96, 96, 120)),       # mid lagoon cools to dusky lilac
    (0.72, (32, 52, 78)),        # deep teal trough
    (1.00, (16, 30, 54)),
]
GLITTER = (255, 232, 178)        # the gold sun-glitter flecks

# Hut materials — sun-bleached warm timber + thatch + the macaw-red/cream awning.
THATCH_HI = (214, 168, 104)      # lit straw ridge (top-left light)
THATCH_MID = (176, 126, 66)
THATCH_LO = (118, 78, 38)        # shaded straw underside
THATCH_EDGE = (74, 46, 22)
WOOD_HI = (198, 150, 96)
WOOD_MID = (150, 104, 60)
WOOD_LO = (92, 60, 32)
WOOD_EDGE = (54, 33, 16)
AWN_RED = (212, 56, 50)          # scarlet-macaw awning stripe
AWN_RED_D = (150, 30, 32)
AWN_CREAM = (244, 232, 206)
AWN_CREAM_D = (206, 188, 158)
STALL_DARK = (30, 24, 34)        # the shaded stall interior behind the dome
LABEL_KEY = (40, 22, 14)         # bold gold-keyline label contour
PALM_FROND = (44, 92, 64)
PALM_FROND_HI = (86, 142, 92)
PALM_TRUNK = (96, 66, 38)
ISLET = (58, 56, 96)             # distant hazy violet islets

# The mystery PARCELS hero hut is re-branded by SHAPE + GOLD, never a red sun
# aura. A warm GOLD trim/crate read carries the mystery, so nothing glows red
# from below the village. (MYST_DEEP kept only for the deep name-board body.)
MYST_GOLD = (255, 206, 110)      # hero accent — warm gold, the store's coin hue
MYST_GOLD_D = (196, 138, 56)
MYST_DEEP = (120, 22, 26)        # deep accent reserved for the hero name board

# Natural water reflection tints — cool + desaturated, NORMAL blend, low alpha.
# A reflection is a darkened, slightly-blued echo of the hut, never an additive
# coloured aura. These read as wet timber/thatch on dusk water.
REFL_HUT = (52, 48, 62)          # generic hut reflection (cool, muted)
REFL_THATCH = (78, 60, 54)       # warmer streak for the lit thatch ridge echo


# =============================================================================
# Stall -> hut binding. Seven groups, each shows its category's REAL preview
# thumbnail in a glass cabochon. PARCELS is the glowing red mystery hero hut.
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


def _group_thumb(group):
    """REAL in-game preview for a stall: the icon/first-frame of its first item.

    SHADES' first catalog id is NO SHADES (a bare-eyed parrot, no icon) — the
    brief forbids showing a bare base parrot for it, so SHADES skips to the
    first shades id that owns a real eyewear icon (a clear shades graphic).
    Returns (surface, letterbox) — letterbox flags aspect-extreme items
    (flip-flops, party hat) so the placer contains them in the dome rather
    than letting an extreme aspect blow past the glass."""
    ids = store_catalog.ids_of_group(group)
    sid = ids[0]
    src = None
    if group == "shades":
        for cand in ids:
            ic = parrot.get_skin_icon(cand)
            if ic is not None:
                src, sid = ic, cand
                break
    if src is None:
        src = parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    w, h = src.get_size()
    letterbox = max(w, h) / max(1, min(w, h)) > 1.7
    return src, letterbox


# =============================================================================
# Background — golden-hour sky, low sun, emerging stars, distant islets, palms.
# =============================================================================
_static_sky = None


def _build_static_sky():
    """The whole behind-the-water backdrop, built once at device resolution:
    multi-stop golden-hour->nebula sky, a raked low sun + halo, a sparse field
    of emerging stars confined to the indigo apex (so they read as 'first
    stars of dusk', not a full night field), hazy violet islets on the
    waterline, and two palm clusters framing the scene."""
    global _static_sky
    sky = pygame.Surface((DW, DH))
    sky.blit(multistop_v(DW, DH, SKY_STOPS), (0, 0))

    # the low golden-hour sun, tucked upper-left so it FRAMES the village. Built
    # as a SELF-CONTAINED NORMAL-blend radial so it can never additively stack to
    # a white moon-blob (the round-2 fault): a warm gold core easing OUT through
    # amber to a transparent rim, painted from concentric radius rings.
    sx, sy = int(DW * 0.26), int(DH * 0.300)
    # halo UNDER the disc as a NORMAL-blend translucent radial (NOT additive):
    # additive glows desaturate to a white ring as their layers stack near the
    # disc edge (the round-2/3 fault). A normal-blend amber halo composites by
    # alpha, so it can only ever read as warm amber dissolving into the sky.
    halo_r = m(120)
    halo = pygame.Surface((halo_r * 2, halo_r * 2), pygame.SRCALPHA)
    for i in range(halo_r, 0, -1):
        t = i / halo_r
        # warm amber, fading from a soft inner glow to nothing at the rim
        a = int(150 * (1.0 - t) ** 2.2)
        pygame.draw.circle(halo, (255, 158, 88, a), (halo_r, halo_r), i)
    sky.blit(halo, (sx - halo_r, sy - halo_r))
    # the disc itself: an OPAQUE warm-gold body with a brighter core, drawn on
    # NORMAL blend so its colour is exactly the gold defined here. The rim is a
    # solid amber edge (no alpha feather) so the additive bloom can never bleed
    # through it as a bright cream band — the bloom lives only OUTSIDE the disc.
    disc_r = m(46)
    sun_disc = pygame.Surface((disc_r * 2, disc_r * 2), pygame.SRCALPHA)
    sun_stops = [
        (0.00, (255, 222, 150)),    # warm gold core — the hottest point
        (0.45, (255, 200, 116)),
        (0.78, (255, 174, 96)),     # body amber
        (1.00, (242, 150, 80)),     # solid amber rim (opaque, clean edge)
    ]
    for i in range(disc_r, 0, -1):
        t = i / disc_r          # i is the ring radius; t=0 core, t=1 rim
        for k in range(len(sun_stops) - 1):
            t0, c0 = sun_stops[k]
            t1, c1 = sun_stops[k + 1]
            if t0 <= t <= t1:
                f = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
                col = tuple(int(c0[j] + (c1[j] - c0[j]) * f) for j in range(3))
                break
        else:
            col = sun_stops[-1][1]
        # full alpha everywhere so the disc is a clean object; the outermost 2px
        # gets a soft anti-alias by the SS downscale, no manual feather needed.
        pygame.draw.circle(sun_disc, (*col, 255), (disc_r, disc_r), i)
    sky.blit(sun_disc, (sx - disc_r, sy - disc_r))

    # emerging dusk stars — only in the upper indigo band, fading out before the
    # warm haze so they never sparkle over daylight.
    rnd = random.Random(417)
    stars = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for _ in range(120):
        x = rnd.randint(0, DW)
        yf = rnd.uniform(0.0, 0.42)
        y = int(yf * DH)
        fade = max(0.0, 1.0 - yf / 0.42)
        r = m(rnd.uniform(0.4, 1.5))
        a = int(rnd.randint(40, 170) * fade)
        if a <= 0:
            continue
        tint = rnd.choice([(255, 252, 240), (224, 224, 255), (255, 236, 200)])
        pygame.draw.circle(stars, (*tint, a), (x, y), max(1, int(r)))
    for _ in range(9):
        x = rnd.randint(m(20), DW - m(20))
        y = int(rnd.uniform(0.04, 0.30) * DH)
        L = m(rnd.uniform(3, 5.5))
        a = rnd.randint(90, 160)
        col = (255, 244, 210, a)
        pygame.draw.line(stars, col, (x - L, y), (x + L, y), max(1, m(0.7)))
        pygame.draw.line(stars, col, (x, y - L), (x, y + L), max(1, m(0.7)))
    # carve the sun out of the star field so no sparkle speckles the gold disc
    # (a clean sun reads as a sun, not a star-pocked blob).
    pygame.draw.circle(stars, (0, 0, 0, 0), (sx, sy), int(disc_r * 1.35))
    sky.blit(stars, (0, 0), special_flags=pygame.BLEND_ADD)

    # back-row scrim: a soft cool atmospheric band across the lower sky (where
    # the back row's thatch ridges sit) so COSTUMES/ANIMALS/HATS read against
    # dusky sky, not against the sun's glow. A gentle dusk haze, peaking just
    # under the back-row rooflines and feathering out top + bottom.
    scrim = pygame.Surface((DW, DH), pygame.SRCALPHA)
    s0, s1 = 0.36, 0.50          # the back-row roofline band
    for y in range(int(s0 * DH), int(s1 * DH)):
        t = (y - s0 * DH) / ((s1 - s0) * DH)
        a = int(78 * max(0.0, math.sin(t * math.pi)) ** 0.9)
        pygame.draw.line(scrim, (40, 38, 78, a), (0, y), (DW, y))
    sky.blit(scrim, (0, 0))

    # distant hazy islets sitting on the waterline (depth cue behind the huts)
    horizon = int(DH * 0.485)
    for ix, iw, ih, tone in ((0.10, 0.22, 0.030, 0.55),
                             (0.40, 0.30, 0.044, 0.70),
                             (0.74, 0.26, 0.034, 0.50),
                             (0.92, 0.18, 0.024, 0.40)):
        cx = int(DW * ix)
        hw = int(DW * iw * 0.5)
        hh = int(DH * ih)
        col = lerp_color(ISLET, SKY_STOPS[4][1], 1.0 - tone)
        pts = [(cx - hw, horizon)]
        n = 8
        for k in range(n + 1):
            t = k / n
            x = cx - hw + int(2 * hw * t)
            bump = math.sin(t * math.pi) * hh * (0.6 + 0.4 * math.sin(t * 9 + ix * 20))
            pts.append((x, horizon - int(bump)))
        pts.append((cx + hw, horizon))
        pygame.draw.polygon(sky, col, pts)
        # haze veil so far islets sit back
        veil = pygame.Surface((DW, DH), pygame.SRCALPHA)
        pygame.draw.polygon(veil, (*SKY_STOPS[4][1], 70), pts)
        sky.blit(veil, (0, 0))

    _draw_palm(sky, int(DW * 0.045), int(DH * 0.50), m(150), flip=False, seed=2)
    _draw_palm(sky, int(DW * 0.965), int(DH * 0.505), m(168), flip=True, seed=7)

    _static_sky = sky


def _draw_palm(surf, base_x, base_y, height, flip, seed):
    """A silhouetted-but-lit coconut palm: a curved trunk + a crown of long
    drooping fronds, rim-lit on the top-left sun side, framing the lagoon."""
    rnd = random.Random(seed)
    sign = -1 if flip else 1
    # curved trunk — stacked tapering segments leaning toward the water
    segs = 9
    px, py = base_x, base_y
    pts_l, pts_r = [], []
    for i in range(segs + 1):
        t = i / segs
        lean = sign * math.sin(t * 1.3) * height * 0.22
        x = base_x + lean
        y = base_y - t * height
        wdt = m(9) * (1.0 - t * 0.55)
        pts_l.append((x - wdt, y))
        pts_r.append((x + wdt, y))
        px, py = x, y
    trunk = pts_l + pts_r[::-1]
    pygame.draw.polygon(surf, WOOD_LO, trunk)
    # lit left edge of the trunk
    pygame.draw.lines(surf, lerp_color(WOOD_LO, SUN_HALO, 0.4), False, pts_l,
                      max(1, m(1.6)))
    crown_x, crown_y = px, py
    # fronds — long drooping arcs radiating from the crown
    n_fronds = 9
    for k in range(n_fronds):
        a0 = math.radians(200 + k * (140 / (n_fronds - 1)))
        length = height * rnd.uniform(0.42, 0.60)
        droop = rnd.uniform(0.5, 0.95)
        midx = crown_x + math.cos(a0) * length * 0.5
        midy = crown_y + math.sin(a0) * length * 0.5 - length * 0.12
        endx = crown_x + math.cos(a0) * length
        endy = crown_y + math.sin(a0) * length + length * droop * 0.5
        # spine as a 3-point arc (quadratic-ish via segments)
        spine = []
        for s in range(11):
            tt = s / 10
            xx = (1 - tt) ** 2 * crown_x + 2 * (1 - tt) * tt * midx + tt ** 2 * endx
            yy = (1 - tt) ** 2 * crown_y + 2 * (1 - tt) * tt * midy + tt ** 2 * endy
            spine.append((xx, yy))
        lit = a0 < math.radians(270)        # left-facing fronds catch the sun
        col = PALM_FROND_HI if lit else PALM_FROND
        # leaflets along the spine give the frond body
        for s in range(1, len(spine)):
            x1, y1 = spine[s - 1]
            x2, y2 = spine[s]
            dx, dy = x2 - x1, y2 - y1
            nrm = math.hypot(dx, dy) or 1
            ox, oy = -dy / nrm, dx / nrm
            spread = m(7) * (1 - s / len(spine)) + m(3)
            pygame.draw.polygon(surf, col, [
                (x1, y1), (x2 + ox * spread, y2 + oy * spread),
                (x2, y2), (x2 - ox * spread, y2 - oy * spread)])
        pygame.draw.lines(surf, lerp_color(col, NEAR_BLACK, 0.35), False, spine,
                          max(1, m(1.0)))
    # a couple of coconuts at the crown
    for _ in range(3):
        cx = crown_x + rnd.randint(-m(6), m(6))
        cy = crown_y + rnd.randint(m(2), m(8))
        pygame.draw.circle(surf, (78, 54, 30), (int(cx), int(cy)), m(4))
        pygame.draw.circle(surf, (120, 88, 52), (int(cx - m(1)), int(cy - m(1))), m(2))


# =============================================================================
# Lagoon water — glitter band + soft hut reflections.
# =============================================================================
def draw_water(surf):
    """The gold lagoon: a multi-stop water gradient from a hot horizon down to
    a cool deep trough, a tapering gold sun-glitter band under the sun, and a
    field of horizontal wavelets that get sparser + dimmer with depth."""
    horizon = int(DH * 0.485)
    water_h = DH - horizon
    band = vgrad_stops(DW, water_h, 0, WATER_STOPS, 255)
    surf.blit(band, (0, horizon))

    # the gold sun-glitter column under the sun, widening with depth then
    # fading — the signature golden-hour-on-water read.
    sun_x = int(DW * 0.26)
    rnd = random.Random(91)
    glit = pygame.Surface((DW, water_h), pygame.SRCALPHA)
    rows = 56
    for i in range(rows):
        t = i / rows
        y = int(t * water_h)
        spread = m(20) + t * m(120)         # column widens toward viewer
        depth_fade = (1.0 - t) ** 0.8
        n = int(4 + t * 9)
        for _ in range(n):
            gx = sun_x + rnd.uniform(-spread, spread)
            falloff = max(0.0, 1.0 - abs(gx - sun_x) / (spread + 1))
            a = int(190 * falloff * depth_fade)
            if a <= 0:
                continue
            ln = m(rnd.uniform(2.5, 8)) * (0.5 + t)
            yy = y + rnd.randint(-m(2), m(2))
            pygame.draw.line(glit, (*GLITTER, a),
                             (gx - ln, yy), (gx + ln, yy), max(1, m(1.0)))
    surf.blit(glit, (0, horizon), special_flags=pygame.BLEND_ADD)

    # broad horizontal wavelets across the whole lagoon for surface texture
    waves = pygame.Surface((DW, water_h), pygame.SRCALPHA)
    for i in range(40):
        t = i / 40
        y = int(t * water_h)
        a = int(46 * (1.0 - t * 0.7))
        col = lerp_color(WATER_STOPS[0][1], WHITE, 0.3)
        seg = m(rnd.uniform(20, 70))
        x = rnd.randint(0, DW)
        for _ in range(rnd.randint(2, 5)):
            pygame.draw.line(waves, (*col, a), (x, y), (x + seg, y), max(1, m(0.8)))
            x += seg + m(rnd.uniform(30, 90))
            if x > DW:
                break
    surf.blit(waves, (0, horizon), special_flags=pygame.BLEND_ADD)
    return horizon


def hut_reflection(surf, cx, deck_y, width, scale, horizon):
    """A NATURAL water reflection of a hut: a cool, desaturated, low-alpha echo
    of the roof + body that fades with depth and is broken up by horizontal
    ripple gaps + a subtle side-to-side wobble — like real dusk water, never a
    coloured aura. NORMAL blend (darkens the water it sits on), never additive.

    The reflection mirrors the hut's value structure (warmer lit ridge near the
    top, cooling into the body echo below) so it reads as a true mirror image
    rather than a flat wash. It starts at the deck waterline and reaches down
    ~roughly the hut's own height."""
    refl_h = int(m(120) * scale)
    if refl_h <= 0 or deck_y < horizon:
        return
    col = pygame.Surface((width, refl_h), pygame.SRCALPHA)
    half = width / 2
    for y in range(refl_h):
        t = y / refl_h
        # warm ridge echo at the top easing into a cool muted body echo below,
        # then dissolving — a reflection loses energy fast on rippled water.
        tone = lerp_color(REFL_THATCH, REFL_HUT, min(1.0, t * 1.7))
        depth = (1.0 - t) ** 1.5
        # ripple gaps: thin horizontal bands where the water surface breaks the
        # image, so it never looks like a solid mirror smear.
        ripple = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(y / m(5.0)))
        a = int(46 * depth * ripple)
        if a <= 0:
            continue
        # gentle horizontal wobble + taper so edges feather into the water.
        wob = math.sin(y / m(13.0)) * m(4) * (1.0 - t)
        taper = half * (0.94 - 0.30 * t)
        x0 = half + wob - taper
        x1 = half + wob + taper
        pygame.draw.line(col, (*tone, a), (x0, y), (x1, y))
    surf.blit(col, (int(cx - half), deck_y))


# =============================================================================
# Stilt hut — the market stall as an over-water thatched hut.
# =============================================================================
def draw_stilts(surf, cx, deck_y, half_w, post_len):
    """The wooden posts the hut stands on, driven into the lagoon: four legs
    with cross-bracing, lit top-left, each with a contact ripple where it meets
    the water + a short submerged reflection. `post_len` is how far the posts
    drop below the deck into the water."""
    legs_x = [cx - half_w + m(6), cx - half_w + m(20),
              cx + half_w - m(20), cx + half_w - m(6)]
    water_y = deck_y + int(post_len * 0.74)
    foot_y = deck_y + post_len
    post_w = m(7)
    for i, lx in enumerate(legs_x):
        # post body — vertical gradient timber
        body = vgrad(post_w, foot_y - deck_y, 0, WOOD_HI, WOOD_LO)
        surf.blit(body, (lx - post_w // 2, deck_y))
        pygame.draw.rect(surf, WOOD_EDGE,
                         (lx - post_w // 2, deck_y, post_w, foot_y - deck_y),
                         width=max(1, m(1)))
        pygame.draw.line(surf, lerp_color(WOOD_HI, WHITE, 0.3),
                         (lx - post_w // 2 + m(1), deck_y),
                         (lx - post_w // 2 + m(1), foot_y), max(1, m(1)))
        # contact ripple at the waterline
        rr = m(11)
        rip = pygame.Surface((rr * 2, rr), pygame.SRCALPHA)
        pygame.draw.ellipse(rip, (*GLITTER, 120), (0, 0, rr * 2, rr), max(1, m(1.2)))
        pygame.draw.ellipse(rip, (*GLITTER, 60),
                            (m(3), m(2), rr * 2 - m(6), rr - m(4)), max(1, m(1)))
        surf.blit(rip, (lx - rr, water_y - rr // 2), special_flags=pygame.BLEND_ADD)
        # short submerged reflection of the post
        sub = vgrad(post_w, m(14), 0, WOOD_LO, WOOD_EDGE, alpha=110)
        surf.blit(sub, (lx - post_w // 2, water_y), special_flags=pygame.BLEND_ADD)
    # cross-bracing between the inner legs
    for a, b in ((legs_x[0], legs_x[1]), (legs_x[2], legs_x[3])):
        my = (deck_y + foot_y) // 2
        pygame.draw.line(surf, WOOD_MID, (a, deck_y + m(6)), (b, my + m(6)), max(1, m(3)))
        pygame.draw.line(surf, WOOD_MID, (a, my + m(6)), (b, deck_y + m(6)), max(1, m(3)))
    pygame.draw.line(surf, WOOD_LO, (legs_x[1], deck_y + m(10)),
                     (legs_x[2], deck_y + m(10)), max(1, m(3)))


def draw_plank(surf, x0, y0, x1, y1, width):
    """A little boardwalk plank linking two huts: a foreshortened timber strip
    with plank seams + a dark contact AO underneath."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    quad = [(x0 + nx * width / 2, y0 + ny * width / 2),
            (x1 + nx * width / 2, y1 + ny * width / 2),
            (x1 - nx * width / 2, y1 - ny * width / 2),
            (x0 - nx * width / 2, y0 - ny * width / 2)]
    # contact shadow on the water below
    sh = [(px, py + m(5)) for px, py in quad]
    shs = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pygame.draw.polygon(shs, (0, 0, 0, 90), sh)
    surf.blit(shs, (0, 0))
    pygame.draw.polygon(surf, WOOD_MID, quad)
    pygame.draw.polygon(surf, WOOD_EDGE, quad, width=max(1, m(1.4)))
    # plank seams across the run
    for s in range(1, 6):
        t = s / 6
        ax = x0 + dx * t + nx * width / 2
        ay = y0 + dy * t + ny * width / 2
        bx = x0 + dx * t - nx * width / 2
        by = y0 + dy * t - ny * width / 2
        pygame.draw.line(surf, WOOD_LO, (ax, ay), (bx, by), max(1, m(1)))
    # lit top edge
    pygame.draw.line(surf, WOOD_HI, quad[0], quad[1], max(1, m(1.4)))


def draw_hut(surf, cx, deck_y, scale, group, label, hero=False):
    """One stilt-market hut, drawn back-to-front so it reads as a solid lit
    object over water:

      thatched roof (lit ridge -> shaded eaves)  ->  striped macaw-red/cream
      awning front  ->  a shaded stall interior carrying a glass cabochon with
      the category's REAL preview thumbnail  ->  a bold gold-keyline label.

    `hero` (PARCELS) glows red as the mystery stall. Returns the hut's footprint
    so the caller can wire reflections + tap-target bookkeeping."""
    half_w = int(m(58) * scale)
    body_h = int(m(64) * scale)
    roof_h = int(m(40) * scale)
    eave = int(m(10) * scale)

    body_top = deck_y - body_h
    roof_apex_y = body_top - roof_h

    # ── soft seat under the whole hut so it sits ON the deck ──
    # The hero gets a restrained WARM-GOLD halo (the store's coin hue) so it
    # reads as "the prize stall", never a red sun-aura bleeding onto the water.
    if hero:
        soft_glow(surf, cx, body_top + int(body_h * 0.42), int(half_w * 1.25),
                  MYST_GOLD, 34, layers=12)
    soft_glow(surf, cx, deck_y, half_w + eave, (0, 0, 0), 110, layers=6)

    # ── stall body (shaded interior box behind the awning) ──
    body_rect = pygame.Rect(cx - half_w, body_top, half_w * 2, body_h)
    surf.blit(vgrad(body_rect.w, body_rect.h, 0,
                    lerp_color(STALL_DARK, WOOD_MID, 0.25), STALL_DARK),
              body_rect.topleft)
    # corner posts of the stall
    for px in (body_rect.left, body_rect.right - m(8)):
        pygame.draw.rect(surf, WOOD_LO, (px, body_top, m(8), body_h))
        pygame.draw.line(surf, WOOD_HI, (px + m(1), body_top),
                         (px + m(1), deck_y), max(1, m(1)))

    # ── thatched roof: a broad triangle with layered straw courses ──
    rl = (cx - half_w - eave, body_top)
    rr = (cx + half_w + eave, body_top)
    apex = (cx, roof_apex_y)
    # roof drop shadow onto the stall front
    shs = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pygame.draw.polygon(shs, (0, 0, 0, 80),
                        [(rl[0], rl[1] + m(6)), (rr[0], rr[1] + m(6)),
                         (apex[0], apex[1] + m(6))])
    surf.blit(shs, (0, 0))
    # base roof fill (vertical-ish straw gradient via stacked courses)
    courses = 9
    for i in range(courses):
        t0 = i / courses
        t1 = (i + 1) / courses
        # interpolate the two base corners up toward the apex
        y_lo = body_top - (body_top - roof_apex_y) * t0
        y_hi = body_top - (body_top - roof_apex_y) * t1
        xl0 = rl[0] + (apex[0] - rl[0]) * t0
        xr0 = rr[0] + (apex[0] - rr[0]) * t0
        xl1 = rl[0] + (apex[0] - rl[0]) * t1
        xr1 = rr[0] + (apex[0] - rr[0]) * t1
        col = lerp_color(THATCH_LO, THATCH_HI, 1.0 - t0)   # eaves dark, ridge lit
        pygame.draw.polygon(surf, col, [(xl0, y_lo), (xr0, y_lo),
                                        (xr1, y_hi), (xl1, y_hi)])
        # ragged straw fringe along the lower edge of each course
        fringe_n = 18
        for f in range(fringe_n):
            ft = f / fringe_n
            fx = xl0 + (xr0 - xl0) * ft
            drop = m(3) * scale * (0.5 + 0.5 * math.sin(f * 2.3 + i))
            pygame.draw.line(surf, lerp_color(col, THATCH_EDGE, 0.5),
                             (fx, y_lo), (fx, y_lo + drop), max(1, m(0.8)))
    # lit top-left face of the roof + ridge highlight
    lit = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pygame.draw.polygon(lit, (*lerp_color(THATCH_HI, WHITE, 0.25), 90),
                        [rl, apex, (cx, body_top)])
    surf.blit(lit, (0, 0))
    pygame.draw.line(surf, THATCH_EDGE, rl, apex, max(1, m(1.6)))
    pygame.draw.line(surf, THATCH_EDGE, rr, apex, max(1, m(1.6)))
    pygame.draw.line(surf, lerp_color(THATCH_HI, WHITE, 0.4),
                     rl, apex, max(1, m(1.0)))
    # a little roof finial / topknot
    pygame.draw.circle(surf, THATCH_EDGE, apex, m(4))
    pygame.draw.circle(surf, THATCH_HI, (apex[0] - m(1), apex[1] - m(1)), m(2))

    # ── striped awning valance hanging under the eaves ──
    awn_y = body_top
    awn_h = int(m(15) * scale)
    stripe_w = max(m(8), int((half_w * 2) / 9))
    awn_surf = pygame.Surface((half_w * 2, awn_h), pygame.SRCALPHA)
    n_str = int((half_w * 2) // stripe_w) + 1
    for s in range(n_str):
        c_top = AWN_RED if s % 2 == 0 else AWN_CREAM
        c_bot = AWN_RED_D if s % 2 == 0 else AWN_CREAM_D
        sx = s * stripe_w
        col = vgrad(stripe_w, awn_h, 0, c_top, c_bot)
        awn_surf.blit(col, (sx, 0))
    # scalloped lower edge
    mask = pygame.Surface((half_w * 2, awn_h), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 255))
    scallop_r = stripe_w // 2
    for s in range(n_str + 1):
        cxs = s * stripe_w
        pygame.draw.circle(mask, (0, 0, 0, 0), (cxs, awn_h), scallop_r)
    awn_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(awn_surf, (cx - half_w, awn_y))
    pygame.draw.line(surf, (0, 0, 0, 120), (cx - half_w, awn_y),
                     (cx + half_w, awn_y), max(1, m(1)))

    # ── deck the hut stands on (front lip of the stilt platform) ──
    deck_rect = pygame.Rect(cx - half_w - m(4), deck_y - m(8),
                            half_w * 2 + m(8), m(10))
    surf.blit(vgrad(deck_rect.w, deck_rect.h, 0, WOOD_HI, WOOD_LO),
              deck_rect.topleft)
    pygame.draw.rect(surf, WOOD_EDGE, deck_rect, width=max(1, m(1)))
    for s in range(1, 8):
        sx = deck_rect.left + deck_rect.w * s // 8
        pygame.draw.line(surf, WOOD_LO, (sx, deck_rect.top),
                         (sx, deck_rect.bottom), max(1, m(0.8)))

    # ── glass cabochon holding the category's real preview thumbnail ──
    # Domes are floored to a minimum radius so the BACK ROW (smallest scale)
    # still carries an identifiable preview; the hero dome is the largest.
    if hero:
        dome_r = int(m(29) * scale)
    else:
        dome_r = max(m(24), int(m(28) * scale))
    dome_cx = cx
    dome_cy = body_top + int(body_h * (0.40 if hero else 0.46))
    soft_glow(surf, dome_cx, dome_cy, dome_r + m(6), GOLD,
              46 if hero else 34, layers=8)
    # SHADES is the one dark-on-dark preview (dark sunglasses on a dark parrot):
    # against the near-black dome well it collapses in value. Give it a LIGHTER
    # cool-slate dome backing so the eyewear reads as a positive shape like the
    # other previews; everything else keeps the standard deep glass well.
    if group == "shades" and not hero:
        C.cabochon(surf, dome_cx, dome_cy, dome_r, (96, 104, 134), (44, 50, 78))
    else:
        C.cabochon(surf, dome_cx, dome_cy, dome_r, C.CABO_LO, C.CABO_HI)
    _place_thumb(surf, group, dome_cx, dome_cy, dome_r, hero)
    # Hero glass takes a warm GOLD tint (was mystery-red) so the prize dome stays
    # in the warm-gold family the rest of the village + the coin live in.
    C.cabochon_glass(surf, dome_cx, dome_cy, dome_r,
                     tint=(255, 222, 168) if hero else (240, 224, 196))

    # ── bold gold-keyline category label on a small banner under the dome ──
    # The hero's board is deferred to render_device (drawn AFTER Pip + the coin)
    # so it sits frontmost in a clean horizontal lane with nothing crossing it.
    if not hero:
        # nudged ~3px lower so the board clears the awning/roof-eave shadow above
        # it (it was kissing that shadow on the back row).
        _hut_label(surf, label, cx, deck_y - int(m(16) * scale), scale, hero)

    return half_w, roof_apex_y


def _place_thumb(surf, group, cx, cy, dome_r, hero):
    """Drop the category's REAL preview into the dome, contained (letterboxed)
    so aspect-extreme items (flip-flops, party hat) sit fully inside the glass
    instead of being clipped. The PARCELS hero shows a glowing red '?' mystery
    mark instead of a literal thumbnail."""
    if hero:
        # Re-branded mystery: a GOLD-BANDED CRATE behind a bold gold "?" — the
        # mystery now reads by SHAPE + GOLD (the store's prize hue), never a red
        # sun-aura. Drawn inside the dark glass dome so the warm gold pops.
        _draw_mystery_crate(surf, cx, cy, dome_r)
        return
    src, letterbox = _group_thumb(group)
    w, h = src.get_size()
    # Previews enlarged ~22% over R1 so the category item is identifiable at 1x;
    # aspect-extreme items (flip-flops, party hat) still get a tighter contain
    # factor so the long axis stays fully inside the glass.
    box = dome_r * (1.62 if letterbox else 1.84)
    s = box / max(w, h)
    img = pygame.transform.smoothscale(
        src, (max(1, int(w * s)), max(1, int(h * s))))
    # lift value off the dark dome + a crisp top-left rim light (the locked
    # CONSTELLATION thumbnail treatment) so it reads as the lit hero in glass.
    img = C._punch_contrast(img)
    r = img.get_rect(center=(cx, cy))
    # SHADES' dark lenses need an extra GOLD key rim (on top of the standard
    # rim light) so the eyewear silhouette pops off its slate backing rather
    # than melting into it — the difference between "reads" and "near-reads".
    if group == "shades":
        surf.blit(C._rim_light(img, color=(255, 224, 150), alpha=210),
                  r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(C._rim_light(img), r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(img, r.topleft)


def _draw_mystery_crate(surf, cx, cy, dome_r):
    """The PARCELS prize, drawn inside its glass dome: a small dark crate bound
    by warm GOLD bands with a bold gold "?" floating over it. This carries the
    'mystery' by SHAPE + GOLD only — there is no red anywhere, so the village
    casts no scarlet aura. Gold band + dark crate + value contrast keep the "?"
    legible (red/green-blind safe)."""
    cw = int(dome_r * 1.30)
    ch = int(dome_r * 1.14)
    rect = pygame.Rect(cx - cw // 2, cy - ch // 2 + m(3), cw, ch)
    # crate body — dark warm timber so the gold bands read as the hero accent
    surf.blit(vgrad(rect.w, rect.h, m(2), (58, 42, 30), (30, 20, 14)),
              rect.topleft)
    pygame.draw.rect(surf, (18, 12, 8), rect, width=max(1, m(1.4)),
                     border_radius=m(2))
    # gold strap bands (vertical + horizontal) with a lit top edge each
    band_w = max(m(4), int(cw * 0.13))
    for bx in (rect.left + int(cw * 0.20), rect.right - int(cw * 0.20) - band_w):
        b = pygame.Rect(bx, rect.top, band_w, rect.h)
        surf.blit(vgrad(b.w, b.h, 0, MYST_GOLD, MYST_GOLD_D), b.topleft)
        pygame.draw.line(surf, (255, 240, 200), (b.left + m(1), b.top),
                         (b.left + m(1), b.bottom), max(1, m(0.8)))
    by = rect.centery - band_w // 2
    hb = pygame.Rect(rect.left, by, rect.w, band_w)
    surf.blit(vgrad(hb.w, hb.h, 0, MYST_GOLD, MYST_GOLD_D), hb.topleft)
    pygame.draw.line(surf, (255, 240, 200), (hb.left, hb.top + m(1)),
                     (hb.right, hb.top + m(1)), max(1, m(0.8)))
    # a gold rivet where the straps cross
    for sx in (rect.left + int(cw * 0.20) + band_w // 2,
               rect.right - int(cw * 0.20) - band_w // 2):
        pygame.draw.circle(surf, (255, 244, 206), (sx, rect.centery), max(1, m(1.6)))
    # bold gold "?" centred on the crate, dark contour for contrast so it reads
    # by SHAPE + VALUE (red/green-blind safe) — the prize mark, all gold.
    from game.surprise_box_variants import _draw_qmark
    _draw_qmark(surf, cx, cy - m(1), dome_r + m(1),
                MYST_GOLD, (22, 12, 6), thick=m(2.8))


def _hut_label(surf, label, cx, cy, scale, hero):
    """A small carved-timber name board under the dome carrying the category in
    bold gradient gold with a dark keyline — the canonical defined-edge label."""
    f = font(11 * scale)
    tw = _glyph_base(label, f, m(0.6)).get_width()
    pad = int(m(12) * scale)
    bw = tw + pad * 2
    bh = int(m(20) * scale)
    r = pygame.Rect(cx - bw // 2, cy - bh // 2, bw, bh)
    rad = bh // 2
    drop_shadow(surf, r, rad, blur=m(4), alpha=120, dy=m(2))
    # board body: dark timber for normal stalls; the hero echoes the STORE
    # header's gold-on-deep-red (the store identity) so PARCELS reads as the
    # prize banner — GOLD type on a deep-red board, a tiny crisp object that
    # nothing glows out from.
    if hero:
        surf.blit(vgrad(r.w, r.h, rad, (132, 28, 30), (78, 14, 16)), r.topleft)
        rim_d, rim_b = (50, 8, 10), (*GOLD_PALE, 235)
        txt_top, txt_bot, key = GOLD_A_TOP, GOLD_A_BOT, (60, 10, 8)
    else:
        surf.blit(vgrad(r.w, r.h, rad, (44, 30, 18), (24, 15, 8)), r.topleft)
        rim_d, rim_b = (60, 38, 14), (*GOLD_PALE, 230)
        txt_top, txt_bot, key = GOLD_A_TOP, GOLD_A_BOT, LABEL_KEY
    top_sheen(surf, r, rad, bh // 2, peak=46)
    pygame.draw.rect(surf, (0, 0, 0, 180), r, width=max(1, m(1.4)),
                     border_radius=rad)
    bevel_rim(surf, r, rad, rim_d, rim_b, w=max(1, m(1.2)))
    gradient_text(surf, label, f, r.center, txt_top, txt_bot,
                  weight=m(1.0 * scale), keyline=key, kw=m(1.0), shadow=False,
                  tracking=m(0.6))


# =============================================================================
# Pip — the jetty merchant on the central stilt-jetty, with a spinning coin.
# =============================================================================
def draw_pip(surf, cx, deck_y):
    """Pip selling from the central jetty: the real macaw scaled up, with a warm
    sun aura + contact shadow + a spinning gold coin floating beside him, all
    clear of the hut labels."""
    pip = parrot.get_parrot(1, 0.0)
    pw, ph = pip.get_size()
    target = m(38)
    s = target / max(pw, ph)
    pip = pygame.transform.smoothscale(pip, (int(pw * s), int(ph * s)))
    pr = pip.get_rect()
    # Pip stands at the FRONT-LEFT corner of the jetty deck — pushed further
    # left + DOWN off the deck lip than R3 so his silhouette FULLY clears the
    # gold crate behind/above (crate-first, merchant-second front-to-back read)
    # rather than merging with the crate face at the same value.
    px = cx - m(42)
    py = deck_y - pr.height // 2 + m(13)
    # warm aura behind Pip
    soft_glow(surf, px, py, m(26), SUN_AURA, 56, layers=10)
    soft_glow(surf, px, py, m(15), SUN_CORE, 78, layers=6)
    # a dark separation halo hugging Pip so his lit silhouette pops off the
    # crate face it sits in front of (a thin dark contour, not a cast shadow).
    sep = pygame.Surface((pr.width + m(10), pr.height + m(10)), pygame.SRCALPHA)
    pygame.draw.ellipse(sep, (8, 6, 14, 150), sep.get_rect())
    surf.blit(sep, (px - sep.get_width() // 2, py - sep.get_height() // 2))
    # darker + wider contact shadow on the jetty deck so he grounds clearly
    sh = pygame.Surface((pr.width + m(10), m(13)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 175), sh.get_rect())
    surf.blit(sh, (px - (pr.width + m(10)) // 2, deck_y + m(1)))
    surf.blit(pip, pip.get_rect(center=(px, py)).topleft)
    # a small spinning coin floating to Pip's upper-LEFT, well clear of the dome
    # rim + the name board (foreshortened => a thin ellipse, reads mid-spin).
    coin_cx, coin_cy = px - m(22), py - m(20)
    soft_glow(surf, coin_cx, coin_cy, m(11), (255, 206, 92), 70, layers=8)
    face = _spin_coin(m(7), squash=0.45)
    surf.blit(face, face.get_rect(center=(coin_cx, coin_cy)).topleft)
    for dx, dy, L in ((m(8), -m(6), m(3)), (-m(7), m(5), m(2.5))):
        sx, sy = coin_cx + dx, coin_cy + dy
        pygame.draw.line(surf, (255, 246, 210), (sx - L, sy), (sx + L, sy), max(1, m(1)))
        pygame.draw.line(surf, (255, 246, 210), (sx, sy - L), (sx, sy + L), max(1, m(1)))


def _spin_coin(r, squash):
    """The real in-game coin squashed horizontally to read as mid-spin (a thin
    ellipse) — reuses entities._get_coin_face so the jetty coin is the exact
    coin the player collects."""
    from game.entities import _get_coin_face
    face = _get_coin_face()
    d = max(2, int(r * 2))
    img = pygame.transform.smoothscale(face, (max(2, int(d * squash)), d))
    return img


# =============================================================================
# Header — STORE wordmark + balance capsule + TAP A STALL hint.
# =============================================================================
def draw_header(surf):
    """The Skybit gold-on-red STORE wordmark, a recessed gold balance capsule
    carrying the REAL in-game coin + gradient-gold number, and the TAP A STALL
    call-to-action — all on a soft darkening band so the chrome stays legible
    over the bright golden-hour sky."""
    band = pygame.Surface((DW, m(126)), pygame.SRCALPHA)
    for y in range(m(126)):
        a = int(150 * (1 - y / m(126)) ** 1.25)
        pygame.draw.line(band, (10, 10, 34, a), (0, y), (DW, y))
    surf.blit(band, (0, 0))
    # screen frame hairline (matches the stall screen)
    pygame.draw.rect(surf, (*GOLD, 60), (m(3), m(3), DW - m(6), DH - m(6)),
                     width=max(1, m(1)), border_radius=m(12))
    title_wordmark(surf, "STORE", (DW // 2, m(26)), 30, tracking=m(4))
    _balance_capsule(surf, DW // 2, m(66))
    _tap_hint(surf, DW // 2, m(112))


def _tap_hint(surf, cx, cy):
    """The TAP A STALL call-to-action promoted onto its own faint gold-ruled
    chip with clear air under the capsule so it reads as the CTA, not a caption:
    a low-alpha recessed pill, a hairline gold rim, and bright gradient-gold
    type flanked by short gold rules."""
    f = font(11)
    tw = _glyph_base("TAP  A  STALL", f, m(3)).get_width()
    pad = m(20)
    w = tw + pad * 2
    h = m(26)
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    rad = h // 2
    # faint recessed chip body so the CTA sits in its own object
    chip = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(chip, (18, 14, 10, 150), chip.get_rect(), border_radius=rad)
    surf.blit(chip, r.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 150), r, width=max(1, m(1.2)),
                     border_radius=rad)
    pygame.draw.rect(surf, (*GOLD, 150), r.inflate(-m(1.2), -m(1.2)),
                     width=max(1, m(1)), border_radius=rad)
    # short gold rules flanking the type — committed to a brighter pale-gold at
    # +value + thicker so they read as intentional rules, not hairline noise.
    gold_rule(surf, r.x + m(8), r.x + m(8) + m(16), cy, GOLD_PALE, peak=235,
              thick=m(1.6))
    gold_rule(surf, r.right - m(8) - m(16), r.right - m(8), cy, GOLD_PALE,
              peak=235, thick=m(1.6))
    gradient_text(surf, "TAP  A  STALL", f, (cx, cy), GOLD_A_TOP, GOLD_A_BOT,
                  weight=m(0.9), keyline=(40, 22, 12), kw=m(0.9), shadow=False,
                  tracking=m(3))


def _balance_capsule(surf, cx, y):
    """The CONSTELLATION balance capsule, reused verbatim in spirit: a recessed
    gold capsule with the REAL coin in its own cell + a loud gradient-gold
    number, crisp double rim — the shared money read across both screens."""
    val = f"{BALANCE:,}"
    vf = font(25)
    vw = _glyph_base(val, vf, 0).get_width() + m(2)
    coin_d, gapc, padl, padr = m(28), m(18), m(15), m(22)
    w = padl + coin_d + gapc + vw + padr
    h = m(44)
    cap = pygame.Rect(cx - w // 2, y - h // 2, w, h)
    drop_shadow(surf, cap, h // 2, blur=m(6), alpha=130, dy=m(3))
    surf.blit(vgrad(cap.w, cap.h, h // 2, (58, 42, 22), (22, 15, 8), 255, gamma=1.1),
              cap.topleft)
    top_sheen(surf, cap, h // 2, m(16), peak=50)
    C.contact_shadow(surf, cap, h // 2, m(5), alpha=110)
    pygame.draw.rect(surf, (0, 0, 0, 200), cap, width=max(1, m(1.8)),
                     border_radius=h // 2)
    bevel_rim(surf, cap, h // 2, lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD_PALE, 240), w=max(1, m(1.8)))
    x = cap.x + padl
    soft_glow(surf, x + coin_d // 2, y, int(coin_d * 0.40), (255, 206, 92), 42, layers=6)
    coin_glyph(surf, x + coin_d // 2, y, coin_d // 2)
    x += coin_d + gapc
    gradient_text(surf, val, vf, (x + vw // 2, y), GOLD_A_TOP, GOLD_A_BOT,
                  weight=m(1.0), keyline=(96, 56, 12), kw=m(1.2), shadow=True)


# =============================================================================
# Compose — the staggered two-tier stilt-village over the lagoon.
# =============================================================================
# Tidy two-tier arrangement so all 7 huts read at 360px without overlap:
#  back row (smaller, set higher + deeper): COSTUMES, ANIMALS, HATS
#  middle row (3 huts): PARROTS, SHOES, SHADES
#  hero on the central jetty (largest, frontmost): PARCELS
# Each hut's deck sits on the lagoon; back-to-front draw order gives depth.
LAYOUT = [
    # group,      cx fraction, deck_y fraction, scale, hero
    # All 7 huts enlarged + spread so each reads confidently at 360px with its
    # category dome. With the sun shrunk + lifted, the village owns the lower
    # two-thirds. Three clean tiers + a frontmost hero; back-row scale lifted
    # 0.68->0.80 and mid-row 0.84/0.76->0.92/0.86 so no stall feels tucked-away.
    # The two outer huts of each non-hero row are pulled to the canvas edges and
    # the centre hut sits a touch higher so all three roofs stay separated.
    ("costume",  0.155, 0.572, 0.80, False),   # back-left
    ("animal",   0.500, 0.548, 0.80, False),   # back-centre (lifted)
    ("hats",     0.845, 0.572, 0.80, False),   # back-right
    # PARROTS + SHOES pulled ~8px further to the canvas edges so a clear
    # dark-water gutter separates them from the lifted hero deck (was 0.180 /
    # 0.820 — they crowded the hero, reading as one central mass).
    ("parrot",   0.142, 0.788, 0.92, False),   # mid-left
    ("shoes",    0.858, 0.788, 0.92, False),   # mid-right
    ("shades",   0.500, 0.704, 0.86, False),   # mid-centre, tucked slightly back
    ("parcels",  0.500, 0.862, 0.96, True),    # hero jetty, frontmost (deck shaved)
]
LABELS = {g: lbl for g, lbl in STALLS}


def render_device():
    surf = pygame.Surface((DW, DH))
    surf.blit(_static_sky, (0, 0))
    horizon = draw_water(surf)

    # Resolve every hut footprint first (for planks + reflections), then draw
    # back-to-front so nearer huts overlap farther ones for real depth.
    huts = []
    for group, fx, fy, scale, hero in LAYOUT:
        cx = int(DW * fx)
        deck_y = int(DH * fy)
        huts.append(dict(group=group, label=LABELS[group], cx=cx, deck_y=deck_y,
                         scale=scale, hero=hero))

    order = sorted(range(len(huts)), key=lambda i: huts[i]["deck_y"])

    # boardwalk planks linking the village (drawn under the huts/stilts so the
    # decks sit on top of them) — a few foreshortened connectors.
    plank_links = [(0, 3), (1, 5), (2, 4), (3, 5), (4, 5), (5, 6)]
    for a, b in plank_links:
        ha, hb = huts[a], huts[b]
        draw_plank(surf, ha["cx"], ha["deck_y"] - m(2),
                   hb["cx"], hb["deck_y"] - m(2), int(m(16)))

    for i in order:
        h = huts[i]
        half_w = int(m(58) * h["scale"])
        # natural cool reflection under the hut on the water (drawn before the
        # stilts/hut). No red tint, no additive blend, no hero exception — the
        # mystery is carried by GOLD + shape on the hut itself, not the water.
        hut_reflection(surf, h["cx"], h["deck_y"], int(half_w * 1.7),
                       h["scale"], horizon)
        # posts drop from the deck into the water; deeper (lower) huts sit on
        # shorter posts since their deck is already near the waterline.
        post_len = max(m(26), int(m(70) * h["scale"]))
        draw_stilts(surf, h["cx"], h["deck_y"], half_w, post_len)
        draw_hut(surf, h["cx"], h["deck_y"], h["scale"], h["group"],
                 h["label"], hero=h["hero"])
        if h["hero"]:
            # Pip stands on the hero jetty deck, in front of the PARCELS hut;
            # then the name board is stamped frontmost on the deck front so it
            # owns a clean horizontal lane that nothing crosses.
            draw_pip(surf, h["cx"], h["deck_y"] - m(2))
            _hut_label(surf, h["label"], h["cx"], h["deck_y"] + m(8),
                       h["scale"], True)

    draw_header(surf)

    # a faint warm vignette so the bright sky doesn't blow the screen edges +
    # keeps the chrome readable (matches the store's controlled-edge ground)
    vig = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for y in range(DH):
        f = y / DH
        a = 0
        if f < 0.10:
            a += int(70 * (1 - f / 0.10) ** 1.4)
        edge = 0
        pygame.draw.line(vig, (8, 6, 24, a), (0, y), (DW, y))
    surf.blit(vig, (0, 0))
    # left/right edge falloff
    side = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for x in range(DW):
        d = abs(x - DW / 2) / (DW / 2)
        a = int(48 * d ** 2.4)
        pygame.draw.line(side, (8, 6, 24, a), (x, 0), (x, DH))
    surf.blit(side, (0, 0))
    return surf


def main():
    _build_static_sky()
    dev = render_device()
    pygame.image.save(downscale(dev, 1), os.path.join(_HERE, "round_3.png"))
    pygame.image.save(downscale(dev, 2), os.path.join(_HERE, "round_3@2x.png"))
    print("SS =", SS, "device =", DW, "x", DH)
    print("saved round_3.png (360x640) + round_3@2x.png (720x1280)")


if __name__ == "__main__":
    main()
