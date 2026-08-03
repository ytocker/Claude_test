#!/usr/bin/env python3
"""
transit — TRANSIT LINE / STRIP MAP, round 2.

Art-director changes from round 1:
  1. Stats block (y≈140-260) + event legend (y≈400-560) fill the blank canvas.
  2. Edge clipping fixed: DAY station moved 10px in; terminus label repositioned.
  3. Unreached station circles at SLATE@160; unreached event diamonds GOLD@60 with
     event-colour fill dot; event leaders raised to @80 alpha.
  4. Death marker strengthened: soft_glow behind 8px disc + downward caret +
     square-cornered "ENDED HERE" chip.
  5. Typography hierarchy: DAY COMPLETE below terminus; station labels alternate
     above/below; death phase "18.4%" above disc; subtitle splits to two lines.
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

from game.draw import lerp_color

W, H = 360, 640
SS = 3
ROOT = "/home/user/skybit"
FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"

INK   = (6,   8,  14)
GOLD  = (255, 206, 92)
CREAM = (246, 240, 230)
COOL  = (150, 168, 196)
SLATE = (58,  62,  82)
SCRIM = (26,  22,  34)

GEYSER_C = (146, 232, 255)
CLOWN_C  = (255, 118, 196)
RAIN_C   = (150, 190, 255)
SNOW_C   = (222, 244, 255)

# ── the run ──────────────────────────────────────────────────────────────────
DEATH_PHASE  = 0.184
DEATH_PILLAR = 25
DAY_N        = 1
TIME_ALIVE   = 47

PHASE_BOUNDARIES = [
    (0.00, "DAY"),
    (0.18, "GOLDEN HOUR"),
    (0.32, "SUNSET"),
    (0.48, "DUSK"),
    (0.62, "NIGHT"),
    (0.78, "PREDAWN"),
    (0.90, "SUNRISE"),
]

EVENTS = [
    (0.167, GEYSER_C, "GEYSER"),
    (0.403, CLOWN_C,  "CLOWN"),
    (0.430, RAIN_C,   "RAIN"),
    (0.820, SNOW_C,   "SNOW"),
]

LINE_Y   = 318
LINE_H   = 10
DEATH_X  = int(DEATH_PHASE * W)   # 66

# Diamond rail — above the line
DIAMOND_Y = 272

# Station label rows
NAME_ABOVE_Y = 302
NAME_BELOW_Y = 334

_fonts: dict = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


# ── helpers ──────────────────────────────────────────────────────────────────

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


def alpha_line(surf, rgba, p0, p1, width=1):
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


def chip(surf, rect, radius=6, fill=(18, 15, 24), alpha=234,
         border=CREAM, border_a=54):
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s, (*fill, alpha), s.get_rect(), border_radius=radius)
    if border_a:
        pygame.draw.rect(s, (*border, border_a), s.get_rect(), width=1,
                         border_radius=radius)
    surf.blit(s, rect.topleft)


def soft_glow(surf, cx, cy, radius, color, peak=160):
    """Radial alpha falloff glow, blended additive. No .gaussian_blur()."""
    d = radius * 2 + 1
    glow_surf = pygame.Surface((d, d), pygame.SRCALPHA)
    r, g, b = color[:3]
    for gy in range(d):
        for gx in range(d):
            dx = gx - radius
            dy = gy - radius
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= radius:
                t = max(0.0, 1.0 - dist / radius)
                a = int(peak * t * t)
                # premultiply
                glow_surf.set_at((gx, gy), (r * a // 255, g * a // 255, b * a // 255, a))
    surf.blit(glow_surf, (cx - radius, cy - radius), special_flags=pygame.BLEND_ADD)


def px(phase):
    return phase * W


def diamond_pts(cx, cy, r):
    return [(cx, cy - r), (cx + r * 0.78, cy), (cx, cy + r), (cx - r * 0.78, cy)]


# ── strip ────────────────────────────────────────────────────────────────────

def draw_strip(surf):
    top = LINE_Y - LINE_H // 2
    pygame.draw.rect(surf, GOLD,  (0,          top, DEATH_X,              LINE_H))
    pygame.draw.rect(surf, INK,   (DEATH_X,    top, 1,                    LINE_H))
    pygame.draw.rect(surf, SLATE, (DEATH_X + 1, top, W - DEATH_X - 1,    LINE_H))


# ── vector overlay (supersampled) ────────────────────────────────────────────

def draw_overlay(ss):
    k  = SS
    ly = LINE_Y * k

    # ── event leaders: raised to @80 alpha ──
    for phase, col, _name in EVENTS:
        x = px(phase) * k
        pygame.draw.line(ss, (*col, 80), (x, (DIAMOND_Y + 8) * k),
                         (x, (LINE_Y - LINE_H / 2 - 1) * k), max(1, int(1.0 * k)))

    # ── event diamonds: GOLD@60 hollow + event-colour dot inside ──
    for phase, col, _name in EVENTS:
        x = px(phase) * k
        cy = DIAMOND_Y * k
        r  = 6.5 * k
        # Hollow GOLD diamond outline
        pygame.draw.polygon(ss, (*GOLD, 60),
                            diamond_pts(x, cy, r),
                            max(1, int(1.0 * k)))
        # Tiny filled event-colour dot in the centre
        pygame.draw.circle(ss, (*col, 180), (int(x), int(cy)), max(1, int(2.5 * k)))

    # ── stations ──
    # First station (DAY, phase=0.00) is moved 10px in from edge to avoid clipping.
    for i, (phase, _name) in enumerate(PHASE_BOUNDARIES):
        x = px(phase)
        if i == 0:
            x = max(x, 10)          # clamp DAY off left edge
        if i == len(PHASE_BOUNDARIES) - 1:
            x = min(x, W - 10)      # clamp SUNRISE off right edge
        cx = int(x * k)
        reached = (px(phase) <= DEATH_X)
        if reached:
            # filled gold disc
            pygame.draw.circle(ss, (*GOLD, 255), (cx, ly), int(7 * k))
            pygame.draw.circle(ss, (*INK,  255), (cx, ly), int(7 * k),
                               max(1, int(1.0 * k)))
        else:
            # dim but visible: SLATE@160 fill, no stroke (avoids fringing)
            pygame.draw.circle(ss, (*SLATE, 160), (cx, ly), int(7 * k))

    # ── death disc — 8px gold + soft_glow ──
    dx = DEATH_X * k
    pygame.draw.circle(ss, (*GOLD, 255), (int(dx), ly), int(8 * k))

    # ── downward caret pointing away from line ──
    pygame.draw.polygon(ss, (*GOLD, 255), [
        (dx - 5.5 * k, (LINE_Y + 9) * k),
        (dx + 5.5 * k, (LINE_Y + 9) * k),
        (dx,            (LINE_Y + 17) * k),
    ])

    # ── terminus (DAY COMPLETE) — only caret is drawn in overlay ──
    # No upward caret needed; label goes below circle.


# ── stats block (y≈140–260) ──────────────────────────────────────────────────

def draw_stats_block(surf):
    """Stats summary above the transit line."""
    cx = W // 2

    # Large day number
    text(surf, f"DAY {DAY_N}", 28, center=(cx, 150), color=GOLD, shadow=None, track=2)

    # Thin separator
    alpha_line(surf, (*SLATE, 100), (cx - 60, 172), (cx + 60, 172), 1)

    # Pillar
    text(surf, f"PILLAR {DEATH_PILLAR}", 16, center=(cx, 188), color=CREAM, shadow=None)

    # Time alive
    time_str = f"0:{TIME_ALIVE:02d}"
    text(surf, time_str, 16, center=(cx, 212), color=CREAM, shadow=None)

    # Thin separator
    alpha_line(surf, (*SLATE, 100), (cx - 60, 232), (cx + 60, 232), 1)

    # Percentage flown
    pct_str = f"{DEATH_PHASE * 100:.1f}%  OF DAY FLOWN"
    text(surf, pct_str, 11, center=(cx, 248), color=(*COOL, 200), shadow=None)


# ── event legend (y≈400–560) ─────────────────────────────────────────────────

def draw_event_legend(surf):
    """List all 4 events with their event colour dot + name + '?'."""
    legend_items = [
        (GEYSER_C, "GEYSER"),
        (CLOWN_C,  "CLOWN"),
        (RAIN_C,   "RAIN"),
        (SNOW_C,   "SNOW"),
    ]

    # Section heading
    text(surf, "EVENTS NOT REACHED", 9, center=(W // 2, 400),
         color=(*COOL, 160), shadow=None, track=1)

    alpha_line(surf, (*SLATE, 80), (20, 412), (W - 20, 412), 1)

    # Two-column layout: left col x=90, right col x=270
    col_xs = [90, 270]
    row_h  = 28
    start_y = 428

    for idx, (col, name) in enumerate(legend_items):
        col_idx = idx % 2
        row_idx = idx // 2
        item_cx = col_xs[col_idx]
        item_y  = start_y + row_idx * row_h

        # Coloured dot
        dot_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(dot_surf, (*col, 220), (4, 4), 4)
        surf.blit(dot_surf, (item_cx - 40, item_y - 4))

        # Name + "?"
        text(surf, f"{name} ?", 10,
             midleft=(item_cx - 28, item_y),
             color=(*col, 180), shadow=None)

    # Footer note
    alpha_line(surf, (*SLATE, 60), (20, 500), (W - 20, 500), 1)
    text(surf, "SEALED UNTIL ENCOUNTERED", 8,
         center=(W // 2, 514), color=(*COOL, 100), shadow=None, track=1)


# ── death marker (on surf, not ss) ───────────────────────────────────────────

def draw_death_marker(surf):
    dx = DEATH_X
    ly = LINE_Y

    # Soft glow behind disc
    soft_glow(surf, dx, ly, radius=18, color=GOLD, peak=160)

    # "18.4%" phase label above disc
    pct_label = f"{DEATH_PHASE * 100:.1f}%"
    text(surf, pct_label, 11, center=(dx, ly - 20), color=GOLD, shadow=None)

    # Square-cornered "ENDED HERE" chip below the caret
    f9, f8 = font(9), font(8)
    line1 = "ENDED HERE"
    line2 = f"PILLAR {DEATH_PILLAR} · DAY {DAY_N}"
    cw = max(f9.size(line1)[0], f8.size(line2)[0]) + 20
    ch = 34
    # Position chip: start just right of death x + small offset
    chip_x = dx + 12
    chip_y = ly + 22        # below caret (caret tip is at ly+17)
    # Keep chip inside canvas
    if chip_x + cw > W - 4:
        chip_x = W - cw - 4
    cr = pygame.Rect(chip_x, chip_y, cw, ch)

    # Square-cornered rect (radius=0), INK fill, GOLD@150 border
    chip_surf = pygame.Surface((cw, ch), pygame.SRCALPHA)
    pygame.draw.rect(chip_surf, (*INK, 230), chip_surf.get_rect(), border_radius=0)
    pygame.draw.rect(chip_surf, (*GOLD, 150), chip_surf.get_rect(), width=1, border_radius=0)
    surf.blit(chip_surf, cr.topleft)

    text(surf, line1, 9, midleft=(cr.x + 8, cr.y + 11), color=CREAM, shadow=None)
    text(surf, line2, 8, midleft=(cr.x + 8, cr.y + 24), color=(*GOLD, 100), shadow=None)

    # Connector line from caret tip to chip top-left area
    alpha_line(surf, (*GOLD, 100), (dx, ly + 17), (cr.x, cr.y + ch // 2), 1)


# ── station labels ────────────────────────────────────────────────────────────

def draw_station_labels(surf):
    """Alternate above/below with manual assignment per note."""
    # Alternation: GOLDEN HOUR above (avoids death caret), rest follow pattern
    # Manual row assignment:
    # DAY(0)→below, GOLDEN HOUR(1)→above, SUNSET(2)→below, DUSK(3)→above,
    # NIGHT(4)→below, PREDAWN(5)→above, SUNRISE(6)→below
    NAME_ROW = [
        NAME_BELOW_Y,   # DAY
        NAME_ABOVE_Y,   # GOLDEN HOUR
        NAME_BELOW_Y,   # SUNSET
        NAME_ABOVE_Y,   # DUSK
        NAME_BELOW_Y,   # NIGHT
        NAME_ABOVE_Y,   # PREDAWN
        NAME_BELOW_Y,   # SUNRISE
    ]
    for i, (phase, name) in enumerate(PHASE_BOUNDARIES):
        x = px(phase)
        # Apply same edge clamping as the station circles
        if i == 0:
            x = max(x, 10)
        if i == len(PHASE_BOUNDARIES) - 1:
            x = min(x, W - 10)
        y = NAME_ROW[i]
        f = font(7)
        half = (f.size(name)[0] + 2 * (len(name) - 1)) / 2
        cx = max(half + 4, min(W - half - 4, x))
        col = GOLD if px(phase) <= DEATH_X else (*SLATE, 160)
        text(surf, name, 7, center=(int(cx), y), color=col, shadow=None, track=2)

    # DAY COMPLETE label — below the terminus circle (per critique note 5)
    terminus_x = min(px(1.0), W - 10)
    text(surf, "DAY COMPLETE", 10, center=(int(terminus_x), NAME_BELOW_Y + 14),
         color=(*COOL, 140), shadow=None)


# ── terminus station circle ───────────────────────────────────────────────────

def draw_terminus(ss):
    """Draw the DAY COMPLETE terminus circle in the SS surface."""
    k  = SS
    ly = LINE_Y * k
    # Terminus at right edge, clamped 10px in
    tx = int(min(px(1.0), W - 10) * k)
    pygame.draw.circle(ss, (*SLATE, 160), (tx, ly), int(7 * k))


# ── main render ───────────────────────────────────────────────────────────────

def render_screen():
    surf = pygame.Surface((W, H))
    surf.fill(INK)

    # ── banner / scrim ──
    pygame.draw.rect(surf, SCRIM, (0, 0, W, 74))
    fade = pygame.Surface((W, 10), pygame.SRCALPHA)
    for i in range(10):
        fade.fill((*SCRIM, int(238 * (1 - i / 10) ** 1.4)), pygame.Rect(0, i, W, 1))
    surf.blit(fade, (0, 74))
    alpha_line(surf, (255, 206, 92, 150), (0, 74), (W - 1, 74), 1)

    text(surf, f"FLIGHT LOG  ·  DAY {DAY_N}", 21,
         center=(W // 2, 28), color=GOLD, track=3, shadow=None)
    text(surf, f"TRANSIT  ·  PILLAR {DEATH_PILLAR}", 12,
         center=(W // 2, 55), color=CREAM, shadow=None)

    # ── stats block above the line ──
    draw_stats_block(surf)

    # ── strip ──
    draw_strip(surf)

    # ── vector overlay (SS) ──
    ss = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    draw_overlay(ss)
    draw_terminus(ss)
    surf.blit(pygame.transform.smoothscale(ss, (W, H)), (0, 0))

    # ── death marker (glow + chip) ──
    draw_death_marker(surf)

    # ── station labels ──
    draw_station_labels(surf)

    # ── "?" under each event diamond ──
    for phase, col, _name in EVENTS:
        q = tuple(c // 3 for c in col)
        text(surf, "?", 8, center=(int(px(phase)), DIAMOND_Y + 14),
             color=q, shadow=None)

    # ── event legend below the line ──
    draw_event_legend(surf)

    # ── BACK pill ──
    pr = pygame.Rect(0, 0, 122, 36)
    pr.center = (W // 2, 597)
    sh = pygame.Surface((pr.w + 8, pr.h + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 100), sh.get_rect(), border_radius=21)
    surf.blit(sh, (pr.x - 4, pr.y - 1))
    grad = pygame.Surface(pr.size, pygame.SRCALPHA)
    for y in range(pr.h):
        grad.fill(
            lerp_color((255, 228, 172), (226, 168, 96), y / (pr.h - 1)) + (255,),
            pygame.Rect(0, y, pr.w, 1))
    mask = pygame.Surface(pr.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=18)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, pr.topleft)
    pygame.draw.rect(surf, (110, 68, 38), pr, width=1, border_radius=18)
    text(surf, "BACK", 13, center=(pr.centerx, pr.centery),
         color=(66, 40, 20), shadow=None, track=2)

    return surf


OUT_SLUG  = "transit"
OUT_ROUND = "round_2"


def main():
    screen = render_screen()
    out = os.path.join(ROOT, "docs", "flight_log_arc_v2", OUT_SLUG, f"{OUT_ROUND}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(screen, out)
    img = pygame.image.load(out)
    print(f"saved {out}  {img.get_size()}")


if __name__ == "__main__":
    main()
