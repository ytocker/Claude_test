"""Five visual treatments for the TREASURE BOX power-up — round 2.

Round 2 brief: every variant is a *classic pirate treasure chest* (the
iconic curved-lid wooden chest with iron straps and a fat lock), open
mid-flight with gold heaped up inside. Differences live in the surface
treatment + the contents of the haul + a single thematic accent. Pip
carries every chest the same way (two hemp ropes from talons to brass
side-handles) so the A/B compares chest design only.

Each `draw_<name>(surf, bird_cx, bird_cy, t=0.0)` paints the carry
ropes, the chest silhouette + variant skin, the treasure mound, and a
4-coin spill cascade trailing behind Pip (he flies left-to-right, so
coins drift left as they fall). The bird itself is positioned by the
caller before invoking the overlay so all variants share the same Pip
sprite.

Preview-only — nothing in game/ imports this yet."""
import math
import pathlib
import pygame

from game.draw import (
    UI_GOLD, UI_CREAM, UI_ORANGE, UI_RED, NEAR_BLACK, WHITE,
    COIN_LIGHT, COIN_DARK, lerp_color,
)


# ── shared palette ──────────────────────────────────────────────────────────

DK_OUTLINE = (20, 12, 8)
GOLD_HI    = (255, 235, 150)
BRASS_BASE = (210, 165,  60)
BRASS_HI   = (255, 230, 140)
BRASS_DK   = (130,  90,  20)
IRON_BASE  = ( 75,  72,  78)
IRON_DARK  = ( 36,  34,  40)
IRON_HI    = (140, 138, 145)
ROPE_BASE  = (170, 120,  62)
ROPE_DARK  = ( 60,  35,  15)


# ── font cache ──────────────────────────────────────────────────────────────

_font_cache: dict = {}
_FONT_PATH = pathlib.Path(__file__).parent / "assets" / "LiberationSans-Bold.ttf"


def _font(size):
    f = _font_cache.get(size)
    if f is None:
        f = pygame.font.Font(str(_FONT_PATH), size)
        _font_cache[size] = f
    return f


# ── shared coin sprite for the spill trail ──────────────────────────────────

