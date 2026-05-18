"""Render 5 polished iterations of the V2 Wheel of Fortune reveal —
each tackling the "doesn't block gameplay" constraint differently.

Variants (all use clear numeric prize values + tick-peg pointer + gem
hub + bulb rim + drop shadow):

  v2a_corner    Small wheel tucked into top-right corner. Bird and
                pillar approach untouched. Most "HUD-y" of the five.
  v2b_glass     Original inline position but translucent — bird stays
                visible through a glass/holographic wheel.
  v2c_descend   Wheel hangs from the top of the screen; only the bottom
                half is visible (pointer up into the wheel). Big slice
                labels because the visible portion is wide.
  v2d_sidehalf  Half-wheel emerging from the left edge, pointer on the
                right side pointing into the screen. Player sees ~3
                slices around the winner at large size.
  v2e_podium    Wheel mounted on a marquee-and-stage podium anchored at
                the bottom of the screen, with a coin-tray result panel
                below the wheel.

Output:
  ./screenshots/v2a_corner.png ... v2e_podium.png   per-variant triptych
  ./screenshots/_wheel_iter_compare.png             5-up reveal-frame row
  ./screenshots/_wheel_iter_contact.png             stacked contact sheet

Run:
    python archive/lottery_design/render_v2_wheel_variants.py
"""
from __future__ import annotations

import math
import os
import pathlib
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE.parent.parent))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from archive.lottery_design.render_lottery_variants import (
    GOLD_BRIGHT, GOLD_DEEP, GOLD_PALE,
    RED_OUTLINE, RED_DEEP, ORANGE,
    PANEL_DARK, PANEL_MID, CREAM, NEAR_BLACK, WHITE,
    _font, _outlined_text, _outer_glow, _glow_circle, _confetti,
    _draw_backdrop, _draw_bird,
)


# ── tier ordering on the wheel (visually balanced: positive tiers
# alternate with negative so adjacent slices contrast). The order goes
# clockwise starting from the slice that will land under the pointer
# at the reveal — index 0 = JACKPOT for the mockups.
TIERS = (
    ("JACKPOT",  +100, GOLD_BRIGHT),
    ("WIN",       +15, (180, 210, 100)),
    ("LOSS",      -10, (210, 120,  80)),
    ("BIG WIN",   +40, (255, 170,  50)),
    ("NOTHING",     0, (180, 180, 195)),
    ("BUST",      -25, (190,  55,  45)),
)
N = len(TIERS)


def _value_str(v: int) -> str:
    if v > 0:
        return f"+{v}"
    if v < 0:
        return str(v)
    return "0"


