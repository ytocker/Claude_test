"""Iterate v3a (top-left compact panel) with PROFESSIONAL number
typography on the wheel slices.

The current mockup renders prize values with the system default font and
a 1 px outline at small size — flat and amateurish. This iteration:

  - Switches to game/assets/LiberationSans-Bold.ttf (the same font the
    score plaque, coin counter, and float-text use), so the wheel
    matches the rest of the game's typography.
  - Applies the project's signature engraved-number treatment: warm
    cream face + tier-tinted rim layer + dark drop shadow. Same recipe
    as hud._score_plaque draws the FINAL SCORE numeral.
  - Tier-tints the rim instead of using a single colour: GOLD_DEEP for
    positive prizes, RED_DEEP for negatives, brown for zero. The cream
    face stays uniform so all numbers read as one type family.
  - Bumps the wheel radius from 36 -> 42 so the numerals have room to
    breathe at a size that the engraved layers actually look good at.
  - Drops a thin gold ring INSIDE the rim and a darker disc at the hub,
    giving the wheel face that "stamped brass" look.

Output a head-to-head comparison strip:

  ./screenshots/v3a_typography_compare.png   side-by-side: OLD vs NEW
  ./screenshots/v3a_pro.png                  the new triptych on its own

Run:
    python archive/lottery_design/render_v3a_typography.py
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
    RED_OUTLINE, RED_DEEP,
    PANEL_DARK, CREAM, NEAR_BLACK, WHITE,
    _outer_glow, _confetti,
    _draw_backdrop, _draw_bird,
)
from archive.lottery_design.render_v2_wheel_variants import (
    TIERS, _draw_hub, _draw_pointer,
    _spin_rotation, _tick_offset, _result_banner,
)


# ── typography ───────────────────────────────────────────────────────────────
_FONT_PATH = str(pathlib.Path(__file__).parent.parent.parent
                 / "game" / "assets" / "LiberationSans-Bold.ttf")
_pro_fonts: dict[int, pygame.font.Font] = {}


def _pro_font(size: int) -> pygame.font.Font:
    f = _pro_fonts.get(size)
    if f is None:
        f = pygame.font.Font(_FONT_PATH, size)
        _pro_fonts[size] = f
    return f


# Cream face (a touch warmer than the project's CREAM, matching the
# hud._score_plaque numerals at (252, 244, 220)).
_CREAM_FACE = (252, 244, 220)
# Tier-tinted rim colours: positives glow gold, negatives bleed red.
_RIM_GOLD = (180, 130, 30)
_RIM_RED  = (140, 25, 18)
_RIM_NEUTRAL = (110, 80, 30)


def _engraved_number(text: str, size: int, *,
                     rim: tuple[int, int, int] = _RIM_GOLD
                     ) -> pygame.Surface:
    """Three-pass engraved numeral, identical recipe to the score plaque:
        bottom : near-black drop shadow at (+1, +2), alpha 170
        middle : tier-tinted rim, offset (-1, -1)..(1, 1) eight-way
        top    : cream face

    Returned surface is SRCALPHA with the layers stacked. Caller is
    responsible for rotation if the slice needs radial orientation."""
    f = _pro_font(size)
    face = f.render(text, True, _CREAM_FACE)
    rim_layer = f.render(text, True, rim)
    shadow = f.render(text, True, NEAR_BLACK)

    pad = 5
    w = face.get_width() + pad * 2
    h = face.get_height() + pad * 2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # Drop shadow.
    shadow.set_alpha(170)
    surf.blit(shadow, (pad + 1, pad + 2))
    # Rim — soft 8-way 1 px outline.
    for ox in (-1, 0, 1):
        for oy in (-1, 0, 1):
            if ox or oy:
                surf.blit(rim_layer, (pad + ox, pad + oy))
    # Cream face on top.
    surf.blit(face, (pad, pad))
    return surf


def _rim_for_value(v: int) -> tuple[int, int, int]:
    if v > 0:
        return _RIM_GOLD
    if v < 0:
        return _RIM_RED
    return _RIM_NEUTRAL


def _value_str(v: int) -> str:
    if v > 0:
        return f"+{v}"
    if v < 0:
        return str(v)
    return "0"


# ── wheel face with PRO typography ──────────────────────────────────────────
def _build_pro_wheel_face(radius: int, *, t: float = 1.0,
                          bulb_count: int = 16) -> pygame.Surface:
    """Polished wheel face with engraved-numeral slice labels."""
    pad = 14
    size = radius * 2 + pad * 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    n = len(TIERS)

    # Slices.
    for i, (name, value, col) in enumerate(TIERS):
        start = (-90 - 360 / n / 2 + i * 360 / n) * math.pi / 180
        end = start + (360 / n) * math.pi / 180
        pts = [(cx, cy)]
        steps = 36
        for k in range(steps + 1):
            a = start + (end - start) * k / steps
            pts.append((cx + math.cos(a) * radius,
                        cy + math.sin(a) * radius))
        pygame.draw.polygon(s, col, pts)

    # Slice separators — thin near-black radial hairlines for the
    # "stamped brass" partition look.
    for i in range(n):
        a = (-90 - 360 / n / 2 + i * 360 / n) * math.pi / 180
        x2 = cx + math.cos(a) * radius
        y2 = cy + math.sin(a) * radius
        pygame.draw.aaline(s, (NEAR_BLACK[0], NEAR_BLACK[1], NEAR_BLACK[2], 220),
                           (cx, cy), (x2, y2))

    # Inner contrast disc behind the hub.
    pygame.draw.circle(s, (*PANEL_DARK, 230), (cx, cy), radius // 5 + 5)

    # Concentric inner ring — gives the face that "stamped" texture.
    pygame.draw.circle(s, (*GOLD_DEEP, 200), (cx, cy),
                       int(radius * 0.66), 1)

    # Outer rim: double gold ring + bulb stipple.
    pygame.draw.circle(s, GOLD_DEEP, (cx, cy), radius + 3, 4)
    pygame.draw.circle(s, GOLD_BRIGHT, (cx, cy), radius + 5, 1)
    pygame.draw.circle(s, GOLD_BRIGHT, (cx, cy), radius - 1, 1)
    for i in range(bulb_count):
        ang = i * math.tau / bulb_count
        bx = cx + math.cos(ang) * (radius + 4)
        by = cy + math.sin(ang) * (radius + 4)
        on = (int(t * 12) + i) % 2 == 0
        pygame.draw.circle(s, GOLD_PALE if on else GOLD_DEEP,
                           (int(bx), int(by)), 2)

    # Engraved numeral labels — rendered upright then rotated radially
    # so each label faces outward from the hub. At the top (-90) the
    # rotation is 0 → label reads horizontally, which is where the
    # JACKPOT slice always lands at reveal. Sized so they sit clear of
    # both the gold rim and the hub.
    label_r = int(radius * 0.62)
    label_size = max(14, int(radius * 0.38))
    for i, (name, value, col) in enumerate(TIERS):
        mid_ang_deg = -90 + i * 360 / n
        mid_ang = mid_ang_deg * math.pi / 180
        lx = cx + math.cos(mid_ang) * label_r
        ly = cy + math.sin(mid_ang) * label_r
        rim = _rim_for_value(value)
        img = _engraved_number(_value_str(value), label_size, rim=rim)
        # Rotate the entire engraved stack so cream/rim/shadow stay aligned.
        deg = -mid_ang_deg - 90
        rotated = pygame.transform.rotate(img, deg)
        s.blit(rotated, rotated.get_rect(center=(lx, ly)))

    return s


# ── pro winning-callout (matches the engraved style) ────────────────────────
def _pro_winning_callout(surf, slice_center, value, *, scale=1.0):
    """Engraved prize callout drawn over the winning slice. Same recipe
    as the slice numerals but on a cream pill so the prize pops over
    any tier colour."""
    txt = _value_str(value)
    size = int(24 * scale)
    img = _engraved_number(txt, size, rim=_RIM_GOLD)
    r = img.get_rect(center=slice_center)
    pill = pygame.Rect(0, 0, r.width + 8, r.height + 2)
    pill.center = slice_center

    sh = pygame.Surface((pill.width + 4, pill.height + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 180),
                     (0, 0, pill.width + 4, pill.height + 4),
                     border_radius=pill.height // 2 + 1)
    surf.blit(sh, (pill.x - 2, pill.y + 2))
    pygame.draw.rect(surf, _CREAM_FACE, pill,
                     border_radius=pill.height // 2)
    pygame.draw.rect(surf, _RIM_GOLD, pill, width=1,
                     border_radius=pill.height // 2)
    surf.blit(img, r.topleft)


def _pro_result_banner(surf, center, *, text="JACKPOT", value=+100,
                       width=190, height=30):
    """Two-line engraved banner: tier name on top, value below. Uses the
    same engraved typography as the slice labels for visual cohesion."""
    rect = pygame.Rect(0, 0, width, height)
    rect.center = center
    sh = pygame.Surface((rect.width + 4, rect.height + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 160),
                     (0, 0, rect.width + 4, rect.height + 4),
                     border_radius=6)
    surf.blit(sh, (rect.x - 2, rect.y + 3))
    pygame.draw.rect(surf, RED_DEEP, rect, border_radius=6)
    pygame.draw.rect(surf, GOLD_BRIGHT, rect, width=1, border_radius=6)
    # Top hairline.
    pygame.draw.line(surf, (255, 220, 140, 110),
                     (rect.x + 8, rect.y + 2),
                     (rect.right - 8, rect.y + 2), 1)

    # Tier name (smaller, top half).
    tname = pygame.font.Font(_FONT_PATH, 13).render(text, True, GOLD_PALE)
    tname_shadow = pygame.font.Font(_FONT_PATH, 13).render(text, True,
                                                            NEAR_BLACK)
    tname_shadow.set_alpha(180)
    tr = tname.get_rect(center=(rect.centerx, rect.y + 9))
    surf.blit(tname_shadow, (tr.x + 1, tr.y + 1))
    surf.blit(tname, tr.topleft)

    # Value (larger, bottom half, engraved).
    value_str = _value_str(value)
    value_img = _engraved_number(value_str, 20, rim=_RIM_GOLD)
    vr = value_img.get_rect(center=(rect.centerx, rect.y + 22))
    surf.blit(value_img, vr.topleft)


# ── v3a renderer (now with pro numbers) ─────────────────────────────────────
TL_CX = 64
TL_CY = 78


def _v3a_pro(surf, t):
    radius = 42
    cx, cy = TL_CX, TL_CY

    backplate = pygame.Rect(0, 0, radius * 2 + 30, radius * 2 + 30)
    backplate.center = (cx, cy)
    sh = pygame.Surface((backplate.width + 6, backplate.height + 6),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 160),
                     (0, 0, backplate.width + 6, backplate.height + 6),
                     border_radius=14)
    surf.blit(sh, (backplate.x - 3, backplate.y + 4))

    bp = pygame.Surface(backplate.size, pygame.SRCALPHA)
    pygame.draw.rect(bp, (10, 6, 24, 210), bp.get_rect(), border_radius=12)
    pygame.draw.rect(bp, (*GOLD_BRIGHT, 230), bp.get_rect(), width=1,
                     border_radius=12)
    pygame.draw.rect(bp, (*GOLD_DEEP, 140), bp.get_rect().inflate(-3, -3),
                     width=1, border_radius=10)
    # Top sheen on the panel — adds the "lacquered" feel.
    sheen = pygame.Surface((backplate.width, 12), pygame.SRCALPHA)
    for yy in range(12):
        a = int(40 * (1 - yy / 12))
        pygame.draw.line(sheen, (255, 240, 200, a),
                         (4, yy + 2), (backplate.width - 4, yy + 2))
    bp.blit(sheen, (0, 2))
    surf.blit(bp, backplate.topleft)

    face = _build_pro_wheel_face(radius, t=t, bulb_count=16)
    rotated = pygame.transform.rotate(face, -_spin_rotation(t))
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))
    _draw_hub(surf, cx, cy, scale=0.9)
    _draw_pointer(surf, (cx, cy - radius - 4), length=11,
                  tick_dx=int(_tick_offset(t)))

    # Footer slot inside the panel: shows "LOTTERY" during the spin and
    # flips to the tier name at reveal (the value is already on the
    # winning slice as a callout pill). Keeps the entire animation in
    # the top-left corner so the pillar lane (right side) stays clear.
    footer = pygame.Rect(0, 0, backplate.width - 14, 18)
    footer.midbottom = (cx, backplate.bottom - 5)
    if t < 0.92:
        lbl = _engraved_number("LOTTERY", 12, rim=_RIM_GOLD)
        surf.blit(lbl, lbl.get_rect(center=footer.center))
    else:
        # Cream pill backplate so the tier name pops.
        pygame.draw.rect(surf, _CREAM_FACE, footer,
                         border_radius=footer.height // 2)
        pygame.draw.rect(surf, _RIM_GOLD, footer, width=1,
                         border_radius=footer.height // 2)
        # Tier name only, large + engraved. The value sits on the slice.
        tname_img = _engraved_number("JACKPOT", 13, rim=_RIM_GOLD)
        surf.blit(tname_img, tname_img.get_rect(center=footer.center))

    if t >= 0.92:
        _outer_glow(surf, (cx, cy), radius + 8, GOLD_PALE, alpha=180)
        _pro_winning_callout(surf, (cx, cy - radius + 14), +100, scale=0.7)
        # Confetti spills BELOW the panel — never to the right where pillars
        # come from, never across centre-screen where the score lives.
        _confetti(surf, cx, backplate.bottom + 12, (t - 0.92) * 8, seed=21)


# ── OLD v3a (the previous render) for the head-to-head comparison ──────────
def _v3a_old(surf, t):
    from archive.lottery_design.render_v3_topleft_variants import _v3a_panel
    _v3a_panel(surf, t)


# ── rendering ───────────────────────────────────────────────────────────────
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
    hdr = pygame.font.Font(_FONT_PATH, 14).render(
        f"{slug}  -  {label}", True, GOLD_BRIGHT)
    tri.blit(hdr, (8, 4))
    for i, t in enumerate(KEYFRAMES):
        frame = _render_frame(draw_fn, t)
        x = pad + i * (W + pad)
        tri.blit(frame, (x, label_h + pad))
        kf = pygame.font.Font(_FONT_PATH, 12).render(
            ("early spin", "settling", "reveal")[i], True, WHITE)
        tri.blit(kf, (x + 6, label_h + pad + H - 18))
    return tri


def _build_zoomed_corner(draw_fn, label: str, t: float = 1.0) -> pygame.Surface:
    """Zoom on just the top-left panel for a numbers-side-by-side
    comparison. 4x scale of the (0..150, 0..150) area."""
    frame = _render_frame(draw_fn, t)
    crop = pygame.Rect(0, 0, 150, 150)
    sub = frame.subsurface(crop).copy()
    zoom = pygame.transform.scale(
        sub, (sub.get_width() * 4, sub.get_height() * 4))
    # Caption strip.
    caption_h = 26
    out = pygame.Surface((zoom.get_width(), zoom.get_height() + caption_h))
    out.fill((18, 14, 28))
    out.blit(zoom, (0, caption_h))
    hdr = pygame.font.Font(_FONT_PATH, 16).render(label, True, GOLD_BRIGHT)
    out.blit(hdr, (8, 5))
    return out


def main():
    out = _HERE / "screenshots"
    out.mkdir(parents=True, exist_ok=True)

    # Triptych for the new pro version.
    tri = _build_triptych("v3a_pro", "Top-left panel with PRO typography",
                          _v3a_pro)
    pygame.image.save(tri, out / "v3a_pro.png")
    print(f"wrote {out / 'v3a_pro.png'}")

    # Side-by-side OLD vs NEW zoom on the wheel itself, at reveal frame.
    old_zoom = _build_zoomed_corner(_v3a_old, "BEFORE  -  default font, thin outline",
                                    t=1.0)
    new_zoom = _build_zoomed_corner(_v3a_pro, "AFTER  -  LiberationSans-Bold, engraved",
                                    t=1.0)
    pad = 12
    cmp_w = old_zoom.get_width() + new_zoom.get_width() + pad * 3
    cmp_h = max(old_zoom.get_height(), new_zoom.get_height()) + pad * 2
    cmp_sheet = pygame.Surface((cmp_w, cmp_h))
    cmp_sheet.fill((10, 8, 22))
    cmp_sheet.blit(old_zoom, (pad, pad))
    cmp_sheet.blit(new_zoom, (pad * 2 + old_zoom.get_width(), pad))
    pygame.image.save(cmp_sheet, out / "v3a_typography_compare.png")
    print(f"wrote {out / 'v3a_typography_compare.png'}")


if __name__ == "__main__":
    main()
