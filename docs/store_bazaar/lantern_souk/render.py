"""
Skybit STORE bazaar landing — concept #2: LANTERN NIGHT-SOUK STREET.

A warm covered market lane at night, read in 1-point perspective: three
striped-awning stalls down each side angle inward toward a vanishing point,
where the PARCELS "mystery" stall glows as the hero beside Pip the
lantern-keeper. A swag of procedural lanterns arcs across the top, each a
soft radial pool of warm gold dropped onto the lane and stalls — the
memorable signature. The night sky above the awnings converges toward the
jewel store's indigo + gold at the screen edges so the push into the
constellation store stays a seamless dissolve.

Same SS=4 supersample pipeline as the constellation store: author logical px
via m(), render the whole scene on 1440x2560, ONE smoothscale down so every
awning scallop, lantern facet, gold keyline and label resolves crisp. All
heavy primitives (vgrad, soft_glow, drop_shadow, gradient/plain text, gem,
cabochon, coin, bevel, sheen, gold rule, wordmark, bg) are reused from the
constellation hi-res render so the souk is unmistakably the same game.

Both build targets safe: pure pygame, no numpy, no desktop/browser-only API.
Docs prototype only — not wired into the live store.
"""
import os
import sys
import math

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

from game.config import W, H
from game.draw import lerp_color, NEAR_BLACK, WHITE
from game import parrot
from game import store_catalog

# REUSE the constellation store's full primitive + palette toolbox so the souk
# stays cohesive with the jewel store.
from render_hi import (
    SS, DW, DH, m, mf, font,
    vgrad, vgrad_stops, gold_a_fill, soft_glow, drop_shadow,
    gradient_text, plain_text, facet_gem, cabochon, cabochon_glass,
    coin_glyph, bevel_rim, top_sheen, gold_rule, title_wordmark,
    multistop_v, _glyph_base, gloss_sweep, contact_shadow,
    GOLD, GOLD_PALE, GOLD_DEEP, RARITY, NEAR_BLACK as NB, WHITE as WH,
    GOLD_A_TOP, GOLD_A_BOT, GOLD_A_STOPS, GOLD_A_COIN_RIM,
    CARD_RING_BRIGHT, downscale, BALANCE,
)


# ── souk palette: warm lamp gold over deep indigo, awnings in macaw red + cream
# Converges toward the constellation indigo at the edges so the transition into
# the jewel store is seamless. Night-souk sky is a warmer indigo->violet than
# the pure nebula, lit from a low lantern glow.
SKY_STOPS = [
    (0.00, (10, 11, 34)),       # high night sky — jewel-store indigo
    (0.34, (20, 17, 54)),       # violet mid
    (0.60, (44, 26, 56)),       # warm dusk band where the lane meets sky
    (0.78, (70, 36, 44)),       # lantern-warmed haze over the stall tops
    (1.00, (40, 22, 36)),
]
LANE_STOPS = [
    (0.00, (58, 34, 30)),       # far floor, lit by the hero lantern
    (0.45, (40, 24, 26)),
    (1.00, (22, 14, 22)),       # near floor, deep
]
AWN_RED = (168, 32, 16)         # macaw-red awning stripe
AWN_RED_HI = (214, 70, 44)
AWN_CREAM = (244, 230, 198)     # cream awning stripe
AWN_CREAM_LO = (206, 184, 150)
POST_TOP = (120, 86, 52)        # warm sandstone-ish stall post
POST_BOT = (66, 44, 28)
SIGN_TOP = (92, 60, 34)         # hanging wooden sign board
SIGN_BOT = (54, 33, 18)
LANTERN_GLASS = (255, 196, 92)  # warm lamp gold
LANTERN_CORE = (255, 234, 176)
LANE_GLOW = (255, 178, 86)      # the warm pool colour on lane + stalls
INDIGO_EDGE = (10, 10, 32)


# Per the brief: 7 category stalls. Six line the lane (3 left, 3 right); PARCELS
# is the glowing hero at the vanishing point. Each previews its group's first
# (representative paid) item. Labels are the category names.
SIDE_GROUPS = [
    # (group, display label, side, depth row 0=far .. 2=near)
    ("costume", "COSTUMES", "L", 0),
    ("parrot",  "PARROTS",  "R", 0),
    ("animal",  "ANIMALS",  "L", 1),
    ("shoes",   "SHOES",    "R", 1),
    ("hats",    "HATS",     "L", 2),
    ("shades",  "SHADES",   "R", 2),
]
HERO_GROUP = ("parcels", "PARCELS")

