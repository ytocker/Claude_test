"""
FLOATING SKY-BAZAAR — store landing HUB mockup (concept #3), round 2.

A flying game deserves a flying shop. Seven category stalls perch on golden
cloud platforms zig-zagging down a twilight portrait; thin gold rope-bridges
link them top-to-bottom and Pip hovers mid-frame in his natural flap pose as
the un-grounded flying vendor. The sky opens at golden hour up top and converges
toward the indigo night-jewel palette at the foot so the push into the
constellation jewel store is a seamless dissolve.

Round-2 polish raises it from good to premium: the cloud platforms are now
sculpted SOLID lit volumes (a top sheen crown + a bottom ambient-occlusion
shelf + a crisp continuous gold under-rim) lit from ONE top-left key, the seven
stalls are evenly bedded with generous padding, every preview is contained in
its dome (extreme-aspect items letterboxed, the NO-SHADES category fronted by a
clean synthetic aviator-shades icon instead of a bare base parrot), Pip carries
a clear focal spotlight clear of the labels, and the sky reads as a warm
golden-hour foot easing into the indigo-and-gold jewel-store nebula at the apex
where the stars emerge.

Authored resolution-independently at SS=4 (1440x2560 device canvas) with ONE
smoothscale down to 360x640, exactly like the constellation hi-res store — the
downscale is what turns oversized geometry into razor-crisp anti-aliased edges.
All primitives + palette anchors are REUSED from
docs/store_redesign/constellation_hi/render_hi.py (m, font, vgrad, vgrad_stops,
gold_a_fill, soft_glow, drop_shadow, gradient_text, plain_text, facet_gem,
cabochon, cabochon_glass, coin_glyph, bevel_rim, top_sheen, gold_rule,
title_wordmark, GOLD, GOLD_PALE, RARITY, NEAR_BLACK, WHITE, downscale) so the
bazaar coheres with the jewel store. Cloud platforms + rope-bridges are the only
new world art, drawn from gradient + glow + line primitives.

Both build targets safe: pure pygame, no numpy, no desktop/browser-only API.
Headless docs prototype — NOT wired into the game.
"""
import os
import sys
import math
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_CONST = os.path.join(_ROOT, "docs", "store_redesign", "constellation_hi")
for p in (_ROOT, _CONST):
    if p not in sys.path:
        sys.path.insert(0, p)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# Reuse the ENTIRE constellation-hi toolbox so this sheet shares the jewel
# store's exact gold, gems, glass, coin, type treatment and SS pipeline.
import render_hi as C
from render_hi import (
    SS, DW, DH, m, mf, font, vgrad, vgrad_stops, gold_a_fill, soft_glow,
    drop_shadow, gradient_text, plain_text, facet_gem, cabochon, cabochon_glass,
    coin_glyph, bevel_rim, top_sheen, gold_rule, title_wordmark, multistop_v,
    gloss_sweep, contact_shadow, _glyph_base, downscale,
    GOLD, GOLD_PALE, GOLD_DEEP, RARITY, MYSTERY, NEAR_BLACK, WHITE, CREAM,
    GOLD_A_TOP, GOLD_A_BOT, GOLD_A_STOPS, GOLD_A_NUM, GOLD_A_RIM_DARK,
    GOLD_A_RIM_BRIGHT, GOLD_A_COIN_RIM, CARD_RING_BRIGHT, CARD_RING_DEEP,
    TITLE_OUT,
)
from game.draw import lerp_color
from game import parrot
from game import store_catalog


# ── twilight sky palette ──────────────────────────────────────────────────────
# Golden-hour up top deepening to the constellation indigo at the foot, so the
# screen reads "high above the play world at dusk" yet still lands the player in
# the jewel store's night sky. The low band keeps the warm sunset glow of the
# play world's golden hour; the apex is the jewel nebula's deep indigo.
SKY_STOPS = [
    (0.00, (20, 18, 58)),     # indigo apex  (jewel-store nebula top)
    (0.22, (40, 30, 86)),     # violet upper
    (0.42, (84, 52, 108)),    # dusk plum
    (0.60, (170, 92, 110)),   # rose mid-horizon
    (0.78, (236, 146, 96)),   # warm sunset band
    (1.00, (255, 196, 112)),  # golden-hour foot glow
]
SUN_GLOW = (255, 206, 130)    # the low golden-hour sun bloom
HAZE = (255, 210, 150)        # warm horizon haze
# Cloud volume ramp — ONE top-left key. A bright warm-cream crown rolls through
# a dusk-rose mid into a deep violet underbelly so each platform reads as a solid
# lit dome, not a flat puff. Gold rim/under-rim wrap it as the premium keyline.
CLOUD_RIM = (255, 234, 176)   # warm-gold rim-light on the lit crown
CLOUD_UNDERRIM = (255, 198, 120)  # hotter gold under-rim catching the foot glow
CLOUD_CROWN = (255, 247, 232)  # hot lit crown (top-left key)
CLOUD_HI = (244, 226, 214)    # lit body (warm cream)
CLOUD_MID = (196, 162, 184)   # cloud mid (dusk-rose)
CLOUD_LO = (104, 80, 124)     # cloud underbelly shadow (violet AO)
CLOUD_LO2 = (70, 52, 92)      # deepest keel shadow

