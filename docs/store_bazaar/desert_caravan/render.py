"""
Store BAZAAR landing — concept #5 DESERT CARAVAN AT DUSK (selection prototype).

A merchant caravan halted among the sandstone pillars at dusk: a shallow
horseshoe of seven canopied wagons enclosing a campfire, with the PARCELS
star-tent as the glowing mystery hero and Pip the macaw perched as caravan-
master atop the lead wagon. This is a docs-only mockup of the STORE landing
HUB — the screen the player lands on before tapping a category into its grid.

WHY the same SS=4 author-then-downscale pipeline as the constellation store:
the amateur look at 360x640 is aliasing, so everything is authored oversized on
a 1440x2560 device canvas (curves, bevels, hairlines, type at size*SS) and the
single smoothscale down is what turns oversized geometry into crisp edges. This
sheet REUSES the constellation store's locked primitive kit (gold ramp A, glow,
gradient type, coin glyph, cabochon, bevel) so the bazaar leads cohesively into
the night jewel store, and it leans on the real game world — biome dusk palette,
sandstone pillar bodies, ground tones — so it unmistakably reads as Skybit after
dark.

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
_CONST = os.path.join(_ROOT, "docs", "store_redesign", "constellation_hi")
for _p in (_ROOT, _CONST):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from game.draw import lerp_color, NEAR_BLACK, WHITE, get_stone_pillar_body
from game.biome import palette_for_phase
from game import parrot
from game import store_catalog

# REUSE the constellation store's locked primitive kit so the bazaar shares one
# gold language with the jewel store it feeds into.
from render_hi import (
    SS, DW, DH, m, mf, font,
    vgrad, vgrad_stops, gold_a_fill, soft_glow, drop_shadow,
    gradient_text, plain_text, coin_glyph, bevel_rim, top_sheen, gold_rule,
    title_wordmark, downscale, _glyph_base,
    GOLD, GOLD_PALE, GOLD_DEEP, NAME_COL, CREAM,
    GOLD_A_TOP, GOLD_A_BOT, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT,
    TITLE_TOP, TITLE_BOT,
)


# ── dusk desert palette ───────────────────────────────────────────────────────
# Pull the real game's DUSK biome tones, then converge the SKY toward the jewel
# store's indigo+gold at the top so the push into the night store is a seamless
# dissolve. The stone is nudged warmer than raw dusk-lavender so the sandstone
# columns keep their desert identity while staying in the dusk family.
DUSK = palette_for_phase(0.512)


def _rgb(key):
    return tuple(int(round(c)) for c in DUSK[key])


def warm(c, amt=0.34):
    """Bias a dusk-lavender stone toward sandstone amber — keeps the desert
    read without leaving the dusk palette."""
    return lerp_color(c, (214, 168, 120), amt)


# warmed well past raw dusk-lavender so the columns clearly read as DESERT
# sandstone (the caravan's home terrain), while the dusk violet still tints the
# shadow tones for the time-of-day bridge into the night store.
STONE_LIGHT = warm(_rgb("stone_light"), 0.62)
STONE_MID = warm(_rgb("stone_mid"), 0.56)
STONE_DARK = lerp_color(warm(_rgb("stone_dark"), 0.34), (38, 22, 30), 0.4)
STONE_ACCENT = warm(_rgb("stone_accent"), 0.55)

# Sky: indigo crown (jewel-store nebula) easing through dusk violet to a warm
# rose-amber band at the horizon where the sun has just dropped.
SKY_STOPS = [
    (0.00, (10, 11, 34)),       # indigo crown -> leads into the night store
    (0.20, (24, 20, 66)),
    (0.44, (58, 40, 104)),      # dusk violet
    (0.66, (118, 70, 120)),
    (0.82, (196, 110, 110)),    # rose
    (1.00, (236, 150, 96)),     # warm sun-just-set amber band
]
SAND_TOP = warm(_rgb("ground_top"), 0.42)
SAND_BOT = warm(_rgb("ground_mid"), 0.30)
SAND_DEEP = lerp_color(SAND_BOT, NEAR_BLACK, 0.45)

FIRE_CORE = (255, 238, 196)
FIRE_GOLD = (255, 196, 88)
FIRE_DEEP = (228, 120, 40)
RED_OUT = (168, 32, 16)
CANVAS_CREAM = (244, 230, 200)
CANVAS_RED = (176, 48, 36)
WOOD = (96, 60, 38)
WOOD_DK = (54, 32, 20)
WHEEL = (70, 46, 30)


# ── catalog adapters ──────────────────────────────────────────────────────────
GROUP_LABEL = {
    "costume": "COSTUMES",
    "parrot": "PARROTS",
    "animal": "ANIMALS",
    "shoes": "SHOES",
    "hats": "HATS",
    "shades": "SHADES",
    "parcels": "PARCELS",
}


def preview_id(group):
    """The representative paid item for a category — the first id in the group,
    per the bazaar brief (REAL thumbnail, not a placeholder)."""
    return store_catalog.ids_of_group(group)[0]


_thumb_cache = {}


def preview_thumb(sid, box_px):
    """The category's real product art, scaled to fit a box. Uses the same
    icon-or-frame fallback the live store uses so shoe/hat/parcel cards show the
    item itself and skins show the macaw."""
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


def _rim_light(img, color=(255, 246, 214), alpha=150, off=None):
    """Crisp top-left rim so the preview pops off the dark canvas interior."""
    w, h = img.get_size()
    if off is None:
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


def blit_preview(surf, sid, cx, cy, box_px):
    t = preview_thumb(sid, box_px)
    r = t.get_rect(center=(cx, cy))
    surf.blit(_rim_light(t), r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(t, r.topleft)


# ── background: sky + first stars + sandstone pillars + sand + campfire ────────
_static_bg = None


def _draw_sky(surf):
    surf.blit(vgrad_stops(DW, DH, 0, SKY_STOPS, 255), (0, 0))
    # the warm afterglow where the sun set — a WIDE low band hugging the horizon
    # (elliptical, low peak) so it reads as the last light, not a white column.
    glow = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for i in range(12, 0, -1):
        rx = m(300) * i // 12
        ry = m(90) * i // 12
        a = int(18 * (1 - (i - 1) / 12) ** 1.5)
        ell = pygame.Surface((rx * 2 + 2, ry * 2 + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(ell, (255, 174, 100, a), ell.get_rect())
        glow.blit(ell, (DW // 2 - rx, int(DH * 0.38) - ry),
                  special_flags=pygame.BLEND_ADD)
    surf.blit(glow, (0, 0))


def _draw_stars(surf):
    """First dusk stars in the indigo crown only — they thin out toward the
    still-lit horizon, the natural dusk read and a nod to the jewel store sky."""
    rnd = random.Random(51)
    for _ in range(120):
        x = rnd.randint(m(6), DW - m(6))
        yf = rnd.random() ** 1.6                      # bias high, into the indigo
        y = int(m(8) + yf * DH * 0.46)
        a = int(rnd.randint(40, 170) * (1.0 - yf))    # fade out toward horizon
        if a <= 6:
            continue
        r = m(rnd.uniform(0.4, 1.4))
        tint = rnd.choice([(255, 252, 240), (216, 222, 255), (255, 234, 200)])
        pygame.draw.circle(surf, (*tint, a), (x, y), max(1, int(r)))
    for _ in range(7):                                # a few bright 4-point stars
        x = rnd.randint(m(24), DW - m(24))
        y = rnd.randint(m(20), int(DH * 0.30))
        L = m(rnd.uniform(2.5, 4.5))
        col = (255, 244, 212, rnd.randint(140, 210))
        pygame.draw.line(surf, col, (x - L, y), (x + L, y), max(1, m(0.7)))
        pygame.draw.line(surf, col, (x, y - L), (x, y + L), max(1, m(0.7)))
        soft_glow(surf, x, y, m(3), (255, 242, 206), 70, layers=4)


def _pillar_silhouette(surf, cx, base_y, w, h, seed, dark=0.0):
    """A single sandstone pillar body (REUSED game primitive) tapered to a
    spire, planted with its base at base_y. `dark` sinks it toward dusk
    silhouette for the far columns so the caravan reads in front of them."""
    body = get_stone_pillar_body(
        w, h,
        lerp_color(STONE_LIGHT, STONE_DARK, dark),
        lerp_color(STONE_MID, STONE_DARK, dark),
        STONE_DARK,
        lerp_color(STONE_ACCENT, STONE_MID, dark),
        body_seed=seed,
    )
    # taper to a rounded spire so the column reads as a desert pillar, not a slab
    poly = [(int(w * 0.30), 0), (int(w * 0.70), 0),
            (int(w * 0.86), int(h * 0.16)), (w, int(h * 0.34)),
            (int(w * 0.92), int(h * 0.62)), (w, h), (0, h),
            (int(w * 0.08), int(h * 0.62)), (0, int(h * 0.34)),
            (int(w * 0.14), int(h * 0.16))]
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    col = body.copy()
    col.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # contact shadow so each column sits on the sand
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 90), [(int(p[0]), int(p[1])) for p in poly])
    surf.blit(sh, (cx - w // 2 + m(3), base_y - h + m(2)))
    surf.blit(col, (cx - w // 2, base_y - h))
    if dark > 0.4:
        # blue-dusk haze over the far columns to push them back behind the camp
        haze = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(haze, (40, 34, 86, int(120 * dark)), poly)
        surf.blit(haze, (cx - w // 2, base_y - h))


def _draw_pillars(surf):
    """A loose colonnade framing the caravan: tall hazed silhouettes far back,
    a strong lit pillar at each side framing the horseshoe."""
    horizon = int(DH * 0.40)
    # far colonnade — hazed, receding behind the wagons
    far = [(m(36), m(58), m(300), 0.78, 11),
           (m(96), m(40), m(360), 0.86, 4),
           (m(196), m(46), m(330), 0.82, 7),
           (m(268), m(64), m(280), 0.74, 2),
           (m(324), m(50), m(340), 0.84, 9)]
    for cx, w, h, dk, sd in far:
        _pillar_silhouette(surf, cx, horizon + m(20), w, h, sd, dark=dk)
    # the two FRAMING pillars: tall lit sandstone columns hugging the screen
    # edges, framing the caravan and catching campfire warmth on their inner
    # faces. Narrow + edge-planted so they frame rather than wall-in the camp.
    _pillar_silhouette(surf, m(6), horizon + m(50), m(74), m(540), 6, dark=0.12)
    _pillar_silhouette(surf, DW - m(6), horizon + m(46), m(70), m(520), 13, dark=0.16)


def _draw_sand(surf):
    """The desert floor — warm dusk sand tones (the game's ground palette,
    warmed), darkening to the foreground so the wagons + fire sit on a grounded
    base. Soft dunes ripple the horizon."""
    horizon = int(DH * 0.40)
    sand = vgrad_stops(DW, DH - horizon, 0,
                       [(0.0, SAND_TOP), (0.45, SAND_BOT), (1.0, SAND_DEEP)], 255)
    surf.blit(sand, (0, horizon))
    # a thin warm rim where sand meets the afterglow
    glow = pygame.Surface((DW, m(26)), pygame.SRCALPHA)
    for y in range(m(26)):
        a = int(120 * (1 - y / m(26)) ** 1.4)
        pygame.draw.line(glow, (255, 176, 110, a), (0, y), (DW, y))
    surf.blit(glow, (0, horizon - m(13)))
    # gentle dune ridges scalloping the mid-ground
    rnd = random.Random(7)
    for k, (yy, alpha) in enumerate(((horizon + m(60), 46), (horizon + m(150), 38))):
        pts = [(0, yy)]
        x = 0
        while x < DW:
            x += m(rnd.uniform(40, 80))
            pts.append((x, yy - m(rnd.uniform(2, 12))))
        pts += [(DW, yy + m(40)), (0, yy + m(40))]
        rib = pygame.Surface((DW, DH), pygame.SRCALPHA)
        pygame.draw.polygon(rib, (20, 14, 30, alpha), pts)
        surf.blit(rib, (0, 0))


def _build_static_bg():
    global _static_bg
    surf = pygame.Surface((DW, DH))
    _draw_sky(surf)
    _draw_stars(surf)
    _draw_pillars(surf)
    _draw_sand(surf)
    _static_bg = surf


# ── the wagon (the shared stall template) ──────────────────────────────────────
def _wagon_card(surf, cx, base_y, w, sid, label, fire_xy, hero=False):
    """One canopied merchant wagon = one category stall. The CANOPY is the
    tappable sign carrying the category name; the wagon body holds the real
    preview thumbnail behind a window, lit warm from the central campfire. The
    whole tile is the tap target. `hero=False`; PARCELS uses _star_tent instead.

    Returns the canopy Rect (the tap-target sign region) for the notes layout.
    """
    canopy_h = int(w * 0.40)
    body_h = int(w * 0.74)
    total_h = canopy_h + body_h
    top_y = base_y - total_h
    rad = m(7)

    # firelight direction (warm side faces the camp) for the rim accents
    lit_left = fire_xy[0] > cx

    # ── drop shadow of the whole wagon onto the sand
    sh = pygame.Rect(cx - w // 2 + m(4), top_y + m(6), w, total_h)
    drop_shadow(surf, sh, rad, blur=m(9), alpha=150, dy=m(5))

    # ── wheels (simplified, per the brief's "simplify wheels") peeking below
    wr = int(w * 0.16)
    for sgn in (-1, 1):
        wx = cx + sgn * (w // 2 - wr - m(2))
        wy = base_y - wr + m(2)
        pygame.draw.circle(surf, (0, 0, 0, 120), (wx + m(2), wy + m(3)), wr)
        pygame.draw.circle(surf, WHEEL, (wx, wy), wr)
        pygame.draw.circle(surf, WOOD_DK, (wx, wy), wr, max(1, m(2)))
        pygame.draw.circle(surf, lerp_color(WOOD, GOLD_DEEP, 0.3),
                           (wx, wy), int(wr * 0.42))
        for a in range(0, 360, 45):
            ex = wx + int(wr * 0.86 * math.cos(math.radians(a)))
            ey = wy + int(wr * 0.86 * math.sin(math.radians(a)))
            pygame.draw.line(surf, WOOD_DK, (wx, wy), (ex, ey), max(1, m(1.4)))

    # ── wagon body: warm wood box with a dark display window
    body = pygame.Rect(cx - w // 2, top_y + canopy_h - m(2), w, body_h)
    surf.blit(vgrad(body.w, body.h, rad, lerp_color(WOOD, STONE_MID, 0.2),
                    WOOD_DK, 255, gamma=1.1), body.topleft)
    # plank seams
    for k in range(1, 4):
        py = body.y + body.h * k // 4
        pygame.draw.line(surf, (*WOOD_DK, 180), (body.x + m(3), py),
                         (body.right - m(3), py), max(1, m(1)))
    pygame.draw.rect(surf, WOOD_DK, body, width=max(1, m(2)), border_radius=rad)
    bevel_rim(surf, body, rad, WOOD_DK, (*lerp_color(GOLD, WOOD, 0.4), 210),
              w=max(1, m(1.4)))

    # display window the preview sits inside — a dark recessed cabochon-like well
    win_pad = m(7)
    win = body.inflate(-win_pad * 2, -win_pad * 2)
    win.height = int(win.height * 0.82)
    win.y = body.y + win_pad
    surf.blit(vgrad(win.w, win.h, m(5), (26, 20, 30), (10, 7, 14), 255),
              win.topleft)
    # warm interior glow from the campfire spilling into the window
    iglow = pygame.Surface(win.size, pygame.SRCALPHA)
    gx = win.w // 2 + (m(10) if lit_left else -m(10))
    soft_glow(iglow, gx, win.h // 2, int(win.w * 0.5), (255, 170, 90), 70, layers=8)
    wm = pygame.Surface(win.size, pygame.SRCALPHA)
    pygame.draw.rect(wm, (255, 255, 255, 255), wm.get_rect(), border_radius=m(5))
    iglow.blit(wm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(iglow, win.topleft, special_flags=pygame.BLEND_ADD)
    # the REAL category preview thumbnail
    blit_preview(surf, sid, win.centerx, win.centery, int(min(win.w, win.h) * 0.80))
    pygame.draw.rect(surf, (0, 0, 0, 200), win, width=max(1, m(1.4)),
                     border_radius=m(5))
    pygame.draw.rect(surf, (*GOLD_DEEP, 150), win, width=max(1, m(1)),
                     border_radius=m(5))

    # ── canopy: striped awning = the SIGN. The category name rides a gold
    # keyline plate on the canopy face so it reads from the periphery.
    cnp = pygame.Rect(cx - w // 2 - m(3), top_y, w + m(6), canopy_h)
    _striped_canopy(surf, cnp, rad, lit_left)
    # gold name plate
    f = font(11.5 if len(label) <= 7 else 10.5)
    plate_w = min(cnp.w - m(8), _glyph_base(label, f, m(0.5)).get_width() + m(18))
    plate = pygame.Rect(0, 0, plate_w, m(17))
    plate.center = (cx, cnp.y + canopy_h // 2 + m(1))
    surf.blit(gold_a_fill(plate.w, plate.h, plate.h // 2), plate.topleft)
    pygame.draw.rect(surf, GOLD_A_RIM_DARK, plate, width=max(1, m(1.4)),
                     border_radius=plate.h // 2)
    bevel_rim(surf, plate, plate.h // 2, GOLD_A_RIM_DARK,
              (*GOLD_A_RIM_BRIGHT, 220), w=max(1, m(1)))
    plain_text(surf, label, f, plate.center, (44, 26, 6), shadow_a=0,
               weight=m(0.9), tracking=m(0.5))
    return cnp


def _striped_canopy(surf, rect, rad, lit_left):
    """Scalloped striped awning (cream + macaw red), peaked and edge-lit by the
    campfire on the side facing the camp."""
    # peaked roof: a low triangle ridge above the rectangle
    ridge = m(8)
    peak = [(rect.centerx, rect.y - ridge),
            (rect.right, rect.y + m(2)), (rect.x, rect.y + m(2))]
    pygame.draw.polygon(surf, lerp_color(CANVAS_RED, NEAR_BLACK, 0.2), peak)
    # striped body
    n = 6
    sw = rect.w / n
    for i in range(n):
        col = CANVAS_CREAM if i % 2 == 0 else CANVAS_RED
        x0 = rect.x + sw * i
        pygame.draw.rect(surf, col, (int(x0), rect.y + m(2),
                                     int(sw) + 1, rect.h - m(2)))
    # scalloped lower hem
    hem_y = rect.bottom
    for i in range(n):
        x0 = int(rect.x + sw * i)
        col = CANVAS_CREAM if i % 2 == 0 else CANVAS_RED
        pygame.draw.polygon(surf, col,
                            [(x0, hem_y - m(3)), (x0 + int(sw) + 1, hem_y - m(3)),
                             (x0 + int(sw / 2), hem_y + m(5))])
    # warm firelit sheen across the awning
    sheen = pygame.Surface(rect.size, pygame.SRCALPHA)
    side = 0 if lit_left else rect.w
    soft_glow(sheen, int(side), rect.h // 2, int(rect.w * 0.7), (255, 200, 120),
              60, layers=8)
    surf.blit(sheen, rect.topleft, special_flags=pygame.BLEND_ADD)
    # crisp edges
    pygame.draw.lines(surf, (60, 14, 10), False,
                      [(rect.x, rect.y + m(2)), (rect.centerx, rect.y - ridge),
                       (rect.right, rect.y + m(2))], max(1, m(2)))
    pygame.draw.line(surf, (60, 14, 10), (rect.x, rect.bottom - m(3)),
                     (rect.right, rect.bottom - m(3)), max(1, m(1.4)))


# ── the PARCELS star-tent (the glowing mystery hero) ────────────────────────────
def _star_tent(surf, cx, base_y, w, sid, fire_xy):
    """The PARCELS stall: a tall glowing conical star-tent crowning the arc — the
    mystery hero. A radiant gold tent-cone with a star finial, its doorway a
    bright portal showing the parcel preview, brighter than every wagon so the
    eye lands here first. Returns the tappable sign Rect (the doorway plate)."""
    tent_h = int(w * 1.30)
    top_y = base_y - tent_h
    apex = (cx, top_y)

    # outer aura — the tent is the brightest light source after the fire, but a
    # CONTAINED bloom (low peak, hugging the cone) so it reads as a lit tent, not
    # a white blowout. A tall soft halo behind the cone.
    aura = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for i in range(12, 0, -1):
        rx = int(w * 0.62) * i // 12
        ry = int(tent_h * 0.70) * i // 12
        a = int(20 * (1 - (i - 1) / 12) ** 1.7)
        ell = pygame.Surface((rx * 2 + 2, ry * 2 + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(ell, (255, 200, 116, a), ell.get_rect())
        aura.blit(ell, (cx - rx, top_y + int(tent_h * 0.46) - ry),
                  special_flags=pygame.BLEND_ADD)
    surf.blit(aura, (0, 0))

    # cone body: a tall triangle filled with a warm vertical ramp
    base_l = (cx - w // 2, base_y)
    base_r = (cx + w // 2, base_y)
    pad = m(4)
    bb = pygame.Surface((w + pad * 2, tent_h + pad * 2), pygame.SRCALPHA)
    grad = vgrad_stops(w + pad * 2, tent_h + pad * 2, 0,
                       [(0.0, (255, 230, 160)), (0.5, (236, 170, 78)),
                        (1.0, (150, 86, 26))], 255)
    cmask = pygame.Surface((w + pad * 2, tent_h + pad * 2), pygame.SRCALPHA)
    poly = [(w // 2 + pad, pad), (w + pad, tent_h + pad), (pad, tent_h + pad)]
    pygame.draw.polygon(cmask, (255, 255, 255, 255), poly)
    grad.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    bb.blit(grad, (0, 0))
    surf.blit(bb, (cx - w // 2 - pad, top_y - pad))

    # tent seams radiating from the apex
    for fx in (0.18, 0.40, 0.60, 0.82):
        bx = base_l[0] + (base_r[0] - base_l[0]) * fx
        pygame.draw.line(surf, (150, 84, 24, 200), apex, (bx, base_y),
                         max(1, m(1.2)))
    # a scalloped hem across the tent foot
    n = 7
    sw = w / n
    for i in range(n):
        x0 = int(base_l[0] + sw * i)
        col = (255, 224, 150) if i % 2 == 0 else (208, 130, 50)
        pygame.draw.polygon(surf, col,
                            [(x0, base_y - m(4)), (x0 + int(sw) + 1, base_y - m(4)),
                             (x0 + int(sw / 2), base_y + m(5))])

    # crisp lit cone edges
    pygame.draw.line(surf, (110, 60, 14), apex, base_l, max(1, m(2)))
    pygame.draw.line(surf, (255, 244, 200), apex, base_l, max(1, m(0.9)))
    pygame.draw.line(surf, (110, 60, 14), apex, base_r, max(1, m(2)))

    # ── the glowing doorway portal showing the parcel preview ──
    door_w, door_h = int(w * 0.46), int(tent_h * 0.40)
    door = pygame.Rect(cx - door_w // 2, base_y - door_h - m(4), door_w, door_h)
    # deep portal well + bright mystery glow
    surf.blit(vgrad(door.w, door.h, door_w // 2, (40, 22, 30), (12, 7, 14), 255),
              door.topleft)
    dglow = pygame.Surface(door.size, pygame.SRCALPHA)
    soft_glow(dglow, door.w // 2, int(door.h * 0.44), int(door.w * 0.6),
              (255, 196, 110), 64, layers=10)
    dm = pygame.Surface(door.size, pygame.SRCALPHA)
    pygame.draw.rect(dm, (255, 255, 255, 255), dm.get_rect(),
                     border_top_left_radius=door_w // 2,
                     border_top_right_radius=door_w // 2)
    dglow.blit(dm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(dglow, door.topleft, special_flags=pygame.BLEND_ADD)
    blit_preview(surf, sid, door.centerx, door.centery - m(2),
                 int(min(door.w, door.h) * 0.78))
    # tied-back curtains + gold portal rim
    pygame.draw.rect(surf, (0, 0, 0, 200), door, width=max(1, m(1.6)),
                     border_top_left_radius=door_w // 2,
                     border_top_right_radius=door_w // 2)
    pygame.draw.rect(surf, (*GOLD, 220), door, width=max(1, m(1.2)),
                     border_top_left_radius=door_w // 2,
                     border_top_right_radius=door_w // 2)

    # star finial at the apex
    soft_glow(surf, apex[0], apex[1], m(13), (255, 222, 150), 80, layers=8)
    _star(surf, apex[0], apex[1] - m(2), m(11), (255, 244, 196))

    # PARCELS sign plate at the doorway crown
    f = font(11.5)
    label = "PARCELS"
    plate_w = _glyph_base(label, f, m(0.6)).get_width() + m(20)
    plate = pygame.Rect(0, 0, plate_w, m(18))
    plate.center = (cx, door.y - m(11))
    drop_shadow(surf, plate, plate.h // 2, blur=m(3), alpha=110, dy=m(2))
    surf.blit(gold_a_fill(plate.w, plate.h, plate.h // 2), plate.topleft)
    pygame.draw.rect(surf, GOLD_A_RIM_DARK, plate, width=max(1, m(1.6)),
                     border_radius=plate.h // 2)
    bevel_rim(surf, plate, plate.h // 2, GOLD_A_RIM_DARK,
              (*GOLD_A_RIM_BRIGHT, 230), w=max(1, m(1.1)))
    plain_text(surf, label, f, plate.center, (44, 26, 6), shadow_a=0,
               weight=m(1.0), tracking=m(0.8))
    return plate


def _star(surf, cx, cy, r, col):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.44
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    pygame.draw.polygon(surf, col, pts)
    pygame.draw.polygon(surf, (150, 86, 26), pts, max(1, m(1)))


# ── the campfire ────────────────────────────────────────────────────────────────
def _campfire(surf, cx, cy):
    """Central campfire — the warm light source pooling onto the sand and the
    wagon canopies. Soft glow base + layered flame tongues + a few sparks."""
    # ground pool — an ELLIPTICAL warm wash on the sand (kept low-alpha so it
    # lights the camp without blowing out to white)
    pool = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for i in range(10, 0, -1):
        rx = m(150) * i // 10
        ry = m(46) * i // 10
        a = int(26 * (1 - (i - 1) / 10) ** 1.6)
        ell = pygame.Surface((rx * 2 + 2, ry * 2 + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(ell, (255, 150, 70, a), ell.get_rect())
        pool.blit(ell, (cx - rx, cy + m(6) - ry), special_flags=pygame.BLEND_ADD)
    surf.blit(pool, (0, 0))
    # log ring
    for sgn in (-1, 1):
        lr = pygame.Rect(cx + sgn * m(4) - m(20), cy + m(6), m(40), m(8))
        pygame.draw.ellipse(surf, WOOD_DK, lr)
        pygame.draw.ellipse(surf, lerp_color(WOOD, FIRE_DEEP, 0.4),
                            lr.inflate(-m(6), -m(3)))
    # flame: stacked tongues, brightest core
    for (rad, col, off, peak) in ((m(30), FIRE_DEEP, m(2), 150),
                                  (m(20), FIRE_GOLD, m(0), 200),
                                  (m(11), FIRE_CORE, -m(3), 255)):
        flame = pygame.Surface((rad * 3, rad * 4), pygame.SRCALPHA)
        fcx = rad * 3 // 2
        tip = (fcx, off)
        pts = [tip,
               (fcx + rad, rad * 2 + off),
               (fcx + int(rad * 0.4), rad * 3 + off),
               (fcx, rad * 3.4 + off),
               (fcx - int(rad * 0.4), rad * 3 + off),
               (fcx - rad, rad * 2 + off)]
        pygame.draw.polygon(flame, (*col, peak), pts)
        surf.blit(flame, (cx - fcx, cy - rad * 3), special_flags=pygame.BLEND_ADD)
    # core bloom + sparks (tight, so the flame keeps a defined edge)
    soft_glow(surf, cx, cy - m(6), m(14), (255, 236, 180), 120, layers=8)
    rnd = random.Random(99)
    for _ in range(10):
        sx = cx + m(rnd.uniform(-12, 12))
        sy = cy - m(rnd.uniform(6, 40))
        a = rnd.randint(120, 230)
        pygame.draw.circle(surf, (255, 214, 130, a), (int(sx), int(sy)),
                           max(1, m(rnd.uniform(0.6, 1.6))))


# ── Pip the caravan-master ──────────────────────────────────────────────────────
def _pip(surf, cx, cy, scale):
    """Pip the scarlet macaw perched as caravan-master atop the lead wagon, his
    gold aviators glinting with the campfire. Drawn clean (no overlapping
    frames) so he reads crisply against the dusk crown."""
    frame = parrot.get_parrot(1, 0.0)
    bb = frame.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        frame = frame.subsurface(bb).copy()
    pw, ph = frame.get_size()
    s = scale / max(pw, ph)
    img = pygame.transform.smoothscale(frame, (max(1, int(pw * s)), max(1, int(ph * s))))
    r = img.get_rect(midbottom=(cx, cy))
    # a soft contact shadow on the canopy beneath him so he sits, not floats
    sh = pygame.Surface((r.w, m(8)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 110), sh.get_rect())
    surf.blit(sh, (r.x, cy - m(4)))
    # low warm halo so the scarlet reads off the indigo crown
    soft_glow(surf, cx, r.centery, int(scale * 0.42), (255, 168, 96), 20, layers=8)
    # crisp top-left rim light (single offset) so his silhouette pops
    surf.blit(_rim_light(img, color=(255, 206, 130), alpha=95, off=m(0.7)),
              r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(img, r.topleft)
    # twin aviator glints catching the fire (tight, bright pips)
    gy = r.y + int(r.h * 0.30)
    for dx in (-int(r.w * 0.17), int(r.w * 0.04)):
        soft_glow(surf, cx + dx, gy, m(2.5), (255, 244, 206), 130, layers=4)


# ── header ──────────────────────────────────────────────────────────────────────
BALANCE = 14250


def _balance_capsule(surf, cx, y):
    """Recessed gold balance capsule with the REAL in-game coin + a loud
    gradient-gold number (same money-screen treatment as the jewel store)."""
    val = f"{BALANCE:,}"
    vf = font(22)
    vw = _glyph_base(val, vf, 0).get_width() + m(2)
    coin_d, gapc, padl, padr = m(26), m(15), m(14), m(20)
    w = padl + coin_d + gapc + vw + padr
    h = m(42)
    cap = pygame.Rect(cx - w // 2, y - h // 2, w, h)
    drop_shadow(surf, cap, h // 2, blur=m(6), alpha=140, dy=m(3))
    surf.blit(vgrad(cap.w, cap.h, h // 2, (58, 40, 20), (24, 14, 8), 255, gamma=1.1),
              cap.topleft)
    top_sheen(surf, cap, h // 2, m(15), peak=50)
    pygame.draw.rect(surf, (0, 0, 0, 200), cap, width=max(1, m(1.8)),
                     border_radius=h // 2)
    bevel_rim(surf, cap, h // 2, lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD_PALE, 240), w=max(1, m(1.8)))
    x = cap.x + padl
    soft_glow(surf, x + coin_d // 2, y, int(coin_d * 0.42), (255, 200, 90), 44, layers=6)
    coin_glyph(surf, x + coin_d // 2, y, coin_d // 2)
    x += coin_d + gapc
    gradient_text(surf, val, vf, (x + vw // 2, y), GOLD_A_TOP, GOLD_A_BOT,
                  weight=m(1.0), keyline=(92, 54, 12), kw=m(1.2), shadow=True)


def _draw_header(surf):
    # a soft indigo band keeps the wordmark legible over the bright dusk crown
    band = pygame.Surface((DW, m(96)), pygame.SRCALPHA)
    for yy in range(m(96)):
        a = int(150 * (1 - yy / m(96)) ** 1.2)
        pygame.draw.line(band, (8, 8, 28, a), (0, yy), (DW, yy))
    surf.blit(band, (0, 0))
    pygame.draw.rect(surf, (*GOLD, 60), (m(3), m(3), DW - m(6), DH - m(6)),
                     width=max(1, m(1)), border_radius=m(12))
    # Skybit gold-on-red wordmark
    title_wordmark(surf, "STORE", (DW // 2, m(28)), 31, tracking=m(4))
    _balance_capsule(surf, DW // 2, m(72))
    # subtle "tap a stall" hint
    plain_text(surf, "TAP A STALL TO BROWSE", font(9.5), (DW // 2, m(96)),
               (236, 214, 170), shadow_a=150, tracking=m(2), weight=m(0.7),
               keyline=(20, 14, 30), kw=m(0.6))


# ── compose ─────────────────────────────────────────────────────────────────────
def render_device():
    surf = pygame.Surface((DW, DH))
    surf.blit(_static_bg, (0, 0))

    # campfire centre — the warm anchor the horseshoe wraps around
    fire = (DW // 2, int(DH * 0.815))

    # ── THE HORSESHOE OF 7 WAGONS — solving the tightest-layout brief ──────────
    # All seven categories placed exactly once, depth-staged so every one reads
    # AND every canopy sign stays comfortably tappable on a 360px phone:
    #   HERO (centre back)  : PARCELS star-tent — tallest, brightest focal anchor
    #   back arc (flank tent): ANIMALS (L) + HATS (R) — raised + smaller, recede
    #   mid flanks          : COSTUMES (L) + SHADES (R) — medium, step down
    #   front pair (nearest) : SHOES = LEAD wagon (Pip rides) + PARROTS (R)
    # Drawn back-to-front so nearer wagons overlap farther ones cleanly.

    # back arc — small, raised so they read over the front pair
    _wagon_card(surf, m(74), int(DH * 0.476), m(98),
                preview_id("animal"), GROUP_LABEL["animal"], fire)
    _wagon_card(surf, m(286), int(DH * 0.476), m(98),
                preview_id("hats"), GROUP_LABEL["hats"], fire)

    # the PARCELS star-tent hero — centred on the back arc, tallest
    _star_tent(surf, m(180), int(DH * 0.566), m(122), preview_id("parcels"), fire)

    # mid flanks — medium, stepping down the sides toward the player
    _wagon_card(surf, m(50), int(DH * 0.668), m(118),
                preview_id("costume"), GROUP_LABEL["costume"], fire)
    _wagon_card(surf, m(310), int(DH * 0.668), m(118),
                preview_id("shades"), GROUP_LABEL["shades"], fire)

    # campfire in front of the tent, behind the front pair
    _campfire(surf, *fire)

    # front pair — largest, nearest tap targets; SHOES is the LEAD wagon Pip
    # rides, PARROTS the front-right. Drawn last so they sit fully in front.
    lead_cx, lead_by, lead_w = m(96), int(DH * 0.960), m(146)
    _wagon_card(surf, m(296), int(DH * 0.960), m(140),
                preview_id("parrot"), GROUP_LABEL["parrot"], fire)
    _wagon_card(surf, lead_cx, lead_by, lead_w,
                preview_id("shoes"), GROUP_LABEL["shoes"], fire)

    # Pip the caravan-master perched atop the lead (front-left) wagon canopy
    lead_total_h = int(lead_w * 0.40) + int(lead_w * 0.74)
    _pip(surf, lead_cx + m(6), lead_by - lead_total_h + m(4), m(104))

    return surf


def main():
    _build_static_bg()
    dev = render_device()
    pygame.image.save(downscale(dev, 1), os.path.join(_HERE, "round_1.png"))
    pygame.image.save(downscale(dev, 2), os.path.join(_HERE, "round_1@2x.png"))
    print("SS =", SS, "device =", DW, "x", DH)
    print("saved round_1.png / round_1@2x.png")


if __name__ == "__main__":
    main()
