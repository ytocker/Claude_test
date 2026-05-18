"""Render 5 top-LEFT placements of the LOTTERY wheel.

Top-left keeps the player's forward gaze (right side — incoming pillars)
completely clear, and avoids the centre score plaque (W/2, y=92) and the
centred buff-timer bars (top_y=128 +). The coins pill sits at x=10..70,
y=14..44 — these variants place the wheel under or just right of it.

All five share the polished wheel face (gem hub, gold double-rim with
bulb stipple, tick-peg pointer, numeric prize values, crisp `+100`
callout on the winning slice at reveal). What differs is the framing.

Variants:
  v3a_panel       Wheel on a small dark gold-trimmed backplate, mirrored
                  v2a treatment into the top-left.
  v3b_hudstrip    Horizontal HUD ribbon along the top: wheel on the left
                  end, "LOTTERY" + prize banner extending to the right.
  v3c_floating    Wheel with only a soft drop shadow — no backplate.
                  Lowest visual weight.
  v3d_cabinet     Wheel inside a tiny slot-machine cabinet with a PRIZE
                  result window below. Most "arcade" of the five.
  v3e_chain       Wheel suspended from the top-left corner by a chain
                  with a sway during the spin.

Output:
  ./screenshots/v3{a..e}_*.png                    triptychs
  ./screenshots/_topleft_compare.png              5-up reveal row
  ./screenshots/_topleft_contact.png              stacked contact

Run:
    python archive/lottery_design/render_v3_topleft_variants.py
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
    _font, _outlined_text, _outer_glow, _confetti,
    _draw_backdrop, _draw_bird,
)
from archive.lottery_design.render_v2_wheel_variants import (
    TIERS, _build_wheel_face, _draw_hub, _draw_pointer,
    _spin_rotation, _tick_offset, _result_banner, _winning_callout,
)


# Anchor: the top-left area we want to occupy. Centred around (60, 75)
# leaves the coins pill (10..70, 14..44) untouched on most frames and
# stays well clear of the score plaque (W/2, 92) and buff timers
# (y >= 128). The wheel CAN briefly cover the coins counter during the
# 1 s reveal — that's acceptable for a once-in-a-while event.
TL_CX = 64
TL_CY = 76


# ─────────────────────────────────────────────────────────────────────────────
# v3a — Compact panel in top-left
# ─────────────────────────────────────────────────────────────────────────────
def _v3a_panel(surf, t):
    radius = 36
    cx, cy = TL_CX, TL_CY

    backplate = pygame.Rect(0, 0, radius * 2 + 28, radius * 2 + 28)
    backplate.center = (cx, cy)
    # Drop shadow.
    sh = pygame.Surface((backplate.width + 6, backplate.height + 6),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 150),
                     (0, 0, backplate.width + 6, backplate.height + 6),
                     border_radius=14)
    surf.blit(sh, (backplate.x - 3, backplate.y + 4))

    bp = pygame.Surface(backplate.size, pygame.SRCALPHA)
    pygame.draw.rect(bp, (10, 6, 24, 200), bp.get_rect(), border_radius=12)
    pygame.draw.rect(bp, (*GOLD_BRIGHT, 220), bp.get_rect(), width=1,
                     border_radius=12)
    pygame.draw.rect(bp, (*GOLD_DEEP, 140), bp.get_rect().inflate(-3, -3),
                     width=1, border_radius=10)
    surf.blit(bp, backplate.topleft)

    face, _fcx, _fcy = _build_wheel_face(radius, t=t, bulb_count=14)
    rotated = pygame.transform.rotate(face, -_spin_rotation(t))
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))
    _draw_hub(surf, cx, cy, scale=0.85)
    _draw_pointer(surf, (cx, cy - radius - 4), length=10,
                  tick_dx=int(_tick_offset(t)))

    # "LOTTERY" mini-label tucked into the panel bottom.
    lbl = _font(11, True).render("LOTTERY", True, GOLD_BRIGHT)
    surf.blit(lbl, lbl.get_rect(center=(cx, backplate.bottom - 8)))

    if t >= 0.92:
        _outer_glow(surf, (cx, cy), radius + 8, GOLD_PALE, alpha=180)
        _winning_callout(surf, (cx, cy - radius + 12), +100, scale=0.7)
        # Result banner appears in safe centre-right space, not over the
        # bird or pillar lane. Mid-screen height so it reads instantly.
        _result_banner(surf, (W // 2 + 30, int(H * 0.30)),
                       width=190, height=26, text="JACKPOT +100")
        # Confetti spills BELOW the panel toward the bird-free margin.
        _confetti(surf, cx, backplate.bottom + 12, (t - 0.92) * 8, seed=21)


# ─────────────────────────────────────────────────────────────────────────────
# v3b — HUD ribbon strip across the top
# ─────────────────────────────────────────────────────────────────────────────
def _v3b_hudstrip(surf, t):
    # Strip starts at the very top-left, extends across the upper area.
    # Score plaque centre is (W/2, 92) so the strip stays above y=64.
    strip = pygame.Rect(6, 50, 240, 44)

    # Shadow + body.
    sh = pygame.Surface((strip.width + 6, strip.height + 6),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 140),
                     (0, 0, strip.width + 6, strip.height + 6),
                     border_radius=12)
    surf.blit(sh, (strip.x - 3, strip.y + 4))
    pygame.draw.rect(surf, (10, 6, 24), strip, border_radius=12)
    pygame.draw.rect(surf, GOLD_BRIGHT, strip, width=1, border_radius=12)
    # Top hairline sheen.
    pygame.draw.line(surf, (255, 220, 140, 100),
                     (strip.x + 8, strip.y + 2),
                     (strip.right - 8, strip.y + 2), 1)

    # Wheel on the left end (smaller — strip is 44 tall).
    radius = 18
    wcx = strip.x + 4 + radius + 2
    wcy = strip.centery
    face, _fcx, _fcy = _build_wheel_face(radius, t=t, bulb_count=10)
    rotated = pygame.transform.rotate(face, -_spin_rotation(t))
    surf.blit(rotated, rotated.get_rect(center=(wcx, wcy)))
    _draw_hub(surf, wcx, wcy, scale=0.6)
    _draw_pointer(surf, (wcx, wcy - radius - 2), length=7,
                  tick_dx=int(_tick_offset(t) * 0.6))

    # Right side of the strip: header + result text.
    text_x = wcx + radius + 12
    hdr = _font(13, True).render("LOTTERY", True, GOLD_BRIGHT)
    surf.blit(hdr, (text_x, strip.y + 4))

    if t >= 0.92:
        result = _font(20, True).render("JACKPOT +100", True, GOLD_PALE)
        out = _font(20, True).render("JACKPOT +100", True, RED_DEEP)
        rect = result.get_rect(midleft=(text_x, strip.y + 30))
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                if ox or oy:
                    surf.blit(out, (rect.x + ox, rect.y + oy))
        surf.blit(result, rect.topleft)
        # Soft glow under the result.
        _outer_glow(surf, (wcx, wcy), radius + 6, GOLD_PALE, alpha=160)
        _winning_callout(surf, (wcx, wcy - radius + 8), +100, scale=0.55)
        # Confetti from the right end of the strip.
        _confetti(surf, strip.right + 8, strip.centery,
                  (t - 0.92) * 8, seed=33)
    else:
        # Three "?" ticks where the result will appear, hinting the slot.
        for i, qx in enumerate((text_x + 14, text_x + 44, text_x + 74)):
            q = _font(20, True).render("?", True, GOLD_DEEP)
            surf.blit(q, q.get_rect(center=(qx, strip.y + 28)))


# ─────────────────────────────────────────────────────────────────────────────
# v3c — Floating minimal (no panel)
# ─────────────────────────────────────────────────────────────────────────────
def _v3c_floating(surf, t):
    radius = 38
    cx, cy = TL_CX + 4, TL_CY + 4

    # Soft shadow under the wheel — no panel.
    shadow_layer = pygame.Surface((radius * 2 + 24, radius * 2 + 24),
                                  pygame.SRCALPHA)
    for k in range(6):
        a = max(0, 70 - k * 10)
        pygame.draw.circle(shadow_layer, (0, 0, 0, a),
                           (radius + 12, radius + 14 + k),
                           radius + 4 + k)
    surf.blit(shadow_layer, (cx - radius - 12, cy - radius - 12))

    face, _fcx, _fcy = _build_wheel_face(radius, t=t, bulb_count=14)
    rotated = pygame.transform.rotate(face, -_spin_rotation(t))
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))
    _draw_hub(surf, cx, cy, scale=0.9)
    _draw_pointer(surf, (cx, cy - radius - 4), length=10,
                  tick_dx=int(_tick_offset(t)))

    # No backplate — just an outlined LOTTERY label floating below.
    if t < 0.92:
        _outlined_text(surf, "LOTTERY", (cx, cy + radius + 14), 13,
                       fill=GOLD_BRIGHT, outline=NEAR_BLACK, px=1)

    if t >= 0.92:
        _outer_glow(surf, (cx, cy), radius + 8, GOLD_PALE, alpha=180)
        _winning_callout(surf, (cx, cy - radius + 12), +100, scale=0.7)
        _result_banner(surf, (cx + 30, cy + radius + 22),
                       width=170, height=26, text="JACKPOT +100")
        _confetti(surf, cx, cy + radius + 18, (t - 0.92) * 8, seed=29)


# ─────────────────────────────────────────────────────────────────────────────
# v3d — Mini slot-machine cabinet
# ─────────────────────────────────────────────────────────────────────────────
def _v3d_cabinet(surf, t):
    cabinet = pygame.Rect(0, 0, 110, 130)
    cabinet.center = (TL_CX + 4, TL_CY + 12)

    # Drop shadow.
    sh = pygame.Surface((cabinet.width + 6, cabinet.height + 6),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 160),
                     (0, 0, cabinet.width + 6, cabinet.height + 6),
                     border_radius=10)
    surf.blit(sh, (cabinet.x - 3, cabinet.y + 4))

    # Cabinet body — red outer / gold middle / dark inner.
    pygame.draw.rect(surf, RED_OUTLINE, cabinet, border_radius=10)
    pygame.draw.rect(surf, GOLD_DEEP, cabinet.inflate(-4, -4),
                     border_radius=8)
    pygame.draw.rect(surf, PANEL_DARK, cabinet.inflate(-10, -10),
                     border_radius=6)

    # Marquee strip at top.
    marquee = pygame.Rect(cabinet.x + 6, cabinet.y + 6,
                          cabinet.width - 12, 16)
    pygame.draw.rect(surf, RED_DEEP, marquee, border_radius=3)
    pygame.draw.rect(surf, GOLD_BRIGHT, marquee, width=1, border_radius=3)
    for i in range(6):
        bx = marquee.x + 6 + i * (marquee.width - 12) // 5
        on = (int(t * 8) + i) % 2 == 0
        pygame.draw.circle(surf, GOLD_PALE if on else GOLD_DEEP,
                           (bx, marquee.y + 3), 1)
    _outlined_text(surf, "LOTTERY", marquee.center, 13,
                   fill=GOLD_BRIGHT, outline=NEAR_BLACK, px=1)

    # Wheel inside the cabinet, upper portion.
    radius = 28
    wcx = cabinet.centerx
    wcy = marquee.bottom + radius + 6
    face, _fcx, _fcy = _build_wheel_face(radius, t=t, bulb_count=12)
    rotated = pygame.transform.rotate(face, -_spin_rotation(t))
    surf.blit(rotated, rotated.get_rect(center=(wcx, wcy)))
    _draw_hub(surf, wcx, wcy, scale=0.75)
    _draw_pointer(surf, (wcx, wcy - radius - 3), length=8,
                  tick_dx=int(_tick_offset(t) * 0.7))

    # Result window below the wheel.
    window = pygame.Rect(0, 0, cabinet.width - 16, 18)
    window.midbottom = (cabinet.centerx, cabinet.bottom - 6)
    pygame.draw.rect(surf, CREAM, window, border_radius=4)
    pygame.draw.rect(surf, GOLD_DEEP, window, width=1, border_radius=4)
    if t < 0.92:
        f = _font(14, True)
        for x in (window.x + 12, window.centerx, window.right - 12):
            q = f.render("?", True, (80, 60, 30))
            surf.blit(q, q.get_rect(center=(x, window.centery)))
    else:
        _outlined_text(surf, "JACKPOT +100", window.center, 14,
                       fill=RED_DEEP, outline=GOLD_BRIGHT, px=1)

    if t >= 0.92:
        _outer_glow(surf, (wcx, wcy), radius + 6, GOLD_PALE, alpha=160)
        _winning_callout(surf, (wcx, wcy - radius + 10), +100, scale=0.55)
        # Confetti out to the right of the cabinet, into safe airspace.
        _confetti(surf, cabinet.right + 12, cabinet.centery,
                  (t - 0.92) * 8, seed=39)


# ─────────────────────────────────────────────────────────────────────────────
# v3e — Hanging from the corner by a chain
# ─────────────────────────────────────────────────────────────────────────────
def _v3e_chain(surf, t):
    radius = 32
    # Sway during the spin: small horizontal offset that easings to 0.
    sway = math.sin(t * 6) * 5 * (1 - t) ** 2
    cx = TL_CX + int(sway)
    cy = TL_CY + 6

    # Chain anchored at the top-left corner, snaking down to the wheel.
    anchor = (12, 8)
    # Draw a few chain links as small circles + connecting lines.
    chain_pts = []
    n_links = 6
    for k in range(n_links + 1):
        u = k / n_links
        # Bezier-ish path: pull the chain toward the wheel top.
        bx = anchor[0] + (cx - anchor[0]) * u
        by = anchor[1] + (cy - radius - 6 - anchor[1]) * u + math.sin(u * 3.14) * 4
        chain_pts.append((bx, by))
    for k in range(len(chain_pts) - 1):
        pygame.draw.line(surf, GOLD_DEEP, chain_pts[k], chain_pts[k + 1], 3)
        pygame.draw.line(surf, GOLD_BRIGHT, chain_pts[k], chain_pts[k + 1], 1)
    for px, py in chain_pts:
        pygame.draw.circle(surf, GOLD_DEEP, (int(px), int(py)), 3)
        pygame.draw.circle(surf, GOLD_PALE, (int(px) - 1, int(py) - 1), 1)
    # Anchor knob.
    pygame.draw.circle(surf, RED_DEEP, anchor, 4)
    pygame.draw.circle(surf, GOLD_BRIGHT, anchor, 4, 1)

    # Top mount on the wheel (small ring).
    mount_y = cy - radius - 5
    pygame.draw.circle(surf, GOLD_DEEP, (cx, mount_y), 3)
    pygame.draw.circle(surf, GOLD_BRIGHT, (cx, mount_y), 3, 1)

    face, _fcx, _fcy = _build_wheel_face(radius, t=t, bulb_count=12)
    rotated = pygame.transform.rotate(face, -_spin_rotation(t))
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))
    _draw_hub(surf, cx, cy, scale=0.8)
    _draw_pointer(surf, (cx, cy - radius - 4), length=9,
                  tick_dx=int(_tick_offset(t) * 0.7))

    if t >= 0.92:
        _outer_glow(surf, (cx, cy), radius + 8, GOLD_PALE, alpha=180)
        _winning_callout(surf, (cx, cy - radius + 10), +100, scale=0.65)
        _result_banner(surf, (cx + 40, cy + radius + 22),
                       width=170, height=26, text="JACKPOT +100")
        _confetti(surf, cx, cy + radius + 16, (t - 0.92) * 8, seed=47)


# ─────────────────────────────────────────────────────────────────────────────
VARIANTS = (
    ("v3a_panel",     "Top-left compact panel",  _v3a_panel),
    ("v3b_hudstrip",  "HUD ribbon across top",   _v3b_hudstrip),
    ("v3c_floating",  "Floating (no panel)",     _v3c_floating),
    ("v3d_cabinet",   "Mini slot cabinet",       _v3d_cabinet),
    ("v3e_chain",     "Hanging by chain",        _v3e_chain),
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
        "WHEEL — top-left placements at JACKPOT reveal",
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
    for slug, *_ in VARIANTS:
        p = out / f"{slug}.png"
        if p.exists():
            p.unlink()
    for fname in ("_topleft_compare.png", "_topleft_contact.png"):
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

    pygame.image.save(_build_reveal_compare(), out / "_topleft_compare.png")
    print(f"wrote {out / '_topleft_compare.png'}")
    pygame.image.save(_build_contact(triptychs), out / "_topleft_contact.png")
    print(f"wrote {out / '_topleft_contact.png'}")


if __name__ == "__main__":
    main()