# Vanishing point: high-center, just under the lantern swag, so the lane and
# awning ridges read as one funnel toward the glowing hero.
VP = (W * 0.5, 250)


# ── thumbnail cache (the REAL category preview, scaled, contrast-lifted) ──────
_preview_cache = {}


def _preview_surf(sid, box_px):
    key = (sid, box_px)
    out = _preview_cache.get(key)
    if out is None:
        src = parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)
        bb = src.get_bounding_rect()
        if bb.width > 0 and bb.height > 0:
            src = src.subsurface(bb).copy()
        sw, sh = src.get_size()
        s = box_px / max(sw, sh)
        out = pygame.transform.smoothscale(
            src, (max(1, int(sw * s)), max(1, int(sh * s))))
        # lift value separation off the dark stall interior (no invented detail)
        boost = out.copy()
        boost.fill((30, 30, 30, 0), special_flags=pygame.BLEND_RGB_ADD)
        out = boost
        _preview_cache[key] = out
    return out


def _rim_light(img, color=(255, 226, 160), alpha=150, off=None):
    """Warm top-left rim so the preview pops off the dark stall like a lit good."""
    w, h = img.get_size()
    if off is None:
        off = max(1, m(0.7))
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
# Background: souk sky converging to indigo + a perspective lane floor
# =============================================================================
_static_sky = None
_static_stars = None


def _build_static_bg():
    global _static_sky, _static_stars
    sky = multistop_v(DW, DH, SKY_STOPS).convert_alpha()
    # converge toward the jewel-store indigo at the LEFT/RIGHT edges so the souk
    # frames into the constellation store — a horizontal vignette to indigo.
    edge = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for x in range(DW):
        d = abs(x - DW * 0.5) / (DW * 0.5)
        a = int(150 * d ** 1.7)
        pygame.draw.line(edge, (*INDIGO_EDGE, a), (x, 0), (x, DH))
    sky.blit(edge, (0, 0))
    _static_sky = sky

    # a sparse, calm starfield only in the upper night band (over the awnings)
    rnd = __import__("random").Random(204)
    stars = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for n, rmin, rmax, amin, amax in ((90, 0.4, 0.9, 26, 80),
                                      (32, 0.8, 1.5, 60, 130),
                                      (10, 1.3, 2.3, 110, 190)):
        for _ in range(n):
            x = rnd.randint(0, DW)
            y = rnd.randint(0, int(DH * 0.40))   # only the high sky
            r = m(rnd.uniform(rmin, rmax))
            a = rnd.randint(amin, amax)
            tint = rnd.choice([(255, 250, 236), (220, 224, 255), (255, 236, 200)])
            pygame.draw.circle(stars, (*tint, a), (x, y), max(1, int(r)))
    _static_stars = stars


def _lane_poly():
    """The receding lane floor: a trapezoid from the full-width near edge up to
    a narrow strip at the vanishing point. Returns the device-px polygon."""
    near_y = H
    far_y = VP[1] + 18
    near_l, near_r = W * 0.06, W * 0.94
    far_l, far_r = VP[0] - 30, VP[0] + 30
    return [(m(near_l), m(near_y)), (m(near_r), m(near_y)),
            (m(far_r), m(far_y)), (m(far_l), m(far_y))]