# ── reusable wheel face builder ───────────────────────────────────────────────
def _build_wheel_face(radius: int, *, label_value=True,
                      bulb_count=16, t=1.0,
                      slice_alpha=255, rim_alpha=255) -> pygame.Surface:
    """Render a self-contained wheel face onto an SRCALPHA surface large
    enough to include rim bulbs. Caller rotates + blits it.

    label_value=True puts the prize value (+100, -25, ...) inside each
    slice as the primary label; False uses the tier name.
    """
    pad = 12
    size = radius * 2 + pad * 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2

    # Slices (pie wedges).
    for i, (name, value, col) in enumerate(TIERS):
        start = (-90 - 360 / N / 2 + i * 360 / N) * math.pi / 180
        end = start + (360 / N) * math.pi / 180
        pts = [(cx, cy)]
        steps = 36
        for k in range(steps + 1):
            a = start + (end - start) * k / steps
            pts.append((cx + math.cos(a) * radius,
                        cy + math.sin(a) * radius))
        slice_col = (*col, slice_alpha) if slice_alpha < 255 else col
        pygame.draw.polygon(s, slice_col, pts)

    # Slice separators (thin black radials).
    for i in range(N):
        a = (-90 - 360 / N / 2 + i * 360 / N) * math.pi / 180
        x2 = cx + math.cos(a) * radius
        y2 = cy + math.sin(a) * radius
        pygame.draw.aaline(s, (NEAR_BLACK[0], NEAR_BLACK[1], NEAR_BLACK[2], 200),
                           (cx, cy), (x2, y2))

    # Inner contrast disc (small, behind hub).
    pygame.draw.circle(s, (*PANEL_DARK, 220), (cx, cy), radius // 5 + 4)

    # Outer rim — double gold ring with bulbs.
    if rim_alpha > 0:
        pygame.draw.circle(s, (*GOLD_DEEP, rim_alpha), (cx, cy), radius + 3, 4)
        pygame.draw.circle(s, (*GOLD_BRIGHT, rim_alpha), (cx, cy), radius + 5, 1)
        pygame.draw.circle(s, (*GOLD_BRIGHT, rim_alpha), (cx, cy), radius - 1, 1)
        for i in range(bulb_count):
            ang = i * math.tau / bulb_count
            bx = cx + math.cos(ang) * (radius + 4)
            by = cy + math.sin(ang) * (radius + 4)
            on = (int(t * 12) + i) % 2 == 0
            col = GOLD_PALE if on else GOLD_DEEP
            pygame.draw.circle(s, (*col, rim_alpha), (int(bx), int(by)), 2)

    # Slice labels — drawn AT the slice's centre angle, rotated so the
    # text reads outward (radial). Skipped for slices behind the hub.
    for i, (name, value, col) in enumerate(TIERS):
        mid_ang = (-90 + i * 360 / N) * math.pi / 180
        label_r = radius - max(13, radius // 4)
        lx = cx + math.cos(mid_ang) * label_r
        ly = cy + math.sin(mid_ang) * label_r
        txt = _value_str(value) if label_value else (
            name[:3] if name != "NOTHING" else "NIL")
        # Bigger numeric prizes get bolder type.
        size_px = max(13, radius // 3)
        f = _font(size_px, True)
        # Black text on bright slices; white on dark slices.
        text_col = NEAR_BLACK if (sum(col) > 360) else WHITE
        # Outline for legibility on any background.
        out_col = WHITE if text_col == NEAR_BLACK else NEAR_BLACK
        img = f.render(txt, True, text_col)
        outline = f.render(txt, True, out_col)
        # Rotate so the text baseline runs along the radial direction.
        deg = -math.degrees(mid_ang) - 90
        img_r = pygame.transform.rotate(img, deg)
        out_r = pygame.transform.rotate(outline, deg)
        r = img_r.get_rect(center=(lx, ly))
        # Outline first.
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                if ox or oy:
                    s.blit(out_r, (r.x + ox, r.y + oy))
        s.blit(img_r, r.topleft)

    return s, cx, cy


def _draw_hub(surf, cx, cy, scale=1.0):
    """Polished jewel hub — dark base + gold ring + red gem + highlight."""
    r_base = max(6, int(8 * scale))
    pygame.draw.circle(surf, NEAR_BLACK, (cx, cy), r_base + 2)
    pygame.draw.circle(surf, GOLD_DEEP, (cx, cy), r_base + 1)
    pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), r_base, 2)
    pygame.draw.circle(surf, RED_DEEP, (cx, cy), max(3, int(4 * scale)))
    pygame.draw.circle(surf, (255, 150, 130),
                       (cx - 1, cy - 1), max(1, int(2 * scale)))


def _draw_pointer(surf, tip, length=14, tick_dx=0):
    """Triangle pointer with a small tick-peg that flicks sideways while
    the wheel ratchets past slice boundaries. tick_dx pushes the peg
    horizontally to suggest mid-tick."""
    px, py = tip
    pts = [
        (px, py),
        (px - 8, py - length),
        (px + 8, py - length),
    ]
    pygame.draw.polygon(surf, RED_OUTLINE, pts)
    pygame.draw.polygon(surf, GOLD_BRIGHT, pts, 1)
    # Highlight on left edge.
    pygame.draw.line(surf, GOLD_PALE,
                     (px - 7, py - length + 2), (px - 1, py - 1), 1)
    # Tick peg dangling from the pointer's base.
    peg_x = px + tick_dx
    pygame.draw.line(surf, GOLD_DEEP, (px, py - 2), (peg_x, py + 5), 2)
    pygame.draw.circle(surf, GOLD_BRIGHT, (peg_x, py + 5), 2)


def _draw_pointer_side(surf, tip, length=14, tick_dy=0):
    """Pointer pointing leftward (tip on right, base on left)."""
    px, py = tip
    pts = [
        (px, py),
        (px + length, py - 8),
        (px + length, py + 8),
    ]
    pygame.draw.polygon(surf, RED_OUTLINE, pts)
    pygame.draw.polygon(surf, GOLD_BRIGHT, pts, 1)
    peg_y = py + tick_dy
    pygame.draw.line(surf, GOLD_DEEP, (px + 2, py), (px - 5, peg_y), 2)
    pygame.draw.circle(surf, GOLD_BRIGHT, (px - 5, peg_y), 2)


def _spin_rotation(t: float) -> float:
    """Eased rotation profile: 3 full spins (integer so we land cleanly
    at 0 deg mod 360, keeping JACKPOT under the pointer). The per-variant
    rotation offset (added after this value) places JACKPOT at the
    variant's pointer location."""
    ease = 1 - (1 - t) ** 3
    return ease * (3.0 * 360.0)


def _tick_offset(t: float) -> float:
    """Approximate horizontal/vertical kick of the tick peg as wheel
    rotates past slice boundaries. Decays as rotation eases out."""
    if t > 0.95:
        return 0.0
    # Higher freq early, slower late.
    freq = 18 * (1 - t) ** 2 + 4
    return math.sin(t * freq * math.tau) * 3 * (1 - t)


def _result_banner(surf, center, width=170, height=22, text="JACKPOT +100",
                   text_color=GOLD_BRIGHT, fill=RED_DEEP):
    rect = pygame.Rect(0, 0, width, height)
    rect.center = center
    sh = pygame.Surface((rect.width + 4, rect.height + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 140),
                     (0, 0, rect.width + 4, rect.height + 4), border_radius=5)
    surf.blit(sh, (rect.x - 2, rect.y + 3))
    pygame.draw.rect(surf, fill, rect, border_radius=5)
    pygame.draw.rect(surf, GOLD_BRIGHT, rect, width=1, border_radius=5)
    _outlined_text(surf, text, rect.center,
                   max(14, height - 6),
                   fill=text_color, outline=NEAR_BLACK, px=1)


def _winning_callout(surf, slice_center, value, *, scale=1.0):
    """Crisp result label drawn ON TOP of the wheel right over the
    winning slice. Guarantees the prize is readable regardless of how
    the rotated radial slice label sits."""
    txt = _value_str(value)
    f = _font(int(22 * scale), True)
    img = f.render(txt, True, NEAR_BLACK)
    out = f.render(txt, True, GOLD_PALE)
    r = img.get_rect(center=slice_center)
    # Soft cream pill behind the text so it pops against any slice.
    pill = pygame.Rect(0, 0, r.width + 14, r.height + 4)
    pill.center = slice_center
    sh = pygame.Surface((pill.width + 4, pill.height + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 160),
                     (0, 0, pill.width + 4, pill.height + 4),
                     border_radius=pill.height // 2 + 1)
    surf.blit(sh, (pill.x - 2, pill.y + 2))
    pygame.draw.rect(surf, CREAM, pill,
                     border_radius=pill.height // 2)
    pygame.draw.rect(surf, RED_DEEP, pill, width=1,
                     border_radius=pill.height // 2)
    for ox in (-1, 0, 1):
        for oy in (-1, 0, 1):
            if ox or oy:
                surf.blit(out, (r.x + ox, r.y + oy))
    surf.blit(img, r.topleft)


# ─────────────────────────────────────────────────────────────────────────────
# v2a — Corner mini wheel
# ─────────────────────────────────────────────────────────────────────────────
def _v2a_corner(surf, t):
    cx, cy = W - 55, 64
    radius = 38

    # Subtle backdrop panel so the wheel reads against busy sky.
    backplate = pygame.Rect(0, 0, radius * 2 + 30, radius * 2 + 30)
    backplate.center = (cx, cy)
    bp = pygame.Surface(backplate.size, pygame.SRCALPHA)
    pygame.draw.rect(bp, (10, 6, 24, 170), bp.get_rect(), border_radius=12)
    pygame.draw.rect(bp, (*GOLD_DEEP, 200), bp.get_rect(), width=1,
                     border_radius=12)
    surf.blit(bp, backplate.topleft)

    face, fcx, fcy = _build_wheel_face(radius, t=t)
    rotated = pygame.transform.rotate(face, -_spin_rotation(t))
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))
    _draw_hub(surf, cx, cy, scale=0.85)
    _draw_pointer(surf, (cx, cy - radius - 4), length=10,
                  tick_dx=int(_tick_offset(t)))

    # "LOTTERY" mini-label below the wheel inside the panel.
    f = _font(11, True)
    lbl = f.render("LOTTERY", True, GOLD_BRIGHT)
    surf.blit(lbl, lbl.get_rect(center=(cx, backplate.bottom - 8)))

    # Reveal: outer ring glow, prize callout on the winning slice, and
    # the big result banner over centre-screen. Confetti spawns BELOW
    # the corner panel so it doesn't blot the wheel face.
    if t >= 0.92:
        _outer_glow(surf, (cx, cy), radius + 8, GOLD_PALE, alpha=180)
        _winning_callout(surf, (cx, cy - radius + 12), +100, scale=0.7)
        _result_banner(surf, (W // 2 - 30, int(H * 0.30)),
                       width=190, height=26, text="JACKPOT +100")
        _confetti(surf, cx, backplate.bottom + 6, (t - 0.92) * 8, seed=21)


# ─────────────────────────────────────────────────────────────────────────────
# v2b — Glass inline wheel (translucent over bird)
# ─────────────────────────────────────────────────────────────────────────────
def _v2b_glass(surf, t):
    cx, cy = 180, int(H * 0.36)
    radius = 55

    face, fcx, fcy = _build_wheel_face(radius, t=t, slice_alpha=170,
                                        rim_alpha=240)
    rotated = pygame.transform.rotate(face, -_spin_rotation(t))
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))

    # Glassy highlight — soft white arc on upper-left of the rim.
    hl = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(hl, (255, 255, 255, 70), (radius, radius),
                       radius - 2, 5)
    # Mask to a partial arc (upper-left).
    mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        ((0, 0), (radius * 2, 0), (radius, radius),
                         (0, radius * 2)))
    hl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hl, (cx - radius, cy - radius))

    _draw_hub(surf, cx, cy, scale=1.0)
    _draw_pointer(surf, (cx, cy - radius - 4), length=14,
                  tick_dx=int(_tick_offset(t)))

    if t >= 0.92:
        _outer_glow(surf, (cx, cy), radius + 10, GOLD_PALE, alpha=170)
        _winning_callout(surf, (cx, cy - radius + 14), +100, scale=0.85)
        _result_banner(surf, (cx, cy + radius + 24),
                       width=190, height=26, text="JACKPOT +100")
        # Confetti from below the wheel so the face stays clear.
        _confetti(surf, cx, cy + radius + 6, (t - 0.92) * 8, seed=37)


