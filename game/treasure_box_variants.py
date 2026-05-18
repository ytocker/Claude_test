"""Five visual treatments for the TREASURE BOX power-up — round 5.

Round 4 read more like a briefcase (flat lid + side handles + front
hasp). Round 5 commits to the iconic pirate-chest silhouette: small
CLOSED box with a curved DOMED LID, iron straps that wrap up over the
dome from the body's front face, a central lock plate, and brass
corner studs. No side handles (those were the briefcase tell). Pip
carries every variant by two short ropes from his talons to the front
corners of the body.

Each `draw_<name>(surf, bird_cx, bird_cy, t=0.0)` paints the carry
ropes, the chest, the variant-specific accent, motion lines, and the
4-coin spill cascade. The bird itself is positioned by the caller so
all variants share Pip's exact frame.

Preview-only — nothing in game/ imports this yet."""
import math
import pathlib
import pygame

from game.draw import (
    UI_GOLD, UI_CREAM, UI_ORANGE, UI_RED, NEAR_BLACK, WHITE,
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

# Wood palettes
WOOD_OAK_HI    = (185, 130,  70)
WOOD_OAK_MID   = (140,  88,  44)
WOOD_OAK_DARK  = ( 78,  44,  16)

WOOD_DOME_HI   = (165, 115,  62)
WOOD_DOME_MID  = (120,  78,  38)
WOOD_DOME_DARK = ( 68,  38,  14)

WOOD_WALNUT_HI   = ( 95,  62,  36)
WOOD_WALNUT_MID  = ( 58,  34,  18)
WOOD_WALNUT_DARK = ( 28,  16,   8)


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


# ── geometry constants ──────────────────────────────────────────────────────

BOX_W  = 40       # body width (lid is the same)
BODY_H = 18       # rectangular body height
DOME_H = 14       # how far the curved lid arcs above the body


def _box_rect(cx, cy):
    """Body rect of the closed chest. cy is the body's vertical centre.
    The domed lid arcs DOME_H px above body.y."""
    return pygame.Rect(cx - BOX_W // 2, cy - BODY_H // 2, BOX_W, BODY_H)


# ── shared helpers ──────────────────────────────────────────────────────────

def _gradient_rect(surf, rect, top_col, bot_col, *, radius=3):
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        c = lerp_color(top_col, bot_col, t) + (255,)
        body.fill(c, pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=radius)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)


def _draw_carry_ropes(surf, bird_cx, bird_cy, body_rect):
    """Two short hemp ropes from Pip's talons to the front-top corners
    of the body (where they'd loop under brass eyelets on a real chest)."""
    # Anchor points on the chest: just inside each top corner of the body.
    for tx, talon_dx in ((body_rect.x + 3, -3), (body_rect.right - 4, 3)):
        sx, sy = bird_cx + talon_dx, bird_cy + 22
        ex, ey = tx, body_rect.y - 1
        pygame.draw.line(surf, ROPE_DARK, (sx, sy), (ex, ey), 4)
        pygame.draw.line(surf, ROPE_BASE, (sx, sy), (ex, ey), 2)
        # Single fiber-hatch at the midpoint
        rx = (sx + ex) // 2
        ry = (sy + ey) // 2
        pygame.draw.line(surf, ROPE_DARK, (rx - 2, ry - 1), (rx + 2, ry + 1), 1)


def _dome_height_at(body, dx):
    """Height of the half-ellipse dome above body.y at horizontal offset
    `dx` from the body's centre. Returns 0 outside the dome footprint."""
    a = body.w / 2
    b = DOME_H
    if abs(dx) >= a:
        return 0
    return int(b * math.sqrt(max(0.0, 1.0 - (dx * dx) / (a * a))))


def _draw_dome_and_body(surf, body, *, wood_hi, wood_mid, wood_dark):
    """Iconic pirate-chest silhouette: domed lid + rectangular body, both
    in the given wood palette. Returns the bounding rect of the dome."""
    # ── Dome (filled half-ellipse on top of the body) ──
    dome_box = pygame.Rect(body.x, body.y - DOME_H, body.w, DOME_H * 2)
    # Outline (slightly enlarged ellipse behind)
    pygame.draw.ellipse(surf, DK_OUTLINE, dome_box.inflate(4, 4))
    # Gradient-filled dome, masked to the upper half of the ellipse
    dome_layer = pygame.Surface(dome_box.size, pygame.SRCALPHA)
    for y in range(dome_box.h):
        t = y / max(1, dome_box.h - 1)
        c = lerp_color(wood_hi, wood_mid, t) + (255,)
        dome_layer.fill(c, pygame.Rect(0, y, dome_box.w, 1))
    mask = pygame.Surface(dome_box.size, pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    dome_layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Cut off the lower half (we only want the dome arc above the body)
    dome_layer.fill((0, 0, 0, 0),
                    pygame.Rect(0, dome_box.h // 2, dome_box.w, dome_box.h),
                    special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(dome_layer, dome_box.topleft)

    # Faint wood-grain arcs across the dome (3 concentric thin curves)
    for i in range(3):
        r_offset = 2 + i * 3
        arc_rect = pygame.Rect(body.x + r_offset, body.y - DOME_H + r_offset,
                               body.w - 2 * r_offset, (DOME_H - r_offset) * 2)
        if arc_rect.w > 0 and arc_rect.h > 0:
            pygame.draw.arc(surf, wood_dark, arc_rect,
                            math.radians(10), math.radians(170), 1)

    # ── Dark seam line where the lid meets the body ──
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(body.x, body.y - 1, body.w, 2))

    # ── Body (rectangular, with vertical grain) ──
    pygame.draw.rect(surf, DK_OUTLINE, body.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, body, wood_mid, wood_dark, radius=2)
    # Vertical grain streaks
    for i in range(1, 4):
        gx = body.x + (body.w * i) // 4
        pygame.draw.line(surf, wood_dark,
                         (gx, body.y + 2), (gx, body.bottom - 3), 1)

    return dome_box


def _draw_wrap_strap(surf, body, dx_from_centre, *,
                     strap_w=4,
                     dark=IRON_DARK, mid=IRON_BASE, hi=IRON_HI):
    """A single iron strap that wraps from the body's front (vertical
    band on the body) UP over the dome (vertical band rising from
    body.y to the dome's height at that x). `dx_from_centre` is the
    horizontal offset of the strap's centre from the body's centre."""
    strap_cx = body.centerx + dx_from_centre
    # Body portion — full-height vertical band on the body
    body_part = pygame.Rect(strap_cx - strap_w // 2, body.y,
                            strap_w, body.h)
    pygame.draw.rect(surf, dark, body_part)
    pygame.draw.rect(surf, mid,  body_part.inflate(-2, 0))
    pygame.draw.line(surf, hi,
                     (body_part.x + 1, body_part.y + 1),
                     (body_part.x + 1, body_part.bottom - 1), 1)
    # Rivet at the bottom of the body strap
    pygame.draw.circle(surf, dark, (strap_cx, body.bottom - 3), 2)
    pygame.draw.circle(surf, hi,   (strap_cx, body.bottom - 3), 1)

    # Dome portion — vertical band from body.y UP to the dome's curve
    dh = _dome_height_at(body, dx_from_centre)
    if dh > 2:
        dome_part = pygame.Rect(strap_cx - strap_w // 2, body.y - dh,
                                strap_w, dh)
        pygame.draw.rect(surf, dark, dome_part)
        pygame.draw.rect(surf, mid,  dome_part.inflate(-2, 0))
        pygame.draw.line(surf, hi,
                         (dome_part.x + 1, dome_part.y + 1),
                         (dome_part.x + 1, dome_part.bottom - 1), 1)
        # Tiny rivet head where the strap crests the dome
        pygame.draw.circle(surf, dark, (strap_cx, body.y - dh + 2), 1)


def _draw_corner_studs(surf, body, *, color=BRASS_BASE,
                       dark=BRASS_DK, hi=BRASS_HI):
    for cnx, cny in (
        (body.x + 2,     body.y + 3),
        (body.right - 3, body.y + 3),
        (body.x + 2,     body.bottom - 3),
        (body.right - 3, body.bottom - 3),
    ):
        pygame.draw.circle(surf, dark,  (cnx, cny), 2, 0)
        pygame.draw.circle(surf, color, (cnx, cny), 1, 0)
        pygame.draw.circle(surf, hi,    (cnx - 1, cny - 1), 1, 0)


def _draw_lock_plate(surf, body, *,
                     dark=BRASS_DK, base=BRASS_BASE, hi=BRASS_HI):
    """Oval brass keyhole plate centred on the body's front face."""
    lp = pygame.Rect(body.centerx - 6, body.centery - 4, 12, 9)
    pygame.draw.ellipse(surf, dark, lp.inflate(2, 2))
    pygame.draw.ellipse(surf, base, lp)
    pygame.draw.arc(surf, hi, lp.inflate(-2, -2),
                    math.radians(180), math.radians(360), 1)
    # Keyhole
    pygame.draw.circle(surf, NEAR_BLACK, (lp.centerx, lp.centery - 1), 2)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(lp.centerx - 1, lp.centery, 2, 3))


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 1 — CLASSIC OAK
# ════════════════════════════════════════════════════════════════════════════
# Warm oak body + domed lid. Two iron straps wrap from the front of the
# body up over the dome. Central brass keyhole plate on the front body.
# The default pirate treasure chest read.

def draw_classic_oak(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _draw_dome_and_body(surf, body,
                        wood_hi=WOOD_DOME_HI, wood_mid=WOOD_DOME_MID,
                        wood_dark=WOOD_DOME_DARK)

    # Two iron wrap-straps, evenly placed away from centre
    _draw_wrap_strap(surf, body, dx_from_centre=-10)
    _draw_wrap_strap(surf, body, dx_from_centre= 10)

    _draw_corner_studs(surf, body)
    _draw_lock_plate(surf, body)

    _shake_lines(surf, cx, body.y - DOME_H, w=BOX_W, color=(45, 28, 12))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 2 — DARK WALNUT
# ════════════════════════════════════════════════════════════════════════════
# Same domed chest shape, same iron straps, same brass plate — but in
# dark walnut wood instead of warm oak. "Older / richer" sibling.

def draw_dark_walnut(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _draw_dome_and_body(surf, body,
                        wood_hi=WOOD_WALNUT_HI, wood_mid=WOOD_WALNUT_MID,
                        wood_dark=WOOD_WALNUT_DARK)

    _draw_wrap_strap(surf, body, dx_from_centre=-10)
    _draw_wrap_strap(surf, body, dx_from_centre= 10)

    _draw_corner_studs(surf, body)
    _draw_lock_plate(surf, body)

    _shake_lines(surf, cx, body.y - DOME_H, w=BOX_W, color=(22, 12, 4))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 3 — BRASS-STRAPPED
# ════════════════════════════════════════════════════════════════════════════
# Same oak dome, but the wrap-straps + corner studs are BRASS instead
# of iron. Reads as the "decorated / valuable" sibling.

def draw_brass_strapped(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _draw_dome_and_body(surf, body,
                        wood_hi=WOOD_DOME_HI, wood_mid=WOOD_DOME_MID,
                        wood_dark=WOOD_DOME_DARK)

    _draw_wrap_strap(surf, body, dx_from_centre=-10,
                     dark=BRASS_DK, mid=BRASS_BASE, hi=BRASS_HI)
    _draw_wrap_strap(surf, body, dx_from_centre= 10,
                     dark=BRASS_DK, mid=BRASS_BASE, hi=BRASS_HI)

    _draw_corner_studs(surf, body)
    _draw_lock_plate(surf, body)

    _shake_lines(surf, cx, body.y - DOME_H, w=BOX_W, color=(45, 28, 12))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 4 — TRIPLE-STRAPPED
# ════════════════════════════════════════════════════════════════════════════
# Same oak dome, but with THREE iron wrap-straps (centre + two side
# straps) instead of two. The "heavily reinforced" sibling. The centre
# strap takes the place of the lock plate.

def draw_triple_strapped(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _draw_dome_and_body(surf, body,
                        wood_hi=WOOD_DOME_HI, wood_mid=WOOD_DOME_MID,
                        wood_dark=WOOD_DOME_DARK)

    # Three iron straps: one centre + two flanking. Slightly thicker.
    _draw_wrap_strap(surf, body, dx_from_centre=-13, strap_w=4)
    _draw_wrap_strap(surf, body, dx_from_centre=  0, strap_w=5)
    _draw_wrap_strap(surf, body, dx_from_centre= 13, strap_w=4)

    _draw_corner_studs(surf, body)

    # Lock plate is mounted ON the centre strap — small brass medallion
    # with a keyhole.
    kh_cx, kh_cy = body.centerx, body.centery
    pygame.draw.circle(surf, BRASS_DK,   (kh_cx, kh_cy), 4)
    pygame.draw.circle(surf, BRASS_BASE, (kh_cx, kh_cy), 3)
    pygame.draw.line(surf, BRASS_HI,
                     (kh_cx - 2, kh_cy - 2), (kh_cx + 1, kh_cy - 2), 1)
    pygame.draw.circle(surf, NEAR_BLACK, (kh_cx, kh_cy - 1), 1)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(kh_cx - 1, kh_cy, 2, 3))

    _shake_lines(surf, cx, body.y - DOME_H, w=BOX_W, color=(45, 28, 12))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 5 — CHAINED
# ════════════════════════════════════════════════════════════════════════════
# Same oak dome + two iron straps + brass plate, plus an iron CHAIN
# wrapped horizontally around the body below the dome. The
# "double-secured" sibling.

def draw_chained(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _draw_dome_and_body(surf, body,
                        wood_hi=WOOD_DOME_HI, wood_mid=WOOD_DOME_MID,
                        wood_dark=WOOD_DOME_DARK)

    _draw_wrap_strap(surf, body, dx_from_centre=-10)
    _draw_wrap_strap(surf, body, dx_from_centre= 10)

    _draw_corner_studs(surf, body)

    # Horizontal chain wrap — overlapping oval iron links across the
    # lower half of the body.
    chain_y = body.y + body.h * 2 // 3
    link_w = 5
    for lx in range(body.x - 2, body.right + 2, link_w - 1):
        link_rect = pygame.Rect(lx, chain_y - 2, link_w, 5)
        pygame.draw.ellipse(surf, NEAR_BLACK, link_rect)
        pygame.draw.ellipse(surf, IRON_BASE, link_rect.inflate(-2, -2))
        pygame.draw.line(surf, IRON_HI,
                         (link_rect.x + 1, link_rect.y + 1),
                         (link_rect.right - 2, link_rect.y + 1), 1)

    # Padlock holding the chain on the centre-front (covers the lock plate)
    pad = pygame.Rect(body.centerx - 5, body.centery - 4, 10, 9)
    pygame.draw.arc(surf, IRON_DARK,
                    pygame.Rect(pad.centerx - 4, pad.y - 5, 8, 10),
                    math.radians(0), math.radians(180), 3)
    pygame.draw.rect(surf, DK_OUTLINE, pad.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, pad, IRON_HI, IRON_DARK, radius=2)
    pygame.draw.circle(surf, NEAR_BLACK, (pad.centerx, pad.centery), 2)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(pad.centerx - 1, pad.centery, 2, 3))

    _shake_lines(surf, cx, body.y - DOME_H, w=BOX_W, color=(45, 28, 12))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ── Registry ────────────────────────────────────────────────────────────────

VARIANTS = [
    ("classic_oak",      "CLASSIC OAK DOMED",     draw_classic_oak),
    ("dark_walnut",      "DARK WALNUT DOMED",     draw_dark_walnut),
    ("brass_strapped",   "BRASS-STRAPPED DOMED",  draw_brass_strapped),
    ("triple_strapped",  "TRIPLE-STRAPPED DOMED", draw_triple_strapped),
    ("chained",          "CHAINED DOMED",         draw_chained),
]