def draw_bg(surf):
    surf.blit(_static_sky, (0, 0))
    surf.blit(_static_stars, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── covered-lane ceiling shadow: the awning canopy darkens the top corners,
    # leaving a warm slot of sky down the lane's center (the "covered" read).
    ceil = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for y in range(int(DH * 0.42)):
        f = y / (DH * 0.42)
        a = int(120 * (1 - f) ** 1.3)
        pygame.draw.line(ceil, (8, 8, 26, a), (0, y), (DW, y))
    surf.blit(ceil, (0, 0))

    # ── the lane floor, in perspective, filled with a depth gradient then masked
    lane = _lane_poly()
    ys = [p[1] for p in lane]
    top_y, bot_y = min(ys), max(ys)
    floor = multistop_v(DW, bot_y - top_y, LANE_STOPS).convert_alpha()
    mask = pygame.Surface((DW, bot_y - top_y), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(px, py - top_y) for px, py in lane])
    floor.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(floor, (0, top_y))

    # cobble/plank perspective lines on the lane — receding toward the VP so the
    # 1-point read is unmistakable. Thin warm gold hairlines, fading near + far.
    cobble = pygame.Surface((DW, DH), pygame.SRCALPHA)
    vpx, vpy = m(VP[0]), m(VP[1])
    # longitudinal rails to the VP
    for fx in (0.10, 0.27, 0.5, 0.73, 0.90):
        nx = m(W * fx)
        pygame.draw.line(cobble, (150, 96, 52, 60), (nx, m(H)), (vpx, vpy), max(1, m(0.8)))
    # transverse plank lines, spaced by a perspective fall-off
    for k in range(1, 7):
        t = (k / 7) ** 1.7
        y = m(H) - (m(H) - m(VP[1] + 22)) * t
        # interpolate lane half-width at this depth
        wf = 1 - t
        xl = m(W * 0.5) - int((m(W * 0.44)) * wf + m(30) * t)
        xr = m(W * 0.5) + int((m(W * 0.44)) * wf + m(30) * t)
        a = int(70 * (1 - t * 0.7))
        pygame.draw.line(cobble, (150, 96, 52, a), (xl, y), (xr, y), max(1, m(0.7)))
    surf.blit(cobble, (0, 0))


# =============================================================================
# Stall: an upright striped-awning tile with a hanging sign + a real preview.
# Perspective scales the tile by depth but never below the comfy-tap floor.
# =============================================================================
def _striped_awning(surf, rect, scallops):
    """A striped scalloped awning across the top of a stall: alternating macaw-
    red + cream vertical bands, a lit top sheen, and a scalloped lower lip."""
    aw = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    band = rect.w / scallops
    for i in range(scallops):
        x0 = int(i * band)
        x1 = int((i + 1) * band)
        if i % 2 == 0:
            col_t, col_b = AWN_RED_HI, AWN_RED
        else:
            col_t, col_b = AWN_CREAM, AWN_CREAM_LO
        for y in range(rect.h):
            c = lerp_color(col_t, col_b, (y / max(1, rect.h - 1)) ** 1.1)
            pygame.draw.line(aw, c, (x0, y), (x1, y))
    # lit crown sheen
    sheen = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        a = int(70 * (1 - y / rect.h) ** 1.6)
        pygame.draw.line(sheen, (255, 244, 214, a), (0, y), (rect.w, y))
    aw.blit(sheen, (0, 0), special_flags=pygame.BLEND_ADD)
    surf.blit(aw, rect.topleft)
    # scalloped lower lip — a row of half-circles hanging off the awning's foot
    lip_r = max(2, int(band * 0.5))
    for i in range(scallops):
        cx = rect.x + int((i + 0.5) * band)
        col = AWN_CREAM if i % 2 else AWN_RED
        pygame.draw.circle(surf, col, (cx, rect.bottom), lip_r)
        pygame.draw.circle(surf, lerp_color(col, NB, 0.35),
                           (cx, rect.bottom), lip_r, max(1, m(0.8)))
    # dark contact keyline along the awning's top + a deep eave shadow beneath
    pygame.draw.rect(surf, (20, 8, 8), rect, width=max(1, m(1.4)))
    eave = pygame.Surface((rect.w, m(8)), pygame.SRCALPHA)
    for y in range(m(8)):
        pygame.draw.line(eave, (0, 0, 0, int(120 * (1 - y / m(8)))),
                         (0, y), (rect.w, y))
    surf.blit(eave, (rect.x, rect.bottom + lip_r))


