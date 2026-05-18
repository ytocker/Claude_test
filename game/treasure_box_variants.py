"""Treasure box power-up — round 7: visible wood-plank construction.

User feedback on round 6: the smooth-gradient flat-top still read as
a briefcase. Real wooden chests are built from individual planks
joined together — the SEAMS between planks, the knots, and the per-
plank colour drift are what sell "this is wood" instead of "this is a
manufactured shell."

Round 7 rebuilds the chest face from individual planks:
  - Body front face: 4 vertical planks (each ~10 px wide), each plank
    has its own slight wood-tone variation + grain streaks + dark gap
    seams between neighbouring planks. One plank carries a small knot.
  - Lid front face: 3 horizontal planks (top, mid, bottom slats),
    same per-plank colour drift + horizontal grain + dark gap seams
    between them.
  - Iron wrap-straps unchanged geometrically — they sit on top of the
    plank face, hiding part of two planks each.

Only one variant in the registry — user picked variant #1 in round 5
and asked for two refinements (flat top + plank texture). When they
approve the texture I'll spin off siblings for the colour palette and
hardware passes.

Preview-only — nothing in game/ imports this yet."""
import math
import pathlib
import pygame

from game.draw import (
    UI_GOLD, NEAR_BLACK, WHITE,
    COIN_LIGHT, COIN_DARK, lerp_color,
)


# ── shared palette ──────────────────────────────────────────────────────────

DK_OUTLINE = (18, 10, 6)
GOLD_HI    = (255, 235, 150)
BRASS_BASE = (210, 165,  60)
BRASS_HI   = (255, 230, 140)
BRASS_DK   = (130,  90,  20)
IRON_BASE  = ( 78,  74,  82)
IRON_DARK  = ( 32,  30,  36)
IRON_HI    = (150, 146, 156)
ROPE_BASE  = (170, 120,  62)
ROPE_DARK  = ( 60,  35,  15)

# Warm oak base tones. Each plank picks slight RGB shifts off these to
# get the per-plank colour drift you see on real timber.
WOOD_HI   = (175, 122,  68)
WOOD_MID  = (130,  82,  40)
WOOD_DARK = ( 70,  40,  14)
WOOD_GROOVE = ( 30,  18,   6)   # the dark seam between planks


# ── font cache ──────────────────────────────────────────────────────────────

_font_cache: dict = {}
_FONT_PATH = pathlib.Path(__file__).parent / "assets" / "LiberationSans-Bold.ttf"


def _font(size):
    f = _font_cache.get(size)
    if f is None:
        f = pygame.font.Font(str(_FONT_PATH), size)
        _font_cache[size] = f
    return f


# ── spill trail (a coin pops out the lid-body seam on every flap) ───────────

