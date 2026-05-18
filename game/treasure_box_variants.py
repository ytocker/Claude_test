"""Treasure box power-up — round 6: flat-top variant of round 5's #1.

User picked round 5's CLASSIC OAK DOMED but asked for a flat lid
instead of the curved dome. Same warm-oak palette, same iron wrap-
straps, same brass keyhole plate, same carry ropes — only the lid
geometry changes: a substantial flat slab on top of the body, with
the iron straps now wrapping from the body's bottom up the front of
the body AND the front of the lid, capped where they bend over the
top edge.

`draw_classic_oak_flat(surf, bird_cx, bird_cy, t=0.0)` paints the
carry ropes, the chest, motion lines, and the 4-coin spill cascade.
The bird itself is positioned by the caller.

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

# Warm oak — same palette as round 5's classic_oak_domed.
WOOD_HI   = (165, 115,  62)
WOOD_MID  = (120,  78,  38)
WOOD_DARK = ( 68,  38,  14)


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
LID_H  = 11        # substantial slab — NOT a briefcase-thin strip


def _box_rect(cx, cy):
    return pygame.Rect(cx - BOX_W // 2, cy - BODY_H // 2, BOX_W, BODY_H)


# ── helpers ─────────────────────────────────────────────────────────────────

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


def _draw_carry_ropes(surf, bird_cx, bird_cy, body_rect, lid_y):
    """Two short hemp ropes from Pip's talons to the top-front corners
    of the LID (above body.y, since the lid is a substantial slab)."""
    for tx, talon_dx in ((body_rect.x + 4, -3), (body_rect.right - 5, 3)):
        sx, sy = bird_cx + talon_dx, bird_cy + 22
        ex, ey = tx, lid_y - 1
        pygame.draw.line(surf, ROPE_DARK, (sx, sy), (ex, ey), 4)
        pygame.draw.line(surf, ROPE_BASE, (sx, sy), (ex, ey), 2)
        rx, ry = (sx + ex) // 2, (sy + ey) // 2
        pygame.draw.line(surf, ROPE_DARK, (rx - 2, ry - 1), (rx + 2, ry + 1), 1)


def _draw_chest(surf, body):
    """Flat-top pirate chest: thick rectangular lid slab on top of the
    rectangular body, with the iron strapping passing across both."""
    lid = pygame.Rect(body.x - 1, body.y - LID_H, body.w + 2, LID_H)

    # ── Lid slab ──
    pygame.draw.rect(surf, DK_OUTLINE, lid.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, lid, WOOD_HI, WOOD_MID, radius=2)
    # Top-edge sheen
    pygame.draw.line(surf, lerp_color(WOOD_HI, WHITE, 0.4),
                     (lid.x + 3, lid.y + 1), (lid.right - 4, lid.y + 1), 1)
    # Horizontal grain lines on the lid face
    for gy in (lid.y + 4, lid.y + 7):
        pygame.draw.line(surf, WOOD_DARK,
                         (lid.x + 3, gy), (lid.right - 4, gy), 1)

    # ── Dark seam where lid meets body ──
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(body.x, body.y - 1, body.w, 2))

    # ── Body ──
    pygame.draw.rect(surf, DK_OUTLINE, body.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, body, WOOD_MID, WOOD_DARK, radius=2)
    # Vertical grain on the body
    for i in range(1, 4):
        gx = body.x + (body.w * i) // 4
        pygame.draw.line(surf, WOOD_DARK,
                         (gx, body.y + 2), (gx, body.bottom - 3), 1)

    return lid


def _draw_wrap_strap(surf, body, lid, dx_from_centre, *,
                     strap_w=4,
                     dark=IRON_DARK, mid=IRON_BASE, hi=IRON_HI):
    """Iron strap wrapping from the body's bottom UP the front of the
    body AND the front of the lid, then bending over the top edge to
    the back. We see one continuous vertical band on the front + a
    tiny dark cap where it crests the lid."""
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
    # Rivet heads at top of body strap + bottom of strap
    for ry in (body.y + 3, body.bottom - 3):
        pygame.draw.circle(surf, dark, (strap_cx, ry), 2)
        pygame.draw.circle(surf, hi,   (strap_cx, ry), 1)


def _draw_corner_studs(surf, rect):
    """Brass studs at the corners of a given rect (used for both the
    body and the lid)."""
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
# CLASSIC OAK — FLAT TOP
# ════════════════════════════════════════════════════════════════════════════

def draw_classic_oak_flat(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    lid_y = body.y - LID_H
    _draw_carry_ropes(surf, bird_cx, bird_cy, body, lid_y)

    lid = _draw_chest(surf, body)

    # Two iron wrap-straps, evenly placed
    _draw_wrap_strap(surf, body, lid, dx_from_centre=-10)
    _draw_wrap_strap(surf, body, lid, dx_from_centre= 10)

    # Brass studs on both the body corners AND the lid corners — the
    # extra row on the lid sells "substantial slab" vs. "briefcase strip"
    _draw_corner_studs(surf, body)
    _draw_corner_studs(surf, lid)

    _draw_lock_plate(surf, body)

    _shake_lines(surf, cx, body.y - LID_H // 2, w=BOX_W, color=(45, 28, 12))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ── Registry ────────────────────────────────────────────────────────────────

VARIANTS = [
    ("classic_oak_flat", "CLASSIC OAK — FLAT TOP", draw_classic_oak_flat),
]