# ─────────────────────────────────────────────────────────────────────────────
# v2c — Top descend (only bottom half of wheel visible)
# ─────────────────────────────────────────────────────────────────────────────
def _v2c_descend(surf, t):
    radius = 78
    cx = 180
    cy = -6

    # Faux chains hanging from above.
    for chx in (cx - 60, cx + 60):
        for k in range(3):
            ky = -12 + k * 4
            pygame.draw.line(surf, GOLD_DEEP, (chx, ky), (chx, ky + 4), 2)

    face, _fcx, _fcy = _build_wheel_face(radius, t=t, bulb_count=20)
    # +180 puts JACKPOT slice at the bottom of the wheel where the
    # upward-pointing pointer sits.
    rotated = pygame.transform.rotate(face, -_spin_rotation(t) + 180)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))

    _draw_hub(surf, cx, cy, scale=1.2)

    # Pointer below the visible wheel arc, pointing up.
    tip_y = cy + radius + 6
    pts = [
        (cx, tip_y),
        (cx - 10, tip_y + 14),
        (cx + 10, tip_y + 14),
    ]
    pygame.draw.polygon(surf, RED_OUTLINE, pts)
    pygame.draw.polygon(surf, GOLD_BRIGHT, pts, 1)
    pygame.draw.line(surf, GOLD_PALE,
                     (cx - 9, tip_y + 12), (cx - 1, tip_y + 2), 1)
    peg_x = cx + int(_tick_offset(t))
    pygame.draw.line(surf, GOLD_DEEP, (cx, tip_y + 2),
                     (peg_x, tip_y - 5), 2)
    pygame.draw.circle(surf, GOLD_BRIGHT, (peg_x, tip_y - 5), 2)

    if t >= 0.92:
        _outer_glow(surf, (cx, cy + radius), radius // 2 + 6,
                    GOLD_PALE, alpha=160)
        _winning_callout(surf, (cx, cy + radius - 14), +100, scale=0.85)
        _result_banner(surf, (cx, cy + radius + 38),
                       width=200, height=28, text="JACKPOT +100")
        # Confetti from BELOW the visible wheel arc so the slice face stays clear.
        _confetti(surf, cx, cy + radius + 50, (t - 0.92) * 8, seed=41)