def draw_stall(surf, group, label, cx, cy, scale, lit=0.0):
    """One side stall. cx,cy is the center of the upright stall FACE; scale in
    (0,1] shrinks far stalls but the face is floored so the tap target stays
    >= ~92px tall at the downscaled target. `lit` 0..1 = how strongly the
    nearest lantern pool falls on this stall."""
    # logical face size, floored so even the far stalls stay comfortably tappable
    fw = int(96 * scale + 24)        # 96..120 logical wide
    fh = int(70 * scale + 30)        # interior height; total tile taller
    fw = max(fw, 96)
    fh = max(fh, 66)
    face = pygame.Rect(m(cx - fw / 2), m(cy - fh / 2), m(fw), m(fh))

    # ── posts: two warm uprights framing the stall, with a dark inner cavity ──
    post_w = m(8)
    awn_h = m(20)
    top_y = face.y - awn_h - m(6)
    bot_y = face.bottom + m(10)
    for px in (face.x - post_w, face.right):
        post = pygame.Rect(px, top_y, post_w, bot_y - top_y)
        drop_shadow(surf, post, m(2), blur=m(3), alpha=90, dy=m(2))
        surf.blit(vgrad(post.w, post.h, m(2), POST_TOP, POST_BOT), post.topleft)
        pygame.draw.rect(surf, (28, 16, 8), post, width=max(1, m(1)),
                         border_radius=m(2))
        pygame.draw.line(surf, (210, 168, 110, 150),
                         (post.x + m(1), post.y), (post.x + m(1), post.bottom),
                         max(1, m(1)))

    # ── stall interior: a dark recessed cavity the preview good sits inside ───
    cav = face.inflate(0, m(6))
    drop_shadow(surf, cav, m(6), blur=m(5), alpha=120, dy=m(2))
    surf.blit(vgrad(cav.w, cav.h, m(6), (40, 28, 26), (16, 11, 14), 255,
                    gamma=1.2), cav.topleft)
    # warm back-wall glow from the lane so the good is readable
    soft_glow(surf, cav.centerx, cav.centery + m(4), m(fw * 0.30),
              (120, 70, 40), 46, layers=7)
    contact_shadow(surf, cav, m(6), m(6), alpha=110)
    pygame.draw.rect(surf, (10, 6, 8), cav, width=max(1, m(1.6)),
                     border_radius=m(6))
    bevel_rim(surf, cav, m(6), (70, 46, 24), (*CARD_RING_BRIGHT, 150),
              w=max(1, m(1.2)))

    # ── the REAL category preview good, scaled into the cavity, rim-lit ──────
    sid = store_catalog.ids_of_group(group)[0]
    box = int(min(fw, fh) * 0.74)
    prev = _preview_surf(sid, m(box))
    pr = prev.get_rect(center=(cav.centerx, cav.centery - m(1)))
    soft_glow(surf, cav.centerx, cav.centery, m(box * 0.28),
              (110, 64, 36), 30, layers=6)
    surf.blit(_rim_light(prev), pr.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(prev, pr.topleft)

    # ── striped awning across the stall top ──────────────────────────────────
    awn = pygame.Rect(face.x - post_w, face.y - awn_h - m(6),
                      face.w + post_w * 2, awn_h)
    _striped_awning(surf, awn, scallops=max(5, int(fw / 16)))

    # ── hanging wooden sign carrying the category label, on two little chains ─
    # the sign must stay on-screen (far stalls hug the edges) AND fully show the
    # word, so the font auto-shrinks until the label fits the available width.
    avail = 2 * min(face.centerx - m(8), DW - m(8) - face.centerx) - m(16)
    base_sz = 11 * (0.80 + 0.20 * scale)
    sz = base_sz
    sf = font(sz)
    while _glyph_base(label, sf, m(0.6)).get_width() > avail and sz > 7.5:
        sz -= 0.5
        sf = font(sz)
    tw = _glyph_base(label, sf, m(0.6)).get_width()
    sign_w = max(tw + m(18), int(face.w * 0.82))
    sign_w = min(sign_w, avail + m(16))
    sign_h = m(20)
    sign = pygame.Rect(face.centerx - sign_w // 2,
                       awn.bottom + m(12), sign_w, sign_h)
    # two chains from the awning lip to the sign's top corners
    for chx in (sign.x + m(8), sign.right - m(8)):
        pygame.draw.line(surf, (40, 26, 12), (chx, awn.bottom + m(2)),
                         (chx, sign.y), max(1, m(1.4)))
        pygame.draw.line(surf, (190, 150, 96, 160), (chx, awn.bottom + m(2)),
                         (chx, sign.y), max(1, m(0.7)))
    drop_shadow(surf, sign, m(5), blur=m(4), alpha=120, dy=m(2))
    surf.blit(vgrad(sign.w, sign.h, m(5), SIGN_TOP, SIGN_BOT), sign.topleft)
    top_sheen(surf, sign, m(5), m(8), peak=40)
    pygame.draw.rect(surf, (18, 10, 4), sign, width=max(1, m(1.6)),
                     border_radius=m(5))
    bevel_rim(surf, sign, m(5), (78, 50, 22), (*GOLD_PALE, 200),
              w=max(1, m(1.2)))
    # thick gold-keyline label
    gradient_text(surf, label, sf, sign.center, GOLD_A_TOP, GOLD_A_BOT,
                  keyline=(28, 16, 4), kw=m(1.1), weight=m(0.9), shadow=True,
                  tracking=m(0.6))

    # ── warm lantern pool falling on this stall (the signature light) ─────────
    if lit > 0:
        # the pool spills onto the LANE in front of the stall (not over the
        # cavity), so the preview stays readable while the floor catches light.
        pool = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        soft_glow(pool, cav.centerx, cav.bottom + m(14), m(26 * scale + 8),
                  LANE_GLOW, int(26 * lit), layers=8)
        surf.blit(pool, (0, 0), special_flags=pygame.BLEND_ADD)


# =============================================================================
# Hero PARCELS stall at the vanishing point + Pip the lantern-keeper
# =============================================================================
def draw_hero(surf):
    """The PARCELS 'mystery' stall, dead-center at the street's end under the
    brightest lantern — the glowing focal anchor, with a real parcel preview and
    a mystery aura. Pip stands beside it holding the lantern that lights the
    lane."""
    cx = m(VP[0])
    cy = m(330)
    pal = RARITY["legendary"]

    # the big warm hero pool washing up the lane from the end of the street —
    # the brightest single light, but bounded so it pools rather than washes.
    floorpool = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    soft_glow(floorpool, cx, m(VP[1] + 90), m(92), LANE_GLOW, 40, layers=12)
    soft_glow(floorpool, cx, m(VP[1] + 90), m(50), LANTERN_CORE, 30, layers=10)
    surf.blit(floorpool, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── the hero stall face: a glowing gift crate under an awning ────────────
    fw, fh = 132, 96
    face = pygame.Rect(cx - m(fw) // 2, cy - m(fh) // 2, m(fw), m(fh))
    # mystery aura behind the crate
    soft_glow(surf, face.centerx, face.centery, m(50), (255, 150, 70),
              44, layers=10)
    # posts
    post_w = m(9)
    awn_h = m(24)
    for px in (face.x - post_w, face.right):
        post = pygame.Rect(px, face.y - awn_h - m(6), post_w,
                           face.h + awn_h + m(20))
        drop_shadow(surf, post, m(2), blur=m(3), alpha=100, dy=m(2))
        surf.blit(vgrad(post.w, post.h, m(2), POST_TOP, POST_BOT), post.topleft)
        pygame.draw.rect(surf, (26, 14, 6), post, width=max(1, m(1)),
                         border_radius=m(2))

    # recessed cavity, brighter than the side stalls (the hero glows)
    cav = face.inflate(0, m(6))
    drop_shadow(surf, cav, m(8), blur=m(7), alpha=140, dy=m(3))
    surf.blit(vgrad(cav.w, cav.h, m(8), (70, 44, 36), (28, 16, 18), 255,
                    gamma=1.18), cav.topleft)
    soft_glow(surf, cav.centerx, cav.centery, m(fw * 0.34),
              (255, 176, 92), 52, layers=9)
    contact_shadow(surf, cav, m(8), m(7), alpha=110)
    pygame.draw.rect(surf, (8, 5, 6), cav, width=max(1, m(2)), border_radius=m(8))
    bevel_rim(surf, cav, m(8), (96, 62, 28), (*CARD_RING_BRIGHT, 200),
              w=max(1, m(1.6)))

    # the real PARCELS preview good, large + rim-lit, with a faceted hero gem
    sid = store_catalog.ids_of_group("parcels")[0]
    box = int(min(fw, fh) * 0.62)
    prev = _preview_surf(sid, m(box))
    pr = prev.get_rect(center=(cav.centerx, cav.centery - m(3)))
    soft_glow(surf, cav.centerx, cav.centery, m(box * 0.5),
              (255, 196, 110), 60, layers=8)
    surf.blit(_rim_light(prev, color=(255, 240, 190), alpha=185),
              pr.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(prev, pr.topleft)
    # a legendary gem set on the crate as the "mystery" jewel tell
    facet_gem(surf, cav.centerx, cav.bottom - m(2), m(9),
              pal["gem"], pal["deep"])

    # hero awning — wider, brighter
    awn = pygame.Rect(face.x - post_w, face.y - awn_h - m(6),
                      face.w + post_w * 2, awn_h)
    _striped_awning(surf, awn, scallops=9)

    # hero hanging sign — the brightest gold keyline label of the set
    sf = font(14)
    label = "PARCELS"
    tw = _glyph_base(label, sf, m(1.0)).get_width()
    sign_w = max(tw + m(28), int(face.w * 0.9))
    sign_h = m(26)
    sign = pygame.Rect(face.centerx - sign_w // 2, awn.bottom + m(14),
                       sign_w, sign_h)
    for chx in (sign.x + m(10), sign.right - m(10)):
        pygame.draw.line(surf, (40, 26, 12), (chx, awn.bottom + m(2)),
                         (chx, sign.y), max(1, m(1.6)))
        pygame.draw.line(surf, (200, 158, 100, 170), (chx, awn.bottom + m(2)),
                         (chx, sign.y), max(1, m(0.8)))
    drop_shadow(surf, sign, m(6), blur=m(5), alpha=140, dy=m(3))
    # the hero sign body is the canonical Ramp-A gold (the brightest gold object)
    surf.blit(gold_a_fill(sign.w, sign.h, m(6)), sign.topleft)
    gloss_sweep(surf, sign, m(6), peak=70)
    pygame.draw.rect(surf, (60, 36, 8), sign, width=max(1, m(1.8)),
                     border_radius=m(6))
    bevel_rim(surf, sign, m(6), (60, 36, 8), (*GOLD_PALE, 235), w=max(1, m(1.4)))
    plain_text(surf, label, sf, sign.center, (52, 28, 4), shadow_a=0,
               weight=m(1.0), tracking=m(1.0))

    # ── Pip the lantern-keeper, standing on the lane just in front of the hero
    # crate (lower-centre, in the empty floor gap between the near stalls) so he
    # is unobstructed and clearly the merchant lighting the lane. Drawn after the
    # side stalls + hero crate, so he sits in front of everything. ────────────
    pip = parrot.get_parrot(1, 6.0)
    ph = m(108)
    pscale = ph / pip.get_height()
    pip = pygame.transform.smoothscale(
        pip, (int(pip.get_width() * pscale), int(pip.get_height() * pscale)))
    px = m(W * 0.5)
    py = m(604)
    prect = pip.get_rect(midbottom=(px, py))
    # a soft warm pool on the lane under Pip (he stands in his own light)
    keeper = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    soft_glow(keeper, px, py - m(20), m(58), LANE_GLOW, 34, layers=10)
    surf.blit(keeper, (0, 0), special_flags=pygame.BLEND_ADD)
    # contact shadow under Pip
    sh = pygame.Surface((prect.w + m(20), m(14)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 130), sh.get_rect())
    surf.blit(sh, (prect.centerx - (prect.w + m(20)) // 2, py - m(6)))
    # rim-light Pip so he reads against the dark lane end
    rim = _rim_light(pip, color=(255, 224, 150), alpha=140)
    surf.blit(rim, prect.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(pip, prect.topleft)
    # the keeper's lantern, held out to one side on a short pole — the lamp that
    # lights the whole lane (its pool is the brightest near-field light).
    lx, ly = prect.right - m(6), prect.centery - m(2)
    pygame.draw.line(surf, (40, 26, 12), (prect.right - m(20), prect.centery),
                     (lx, ly - m(8)), max(1, m(2.0)))
    draw_lantern(surf, lx, ly, m(13), big=True)
    # a tiny gold-aviator glint on Pip
    soft_glow(surf, prect.centerx + m(4), prect.top + m(30), m(5),
              (255, 240, 190), 120, layers=4)


# =============================================================================
# Lantern string — the SIGNATURE: a swag of glowing lanterns arcing overhead,
# each a soft warm pool + a faceted-glass body. Drawn last so the pools read.
# =============================================================================
def draw_lantern(surf, cx, cy, r, big=False):
    """A single hanging lantern: a warm radial pool, a faceted-glass body with a
    bright core, a gold cap + finial, drawn crisp at SS."""
    # the warm light pool (soft_glow, no mush — tight layered falloff). Kept
    # restrained: a small warm halo close to the lantern, not a screen-wash.
    pool = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    soft_glow(pool, cx, cy, int(r * (2.6 if big else 2.0)), LANE_GLOW,
              42 if big else 30, layers=9)
    soft_glow(pool, cx, cy, int(r * 1.15), LANTERN_CORE, 60 if big else 44,
              layers=7)
    surf.blit(pool, (0, 0), special_flags=pygame.BLEND_ADD)

    # gold cap
    cap_w = int(r * 1.1)
    pygame.draw.polygon(surf, (180, 130, 60),
                        [(cx - cap_w, cy - r), (cx + cap_w, cy - r),
                         (cx + int(cap_w * 0.6), cy - int(r * 1.4)),
                         (cx - int(cap_w * 0.6), cy - int(r * 1.4))])
    pygame.draw.line(surf, (255, 230, 160),
                     (cx - cap_w, cy - r), (cx + cap_w, cy - r), max(1, m(0.8)))

    # faceted glass body — a vertical hex lantern, value-stepped off a top light
    n = 6
    body = []
    for i in range(n):
        a = math.pi / 2 + 2 * math.pi * i / n
        rr = r * (1.0 if i % 3 else 0.9)
        body.append((cx + rr * math.cos(a), cy + r * 0.05 + r * math.sin(a) * 1.12))
    # fill with a warm vertical gradient via per-facet shading
    for i in range(n):
        a = body[i]
        b = body[(i + 1) % n]
        my = (a[1] + b[1]) / 2
        f = 1 - (my - (cy - r)) / (r * 2.4)
        col = lerp_color(LANTERN_GLASS, LANTERN_CORE, max(0.0, min(1.0, f)))
        pygame.draw.polygon(surf, col, [(cx, cy + r * 0.05), a, b])
    # hot core
    soft_glow(surf, cx, cy + int(r * 0.05), int(r * 0.55), (255, 248, 220),
              90, layers=6)
    # glass facet keylines + gold rim
    pygame.draw.polygon(surf, (120, 74, 28), body, max(1, m(0.9)))
    for v in body:
        pygame.draw.line(surf, (255, 224, 150, 120), (cx, cy + r * 0.05), v,
                         max(1, m(0.5)))
    # finial bead below
    pygame.draw.circle(surf, (200, 150, 70), (cx, int(body[3][1] + r * 0.18)),
                       max(2, m(2)))
    pygame.draw.circle(surf, (255, 232, 160),
                       (cx - m(0.6), int(body[3][1] + r * 0.18) - m(0.6)),
                       max(1, m(0.9)))


def draw_lantern_string(surf):
    """The signature swag: a catenary cord across the top with lanterns hung at
    intervals, the centre lantern (over the hero) the brightest."""
    n = 7
    x0, x1 = m(W * 0.04), m(W * 0.96)
    base_y = m(70)
    sag = m(46)
    cord = []
    for i in range(n * 6 + 1):
        t = i / (n * 6)
        x = x0 + (x1 - x0) * t
        # catenary-ish: dip in the middle
        y = base_y + sag * math.sin(math.pi * t) * (0.6 + 0.4 * math.sin(math.pi * t))
        cord.append((x, y))
    # the cord: a dark core under a thin warm gold thread
    pygame.draw.lines(surf, (28, 18, 10), False, cord, max(1, m(2.0)))
    pygame.draw.lines(surf, (190, 148, 92, 200), False, cord, max(1, m(0.9)))

    # hang lanterns at the node positions; centre is biggest/brightest
    for i in range(n):
        t = (i + 0.5) / n
        x = x0 + (x1 - x0) * t
        y = base_y + sag * math.sin(math.pi * t) * (0.6 + 0.4 * math.sin(math.pi * t))
        # a short drop cord to the lantern
        ly = y + m(14)
        pygame.draw.line(surf, (28, 18, 10), (x, y), (x, ly), max(1, m(1.6)))
        center = abs(t - 0.5)
        r = m(9) + int(m(5) * (1 - center * 2))     # bigger toward centre
        draw_lantern(surf, int(x), int(ly + r * 1.2), r, big=(i == n // 2))


# =============================================================================
# Header — Skybit wordmark + recessed gold balance capsule + "tap a stall" hint
# =============================================================================
def draw_header(surf):
    # a soft warm band behind the title lane for legibility (sits under the swag)
    band = pygame.Surface((DW, m(60)), pygame.SRCALPHA)
    for y in range(m(60)):
        a = int(150 * (1 - y / m(60)) ** 1.2)
        pygame.draw.line(band, (14, 10, 30, a), (0, y), (DW, y))
    surf.blit(band, (0, 0))
    # screen frame hairline (matches the constellation store)
    pygame.draw.rect(surf, (*GOLD, 60), (m(3), m(3), DW - m(6), DH - m(6)),
                     width=max(1, m(1)), border_radius=m(12))
    # gold-on-red Skybit wordmark, top-left, leaving room for the balance capsule
    title_wordmark(surf, "STORE", (m(70), m(26)), 24, tracking=m(3))
    balance_capsule(surf, DW - m(96), m(26))
    # the subtle "tap a stall" hint, centred under the wordmark lane
    plain_text(surf, "TAP A STALL TO BROWSE", font(9),
               (DW // 2, m(48)), (224, 198, 150), shadow_a=140,
               tracking=m(1.2), weight=m(0.6), keyline=(12, 8, 18), kw=m(0.6))


def balance_capsule(surf, cx, y):
    """Recessed gold balance capsule with the REAL in-game coin + a gradient-gold
    number — the same money object as the constellation store, shrunk to sit in
    the souk header beside the wordmark."""
    val = f"{BALANCE:,}"
    vf = font(17)
    vw = _glyph_base(val, vf, 0).get_width() + m(2)
    coin_d, gapc, padl, padr = m(20), m(12), m(11), m(15)
    w = padl + coin_d + gapc + vw + padr
    h = m(32)
    cap = pygame.Rect(cx - w // 2, y - h // 2, w, h)
    drop_shadow(surf, cap, h // 2, blur=m(5), alpha=130, dy=m(2))
    surf.blit(vgrad(cap.w, cap.h, h // 2, (58, 42, 22), (22, 15, 8), 255, gamma=1.1),
              cap.topleft)
    top_sheen(surf, cap, h // 2, m(12), peak=50)
    contact_shadow(surf, cap, h // 2, m(4), alpha=110)
    pygame.draw.rect(surf, (0, 0, 0, 200), cap, width=max(1, m(1.6)),
                     border_radius=h // 2)
    bevel_rim(surf, cap, h // 2, lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD_PALE, 240), w=max(1, m(1.5)))
    x = cap.x + padl
    soft_glow(surf, x + coin_d // 2, y, int(coin_d * 0.42), (255, 206, 92), 46,
              layers=6)
    coin_glyph(surf, x + coin_d // 2, y, coin_d // 2)
    x += coin_d + gapc
    gradient_text(surf, val, vf, (x + vw // 2, y), GOLD_A_TOP, GOLD_A_BOT,
                  weight=m(0.9), keyline=(96, 56, 12), kw=m(1.0), shadow=True)


# =============================================================================
# Compose
# =============================================================================
def render_device():
    surf = pygame.Surface((DW, DH))
    draw_bg(surf)

    # side stalls — far rows first so the perspective stacks correctly (far
    # stalls partly behind nearer ones). Depth row drives both scale + position.
    # Layout: 3 left + 3 right receding toward the VP; X pulled toward centre +
    # Y raised as depth increases, but the face is floored so taps stay comfy.
    # row 0 = farthest (small, high, pulled toward the VP, dim) .. row 2 =
    # nearest (large, low, out at the screen edges, brightest). The x pull + the
    # y rise together angle the two rows of stalls inward toward the VP.
    DEPTH = {0: dict(scale=0.66, x=0.255, y=352, lit=0.32),
             1: dict(scale=0.82, x=0.220, y=444, lit=0.40),
             2: dict(scale=1.00, x=0.185, y=540, lit=0.48)}
    # draw far -> near so nearer stalls overlap farther ones
    order = sorted(SIDE_GROUPS, key=lambda g: g[3])
    for group, label, side, row in order:
        d = DEPTH[row]
        if side == "L":
            cx = W * d["x"]
        else:
            cx = W * (1.0 - d["x"])
        draw_stall(surf, group, label, cx, d["y"], d["scale"], lit=d["lit"])

    draw_hero(surf)
    draw_lantern_string(surf)
    draw_header(surf)
    return surf


def main():
    _build_static_bg()
    dev = render_device()
    pygame.image.save(downscale(dev, 1), os.path.join(_HERE, "round_1.png"))
    pygame.image.save(downscale(dev, 2), os.path.join(_HERE, "round_1@2x.png"))
    print("SS =", SS, "device =", DW, "x", DH)
    print("saved round_1.png + round_1@2x.png")


if __name__ == "__main__":
    main()
