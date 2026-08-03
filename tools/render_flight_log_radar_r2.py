#!/usr/bin/env python3
"""
radar round 2 — COMMAND RADAR (revised per art-director critique).

Changes from round 1:
  1. Post-death hairline → GOLD@18, dashed 3-on-5-off = projected track, not flown
  2. DAY COMPLETE moves off the trace row → terminus tick + right-rail label at top-right
     corner of scope frame; arrowhead removed
  3. Death reticle → clear 22×22 ink cell first, then draw GOLD@100 corner brackets
     re-registered at ±11px; no INK outline
  4. Contacts → GOLD@75 ring + GOLD@100 1px center pip; RAIN & CLOWN get broken ring;
     GEYSER nudged to x≈91 (8px right of x=83)
  5. ENDED HERE callout → square-cornered ink plate, 1px GOLD@60 left rule inside border,
     right-angle leader (horizontal then vertical), plate tied to crosshair
  6. Persistence → 4–6px forward bloom past sweep head fading to zero;
     vertical envelope tightened to ±90px around trace row
  7. ALTITUDE BAND → rotated left-rail label
  8. DAY COMPLETE terminus label pulled 20px from right canvas edge
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color, lerp_color_multi

W, H = 360, 640
SS = 3
ROOT = "/home/user/skybit"
FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
INK = (6, 8, 14)
GOLD = (255, 206, 92)
CREAM = (246, 240, 230)
SCRIM = (26, 22, 34)

_fonts: dict = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


# ── text / chrome helpers ────────────────────────────────────────────────────

def text(surf, s, size, center=None, midleft=None, midright=None,
         color=CREAM, shadow=(0, 0, 0, 150), track=0):
    f = font(size)
    if track:
        glyphs = [f.render(ch, True, color) for ch in s]
        tw = sum(g.get_width() for g in glyphs) + track * (len(s) - 1)
        th = f.get_height()
        img = pygame.Surface((max(1, tw), th), pygame.SRCALPHA)
        x = 0
        for ch, g in zip(s, glyphs):
            img.blit(g, (x, 0))
            x += g.get_width() + track
    else:
        img = f.render(s, True, color)
    rect = img.get_rect()
    if center:
        rect.center = center
    elif midleft:
        rect.midleft = midleft
    elif midright:
        rect.midright = midright
    if shadow:
        sh = img.copy()
        sh.fill((*shadow[:3], 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow[3])
        surf.blit(sh, (rect.x + 1, rect.y + 1))
    surf.blit(img, rect)
    return rect


def soft_glow(radius, color, peak=110, falloff=2.0):
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        f = (1 - (r / radius) ** falloff) * (peak / 255.0)
        s_col = (int(color[0] * f), int(color[1] * f), int(color[2] * f), 255)
        pygame.draw.circle(s, s_col, (c, c), r)
    return s


def alpha_line(surf, rgba, p0, p1, width=1):
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


def gold_a(a):
    return lerp_color(INK, GOLD, max(0, min(255, a)) / 255.0)


DIM_GOLD = gold_a(198)
LABEL_GOLD = gold_a(80)

# ── run + scope geometry ─────────────────────────────────────────────────────

DEATH_PHASE = 0.184
DEATH_PILLAR = 25
DAY_N = 1
TIME_ALIVE = 47
PHASE_LABEL = "DAY"

SX0, SY0 = 26, 150
SX1, SY1 = 334, 486
SW, SH = SX1 - SX0, SY1 - SY0    # 308 × 336

ALT_TOP, ALT_BOT = SY0 + 40, SY1 - 20


def px(p):
    return SX0 + max(0.0, min(1.0, p)) * SW


def py(alt):
    return ALT_BOT - max(0.0, min(1.0, alt)) * (ALT_BOT - ALT_TOP)


DEATH_X = px(DEATH_PHASE)          # ≈ 82.7
TRACE_ALT = 0.42
TRACE_Y = int(round(py(TRACE_ALT)))

# GEYSER nudged 8px right of x=83 → p≈0.186 maps to x≈83, so nudge to x≈91 → p≈0.210
CONTACTS = [
    ("GEYSER",    0.210, 0.72,  9, "above"),   # nudged 8px right from original
    ("CLOWN",     0.403, 0.30,  6, "below"),
    ("RAIN",      0.430, 0.55,  4, "above"),
    ("SNOWSTORM", 0.820, 0.85, 11, "below"),
]

# Contacts near death point: RAIN & CLOWN get broken ring
NEAR_DEATH = {"RAIN", "CLOWN"}


# ── scope furniture ──────────────────────────────────────────────────────────

def draw_scope_frame(surf):
    alpha_line(surf, (*GOLD, 70), (SX0, SY0), (SX1, SY0))
    alpha_line(surf, (*GOLD, 70), (SX0, SY1), (SX1, SY1))
    alpha_line(surf, (*GOLD, 70), (SX0, SY0), (SX0, SY1))
    alpha_line(surf, (*GOLD, 70), (SX1, SY0), (SX1, SY1))

    t = 9
    for cx, cy, sx, sy in ((SX0, SY0, 1, 1), (SX1, SY0, -1, 1),
                           (SX0, SY1, 1, -1), (SX1, SY1, -1, -1)):
        alpha_line(surf, (*GOLD, 165), (cx, cy), (cx + sx * t, cy))
        alpha_line(surf, (*GOLD, 165), (cx, cy), (cx, cy + sy * t))

    # DAY COMPLETE terminus tick at top-right corner of scope frame (critique #2)
    # A short horizontal tick at SX1, SY0+offset to mark the day's far end
    tick_y = SY0 + 20
    alpha_line(surf, (*GOLD, 140), (SX1 - 10, tick_y), (SX1, tick_y))
    alpha_line(surf, (*GOLD, 100), (SX1 - 6, tick_y - 4), (SX1 - 6, tick_y + 4))

    # Label: "DAY COMPLETE" pulled 20px from right canvas edge (critique #5)
    lbl = font(7).render("DAY COMPLETE", True, gold_a(150))
    lbl_rot = pygame.transform.rotate(lbl, -90)
    r = lbl_rot.get_rect()
    r.midright = (W - 20, SY0 + 55)   # 20px from right canvas edge
    surf.blit(lbl_rot, r)


def draw_scanlines(surf):
    lay = pygame.Surface((SW - 1, SH - 1), pygame.SRCALPHA)
    for y in range(0, SH - 1, 2):
        pygame.draw.line(lay, (*GOLD, 14), (0, y), (SW - 2, y))
    surf.blit(lay, (SX0 + 1, SY0 + 1))


def draw_persistence(surf):
    """Backward-decaying sweep afterglow. Changes from r1:
    - Vertical envelope tightened to ±90px around TRACE_Y (critique #5)
    - 4-6px forward bloom past sweep head fading to zero (critique #5)
    """
    lay = pygame.Surface((SW + 8, SH), pygame.SRCALPHA)   # +8 for forward bloom
    x_head = DEATH_X - SX0
    ty = TRACE_Y - SY0

    ENVELOPE_HALF = 90   # tightened from full SH to ±90px

    # Vertical envelope: tight Gaussian-ish falloff within ±90px
    env = []
    for y in range(SH):
        d = abs(y - ty)
        if d >= ENVELOPE_HALF:
            env.append(0.0)
        else:
            # Smooth falloff: 1 at center, 0 at ±ENVELOPE_HALF
            frac = d / float(ENVELOPE_HALF)
            env.append((1.0 - frac ** 1.5) ** 2)

    # Backward sweep: bright at head, dim toward start
    for i in range(int(x_head) + 1):
        k = i / max(1.0, x_head)
        a = 25 + (150 - 25) * (k ** 1.6)
        for y in range(max(0, ty - ENVELOPE_HALF), min(SH, ty + ENVELOPE_HALF + 1)):
            av = int(round(a * env[y]))
            if av > 0:
                lay.set_at((i, y), (*GOLD, av))

    # Forward bloom: 4-6px past sweep head, alpha fading to zero (critique #5)
    BLOOM_PX = 6
    for bi in range(1, BLOOM_PX + 1):
        xi = int(x_head) + bi
        if xi < lay.get_width():
            fade_frac = 1.0 - (bi / BLOOM_PX)
            a_bloom = int(round(90 * fade_frac))
            for y in range(max(0, ty - ENVELOPE_HALF), min(SH, ty + ENVELOPE_HALF + 1)):
                av = int(round(a_bloom * env[y]))
                if av > 0:
                    lay.set_at((xi, y), (*GOLD, av))

    surf.blit(lay, (SX0, SY0))


def draw_axis(surf):
    """Phase ruler. ALTITUDE BAND rotated as left-rail label (critique #5)."""
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        x = int(round(px(frac)))
        alpha_line(surf, (*GOLD, 90), (x, SY1 + 1), (x, SY1 + 5))
        text(surf, f"{int(frac * 100)}%", 7, center=(x, SY1 + 14),
             color=gold_a(96), shadow=None)
    text(surf, "PHASE OF DAY", 7, midleft=(SX0, SY1 + 30), color=gold_a(74),
         shadow=None, track=1)

    # ALTITUDE BAND: rotated left-rail label (critique #5)
    lbl = font(7).render("ALTITUDE BAND", True, gold_a(74))
    lbl_rot = pygame.transform.rotate(lbl, 90)
    r = lbl_rot.get_rect()
    r.midright = (SX0 - 4, (SY0 + SY1) // 2)
    surf.blit(lbl_rot, r)


# ── the run ──────────────────────────────────────────────────────────────────

def draw_trace(surf):
    """Flown 18.4% trace. No arrowhead (critique #2)."""
    g = soft_glow(13, GOLD, peak=30, falloff=1.6)
    for x in range(SX0, int(DEATH_X) + 1, 6):
        surf.blit(g, (x - 14, TRACE_Y - 14), special_flags=pygame.BLEND_ADD)
    g2 = soft_glow(19, GOLD, peak=58, falloff=1.9)
    surf.blit(g2, (int(DEATH_X) - 20, TRACE_Y - 20), special_flags=pygame.BLEND_ADD)

    # Solid flown trace line — NO arrowhead (critique #2)
    pygame.draw.line(surf, GOLD, (SX0, TRACE_Y), (int(DEATH_X), TRACE_Y), 2)

    # Post-death: dashed/dotted projected track GOLD@18, 3-on-5-off (critique #1)
    proj_color = gold_a(18)
    dx = int(DEATH_X)
    x = dx
    on_off = (3, 5)
    drawing = True
    seg_pos = 0
    while x < SX1 - 1:
        seg_len = on_off[0] if drawing else on_off[1]
        end_x = min(x + seg_len, SX1 - 1)
        if drawing:
            pygame.draw.line(surf, proj_color, (x, TRACE_Y), (end_x, TRACE_Y), 1)
        x = end_x
        drawing = not drawing


def draw_death(surf):
    """Crosshair with cleared ink cell + GOLD@100 reticle (critique #3)."""
    dx = int(round(DEATH_X))
    dy = TRACE_Y

    # Hairlines
    alpha_line(surf, (*INK, 200), (dx - 1, SY0 + 1), (dx - 1, SY1 - 1))
    alpha_line(surf, (*GOLD, 120), (SX0 + 1, dy), (SX1 - 1, dy))
    alpha_line(surf, (*GOLD, 120), (dx, SY0 + 1), (dx, SY1 - 1))

    # Critique #3: punch a clean 22×22 ink cell around death point
    CELL = 11   # half-size = 11 → full 22×22
    cell_color = (20, 18, 16)
    cell_rect = pygame.Rect(dx - CELL, dy - CELL, CELL * 2, CELL * 2)
    pygame.draw.rect(surf, cell_color, cell_rect)

    # Redraw hairlines through the cleared cell (so they're visible inside)
    pygame.draw.line(surf, gold_a(120), (dx - CELL, dy), (dx + CELL, dy), 1)
    pygame.draw.line(surf, gold_a(120), (dx, dy - CELL), (dx, dy + CELL), 1)

    # Reticle: corner-only brackets GOLD@100, re-registered at ±11px (critique #3)
    # No INK outline — gold on ink for maximum contrast
    arm = 4
    OFFSET = 11
    gold100 = GOLD  # GOLD@100 = full GOLD
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx = dx + sx * OFFSET
            cy = dy + sy * OFFSET
            # Horizontal arm
            pygame.draw.line(surf, gold100, (cx, cy), (cx - sx * arm, cy))
            # Vertical arm
            pygame.draw.line(surf, gold100, (cx, cy), (cx, cy - sy * arm))


def draw_dashed_circle(surf, color, center, radius, dash_on=6, dash_off=6, width=1):
    """Draw a dashed/broken circle using arc segments."""
    cx, cy = center
    circumference = 2 * math.pi * radius
    dash_total = dash_on + dash_off
    n_dashes = max(1, int(circumference / dash_total))
    for i in range(n_dashes):
        start_frac = i / n_dashes
        end_frac = start_frac + (dash_on / (dash_total * n_dashes)) * n_dashes
        angle_start = start_frac * 2 * math.pi - math.pi / 2
        angle_end = end_frac * 2 * math.pi - math.pi / 2
        if angle_end <= angle_start:
            continue
        # Draw via polyline approximation
        steps = max(2, int((angle_end - angle_start) * radius))
        pts = []
        for s in range(steps + 1):
            a = angle_start + (angle_end - angle_start) * s / steps
            pts.append((int(cx + math.cos(a) * radius), int(cy + math.sin(a) * radius)))
        if len(pts) >= 2:
            pygame.draw.lines(surf, color, False, pts, width)


def draw_contacts(surf):
    """Contacts: GOLD@75 ring + GOLD@100 center pip; RAIN & CLOWN get dashed ring (critique #3)."""
    gold75 = gold_a(75 * 255 // 100)  # GOLD@75 as opaque blend
    gold100 = GOLD

    for name, p, alt, rad, side in CONTACTS:
        x, y = int(round(px(p))), int(round(py(alt)))

        near = name in NEAR_DEATH

        if near:
            # Broken/dashed ring for near-miss contacts
            draw_dashed_circle(surf, gold75, (x, y), rad, dash_on=4, dash_off=4, width=1)
        else:
            lay = pygame.Surface((rad * 2 + 4, rad * 2 + 4), pygame.SRCALPHA)
            # GOLD@75 ring (hollow) — alpha-composited
            pygame.draw.circle(lay, (*GOLD, 75), (rad + 2, rad + 2), rad, width=1)
            surf.blit(lay, (x - rad - 2, y - rad - 2))

        # GOLD@100 1px center pip
        surf.set_at((x, y), gold100)

        # Labels
        if x < DEATH_X + 40:
            text(surf, name, 8, midleft=(x + rad + 7, y), color=LABEL_GOLD, shadow=None)
        else:
            ly = y - rad - 9 if side == "above" else y + rad + 9
            text(surf, name, 8 if rad >= 9 else 7, center=(x, ly),
                 color=LABEL_GOLD, shadow=None)


def draw_callout(surf):
    """ENDED HERE as square-cornered ink plate with left rule + right-angle leader (critique #4)."""
    f10, f8 = font(10), font(8)
    body = f"PILLAR {DEATH_PILLAR}  ·  {PHASE_LABEL} 18.4%"
    cw = max(f10.size("ENDED HERE")[0], f8.size(body)[0]) + 20
    cr_h = 34

    dx = int(round(DEATH_X))
    dy = TRACE_Y

    # Position plate: just below and slightly right of the crosshair
    # Tied clearly to the crosshair (critique #4) — 18px below hairline intersection
    plate_y = dy + 18
    # Keep plate within scope horizontal bounds
    plate_x = max(SX0 + 4, min(dx - cw // 2, SX1 - cw - 4))

    cr = pygame.Rect(plate_x, plate_y, cw, cr_h)

    # Square-cornered ink plate (no radius) — critique #4
    plate_surf = pygame.Surface((cw, cr_h), pygame.SRCALPHA)
    plate_surf.fill((16, 14, 12, 240))
    # Border: 1px GOLD@86
    pygame.draw.rect(plate_surf, (*GOLD, 86), plate_surf.get_rect(), width=1)
    # Left-edge vertical rule GOLD@60 inside left border (critique #4)
    pygame.draw.line(plate_surf, (*GOLD, 60), (1, 1), (1, cr_h - 2), 1)
    surf.blit(plate_surf, cr.topleft)

    # Right-angle leader: horizontal then vertical (critique #4)
    # Horizontal: from death_x to plate left-center, at mid-plate y
    leader_y = cr.y + cr_h // 2
    # Only draw if plate is to the right of death_x; otherwise adapt
    h_start = dx
    h_end = cr.x
    if h_end > h_start:
        alpha_line(surf, (*GOLD, 100), (h_start, leader_y), (h_end, leader_y))
    elif h_end < h_start:
        alpha_line(surf, (*GOLD, 100), (h_start, leader_y), (h_end + cw, leader_y))
        alpha_line(surf, (*GOLD, 100), (h_start, dy), (h_start, leader_y))

    # Vertical: from dy (crosshair) down to leader_y at death_x
    if leader_y > dy:
        alpha_line(surf, (*GOLD, 100), (dx, dy + 1), (dx, leader_y))

    # Text inside plate
    text(surf, "ENDED HERE", 10, midleft=(cr.x + 10, cr.y + 11), color=GOLD, shadow=None)
    text(surf, body, 8, midleft=(cr.x + 10, cr.y + 24), color=gold_a(190), shadow=None)


# ── screen ───────────────────────────────────────────────────────────────────

def render_screen():
    surf = pygame.Surface((W, H))
    surf.fill(INK)

    draw_scanlines(surf)
    draw_persistence(surf)
    draw_scope_frame(surf)
    draw_axis(surf)
    draw_contacts(surf)
    draw_trace(surf)
    draw_death(surf)
    draw_callout(surf)
    # draw_day_complete removed — terminus is now in draw_scope_frame (critique #2)

    # ── banner ──
    pygame.draw.rect(surf, SCRIM, (0, 0, W, 74))
    fade = pygame.Surface((W, 10), pygame.SRCALPHA)
    for i in range(10):
        fade.fill((*SCRIM, int(238 * (1 - i / 10) ** 1.4)), pygame.Rect(0, i, W, 1))
    surf.blit(fade, (0, 74))
    alpha_line(surf, (255, 206, 92, 150), (0, 74), (W - 1, 74), 1)

    text(surf, f"FLIGHT LOG  ·  DAY {DAY_N}", 21, center=(W // 2, 28), color=GOLD,
         track=3, shadow=None)
    text(surf, f"PILLAR {DEATH_PILLAR}   ·   0:{TIME_ALIVE:02d}", 12,
         center=(W // 2, 55), color=CREAM, shadow=None)

    # ── headline ──
    pct = f"{DEATH_PHASE * 100:.0f}%"
    f_big, f_sml = font(21), font(11)
    w_pct = f_big.size(pct)[0]
    w_tail = f_sml.size("  OF THE DAY FLOWN")[0]
    x0 = (W - (w_pct + w_tail)) / 2
    text(surf, pct, 21, midleft=(x0, 104), color=GOLD, shadow=(0, 0, 0, 170))
    text(surf, "  OF THE DAY FLOWN", 11, midleft=(x0 + w_pct, 106),
         color=DIM_GOLD, shadow=(0, 0, 0, 170))
    alpha_line(surf, (255, 206, 92, 96), (int(x0), 120),
               (int(x0 + w_pct + w_tail), 120), 1)

    text(surf, "B-SCOPE  ·  SWEEP HALTED", 7, midleft=(SX0, 138),
         color=gold_a(96), shadow=None, track=1)
    text(surf, "4 CONTACTS UNSWEPT", 7, midright=(SX1, 138), color=gold_a(96),
         shadow=None, track=1)

    text(surf, "NOTHING PAST THE HALT WAS SWEPT", 8, center=(W // 2, 540),
         color=gold_a(112), shadow=None, track=1)

    # BACK pill
    pr = pygame.Rect(0, 0, 122, 36)
    pr.center = (W // 2, 597)
    sh = pygame.Surface((pr.w + 8, pr.h + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 100), sh.get_rect(), border_radius=21)
    surf.blit(sh, (pr.x - 4, pr.y - 1))
    grad = pygame.Surface(pr.size, pygame.SRCALPHA)
    for y in range(pr.h):
        grad.fill(lerp_color((255, 228, 172), (226, 168, 96), y / (pr.h - 1)) + (255,),
                  pygame.Rect(0, y, pr.w, 1))
    mask = pygame.Surface(pr.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=18)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, pr.topleft)
    pygame.draw.rect(surf, (110, 68, 38), pr, width=1, border_radius=18)
    text(surf, "BACK", 13, center=(pr.centerx, pr.centery), color=(66, 40, 20),
         shadow=None, track=2)

    return surf


def main():
    surf = render_screen()
    out = "/home/user/skybit/docs/flight_log_arc_v2/radar/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(surf, out)
    loaded = pygame.image.load(out)
    print(f"saved {out}  {loaded.get_size()}")


if __name__ == "__main__":
    main()