# ─────────────────────────────────────────────────────────────────────────────
# v2d — Side half wheel (emerges from left edge)
# ─────────────────────────────────────────────────────────────────────────────
def _v2d_sidehalf(surf, t):
    radius = 64
    # Wheel centre sits LEFT of the screen so only the right half shows.
    # Sized + positioned so the pointer tip lands clear of the bird's
    # x position (BIRD_X = 90).
    cx = -22
    cy = int(H * 0.38)

    face, _fcx, _fcy = _build_wheel_face(radius, t=t, bulb_count=20)
    # Pointer points leftward into the right edge of the visible half-
    # wheel; JACKPOT needs to be at 3 o'clock. Default places it at 12
    # o'clock so we add +90 (which visually moves it CW one quarter in
    # screen y-down coords).
    rotated = pygame.transform.rotate(face, -_spin_rotation(t) + 90)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))

    _draw_hub(surf, cx, cy, scale=1.2)

    # Pointer on the right side of the wheel, pointing leftward.
    tip_x = cx + radius + 6
    pts = [
        (tip_x, cy),
        (tip_x + 14, cy - 10),
        (tip_x + 14, cy + 10),
    ]
    pygame.draw.polygon(surf, RED_OUTLINE, pts)
    pygame.draw.polygon(surf, GOLD_BRIGHT, pts, 1)
    pygame.draw.line(surf, GOLD_PALE,
                     (tip_x + 12, cy - 9), (tip_x + 2, cy - 1), 1)
    peg_y = cy + int(_tick_offset(t))
    pygame.draw.line(surf, GOLD_DEEP, (tip_x + 2, cy),
                     (tip_x - 5, peg_y), 2)
    pygame.draw.circle(surf, GOLD_BRIGHT, (tip_x - 5, peg_y), 2)

    # Subtle vertical mount post on the left edge.
    pygame.draw.line(surf, GOLD_DEEP, (-2, cy - 40), (-2, cy + 40), 4)
    pygame.draw.line(surf, GOLD_BRIGHT, (0, cy - 40), (0, cy + 40), 1)

    if t >= 0.92:
        _outer_glow(surf, (cx + radius, cy), radius // 2 + 6,
                    GOLD_PALE, alpha=160)
        _winning_callout(surf, (cx + radius - 18, cy), +100, scale=0.85)
        _result_banner(surf, (180, cy + radius + 18),
                       width=200, height=28, text="JACKPOT +100")
        # Confetti from the RIGHT of the visible wheel.
        _confetti(surf, cx + radius + 30, cy, (t - 0.92) * 8, seed=53)