# Stall categories in store order, each with its display label + group key.
# The preview thumbnail is the group's representative paid item ([0] of the
# group), exactly as the live store would seed a category tile.
STALLS = [
    ("COSTUMES", "costume"),
    ("PARROTS",  "parrot"),
    ("ANIMALS",  "animal"),
    ("SHOES",    "shoes"),
    ("HATS",     "hats"),
    ("SHADES",   "shades"),
    ("PARCELS",  "parcels"),
]

BALANCE = 14250


def preview_id(group):
    """The representative paid item that fronts a category stall."""
    ids = store_catalog.ids_of_group(group)
    return ids[0] if ids else None


# =============================================================================
# Background — twilight sky, golden-hour sun, distant clouds + a sparse star bed
# =============================================================================
_bg_static = None


def _build_bg():
    """Pre-bake the static twilight bed: gradient sky, low golden-hour sun bloom,
    a few far parallax clouds drifting below, and a faint upper star field that
    only emerges in the indigo apex (the night-jewel hand-off)."""
    global _bg_static
    bg = pygame.Surface((DW, DH))
    bg.blit(multistop_v(DW, DH, SKY_STOPS), (0, 0))

    # the indigo-and-gold jewel-store nebula seeded in the APEX so entering a
    # stall dissolves cohesively into the constellation store: a soft violet bloom
    # high-centre with a faint warm-gold core, kept low + tight so it never mushes.
    soft_glow(bg, int(DW * 0.50), int(DH * 0.12), m(190), (66, 56, 140), 40, layers=12)
    soft_glow(bg, int(DW * 0.40), int(DH * 0.07), m(110), (150, 120, 90), 26, layers=10)
    soft_glow(bg, int(DW * 0.66), int(DH * 0.17), m(90), (120, 90, 160), 28, layers=8)

    # low golden-hour sun bloom pushed to the lower-RIGHT corner so it warms the
    # scene + rakes light top-left across the islands. Kept restrained (no blown-
    # out white core) and off the bottom-CENTRE so the PARCELS treasure stall
    # keeps its own controlled red aura instead of being swallowed by the sun.
    soft_glow(bg, int(DW * 0.94), int(DH * 0.96), m(160), SUN_GLOW, 50, layers=14)
    soft_glow(bg, int(DW * 0.94), int(DH * 0.96), m(64), (255, 238, 196), 56, layers=10)

    # warm horizon haze lifting off the bottom third
    haze = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for y in range(int(DH * 0.6), DH):
        t = (y - DH * 0.6) / (DH * 0.4)
        a = int(60 * t ** 1.6)
        pygame.draw.line(haze, (*HAZE, a), (0, y), (DW, y))
    bg.blit(haze, (0, 0))

    # sparse star bed — only the upper indigo reads stars; they fade out before
    # the warm band so the golden hour stays clean.
    rnd = random.Random(73)
    stars = pygame.Surface((DW, DH), pygame.SRCALPHA)
    # densest + brightest right at the apex (fade**1.5) so the jewel-store night
    # sky emerges crisply up top and is gone before the warm band — no haze of
    # half-lit dots smearing the mid sky.
    for _ in range(170):
        x = rnd.randint(0, DW)
        y = rnd.randint(0, int(DH * 0.46))
        fade = (1.0 - (y / (DH * 0.46))) ** 1.5
        r = m(rnd.uniform(0.4, 1.6))
        a = int(rnd.randint(50, 185) * fade)
        if a <= 4:
            continue
        tint = rnd.choice([(255, 252, 240), (216, 222, 255), (255, 232, 190),
                           (255, 240, 210)])
        pygame.draw.circle(stars, (*tint, a), (x, y), max(1, int(r)))
    for _ in range(10):
        x = rnd.randint(m(20), DW - m(20))
        y = rnd.randint(m(20), int(DH * 0.30))
        L = m(rnd.uniform(3, 5.5))
        a = rnd.randint(140, 210)
        col = (255, 244, 206, a)
        pygame.draw.line(stars, col, (x - L, y), (x + L, y), max(1, m(0.8)))
        pygame.draw.line(stars, col, (x, y - L), (x, y + L), max(1, m(0.8)))
        soft_glow(stars, x, y, m(3.2), (255, 240, 200), 80, layers=4)
    bg.blit(stars, (0, 0), special_flags=pygame.BLEND_ADD)

    # far parallax clouds drifting low + small (depth below the platforms); kept
    # dusk-tinted + soft so they sit behind everything, never competing.
    _far_cloud(bg, int(DW * 0.16), int(DH * 0.70), m(38), 95, (210, 168, 188))
    _far_cloud(bg, int(DW * 0.80), int(DH * 0.62), m(30), 80, (198, 158, 184))
    _far_cloud(bg, int(DW * 0.42), int(DH * 0.80), m(46), 110, (226, 180, 168))
    _far_cloud(bg, int(DW * 0.92), int(DH * 0.82), m(34), 90, (230, 184, 162))

    _bg_static = bg


