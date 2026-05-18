"""Five visual treatments for the TREASURE BOX power-up.

Concept: Pip picks up a treasure container and shakes it while flying.
Each wing flap rattles the container and a coin tumbles out into the
"+1 / +3" pool. The five variants explore different container styles and
spill metaphors so we can pick the read that fits Skybit best.

Each `draw_<name>(surf, bird_cx, bird_cy, t=0.0)` paints the carried
container, the carry attachment (claws, ribbon, chain), and 3-4 in-flight
coins trailing behind/below the bird at staggered fall heights. The
bird itself is NOT painted here — the caller positions a parrot frame
at (bird_cx, bird_cy) before invoking the overlay so all variants share
the exact same Pip silhouette. `t` is reserved for an optional shake
phase; default 0 = static for preview renders.

Preview-only — nothing in game/ imports this yet. Designed at the same
2× scratch density as `surprise_box_variants.py` so the look transfers
cleanly when one variant is wired into `entities.PowerUp` /
`world._activate_heist`.
"""
import math
import pathlib
import pygame

from game.draw import (
    UI_GOLD, UI_CREAM, UI_ORANGE, UI_RED, NEAR_BLACK, WHITE,
    COIN_LIGHT, COIN_DARK, lerp_color,
)


# ── shared palette ──────────────────────────────────────────────────────────

DK_OUTLINE = (22, 14, 10)
WOOD_BASE  = (140,  85,  42)
WOOD_DARK  = ( 90,  52,  22)
WOOD_HI    = (190, 130,  72)
BRASS_BASE = (210, 165,  60)
BRASS_HI   = (255, 230, 140)
BRASS_DK   = (130,  90,  20)
GOLD_HI    = (255, 235, 150)
BURLAP_BASE  = (190, 155,  95)
BURLAP_DARK  = (130,  95,  55)
BURLAP_HI    = (220, 195, 135)
ARCANE_BASE  = ( 60,  35, 100)
ARCANE_DARK  = ( 28,  14,  55)
ARCANE_RUNE  = (100, 230, 230)
ARCANE_GLOW  = (140, 240, 255)
IRON_BASE    = ( 75,  72,  78)
IRON_DARK    = ( 38,  36,  42)
IRON_HI      = (140, 138, 145)
RUST_HI      = (180,  95,  45)


# ── font cache ──────────────────────────────────────────────────────────────

_font_cache: dict = {}
_FONT_PATH = pathlib.Path(__file__).parent / "assets" / "LiberationSans-Bold.ttf"


def _font(size):
    f = _font_cache.get(size)
    if f is None:
        f = pygame.font.Font(str(_FONT_PATH), size)
        _font_cache[size] = f
    return f


# ── shared coin sprite (small static coin for the spill trail) ──────────────