# ─────────────────────────────────────────────────────────────────────────────
# v2e — Bottom podium (mounted on a marquee-and-stage)
# ─────────────────────────────────────────────────────────────────────────────
def _v2e_podium(surf, t):
    radius = 46
    cx = 180
    # Anchor low — podium top sits near the ground line. Wheel centre
    # is above the podium.
    podium_top_y = int(H * 0.78)
    cy = podium_top_y - radius - 6

    # Podium / stage frame.
    stage = pygame.Rect(0, 0, 200, 70)
    stage.midtop = (cx, podium_top_y)
    sh = pygame.Surface((stage.width + 6, stage.height + 6), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 160),
                     (0, 0, stage.width + 6, stage.height + 6),
                     border_radius=8)
    surf.blit(sh, (stage.x - 3, stage.y + 4))
    pygame.draw.rect(surf, RED_DEEP, stage, border_radius=8)
    pygame.draw.rect(surf, GOLD_BRIGHT, stage, width=1, border_radius=8)
    inner = stage.inflate(-8, -8)
    pygame.draw.rect(surf, PANEL_DARK, inner, border_radius=6)
    pygame.draw.rect(surf, GOLD_DEEP, inner, width=1, border_radius=6)

    # Marquee above the wheel.
    marquee = pygame.Rect(0, 0, 110, 18)
    marquee.midbottom = (cx, cy - radius - 8)
    pygame.draw.rect(surf, RED_DEEP, marquee, border_radius=4)
    pygame.draw.rect(surf, GOLD_BRIGHT, marquee, width=1, border_radius=4)
    _outlined_text(surf, "LOTTERY", marquee.center, 16,
                   fill=GOLD_BRIGHT, outline=NEAR_BLACK, px=1)
    # Marquee bulbs.
    for i in range(7):
        bx = marquee.x + 8 + i * (marquee.width - 16) // 6
        by = marquee.y + 2
        on = (int(t * 8) + i) % 2 == 0
        pygame.draw.circle(surf, GOLD_PALE if on else GOLD_DEEP,
                           (bx, by), 1)

    # Wheel.
    face, _fcx, _fcy = _build_wheel_face(radius, t=t, bulb_count=16)
    rotated = pygame.transform.rotate(face, -_spin_rotation(t))
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))
    _draw_hub(surf, cx, cy, scale=1.0)
    _draw_pointer(surf, (cx, cy - radius - 4), length=12,
                  tick_dx=int(_tick_offset(t)))

    # Coin-tray result panel inside the podium.
    tray = inner.inflate(-10, -20)
    tray.height = 22
    tray.bottom = inner.bottom - 8
    pygame.draw.rect(surf, CREAM, tray, border_radius=4)
    pygame.draw.rect(surf, GOLD_DEEP, tray, width=1, border_radius=4)
    if t < 0.92:
        # "?" hint inside the tray until reveal.
        f = _font(16, True)
        for x in (tray.x + 18, tray.centerx, tray.right - 18):
            qimg = f.render("?", True, (80, 60, 30))
            surf.blit(qimg, qimg.get_rect(center=(x, tray.centery)))
    else:
        _outlined_text(surf, "JACKPOT +100", tray.center, 18,
                       fill=RED_DEEP, outline=GOLD_BRIGHT, px=1)
        _outer_glow(surf, (cx, cy), radius + 6, GOLD_PALE, alpha=150)
        _winning_callout(surf, (cx, cy - radius + 12), +100, scale=0.8)
        # Confetti spawns at the LEFT and RIGHT of the wheel, not over it,
        # so the winning slice label stays crisp.
        _confetti(surf, cx - radius - 10, cy, (t - 0.92) * 8, seed=67)
        _confetti(surf, cx + radius + 10, cy, (t - 0.92) * 8, seed=68)