def _far_cloud(surf, cx, cy, r, alpha, tint):
    """A soft distant puff for parallax depth far below the platforms."""
    puffs = [(-r * 0.9, r * 0.1, r * 0.62), (-r * 0.3, -r * 0.2, r * 0.85),
             (r * 0.4, -r * 0.05, r * 0.72), (r * 0.95, r * 0.15, r * 0.5),
             (0, r * 0.35, r * 0.9)]
    cloud = pygame.Surface((int(r * 4), int(r * 3)), pygame.SRCALPHA)
    ox, oy = int(r * 2), int(r * 1.5)
    for px, py, pr in puffs:
        s = pygame.Surface((int(pr * 2 + 2), int(pr * 2 + 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*tint, alpha), (int(pr + 1), int(pr + 1)), int(pr))
        cloud.blit(s, (ox + int(px) - int(pr), oy + int(py) - int(pr)))
    surf.blit(cloud, (cx - ox, cy - oy))


def draw_bg(surf):
    surf.blit(_bg_static, (0, 0))


# =============================================================================
# Cloud platform — a golden-rimmed floating island disc that holds one stall
# =============================================================================
def _cloud_silhouette(rw, rh, seed):
    """A bumpy cloud-island outline: a smooth flat-ish TOP deck edge bumped with
    a few rounded lobes, dropping to a single rounded keel below. Returns a
    closed point list centred on (0,0) — the ONE mass we shade + rim, so the
    island reads as a sculpted whole rather than a heap of separate blobs."""
    rnd = random.Random(seed)
    pts = []
    # top edge: left->right, gently undulating lobes (the fluffy deck crown)
    lobes = 5
    for i in range(lobes + 1):
        t = i / lobes
        x = -rw + 2 * rw * t
        bump = math.sin(t * math.pi) ** 0.6
        y = -rh * (0.42 + 0.40 * bump) + rnd.uniform(-rh * 0.06, rh * 0.06) \
            - abs(math.sin(t * math.pi * lobes)) * rh * 0.10
        pts.append((x, y))
    # right shoulder rounding down
    pts.append((rw * 0.98, rh * 0.02))
    pts.append((rw * 0.86, rh * 0.40))
    # keel: a soft ROUNDED underbelly arc (several shallow points, no sharp tip)
    keel = 7
    for i in range(keel + 1):
        t = i / keel
        ang = math.pi * t                            # right->left under-arc
        x = rw * 0.62 * math.cos(ang)
        y = rh * (0.74 + 0.16 * math.sin(ang)) \
            + rnd.uniform(-rh * 0.03, rh * 0.03)
        pts.append((x, y))
    # left shoulder back up
    pts.append((-rw * 0.86, rh * 0.40))
    pts.append((-rw * 0.98, rh * 0.02))
    return pts


def cloud_platform(surf, cx, cy, rw, rh):
    """A floating cloud island as a SOLID LIT VOLUME: ONE sculpted mass — a
    flat-ish fluffy top deck (where the stall stands) over a single rounded
    violet keel — shaded by a top-left key so it reads tactile and round: a hot
    cream crown, a sheen band on the upper deck, a violet ambient-occlusion shelf
    cupping the underbelly, a fluffy lit-crown fringe, and a clean continuous
    warm-GOLD rim that brightens to a hotter under-rim along the lit foot.
    Oversized at SS so it downscales razor-crisp. Returns the deck-y for a stall."""
    pad = m(34)
    surf_w = int(rw * 2 + pad * 2)
    surf_h = int(rh * 2.6 + pad * 2)
    isl = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    ox, oy = int(rw + pad), int(rh + pad)

    sil = [(ox + px, oy + py) for px, py in _cloud_silhouette(rw, rh, int(cx + cy))]
    bmask = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    pygame.draw.polygon(bmask, (255, 255, 255, 255), sil)
    top_y = min(p[1] for p in sil)
    bot_y = max(p[1] for p in sil)

    # body shade: a continuous vertical ramp (hot crown -> lit cream -> dusk mid
    # -> violet keel -> deepest keel) clipped to the silhouette. The extra dark
    # stop at the very foot is what reads as the rounded underbelly turning away
    # from the light, so the mass is a VOLUME rather than a flat lozenge.
    body = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    bstops = [(0.00, CLOUD_CROWN), (0.20, CLOUD_HI), (0.46, CLOUD_MID),
              (0.74, CLOUD_LO), (1.00, CLOUD_LO2)]
    for y in range(int(top_y), int(bot_y) + 1):
        t = (y - top_y) / max(1, bot_y - top_y)
        seg = 0
        while seg < len(bstops) - 2 and t > bstops[seg + 1][0]:
            seg += 1
        t0, c0 = bstops[seg]
        t1, c1 = bstops[seg + 1]
        col = lerp_color(c0, c1, (t - t0) / max(1e-6, t1 - t0))
        pygame.draw.line(body, (*col, 255), (0, y), (surf_w, y))
    body.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    isl.blit(body, (0, 0))

    # top-left key light: a soft hot-cream wash on the upper-left crown so the
    # mass has a clearly lit shoulder, all consistent with the one light source.
    lit = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    soft_glow(lit, int(ox - rw * 0.34), int(oy - rh * 0.42), int(rw * 0.95),
              (255, 248, 230), 78, layers=12)
    lit.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    isl.blit(lit, (0, 0), special_flags=pygame.BLEND_ADD)

    # bottom ambient-occlusion shelf: a soft translucent violet shade cupping the
    # lower-RIGHT keel (away from the light) so the underbelly recedes and the
    # deck reads as a raised, sittable shelf on a solid cloud. Painted as a normal
    # alpha overlay (NOT a channel-subtract, which would skew the dusk-rose body
    # toward muddy green) and masked to the silhouette so it never spills.
    ao = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    for i in range(10, 0, -1):
        r = int(rw * 0.74 * i / 10)
        a = int(78 * (1 - (i - 1) / 10) ** 1.7)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*CLOUD_LO2, a), (r + 1, r + 1), r)
        ao.blit(g, (int(ox + rw * 0.26) - r - 1, int(oy + rh * 0.62) - r - 1))
    ao.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    isl.blit(ao, (0, 0))

    # fluffy puff fringe ONLY along the lit top crown — rounded lobes hugging the
    # top silhouette, each shaded round (lit cap -> dusk base) so the upper edge
    # reads as soft, tactile cloud and the keel stays a smooth turning volume.
    rnd = random.Random(int(cx * 5 + cy))
    crown = [p for p in sil if p[1] < oy - rh * 0.2]
    for pxp, pyp in crown:
        pr = rnd.uniform(rh * 0.36, rh * 0.52)
        f = max(0.0, min(1.0, (pxp - (ox - rw)) / (rw * 2)))
        cap = lerp_color(CLOUD_CROWN, CLOUD_HI, f * 0.6)
        base = lerp_color(CLOUD_HI, CLOUD_MID, 0.55 + f * 0.3)
        s = pygame.Surface((int(pr * 2 + 4), int(pr * 2 + 4)), pygame.SRCALPHA)
        cc = int(pr + 2)
        for i in range(int(pr), 0, -1):
            ff = i / pr                              # 1 at lit cap -> 0 at base
            cv = lerp_color(base, cap, ff ** 0.8)
            pygame.draw.circle(s, (*cv, 255),
                               (cc - int(pr * 0.18), cc - int(pr * 0.22)), i)
        isl.blit(s, (int(pxp - cc), int(pyp - cc + rh * 0.06)))

    # the CONTINUOUS gold keyline — the platform's signature. A clean full gold
    # contour for definition everywhere, a brighter warm-gold rim on the lit
    # upper-left crown, and a HOTTER under-rim along the lit lower-left foot
    # (golden-hour sun bouncing up), so the island is gold-rimmed all the way
    # round with a crisp under-edge rather than dissolving into the sky.
    pygame.draw.polygon(isl, (*GOLD_DEEP, 150), sil, max(1, m(1.6)))
    rim = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    n = len(sil)
    for i in range(n):
        a = sil[i]
        b = sil[(i + 1) % n]
        midx = (a[0] + b[0]) / 2
        midy = (a[1] + b[1]) / 2
        if midy < oy + rh * 0.1 and midx < ox + rw * 0.55:
            pygame.draw.line(rim, (*CLOUD_RIM, 240), a, b, max(1, m(2.4)))
        elif midy > oy + rh * 0.3 and midx < ox + rw * 0.35:
            # lit lower-left foot catches the hotter golden under-rim
            pygame.draw.line(rim, (*CLOUD_UNDERRIM, 235), a, b, max(1, m(2.2)))
    isl.blit(rim, (0, 0), special_flags=pygame.BLEND_ADD)

    # gold underglow kiss on the keel (sun bouncing up from the golden foot)
    soft_glow(isl, int(ox - rw * 0.05), int(oy + rh * 0.55), int(rw * 0.58),
              (236, 158, 96), 34, layers=8)

    # composite with a soft drop shadow so platforms genuinely float
    isl_rect = pygame.Rect(cx - ox, cy - oy, surf_w, surf_h)
    sh = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    for k in range(m(10), 0, -1):
        a = int(64 * (k / m(10)) ** 1.6 / m(10) * 3)
        pygame.draw.ellipse(sh, (10, 8, 24, a),
                            (ox - rw - k, oy + rh * 0.2 - k,
                             rw * 2 + k * 2, rh * 1.3 + k * 2))
    surf.blit(sh, (isl_rect.x, isl_rect.y + m(8)))
    surf.blit(isl, isl_rect.topleft)

    return cy - int(rh * 0.34)                        # the deck line for the stall