def _draw_coin(surf, cx, cy, r=8, squeeze=1.0):
    w = max(2, int(r * 2 * squeeze))
    h = r * 2
    disc = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(disc, DK_OUTLINE, pygame.Rect(0, 0, w + 2, h + 2))
    pygame.draw.ellipse(disc, COIN_DARK,  pygame.Rect(1, 1, w, h))
    inner = pygame.Rect(2, 2, max(0, w - 2), max(0, h - 2))
    if inner.w > 0 and inner.h > 0:
        for y in range(inner.h):
            t = y / max(1, inner.h - 1)
            c = lerp_color(COIN_LIGHT, COIN_DARK, t)
            pygame.draw.line(disc, c,
                             (inner.x, inner.y + y),
                             (inner.x + inner.w - 1, inner.y + y))
        if inner.w >= 6:
            f = _font(max(8, int(h * 0.7)))
            g = f.render("$", True, COIN_DARK)
            disc.blit(g, g.get_rect(center=(disc.get_width() // 2,
                                            disc.get_height() // 2)))
            pygame.draw.arc(disc, GOLD_HI,
                            pygame.Rect(2, 2, inner.w, inner.h - 2),
                            math.radians(40), math.radians(140), 1)
    surf.blit(disc, (cx - disc.get_width() // 2, cy - disc.get_height() // 2))


def _spill_trail(surf, anchor_x, anchor_y, *, side=-1):
    burst = pygame.Surface((22, 22), pygame.SRCALPHA)
    pygame.draw.line(burst, (*GOLD_HI, 230), (11,  1), (11, 21), 3)
    pygame.draw.line(burst, (*GOLD_HI, 230), ( 1, 11), (21, 11), 3)
    pygame.draw.line(burst, (255, 255, 255, 230), (11,  4), (11, 18), 1)
    pygame.draw.line(burst, (255, 255, 255, 230), ( 4, 11), (18, 11), 1)
    surf.blit(burst, (anchor_x - 11, anchor_y - 11))

    stages = (
        (  3 * side, -10, 7, 0.45),
        (  8 * side,  10, 8, 1.00),
        ( 20 * side,  28, 7, 0.70),
        ( 36 * side,  48, 6, 0.90),
    )
    for dx, dy, r, sq in stages:
        _draw_coin(surf, anchor_x + dx, anchor_y + dy, r=r, squeeze=sq)

    for dx, dy, sr in ((12 * side, 18, 2), (26 * side, 38, 2)):
        s = pygame.Surface((sr * 4, sr * 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*GOLD_HI, 220), (sr * 2, sr * 2), sr)
        pygame.draw.circle(s, (255, 255, 255, 200), (sr * 2, sr * 2),
                           max(1, sr - 1))
        surf.blit(s, (anchor_x + dx - sr * 2, anchor_y + dy - sr * 2))


def _shake_lines(surf, cx, cy, w=18, *, color=(40, 30, 20)):
    for sx in (cx - w // 2 - 7, cx + w // 2 + 7):
        for dy in (-4, 4):
            ex = sx + (4 if sx > cx else -4)
            pygame.draw.line(surf, color, (sx, cy + dy), (ex, cy + dy), 2)


# ── geometry ────────────────────────────────────────────────────────────────

BOX_W  = 40
BODY_H = 18
LID_H  = 11


def _box_rect(cx, cy):
    return pygame.Rect(cx - BOX_W // 2, cy - BODY_H // 2, BOX_W, BODY_H)


# ── plank rendering ─────────────────────────────────────────────────────────

def _shift(rgb, dr, dg, db):
    return (
        max(0, min(255, rgb[0] + dr)),
        max(0, min(255, rgb[1] + dg)),
        max(0, min(255, rgb[2] + db)),
    )


# Per-plank colour drift. Each tuple is an (R, G, B) shift applied to
# the base WOOD_HI / WOOD_MID / WOOD_DARK so each plank reads as its
# own piece of timber — some redder, some greyer, some lighter at the
# top, etc. Pulled from a quick survey of real-pirate-chest references
# where planks rarely match perfectly.
_BODY_PLANK_SHIFTS = (
    (   0,   0,   0),    # plank 1 — base oak
    ( -18, -10,  -4),    # plank 2 — slightly darker
    ( +10,  +4,  -2),    # plank 3 — slightly redder/warmer
    (  -8,  -6,  -2),    # plank 4 — slightly cooler
)
_LID_PLANK_SHIFTS = (
    ( +12,  +6,   0),    # top slat — lighter (catches more light)
    (   0,   0,   0),    # middle slat — base
    ( -16,  -8,  -4),    # bottom slat — shadowed
)


def _paint_vertical_plank(surf, rect, hi, mid, dark):
    """One vertical plank: top-to-bottom gradient + a few vertical
    grain streaks for texture."""
    # Gradient fill (top lighter, bottom darker)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        c = lerp_color(hi, mid, t)
        pygame.draw.line(surf, c,
                         (rect.x, rect.y + y),
                         (rect.right - 1, rect.y + y))
    # Bottom 1/3 darker shadow
    for y in range(rect.h * 2 // 3, rect.h):
        t = (y - rect.h * 2 // 3) / max(1, rect.h // 3 - 1)
        c = lerp_color(mid, dark, t)
        pygame.draw.line(surf, c,
                         (rect.x, rect.y + y),
                         (rect.right - 1, rect.y + y))
    # Vertical grain streaks — 2-3 thin darker lines running the height
    # of the plank, at slightly random horizontal positions
    grain_xs = (rect.w // 3, rect.w // 2 + 1, rect.w - 3)
    for gx_off in grain_xs:
        gx = rect.x + gx_off
        if rect.x < gx < rect.right - 1:
            pygame.draw.line(surf, dark,
                             (gx, rect.y + 1),
                             (gx, rect.bottom - 2), 1)


def _paint_horizontal_plank(surf, rect, hi, mid, dark):
    """One horizontal plank (used on the lid): top-to-bottom gradient
    + horizontal grain streaks running along the plank's length."""
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        c = lerp_color(hi, mid, t)
        pygame.draw.line(surf, c,
                         (rect.x, rect.y + y),
                         (rect.right - 1, rect.y + y))
    # Horizontal grain — 1 darker line near the centre of the plank
    if rect.h >= 3:
        gy = rect.y + rect.h // 2
        pygame.draw.line(surf, dark,
                         (rect.x + 2, gy),
                         (rect.right - 3, gy), 1)


def _draw_body_planks(surf, body):
    """Paint the body face as 4 vertical planks with dark seam-grooves
    between them and a single knot on one plank."""
    n = 4
    plank_w = body.w // n
    for i in range(n):
        plank_x = body.x + i * plank_w
        # Last plank picks up any width remainder
        pw = plank_w if i < n - 1 else body.right - plank_x
        rect = pygame.Rect(plank_x, body.y, pw, body.h)
        ds = _BODY_PLANK_SHIFTS[i]
        hi   = _shift(WOOD_HI,   *ds)
        mid  = _shift(WOOD_MID,  *ds)
        dark = _shift(WOOD_DARK, *ds)
        _paint_vertical_plank(surf, rect, hi, mid, dark)

    # Dark seam-grooves between planks
    for i in range(1, n):
        gx = body.x + i * plank_w
        pygame.draw.line(surf, WOOD_GROOVE,
                         (gx, body.y + 1), (gx, body.bottom - 1), 1)

    # Knot on plank 3 (slightly off-centre, near the upper-mid of the plank)
    knot_cx = body.x + 2 * plank_w + plank_w // 2 + 1
    knot_cy = body.y + body.h // 3
    pygame.draw.circle(surf, NEAR_BLACK, (knot_cx, knot_cy), 2)
    pygame.draw.circle(surf, WOOD_GROOVE, (knot_cx, knot_cy), 1)


def _draw_lid_planks(surf, lid):
    """Paint the lid as 3 horizontal slats with dark seam-grooves
    between them."""
    n = 3
    plank_h = lid.h // n
    for i in range(n):
        plank_y = lid.y + i * plank_h
        ph = plank_h if i < n - 1 else lid.bottom - plank_y
        rect = pygame.Rect(lid.x, plank_y, lid.w, ph)
        ds = _LID_PLANK_SHIFTS[i]
        hi   = _shift(WOOD_HI,   *ds)
        mid  = _shift(WOOD_MID,  *ds)
        dark = _shift(WOOD_DARK, *ds)
        _paint_horizontal_plank(surf, rect, hi, mid, dark)

    # Dark seam-grooves between lid slats
    for i in range(1, n):
        gy = lid.y + i * plank_h
        pygame.draw.line(surf, WOOD_GROOVE,
                         (lid.x + 1, gy), (lid.right - 2, gy), 1)


# ── carry ropes + chest assembly ────────────────────────────────────────────

def _draw_carry_ropes(surf, bird_cx, bird_cy, body_rect, lid_y):
    for tx, talon_dx in ((body_rect.x + 4, -3), (body_rect.right - 5, 3)):
        sx, sy = bird_cx + talon_dx, bird_cy + 22
        ex, ey = tx, lid_y - 1
        pygame.draw.line(surf, ROPE_DARK, (sx, sy), (ex, ey), 4)
        pygame.draw.line(surf, ROPE_BASE, (sx, sy), (ex, ey), 2)
        rx, ry = (sx + ex) // 2, (sy + ey) // 2
        pygame.draw.line(surf, ROPE_DARK, (rx - 2, ry - 1), (rx + 2, ry + 1), 1)


def _draw_chest(surf, body):
    """Flat-top plank chest: lid + body, both built from visible planks
    with dark seam-grooves between them. Returns the lid rect."""
    lid = pygame.Rect(body.x - 1, body.y - LID_H, body.w + 2, LID_H)

    # Hairline dark outline behind both pieces
    pygame.draw.rect(surf, DK_OUTLINE, lid.inflate(2, 2), border_radius=2)
    pygame.draw.rect(surf, DK_OUTLINE, body.inflate(2, 2), border_radius=2)

    # Paint the plank faces
    _draw_lid_planks(surf, lid)
    _draw_body_planks(surf, body)

    # The seam between lid and body (deeper/darker — this is where the
    # lid would crack open if hinged).
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(body.x, body.y - 1, body.w, 2))

    # Faint top-edge sheen on the lid to suggest sunlight catching the
    # rounded top corners of the planks.
    pygame.draw.line(surf, _shift(WOOD_HI, 20, 14, 6),
                     (lid.x + 3, lid.y + 1), (lid.right - 4, lid.y + 1), 1)

    return lid


def _draw_wrap_strap(surf, body, lid, dx_from_centre, *,
                     strap_w=4,
                     dark=IRON_DARK, mid=IRON_BASE, hi=IRON_HI):
    strap_cx = body.centerx + dx_from_centre
    strap_x = strap_cx - strap_w // 2
    band = pygame.Rect(strap_x, lid.y, strap_w, body.bottom - lid.y)
    pygame.draw.rect(surf, dark, band)
    pygame.draw.rect(surf, mid,  band.inflate(-2, 0))
    pygame.draw.line(surf, hi,
                     (band.x + 1, band.y + 1),
                     (band.x + 1, band.bottom - 1), 1)
    # Cap where the strap bends over the lid's top edge
    cap = pygame.Rect(strap_x - 1, lid.y - 2, strap_w + 2, 3)
    pygame.draw.rect(surf, dark, cap)
    pygame.draw.line(surf, hi,
                     (cap.x + 1, cap.y), (cap.right - 2, cap.y), 1)
    # Rivets — one at the top of the body strap, one near the bottom
    for ry in (body.y + 3, body.bottom - 3):
        pygame.draw.circle(surf, dark, (strap_cx, ry), 2)
        pygame.draw.circle(surf, hi,   (strap_cx, ry), 1)


def _draw_corner_studs(surf, rect):
    for cnx, cny in (
        (rect.x + 2,     rect.y + 2),
        (rect.right - 3, rect.y + 2),
        (rect.x + 2,     rect.bottom - 3),
        (rect.right - 3, rect.bottom - 3),
    ):
        pygame.draw.circle(surf, BRASS_DK,   (cnx, cny), 2, 0)
        pygame.draw.circle(surf, BRASS_BASE, (cnx, cny), 1, 0)
        pygame.draw.circle(surf, BRASS_HI,   (cnx - 1, cny - 1), 1, 0)


def _draw_lock_plate(surf, body):
    lp = pygame.Rect(body.centerx - 6, body.centery - 4, 12, 9)
    pygame.draw.ellipse(surf, BRASS_DK,   lp.inflate(2, 2))
    pygame.draw.ellipse(surf, BRASS_BASE, lp)
    pygame.draw.arc(surf, BRASS_HI, lp.inflate(-2, -2),
                    math.radians(180), math.radians(360), 1)
    pygame.draw.circle(surf, NEAR_BLACK, (lp.centerx, lp.centery - 1), 2)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(lp.centerx - 1, lp.centery, 2, 3))


# ════════════════════════════════════════════════════════════════════════════
# CLASSIC OAK — FLAT TOP — PLANKED
# ════════════════════════════════════════════════════════════════════════════

def draw_planked_oak(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    lid_y = body.y - LID_H
    _draw_carry_ropes(surf, bird_cx, bird_cy, body, lid_y)

    lid = _draw_chest(surf, body)

    _draw_wrap_strap(surf, body, lid, dx_from_centre=-10)
    _draw_wrap_strap(surf, body, lid, dx_from_centre= 10)

    _draw_corner_studs(surf, body)
    _draw_corner_studs(surf, lid)
    _draw_lock_plate(surf, body)

    _shake_lines(surf, cx, body.y - LID_H // 2, w=BOX_W, color=(45, 28, 12))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ── Registry ────────────────────────────────────────────────────────────────

VARIANTS = [
    ("planked_oak", "PLANKED OAK — FLAT TOP", draw_planked_oak),
]