# ─────────────────────────────────────────────────────────────────────────────
VARIANTS = (
    ("v2a_corner",   "Corner mini wheel",          _v2a_corner),
    ("v2b_glass",    "Glass inline (translucent)", _v2b_glass),
    ("v2c_descend",  "Top descend (bottom half)",  _v2c_descend),
    ("v2d_sidehalf", "Side half (right half)",     _v2d_sidehalf),
    ("v2e_podium",   "Bottom podium with tray",    _v2e_podium),
)

KEYFRAMES = (0.20, 0.65, 1.00)


def _render_frame(draw_fn, t) -> pygame.Surface:
    surf = pygame.Surface((W, H))
    _draw_backdrop(surf)
    _draw_bird(surf)
    draw_fn(surf, t)
    return surf


def _build_triptych(slug, label, draw_fn) -> pygame.Surface:
    pad = 6
    label_h = 22
    tri = pygame.Surface((W * 3 + pad * 4, H + label_h + pad * 2))
    tri.fill((18, 14, 28))
    bar = pygame.Surface((tri.get_width(), label_h), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 160))
    tri.blit(bar, (0, 0))
    tri.blit(_font(16, True).render(f"{slug}  —  {label}", True, GOLD_BRIGHT),
             (8, 4))
    for i, t in enumerate(KEYFRAMES):
        frame = _render_frame(draw_fn, t)
        x = pad + i * (W + pad)
        tri.blit(frame, (x, label_h + pad))
        kf_lbl = ("early spin", "settling", "reveal")[i]
        tri.blit(_font(13, True).render(kf_lbl, True, WHITE),
                 (x + 6, label_h + pad + H - 18))
    return tri


