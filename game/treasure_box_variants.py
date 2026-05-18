"""Five visual treatments for the TREASURE BOX power-up — round 3.

Round 3 brief: every variant is a *small CLOSED wooden treasure box*,
held tight under Pip with short carry ropes. The chest is locked, the
gold stays hidden until each flap rattles a single coin loose through
the lid-body seam. Variation lives in the wood styling + the iron /
brass / engraving on the lid face — not in size or contents.

Each `draw_<name>(surf, bird_cx, bird_cy, t=0.0)` paints the carry
ropes, the closed wooden box (with its variant-specific lid + body
treatment), motion lines suggesting the shake, and a 4-coin spill
cascade trailing behind Pip. The bird itself is positioned by the
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
    """Burst at the lid-body seam + 4 staggered coins cascading down and
    BACK (left, since Pip flies left-to-right). Identical across all
    variants so the A/B compares the chest only."""
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
    """Cartoon motion lines flanking the chest so the still mockup
    reads as 'being shaken'."""
    for sx in (cx - w // 2 - 7, cx + w // 2 + 7):
        for dy in (-4, 4):
            ex = sx + (4 if sx > cx else -4)
            pygame.draw.line(surf, color, (sx, cy + dy), (ex, cy + dy), 2)


# ── geometry constants ──────────────────────────────────────────────────────
# Small + tight to Pip's belly. The box is just 42×34 px at 1×, which at
# the 3× preview render becomes 126×102 — still readable but reads as a
# small carried object rather than a giant haul.

BOX_W  = 42
BODY_H = 22
LID_H  = 12          # flat-top variants
DOMED_LID_H = 16     # domed-top variants


def _box_rect(cx, cy):
    """Body rect of the closed chest. cy is the body's vertical centre."""
    return pygame.Rect(cx - BOX_W // 2, cy - BODY_H // 2, BOX_W, BODY_H)


# ── carry rope + drop shadow + gradient helpers ─────────────────────────────

def _drop_shadow(surf, cx, cy, w):
    sh = pygame.Surface((w + 8, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 12, 130), sh.get_rect())
    surf.blit(sh, (cx - (w + 8) // 2, cy))


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
    """Two short hemp ropes from Pip's talons to brass D-rings on the
    sides of the chest. Drawn BEFORE the chest so the rope passes
    behind the silhouette."""
    handle_y = body_rect.y + BODY_H // 2
    for tx, talon_dx in ((body_rect.x - 1, -3), (body_rect.right + 1, 3)):
        pygame.draw.line(surf, ROPE_DARK,
                         (bird_cx + talon_dx, bird_cy + 22),
                         (tx, handle_y), 4)
        pygame.draw.line(surf, ROPE_BASE,
                         (bird_cx + talon_dx, bird_cy + 22),
                         (tx, handle_y), 2)
        # Single fiber-hatch at the rope midpoint for texture
        rx = int((bird_cx + talon_dx + tx) / 2)
        ry = int(((bird_cy + 22) + handle_y) / 2)
        pygame.draw.line(surf, ROPE_DARK, (rx - 2, ry - 1), (rx + 2, ry + 1), 1)


def _draw_side_handles(surf, body, wood_dark):
    """Small brass D-ring handles on each side of the chest body."""
    for hx in (body.x - 1, body.right):
        pygame.draw.circle(surf, NEAR_BLACK, (hx, body.centery), 4, 0)
        pygame.draw.circle(surf, BRASS_DK,   (hx, body.centery), 3, 0)
        pygame.draw.circle(surf, BRASS_BASE, (hx, body.centery), 3, 1)
        pygame.draw.circle(surf, wood_dark,  (hx, body.centery), 1, 0)


def _draw_corner_studs(surf, body, *, color=BRASS_BASE,
                       dark=BRASS_DK, hi=BRASS_HI):
    """Four small studs at the corners of the body."""
    for cnx, cny in (
        (body.x + 2,     body.y + 2),
        (body.right - 3, body.y + 2),
        (body.x + 2,     body.bottom - 3),
        (body.right - 3, body.bottom - 3),
    ):
        pygame.draw.circle(surf, dark,  (cnx, cny), 2, 0)
        pygame.draw.circle(surf, color, (cnx, cny), 1, 0)


def _wood_grain(surf, body, dark, *, n=3):
    """Faint vertical grain streaks on the body."""
    step = body.w // (n + 1)
    for i in range(1, n + 1):
        gx = body.x + step * i
        pygame.draw.line(surf, dark,
                         (gx, body.y + 3),
                         (gx, body.bottom - 3), 1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 1 — PADLOCKED OAK
# ════════════════════════════════════════════════════════════════════════════
# The most "story-book" chest: warm oak body, flat lid, one big iron
# padlock dangling from a hasp on the front. Two iron straps. Brass
# corner studs. The padlock telegraphs "locked treasure inside."

WOOD_OAK_HI   = (185, 130,  70)
WOOD_OAK_MID  = (140,  88,  44)
WOOD_OAK_DARK = ( 78,  44,  16)


def draw_padlocked_oak(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _drop_shadow(surf, cx, body.bottom + 4, BOX_W)

    # Flat lid sitting on top of the body
    lid = pygame.Rect(body.x - 2, body.y - LID_H, body.w + 4, LID_H)
    pygame.draw.rect(surf, DK_OUTLINE, lid.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, lid, WOOD_OAK_HI, WOOD_OAK_MID, radius=2)
    # Lid bottom edge shadow (where the lid meets the body — the seam)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(body.x, body.y - 1, body.w, 2))

    # Body
    pygame.draw.rect(surf, DK_OUTLINE, body.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, body, WOOD_OAK_MID, WOOD_OAK_DARK, radius=2)
    _wood_grain(surf, body, WOOD_OAK_DARK, n=3)

    # Two iron straps across the body
    for by in (body.y + 4, body.bottom - 7):
        strap = pygame.Rect(body.x - 1, by, body.w + 2, 4)
        pygame.draw.rect(surf, IRON_DARK, strap)
        pygame.draw.rect(surf, IRON_BASE, strap.inflate(0, -2))
        pygame.draw.line(surf, IRON_HI,
                         (strap.x + 2, strap.y + 1),
                         (strap.right - 2, strap.y + 1), 1)
        # Rivet heads at the ends
        for rx in (body.x + 2, body.right - 3):
            pygame.draw.circle(surf, IRON_DARK, (rx, by + 2), 2)
            pygame.draw.circle(surf, IRON_HI,   (rx, by + 2), 1)

    _draw_corner_studs(surf, body)
    _draw_side_handles(surf, body, WOOD_OAK_DARK)

    # ── Hasp + padlock (the feature)
    # Hasp plate on the lid centre + a vertical lug protruding down past
    # the seam, with the padlock hooked through.
    hasp_top = pygame.Rect(lid.centerx - 5, lid.y + 3, 10, LID_H - 2)
    pygame.draw.rect(surf, IRON_DARK, hasp_top)
    pygame.draw.rect(surf, IRON_BASE, hasp_top.inflate(-2, -2))
    pygame.draw.line(surf, IRON_HI,
                     (hasp_top.x + 1, hasp_top.y + 1),
                     (hasp_top.right - 2, hasp_top.y + 1), 1)
    # Padlock body — fat rounded square with a shackle arc up through the hasp
    pad_y = body.y + 4
    pad = pygame.Rect(body.centerx - 6, pad_y, 12, 11)
    # Shackle (U-bend) behind the lock body, looping through the hasp lug
    pygame.draw.arc(surf, IRON_DARK,
                    pygame.Rect(pad.centerx - 5, pad.y - 6, 10, 12),
                    math.radians(0), math.radians(180), 3)
    pygame.draw.arc(surf, IRON_HI,
                    pygame.Rect(pad.centerx - 5, pad.y - 6, 10, 12),
                    math.radians(20), math.radians(160), 1)
    # Lock body
    pygame.draw.rect(surf, DK_OUTLINE, pad.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, pad, IRON_HI, IRON_DARK, radius=2)
    # Keyhole
    pygame.draw.circle(surf, NEAR_BLACK, (pad.centerx, pad.centery), 2)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(pad.centerx - 1, pad.centery, 2, 3))

    _shake_lines(surf, cx, body.y - 4, w=BOX_W, color=(45, 28, 12))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 2 — DOMED PIRATE
# ════════════════════════════════════════════════════════════════════════════
# Curved/domed lid — the iconic round-top pirate chest you'd picture
# first. Closed. Two iron straps curving over the dome, one keyhole
# plate on the front. Slightly darker oak.

WOOD_DOME_HI   = (175, 120,  62)
WOOD_DOME_MID  = (128,  78,  36)
WOOD_DOME_DARK = ( 70,  38,  14)


def draw_domed_pirate(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _drop_shadow(surf, cx, body.bottom + 4, BOX_W)

    # Domed lid: half-ellipse rising above the body
    dome_rect = pygame.Rect(body.x - 2, body.y - DOMED_LID_H,
                            body.w + 4, DOMED_LID_H * 2)
    # Outline (slightly bigger ellipse behind)
    out_rect = dome_rect.inflate(4, 4)
    out_rect.y -= 2
    pygame.draw.ellipse(surf, DK_OUTLINE, out_rect)
    # Fill
    dome_layer = pygame.Surface((dome_rect.w, dome_rect.h), pygame.SRCALPHA)
    for y in range(dome_rect.h):
        t = y / max(1, dome_rect.h - 1)
        c = lerp_color(WOOD_DOME_HI, WOOD_DOME_MID, t) + (255,)
        dome_layer.fill(c, pygame.Rect(0, y, dome_rect.w, 1))
    mask = pygame.Surface(dome_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    dome_layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Clip to upper half of the ellipse only — that's the lid arc
    clip = pygame.Surface(dome_rect.size, pygame.SRCALPHA)
    clip.blit(dome_layer, (0, 0))
    clip.fill((0, 0, 0, 0),
              pygame.Rect(0, dome_rect.h // 2, dome_rect.w, dome_rect.h),
              special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(clip, dome_rect.topleft)

    # Seam
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(body.x, body.y - 1, body.w, 2))

    # Body
    pygame.draw.rect(surf, DK_OUTLINE, body.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, body, WOOD_DOME_MID, WOOD_DOME_DARK, radius=2)
    _wood_grain(surf, body, WOOD_DOME_DARK, n=3)

    # Two iron straps curving over the dome (just the arc segments)
    for sx in (body.x + 8, body.right - 13):
        # Strap goes from body bottom up over the dome and down again
        sw = 5
        # Body half
        body_strap = pygame.Rect(sx, body.y + 1, sw, body.h - 2)
        pygame.draw.rect(surf, IRON_DARK, body_strap)
        pygame.draw.rect(surf, IRON_BASE, body_strap.inflate(-2, 0))
        pygame.draw.line(surf, IRON_HI,
                         (body_strap.x + 1, body_strap.y),
                         (body_strap.x + 1, body_strap.bottom - 1), 1)
        # Dome half — arc traced over the dome
        cx_arc = dome_rect.centerx
        # Approximate the strap as a short vertical line on the dome
        # at the same x as the body strap
        for dy in range(0, DOMED_LID_H + 1):
            # ellipse equation to find x range at y
            a = dome_rect.w / 2
            b = DOMED_LID_H
            y_in_dome = DOMED_LID_H - dy
            if y_in_dome >= 0:
                # Determine if (sx, body.y - dy) is inside the dome shape
                rel_x = (sx + sw // 2) - cx_arc
                rel_y = y_in_dome
                if (rel_x / a) ** 2 + (rel_y / b) ** 2 <= 1:
                    pygame.draw.line(surf, IRON_DARK,
                                     (sx, body.y - dy),
                                     (sx + sw - 1, body.y - dy), 1)
                    pygame.draw.line(surf, IRON_BASE,
                                     (sx + 1, body.y - dy),
                                     (sx + sw - 2, body.y - dy), 1)

    _draw_corner_studs(surf, body)
    _draw_side_handles(surf, body, WOOD_DOME_DARK)

    # Central keyhole plate (oval brass)
    kh_cx, kh_cy = body.centerx, body.centery + 1
    pygame.draw.ellipse(surf, BRASS_DK,
                        pygame.Rect(kh_cx - 6, kh_cy - 5, 12, 10))
    pygame.draw.ellipse(surf, BRASS_BASE,
                        pygame.Rect(kh_cx - 5, kh_cy - 4, 10, 8))
    pygame.draw.line(surf, BRASS_HI, (kh_cx - 4, kh_cy - 3),
                     (kh_cx + 3, kh_cy - 3), 1)
    pygame.draw.circle(surf, NEAR_BLACK, (kh_cx, kh_cy - 1), 2)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(kh_cx - 1, kh_cy, 2, 3))

    _shake_lines(surf, cx, body.y - 6, w=BOX_W, color=(40, 24, 10))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 3 — PLANKED & STRAPPED
# ════════════════════════════════════════════════════════════════════════════
# Visible vertical wood planks (4 of them) bound by two horizontal iron
# bands with prominent rivets. "Shipwright built" look. Lighter wood
# than oak, more like driftwood-salt-cured pine.

WOOD_PINE_HI   = (200, 160, 100)
WOOD_PINE_MID  = (155, 115,  62)
WOOD_PINE_DARK = ( 95,  62,  28)


def draw_planked_strapped(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _drop_shadow(surf, cx, body.bottom + 4, BOX_W)

    # Flat lid
    lid = pygame.Rect(body.x - 2, body.y - LID_H, body.w + 4, LID_H)
    pygame.draw.rect(surf, DK_OUTLINE, lid.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, lid, WOOD_PINE_HI, WOOD_PINE_MID, radius=2)
    # Plank seams on the LID too
    for px in (lid.x + lid.w // 4, lid.centerx, lid.x + lid.w * 3 // 4):
        pygame.draw.line(surf, WOOD_PINE_DARK,
                         (px, lid.y + 2), (px, lid.bottom - 1), 1)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(body.x, body.y - 1, body.w, 2))

    # Body
    pygame.draw.rect(surf, DK_OUTLINE, body.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, body, WOOD_PINE_MID, WOOD_PINE_DARK, radius=2)

    # 4 vertical PLANK seams (with a tiny carved groove highlight)
    plank_w = body.w // 4
    for i in range(1, 4):
        gx = body.x + plank_w * i
        # Dark groove
        pygame.draw.line(surf, WOOD_PINE_DARK,
                         (gx, body.y + 2), (gx, body.bottom - 2), 1)
        # Faint highlight on one side of the groove
        pygame.draw.line(surf, WOOD_PINE_HI,
                         (gx + 1, body.y + 3), (gx + 1, body.bottom - 3), 1)
        # Tiny knot mark on one plank
        if i == 2:
            pygame.draw.circle(surf, WOOD_PINE_DARK,
                               (gx - 4, body.y + 9), 2)
            pygame.draw.circle(surf, NEAR_BLACK,
                               (gx - 4, body.y + 9), 1)

    # Two prominent iron bands (thicker than V1) with many rivets
    for by in (body.y + 3, body.bottom - 6):
        strap = pygame.Rect(body.x - 2, by, body.w + 4, 5)
        pygame.draw.rect(surf, IRON_DARK, strap)
        pygame.draw.rect(surf, IRON_BASE, strap.inflate(0, -2))
        pygame.draw.line(surf, IRON_HI,
                         (strap.x + 2, strap.y + 1),
                         (strap.right - 2, strap.y + 1), 1)
        # Rivet at every plank seam
        for plank_i in range(5):
            rx = body.x + plank_w * plank_i - (1 if plank_i in (0, 4) else 0)
            rx = max(body.x + 2, min(body.right - 2, rx))
            pygame.draw.circle(surf, IRON_DARK, (rx, by + 2), 2)
            pygame.draw.circle(surf, IRON_HI,   (rx, by + 2), 1)

    # Small padlock on the lid centre — hasp + lock
    hasp = pygame.Rect(lid.centerx - 4, lid.y + 4, 8, LID_H - 4)
    pygame.draw.rect(surf, IRON_DARK, hasp)
    pygame.draw.rect(surf, IRON_BASE, hasp.inflate(-2, -2))
    # Padlock body sits at the body's top under the hasp
    pad = pygame.Rect(body.centerx - 5, body.centery - 4, 10, 9)
    pygame.draw.arc(surf, IRON_DARK,
                    pygame.Rect(pad.centerx - 4, pad.y - 5, 8, 10),
                    math.radians(0), math.radians(180), 3)
    pygame.draw.rect(surf, DK_OUTLINE, pad.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, pad, IRON_HI, IRON_DARK, radius=2)
    pygame.draw.circle(surf, NEAR_BLACK, (pad.centerx, pad.centery), 2)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(pad.centerx - 1, pad.centery, 2, 3))

    _draw_side_handles(surf, body, WOOD_PINE_DARK)

    _shake_lines(surf, cx, body.y - 4, w=BOX_W, color=(60, 40, 20))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 4 — STUDDED BRASS
# ════════════════════════════════════════════════════════════════════════════
# Ornate: dark mahogany body covered in a regular grid of brass studs
# (3 rows × 5 cols) framing a central brass oval plate with a keyhole.
# Iron corner brackets. Smaller iron straps. "Captain's display chest"
# energy — fancier than the others.

WOOD_MAHO_HI   = (130,  80,  44)
WOOD_MAHO_MID  = ( 85,  46,  20)
WOOD_MAHO_DARK = ( 42,  20,   8)


def draw_studded_brass(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _drop_shadow(surf, cx, body.bottom + 4, BOX_W)

    # Flat lid
    lid = pygame.Rect(body.x - 2, body.y - LID_H, body.w + 4, LID_H)
    pygame.draw.rect(surf, DK_OUTLINE, lid.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, lid, WOOD_MAHO_HI, WOOD_MAHO_MID, radius=2)
    # Brass stud row across the lid
    for sx in range(lid.x + 4, lid.right - 3, 5):
        pygame.draw.circle(surf, BRASS_DK, (sx, lid.centery), 1, 0)
        pygame.draw.circle(surf, BRASS_HI, (sx, lid.centery - 1), 1, 0)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(body.x, body.y - 1, body.w, 2))

    # Body
    pygame.draw.rect(surf, DK_OUTLINE, body.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, body, WOOD_MAHO_MID, WOOD_MAHO_DARK, radius=2)

    # Iron L-shape corner brackets (4 corners)
    bracket_size = 6
    for ax, ay, signs in (
        (body.x, body.y, (1, 1)),
        (body.right - 1, body.y, (-1, 1)),
        (body.x, body.bottom - 1, (1, -1)),
        (body.right - 1, body.bottom - 1, (-1, -1)),
    ):
        sx, sy = signs
        pygame.draw.line(surf, IRON_DARK,
                         (ax, ay), (ax + sx * bracket_size, ay), 3)
        pygame.draw.line(surf, IRON_DARK,
                         (ax, ay), (ax, ay + sy * bracket_size), 3)
        pygame.draw.line(surf, IRON_HI,
                         (ax, ay), (ax + sx * bracket_size, ay), 1)
        pygame.draw.line(surf, IRON_HI,
                         (ax, ay), (ax, ay + sy * bracket_size), 1)

    # Grid of brass studs (3 rows × 5 cols) — but skip the centre where
    # the lock plate sits.
    inner = body.inflate(-12, -8)
    rows = 3
    cols = 5
    for r in range(rows):
        for c in range(cols):
            sx = inner.x + c * (inner.w // (cols - 1))
            sy = inner.y + r * (inner.h // (rows - 1))
            # Skip the 6 central cells where the lock plate lives
            if r == 1 and 1 <= c <= 3:
                continue
            pygame.draw.circle(surf, BRASS_DK, (sx, sy + 1), 2, 0)
            pygame.draw.circle(surf, BRASS_BASE, (sx, sy), 2, 0)
            pygame.draw.circle(surf, BRASS_HI, (sx, sy - 1), 1, 0)

    # Central brass oval lock plate
    lp = pygame.Rect(body.centerx - 9, body.centery - 5, 18, 11)
    pygame.draw.ellipse(surf, BRASS_DK, lp.inflate(2, 2))
    pygame.draw.ellipse(surf, BRASS_BASE, lp)
    pygame.draw.arc(surf, BRASS_HI, lp.inflate(-2, -2),
                    math.radians(180), math.radians(360), 1)
    # Keyhole
    pygame.draw.circle(surf, NEAR_BLACK, (lp.centerx, lp.centery - 1), 2)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(lp.centerx - 1, lp.centery, 2, 4))

    _draw_side_handles(surf, body, WOOD_MAHO_DARK)

    _shake_lines(surf, cx, body.y - 4, w=BOX_W, color=(30, 18,  8))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ════════════════════════════════════════════════════════════════════════════
# VARIANT 5 — SKULL-BRANDED
# ════════════════════════════════════════════════════════════════════════════
# Plain wooden box, no padlock or fancy hardware — just a burned/branded
# SKULL stamp scorched into the front face. The pirate's personal mark.
# Two thin iron bands, simple latch, leather wrap on one side. The
# threatening simplicity.

WOOD_BRAND_HI   = (170, 120,  68)
WOOD_BRAND_MID  = (118,  76,  38)
WOOD_BRAND_DARK = ( 62,  36,  14)
BRAND_BURN      = ( 22,  10,   4)


def draw_skull_branded(surf, bird_cx, bird_cy, t=0.0):
    cx = bird_cx + 4
    cy = bird_cy + 56
    body = _box_rect(cx, cy)

    _draw_carry_ropes(surf, bird_cx, bird_cy, body)
    _drop_shadow(surf, cx, body.bottom + 4, BOX_W)

    # Flat lid
    lid = pygame.Rect(body.x - 2, body.y - LID_H, body.w + 4, LID_H)
    pygame.draw.rect(surf, DK_OUTLINE, lid.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, lid, WOOD_BRAND_HI, WOOD_BRAND_MID, radius=2)
    pygame.draw.rect(surf, NEAR_BLACK,
                     pygame.Rect(body.x, body.y - 1, body.w, 2))

    # Body
    pygame.draw.rect(surf, DK_OUTLINE, body.inflate(2, 2), border_radius=2)
    _gradient_rect(surf, body, WOOD_BRAND_MID, WOOD_BRAND_DARK, radius=2)
    _wood_grain(surf, body, WOOD_BRAND_DARK, n=4)

    # Two thin iron straps near the top and bottom
    for by in (body.y + 3, body.bottom - 5):
        strap = pygame.Rect(body.x - 1, by, body.w + 2, 3)
        pygame.draw.rect(surf, IRON_DARK, strap)
        pygame.draw.rect(surf, IRON_HI, strap.inflate(0, -2), 0)

    # Branded SKULL stamp dead-centre on the body face.
    skull_cx = body.centerx
    skull_cy = body.centery + 1
    # Scorched halo (faint dark wash around the brand to suggest a burn)
    halo = pygame.Surface((20, 18), pygame.SRCALPHA)
    for rr in range(8, 4, -1):
        a = int(40 + (8 - rr) * 14)
        pygame.draw.circle(halo, (*BRAND_BURN, a), (10, 9), rr)
    surf.blit(halo, (skull_cx - 10, skull_cy - 9))

    # Skull silhouette — burned-in look, all near-black
    # Skull cap (circle)
    pygame.draw.circle(surf, BRAND_BURN, (skull_cx, skull_cy - 1), 5)
    # Jaw (small trapezoid)
    pygame.draw.polygon(surf, BRAND_BURN, [
        (skull_cx - 3, skull_cy + 3),
        (skull_cx + 3, skull_cy + 3),
        (skull_cx + 2, skull_cy + 6),
        (skull_cx - 2, skull_cy + 6),
    ])
    # Eye sockets (cut out of the burn — use the wood mid colour to
    # show that the wood is exposed where the burn didn't fully char)
    pygame.draw.circle(surf, WOOD_BRAND_MID, (skull_cx - 2, skull_cy - 1), 1)
    pygame.draw.circle(surf, WOOD_BRAND_MID, (skull_cx + 2, skull_cy - 1), 1)
    # Nose (tiny triangle)
    pygame.draw.polygon(surf, WOOD_BRAND_MID, [
        (skull_cx, skull_cy + 1),
        (skull_cx - 1, skull_cy + 3),
        (skull_cx + 1, skull_cy + 3),
    ])
    # Tooth gaps
    pygame.draw.line(surf, WOOD_BRAND_MID,
                     (skull_cx - 1, skull_cy + 4), (skull_cx - 1, skull_cy + 5), 1)
    pygame.draw.line(surf, WOOD_BRAND_MID,
                     (skull_cx + 1, skull_cy + 4), (skull_cx + 1, skull_cy + 5), 1)
    # Crossbones (X behind the skull, drawn first conceptually but on top here
    # so they show up against the body)
    pygame.draw.line(surf, BRAND_BURN,
                     (skull_cx - 7, skull_cy + 6), (skull_cx + 7, skull_cy + 5), 2)
    pygame.draw.line(surf, BRAND_BURN,
                     (skull_cx - 7, skull_cy + 5), (skull_cx + 7, skull_cy + 6), 2)
    # Tiny dots at the ends of the bones (bone knobs)
    for bx in (skull_cx - 7, skull_cx + 7):
        pygame.draw.circle(surf, BRAND_BURN, (bx, skull_cy + 5), 2)

    # Simple latch above the brand — just a small iron tongue across the seam
    latch = pygame.Rect(body.centerx - 3, body.y - 2, 6, 4)
    pygame.draw.rect(surf, IRON_DARK, latch)
    pygame.draw.rect(surf, IRON_BASE, latch.inflate(-2, -1))

    # Leather wrap on one side: a dark band wrapping the right corner
    wrap_pts = [
        (body.right - 3, body.y + 2),
        (body.right + 1, body.y + 4),
        (body.right + 1, body.bottom - 4),
        (body.right - 3, body.bottom - 2),
    ]
    pygame.draw.polygon(surf, (40, 22, 10), wrap_pts)
    pygame.draw.line(surf, (75, 45, 18),
                     (body.right - 2, body.y + 4),
                     (body.right - 2, body.bottom - 4), 1)
    # Stitch marks
    for sy in range(body.y + 6, body.bottom - 4, 3):
        pygame.draw.circle(surf, (200, 170, 120), (body.right - 1, sy), 1)

    _draw_side_handles(surf, body, WOOD_BRAND_DARK)

    _shake_lines(surf, cx, body.y - 4, w=BOX_W, color=(40, 24, 10))
    _spill_trail(surf, body.x - 4, body.y, side=-1)


# ── Registry ────────────────────────────────────────────────────────────────

VARIANTS = [
    ("padlocked_oak",    "PADLOCKED OAK",        draw_padlocked_oak),
    ("domed_pirate",     "DOMED PIRATE CHEST",   draw_domed_pirate),
    ("planked_strapped", "PLANKED & STRAPPED",   draw_planked_strapped),
    ("studded_brass",    "STUDDED BRASS",        draw_studded_brass),
    ("skull_branded",    "SKULL-BRANDED",        draw_skull_branded),
]
