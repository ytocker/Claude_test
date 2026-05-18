"""Render 5 MEGA MAGNET icon candidates next to the live regular Magnet.

The regular Magnet icon is rendered through the actual game code
(`game.entities.PowerUp` with `kind="magnet"`) so every comparison
sits next to the real in-game silhouette — no re-drawing.

Each Mega variant is a function that draws into a square cell at a
given center. We pair each variant with the live regular icon at a
matched pulse so the two read as the same instant of bob/crackle.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_mega_magnet_icon_candidates.py
"""

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

_OUT = os.path.join(_REPO, "docs", "mega_magnet_icons")
os.makedirs(_OUT, exist_ok=True)

pygame.init()
pygame.font.init()

from game.entities import PowerUp  # noqa: E402  — needs init first


# ── helpers ─────────────────────────────────────────────────────────────────


# Use the in-game sky-mid colour so every icon sits on the backdrop it
# actually ships against. Matches `game/draw.py:SKY_MID`.
SKY_BG = (25, 60, 130)


def draw_regular_magnet(surf, cx, cy, pulse):
    """Calls the live game renderer for the regular Magnet icon."""
    p = PowerUp(cx, cy, "magnet")
    p.pulse = pulse
    p.draw(surf)


# ── 5 mega variants ─────────────────────────────────────────────────────────