# =============================================================================
# Rope-bridge — a thin gold swag linking two platforms, guiding the eye down
# =============================================================================
def rope_bridge(surf, p0, p1, coins=2):
    """A thin twin gold rope with plank rungs slung between two platform anchors,
    sagging under gravity, with a couple of floating coins riding it to lead the
    eye down the zig-zag. Kept slim (≈2px) so it links without cluttering."""
    x0, y0 = p0
    x1, y1 = p1
    sag = m(26) + abs(x1 - x0) * 0.06
    bridge = pygame.Surface((DW, DH), pygame.SRCALPHA)

    def pt(t):
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t + math.sin(math.pi * t) * sag
        return x, y

    samples = [pt(i / 48) for i in range(49)]
    # twin ropes (a hair apart) + a darker keyline under for definition
    for off, col, w in (((0, m(2.4)), (60, 38, 10), m(3.0)),
                        ((-m(1.4), 0), (*CLOUD_RIM, 235), m(1.6)),
                        ((m(1.4), 0), (212, 158, 70, 220), m(1.6))):
        dy = off[0]
        pts = [(x, y + dy) for x, y in samples]
        pygame.draw.lines(bridge, col[:3] if len(col) == 3 else col, False,
                          pts, max(1, int(w if isinstance(w, (int, float)) else off[1])))
    # plank rungs across the two ropes
    for i in range(3, 46, 4):
        x, y = samples[i]
        pygame.draw.line(bridge, (*CLOUD_RIM, 200),
                         (x, y - m(2.2)), (x, y + m(2.2)), max(1, m(1.4)))
    surf.blit(bridge, (0, 0))

    # floating lead coins riding the bridge curve
    for c in range(coins):
        t = (c + 1) / (coins + 1)
        x, y = pt(t)
        soft_glow(surf, int(x), int(y - m(9)), m(8), (255, 210, 110), 60, layers=6)
        coin_glyph(surf, int(x), int(y - m(9)), m(6))


