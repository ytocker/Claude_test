#!/usr/bin/env python3
"""
radar round 1 — COMMAND RADAR.

A single monochrome B-scope. X is phase, mapped *linearly* (no easing) across
the scope window; Y is an altitude band. The flown run is a short gold trace
hard against the left rail; everything past it is unswept, so the four events
the player never reached are hollow contacts differentiated by size alone.

Rules this screen commits to:
  - One hue. Every mark is an amber value step over INK. No cream, no cool,
    no per-event colour — an unswept contact must not leak its identity.
  - Phase is linear. Nothing is eased into looking further along than it was:
    18.4% of the day is 18.4% of the rail.
  - Phosphor persistence carries the reading. The swept region decays backward
    from the sweep head, so the eye lands on the death point without a label
    having to shout.
"""
import os
import math
import random

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


# ── text / chrome helpers (verbatim from arc_count_r7) ───────────────────────

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


def chip(surf, rect, radius=6, fill=(18, 15, 24), alpha=234,
         border=CREAM, border_a=54):
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s, (*fill, alpha), s.get_rect(), border_radius=radius)
    if border_a:
        pygame.draw.rect(s, (*border, border_a), s.get_rect(), width=1,
                         border_radius=radius)
    surf.blit(s, rect.topleft)


def soft_glow(radius, color, peak=110, falloff=2.0):
    """Additive glow with the falloff baked into RGB.

    BLEND_ADD ignores the source alpha channel, so an alpha-ramped glow blits
    as a flat hard-edged disc. Premultiplying keeps the ramp.
    """
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        f = (1 - (r / radius) ** falloff) * (peak / 255.0)
        s_col = (int(color[0] * f), int(color[1] * f), int(color[2] * f), 255)
        pygame.draw.circle(s, s_col, (c, c), r)
    return s


def alpha_line(surf, rgba, p0, p1, width=1):
    """`surf` is an opaque Surface, so pygame.draw would ignore the alpha and
    stamp the colour at full strength. Route through a scratch layer."""
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


def add_ink(src, color=(6, 8, 14, 240), pad=2):
    """Dilated dark keyline — the only thing that guarantees a small sprite
    holds its silhouette over both a bright dune and a dark veiled sky."""
    mask = pygame.mask.from_surface(src, threshold=12)
    sil = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface((src.get_width() + pad * 2, src.get_height() + pad * 2),
                         pygame.SRCALPHA)
    for dx in range(-pad, pad + 1):
        for dy in range(-pad, pad + 1):
            if dx or dy:
                out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


# ── monochrome ladder ────────────────────────────────────────────────────────
# Text cannot carry an alpha, so every "GOLD@n" typographic value is resolved
# against INK up front. Composited over the ink field the result is identical
# to an alpha blend, and it keeps the whole screen on one hue by construction.

def gold_a(a):
    return lerp_color(INK, GOLD, max(0, min(255, a)) / 255.0)


DIM_GOLD = gold_a(198)     # the headline tail — an amber step, not cream
LABEL_GOLD = gold_a(80)    # phase names beside their contacts


# ── run + scope geometry ─────────────────────────────────────────────────────

DEATH_PHASE = 0.184
DEATH_PILLAR = 25
DAY_N = 1
TIME_ALIVE = 47
PHASE_LABEL = "DAY"

SX0, SY0 = 26, 150
SX1, SY1 = 334, 486
SW, SH = SX1 - SX0, SY1 - SY0    # 308 × 336

ALT_TOP, ALT_BOT = SY0 + 40, SY1 - 20   # altitude band, inset from the rails


def px(p):
    """Phase → scope x. Linear, deliberately: no easing anywhere on this screen."""
    return SX0 + max(0.0, min(1.0, p)) * SW


def py(alt):
    """Altitude 0..1 → scope y. Arbitrary band, but the only one on the screen."""
    return ALT_BOT - max(0.0, min(1.0, alt)) * (ALT_BOT - ALT_TOP)


DEATH_X = px(DEATH_PHASE)          # ≈ 82.7
TRACE_ALT = 0.42
TRACE_Y = int(round(py(TRACE_ALT)))

# Unreached contacts. Size is the only channel that separates them — hue would
# tell the player which event it is, and they never got there.
CONTACTS = [
    ("GEYSER",    0.167, 0.72,  9, "above"),
    ("CLOWN",     0.403, 0.30,  6, "below"),
    ("RAIN",      0.430, 0.55,  4, "above"),
    ("SNOWSTORM", 0.820, 0.85, 11, "below"),
]