def _draw_coin(surf, cx, cy, r=8, squeeze=1.0, glint=True):
    """Tiny gold coin disc with the COIN_DARK rope rim + COIN_LIGHT gradient
    fill. Stamped at the spill positions to suggest "+1 just popped out"
    without having to instance the real Coin class."""
    w = max(2, int(r * 2 * squeeze))
    h = r * 2
    disc = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(disc, DK_OUTLINE, pygame.Rect(0, 0, w + 2, h + 2))
    pygame.draw.ellipse(disc, COIN_DARK,  pygame.Rect(1, 1, w, h))
    # vertical-gradient face
    inner = pygame.Rect(2, 2, max(0, w - 2), max(0, h - 2))
    if inner.w > 0 and inner.h > 0:
        for y in range(inner.h):
            t = y / max(1, inner.h - 1)
            c = lerp_color(COIN_LIGHT, COIN_DARK, t)
            pygame.draw.line(disc, c,
                             (inner.x, inner.y + y),
                             (inner.x + inner.w - 1, inner.y + y))
        # embossed "$" + top sheen
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
    """Four falling coins at successive stages of the drop, staggered to
    suggest 1 coin per flap. `side` = -1 spills to the LEFT (i.e. behind
    Pip, who flies left-to-right), +1 to the right. The bird's flight is
    left-to-right, so the spilled coins drift BACKWARD (to the left of
    anchor) as they fall — like dropped objects relative to a moving
    carrier. A few sparkle dots tie the trail back to the container.

    Anchor is the spill mouth (top edge of the container's opening).
    First coin pops UPWARD just above the anchor; the rest cascade
    downward and backward so the read of "shaken loose, drifting behind"
    is unambiguous in a still mockup."""
    # 4-point starburst right at the container mouth (each flap → new puff).
    burst = pygame.Surface((26, 26), pygame.SRCALPHA)
    pygame.draw.line(burst, (*GOLD_HI, 230), (13,  1), (13, 25), 3)
    pygame.draw.line(burst, (*GOLD_HI, 230), ( 1, 13), (25, 13), 3)
    pygame.draw.line(burst, (255, 255, 255, 230), (13,  4), (13, 22), 1)
    pygame.draw.line(burst, (255, 255, 255, 230), ( 4, 13), (22, 13), 1)
    surf.blit(burst, (anchor_x - 13, anchor_y - 13))

    # Four coins: just-popped (above anchor, max squeeze = mid-spin),
    # then three cascading down-and-back at growing distances.
    stages = (
        # (dx, dy, radius, squeeze)
        (  3 * side, -14, 8, 0.45),
        (  8 * side,   8, 9, 1.00),
        ( 22 * side,  28, 8, 0.70),
        ( 40 * side,  52, 7, 0.90),
    )
    for dx, dy, r, sq in stages:
        _draw_coin(surf, anchor_x + dx, anchor_y + dy, r=r, squeeze=sq)

    # Sparkle puffs trailing alongside the coins.
    for dx, dy, sr in ((14 * side, 18, 2), (30 * side, 40, 2),
                       (6 * side, -22, 2)):
        s = pygame.Surface((sr * 4, sr * 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*sparkle, 220), (sr * 2, sr * 2), sr)
        pygame.draw.circle(s, (255, 255, 255, 200), (sr * 2, sr * 2),
                           max(1, sr - 1))
        surf.blit(s, (anchor_x + dx - sr * 2, anchor_y + dy - sr * 2))