def _draw_coin(surf, cx, cy, r=8, squeeze=1.0, glint=True):
    """Tiny gold doubloon with the in-game COIN_DARK rope rim and
    COIN_LIGHT gradient fill. Used both inside the chest's heap and
    along the falling spill trail."""
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
        if glint and inner.w >= 6:
            f = _font(max(8, int(h * 0.7)))
            g = f.render("$", True, COIN_DARK)
            disc.blit(g, g.get_rect(center=(disc.get_width() // 2,
                                            disc.get_height() // 2)))
            pygame.draw.arc(disc, GOLD_HI,
                            pygame.Rect(2, 2, inner.w, inner.h - 2),
                            math.radians(40), math.radians(140), 1)
    surf.blit(disc, (cx - disc.get_width() // 2, cy - disc.get_height() // 2))


def _spill_trail(surf, anchor_x, anchor_y, *, side=-1, sparkle=GOLD_HI):
    """A burst star + 4 coins in successive stages of the fall + 3
    sparkle puffs. The anchor is the spill mouth (where the coin pops
    out); the rest cascades down and BACKWARD (left), since Pip flies
    left-to-right. Same shape for every variant so the spill reads
    identically across the A/B set."""
    burst = pygame.Surface((26, 26), pygame.SRCALPHA)
    pygame.draw.line(burst, (*GOLD_HI, 230), (13,  1), (13, 25), 3)
    pygame.draw.line(burst, (*GOLD_HI, 230), ( 1, 13), (25, 13), 3)
    pygame.draw.line(burst, (255, 255, 255, 230), (13,  4), (13, 22), 1)
    pygame.draw.line(burst, (255, 255, 255, 230), ( 4, 13), (22, 13), 1)
    surf.blit(burst, (anchor_x - 13, anchor_y - 13))

    stages = (
        (  3 * side, -14, 8, 0.45),
        (  8 * side,   8, 9, 1.00),
        ( 22 * side,  28, 8, 0.70),
        ( 40 * side,  52, 7, 0.90),
    )
    for dx, dy, r, sq in stages:
        _draw_coin(surf, anchor_x + dx, anchor_y + dy, r=r, squeeze=sq)

    for dx, dy, sr in ((14 * side, 18, 2), (30 * side, 40, 2),
                       (6 * side, -22, 2)):
        s = pygame.Surface((sr * 4, sr * 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*sparkle, 220), (sr * 2, sr * 2), sr)
        pygame.draw.circle(s, (255, 255, 255, 200), (sr * 2, sr * 2),
                           max(1, sr - 1))
        surf.blit(s, (anchor_x + dx - sr * 2, anchor_y + dy - sr * 2))


def _shake_lines(surf, cx, cy, w=24, *, color=(40, 30, 20)):
    """Cartoon motion lines flanking the chest so the still mockup reads
    as 'being shaken' — two short hashes on each side."""
    for sx in (cx - w // 2 - 8, cx + w // 2 + 8):
        for dy in (-5, 5):
            ex = sx + (5 if sx > cx else -5)
            pygame.draw.line(surf, color, (sx, cy + dy), (ex, cy + dy), 2)


# ── shared chest geometry ───────────────────────────────────────────────────
# Designed for a ~60-px-wide footprint that reads at game scale (1×) and
# still shows lock + bands + handles at the 3× preview render.

CHEST_W = 60
BODY_H  = 32      # vertical run of the rectangular body
LID_H   = 22      # height of the open lid arc visible above the body


def _chest_body_rect(cx, cy):
    """Body rect of the closed-shape chest. cy is the body's vertical
    centre — the open lid extends LID_H px further up from the body's
    top edge."""
    return pygame.Rect(cx - CHEST_W // 2, cy - BODY_H // 2, CHEST_W, BODY_H)


def _draw_carry_ropes(surf, bird_cx, bird_cy, body_rect):
    """Two thick hemp ropes from Pip's talons to brass D-ring handles on
    each side of the chest body. Drawn BEFORE the chest so the rope
    passes behind the chest's silhouette."""
    handle_y = body_rect.y + BODY_H // 2
    for tx, talon_dx in ((body_rect.x - 1, -4), (body_rect.right + 1, 4)):
        pygame.draw.line(surf, ROPE_DARK,
                         (bird_cx + talon_dx, bird_cy + 22),
                         (tx, handle_y), 5)
        pygame.draw.line(surf, ROPE_BASE,
                         (bird_cx + talon_dx, bird_cy + 22),
                         (tx, handle_y), 3)
        # Rope hatching for fiber texture
        for i in range(1, 4):
            ti = i / 4.0
            rx = int((bird_cx + talon_dx) + (tx - (bird_cx + talon_dx)) * ti)
            ry = int((bird_cy + 22) + (handle_y - (bird_cy + 22)) * ti)
            pygame.draw.line(surf, ROPE_DARK, (rx - 2, ry - 1), (rx + 2, ry + 1), 1)


def _draw_chest(surf, cx, cy, *,
                wood_hi, wood_mid, wood_dark,
                band_dark, band_mid, band_hi,
                interior=(22, 14, 6),
                lid_inside=(28, 18, 8),
                lid_mark=None):
    """Paint the canonical pirate chest at (cx, cy) using the given
    wood + iron palette. The chest is in the 'open' pose: lid hinged
    back, treasure visible at the top edge of the body. Returns
    (body_rect, top_interior_y, lid_back_rect) so callers can layer
    treasure + extras correctly."""
    body = _chest_body_rect(cx, cy)

    _drop_shadow(surf, cx, body.bottom + 6, CHEST_W + 6)

    # ── Lid (open, hinged back) ──
    # The closed lid would be a half-ellipse above the body. When OPEN
    # it pivots back ~110°, so we draw it as a small upright curved
    # shape standing BEHIND the body's top edge. The lid's underside
    # (lid_inside colour) is what the viewer sees.
    lid_back = pygame.Rect(body.x + 3, body.y - LID_H - 4, CHEST_W - 6, LID_H + 6)
    # Lid silhouette: an inverted half-ellipse
    pygame.draw.ellipse(surf, DK_OUTLINE,
                        lid_back.inflate(4, 4))
    # The underside of the lid is what we see when the lid is open
    lid_inner = lid_back.inflate(-4, -4)
    _gradient_rect_arc(surf, lid_inner, lid_inside,
                       lerp_color(lid_inside, NEAR_BLACK, 0.6))
    # Iron strap across the lid arc (centred)
    strap = pygame.Rect(lid_inner.x, lid_inner.centery - 3, lid_inner.w, 6)
    pygame.draw.rect(surf, band_dark, strap)
    pygame.draw.rect(surf, band_mid,  strap.inflate(0, -2))
    pygame.draw.line(surf, band_hi,
                     (strap.x + 2, strap.y + 1),
                     (strap.right - 2, strap.y + 1), 1)
    # Optional decoration on the lid front (e.g. an X for the map variant,
    # or a skull for the captain variant) — applied by caller via lid_mark.
    if lid_mark is not None:
        lid_mark(surf, lid_inner)

    # ── Body (rectangular wooden box, front-facing) ──
    pygame.draw.rect(surf, DK_OUTLINE, body.inflate(4, 4), border_radius=4)
    _gradient_rect(surf, body, wood_hi, wood_dark, radius=3)
    # Vertical wood grain (4 darker streaks)
    for gx in (body.x + 8, body.x + 22, body.x + 38, body.right - 9):
        pygame.draw.line(surf, wood_dark, (gx, body.y + 4),
                         (gx, body.bottom - 4), 1)

    # ── 3 iron strap bands across the body ──
    for by in (body.y + 4, body.centery - 2, body.bottom - 7):
        band = pygame.Rect(body.x - 1, by, body.w + 2, 6)
        pygame.draw.rect(surf, band_dark, band)
        pygame.draw.rect(surf, band_mid,  band.inflate(0, -2))
        pygame.draw.line(surf, band_hi,
                         (band.x + 2, band.y + 1),
                         (band.right - 2, band.y + 1), 1)
        # Rivet heads at the ends of each band
        for rx in (body.x + 3, body.right - 4):
            pygame.draw.circle(surf, band_dark, (rx, by + 3), 2)
            pygame.draw.circle(surf, band_hi,   (rx, by + 3), 1)

    # ── Brass corner caps ──
    for cnx, cny, anchor in (
        (body.x + 2,        body.y + 2,        "tl"),
        (body.right - 8,    body.y + 2,        "tr"),
        (body.x + 2,        body.bottom - 8,   "bl"),
        (body.right - 8,    body.bottom - 8,   "br"),
    ):
        cap = pygame.Rect(cnx, cny, 7, 7)
        pygame.draw.rect(surf, BRASS_DK, cap.inflate(2, 2), border_radius=2)
        pygame.draw.rect(surf, BRASS_BASE, cap, border_radius=2)
        pygame.draw.line(surf, BRASS_HI, (cap.x + 1, cap.y + 1),
                         (cap.right - 2, cap.y + 1), 1)

    # ── Central lock plate (over the middle band) ──
    lock = pygame.Rect(body.centerx - 8, body.centery - 8, 16, 16)
    pygame.draw.rect(surf, IRON_DARK, lock.inflate(2, 2), border_radius=3)
    pygame.draw.rect(surf, IRON_BASE, lock, border_radius=2)
    pygame.draw.line(surf, IRON_HI,
                     (lock.x + 2, lock.y + 2),
                     (lock.right - 2, lock.y + 2), 1)
    # Keyhole — circle + slot
    pygame.draw.circle(surf, NEAR_BLACK, (lock.centerx, lock.centery - 1), 3)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(lock.centerx - 1, lock.centery, 2, 4))

    # ── Brass D-ring handles on the sides ──
    for hx in (body.x - 1, body.right):
        pygame.draw.circle(surf, NEAR_BLACK, (hx, body.centery), 5, 0)
        pygame.draw.circle(surf, BRASS_DK,   (hx, body.centery), 4, 0)
        pygame.draw.circle(surf, BRASS_BASE, (hx, body.centery), 4, 1)
        # hollow centre
        pygame.draw.circle(surf, wood_dark,  (hx, body.centery), 2, 0)

    # The interior strip (the dark slice between body top and lid back)
    # — this is the gold-spilling mouth of the chest.
    interior_strip = pygame.Rect(body.x + 4, body.y - 2, body.w - 8, 6)
    pygame.draw.rect(surf, interior, interior_strip)

    return body, body.y - 2, lid_back


def _gradient_rect(surf, rect, top_col, bot_col, *, radius=4):
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


def _gradient_rect_arc(surf, rect, top_col, bot_col):
    """Half-ellipse with top→bottom gradient. Used for the lid arc."""
    layer = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        c = lerp_color(top_col, bot_col, t) + (255,)
        layer.fill(c, pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(layer, rect.topleft)


def _drop_shadow(surf, cx, cy, w):
    sh = pygame.Surface((w + 10, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 12, 130), sh.get_rect())
    surf.blit(sh, (cx - (w + 10) // 2, cy))


# ── treasure helpers (the heap rising out of the open chest) ────────────────

def _heap_gold(surf, body_rect, *, n_coins=9, accent=GOLD_HI):
    """A heaped mound of gold coins rising out of the body's top edge.
    Coins are stacked from a wide base at body.y to a single peak ~14 px
    above. The mound width hugs the body's interior so it reads as
    'overflowing the chest.'"""
    base_y = body_rect.y + 1
    layers = (
        # (y_offset, n, radii, jitter)
        (  0, 6, (8, 7, 8, 7, 8, 7)),
        ( -8, 5, (7, 7, 8, 7, 7)),
        (-14, 3, (7, 8, 7)),
        (-19, 1, (6,)),
    )
    interior_left  = body_rect.x + 6
    interior_right = body_rect.right - 6
    interior_w     = interior_right - interior_left
    for dy, n, radii in layers:
        for i in range(n):
            t = (i + 0.5) / n
            cx = int(interior_left + interior_w * t)
            cy = base_y + dy
            r  = radii[i]
            # Slight squeeze for the topmost row so the peak reads
            squeeze = 1.0 if dy > -12 else 0.85
            _draw_coin(surf, cx, cy, r=r, squeeze=squeeze)
    # Stray little glint specks on the peak
    for dx, dy in ((-4, -22), (6, -19), (12, -16)):
        s = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(s, (*accent, 220), (3, 3), 2)
        pygame.draw.circle(s, WHITE, (3, 3), 1)
        surf.blit(s, (body_rect.centerx + dx - 3, base_y + dy - 3))


def _draw_gem(surf, cx, cy, color, *, w=10, h=12):
    """Faceted gem: diamond polygon with dark outline + bright top facet."""
    top = (cx, cy - h // 2)
    L   = (cx - w // 2, cy - 2)
    R   = (cx + w // 2, cy - 2)
    bot = (cx, cy + h // 2)
    pygame.draw.polygon(surf, NEAR_BLACK, [
        (top[0], top[1] - 1), (L[0] - 1, L[1]),
        (bot[0], bot[1] + 1), (R[0] + 1, R[1]),
    ])
    pygame.draw.polygon(surf, color, [top, L, bot, R])
    # Bright top facet
    lighter = lerp_color(color, WHITE, 0.45)
    pygame.draw.polygon(surf, lighter, [
        top, (cx - 2, cy - h // 4), (cx, cy - 2), (cx + 2, cy - h // 4)
    ])
    # Tiny specular dot
    pygame.draw.circle(surf, WHITE, (cx - 1, cy - h // 3), 1)


def _draw_crown(surf, cx, cy):
    """Tiny royal crown perched on the heap peak."""
    base = pygame.Rect(cx - 8, cy - 2, 16, 5)
    pygame.draw.rect(surf, BRASS_DK, base.inflate(2, 2), border_radius=1)
    pygame.draw.rect(surf, BRASS_BASE, base)
    pygame.draw.line(surf, BRASS_HI, (base.x + 1, base.y + 1),
                     (base.right - 2, base.y + 1), 1)
    # 3 spikes
    for sx in (cx - 6, cx, cx + 6):
        pygame.draw.polygon(surf, BRASS_DK, [
            (sx - 2, cy - 2), (sx + 2, cy - 2), (sx, cy - 7)
        ])
        pygame.draw.polygon(surf, BRASS_BASE, [
            (sx - 1, cy - 2), (sx + 1, cy - 2), (sx, cy - 6)
        ])
    # 3 gem dots in the band
    for i, col in enumerate(((220, 60, 60), (60, 200, 90), (80, 150, 230))):
        pygame.draw.circle(surf, NEAR_BLACK, (cx - 6 + i * 6, cy + 1), 2)
        pygame.draw.circle(surf, col, (cx - 6 + i * 6, cy + 1), 1)


def _draw_pearl_strand(surf, x1, y1, x2, y2, n=8):
    """Pearl necklace draped from (x1,y1) to (x2,y2). Pearls sag in
    a slight catenary."""
    for i in range(n):
        t = i / (n - 1)
        # Catenary sag
        sag = math.sin(t * math.pi) * 4
        px = int(x1 + (x2 - x1) * t)
        py = int(y1 + (y2 - y1) * t + sag)
        pygame.draw.circle(surf, NEAR_BLACK, (px, py), 3)
        pygame.draw.circle(surf, (240, 230, 215), (px, py), 2)
        pygame.draw.circle(surf, WHITE, (px - 1, py - 1), 1)


def _draw_barnacle(surf, cx, cy, *, r=4):
    """Conical barnacle cluster — cream cone with a dark mouth opening."""
    pygame.draw.polygon(surf, (40, 30, 20), [
        (cx - r - 1, cy + 1), (cx + r + 1, cy + 1),
        (cx + 1, cy - r - 1), (cx - 1, cy - r - 1),
    ])
    pygame.draw.polygon(surf, (220, 200, 170), [
        (cx - r, cy), (cx + r, cy), (cx + 1, cy - r), (cx - 1, cy - r),
    ])
    pygame.draw.line(surf, (60, 40, 30), (cx - 1, cy - 1), (cx + 1, cy - 1), 1)


def _draw_skull(surf, cx, cy):
    """Tiny brass skull-and-crossbones for the captain's chest medallion."""
    # Skull (cream circle + 2 dark eye sockets)
    pygame.draw.circle(surf, NEAR_BLACK, (cx, cy - 1), 6)
    pygame.draw.circle(surf, (240, 230, 210), (cx, cy - 1), 5)
    pygame.draw.circle(surf, NEAR_BLACK, (cx - 2, cy - 1), 1)
    pygame.draw.circle(surf, NEAR_BLACK, (cx + 2, cy - 1), 1)
    # Jaw notch
    pygame.draw.line(surf, NEAR_BLACK, (cx - 1, cy + 3), (cx + 1, cy + 3), 1)
    # Crossbones (two diagonal beige sticks behind the skull)
    pygame.draw.line(surf, NEAR_BLACK, (cx - 7, cy + 5), (cx + 7, cy + 5), 4)
    pygame.draw.line(surf, (220, 200, 170),
                     (cx - 6, cy + 5), (cx + 6, cy + 5), 2)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 1 — CLASSIC GOLD HOARD
# ════════════════════════════════════════════════════════════════════════════
# The default pirate chest you'd picture: warm oak, iron strapping,
# brass corners + lock, and a fat heaping mound of gold doubloons
# overflowing the open lid. Nothing fancy — this is the baseline read.

CLASSIC_PALETTE = dict(
    wood_hi   = (180, 125,  68),
    wood_mid  = (140,  85,  42),
    wood_dark = ( 80,  46,  18),
    band_dark = ( 35,  30,  35),
    band_mid  = ( 78,  72,  80),
    band_hi   = (160, 158, 168),
)


def draw_classic_chest(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 96
    body = _chest_body_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _draw_chest(surf, cx, cy, **CLASSIC_PALETTE)
    _heap_gold(surf, body)

    _shake_lines(surf, cx, body.y - LID_H, w=CHEST_W, color=(40, 25, 12))
    _spill_trail(surf, body.x - 4, body.y - 2, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 2 — JEWELED ROYAL HAUL
# ════════════════════════════════════════════════════════════════════════════
# Same chest, but the heap contains coloured gemstones (ruby, emerald,
# sapphire) mixed with the gold, a small gold crown perched on the peak,
# and a pearl necklace draping over the front lip. The "legendary haul"
# read.

JEWELED_PALETTE = dict(
    wood_hi   = (175, 120,  68),
    wood_mid  = (130,  78,  38),
    wood_dark = ( 72,  40,  14),
    band_dark = ( 50,  35,  10),
    band_mid  = (210, 165,  60),  # brass bands instead of iron — richer
    band_hi   = (255, 230, 140),
)


def draw_jeweled_chest(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 96
    body = _chest_body_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _draw_chest(surf, cx, cy, **JEWELED_PALETTE)
    _heap_gold(surf, body, n_coins=7)

    # Gems peeking out of the heap at varied depths
    gems = (
        (body.centerx - 12, body.y - 12, (210,  40,  50)),    # ruby
        (body.centerx + 10, body.y - 10, ( 50, 200, 110)),    # emerald
        (body.centerx -  3, body.y -  4, ( 80, 150, 230)),    # sapphire
        (body.centerx + 16, body.y -  4, (220, 100, 220)),    # amethyst
    )
    for gx, gy, col in gems:
        _draw_gem(surf, gx, gy, col)

    # Crown on the heap peak
    _draw_crown(surf, body.centerx + 2, body.y - 18)

    # Pearl strand draped from one corner of the chest over the lip
    _draw_pearl_strand(surf, body.x + 8, body.y - 2,
                       body.x - 4, body.y + 10, n=7)

    _shake_lines(surf, cx, body.y - LID_H, w=CHEST_W, color=(40, 25, 12))
    _spill_trail(surf, body.x - 4, body.y - 2, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 3 — SUNKEN BARNACLED CHEST
# ════════════════════════════════════════════════════════════════════════════
# Recovered from the ocean floor: darker waterlogged wood, green algae
# streaks running down the sides, barnacle clusters dotted across the
# lid + body, a starfish stuck to the front lock plate. Gold + a few
# pearls mixed into the heap.

SUNKEN_PALETTE = dict(
    wood_hi   = (105,  90,  68),
    wood_mid  = ( 65,  56,  40),
    wood_dark = ( 30,  26,  18),
    band_dark = ( 18,  22,  22),
    band_mid  = ( 50,  62,  58),
    band_hi   = ( 95, 115, 100),
)


def draw_sunken_chest(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 96
    body = _chest_body_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _draw_chest(surf, cx, cy, **SUNKEN_PALETTE,
                interior=(12, 18, 18), lid_inside=(20, 26, 24))

    # Algae streaks down the front (translucent green)
    algae = pygame.Surface((body.w, body.h), pygame.SRCALPHA)
    for sx in (8, 22, 38, 50):
        for y in range(body.h):
            t = y / body.h
            a = int(120 * t)
            algae.fill((40, 110, 50, a), pygame.Rect(sx, y, 2, 1))
    surf.blit(algae, body.topleft)

    # Barnacle clusters on the lid arc + body corners
    barnacles = (
        (body.centerx - 12, body.y - LID_H + 4, 4),
        (body.centerx + 8,  body.y - LID_H + 2, 5),
        (body.centerx + 18, body.y - LID_H + 8, 3),
        (body.x + 6,        body.y + 22,         4),
        (body.right - 8,    body.y + 18,         3),
    )
    for bx, by, br in barnacles:
        _draw_barnacle(surf, bx, by, r=br)

    # Starfish stuck on the lock plate
    sx, sy = body.centerx + 12, body.centery + 4
    star_pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        r = 6 if i % 2 == 0 else 2
        star_pts.append((sx + math.cos(ang) * r, sy + math.sin(ang) * r))
    pygame.draw.polygon(surf, NEAR_BLACK,
                        [(p[0], p[1] + 1) for p in star_pts])
    pygame.draw.polygon(surf, (220, 110,  70), star_pts)
    pygame.draw.polygon(surf, (250, 160, 120),
                        [(sx, sy - 4), (sx - 1, sy), (sx + 1, sy)])

    # Treasure: gold heap, but swap a few discs for pearls
    _heap_gold(surf, body, n_coins=6)
    for px, py in ((body.centerx - 5, body.y - 12),
                   (body.centerx + 4, body.y - 16),
                   (body.centerx + 12, body.y - 8)):
        pygame.draw.circle(surf, NEAR_BLACK, (px, py), 5)
        pygame.draw.circle(surf, (240, 230, 215), (px, py), 4)
        pygame.draw.circle(surf, WHITE, (px - 1, py - 1), 1)

    # Drip particle below the chest (water trickle)
    for dx, dy in ((-8, 8), (4, 14), (18, 10)):
        pygame.draw.line(surf, (90, 170, 210),
                         (cx + dx, body.bottom + dy),
                         (cx + dx, body.bottom + dy + 4), 2)

    _shake_lines(surf, cx, body.y - LID_H, w=CHEST_W, color=(20, 35, 30))
    _spill_trail(surf, body.x - 4, body.y - 2, side=-1, sparkle=(190, 230, 200))


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 4 — WEATHERED MAP CHEST
# ════════════════════════════════════════════════════════════════════════════
# The "just dug up at X marks the spot" chest: sun-bleached pale wood,
# sandy crust at the base, a folded parchment map sticking out of the
# heap, a big red X painted across the closed half of the lid. Tied with
# an old rope across the body.

WEATHERED_PALETTE = dict(
    wood_hi   = (230, 200, 150),
    wood_mid  = (175, 140,  88),
    wood_dark = (115,  85,  44),
    band_dark = ( 60,  50,  40),
    band_mid  = (130, 115,  90),
    band_hi   = (200, 185, 160),
)


def _lid_mark_X(surf, lid_rect):
    """Red painted X across the open lid back (visible because the lid
    is hinged backward, so the outside of the lid faces upward)."""
    # The visible side IS the lid's underside, but for the map-chest
    # variant we paint a faded X across the rim where the outside
    # would peek over the top edge.
    pad = 4
    x1 = (lid_rect.x + pad, lid_rect.y + pad)
    x2 = (lid_rect.right - pad, lid_rect.bottom - 4)
    pygame.draw.line(surf, (140, 30, 20), x1, x2, 4)
    pygame.draw.line(surf, (200, 60, 50), x1, x2, 2)
    x3 = (lid_rect.right - pad, lid_rect.y + pad)
    x4 = (lid_rect.x + pad, lid_rect.bottom - 4)
    pygame.draw.line(surf, (140, 30, 20), x3, x4, 4)
    pygame.draw.line(surf, (200, 60, 50), x3, x4, 2)


def draw_weathered_chest(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 96
    body = _chest_body_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _draw_chest(surf, cx, cy, **WEATHERED_PALETTE,
                interior=(60, 40, 20), lid_inside=(120, 95, 55),
                lid_mark=_lid_mark_X)

    # Sand caked along the bottom edge
    sand_y = body.bottom - 6
    sand_surf = pygame.Surface((body.w + 6, 10), pygame.SRCALPHA)
    for i in range(40):
        x = (i * 7 + (i * 13) % 5) % (body.w + 6)
        y = (i * 3) % 8
        pygame.draw.circle(sand_surf, (230, 200, 150, 200), (x, y + 2), 2)
        pygame.draw.circle(sand_surf, (250, 220, 170, 220), (x - 1, y + 1), 1)
    surf.blit(sand_surf, (body.x - 3, sand_y))
    # A few sand grains falling off
    for sx, sy in ((body.x - 4, body.bottom + 6),
                   (body.right - 10, body.bottom + 10),
                   (body.x + 18, body.bottom + 14)):
        pygame.draw.circle(surf, (230, 200, 150), (sx, sy), 1)

    # Old fraying rope tied across the body (vertical)
    rope_x = body.centerx + 18
    pygame.draw.line(surf, (90, 65, 30),
                     (rope_x, body.y - 4), (rope_x, body.bottom + 2), 3)
    pygame.draw.line(surf, (165, 120, 60),
                     (rope_x, body.y - 4), (rope_x, body.bottom + 2), 1)
    # Knot
    pygame.draw.circle(surf, (90, 65, 30), (rope_x, body.bottom + 2), 3)
    pygame.draw.circle(surf, (165, 120, 60), (rope_x, body.bottom + 2), 2)

    # Treasure heap (slightly smaller, more "dug up" not overflowing)
    _heap_gold(surf, body, n_coins=6)

    # Folded parchment map sticking up out of the heap
    map_rect = pygame.Rect(body.centerx - 14, body.y - 24, 12, 14)
    pygame.draw.polygon(surf, NEAR_BLACK, [
        (map_rect.x - 1, map_rect.y),
        (map_rect.right + 1, map_rect.y - 2),
        (map_rect.right + 1, map_rect.bottom + 1),
        (map_rect.x - 1, map_rect.bottom + 1),
    ])
    pygame.draw.polygon(surf, (235, 210, 160), [
        (map_rect.x, map_rect.y + 1),
        (map_rect.right, map_rect.y - 1),
        (map_rect.right, map_rect.bottom),
        (map_rect.x, map_rect.bottom),
    ])
    # Map's faint compass + X
    pygame.draw.line(surf, (140,  60,  20),
                     (map_rect.x + 2, map_rect.y + 4),
                     (map_rect.right - 2, map_rect.y + 4), 1)
    pygame.draw.line(surf, (180,  40,  30),
                     (map_rect.centerx - 2, map_rect.centery + 2),
                     (map_rect.centerx + 2, map_rect.centery + 6), 1)
    pygame.draw.line(surf, (180,  40,  30),
                     (map_rect.centerx + 2, map_rect.centery + 2),
                     (map_rect.centerx - 2, map_rect.centery + 6), 1)

    _shake_lines(surf, cx, body.y - LID_H, w=CHEST_W, color=(80, 60, 30))
    _spill_trail(surf, body.x - 4, body.y - 2, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 5 — CAPTAIN'S BLACK-IRON CHEST
# ════════════════════════════════════════════════════════════════════════════
# Dark-stained chest, almost black-iron in feel: heavy iron strapping,
# a brass skull-and-crossbones medallion replacing the keyhole, deep
# crimson velvet lining visible inside the open lid, and a more
# packed-tight gold heap. The captain's personal stash.

CAPTAIN_PALETTE = dict(
    wood_hi   = ( 95,  78,  60),
    wood_mid  = ( 55,  42,  30),
    wood_dark = ( 22,  16,  10),
    band_dark = ( 12,  12,  16),
    band_mid  = ( 60,  60,  70),
    band_hi   = (140, 140, 155),
)


def draw_captains_chest(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 96
    body = _chest_body_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _draw_chest(surf, cx, cy, **CAPTAIN_PALETTE,
                interior=(15, 8, 8), lid_inside=(140, 18, 28))

    # Brass skull-and-crossbones medallion ON TOP of the lock plate
    _draw_skull(surf, body.centerx, body.centery + 1)

    # Gold heap (tightly packed)
    _heap_gold(surf, body, n_coins=8)

    # A glint of crimson velvet edge peeking over the top of the body
    velvet = pygame.Rect(body.x + 6, body.y - 3, body.w - 12, 3)
    pygame.draw.rect(surf, (140, 18, 28), velvet)
    pygame.draw.line(surf, (200, 50, 60),
                     (velvet.x + 1, velvet.y),
                     (velvet.right - 2, velvet.y), 1)

    _shake_lines(surf, cx, body.y - LID_H, w=CHEST_W, color=(20, 14, 14))
    _spill_trail(surf, body.x - 4, body.y - 2, side=-1)


# ── Registry ────────────────────────────────────────────────────────────────

VARIANTS = [
    ("classic_chest",   "CLASSIC GOLD HOARD",       draw_classic_chest),
    ("jeweled_chest",   "JEWELED ROYAL HAUL",       draw_jeweled_chest),
    ("sunken_chest",    "SUNKEN BARNACLED CHEST",   draw_sunken_chest),
    ("weathered_chest", "WEATHERED MAP CHEST",      draw_weathered_chest),
    ("captains_chest",  "CAPTAIN'S BLACK-IRON",     draw_captains_chest),
]
