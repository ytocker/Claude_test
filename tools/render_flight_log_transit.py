#!/usr/bin/env python3
"""
transit — TRANSIT LINE / STRIP MAP, round 1.

One dead-flat strip map, edge to edge: a single 10px rect at y=318 running
x=0→360 with zero margin, bleeding off both edges like a train-door diagram.

Rules that separate this from every other concept in the set:
  - Phase maps LINEARLY to x (x = phase * 360). No easing, no arc, no dome.
  - Absolute flatness: not one pixel of vertical deviation, dogleg, taper or
    corner radius on the strip. Everything lives at y=318 ± 5.
  - Zero gradients, zero glows, zero atmosphere. Pure flat colour. The screen
    is an information diagram, and typography carries all of the warmth.
  - Unreached events keep their identity sealed: shape and colour only, with a
    "?" instead of a name.
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

INK = (6, 8, 14)
GOLD = (255, 206, 92)
CREAM = (246, 240, 230)
COOL = (150, 168, 196)
SLATE = (58, 62, 82)
SCRIM = (26, 22, 34)
GEYSER_C = (146, 232, 255)
CLOWN_C = (255, 118, 196)
RAIN_C = (150, 190, 255)
SNOW_C = (222, 244, 255)

# ── the run ──────────────────────────────────────────────────────────────────
DEATH_PHASE = 0.184
DEATH_PILLAR = 25
DAY_N = 1
TIME_ALIVE = 47

PHASE_BOUNDARIES = [
    (0.00, "DAY"),
    (0.18, "GOLDEN HOUR"),
    (0.32, "SUNSET"),
    (0.48, "DUSK"),
    (0.62, "NIGHT"),
    (0.78, "PREDAWN"),
    (0.90, "SUNRISE"),
]

# Unreached events — colour and silhouette only, never a name.
EVENTS = [
    (0.167, GEYSER_C),
    (0.403, CLOWN_C),
    (0.430, RAIN_C),
    (0.820, SNOW_C),
]

LINE_Y = 318          # the one y value this whole screen is allowed to use
LINE_H = 10           # 313 → 322
DEATH_X = 66          # int(0.184 * 360) — the hard butt-joint
DIAMOND_Y = 272       # event rail, parked well clear of the station names
NAME_ABOVE_Y = 302
NAME_BELOW_Y = 334

_fonts: dict = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


# ── text / chrome helpers (carried over from render_flight_log_arc_count_r7) ──

def text(surf, s, size, center=None, midleft=None, midright=None,
         color=CREAM, shadow=(0, 0, 0, 150), track=0):
    f = font(size)
    if track:
        # Manual letter-spacing keeps headers reading as signage; pygame has no
        # tracking control.
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
    """`surf` is an opaque Surface, so pygame.draw would ignore the alpha and
    stamp the colour at full strength. Route through a scratch layer."""
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


# ── the linear mapping — the whole concept lives in this one line ────────────

def px(phase):
    return phase * W


def diamond_pts(cx, cy, r):
    return [(cx, cy - r), (cx + r * 0.78, cy), (cx, cy + r), (cx - r * 0.78, cy)]


# ── the strip ────────────────────────────────────────────────────────────────

def draw_strip(surf):
    """Flown span in GOLD, remainder in SLATE, hard butt-joint with a 1px INK
    gap. Drawn natively rather than supersampled: any resampling of a flat bar
    softens the very edge the diagram is built on."""
    top = LINE_Y - LINE_H // 2
    pygame.draw.rect(surf, GOLD, (0, top, DEATH_X, LINE_H))
    pygame.draw.rect(surf, INK, (DEATH_X, top, 1, LINE_H))
    pygame.draw.rect(surf, SLATE, (DEATH_X + 1, top, W - DEATH_X - 1, LINE_H))


# ── vector overlay (supersampled, then downscaled once) ──────────────────────

def draw_overlay(ss):
    k = SS
    ly = LINE_Y * k

    # Event leaders: a hairline from each sealed diamond down to its true x on
    # the strip. Without it a floating diamond states no position at all.
    for phase, col in EVENTS:
        x = px(phase) * k
        pygame.draw.line(ss, (*col, 52), (x, (DIAMOND_Y + 8) * k),
                         (x, (LINE_Y - LINE_H / 2 - 1) * k), max(1, int(1.0 * k)))

    # Sealed events — hollow diamonds, 60% alpha, width=1. Shape survives a
    # colourblind read; the colour is the only hint of identity, and the name
    # is withheld entirely.
    for phase, col in EVENTS:
        x = px(phase) * k
        pygame.draw.polygon(ss, (*col, 153),
                            diamond_pts(x, DIAMOND_Y * k, 6.5 * k),
                            max(1, int(1.0 * k)))

    # Stations — the 7 phase boundaries. Filled gold behind the run, hollow
    # slate ahead of it: one glyph, two states, no legend needed.
    for phase, _name in PHASE_BOUNDARIES:
        x = px(phase)
        cx = int(x * k)
        if x < DEATH_X:
            pygame.draw.circle(ss, (*GOLD, 255), (cx, ly), int(7 * k))
            pygame.draw.circle(ss, (*INK, 255), (cx, ly), int(7 * k),
                               max(1, int(1.0 * k)))
        else:
            pygame.draw.circle(ss, (*SLATE, 255), (cx, ly), int(7 * k))
            pygame.draw.circle(ss, (*COOL, 150), (cx, ly), int(7 * k),
                               max(1, int(1.0 * k)))

    # Death mark — gold disc with a near-white core, the brightest thing on the
    # screen, sitting exactly on the joint.
    dx = DEATH_X * k
    pygame.draw.circle(ss, (*INK, 255), (int(dx), ly), int(10.5 * k))
    pygame.draw.circle(ss, (*GOLD, 255), (int(dx), ly), int(8 * k))
    pygame.draw.circle(ss, (255, 252, 240, 255), (int(dx), ly), int(3 * k))

    # Downward caret under the death mark — points at the callout, and is the
    # only vertical the flown side of the strip is allowed.
    pygame.draw.polygon(ss, (*GOLD, 255), [
        (dx - 5.5 * k, (LINE_Y + 9) * k),
        (dx + 5.5 * k, (LINE_Y + 9) * k),
        (dx, (LINE_Y + 17) * k),
    ])

    # DAY COMPLETE — upward caret pinned at the far right terminus.
    cx = 355 * k
    pygame.draw.polygon(ss, (*GOLD, 255), [
        (cx - 5.5 * k, (LINE_Y - 9) * k),
        (cx + 5.5 * k, (LINE_Y - 9) * k),
        (cx, (LINE_Y - 17) * k),
    ])


# ── screen ───────────────────────────────────────────────────────────────────

def render_screen():
    surf = pygame.Surface((W, H))
    surf.fill(INK)

    draw_strip(surf)

    ss = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    draw_overlay(ss)
    surf.blit(pygame.transform.smoothscale(ss, (W, H)), (0, 0))

    # "?" under each sealed diamond, at a third of the event's brightness — a
    # marker you can see is there without it announcing what it is.
    for phase, col in EVENTS:
        q = tuple(c // 3 for c in col)
        text(surf, "?", 8, center=(int(px(phase)), DIAMOND_Y + 14), color=q,
             shadow=None)

    # Sealed-event rail label, far enough left of the first diamond to read as
    # a row heading rather than a caption.
    text(surf, "SEALED", 6, midleft=(6, DIAMOND_Y), color=(*COOL, 120),
         shadow=None, track=1)

    # Station names — always horizontal, alternating above and below so the
    # tight early boundaries never collide. Clamped to the canvas so the x=0
    # station still gets a readable name.
    #
    # Two hand-placed exceptions to the alternation. GOLDEN HOUR sits at x=65,
    # which is exactly where the death caret drops, so it takes the upper row;
    # DAY then moves to the lower row, because left-clamped at x=0 it would
    # otherwise butt straight into GOLDEN HOUR and read as one string.
    NAME_ROW = [NAME_BELOW_Y, NAME_ABOVE_Y, NAME_BELOW_Y, NAME_ABOVE_Y,
                NAME_BELOW_Y, NAME_ABOVE_Y, NAME_BELOW_Y]
    for i, (phase, name) in enumerate(PHASE_BOUNDARIES):
        x = px(phase)
        y = NAME_ROW[i]
        f = font(7)
        half = (f.size(name)[0] + 2 * (len(name) - 1)) / 2
        cx = max(half + 4, min(W - half - 4, x))
        col = GOLD if x < DEATH_X else COOL
        text(surf, name, 7, center=(int(cx), y), color=col, shadow=None, track=2)

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
    text(surf, pct, 21, midleft=(x0, 104), color=GOLD, shadow=None)
    text(surf, "  OF THE DAY FLOWN", 11, midleft=(x0 + w_pct, 106), color=CREAM,
         shadow=None)

    # ── death callout, hung off the caret to the right and below ──
    f10, f8 = font(10), font(8)
    label_b = f"PILLAR {DEATH_PILLAR}  ·  0:{TIME_ALIVE:02d}"
    cw = max(f10.size("ENDED HERE")[0], f8.size(label_b)[0]) + 20
    cr = pygame.Rect(0, 0, cw, 34)
    cr.topleft = (DEATH_X + 12, 352)
    chip(surf, cr, radius=7, alpha=238, border_a=66)
    alpha_line(surf, (255, 206, 92, 150), (DEATH_X, LINE_Y + 18),
               (cr.x, cr.centery), 1)
    text(surf, "ENDED HERE", 10, midleft=(cr.x + 10, cr.y + 11), color=GOLD,
         shadow=None)
    text(surf, label_b, 8, midleft=(cr.x + 10, cr.y + 24), color=CREAM,
         shadow=None)

    # DAY COMPLETE caption, dropped below the station-name band so it does not
    # sit on top of SUNRISE at x=324.
    text(surf, "DAY COMPLETE", 6, midright=(357, 354), color=(*COOL, 120),
         shadow=None, track=1)

    # ── BACK pill ──
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


OUT_SLUG = "transit"
OUT_ROUND = "round_1"


def main():
    screen = render_screen()
    out = os.path.join(ROOT, "docs", "flight_log_arc_v2", OUT_SLUG, f"{OUT_ROUND}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(screen, out)
    print(f"saved {out}  {pygame.image.load(out).get_size()}")


if __name__ == "__main__":
    main()