def _shake_lines(surf, cx, cy, w=24, *, color=(40, 30, 20)):
    """Cartoon motion lines flanking the container so the still mockup
    reads as 'being shaken'. Two short hashes on each side."""
    for sx in (cx - w // 2 - 6, cx + w // 2 + 6):
        for dy in (-4, 4):
            pygame.draw.line(surf, color, (sx, cy + dy), (sx + (4 if sx > cx else -4) * (1 if sx > cx else 1), cy + dy), 2)


# ── shared geometry helpers ─────────────────────────────────────────────────

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


def _drop_shadow(surf, cx, cy, w):
    sh = pygame.Surface((w + 10, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 12, 130), sh.get_rect())
    surf.blit(sh, (cx - (w + 10) // 2, cy))


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 1 — WOODEN PIRATE CHEST
# ════════════════════════════════════════════════════════════════════════════
# Heavy oak chest with brass bands and a dangling padlock. Carried under
# Pip's belly, gripped by both talons. Lid hinged but a brass key dangles
# from the keyhole — each flap rattles the chest open a sliver and one
# doubloon tumbles out the front gap with a tiny puff of woodsmoke-dust.
# Warm earthy palette to contrast with the surprise box's red+gold.

def draw_wooden_chest(surf, bird_cx, bird_cy, t=0.0):
    # Box sits well below the bird so Pip's silhouette doesn't overlap it.
    # The parrot sprite is ~60 px tall (centred), so anchor the chest top
    # at +32 from bird_cy to give a clean ~12 px gap below Pip's feet.
    box_w, box_h = 56, 40
    cx = bird_cx + 4
    cy = bird_cy + 60
    rect = pygame.Rect(cx - box_w // 2, cy - box_h // 2, box_w, box_h)

    _drop_shadow(surf, cx, rect.bottom + 4, box_w)

    # Two thin ropes from bird's belly down to the chest corners — visible
    # above the chest, anchored where the talons would tuck under the body.
    for tx in (rect.x + 8, rect.right - 8):
        pygame.draw.line(surf, (50, 30, 18),
                         (bird_cx - 4 + (tx - cx) // 4, bird_cy + 24),
                         (tx, rect.y + 2), 3)
        pygame.draw.line(surf, (180, 130, 60),
                         (bird_cx - 4 + (tx - cx) // 4, bird_cy + 24),
                         (tx, rect.y + 2), 1)

    # Outline + wood body
    pygame.draw.rect(surf, DK_OUTLINE, rect.inflate(4, 4), border_radius=5)
    _gradient_rect(surf, rect, WOOD_HI, WOOD_DARK, radius=4)

    # Hinged lid as separate band on top
    lid = pygame.Rect(rect.x, rect.y, rect.w, 14)
    pygame.draw.rect(surf, DK_OUTLINE, lid.inflate(4, 2), border_radius=5)
    _gradient_rect(surf, lid, WOOD_HI, WOOD_BASE, radius=4)
    # Lid is slightly ajar — paint a thin black slit just under it
    pygame.draw.rect(surf, NEAR_BLACK, pygame.Rect(rect.x + 4, lid.bottom - 1,
                                                   rect.w - 8, 3))

    # Vertical wood grain (3 darker streaks)
    for gx in (rect.x + 10, rect.x + rect.w // 2, rect.right - 10):
        pygame.draw.line(surf, WOOD_DARK, (gx, rect.y + 16),
                         (gx, rect.bottom - 4), 1)

    # Two brass bands across the body
    for by in (rect.y + 18, rect.bottom - 10):
        pygame.draw.rect(surf, BRASS_DK, pygame.Rect(rect.x - 1, by - 1, rect.w + 2, 5))
        pygame.draw.rect(surf, BRASS_BASE, pygame.Rect(rect.x, by, rect.w, 3))
        pygame.draw.line(surf, BRASS_HI, (rect.x + 2, by), (rect.right - 2, by), 1)

    # Brass corner studs
    for sx, sy in ((rect.x + 3, rect.y + 4), (rect.right - 5, rect.y + 4),
                   (rect.x + 3, rect.bottom - 5), (rect.right - 5, rect.bottom - 5)):
        pygame.draw.circle(surf, BRASS_DK, (sx, sy), 2)
        pygame.draw.circle(surf, BRASS_HI, (sx, sy), 1)

    # Front-facing keyhole + dangling brass key (key swings with shake)
    kh_cx, kh_cy = cx, rect.y + 22
    pygame.draw.circle(surf, BRASS_DK, (kh_cx, kh_cy), 4)
    pygame.draw.circle(surf, NEAR_BLACK, (kh_cx, kh_cy), 2)
    pygame.draw.rect(surf, NEAR_BLACK, pygame.Rect(kh_cx - 1, kh_cy, 2, 4))

    # Key dangling from the lock
    kx, ky = kh_cx + 6, kh_cy + 10
    pygame.draw.line(surf, BRASS_DK, (kh_cx, kh_cy + 2), (kx, ky), 1)
    pygame.draw.circle(surf, BRASS_DK, (kx + 2, ky), 3)
    pygame.draw.circle(surf, BRASS_BASE, (kx + 2, ky), 2)
    pygame.draw.line(surf, BRASS_BASE, (kx + 2, ky + 2), (kx + 2, ky + 6), 2)
    pygame.draw.line(surf, BRASS_BASE, (kx + 2, ky + 6), (kx + 5, ky + 6), 1)

    _shake_lines(surf, cx, rect.y + 4, w=box_w, color=(40, 25, 12))

    # Spill trail: anchor at the chest's TOP-LEFT corner so the burst
    # sits at the lid-body seam, then coins arc into clear air to the
    # left (behind Pip, who flies left-to-right).
    _spill_trail(surf, rect.x - 4, lid.bottom - 4, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 2 — ARCANE RUNE CHEST
# ════════════════════════════════════════════════════════════════════════════
# Late-game / mystical aesthetic. Deep purple chest etched with glowing
# teal runes, floating below Pip with no visible attachment (held by a
# pair of glittering cyan magic chains). Lid is permanently open and a
# column of pale teal light beams up out of it. Coins materialize at the
# top of the light column, arc outward with sparkle-trails. Whole thing
# pulses brighter on each flap.

def draw_arcane_chest(surf, bird_cx, bird_cy, t=0.0):
    box_w, box_h = 54, 40
    cx = bird_cx + 4
    cy = bird_cy + 68
    rect = pygame.Rect(cx - box_w // 2, cy - box_h // 2, box_w, box_h)

    # Soft cyan halo behind everything
    halo = pygame.Surface((box_w + 60, box_h + 60), pygame.SRCALPHA)
    for rr, a in ((box_w // 2 + 28, 36), (box_w // 2 + 18, 54), (box_w // 2 + 8, 72)):
        pygame.draw.circle(halo, (*ARCANE_GLOW, a),
                           (halo.get_width() // 2, halo.get_height() // 2), rr)
    surf.blit(halo, (cx - halo.get_width() // 2, cy - halo.get_height() // 2))

    # Light column rising from the open lid up toward the bird (taller now)
    col_h = (bird_cy + 22) - (rect.y - 8)
    col_h = max(20, col_h)
    col = pygame.Surface((24, col_h), pygame.SRCALPHA)
    for y in range(col_h):
        ty = y / max(1, col_h - 1)
        a = int(180 * (1 - ty))
        w = int(22 - ty * 14)
        col.fill((*ARCANE_GLOW, a),
                 pygame.Rect((24 - w) // 2, y, w, 1))
    surf.blit(col, (cx - 12, rect.y - col_h))

    # Magic chains: dotted cyan links from the bird's belly to chest top
    for tx in (rect.x + 10, rect.right - 10):
        for i in range(6):
            t_i = i / 5.0
            lx = int(bird_cx + (tx - bird_cx) * t_i)
            ly = int((bird_cy + 24) + (rect.y - 2 - (bird_cy + 24)) * t_i)
            pygame.draw.circle(surf, (*ARCANE_GLOW, 220), (lx, ly), 3)
            pygame.draw.circle(surf, WHITE, (lx, ly), 1)

    _drop_shadow(surf, cx, rect.bottom + 4, box_w - 4)

    # Chest body (dark amethyst gradient)
    pygame.draw.rect(surf, DK_OUTLINE, rect.inflate(4, 4), border_radius=5)
    _gradient_rect(surf, rect, ARCANE_BASE, ARCANE_DARK, radius=4)

    # Open lid: thin curved band BEHIND the chest, hinged backward
    lid_rect = pygame.Rect(rect.x, rect.y - 8, rect.w, 8)
    pygame.draw.rect(surf, DK_OUTLINE, lid_rect.inflate(4, 2), border_radius=4)
    _gradient_rect(surf, lid_rect, ARCANE_BASE, ARCANE_DARK, radius=3)
    # Lid inner glow (the inside is lit cyan)
    pygame.draw.line(surf, ARCANE_GLOW,
                     (rect.x + 4, lid_rect.bottom), (rect.right - 4, lid_rect.bottom), 2)

    # Etched glowing runes — a simple sigil grid across the front face
    rune_y = rect.y + rect.h // 2 + 2
    for i, gx in enumerate((rect.x + 10, rect.x + rect.w // 2 - 4, rect.right - 14)):
        # Rune outline (slightly different per slot)
        if i == 0:
            # Triangle
            pygame.draw.polygon(surf, ARCANE_RUNE,
                                [(gx + 4, rune_y - 6), (gx, rune_y + 4), (gx + 8, rune_y + 4)], 1)
        elif i == 1:
            # Diamond
            pygame.draw.polygon(surf, ARCANE_RUNE,
                                [(gx + 4, rune_y - 6), (gx + 8, rune_y),
                                 (gx + 4, rune_y + 6), (gx, rune_y)], 1)
        else:
            # Cross
            pygame.draw.line(surf, ARCANE_RUNE,
                             (gx + 4, rune_y - 6), (gx + 4, rune_y + 6), 2)
            pygame.draw.line(surf, ARCANE_RUNE,
                             (gx, rune_y), (gx + 8, rune_y), 2)

    # Coins emerge out of the open lid and arc out behind Pip.
    _spill_trail(surf, rect.x - 4, rect.y - 2, side=-1, sparkle=ARCANE_GLOW)

    _shake_lines(surf, cx, rect.y - 4, w=box_w, color=(40, 30, 80))


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 3 — PIRATE LOOT SACK
# ════════════════════════════════════════════════════════════════════════════
# Cinched burlap money sack with a rope tie at the top + a hand-painted
# "$" mark on the front. Dangles from one of Pip's talons by the rope.
# Bulbous, asymmetric shape suggesting it's stuffed with coins. Each flap
# swings the sack, and a coin dribbles out the puckered top with a puff
# of gold dust. Most cartoonish/exaggerated of the five.

def draw_loot_sack(surf, bird_cx, bird_cy, t=0.0):
    sack_w, sack_h = 48, 58
    cx = bird_cx + 4              # hangs slightly to the right of Pip's centre
    top_y = bird_cy + 40
    bot_y = top_y + sack_h

    _drop_shadow(surf, cx, bot_y + 2, sack_w + 4)

    # Rope from talon down to cinch (thicker, segmented)
    pygame.draw.line(surf, (60, 35, 12),
                     (bird_cx, bird_cy + 24), (cx, top_y - 2), 4)
    pygame.draw.line(surf, (160, 110, 60),
                     (bird_cx, bird_cy + 24), (cx, top_y - 2), 2)
    # Rope hatching for texture
    for i in range(3):
        rx1 = bird_cx + (cx - bird_cx) * (i + 1) / 4
        ry1 = (bird_cy + 24) + ((top_y - 2) - (bird_cy + 24)) * (i + 1) / 4
        pygame.draw.line(surf, (60, 35, 12),
                         (int(rx1 - 2), int(ry1 - 1)),
                         (int(rx1 + 2), int(ry1 + 1)), 1)

    # Sack outline as a bulging polygon (wider in the middle bottom)
    body_pts = [
        (cx - 8,       top_y),       # cinched top-left
        (cx + 8,       top_y),       # cinched top-right
        (cx + sack_w // 2,   top_y + 14),    # bulge right shoulder
        (cx + sack_w // 2 - 2, bot_y - 4),   # bottom right
        (cx - sack_w // 2 + 2, bot_y - 2),   # bottom left (asymmetric)
        (cx - sack_w // 2,   top_y + 16),    # bulge left shoulder
    ]
    # Outline
    pygame.draw.polygon(surf, DK_OUTLINE, [(x, y + 2) for x, y in body_pts])
    pygame.draw.polygon(surf, DK_OUTLINE, body_pts, 0)
    # Body fill — simulate gradient with two stacked passes
    body_surf = pygame.Surface((sack_w + 4, sack_h + 6), pygame.SRCALPHA)
    pts_local = [(x - cx + sack_w // 2 + 2, y - top_y + 2) for x, y in body_pts]
    pygame.draw.polygon(body_surf, BURLAP_BASE, pts_local)
    # Top-half lighter (highlight)
    hl_pts = [(p[0], p[1]) for p in pts_local if p[1] < sack_h // 2 + 4]
    if len(hl_pts) >= 3:
        pygame.draw.polygon(body_surf, BURLAP_HI, hl_pts)
    surf.blit(body_surf, (cx - sack_w // 2 - 2, top_y - 2))

    # Burlap texture: short diagonal stitches across the bag
    for sy in range(top_y + 18, bot_y - 4, 6):
        for sx_off in range(-sack_w // 2 + 6, sack_w // 2 - 4, 7):
            sx = cx + sx_off + (3 if (sy // 6) % 2 else 0)
            pygame.draw.line(surf, BURLAP_DARK, (sx, sy), (sx + 2, sy + 2), 1)

    # Rope cinch at the top — fat horizontal band with vertical pleat marks
    cinch = pygame.Rect(cx - 11, top_y - 4, 22, 9)
    pygame.draw.rect(surf, DK_OUTLINE, cinch.inflate(2, 2), border_radius=3)
    _gradient_rect(surf, cinch, (200, 150,  70), (140, 100, 40), radius=3)
    for px in range(cinch.x + 3, cinch.right - 2, 4):
        pygame.draw.line(surf, (90, 60, 20), (px, cinch.y + 1),
                         (px, cinch.bottom - 1), 1)

    # Pucker — three radial creases going down from the cinch
    for ang_d in (-30, 0, 30):
        ang = math.radians(ang_d + 90)
        ex = cx + int(math.cos(ang) * 14)
        ey = top_y + 6 + int(math.sin(ang) * 12)
        pygame.draw.line(surf, BURLAP_DARK, (cx, top_y + 6), (ex, ey), 1)

    # Big hand-painted "$" on the front of the sack
    f = _font(28)
    g = f.render("$", True, NEAR_BLACK)
    gh = f.render("$", True, UI_GOLD)
    g_rect = g.get_rect(center=(cx, top_y + sack_h // 2 + 6))
    surf.blit(g,  (g_rect.x + 2, g_rect.y + 2))
    surf.blit(gh,  g_rect.topleft)

    _shake_lines(surf, cx, top_y + 4, w=sack_w + 4, color=(60, 40, 12))

    # Coins dribble out the puckered cinch on the LEFT side, drift back-down.
    _spill_trail(surf, cx - sack_w // 2 + 4, top_y + 4, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 4 — RED GIFT BOX (Surprise-box sibling)
# ════════════════════════════════════════════════════════════════════════════
# Same red-gift-wrap DNA as the existing Surprise Box pickup, but now it
# hangs by a glittery silver ribbon under Pip and the lid pops up an inch
# each flap to fountain coins + confetti. Pure festive: easiest visual
# integration since the surprise box already establishes the gift-box look
# in the game.

def draw_gift_box(surf, bird_cx, bird_cy, t=0.0):
    box_w, box_h = 52, 46
    cx = bird_cx + 2
    cy = bird_cy + 70
    rect = pygame.Rect(cx - box_w // 2, cy - box_h // 2, box_w, box_h)

    _drop_shadow(surf, cx, rect.bottom + 2, box_w)

    # Silver ribbon tether from bird's belly to box top
    rib_top = (bird_cx, bird_cy + 24)
    rib_bot = (cx, rect.y - 6)
    # Silver shimmer line (3-pass: dark / silver / white)
    pygame.draw.line(surf, NEAR_BLACK,   rib_top, rib_bot, 4)
    pygame.draw.line(surf, (180, 180, 200), rib_top, rib_bot, 2)
    pygame.draw.line(surf, WHITE,        rib_top, rib_bot, 1)
    # Glitter dots along ribbon
    for i in range(4):
        ti = (i + 1) / 5.0
        gx = int(rib_top[0] + (rib_bot[0] - rib_top[0]) * ti)
        gy = int(rib_top[1] + (rib_bot[1] - rib_top[1]) * ti)
        pygame.draw.circle(surf, (255, 255, 230), (gx, gy), 2)
        pygame.draw.circle(surf, GOLD_HI, (gx, gy), 1)

    # Box body — red with vertical gradient
    pygame.draw.rect(surf, DK_OUTLINE, rect.inflate(4, 4), border_radius=5)
    _gradient_rect(surf, rect, (250, 95, 85), (140, 18, 26), radius=4)
    # Top sheen
    pygame.draw.line(surf, (255, 180, 170), (rect.x + 4, rect.y + 3),
                     (rect.right - 5, rect.y + 3), 2)

    # Cross gold ribbon
    rib_w = 6
    # Vertical
    pygame.draw.rect(surf, BRASS_DK, pygame.Rect(rect.centerx - rib_w // 2 - 1,
                                                  rect.y, rib_w + 2, rect.h))
    pygame.draw.rect(surf, UI_GOLD, pygame.Rect(rect.centerx - rib_w // 2,
                                                rect.y, rib_w, rect.h))
    pygame.draw.line(surf, GOLD_HI, (rect.centerx - rib_w // 2 + 1, rect.y),
                     (rect.centerx - rib_w // 2 + 1, rect.bottom - 1), 1)
    # Horizontal
    pygame.draw.rect(surf, BRASS_DK, pygame.Rect(rect.x, rect.centery - rib_w // 2 - 1,
                                                  rect.w, rib_w + 2))
    pygame.draw.rect(surf, UI_GOLD, pygame.Rect(rect.x, rect.centery - rib_w // 2,
                                                rect.w, rib_w))
    pygame.draw.line(surf, GOLD_HI, (rect.x, rect.centery - rib_w // 2 + 1),
                     (rect.right - 1, rect.centery - rib_w // 2 + 1), 1)

    # Bow up top (popped lid). Two little ellipse loops + knot.
    bow_cx, bow_cy = rect.centerx, rect.y - 4
    for dx in (-1, 1):
        pygame.draw.ellipse(surf, DK_OUTLINE,
                            pygame.Rect(bow_cx + dx * 4 - 6, bow_cy - 5, 11, 10))
        pygame.draw.ellipse(surf, UI_GOLD,
                            pygame.Rect(bow_cx + dx * 4 - 5, bow_cy - 4,  9,  8))
    pygame.draw.rect(surf, DK_OUTLINE, pygame.Rect(bow_cx - 3, bow_cy - 5, 7, 10),
                     border_radius=2)
    pygame.draw.rect(surf, UI_GOLD, pygame.Rect(bow_cx - 2, bow_cy - 4, 5, 8),
                     border_radius=2)

    # Confetti specks bursting up from behind the bow
    for i, (dx, dy, col) in enumerate((
        (-12, -16, UI_GOLD), (-4, -22, UI_CREAM), (5, -20, UI_RED),
        (12, -14, WHITE), (-16, -10, UI_ORANGE), (16, -8, UI_GOLD),
    )):
        cx_c = bow_cx + dx
        cy_c = bow_cy + dy
        rect_c = pygame.Rect(cx_c - 2, cy_c - 1, 4, 2)
        pygame.draw.rect(surf, NEAR_BLACK, rect_c.inflate(2, 2))
        pygame.draw.rect(surf, col, rect_c)

    _shake_lines(surf, cx, rect.y - 8, w=box_w + 10, color=(70, 8, 12))

    # Spill: coins fountain up + arc out behind Pip. Anchor outside the
    # box's left edge so the cascade reads clearly against open sky.
    _spill_trail(surf, rect.x - 6, rect.y + 8, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 5 — MINI MINE CART
# ════════════════════════════════════════════════════════════════════════════
# Tiny rusted iron mining cart on wheels, hanging by a pair of chains
# under Pip. Cart is brim-full of gold nuggets so the top edge looks
# overflowing. Each flap rocks the cart and a nugget bounces over the rim.
# Industrial / Donkey-Kong-Country vibe. Wheels spin freely (we draw spoke
# lines at an angle to suggest motion blur in the still mockup).

def draw_mine_cart(surf, bird_cx, bird_cy, t=0.0):
    cart_w, cart_h = 60, 32
    cx = bird_cx + 4
    cy = bird_cy + 76
    rect = pygame.Rect(cx - cart_w // 2, cy - cart_h // 2, cart_w, cart_h)

    _drop_shadow(surf, cx, rect.bottom + 12, cart_w + 8)

    # Two chains from bird belly to cart corners
    for tx in (rect.x + 6, rect.right - 6):
        # Chain links as dots
        for i in range(7):
            ti = i / 6.0
            lx = int(bird_cx + (tx - bird_cx) * ti)
            ly = int((bird_cy + 24) + (rect.y - 2 - (bird_cy + 24)) * ti)
            pygame.draw.circle(surf, NEAR_BLACK, (lx, ly), 3)
            pygame.draw.circle(surf, (170, 170, 180), (lx, ly), 2)

    # Cart body — trapezoid (wider at top, narrower at bottom) so it looks
    # like a 3/4 view bucket.
    body_pts = [
        (rect.x,           rect.y + 4),
        (rect.right,       rect.y + 4),
        (rect.right - 6,   rect.bottom - 2),
        (rect.x + 6,       rect.bottom - 2),
    ]
    pygame.draw.polygon(surf, DK_OUTLINE, [(x, y + 2) for x, y in body_pts])
    pygame.draw.polygon(surf, IRON_DARK,  body_pts)
    # Top rim (slightly lighter band)
    rim_pts = [
        (rect.x,         rect.y + 4),
        (rect.right,     rect.y + 4),
        (rect.right - 2, rect.y + 9),
        (rect.x + 2,     rect.y + 9),
    ]
    pygame.draw.polygon(surf, IRON_HI, rim_pts)
    # Rust streaks
    for sx in (rect.x + 12, rect.x + 30, rect.right - 14):
        pygame.draw.line(surf, RUST_HI, (sx, rect.y + 9),
                         (sx + 2, rect.bottom - 4), 1)
    # Iron rivets along the rim
    for rx in range(rect.x + 5, rect.right - 4, 8):
        pygame.draw.circle(surf, NEAR_BLACK, (rx, rect.y + 6), 2)
        pygame.draw.circle(surf, IRON_HI, (rx, rect.y + 6), 1)

    # Gold pile heaped up over the top (3 stacked nuggets visible)
    pile_y = rect.y + 4
    nuggets = (
        (cx - 12, pile_y - 4,  6),
        (cx,      pile_y - 7,  7),
        (cx + 13, pile_y - 3,  5),
        (cx - 5,  pile_y - 10, 4),
        (cx + 6,  pile_y - 9,  4),
    )
    for nx, ny, nr in nuggets:
        pygame.draw.circle(surf, BRASS_DK, (nx, ny + 1), nr + 1)
        pygame.draw.circle(surf, UI_GOLD, (nx, ny), nr)
        pygame.draw.circle(surf, GOLD_HI, (nx - nr // 3, ny - nr // 3), max(1, nr // 3))

    # Two wheels, spoked, with motion-blur arc lines to suggest rotation
    for wx in (rect.x + 10, rect.right - 12):
        wy = rect.bottom + 4
        pygame.draw.circle(surf, NEAR_BLACK, (wx, wy), 8)
        pygame.draw.circle(surf, IRON_HI,    (wx, wy), 6)
        pygame.draw.circle(surf, IRON_DARK,  (wx, wy), 3)
        # 4 spokes at a 30° rotation
        for ang_d in (15, 105, 195, 285):
            ang = math.radians(ang_d)
            ex = wx + int(math.cos(ang) * 6)
            ey = wy + int(math.sin(ang) * 6)
            pygame.draw.line(surf, IRON_DARK, (wx, wy), (ex, ey), 1)
        # Motion blur — an arc behind each wheel
        pygame.draw.arc(surf, (40, 30, 25),
                        pygame.Rect(wx - 9, wy - 9, 18, 18),
                        math.radians(170), math.radians(280), 2)

    _shake_lines(surf, cx, rect.y - 4, w=cart_w + 8, color=(35, 30, 28))

    # Spill: coins bouncing over the rim, drifting back behind Pip
    _spill_trail(surf, rect.x - 4, rect.y + 2, side=-1)


# ── Registry ────────────────────────────────────────────────────────────────

VARIANTS = [
    ("wooden_chest", "WOODEN PIRATE CHEST",  draw_wooden_chest),
    ("arcane_chest", "ARCANE RUNE CHEST",    draw_arcane_chest),
    ("loot_sack",    "PIRATE LOOT SACK",     draw_loot_sack),
    ("gift_box",     "RED GIFT BOX",         draw_gift_box),
    ("mine_cart",    "MINI MINE CART",       draw_mine_cart),
]