# ── scope furniture ──────────────────────────────────────────────────────────

def draw_scope_frame(surf):
    """1px rail + corner ticks. The ticks are the only bright frame value, so
    the window reads as an instrument bezel rather than a drawn box."""
    alpha_line(surf, (*GOLD, 70), (SX0, SY0), (SX1, SY0))
    alpha_line(surf, (*GOLD, 70), (SX0, SY1), (SX1, SY1))
    alpha_line(surf, (*GOLD, 70), (SX0, SY0), (SX0, SY1))
    alpha_line(surf, (*GOLD, 70), (SX1, SY0), (SX1, SY1))

    t = 9
    for cx, cy, sx, sy in ((SX0, SY0, 1, 1), (SX1, SY0, -1, 1),
                           (SX0, SY1, 1, -1), (SX1, SY1, -1, -1)):
        alpha_line(surf, (*GOLD, 165), (cx, cy), (cx + sx * t, cy))
        alpha_line(surf, (*GOLD, 165), (cx, cy), (cx, cy + sy * t))


def draw_scanlines(surf):
    """2px-pitch phosphor raster across the whole window, at the threshold of
    visibility. It gives the empty right-hand two-thirds a surface to be empty
    *on* — without it the unswept region reads as a hole, not as sky unlooked-at."""
    lay = pygame.Surface((SW - 1, SH - 1), pygame.SRCALPHA)
    for y in range(0, SH - 1, 2):
        pygame.draw.line(lay, (*GOLD, 14), (0, y), (SW - 2, y))
    surf.blit(lay, (SX0 + 1, SY0 + 1))


def draw_persistence(surf):
    """Backward-decaying sweep afterglow: bright at the head where the run
    ended, guttering out toward the start of the day. This is what makes the
    death point the focus without a second highlight competing for it."""
    lay = pygame.Surface((SW, SH), pygame.SRCALPHA)
    x_head = DEATH_X - SX0
    ty = TRACE_Y - SY0
    # Vertical envelope: a flat column at the head alpha would fill the swept
    # third as a solid ochre slab and eat the trace, the crosshair and the
    # first contact. Concentrating the charge around the sweep line — with a
    # floor so the rails still carry the decay — keeps the spec's 150→25
    # backward ramp while reading as phosphor rather than as paint.
    env = []
    for y in range(SH):
        d = abs(y - ty) / float(max(ty, SH - ty))
        env.append(0.22 + 0.78 * (1.0 - d) ** 2.2)
    for i in range(int(x_head) + 1):
        k = i / max(1.0, x_head)
        a = 25 + (150 - 25) * (k ** 1.6)
        for y in range(1, SH - 1):
            av = int(round(a * env[y]))
            if av > 0:
                lay.set_at((i, y), (*GOLD, av))
    surf.blit(lay, (SX0, SY0))


def draw_axis(surf):
    """Phase ruler under the bottom rail. Quarter ticks only — a denser scale
    would imply a precision the run does not have."""
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        x = int(round(px(frac)))
        alpha_line(surf, (*GOLD, 90), (x, SY1 + 1), (x, SY1 + 5))
        text(surf, f"{int(frac * 100)}%", 7, center=(x, SY1 + 14),
             color=gold_a(96), shadow=None)
    text(surf, "PHASE OF DAY", 7, midleft=(SX0, SY1 + 30), color=gold_a(74),
         shadow=None, track=1)
    text(surf, "ALTITUDE BAND", 7, midright=(SX1, SY1 + 30), color=gold_a(74),
         shadow=None, track=1)


# ── the run ──────────────────────────────────────────────────────────────────

def draw_trace(surf):
    """The flown 18.4%, glowing. Additive so the phosphor beneath it survives."""
    g = soft_glow(13, GOLD, peak=30, falloff=1.6)
    for x in range(SX0, int(DEATH_X) + 1, 6):
        surf.blit(g, (x - 14, TRACE_Y - 14), special_flags=pygame.BLEND_ADD)
    g2 = soft_glow(19, GOLD, peak=58, falloff=1.9)
    surf.blit(g2, (int(DEATH_X) - 20, TRACE_Y - 20), special_flags=pygame.BLEND_ADD)

    pygame.draw.line(surf, GOLD, (SX0, TRACE_Y), (int(DEATH_X), TRACE_Y), 2)


