"""
STORE BAZAAR — concept #4: GOLDEN-HOUR DOCK MARKET (selection-sheet prototype).

A tropical harbor boardwalk at golden hour. Two tiers of category stalls split
by a band of glittering gold water, palms framing the left/right edges, Pip the
scarlet macaw at a dockside cart, and the signature: animated-looking sun-glitter
specular dashes raked across the water. The most overtly "scarlet macaw island"
of the five bazaar concepts.

DOCS-ONLY mockup. Not wired into the game. The whole frame is authored
resolution-independently at SS=4 (1440x2560 device) and ONE smoothscale brings
it down to 360x640 — the downscale is what turns oversized geometry into crisp
anti-aliased edges, exactly like the constellation hi-res store sheet whose
primitive kit this reuses.

Palette comes from the real golden-hour biome keyframe
(game.biome.palette_for_phase(~0.23)) + the biome sky surface, so the dock reads
as the same game world; the Skybit warm-gold + gem UI kit (the constellation
store's m()/vgrad/gold_a_fill/coin_glyph/cabochon/facet_gem/etc.) sits on top so
it still leads cleanly into the jewel store. A small night/indigo jewel accent
(the PARCELS "mystery hero" lantern) seeds the dissolve into that night souk.

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
    GOLD, GOLD_PALE, GOLD_DEEP, RARITY,
    GOLD_A_STOPS, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, GOLD_A_NUM,
    gloss_sweep, contact_shadow, _glyph_base, _stamp_bold,
)


# ── golden-hour palette (the real biome keyframe) ─────────────────────────────
GH_PHASE = 0.23125                       # the GOLDEN HOUR biome keyframe exactly
PAL = biome.palette_for_phase(GH_PHASE)
PHASE_BUCKET = biome.phase_bucket(GH_PHASE)

# Warm anchors pulled toward the verified Skybit golden-hour tones.
SKY_HI = PAL["sky_bot"]                   # (255,210,160) peachy upper
HORIZON = PAL["horizon"]                  # (255,220,140) hot horizon band
WATER_GOLD = (244, 190, 92)              # gold water body
WATER_DEEP = (150, 96, 38)               # shaded trough between glints
AWNING_RED = (168, 32, 16)               # macaw-red awning (verified #A82010-ish)
AWNING_RED_HI = (214, 78, 44)
CREAM = (246, 238, 214)
WOOD_HI = (206, 150, 92)                 # sunlit plank
WOOD_MID = (160, 108, 62)
WOOD_DK = (96, 60, 34)
PALM_TRUNK = (120, 82, 48)
PALM_TRUNK_HI = (172, 124, 76)
FROND_DK = (38, 92, 56)
FROND_MID = (66, 138, 74)
FROND_HI = (132, 196, 96)
# the night/jewel accent that seeds the dissolve into the constellation store
JEWEL_INDIGO = (24, 20, 64)
JEWEL_INDIGO_DEEP = (10, 10, 36)

BALANCE = 14250


# ── stall manifest: 7 categories -> group key + preview id ────────────────────
# The brief's category labels map onto the catalog's group keys (some singular).
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
    ids = store_catalog.ids_of_group(group)
    return ids[0] if ids else None


def _preview_icon(sid, box_px):
    """Representative paid item thumbnail for a stall, fit to a box, bounding-
    boxed + contrast-lifted so it reads as the lit hero under the awning."""
    src = parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    s = box_px / max(sw, sh)
    scaled = pygame.transform.smoothscale(
        src, (max(1, int(sw * s)), max(1, int(sh * s))))
    lift = scaled.copy()
    lift.fill((30, 30, 30, 0), special_flags=pygame.BLEND_RGB_ADD)
    return lift


def _rim_lit(img, color=(255, 244, 210), alpha=170):
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
# Backdrop — biome sky + mountains + clouds + golden glitter water
# =============================================================================
WATER_TOP = m(218)                        # logical y where the water band begins
WATER_BOT = m(266)                        # ...and ends (the near-deck waterline)


def draw_sky(surf):
    """The real golden-hour biome sky (reused cache surface) stretched over the
    upper frame, with biome mountains + a few clouds for tropical depth."""
    horizon_y = WATER_TOP
    sky = get_sky_surface_biome(DW, DH, horizon_y, PAL, PHASE_BUCKET)
    surf.blit(sky, (0, 0))
    # the biome golden-hour sky is pale near the horizon; lay a warm amber
    # gradient over it (strongest low, near the sun) so the sky reads GOLDEN
    # hour, not washed white, while keeping the biome hues underneath.
    warm = pygame.Surface((DW, horizon_y), pygame.SRCALPHA)
    for y in range(horizon_y):
        f = y / max(1, horizon_y - 1)
        a = int(70 + 150 * f ** 1.5)               # warm up top, hot amber at horizon
        col = lerp_color((242, 150, 78), (255, 196, 120), f)
        pygame.draw.line(warm, (*col, a), (0, y), (DW, y))
    surf.blit(warm, (0, 0))

    # the low sun: a warm bloom near the horizon, slightly off-centre. Kept in
    # check so it never blooms to a white wash over the stalls.
    sun_x, sun_y = int(DW * 0.62), int(horizon_y * 0.74)
    soft_glow(surf, sun_x, sun_y, m(66), (255, 214, 140), 46, layers=12)
    soft_glow(surf, sun_x, sun_y, m(28), (255, 236, 190), 90, layers=10)
    disc = pygame.Surface((m(48), m(48)), pygame.SRCALPHA)
    pygame.draw.circle(disc, (255, 244, 214, 235), (m(24), m(24)), m(18))
    surf.blit(disc, (sun_x - m(24), sun_y - m(24)))

    # distant tropical islands / mountains in the warm haze, kept low + hazy
    draw_mountains(surf, scroll=140, ground_y=horizon_y, w=DW,
                   far_color=PAL["mtn_far"], near_color=PAL["mtn_near"])

    # two small soft clouds catching the low light, kept HIGH so they never
    # drift over the stall band or the water glitter.
    for x, y, sc, v in ((m(48), m(40), SS * 0.85, 2),
                        (m(280), m(30), SS * 0.7, 3)):
        draw_cloud(surf, x, y, scale=sc, variant=v)


def draw_water(surf):
    """The glittering gold harbor band that splits the two boardwalk tiers, with
    the SIGNATURE sun-glitter: a sparse field of large bright specular dashes +
    soft glows raking across the water under the low sun. Sparse + large so it
    reads premium, not noisy, at 360px."""
    band_h = WATER_BOT - WATER_TOP
    # base water gradient: hot gold at the far shore deepening toward the viewer
    water = vgrad_stops(DW, band_h, 0,
                        [(0.00, lerp_color(WATER_GOLD, (255, 232, 168), 0.4)),
                         (0.35, WATER_GOLD),
                         (1.00, WATER_DEEP)], 255, gamma=1.05)
    surf.blit(water, (0, WATER_TOP))

    # jetty support posts dropping into the harbor + wobbly dark reflections
    for px in range(m(46), DW - m(36), m(54)):
        pygame.draw.line(surf, (78, 48, 26), (px, WATER_TOP - m(2)),
                         (px, WATER_TOP + m(20)), max(1, m(3.2)))
        pygame.draw.line(surf, (*PALM_TRUNK_HI, 150), (px - m(1), WATER_TOP - m(2)),
                         (px - m(1), WATER_TOP + m(14)), max(1, m(1.0)))
        # broken reflection streak under each post
        for ry in range(WATER_TOP + m(20), WATER_BOT - m(4), m(4)):
            jit = int(math.sin(ry * 0.6 + px) * m(1.4))
            pygame.draw.line(surf, (60, 36, 18, 90), (px + jit, ry),
                             (px + jit, ry + m(2)), max(1, m(2.4)))

    # a hot reflection column straight under the sun (the classic sun-on-water
    # vertical smear), kept to the sun's x and feathered at the edges.
    sun_x = int(DW * 0.62)
    col_w = m(58)
    colsurf = pygame.Surface((col_w, band_h), pygame.SRCALPHA)
    for sx in range(col_w):
        hx = abs(sx - col_w / 2) / (col_w / 2)
        a = int(54 * (1 - hx ** 1.4))              # restrained so it never blows white
        if a > 0:
            pygame.draw.line(colsurf, (255, 238, 184, a), (sx, 0), (sx, band_h))
    surf.blit(colsurf, (sun_x - col_w // 2, WATER_TOP),
              special_flags=pygame.BLEND_ADD)

    # SIGNATURE specular glitter — sparse, large, brightest in the sun column,
    # thinning toward the dark flanks. Seeded so the layout is stable.
    rng = random.Random(404)
    # SPARSE + LARGE specular dashes (the AD risk-note for water shimmer): a few
    # rows of horizontal gold glints, brightest in the sun column, thinning to
    # the dark flanks. Authored as clean dashes — no blobby glows.
    rows = [WATER_TOP + int(band_h * f) for f in (0.20, 0.40, 0.62, 0.84)]
    for ri, ry in enumerate(rows):
        depth = (ry - WATER_TOP) / max(1, band_h)
        count = 6 + ri                              # more glints in the near rows
        for c in range(count):
            x = int((c + rng.uniform(0.2, 0.8)) * DW / count)
            x += int(rng.uniform(-m(6), m(6)))
            x = max(m(8), min(DW - m(8), x))
            dist_sun = abs(x - sun_x) / (DW * 0.55)
            bright = max(0.12, 1.0 - dist_sun)
            ln = m(3.0 + depth * 8.0) * rng.uniform(0.8, 1.2)
            a = int(235 * bright)
            col = lerp_color((255, 226, 150), (255, 252, 232), bright)
            y = ry + int(rng.uniform(-m(3), m(3)))
            # a soft underglow only for the brightest glints near the sun path
            if bright > 0.55:
                soft_glow(surf, x, y, int(ln * 0.7), (255, 220, 140),
                          int(60 * bright), layers=5)
            dash = pygame.Surface((int(ln * 2) + m(2), m(3)), pygame.SRCALPHA)
            pygame.draw.line(dash, (*col, a), (0, m(1)), (int(ln * 2), m(1)),
                             max(1, m(1.6)))
            surf.blit(dash, (x - int(ln), y - m(1)), special_flags=pygame.BLEND_ADD)
            # a hot 4-point star kiss on the brightest, on the sun path
            if bright > 0.72:
                L = int(ln * 1.0)
                pygame.draw.line(surf, (255, 255, 246, 210), (x - L, y), (x + L, y),
                                 max(1, m(0.8)))
                pygame.draw.line(surf, (255, 255, 246, 170), (x, y - m(3)),
                                 (x, y + m(3)), max(1, m(0.8)))

    # far waterline lip (catches the sun, defines the back jetty's foot) and a
    # dark contact line at the near edge where the front boardwalk meets water.
    pygame.draw.line(surf, (255, 244, 200, 230), (0, WATER_TOP),
                     (DW, WATER_TOP), max(1, m(1.6)))
    near_shade = pygame.Surface((DW, m(8)), pygame.SRCALPHA)
    for yy in range(m(8)):
        near_shade.fill((40, 22, 8, int(150 * (yy / m(8)))),
                        (0, yy, DW, 1))
    surf.blit(near_shade, (0, WATER_BOT - m(8)))


# =============================================================================
# Boardwalk decks (the two tiers) + palms + dock posts
# =============================================================================
def _plank_deck(surf, rect, plank_h, light, mid, dark, scroll=0, joist=True):
    """A wooden boardwalk deck: horizontal planks receding in perspective with a
    lit top edge, dark seams, and a few grain streaks. Authored oversized so the
    seams downscale to crisp hairlines."""
    deck = vgrad_stops(rect.w, rect.h, 0,
                       [(0.0, light), (0.5, mid), (1.0, dark)], 255, gamma=1.05)
    surf.blit(deck, rect.topleft)
    rng = random.Random(7 + rect.y)
    y = rect.y
    i = 0
    while y < rect.bottom:
        # planks grow toward the viewer (simple perspective)
        f = (y - rect.y) / max(1, rect.h)
        ph = int(plank_h * (0.7 + f * 0.9))
        # seam: dark groove + a thin lit lip just below it
        pygame.draw.line(surf, (*dark, 255), (rect.x, y), (rect.right, y),
                         max(1, m(1.2)))
        pygame.draw.line(surf, (*lerp_color(light, WHITE, 0.2), 150),
                         (rect.x, y + max(1, m(0.8))),
                         (rect.right, y + max(1, m(0.8))), max(1, m(0.8)))
        # a couple of grain streaks per plank
        for _ in range(3):
            gx = rng.randint(rect.x, rect.right - m(20))
            gw = rng.randint(m(18), m(60))
            ga = rng.randint(20, 55)
            pygame.draw.line(surf, (60, 36, 18, ga),
                             (gx, y + ph // 2), (gx + gw, y + ph // 2),
                             max(1, m(0.8)))
        y += ph
        i += 1
    # board butt-joints (vertical seams) staggered per row for a real deck read
    rng2 = random.Random(99 + rect.y)
    for _ in range(8):
        vx = rng2.randint(rect.x + m(20), rect.right - m(20))
        vy = rng2.randint(rect.y, rect.bottom - m(10))
        pygame.draw.line(surf, (50, 30, 16, 120), (vx, vy), (vx, vy + m(14)),
                         max(1, m(0.9)))
    # lit front lip of the deck
    pygame.draw.line(surf, (*lerp_color(light, WHITE, 0.35), 220),
                     (rect.x, rect.y), (rect.right, rect.y), max(1, m(1.4)))


def draw_back_jetty(surf):
    """The upper boardwalk tier (back jetty) the 3 back stalls sit on. A thin
    deck just behind the water with support posts dropping into the harbor."""
    deck = pygame.Rect(m(20), m(210), DW - m(40), m(14))
    _plank_deck(surf, deck, 7, WOOD_HI, WOOD_MID, WOOD_DK)


def draw_front_boardwalk(surf):
    """The lower, larger boardwalk tier the 4 front stalls + Pip's cart sit on —
    it fills the bottom of the frame and reads as the floor the player stands on."""
    deck = pygame.Rect(0, WATER_BOT, DW, DH - WATER_BOT)
    _plank_deck(surf, deck, 9, lerp_color(WOOD_HI, (235, 196, 150), 0.3),
                WOOD_MID, WOOD_DK)
    # warm light raking from the low sun across the near deck — kept subtle so
    # it warms the planks without reading as a hard spotlight.
    pool = pygame.Surface((DW, deck.h), pygame.SRCALPHA)
    soft_glow(pool, int(DW * 0.58), m(70), m(170), (255, 198, 120), 16, layers=10)
    surf.blit(pool, deck.topleft, special_flags=pygame.BLEND_ADD)


def draw_palm(surf, x_base, y_base, height, lean, flip=False, behind=False):
    """A coconut palm framing an edge: a curved gradient trunk with ring scars +
    a crown of layered fronds. `lean` curves the trunk outward; `behind` mutes it
    into the haze so the back-edge palms read as further away."""
    seg = 14
    pts_l, pts_r = [], []
    trunk_w_base = m(11) if not behind else m(8)
    sway = lean
    top_x = x_base + sway
    top_y = y_base - height
    for i in range(seg + 1):
        t = i / seg
        # quadratic-ish curve out toward the top
        cx = x_base + sway * (t * t)
        cy = y_base - height * t
        w_here = trunk_w_base * (1.0 - 0.45 * t)
        pts_l.append((cx - w_here / 2, cy))
        pts_r.append((cx + w_here / 2, cy))
    trunk_poly = pts_l + pts_r[::-1]
    tcol = lerp_color(PALM_TRUNK, (60, 40, 24), 0.25) if behind else PALM_TRUNK
    pygame.draw.polygon(surf, tcol, trunk_poly)
    # lit left edge of trunk
    if not behind:
        pygame.draw.lines(surf, lerp_color(PALM_TRUNK_HI, WHITE, 0.1), False,
                          pts_l, max(1, m(1.6)))
    # ring scars
    for i in range(2, seg, 2):
        a, b = pts_l[i], pts_r[i]
        pygame.draw.line(surf, (70, 46, 26), a, b, max(1, m(1.0)))
    # crown fronds — layered teardrops radiating from the top
    cxr, cyr = top_x, top_y
    soft_glow(surf, int(cxr), int(cyr), m(20), (120, 200, 120), 30, layers=6)
    n_fronds = 9
    base_ang = 200 if not flip else 340
    for k in range(n_fronds):
        ang = math.radians(-150 + (300 / (n_fronds - 1)) * k)
        flen = height * (0.42 if not behind else 0.34) * (0.8 + 0.4 * abs(math.cos(ang)))
        ex = cxr + math.cos(ang) * flen
        # fronds droop: pull tips down
        ey = cyr + math.sin(ang) * flen * 0.55 + flen * 0.22
        # frond as a tapered triangle fan with a darker spine
        midx = (cxr + ex) / 2 + math.cos(ang + math.pi / 2) * flen * 0.10
        midy = (cyr + ey) / 2 - flen * 0.12
        wfr = m(7) if not behind else m(5)
        perp = (math.cos(ang + math.pi / 2), math.sin(ang + math.pi / 2))
        leaf = [
            (cxr, cyr),
            (midx + perp[0] * wfr, midy + perp[1] * wfr),
            (ex, ey),
            (midx - perp[0] * wfr, midy - perp[1] * wfr),
        ]
        shade = FROND_DK if (k % 2 == 0) else FROND_MID
        if behind:
            shade = lerp_color(shade, (50, 60, 50), 0.45)
        pygame.draw.polygon(surf, shade, leaf)
        # lit upper edge of frond
        pygame.draw.line(surf, lerp_color(FROND_HI, WHITE, 0.1),
                         (cxr, cyr), (ex, ey), max(1, m(1.0)))
    # coconuts clustered at the crown base
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
def draw_stall(surf, label, sid, cx, top_y, w, h, front=True, mystery=False):
    """One category stall: a striped macaw-red awning over a driftwood counter,
    a glass-dome preview well holding the category's representative item, and a
    thick gold-keyline category sign. `front` stalls are larger + brighter than
    the back-jetty stalls; `mystery` (PARCELS) gets the night/indigo jewel-glow
    treatment that seeds the dissolve into the constellation store."""
    rect = pygame.Rect(cx - w // 2, top_y, w, h)
    rad = m(10)

    # ── post legs + soft cast shadow on the deck ──────────────────────────────
    drop = pygame.Surface((w + m(20), m(16)), pygame.SRCALPHA)
    pygame.draw.ellipse(drop, (20, 10, 4, 120), drop.get_rect())
    surf.blit(drop, (rect.centerx - (w + m(20)) // 2, rect.bottom - m(8)))
    leg_col = (104, 68, 38)
    for lx in (rect.x + m(8), rect.right - m(8)):
        pygame.draw.line(surf, leg_col, (lx, rect.y + m(20)),
                         (lx, rect.bottom), max(1, m(3.2)))
        pygame.draw.line(surf, (*PALM_TRUNK_HI, 150), (lx - m(1), rect.y + m(20)),
                         (lx - m(1), rect.bottom), max(1, m(1.0)))

    # ── counter / backboard the preview sits on ───────────────────────────────
    board = pygame.Rect(rect.x, rect.y + m(20), w, h - m(20))
    surf.blit(vgrad_stops(board.w, board.h, rad,
                          [(0.0, lerp_color(WOOD_HI, CREAM, 0.25)),
                           (1.0, WOOD_DK)], 248, gamma=1.1), board.topleft)
    if mystery:
        # the night/jewel accent: an indigo inner panel + violet bloom (the
        # constellation store's ground), so PARCELS reads as the mystery hero
        # and pre-loads the jewel store on tap.
        inner = board.inflate(-m(8), -m(8))
        surf.blit(vgrad(inner.w, inner.h, rad - m(2), JEWEL_INDIGO,
                        JEWEL_INDIGO_DEEP, 235), inner.topleft)
        soft_glow(surf, board.centerx, board.centery, m(26), (120, 96, 220),
                  46, layers=8)
    top_sheen(surf, board, rad, m(12), peak=44)
    contact_shadow(surf, board, rad, m(5), alpha=90)
    pygame.draw.rect(surf, (40, 22, 10), board, width=max(1, m(1.6)),
                     border_radius=rad)
    bevel_rim(surf, board, rad, (60, 38, 16), (*GOLD_PALE, 200),
              w=max(1, m(1.2)))

    # ── preview well (the constellation glass cabochon) + thumbnail ───────────
    # A warm-amber well (not the night store's near-black) so previews read in
    # the golden-hour light; mystery keeps the indigo jewel well.
    disc_r = m(23) if front else m(18)
    disc_cy = board.y + (m(34) if front else m(28))
    tier_glow = (130, 104, 230) if mystery else (255, 200, 120)
    soft_glow(surf, board.centerx, disc_cy, disc_r + m(4), tier_glow, 40, layers=8)
    cabochon(surf, board.centerx, disc_cy, disc_r,
             (40, 36, 78) if mystery else (96, 66, 36),
             (12, 12, 32) if mystery else (40, 24, 10))
    if sid is not None:
        box = int(disc_r * 1.7)
        thumb = _preview_icon(sid, box)
        tr = thumb.get_rect(center=(board.centerx, disc_cy))
        surf.blit(_rim_lit(thumb), tr.topleft, special_flags=pygame.BLEND_ADD)
        surf.blit(thumb, tr.topleft)
    cabochon_glass(surf, board.centerx, disc_cy, disc_r,
                   tint=(190, 162, 255) if mystery else GOLD_PALE)
    # a tier gem set on the dome's upper-right rim (the jewel-store DNA)
    g45 = disc_r * 0.7071
    gpal = RARITY["epic"] if mystery else RARITY["legendary"]
    facet_gem(surf, int(board.centerx + g45), int(disc_cy - g45),
              m(6 if front else 5), gpal["gem"], gpal["deep"])

    # ── category sign: a gold-keyline plaque with thick crisp type ────────────
    sign_y = board.bottom - (m(15) if front else m(13))
    sf = font(12 if front else 10)
    label_w = _glyph_base(label, sf, m(0.6)).get_width()
    plaque = pygame.Rect(0, 0, label_w + m(20), m(20 if front else 17))
    plaque.center = (board.centerx, sign_y)
    surf.blit(gold_a_fill(plaque.w, plaque.h, plaque.h // 2), plaque.topleft)
    gloss_sweep(surf, plaque, plaque.h // 2, peak=60)
    pygame.draw.rect(surf, GOLD_A_RIM_DARK, plaque, width=max(1, m(1.6)),
                     border_radius=plaque.h // 2)
    bevel_rim(surf, plaque, plaque.h // 2, GOLD_A_RIM_DARK,
              (*GOLD_A_RIM_BRIGHT, 230), w=max(1, m(1.1)))
    plain_text(surf, label, sf, plaque.center, GOLD_A_NUM, shadow_a=0,
               tracking=m(0.6), weight=m(0.9))

    # ── striped awning on top (drawn LAST so it overhangs the counter) ────────
    _awning(surf, rect.x - m(2), rect.y, w + m(4),
            m(24) if front else m(18), front=front)


def _awning(surf, x, y, w, h, front=True):
    """A scalloped striped awning in macaw red + cream — the shared bazaar
    signature across all 7 stalls. Slight forward droop + a lit top ridge."""
    n_stripe = 5
    sw = w / n_stripe
    # the awning slopes forward: front edge dips down h*0.55
    front_dip = int(h * 0.55)
    top = y
    # solid back board of the awning
    pygame.draw.rect(surf, (60, 14, 6), (x, top - m(3), w, m(4)))
    for i in range(n_stripe):
        sx = x + i * sw
        red = (i % 2 == 0)
        c_top = AWNING_RED_HI if red else lerp_color(CREAM, WHITE, 0.2)
        c_bot = AWNING_RED if red else CREAM
        poly = [(sx, top), (sx + sw, top),
                (sx + sw, top + h), (sx + sw / 2, top + h + front_dip * 0.0 + m(6)),
                (sx, top + h)]
        # build the stripe as a gradient quad then a scalloped lower edge
        quad = [(sx, top), (sx + sw, top), (sx + sw, top + h), (sx, top + h)]
        stripe = vgrad_stops(int(sw) + 2, h, 0,
                             [(0.0, c_top), (1.0, c_bot)], 255, gamma=1.05)
        surf.blit(stripe, (int(sx), top))
        # scallop: a filled half-disc hanging off the bottom of each stripe
        scal = pygame.Surface((int(sw) + 2, int(front_dip) + m(4)), pygame.SRCALPHA)
        pygame.draw.ellipse(scal, (*c_bot, 255),
                            (0, -int(front_dip), int(sw) + 2, int(front_dip) * 2))
        surf.blit(scal, (int(sx), top + h - m(1)))
    # lit top ridge + dark seam between stripes
    pygame.draw.line(surf, (255, 230, 190, 220), (x, top), (x + w, top),
                     max(1, m(1.6)))
    for i in range(1, n_stripe):
        sx = x + i * sw
        pygame.draw.line(surf, (40, 12, 6, 140), (sx, top), (sx, top + h),
                         max(1, m(0.8)))
    # a thin gold valance trim along the scallop crest
    pygame.draw.line(surf, (*GOLD, 200), (x, top + h), (x + w, top + h),
                     max(1, m(1.2)))


# =============================================================================
# Pip at the dockside cart
# =============================================================================
def draw_pip_cart(surf, cx, base_y):
    """Pip the scarlet macaw tending a small wooden dockside cart, gold aviators
    catching the low sun, a coin spinning above the cart. Lower-centre anchor."""
    # ── the cart: a two-wheel barrow with a crate of goods ────────────────────
    cw, ch = m(96), m(34)
    cart = pygame.Rect(int(cx - cw / 2), int(base_y - ch), cw, ch)
    surf.blit(vgrad_stops(cart.w, cart.h, m(5),
                          [(0.0, lerp_color(WOOD_HI, CREAM, 0.2)),
                           (1.0, WOOD_DK)], 252, gamma=1.1), cart.topleft)
    top_sheen(surf, cart, m(5), m(10), peak=46)
    pygame.draw.rect(surf, (44, 24, 10), cart, width=max(1, m(1.6)),
                     border_radius=m(5))
    bevel_rim(surf, cart, m(5), (60, 36, 16), (*GOLD_PALE, 200), w=max(1, m(1.1)))
    # plank lines on the cart face
    for k in range(1, 4):
        ly = cart.y + cart.h * k // 4
        pygame.draw.line(surf, (50, 30, 14, 150), (cart.x + m(2), ly),
                         (cart.right - m(2), ly), max(1, m(0.8)))
    # wheels
    for wx in (cart.x + m(20), cart.right - m(20)):
        pygame.draw.circle(surf, (40, 24, 12), (wx, cart.bottom + m(6)), m(11))
        pygame.draw.circle(surf, (150, 110, 66), (wx, cart.bottom + m(6)), m(11),
                           max(1, m(2)))
        pygame.draw.circle(surf, (90, 60, 32), (wx, cart.bottom + m(6)), m(3))
        for sp in range(0, 360, 45):
            ex = wx + math.cos(math.radians(sp)) * m(9)
            ey = cart.bottom + m(6) + math.sin(math.radians(sp)) * m(9)
            pygame.draw.line(surf, (110, 76, 42), (wx, cart.bottom + m(6)),
                             (ex, ey), max(1, m(1.2)))
    # a couple of crated goods + a tiny awning over the cart
    pygame.draw.rect(surf, (120, 30, 16), (cart.x + m(6), cart.y - m(10), m(20), m(12)),
                     border_radius=m(2))
    pygame.draw.rect(surf, (40, 12, 6), (cart.x + m(6), cart.y - m(10), m(20), m(12)),
                     width=max(1, m(1)), border_radius=m(2))

    # ── coin spinning above the cart ──────────────────────────────────────────
    coin_cx, coin_cy = cx + m(34), int(base_y - ch - m(30))
    soft_glow(surf, coin_cx, coin_cy, m(13), (255, 210, 110), 70, layers=8)
    coin_glyph(surf, coin_cx, coin_cy, m(11))
    # a little sparkle off the coin
    pygame.draw.line(surf, (255, 255, 240, 220), (coin_cx + m(10), coin_cy - m(8)),
                     (coin_cx + m(16), coin_cy - m(14)), max(1, m(1)))

    # ── Pip himself: the real parrot frame, scaled, set behind/beside the cart ─
    bird = parrot.get_parrot(1, -6.0)
    bw, bh = bird.get_size()
    target_h = m(78)
    s = target_h / bh
    bird = pygame.transform.smoothscale(bird, (int(bw * s), int(bh * s)))
    br = bird.get_rect()
    br.midbottom = (int(cx - m(30)), int(base_y - ch + m(10)))
    # soft contact shadow under Pip
    sh = pygame.Surface((br.w, m(12)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (20, 10, 4, 130), sh.get_rect())
    surf.blit(sh, (br.centerx - br.w // 2, base_y - ch + m(6)))
    # a warm rim light on Pip from the low sun
    rim = bird.copy()
    rim.fill((255, 220, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(rim, (br.x + m(2), br.y - m(1)), special_flags=pygame.BLEND_ADD)
    surf.blit(bird, br.topleft)
    # gold aviator flare — two hot pips where the sun hits the lenses
    soft_glow(surf, br.centerx + m(6), br.y + int(br.h * 0.30), m(5),
              (255, 244, 200), 150, layers=6)


# =============================================================================
# Header — wordmark + balance capsule + hint
# =============================================================================
def draw_header(surf):
    # a soft warm darkening band so the gold wordmark + capsule read on the sky
    band = pygame.Surface((DW, m(96)), pygame.SRCALPHA)
    for y in range(m(96)):
        a = int(110 * (1 - y / m(96)) ** 1.2)
        pygame.draw.line(band, (90, 40, 16, a), (0, y), (DW, y))
    surf.blit(band, (0, 0))
    # screen frame hairline (warm gold)
    pygame.draw.rect(surf, (*GOLD, 70), (m(3), m(3), DW - m(6), DH - m(6)),
                     width=max(1, m(1)), border_radius=m(12))
    # Skybit gold-on-red wordmark
    title_wordmark(surf, "BAZAAR", (DW // 2, m(26)), 28, tracking=m(3))
    balance_capsule(surf, DW // 2, m(64))
    # the "tap a stall" hint, small + warm
    plain_text(surf, "TAP A STALL TO BROWSE", font(9),
               (DW // 2, m(86)), (255, 234, 188), shadow_a=140,
               tracking=m(1.2), weight=m(0.6), keyline=(80, 36, 14), kw=m(0.6))


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
    drop_shadow(surf, cap, h // 2, blur=m(6), alpha=130, dy=m(3))
    surf.blit(vgrad(cap.w, cap.h, h // 2, (74, 48, 22), (32, 18, 8), 255, gamma=1.1),
              cap.topleft)
    top_sheen(surf, cap, h // 2, m(14), peak=50)
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
    gradient_text(surf, val, vf, (x + vw // 2, y), GOLD_A_STOPS[0][1],
                  GOLD_A_STOPS[-1][1], weight=m(1.0), keyline=(96, 56, 12),
                  kw=m(1.2), shadow=True)


# =============================================================================
# Compose
# =============================================================================
def render_device():
    surf = pygame.Surface((DW, DH))
    draw_sky(surf)

    # ── BACK ROW: 3 stalls on the far jetty (smaller), seated ABOVE the water
    # so the glitter band reads clearly between the two tiers. Drawn before the
    # water/jetty so their post-legs land on the jetty deck. ───────────────────
    draw_back_jetty(surf)
    back = [("COSTUMES", "costume"), ("HATS", "hats"), ("SHADES", "shades")]
    back_w = m(90)
    back_xs = [int(DW * f) for f in (0.215, 0.50, 0.785)]
    for (label, group), bx in zip(back, back_xs):
        draw_stall(surf, label, _preview_id(group), bx, m(150), back_w, m(60),
                   front=False)

    # back-edge palms (hazy) framing the jetty so depth reads
    draw_palm(surf, m(14), m(214), m(118), -m(24), flip=False, behind=True)
    draw_palm(surf, DW - m(14), m(214), m(118), m(24), flip=True, behind=True)

    # ── the signature glitter water between the tiers ─────────────────────────
    draw_water(surf)

    # ── near boardwalk fills the lower frame ──────────────────────────────────
    draw_front_boardwalk(surf)

    # front-edge palms framing the lower corners (full, lit)
    draw_palm(surf, m(6), DH - m(6), m(232), -m(50), flip=False)
    draw_palm(surf, DW - m(6), DH - m(6), m(232), m(50), flip=True)

    # ── FRONT ROW: 4 stalls (larger): PARROTS / ANIMALS / SHOES / PARCELS ──────
    front = [("PARROTS", "parrot"), ("ANIMALS", "animal"),
             ("SHOES", "shoes"), ("PARCELS", "parcels")]
    front_w = m(84)
    front_xs = [int(DW * f) for f in (0.155, 0.385, 0.615, 0.845)]
    for (label, group), fx in zip(front, front_xs):
        draw_stall(surf, label, _preview_id(group), fx, m(296), front_w, m(96),
                   front=True, mystery=(group == "parcels"))

    # ── Pip at his dockside cart, lower-centre on the near boardwalk ──────────
    draw_pip_cart(surf, int(DW * 0.5), DH - m(58))

    draw_header(surf)
    return surf


def main():
    dev = render_device()
    pygame.image.save(downscale(dev, 1), os.path.join(_HERE, "round_1.png"))
    pygame.image.save(downscale(dev, 2), os.path.join(_HERE, "round_1@2x.png"))
    print("SS =", SS, "device =", DW, "x", DH)
    print("saved round_1.png + round_1@2x.png")


if __name__ == "__main__":
    main()