def _build_reveal_compare():
    pad = 6
    label_h = 28
    n = len(VARIANTS)
    sheet_w = pad + n * (W + pad)
    sheet_h = label_h + pad * 2 + H
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 8, 22))
    bar = pygame.Surface((sheet_w, label_h), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 200))
    sheet.blit(bar, (0, 0))
    sheet.blit(_font(18, True).render(
        "WHEEL — 5 placement iterations at JACKPOT reveal",
        True, GOLD_BRIGHT), (10, 5))
    for i, (slug, label, draw_fn) in enumerate(VARIANTS):
        frame = _render_frame(draw_fn, 1.0)
        tag = pygame.Surface((W, 18), pygame.SRCALPHA)
        tag.fill((0, 0, 0, 170))
        tag.blit(_font(13, True).render(slug, True, GOLD_PALE), (4, 2))
        frame.blit(tag, (0, 0))
        sheet.blit(frame, (pad + i * (W + pad), label_h + pad))
    return sheet


def _build_contact(triptychs):
    pad = 10
    scale = 0.55
    tw = int(triptychs[0].get_width() * scale)
    th = int(triptychs[0].get_height() * scale)
    sheet = pygame.Surface((tw + pad * 2, pad + (th + pad) * len(triptychs)))
    sheet.fill((10, 8, 22))
    for i, tri in enumerate(triptychs):
        scaled = pygame.transform.smoothscale(tri, (tw, th))
        sheet.blit(scaled, (pad, pad + i * (th + pad)))
    return sheet


def main():
    out = _HERE / "screenshots"
    out.mkdir(parents=True, exist_ok=True)
    # Don't wipe the original 5 mockups; only remove our own outputs.
    for slug, *_ in VARIANTS:
        p = out / f"{slug}.png"
        if p.exists():
            p.unlink()
    for fname in ("_wheel_iter_compare.png", "_wheel_iter_contact.png"):
        p = out / fname
        if p.exists():
            p.unlink()

    triptychs = []
    for slug, label, draw_fn in VARIANTS:
        tri = _build_triptych(slug, label, draw_fn)
        path = out / f"{slug}.png"
        pygame.image.save(tri, path)
        print(f"wrote {path}")
        triptychs.append(tri)

    pygame.image.save(_build_reveal_compare(), out / "_wheel_iter_compare.png")
    print(f"wrote {out / '_wheel_iter_compare.png'}")
    pygame.image.save(_build_contact(triptychs), out / "_wheel_iter_contact.png")
    print(f"wrote {out / '_wheel_iter_contact.png'}")


if __name__ == "__main__":
    main()
