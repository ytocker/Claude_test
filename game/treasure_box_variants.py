"""Five visual treatments for the TREASURE BOX power-up — round 4.

Round 4 brief: the user picked round 3's PADLOCKED OAK as the keeper.
This round generates 5 sibling chests in that same family — small,
closed, locked wooden boxes carried tight under Pip — and varies a
single thing each: lock count, band material, wood tone, rivet
density, or an added chain wrap.

No drop shadow (user explicitly asked to drop the shade).

Each `draw_<name>(surf, bird_cx, bird_cy, t=0.0)` paints the carry
ropes, the chest, the variant-specific hardware accent, motion lines,
and the 4-coin spill cascade. The bird itself is positioned by the
caller before invoking the overlay so every variant uses the exact
same Pip sprite.

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

BOX_W  = 42
BODY_H = 22
LID_H  = 12


def _box_rect(cx, cy):
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
    handle_y = body_rect.y + BODY_H // 2
    for tx, talon_dx in ((body_rect.x - 1, -3), (body_rect.right + 1, 3)):
        pygame.draw.line(surf, ROPE_DARK,
                         (bird_cx + talon_dx, bird_cy + 22),
                         (tx, handle_y), 4)
        pygame.draw.line(surf, ROPE_BASE,
                         (bird_cx + talon_dx, bird_cy + 22),
                         (tx, handle_y), 2)
        rx = int((bird_cx + talon_dx + tx) / 2)
        ry = int(((bird_cy + 22) + handle_y) / 2)
        pygame.draw.line(surf, ROPE_DARK, (rx - 2, ry - 1), (rx + 2, ry + 1), 1)


def _draw_side_handles(surf, body, wood_dark, *, brass_base=BRASS_BASE,
                      brass_dark=BRASS_DK):
    for hx in (body.x - 1, body.right):
        pygame.draw.circle(surf, NEAR_BLACK, (hx, body.centery), 4, 0)
        pygame.draw.circle(surf, brass_dark, (hx, body.centery), 3, 0)
        pygame.draw.circle(surf, brass_base, (hx, body.centery), 3, 1)
        pygame.draw.circle(surf, wood_dark,  (hx, body.centery), 1, 0)


def _draw_corner_studs(surf, body, *, color=BRASS_BASE,
                       dark=BRASS_DK, hi=BRASS_HI, size=2):
    for cnx, cny in (
        (body.x + 2,     body.y + 2),
        (body.right - 3, body.y + 2),
        (body.x + 2,     body.bottom - 3),
        (body.right - 3, body.bottom - 3),
    ):
        pygame.draw.circle(surf, dark,  (cnx, cny), size, 0)
        pygame.draw.circle(surf, color, (cnx, cny), size - 1, 0)
        pygame.draw.circle(surf, hi,    (cnx - 1, cny - 1), 1, 0)


def _wood_grain(surf, body, dark, *, n=3):
    step = body.w // (n + 1)
    for i in range(1, n + 1):
        gx = body.x + step * i
        pygame.draw.line(surf, dark,
                         (gx, body.y + 3),
                         (gx, body.bottom - 3), 1)


def _draw_lid_and_body(surf, body, wood_hi, wood_mid, wood_dark, *,
                       grain_n=3):
    """Common: flat lid + dark seam + body w/ vertical grain. Returns
    the lid rect for callers that want to draw locks/hasps on the lid."""
    lid = pygame.Rect(body.x - 2, body.y - LID_H, body.w + 4, LID_H)
    pygame.draw.rect(surf, DK_OUTLINE, lid.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, lid, wood_hi, wood_mid, radius=2)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(body.x, body.y - 1, body.w, 2))

    pygame.draw.rect(surf, DK_OUTLINE, body.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, body, wood_mid, wood_dark, radius=2)
    _wood_grain(surf, body, wood_dark, n=grain_n)
    return lid


def _draw_strap(surf, body, by, *,
                strap_dark=IRON_DARK, strap_mid=IRON_BASE,
                strap_hi=IRON_HI, thickness=4, rivets=2):
    """One horizontal metal strap across the body at `by` (top edge of
    the strap). `rivets` = how many rivet heads to stamp evenly across."""
    strap = pygame.Rect(body.x - 1, by, body.w + 2, thickness)
    pygame.draw.rect(surf, strap_dark, strap)
    pygame.draw.rect(surf, strap_mid,  strap.inflate(0, -2))
    pygame.draw.line(surf, strap_hi,
                     (strap.x + 2, strap.y + 1),
                     (strap.right - 2, strap.y + 1), 1)
    # Rivet heads at evenly spaced positions
    if rivets >= 2:
        for i in range(rivets):
            t = i / (rivets - 1) if rivets > 1 else 0.5
            rx = int(body.x + 2 + (body.w - 4) * t)
            pygame.draw.circle(surf, strap_dark, (rx, by + thickness // 2), 2)
            pygame.draw.circle(surf, strap_hi,   (rx, by + thickness // 2), 1)


def _draw_padlock(surf, cx, cy, *, size="big", shackle_color=IRON_DARK,
                  shackle_hi=IRON_HI, body_top=IRON_HI, body_bot=IRON_DARK):
    """Padlock at (cx, cy). `size` ∈ {"small", "big"}. The lock body is
    drawn centred on (cx, cy); the U-shackle bends up out of the top."""
    if size == "small":
        w, h = 8, 8
        shackle_w, shackle_h = 6, 8
    else:
        w, h = 12, 11
        shackle_w, shackle_h = 10, 12

    pad = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    # Shackle arc behind the lock body
    pygame.draw.arc(surf, shackle_color,
                    pygame.Rect(cx - shackle_w // 2,
                                pad.y - shackle_h // 2 - 1,
                                shackle_w, shackle_h),
                    math.radians(0), math.radians(180), 3)
    pygame.draw.arc(surf, shackle_hi,
                    pygame.Rect(cx - shackle_w // 2,
                                pad.y - shackle_h // 2 - 1,
                                shackle_w, shackle_h),
                    math.radians(20), math.radians(160), 1)
    # Lock body
    pygame.draw.rect(surf, DK_OUTLINE, pad.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, pad, body_top, body_bot, radius=2)
    # Keyhole
    pygame.draw.circle(surf, NEAR_BLACK, (pad.centerx, pad.centery), 2)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(pad.centerx - 1, pad.centery, 2, 3))


def _draw_hasp(surf, lid, body, *,
               width=10, dark=IRON_DARK, mid=IRON_BASE, hi=IRON_HI):
    """Vertical hasp plate from the lid down past the seam onto the
    body. The padlock's shackle would loop through the protruding lug
    at the bottom."""
    hasp = pygame.Rect(lid.centerx - width // 2, lid.y + 3, width, LID_H - 2)
    pygame.draw.rect(surf, dark, hasp)
    pygame.draw.rect(surf, mid,  hasp.inflate(-2, -2))
    pygame.draw.line(surf, hi,
                     (hasp.x + 1, hasp.y + 1),
                     (hasp.right - 2, hasp.y + 1), 1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 1 — TWIN PADLOCKED
# ════════════════════════════════════════════════════════════════════════════
# Round 3's padlocked-oak chest, but with TWO smaller padlocks
# side-by-side on the lid instead of one big central one. Doubles the
# "extra-secure" read without changing the silhouette.

def draw_twin_padlocked(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)

    lid = _draw_lid_and_body(surf, body, WOOD_OAK_HI, WOOD_OAK_MID, WOOD_OAK_DARK)

    # Two iron straps with 2 rivets each
    _draw_strap(surf, body, body.y + 4, rivets=2)
    _draw_strap(surf, body, body.bottom - 7, rivets=2)

    _draw_corner_studs(surf, body)
    _draw_side_handles(surf, body, WOOD_OAK_DARK)

    # TWO smaller hasps + padlocks, one to each side of centre.
    for dx in (-10, 10):
        # Hasp
        hasp = pygame.Rect(lid.centerx + dx - 3, lid.y + 4, 6, LID_H - 3)
        pygame.draw.rect(surf, IRON_DARK, hasp)
        pygame.draw.rect(surf, IRON_BASE, hasp.inflate(-2, -2))
        # Padlock (small)
        _draw_padlock(surf, body.centerx + dx, body.y + 6, size="small")

    _shake_lines(surf, cx, body.y - 4, w=BOX_W, color=(45, 28, 12))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 2 — BRASS-BANDED
# ════════════════════════════════════════════════════════════════════════════
# Same oak chest + single padlock, but the strapping is BRASS instead
# of iron. Reads as a "decorated / valuable" version of the same chest.

def draw_brass_banded(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)

    lid = _draw_lid_and_body(surf, body, WOOD_OAK_HI, WOOD_OAK_MID, WOOD_OAK_DARK)

    # Two BRASS bands (replacing iron) — same geometry, gold palette.
    for by in (body.y + 4, body.bottom - 7):
        _draw_strap(surf, body, by,
                    strap_dark=BRASS_DK, strap_mid=BRASS_BASE,
                    strap_hi=BRASS_HI, rivets=3)

    _draw_corner_studs(surf, body)
    _draw_side_handles(surf, body, WOOD_OAK_DARK)

    # Single brass padlock (centre) + brass hasp
    _draw_hasp(surf, lid, body, width=10,
               dark=BRASS_DK, mid=BRASS_BASE, hi=BRASS_HI)
    _draw_padlock(surf, body.centerx, body.y + 6, size="big",
                  shackle_color=BRASS_DK, shackle_hi=BRASS_HI,
                  body_top=BRASS_HI, body_bot=BRASS_DK)

    _shake_lines(surf, cx, body.y - 4, w=BOX_W, color=(45, 28, 12))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 3 — DARK WALNUT
# ════════════════════════════════════════════════════════════════════════════
# Same form factor, same single-padlock layout, but in dark walnut wood
# instead of warm oak. Iron hardware stays. The "richer / older" feel.

def draw_dark_walnut(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)

    lid = _draw_lid_and_body(surf, body,
                             WOOD_WALNUT_HI, WOOD_WALNUT_MID, WOOD_WALNUT_DARK)

    _draw_strap(surf, body, body.y + 4, rivets=2)
    _draw_strap(surf, body, body.bottom - 7, rivets=2)

    _draw_corner_studs(surf, body)
    _draw_side_handles(surf, body, WOOD_WALNUT_DARK)

    _draw_hasp(surf, lid, body)
    _draw_padlock(surf, body.centerx, body.y + 6, size="big")

    _shake_lines(surf, cx, body.y - 4, w=BOX_W, color=(22, 12, 4))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 4 — HEAVY-RIVETED
# ════════════════════════════════════════════════════════════════════════════
# Same warm oak + single padlock, but the iron strapping is THICKER and
# studded with many more rivets along its length — the "fortified
# / extra-secure" read.

def draw_heavy_riveted(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)

    lid = _draw_lid_and_body(surf, body, WOOD_OAK_HI, WOOD_OAK_MID, WOOD_OAK_DARK)

    # Three thicker straps with 5 rivets each (1 top, 1 mid below the
    # lock area, 1 bottom)
    _draw_strap(surf, body, body.y + 3,         thickness=5, rivets=5)
    _draw_strap(surf, body, body.bottom - 8,    thickness=5, rivets=5)

    # Bigger corner studs
    _draw_corner_studs(surf, body, size=3)
    _draw_side_handles(surf, body, WOOD_OAK_DARK)

    # Padlock + hasp (slightly chunkier hasp)
    _draw_hasp(surf, lid, body, width=12)
    _draw_padlock(surf, body.centerx, body.y + 7, size="big")

    # Extra rivets along the centre line of the body (around the lock)
    for sx in (body.x + 4, body.right - 5):
        pygame.draw.circle(surf, IRON_DARK, (sx, body.centery), 2)
        pygame.draw.circle(surf, IRON_HI,   (sx, body.centery), 1)

    _shake_lines(surf, cx, body.y - 4, w=BOX_W, color=(45, 28, 12))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 5 — CHAINED
# ════════════════════════════════════════════════════════════════════════════
# Same warm oak chest, but with an iron CHAIN wrapped horizontally
# around the body in addition to the padlock — the "double-secured /
# nobody-opens-this" read.

def draw_chained(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)

    lid = _draw_lid_and_body(surf, body, WOOD_OAK_HI, WOOD_OAK_MID, WOOD_OAK_DARK)

    # Single iron strap near the bottom only (the chain replaces the
    # other one across the upper-middle)
    _draw_strap(surf, body, body.bottom - 7, rivets=2)

    _draw_corner_studs(surf, body)
    _draw_side_handles(surf, body, WOOD_OAK_DARK)

    # Horizontal chain wrap — overlapping oval links across the body
    chain_y = body.y + body.h // 2 - 1
    link_w = 6
    for lx in range(body.x - 2, body.right + 2, link_w - 1):
        link_rect = pygame.Rect(lx, chain_y - 3, link_w, 6)
        pygame.draw.ellipse(surf, NEAR_BLACK, link_rect)
        pygame.draw.ellipse(surf, IRON_BASE, link_rect.inflate(-2, -2))
        pygame.draw.line(surf, IRON_HI,
                         (link_rect.x + 2, link_rect.y + 1),
                         (link_rect.right - 2, link_rect.y + 1), 1)

    # Hasp + padlock anchoring the chain at the centre-front
    _draw_hasp(surf, lid, body, width=10)
    _draw_padlock(surf, body.centerx, body.y + 6, size="big")

    _shake_lines(surf, cx, body.y - 4, w=BOX_W, color=(45, 28, 12))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ── Registry ────────────────────────────────────────────────────────────────

VARIANTS = [
    ("twin_padlocked", "TWIN PADLOCKED",  draw_twin_padlocked),
    ("brass_banded",   "BRASS-BANDED",    draw_brass_banded),
    ("dark_walnut",    "DARK WALNUT",     draw_dark_walnut),
    ("heavy_riveted",  "HEAVY-RIVETED",   draw_heavy_riveted),
    ("chained",        "CHAINED",         draw_chained),
]