def _chrome_pole(surf, tip_cx, leg_bot, arm_w):
    """Reused chrome pole tip from _draw_magnet (entities.py:1408)."""
    pygame.draw.rect(surf, (40, 42, 60),
                     (tip_cx - arm_w // 2 - 1, leg_bot - 4, arm_w + 2, 9),
                     border_radius=4)
    pygame.draw.rect(surf, (195, 210, 232),
                     (tip_cx - arm_w // 2, leg_bot - 3, arm_w, 7),
                     border_radius=3)
    pygame.draw.rect(surf, (238, 246, 255),
                     (tip_cx - arm_w // 2 + 1, leg_bot - 3, arm_w - 2, 3),
                     border_radius=2)


def _horseshoe_body(surf, cx, arch_cy, leg_bot, outer_r, inner_r,
                    body_col=(235, 35, 45), shadow_col=(80, 5, 8),
                    hi_col=(255, 95, 95)):
    """Mirrors the regular _draw_magnet body construction at any size."""
    sz = (outer_r + 4) * 2 + max(0, leg_bot - arch_cy)
    scratch = pygame.Surface((sz, sz), pygame.SRCALPHA)
    scx = sz // 2
    scy = outer_r + 4
    # Shadow rim
    pygame.draw.circle(scratch, shadow_col, (scx, scy), outer_r + 2)
    pygame.draw.rect(scratch, shadow_col,
                     (scx - outer_r - 2, scy,
                      (outer_r + 2) * 2, leg_bot - arch_cy + 4))
    # Body
    pygame.draw.circle(scratch, body_col, (scx, scy), outer_r + 1)
    pygame.draw.rect(scratch, body_col,
                     (scx - outer_r - 1, scy,
                      (outer_r + 1) * 2, leg_bot - arch_cy + 3))
    # Highlight rings
    pygame.draw.circle(scratch, hi_col, (scx, scy), inner_r + 1, 2)
    pygame.draw.circle(scratch, hi_col, (scx, scy), outer_r, 2)
    # Punch hollow
    pygame.draw.circle(scratch, (0, 0, 0, 0), (scx, scy), inner_r)
    pygame.draw.rect(scratch, (0, 0, 0, 0),
                     (scx - inner_r, scy, inner_r * 2, sz - scy))
    surf.blit(scratch, (cx - scx, arch_cy - scy))


def _crackle(surf, cx, cy, pulse, count=2, span=8, thick=2):
    """Yellow-white lightning crackle around (cx, cy)."""
    YELLOW = (255, 220, 60)
    WHITE = (255, 250, 220)
    for i in range(count):
        ang = i * (math.tau / count) + pulse * 1.3
        pts = []
        for k in range(4):
            r = (k / 3) * span
            jit = math.sin(pulse * 9 + i + k) * 2
            pts.append((cx + math.cos(ang + jit * 0.1) * r,
                        cy + math.sin(ang + jit * 0.1) * r + jit))
        pygame.draw.lines(surf, YELLOW, False, pts, thick)
        pygame.draw.lines(surf, WHITE, False, pts, max(1, thick - 1))


# ── V1. SCALED UP — same silhouette, ~1.6× bigger, soft red glow halo ──────


def draw_mega_v1_scaled(surf, cx, cy, pulse):
    cy = cy + int(math.sin(pulse * 1.1) * 3)
    outer_r = 22
    inner_r = 10
    arch_cy = cy - 5
    leg_bot = cy + 22
    # Soft warm halo behind — width-1 rings stacked tight so the glow
    # reads as a continuous gradient rather than concentric bands.
    halo = pygame.Surface((120, 120), pygame.SRCALPHA)
    a_peak = 24 + int(10 * (0.5 + 0.5 * math.sin(pulse * 2)))
    halo_outer = outer_r + 22
    halo_inner = outer_r + 3
    for rr in range(halo_outer, halo_inner - 1, -1):
        falloff = (rr - halo_inner) / max(1, (halo_outer - halo_inner))
        a = int(a_peak * (1 - falloff) ** 1.6)
        if a > 0:
            pygame.draw.circle(halo, (255, 140, 60, a), (60, 60), rr, width=1)
    surf.blit(halo, (cx - 60, arch_cy - 60),
              special_flags=pygame.BLEND_RGBA_ADD)
    _horseshoe_body(surf, cx, arch_cy, leg_bot, outer_r, inner_r)
    arm_w = outer_r - inner_r
    left_cx = cx - inner_r - arm_w // 2
    right_cx = cx + inner_r + arm_w // 2
    _chrome_pole(surf, left_cx, leg_bot, arm_w)
    _chrome_pole(surf, right_cx, leg_bot, arm_w)
    # Lightning arc between poles, proportionally taller.
    arc_y0 = leg_bot + 8
    arc_pts = [(left_cx, arc_y0)]
    for i in range(1, 8):
        t = i / 8
        x = int(left_cx + (right_cx - left_cx) * t)
        y = int(arc_y0 + math.sin(pulse * 11 + i * 1.7) * 6)
        arc_pts.append((x, y))
    arc_pts.append((right_cx, arc_y0))
    pygame.draw.lines(surf, (100, 195, 255), False, arc_pts, 3)
    pygame.draw.lines(surf, (220, 240, 255), False, arc_pts, 1)
    # Two extra crackle plumes per pole
    for tip_cx in (left_cx, right_cx):
        _crackle(surf, tip_cx, leg_bot + 2, pulse, count=2, span=9, thick=2)


# ── V2. INDUSTRIAL — broader proportions, bolt-head studs, hazard stripe ────


def draw_mega_v2_industrial(surf, cx, cy, pulse):
    cy = cy + int(math.sin(pulse * 1.1) * 3)
    outer_r = 20
    inner_r = 11
    arch_cy = cy - 5
    leg_bot = cy + 22
    # Body with a darker, more "cast iron" red
    _horseshoe_body(surf, cx, arch_cy, leg_bot, outer_r, inner_r,
                    body_col=(200, 35, 40),
                    shadow_col=(45, 0, 5),
                    hi_col=(245, 110, 100))
    # Hazard stripes diagonally across the arch (3 short angled lines)
    for off in (-7, 0, 7):
        x0 = cx + off - 3
        y0 = arch_cy - outer_r + 6
        pygame.draw.line(surf, (245, 215, 30),
                         (x0, y0), (x0 + 6, y0 + 6), 2)
    # Bolt-head studs around the rim — 6 small dark circles
    for ang_deg in (135, 165, 195, 225, 255, 285):
        ang = math.radians(ang_deg)
        sx = cx + int(math.cos(ang) * (outer_r + 1))
        sy = arch_cy + int(math.sin(ang) * (outer_r + 1))
        pygame.draw.circle(surf, (35, 20, 25), (sx, sy), 2)
        pygame.draw.circle(surf, (155, 155, 165), (sx, sy), 1)
    # Chrome poles a bit wider
    arm_w = outer_r - inner_r
    left_cx = cx - inner_r - arm_w // 2
    right_cx = cx + inner_r + arm_w // 2
    _chrome_pole(surf, left_cx, leg_bot, arm_w + 2)
    _chrome_pole(surf, right_cx, leg_bot, arm_w + 2)
    # Single fat lightning arc
    arc_y0 = leg_bot + 6
    arc_pts = [(left_cx, arc_y0)]
    for i in range(1, 7):
        t = i / 7
        x = int(left_cx + (right_cx - left_cx) * t)
        y = int(arc_y0 + math.sin(pulse * 9 + i * 1.5) * 4)
        arc_pts.append((x, y))
    arc_pts.append((right_cx, arc_y0))
    pygame.draw.lines(surf, (100, 195, 255), False, arc_pts, 3)


# ── V3. TWIN-COIL ELECTROMAGNET — copper windings around each leg ──────────


def draw_mega_v3_twincoil(surf, cx, cy, pulse):
    cy = cy + int(math.sin(pulse * 1.1) * 3)
    outer_r = 20
    inner_r = 8
    arch_cy = cy - 5
    leg_bot = cy + 26
    _horseshoe_body(surf, cx, arch_cy, leg_bot, outer_r, inner_r)
    # Copper coil bands wrapping each leg.
    arm_w = outer_r - inner_r
    left_outer = cx - outer_r
    right_inner = cx + inner_r
    band_h = 3
    gap = 1
    band_n = 6
    leg_top = arch_cy + 1
    for i in range(band_n):
        by = leg_top + i * (band_h + gap)
        if by + band_h > leg_bot + 3:
            break
        # Left leg
        pygame.draw.rect(surf, (90, 45, 15),
                         (left_outer - 1, by, arm_w + 2, band_h))
        pygame.draw.rect(surf, (210, 130, 50),
                         (left_outer, by, arm_w, band_h - 1))
        pygame.draw.line(surf, (255, 200, 110),
                         (left_outer + 1, by),
                         (left_outer + arm_w - 2, by), 1)
        # Right leg
        pygame.draw.rect(surf, (90, 45, 15),
                         (right_inner - 1, by, arm_w + 2, band_h))
        pygame.draw.rect(surf, (210, 130, 50),
                         (right_inner, by, arm_w, band_h - 1))
        pygame.draw.line(surf, (255, 200, 110),
                         (right_inner + 1, by),
                         (right_inner + arm_w - 2, by), 1)
    # Wire connector arcing over the top of the arch
    wire_top = arch_cy - outer_r - 4
    pygame.draw.line(surf, (40, 25, 10), (cx - 10, wire_top + 1),
                     (cx + 10, wire_top + 1), 4)
    pygame.draw.line(surf, (210, 130, 50), (cx - 10, wire_top),
                     (cx + 10, wire_top), 2)
    # Chrome poles + arc
    left_cx = cx - inner_r - arm_w // 2
    right_cx = cx + inner_r + arm_w // 2
    _chrome_pole(surf, left_cx, leg_bot, arm_w)
    _chrome_pole(surf, right_cx, leg_bot, arm_w)
    arc_y0 = leg_bot + 7
    arc_pts = [(left_cx, arc_y0)]
    for i in range(1, 7):
        t = i / 7
        x = int(left_cx + (right_cx - left_cx) * t)
        y = int(arc_y0 + math.sin(pulse * 11 + i * 1.7) * 5)
        arc_pts.append((x, y))
    arc_pts.append((right_cx, arc_y0))
    pygame.draw.lines(surf, (100, 195, 255), False, arc_pts, 3)
    pygame.draw.lines(surf, (240, 250, 255), False, arc_pts, 1)


# ── V4. STACKED DOUBLE — two horseshoes layered for 3D depth ────────────────


def draw_mega_v4_stacked(surf, cx, cy, pulse):
    cy = cy + int(math.sin(pulse * 1.1) * 3)
    outer_r = 18
    inner_r = 8
    arch_cy = cy - 4
    leg_bot = cy + 20
    # Two horseshoes side by side, the right one offset back+right so
    # both silhouettes are clearly visible (not just a shadow stack).
    offset_x = outer_r + 4
    offset_y = 4
    # Back horseshoe — darker, behind
    _horseshoe_body(surf, cx + offset_x, arch_cy + offset_y,
                    leg_bot + offset_y,
                    outer_r, inner_r,
                    body_col=(170, 25, 30),
                    shadow_col=(45, 0, 0),
                    hi_col=(210, 80, 80))
    arm_w_back = outer_r - inner_r
    left_cx_b = (cx + offset_x) - inner_r - arm_w_back // 2
    right_cx_b = (cx + offset_x) + inner_r + arm_w_back // 2
    _chrome_pole(surf, left_cx_b, leg_bot + offset_y, arm_w_back)
    _chrome_pole(surf, right_cx_b, leg_bot + offset_y, arm_w_back)
    # Front horseshoe — vivid, slightly forward
    _horseshoe_body(surf, cx - offset_x // 2, arch_cy, leg_bot,
                    outer_r, inner_r,
                    body_col=(235, 35, 45),
                    shadow_col=(80, 5, 8),
                    hi_col=(255, 95, 95))
    arm_w = outer_r - inner_r
    left_cx = (cx - offset_x // 2) - inner_r - arm_w // 2
    right_cx = (cx - offset_x // 2) + inner_r + arm_w // 2
    _chrome_pole(surf, left_cx, leg_bot, arm_w)
    _chrome_pole(surf, right_cx, leg_bot, arm_w)
    # Lightning arc spanning BOTH magnets — outermost left pole to
    # outermost right pole, conveying "doubled field".
    arc_y0 = leg_bot + 8
    span_l, span_r = left_cx, right_cx_b
    arc_pts = [(span_l, arc_y0)]
    for i in range(1, 9):
        t = i / 9
        x = int(span_l + (span_r - span_l) * t)
        y = int(arc_y0 + math.sin(pulse * 11 + i * 1.4) * 6)
        arc_pts.append((x, y))
    arc_pts.append((span_r, arc_y0))
    pygame.draw.lines(surf, (100, 195, 255), False, arc_pts, 3)
    pygame.draw.lines(surf, (240, 250, 255), False, arc_pts, 1)
    # Crackle at each outer pole
    for tip in (left_cx, right_cx_b):
        _crackle(surf, tip, leg_bot + 2, pulse, count=2, span=8, thick=2)


# ── V5. PLASMA CROWN — orb between poles + radiating bolt corona ────────────


def draw_mega_v5_plasma(surf, cx, cy, pulse):
    cy = cy + int(math.sin(pulse * 1.1) * 3)
    outer_r = 19
    inner_r = 8
    arch_cy = cy - 5
    leg_bot = cy + 22
    # Body
    _horseshoe_body(surf, cx, arch_cy, leg_bot, outer_r, inner_r)
    arm_w = outer_r - inner_r
    left_cx = cx - inner_r - arm_w // 2
    right_cx = cx + inner_r + arm_w // 2
    _chrome_pole(surf, left_cx, leg_bot, arm_w)
    _chrome_pole(surf, right_cx, leg_bot, arm_w)
    # Plasma orb floating between the poles, breathing on pulse.
    orb_cy = leg_bot + 9
    orb_r = 6 + int(2 * math.sin(pulse * 3))
    orb = pygame.Surface((orb_r * 4, orb_r * 4), pygame.SRCALPHA)
    oc = (orb_r * 2, orb_r * 2)
    # Outer corona
    for i in range(8, 0, -1):
        a = int(140 * (1 - i / 8) ** 1.2)
        rr = int(orb_r * 2 * i / 8)
        col = (110, 200, 255) if i > 3 else (220, 240, 255)
        pygame.draw.circle(orb, (*col, a), oc, rr)
    # Hot core
    pygame.draw.circle(orb, (255, 255, 255, 240), oc, max(2, orb_r - 4))
    surf.blit(orb, (cx - orb_r * 2, orb_cy - orb_r * 2),
              special_flags=pygame.BLEND_RGBA_ADD)
    # Bolts from BOTH pole tips into the orb (electric leashes)
    for tip_cx in (left_cx, right_cx):
        jitter = math.sin(pulse * 13 + tip_cx) * 2
        pts = [
            (tip_cx, leg_bot + 1),
            (tip_cx + (cx - tip_cx) * 0.4, leg_bot + 5 + jitter),
            (cx, orb_cy - 2),
        ]
        pygame.draw.lines(surf, (110, 200, 255), False, pts, 3)
        pygame.draw.lines(surf, (240, 250, 255), False, pts, 1)
    # 8-direction bolt corona radiating from the magnet body
    for k in range(8):
        ang = k * (math.tau / 8) + pulse * 0.4
        r0 = outer_r + 2
        r1 = outer_r + 14 + int(3 * math.sin(pulse * 5 + k))
        x0 = cx + math.cos(ang) * r0
        y0 = arch_cy + math.sin(ang) * r0
        mx = cx + math.cos(ang) * (r0 + r1) * 0.55
        my = arch_cy + math.sin(ang) * (r0 + r1) * 0.55
        x1 = cx + math.cos(ang) * r1
        y1 = arch_cy + math.sin(ang) * r1
        jit_x = math.sin(pulse * 7 + k) * 1.5
        jit_y = math.cos(pulse * 7 + k) * 1.5
        pts = [(x0, y0), (mx + jit_x, my + jit_y), (x1, y1)]
        pygame.draw.lines(surf, (255, 220, 60), False, pts, 2)
        pygame.draw.lines(surf, (255, 250, 220), False, pts, 1)


# ── compositing ─────────────────────────────────────────────────────────────


VARIANTS = (
    ("v1_scaled",      "MEGA — Scaled Up",     draw_mega_v1_scaled),
    ("v2_industrial",  "MEGA — Industrial",    draw_mega_v2_industrial),
    ("v3_twincoil",    "MEGA — Twin-Coil",     draw_mega_v3_twincoil),
    ("v4_stacked",     "MEGA — Stacked Dual",  draw_mega_v4_stacked),
    ("v5_plasma",      "MEGA — Plasma Crown",  draw_mega_v5_plasma),
)


# Cell layout. Each comparison frame is 360×220:
#   [ regular | mega ] icons each in a 180×170 cell, with a label band
#   at the bottom (50 px) per cell.
CELL_W = 180
CELL_H = 170
BAND_H = 50
FRAME_W = CELL_W * 2
FRAME_H = CELL_H + BAND_H


def _cell_bg(cell):
    # Vertical sky gradient swatch — same colour family as `game/draw.py`
    # so each icon sits on the backdrop it actually ships against.
    top = (40, 90, 160)
    bot = (18, 45, 105)
    for y in range(CELL_H):
        t = y / max(1, CELL_H - 1)
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t))
        pygame.draw.line(cell, c, (0, y), (CELL_W, y))


def _label(surf, x, y, w, h, line1, line2=None):
    band = pygame.Surface((w, h), pygame.SRCALPHA)
    band.fill((0, 0, 0, 200))
    pygame.draw.line(band, (255, 215, 0), (0, 0), (w, 0), 1)
    f1 = pygame.font.SysFont(None, 22)
    t1 = f1.render(line1, True, (255, 240, 200))
    band.blit(t1, t1.get_rect(midtop=(w // 2, 6)))
    if line2:
        f2 = pygame.font.SysFont(None, 16)
        t2 = f2.render(line2, True, (180, 200, 220))
        band.blit(t2, t2.get_rect(midtop=(w // 2, 28)))
    surf.blit(band, (x, y))


def render_comparison(title, draw_mega):
    """One 360×220 side-by-side frame: regular vs this variant."""
    frame = pygame.Surface((FRAME_W, FRAME_H))
    # Two icon cells
    for ci, drawer in enumerate((
            lambda s, cx, cy: draw_regular_magnet(s, cx, cy, pulse=1.2),
            lambda s, cx, cy: draw_mega(s, cx, cy, pulse=1.2))):
        cell = pygame.Surface((CELL_W, CELL_H))
        _cell_bg(cell)
        # Icon centered horizontally, biased upward so lightning sits low
        drawer(cell, CELL_W // 2, CELL_H // 2 - 8)
        frame.blit(cell, (ci * CELL_W, 0))
    # Divider line between cells
    pygame.draw.line(frame, (10, 20, 40), (CELL_W, 0), (CELL_W, CELL_H), 2)
    # Labels
    _label(frame, 0, CELL_H, CELL_W, BAND_H,
           "REGULAR", "current magnet (game/entities.py)")
    _label(frame, CELL_W, CELL_H, CELL_W, BAND_H, title)
    return frame


def render_contact_sheet():
    """Single column: 5 comparison frames stacked vertically."""
    sheet = pygame.Surface((FRAME_W, FRAME_H * len(VARIANTS) + 2 * (len(VARIANTS) - 1)))
    sheet.fill((5, 10, 20))
    for i, (_slug, title, fn) in enumerate(VARIANTS):
        f = render_comparison(title, fn)
        sheet.blit(f, (0, i * (FRAME_H + 2)))
    return sheet


def main():
    for slug, title, fn in VARIANTS:
        f = render_comparison(title, fn)
        pygame.image.save(f, os.path.join(_OUT, f"{slug}.png"))
    sheet = render_contact_sheet()
    pygame.image.save(sheet, os.path.join(_OUT, "00_contact_sheet.png"))
    print(f"wrote {len(VARIANTS) + 1} images to {_OUT}")


if __name__ == "__main__":
    main()