def draw_death(surf):
    """Crosshair: two full-window hairlines and an open reticle. The reticle is
    corner strokes only — a closed box would read as another contact."""
    dx = int(round(DEATH_X))
    # The vertical hairline lands exactly on the sweep head, where gold@120
    # sits on top of gold@150 and disappears. A 1px ink shim on the lit side
    # is the only thing that gives it an edge to be seen against.
    alpha_line(surf, (*INK, 200), (dx - 1, SY0 + 1), (dx - 1, SY1 - 1))
    alpha_line(surf, (*GOLD, 120), (SX0 + 1, TRACE_Y), (SX1 - 1, TRACE_Y))
    alpha_line(surf, (*GOLD, 120), (dx, SY0 + 1), (dx, SY1 - 1))

    r = 7                      # 14px open reticle
    arm = 4
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = dx + sx * r, TRACE_Y + sy * r
            for col, off in ((INK, 1), (GOLD, 0)):
                pygame.draw.line(surf, col, (cx, cy + off),
                                 (cx - sx * arm, cy + off))
                pygame.draw.line(surf, col, (cx + off, cy),
                                 (cx + off, cy - sy * arm))


def draw_contacts(surf):
    """Four hollow returns the sweep never reached. Radius is the only thing
    that tells them apart."""
    for name, p, alt, rad, side in CONTACTS:
        x, y = int(round(px(p))), int(round(py(alt)))
        lay = pygame.Surface((rad * 2 + 4, rad * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(lay, (*GOLD, 55), (rad + 2, rad + 2), rad, width=1)
        pygame.draw.circle(lay, (*GOLD, 38), (rad + 2, rad + 2), 1)
        surf.blit(lay, (x - rad - 2, y - rad - 2))

        if x < DEATH_X + 40:
            # Too close to the sweep head to sit above its own contact — the
            # label would land in the brightest phosphor on the screen.
            text(surf, name, 8, midleft=(x + rad + 7, y), color=LABEL_GOLD,
                 shadow=None)
        else:
            ly = y - rad - 9 if side == "above" else y + rad + 9
            text(surf, name, 8 if rad >= 9 else 7, center=(x, ly),
                 color=LABEL_GOLD, shadow=None)


def draw_day_complete(surf):
    """A caret hard against the right rail — the day's far end exists, and the
    run is nowhere near it. Labelled up the rail so it costs no scope width."""
    y = TRACE_Y
    # Open chevron, not a filled head: a solid triangle at the end of the
    # horizontal hairline turns the whole rail into one arrow, which is the
    # exact false claim this screen exists to avoid.
    pygame.draw.lines(surf, GOLD, False,
                      [(SX1 - 7, y - 7), (SX1 - 1, y), (SX1 - 7, y + 7)], 2)
    lbl = font(7).render("DAY COMPLETE", True, gold_a(150))
    lbl = pygame.transform.rotate(lbl, -90)
    r = lbl.get_rect()
    r.midtop = (SX1 + 14, y - 40)
    surf.blit(lbl, r)


def draw_callout(surf):
    """Ends-here chip, hung under the sweep head. Amber border, so it stays on
    the one hue the screen is allowed."""
    f10, f8 = font(10), font(8)
    body = f"PILLAR {DEATH_PILLAR}  ·  {PHASE_LABEL} 18.4%"
    cw = max(f10.size("ENDED HERE")[0], f8.size(body)[0]) + 20
    cr = pygame.Rect(0, 0, cw, 34)
    cr.topleft = (SX0 + 8, TRACE_Y + 68)
    chip(surf, cr, radius=7, fill=(16, 14, 12), alpha=240,
         border=GOLD, border_a=86)
    alpha_line(surf, (*GOLD, 110), (int(DEATH_X), TRACE_Y + 14),
               (int(DEATH_X), cr.y))
    text(surf, "ENDED HERE", 10, midleft=(cr.x + 10, cr.y + 11), color=GOLD,
         shadow=None)
    text(surf, body, 8, midleft=(cr.x + 10, cr.y + 24), color=gold_a(190),
         shadow=None)


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
    draw_day_complete(surf)
    draw_callout(surf)

    # ── banner: fully opaque dark neutral, nothing bleeding through ──
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
    out = "/home/user/skybit/docs/flight_log_arc_v2/radar/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(surf, out)
    loaded = pygame.image.load(out)
    print(f"saved {out}  {loaded.get_size()}")


if __name__ == "__main__":
    main()