# =============================================================================
# Stall — a small awning storefront on a cloud, fronting one category preview
# =============================================================================
def _awning(surf, cx, top_y, w, h, scallops=5):
    """A striped scalloped awning (macaw-red + cream) over the stall mouth — the
    universal bazaar tell, shared by all seven stalls."""
    red = (172, 38, 28)
    cream = (246, 238, 222)
    x0 = cx - w // 2
    # awning body: alternating stripe quads
    sw = w / scallops
    for i in range(scallops):
        col = red if i % 2 == 0 else cream
        rx = int(x0 + i * sw)
        pygame.draw.polygon(surf, col,
                            [(rx, top_y), (rx + int(sw) + 1, top_y),
                             (rx + int(sw) + 1, top_y + h), (rx, top_y + h)])
    # scalloped lower lip
    for i in range(scallops):
        col = red if i % 2 == 0 else cream
        rx = x0 + i * sw + sw / 2
        pygame.draw.circle(surf, col, (int(rx), top_y + h), int(sw / 2))
    # top sheen + a defined edge
    sheen = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        a = int(70 * (1 - y / h) ** 1.4)
        pygame.draw.line(sheen, (255, 255, 255, a), (0, y), (w, y))
    surf.blit(sheen, (x0, top_y))
    pygame.draw.line(surf, (40, 8, 6), (x0, top_y), (x0 + w, top_y), max(1, m(1.4)))
    # a tiny gold valance rail
    pygame.draw.line(surf, GOLD_DEEP, (x0, top_y + h), (x0 + w, top_y + h),
                     max(1, m(1.2)))


def category_label(surf, txt, cx, cy, w):
    """The stall's category name in thick gold-keyline type on a recessed gold
    nameplate rail — the tappable affordance's headline."""
    f = font(11.5)
    h = m(20)
    rail = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    drop_shadow(surf, rail, h // 2, blur=m(3), alpha=110, dy=m(2))
    surf.blit(vgrad(rail.w, rail.h, h // 2, (40, 24, 12), (18, 11, 6), 252,
                    gamma=1.1), rail.topleft)
    top_sheen(surf, rail, h // 2, m(8), peak=44)
    pygame.draw.rect(surf, (4, 4, 12), rail, width=max(1, m(1.4)),
                     border_radius=h // 2)
    bevel_rim(surf, rail, h // 2, lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD_PALE, 230), w=max(1, m(1.2)))
    gradient_text(surf, txt, f, rail.center, GOLD_A_TOP, GOLD_A_BOT,
                  weight=m(1.0), keyline=(70, 40, 8), kw=m(1.1),
                  tracking=m(1.0), shadow=False)


def draw_stall(surf, label, group, cx, deck_y, scale=1.0):
    """One category storefront on its cloud deck: a tier-aura glass dome holding
    the REAL category preview thumbnail, a striped awning above it, and the gold
    category nameplate below — the comfortably-tappable category tile."""
    sid = preview_id(group)
    # PARCELS is the store's mystery tier — it always wears the glowing red
    # MYSTERY aura/gem so it reads as the treasure hero, never a common-grey tile.
    if group == "parcels":
        pal = MYSTERY
    else:
        rar = store_catalog.rarity(sid) if sid else "common"
        pal = RARITY.get(rar, RARITY["common"])
    R = int(m(26) * scale)

    # awning canopy over the dome
    aw = int(R * 2.5)
    ah = int(R * 0.62)
    awn_top = deck_y - R - int(R * 1.7)
    _awning(surf, cx, awn_top, aw, ah, scallops=5)
    # two slim posts from the awning down toward the deck (the stall frame)
    for sx in (cx - aw // 2 + m(3), cx + aw // 2 - m(3)):
        pygame.draw.line(surf, (62, 40, 16), (sx, awn_top + ah),
                         (sx, deck_y - m(2)), max(1, m(2.0)))
        pygame.draw.line(surf, GOLD_DEEP, (sx - m(0.6), awn_top + ah),
                         (sx - m(0.6), deck_y - m(2)), max(1, m(0.8)))

    # the glass-dome product well with the REAL preview thumbnail (jewel-store DNA)
    dome_cy = deck_y - R - int(R * 0.12)
    soft_glow(surf, cx, dome_cy, R + m(4), pal["glow"], 34, layers=8)
    cabochon(surf, cx, dome_cy, R, ring=pal["gem"], ring_a=55)
    if sid:
        # box kept inside the dome's inscribed square (≈R*1.41) with a little
        # breathing room so even square previews never kiss the glass rim.
        _blit_preview(surf, sid, cx, dome_cy, R * 1.30)
    cabochon_glass(surf, cx, dome_cy, R, tint=pal["gem"])
    # a tier gem set on the dome rim (upper-right), echoing the jewel cards
    g45 = R * 0.7071
    facet_gem(surf, int(cx + g45), int(dome_cy - g45), int(m(7) * scale),
              pal["gem"], pal["deep"])

    # category nameplate just under the deck
    category_label(surf, label, cx, deck_y + m(20), int(aw * 0.96))


_preview_cache = {}


def _shades_icon(px):
    """A clean synthetic AVIATOR-shades icon for the SHADES stall — the catalog's
    first SHADES item is 'NO SHADES' (no icon), which would otherwise front the
    category with a bare base parrot reading nothing. This draws the same gold-
    rim / black-lens / sky-tint / glint aviators the game paints on the bird, at
    a tall enough resolution to downscale crisp, so the category previews its
    actual product instead of an empty face."""
    GF = (255, 200, 50)        # gold aviator rim (parrot.SHADE_FRAME)
    GL = (190, 138, 30)        # frame shade
    BLK = (20, 20, 32)         # lens body (parrot.SHADE_BLACK, lifted a touch)
    TINT = (60, 96, 150)       # reflected-sky blue
    s = pygame.Surface((px, int(px * 0.62)), pygame.SRCALPHA)
    w, h = s.get_size()
    lr = int(h * 0.40)
    cy = int(h * 0.52)
    lx = int(w * 0.30)
    rx = int(w * 0.70)
    bridge_y = int(h * 0.40)
    # top brow bar across both lenses
    pygame.draw.line(s, GF, (lx - lr, bridge_y - lr // 2),
                     (rx + lr, bridge_y - lr // 2), max(2, int(px * 0.035)))
    for lcx in (lx, rx):
        pygame.draw.circle(s, GL, (lcx, cy + 1), lr + max(2, int(px * 0.05)))
        pygame.draw.circle(s, GF, (lcx, cy), lr + max(2, int(px * 0.05)))
        pygame.draw.circle(s, BLK, (lcx, cy), lr)
        # sky-tint reflected on the upper lens
        tint = pygame.Surface((lr * 2, lr), pygame.SRCALPHA)
        pygame.draw.ellipse(tint, (*TINT, 150), tint.get_rect())
        s.blit(tint, (lcx - lr, cy - lr + 1))
        # bright top-left glint + a small secondary
        pygame.draw.circle(s, (255, 255, 255), (lcx - lr // 2, cy - lr // 2),
                           max(2, int(lr * 0.26)))
        pygame.draw.circle(s, (255, 255, 255, 200),
                           (lcx + lr // 3, cy + lr // 3), max(1, int(lr * 0.16)))
    # gold bridge between the lenses
    pygame.draw.line(s, GF, (lx + lr, cy), (rx - lr, cy), max(2, int(px * 0.04)))
    return s


def _preview_box(src, box_px):
    """Scale a trimmed preview to FIT entirely inside the dome's box (contain on
    BOTH dims, not just the long edge) so aspect-extreme items — wide flip-flops,
    tall party hats — are letterboxed in the cabochon rather than clipped by the
    glass rim. Then the contrast lift for legibility on the dark dome."""
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    s = box_px / max(sw, sh)                          # contain longest edge in box
    scaled = pygame.transform.smoothscale(
        src, (max(1, int(sw * s)), max(1, int(sh * s))))
    lift = scaled.copy()
    lift.fill((C.CABO_RIM_BOOST, C.CABO_RIM_BOOST, C.CABO_RIM_BOOST, 0),
              special_flags=pygame.BLEND_RGB_ADD)
    return lift


def _blit_preview(surf, sid, cx, cy, box_px):
    """Place a category's representative thumbnail inside the dome with a crisp
    top-left rim light so it reads as the lit hero, not a flat sticker. Mirrors
    the store's blit_thumb but seeds from the category's first item; falls back
    to the synthetic aviator-shades icon when the SHADES category's first item
    has no real icon (NO-SHADES), and contains every preview within the dome."""
    key = (sid, int(box_px))
    out = _preview_cache.get(key)
    if out is None:
        icon = parrot.get_skin_icon(sid)
        if icon is None and store_catalog.group(sid) == "shades":
            out = _preview_box(_shades_icon(m(64)), box_px)
        else:
            src = icon or parrot.get_skin_frame(sid, 1, 0.0)
            out = _preview_box(src, box_px)
        _preview_cache[key] = out
    r = out.get_rect(center=(cx, cy))
    rim = C._rim_light(out)
    surf.blit(rim, r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(out, r.topleft)


# =============================================================================
# Pip — the hovering flying vendor, mid-frame in his natural flap pose
# =============================================================================
def draw_pip(surf, cx, cy, scale):
    """Pip the scarlet macaw hovering as the flying vendor: his real flap-pose
    frame (parrot.get_parrot(1, 0.0)), scaled up, on a soft gold updraft glow,
    holding a coin so he reads as the merchant mid-air."""
    frame = parrot.get_parrot(1, 0.0)
    bb = frame.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        frame = frame.subsurface(bb).copy()
    fw, fh = frame.get_size()
    target = int(m(64) * scale)
    s = target / max(fw, fh)
    pip = pygame.transform.smoothscale(
        frame, (max(1, int(fw * s)), max(1, int(fh * s))))

    # a clear FOCAL SPOTLIGHT so Pip is unmistakably the hero of the frame: a
    # warm-gold aura grading to a tight hot core under him, kept compact so it
    # crowns the bird without bleeding onto the neighbouring stall labels.
    soft_glow(surf, cx, cy + int(target * 0.16), int(target * 0.74),
              (255, 196, 108), 60, layers=14)
    soft_glow(surf, cx, cy, int(target * 0.48), (255, 230, 168), 50, layers=10)
    soft_glow(surf, cx, cy - int(target * 0.04), int(target * 0.26),
              (255, 248, 220), 44, layers=8)

    # a soft hover shadow drifting below (sells the float)
    shadow = pygame.Surface((target, int(target * 0.4)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (20, 12, 34, 90), shadow.get_rect())
    surf.blit(shadow, (cx - target // 2, cy + int(target * 0.62)))

    # a few motion-sparkle coins drifting up around him (the vendor's coins)
    for ang, rr, cr in ((-40, 0.62, 7), (210, 0.7, 6), (150, 0.55, 5)):
        px = cx + int(math.cos(math.radians(ang)) * target * rr)
        py = cy + int(math.sin(math.radians(ang)) * target * rr)
        soft_glow(surf, px, py, m(7), (255, 208, 110), 55, layers=5)
        coin_glyph(surf, px, py, m(cr))

    r = pip.get_rect(center=(cx, cy))
    # crisp top-left rim light so the macaw pops off the twilight sky
    rim = C._rim_light(pip, alpha=150)
    surf.blit(rim, r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(pip, r.topleft)


# =============================================================================
# Header — Skybit gold-on-red wordmark, recessed balance capsule, tap hint
# =============================================================================
def draw_header(surf):
    # legibility band behind the title lane
    band = pygame.Surface((DW, m(118)), pygame.SRCALPHA)
    for y in range(m(118)):
        a = int(130 * (1 - y / m(118)) ** 1.2)
        pygame.draw.line(band, (12, 12, 40, a), (0, y), (DW, y))
    surf.blit(band, (0, 0))
    # screen frame hairline (matches the jewel store chrome)
    pygame.draw.rect(surf, (*GOLD, 64), (m(3), m(3), DW - m(6), DH - m(6)),
                     width=max(1, m(1)), border_radius=m(12))
    # gold-on-red Skybit wordmark
    title_wordmark(surf, "STORE", (DW // 2, m(28)), 31, tracking=m(4))
    balance_capsule(surf, DW // 2, m(74))
    # subtle "tap a stall to shop" hint under the capsule, on a slim dark scrim
    # pill so it stays legible over whatever cloud crown rises behind it.
    hint = "TAP A STALL TO SHOP"
    hf = font(9.5)
    hw = _glyph_base(hint, hf, m(2.0)).get_width()
    hpill = pygame.Rect(0, 0, hw + m(26), m(17))
    hpill.center = (DW // 2, m(100))
    sc = pygame.Surface(hpill.size, pygame.SRCALPHA)
    pygame.draw.rect(sc, (8, 8, 24, 150), sc.get_rect(), border_radius=m(9))
    surf.blit(sc, hpill.topleft)
    pygame.draw.rect(surf, (*GOLD, 70), hpill, width=max(1, m(0.8)),
                     border_radius=m(9))
    plain_text(surf, hint, hf, (DW // 2, m(100)),
               (244, 222, 176), shadow_a=120, tracking=m(2.0), weight=m(0.6))


def balance_capsule(surf, cx, y):
    """The recessed gold balance capsule with the REAL in-game coin + a loud
    gradient-gold number — identical treatment to the jewel store so the wallet
    reads the same everywhere."""
    val = f"{BALANCE:,}"
    vf = font(25)
    vw = _glyph_base(val, vf, 0).get_width() + m(2)
    coin_d, gapc, padl, padr = m(28), m(18), m(15), m(22)
    w = padl + coin_d + gapc + vw + padr
    h = m(44)
    cap = pygame.Rect(cx - w // 2, y - h // 2, w, h)
    drop_shadow(surf, cap, h // 2, blur=m(6), alpha=140, dy=m(3))
    surf.blit(vgrad(cap.w, cap.h, h // 2, (58, 42, 22), (22, 15, 8), 255,
                    gamma=1.1), cap.topleft)
    top_sheen(surf, cap, h // 2, m(16), peak=50)
    contact_shadow(surf, cap, h // 2, m(5), alpha=110)
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


# =============================================================================
# Compose — the 7-slot zig-zag template
# =============================================================================
# A locked 7-slot zig-zag so every platform stays on-screen at 360px without
# overlap and every hit target is generous. Slots alternate left/right and march
# down the portrait; PARCELS lands dead-centre at the foot as the glowing
# "treasure" anchor. Logical-px (cx, deck-centre-y, platform-half-width, scale).
SLOTS = [
    (104, 178, 62, 1.00),   # COSTUMES  (upper-left)
    (256, 248, 60, 0.96),   # PARROTS   (upper-right)
    (100, 322, 60, 0.96),   # ANIMALS   (mid-left)
    (258, 392, 58, 0.92),   # SHOES     (mid-right)
    (102, 466, 58, 0.92),   # HATS      (lower-left)
    (258, 522, 58, 0.92),   # SHADES    (lower-right)
    (180, 582, 70, 1.06),   # PARCELS   (centre foot — treasure anchor)
]
PIP_SLOT = (180, 362, 1.16)     # Pip hovers dead-centre, between the columns


def render_device():
    surf = pygame.Surface((DW, DH))
    draw_bg(surf)

    # platform decks first (so bridges + stalls + Pip layer on top correctly)
    decks = []
    for (cx, cyl, hw, sc) in SLOTS:
        deck_y = cloud_platform(surf, m(cx), m(cyl), m(hw), m(hw) * 0.52)
        decks.append((m(cx), deck_y))

    # rope-bridges weaving the zig-zag: each platform to the next, anchored a
    # touch inboard on the cloud crowns so the swag reads as tied to the islands.
    for i in range(len(SLOTS) - 1):
        (cx0, cyl0, hw0, _), (cx1, cyl1, hw1, _) = SLOTS[i], SLOTS[i + 1]
        a = (m(cx0 + (hw0 * 0.5 if cx1 > cx0 else -hw0 * 0.5)),
             decks[i][1] - m(2))
        b = (m(cx1 + (-hw1 * 0.5 if cx1 > cx0 else hw1 * 0.5)),
             decks[i + 1][1] - m(2))
        rope_bridge(surf, a, b, coins=2)

    # PARCELS is the glowing treasure anchor — a red MYSTERY aura blooms BEHIND
    # its dome (drawn before the stall) so the mystery hero radiates red, the
    # store's signal that this stall hides the unknown.
    (pcx, pcyl, phw, psc) = SLOTS[-1]
    pdome_y = decks[-1][1] - int(m(26) * psc) - int(m(26) * psc * 0.12)
    soft_glow(surf, m(pcx), pdome_y, m(56), MYSTERY["glow"], 46, layers=12)
    soft_glow(surf, m(pcx), pdome_y, m(34), (255, 150, 130), 40, layers=8)

    # the seven stalls planted on each platform's returned deck line
    for (label, group), (cx, cyl, hw, sc), (dcx, deck_y) in zip(
            STALLS, SLOTS, decks):
        draw_stall(surf, label, group, dcx, deck_y, scale=sc)

    # Pip the flying vendor, hovering dead-centre between the columns
    draw_pip(surf, m(PIP_SLOT[0]), m(PIP_SLOT[1]), PIP_SLOT[2])

    draw_header(surf)
    return surf


def main():
    C._build_static_bg()        # primes any constellation-hi caches it needs
    _build_bg()
    dev = render_device()
    pygame.image.save(downscale(dev, 1), os.path.join(_HERE, "round_2.png"))
    pygame.image.save(downscale(dev, 2), os.path.join(_HERE, "round_2@2x.png"))
    print("SS =", SS, "device =", DW, "x", DH)
    print("saved round_2.png (360x640) + round_2@2x.png (720x1280)")


if __name__ == "__main__":
    main()
