#!/usr/bin/env python3
"""
black-box  ·  flight_log_screen  ·  round 2

The screen is the flight recorder tape, not a report about it. There is no
container, no bezel and no chrome: a single 2 px gold trace of the parrot's
altitude -- run through Skybit's own GRAVITY / FLAP_V / MAX_FALL numbers, so
the sawtooth is the real tap rhythm rather than a decorative wave -- winds
across four horizontal lanes the way a paper recorder winds a long strip onto
a short page. Time is the only axis, and the run does not own all of it: the
tape covers the whole day the parrot died in, so the length of the charted
stretch versus the uncharted one IS the progress readout.

Death is the only saturated non-gold mark on the screen -- the trace stops
oscillating, turns scarlet, and holds dead-level. No callout, no label: a
flatline needs no caption. Everything after it is the same trace, same
amplitude envelope, drawn as faint gold dashes -- signal that exists but was
never recorded, which is a far better invitation than a grey empty bar.

Two runs, same construction: pillar 25 (barely off the ground, a long dotted
tail) and pillar 180 (a dense gold band that almost finishes the tape).
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

from game.config import GRAVITY, FLAP_V, MAX_FALL
from game.biome import palette_for_phase
from game.draw import lerp_color


W, H = 360, 640

FONT = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
_fonts = {}


def _font(size):
    f = _fonts.get(size)
    if f is None:
        f = pygame.font.Font(FONT, size)
        _fonts[size] = f
    return f


# ── palette ──────────────────────────────────────────────────────────────────
BG          = (  8,   8,  20)
GOLD        = (240, 192,  64)
GOLD_MUTED  = (216, 184,  85)
GOLD_PALE   = (255, 232, 168)
GOLD_DEEP   = (214, 150,  44)
SCARLET     = (172,  40,  32)

# ── lane geometry ────────────────────────────────────────────────────────────
LANES   = 4
LX0     = 26
LX1     = 340
LW      = LX1 - LX0
LANE_H  = 98
LANE_Y0 = 44

BAND_HI = 6                              # trace ceiling, relative to lane top
BAND_LO = 78                             # trace floor
BASE_DY = 88                             # pillar-tick baseline
PATH_PX = LANES * LW

# A flatline longer than this stops reading as an event marker and starts
# reading as a filled bar, which is the one thing the screen must not have.
FLATLINE_MAX = 96

RAIL_X, RAIL_W = 10, 5
RAIL_Y0, RAIL_Y1 = LANE_Y0, LANE_Y0 + (LANES - 1) * LANE_H + BASE_DY


def lane_top(i):
    return LANE_Y0 + i * LANE_H


def path_xy(frac, norm):
    """Timeline fraction + normalised altitude -> (lane index, x, y)."""
    frac = min(max(frac, 0.0), 0.999999)
    i = int(frac * LANES)
    local = frac * LANES - i
    top = lane_top(i)
    x = LX0 + local * LW
    y = top + BAND_LO - norm * (BAND_LO - BAND_HI)
    return i, x, y


# ═════════════════════════════════════════════════════════════════════════════
# text
# ═════════════════════════════════════════════════════════════════════════════
def _render(txt, size, color, spacing=0):
    f = _font(size)
    if spacing <= 0:
        return f.render(txt, True, color)
    imgs = [f.render(c, True, color) for c in txt]
    w = int(round(sum(i.get_width() for i in imgs) + spacing * (len(txt) - 1)))
    h = max(i.get_height() for i in imgs)
    s = pygame.Surface((max(1, w), h), pygame.SRCALPHA)
    x = 0.0
    for i in imgs:
        s.blit(i, (int(round(x)), 0))
        x += i.get_width() + spacing
    return s


def text(surf, txt, size, color, pos, anchor="midleft", spacing=0, alpha=255):
    img = _render(txt, size, color, spacing)
    if alpha < 255:
        img.set_alpha(alpha)
    r = img.get_rect(**{anchor: pos})
    surf.blit(img, r.topleft)
    return r


def runs(surf, parts, x, y, size, spacing=0):
    for txt, col in parts:
        r = text(surf, txt, size, col, (x, y), "midleft", spacing=spacing)
        x = r.right + (spacing if spacing > 0 else 0)
    return x


def gradient_numeral(txt, size, stops):
    """Cropped to the glyph bbox so the hero numeral can be positioned by its
    ink rather than by the font's line box, which carries ~30% dead space."""
    img = _render(txt, size, (255, 255, 255))
    bb = img.get_bounding_rect()
    if bb.w == 0 or bb.h == 0:
        return img
    glyph = img.subsurface(bb).copy()
    gw, gh = glyph.get_size()
    grad = pygame.Surface((gw, gh), pygame.SRCALPHA)
    for y in range(gh):
        t = y / max(1, gh - 1)
        for k in range(len(stops) - 1):
            a0, c0 = stops[k]
            a1, c1 = stops[k + 1]
            if a0 <= t <= a1:
                u = (t - a0) / (a1 - a0) if a1 > a0 else 0.0
                grad.fill(lerp_color(c0, c1, u), (0, y, gw, 1))
                break
    grad.blit(glyph, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return grad


# ═════════════════════════════════════════════════════════════════════════════
# flight simulation — the real Skybit numbers at the real fixed timestep
# ═════════════════════════════════════════════════════════════════════════════
DT = 1.0 / 60.0


def simulate(seed, span_s):
    """Fixed-step altitude trace for a whole day of flying.

    A metronome alone would give a perfectly regular comb, so the pilot is
    modelled instead: taps are scheduled on a jittered ~0.4 s rhythm but only
    spent when the parrot has fallen below the corridor it is aiming at.
    Skipped taps are what produce the long free-fall teeth that make the
    sawtooth read as flown rather than generated.
    """
    rng = random.Random(seed)
    wander = [(rng.uniform(26.0, 95.0), rng.uniform(0.0, math.tau),
               rng.uniform(18.0, 46.0)) for _ in range(3)]

    def corridor(t):
        c = 320.0
        for period, phase, amp in wander:
            c += amp * math.sin(math.tau * t / period + phase)
        return c

    y, vy, t = 320.0, 0.0, 0.0
    next_tap = rng.uniform(0.10, 0.35)
    ys = []
    n = int(span_s / DT)
    for _ in range(n):
        if t >= next_tap:
            if y > corridor(t) + rng.uniform(-30.0, 30.0):
                vy = FLAP_V
            next_tap = t + min(0.85, max(0.17, rng.gauss(0.40, 0.15)))
        vy = min(vy + GRAVITY * DT, MAX_FALL)
        y += vy * DT
        if y < 46.0:
            y, vy = 46.0, 0.0
        elif y > 596.0:
            y, vy = 596.0, 0.0
        ys.append(y)
        t += DT
    return ys


def normalise(ys):
    """Percentile-clipped so the odd ceiling scrape doesn't flatten the whole
    envelope, and clamped so the uncharted tail keeps the charted amplitude."""
    s = sorted(ys)
    lo = s[int(len(s) * 0.004)]
    hi = s[int(len(s) * 0.996)]
    if hi - lo < 1e-6:
        hi = lo + 1.0
    return [min(1.0, max(0.0, (hi - v) / (hi - lo))) for v in ys]


# ═════════════════════════════════════════════════════════════════════════════
# panel
# ═════════════════════════════════════════════════════════════════════════════
FLATLINE_SCARLET = (255, 92, 74)


def _macaw_glyph(surf, cx, cy):
    """Tiny macaw silhouette: filled gold circle (head) + beak polygon."""
    r = 5
    pygame.draw.circle(surf, (0, 0, 12), (cx + 1, cy + 1), r + 1)
    pygame.draw.circle(surf, GOLD, (cx, cy), r)
    pygame.draw.circle(surf, BG, (cx, cy), r - 2)
    pygame.draw.polygon(surf, GOLD, [
        (cx + r - 1, cy - 1),
        (cx + r + 3, cy),
        (cx + r - 1, cy + 2),
    ])


def render_panel(run):
    surf = pygame.Surface((W, H))
    surf.fill(BG)

    span_s = run["seconds"] / run["death_frac"]
    ys = simulate(run["pillars"], span_s)
    norm = normalise(ys)
    n = len(norm)
    death_i = min(n - 1, int(run["seconds"] / DT))

    # The flatline owns the rest of its lane outright — letting the uncharted
    # dashes run underneath it would turn the one unambiguous mark on the
    # screen into a crossed-out one.
    dl, dx, dy = path_xy(death_i / n, norm[death_i])
    dx1 = min(LX1, dx + FLATLINE_MAX)
    resume = (dl + (dx1 - LX0) / LW) / LANES

    # ── uncharted tail: dashes keyed to screen x, so the gap stays 3 px wide
    #    whatever the time compression of the run is ──────────────────────────
    ghost = pygame.Surface((W, H), pygame.SRCALPHA)
    px, py, pl = None, None, None
    for i in range(int(resume * n), n):
        li, x, y = path_xy(i / n, norm[i])
        if px is not None and li == pl and int((px + x) * 0.5 / 3.0) % 2 == 0:
            pygame.draw.line(ghost, GOLD, (px, py), (x, y), 2)
        px, py, pl = x, y, li
    ghost.set_alpha(66)
    surf.blit(ghost, (0, 0))

    # ── lane baselines: the tape's own rule, faint enough to sit under the
    #    trace rather than box it in ────────────────────────────────────────
    rules = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(LANES):
        by = lane_top(i) + BASE_DY
        pygame.draw.line(rules, GOLD_MUTED, (LX0, by), (LX1, by), 1)
    rules.set_alpha(26)
    surf.blit(rules, (0, 0))

    # ── pillar ticks on the lane baselines ───────────────────────────────────
    ticks = pygame.Surface((W, H), pygame.SRCALPHA)
    trng = random.Random(run["pillars"] * 7 + 3)
    for k in range(run["pillars"]):
        tp = run["seconds"] * (k + 0.6) / run["pillars"] * trng.uniform(.985, 1.015)
        li, x, _ = path_xy(tp / span_s, 0.0)
        by = lane_top(li) + BASE_DY
        pygame.draw.line(ticks, GOLD_MUTED, (x, by), (x, by + 5), 2)
    ticks.set_alpha(120)
    surf.blit(ticks, (0, 0))

    # ── macaw glyph at trace origin ──────────────────────────────────────────
    _macaw_glyph(surf, LX0, lane_top(0) + BAND_HI + 5)

    # ── charted trace ────────────────────────────────────────────────────────
    px, py, pl = None, None, None
    for i in range(0, death_i + 1):
        li, x, y = path_xy(i / n, norm[i])
        if px is not None and li == pl:
            pygame.draw.line(surf, GOLD, (px, py), (x, y), 2)
        px, py, pl = x, y, li

    # ── coins ────────────────────────────────────────────────────────────────
    # Riding the raw sample would bury most dots inside the ~20 px-thick trace
    # band, so they sit above a short rolling peak of the envelope instead.
    coins = pygame.Surface((W, H), pygame.SRCALPHA)
    crng = random.Random(run["pillars"] * 31 + 11)
    win = 26
    for _ in range(int(run["seconds"] * 0.7)):
        ct = crng.uniform(0.0, run["seconds"])
        ci = min(death_i, int(ct / DT))
        peak = max(norm[max(0, ci - win):ci + win + 1])
        _, x, y = path_xy(ci / n, peak)
        r = 1 if crng.random() < 0.72 else 2
        pygame.draw.circle(coins, GOLD_PALE,
                           (int(x), int(y - crng.uniform(4.0, 9.0))), r)
    coins.set_alpha(180)
    surf.blit(coins, (0, 0))

    # ── phase rail — drawn after trace so it reads as an annotation ──────────
    rail = pygame.Surface((RAIL_W, RAIL_Y1 - RAIL_Y0), pygame.SRCALPHA)
    rh = rail.get_height()
    for i in range(rh):
        phase_t = i / max(1, rh - 1)
        pal = palette_for_phase(phase_t)
        c = pal["sky_mid"]
        # Lift night-range luma so the rail stays readable on the dark bg
        luma = int(0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2])
        if luma < 45:
            boost = (45 - luma) / 255.0
            c = (min(255, int(c[0] + boost * 80)),
                 min(255, int(c[1] + boost * 80)),
                 min(255, int(c[2] + boost * 100)))
        rail.fill(c, (0, i, RAIL_W, 1))
    rail.set_alpha(88)
    surf.blit(rail, (RAIL_X, RAIL_Y0))

    mk = pygame.Surface((RAIL_W + 8, 7), pygame.SRCALPHA)
    pygame.draw.circle(mk, GOLD_PALE, (RAIL_W // 2, 3), 3)
    pygame.draw.line(mk, GOLD_PALE, (RAIL_W + 1, 3), (RAIL_W + 7, 3), 1)
    mk.set_alpha(90)
    surf.blit(mk, (RAIL_X, RAIL_Y0 + int(run["phase"] * (rh - 1)) - 3))

    # ── the flatline: the one scarlet mark, and the whole death report ───────
    # Radial glow baked into RGB channels (BLEND_ADD ignores source alpha).
    gw, gh = int(dx1 - dx) + 28, 28
    glow_surf = pygame.Surface((gw, gh))
    glow_surf.fill((0, 0, 0))
    cx_local = gw // 2
    cy_local = gh // 2
    for gy in range(gh):
        for gx in range(gw):
            dist = abs(gy - cy_local) + 0.3 * abs(gx - cx_local)
            r_max = 14.0
            if dist < r_max:
                f = (1.0 - dist / r_max) ** 1.8
                peak = 0.18
                rc = int(FLATLINE_SCARLET[0] * f * peak)
                gc = int(FLATLINE_SCARLET[1] * f * peak)
                bc = int(FLATLINE_SCARLET[2] * f * peak)
                glow_surf.set_at((gx, gy), (rc, gc, bc))
    surf.blit(glow_surf, (int(dx) - 14, int(dy) - cy_local),
              special_flags=pygame.BLEND_ADD)
    # 3px solid flatline + terminal cap dot
    pygame.draw.line(surf, FLATLINE_SCARLET, (int(dx), int(dy)), (int(dx1), int(dy)), 3)
    pygame.draw.circle(surf, FLATLINE_SCARLET, (int(dx1), int(dy)), 3)

    # ── telemetry block ──────────────────────────────────────────────────────
    text(surf, "PILLAR", 11, GOLD_MUTED, (LX0, 474), spacing=2.6, alpha=190)
    num = gradient_numeral(str(run["pillars"]), 100,
                           [(0.00, (250, 235, 200)), (0.42, GOLD), (1.00, GOLD_DEEP)])
    surf.blit(num, (LX0 - 2, 486))

    y2 = 486 + num.get_height() + 22
    runs(surf, [(f"DAY {run['day']}", GOLD_MUTED),
                ("  ·  ", (120, 104, 62)),
                (run["clock"], GOLD_MUTED)], LX0, y2, 12)
    runs(surf, [("CAUSE ", (138, 118, 70)),
                (run["cause"], GOLD_MUTED)], LX0, y2 + 19, 12, spacing=1.2)

    return surf, {"span": span_s, "flaps": None, "death_x": dx, "lane": dl}


# ═════════════════════════════════════════════════════════════════════════════
RUNS = [
    dict(pillars=25,  day=1, clock="0:47", cause="GEYSER",
         seconds=47.0,  death_frac=0.184, phase=0.184),
    dict(pillars=180, day=2, clock="5:30", cause="SNOW",
         seconds=330.0, death_frac=0.880, phase=0.880),
]

MARGIN, GAP, HEADER = 4, 8, 32
SHEET_W = MARGIN * 2 + W * 2 + GAP
SHEET_H = MARGIN * 2 + HEADER + H


def main():
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill(BG)
    text(sheet, "BLACK BOX  ·  ROUND 2", 14, GOLD,
         (SHEET_W // 2, MARGIN + HEADER // 2), "center", spacing=3.0)

    info = []
    for k, run in enumerate(RUNS):
        panel, meta = render_panel(run)
        sheet.blit(panel, (MARGIN + k * (W + GAP), MARGIN + HEADER))
        info.append((run, meta))

    out = "/home/user/skybit/docs/flight_log_screen/black_box/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)

    print(f"saved {out}  {sheet.get_width()}x{sheet.get_height()}")
    for run, meta in info:
        print(f"  pillar {run['pillars']:>3}  span={meta['span']:6.1f}s  "
              f"s/px={run['seconds'] / (run['death_frac'] * PATH_PX):.3f}  "
              f"death lane={meta['lane']} x={meta['death_x']:.1f}")
    for p in ((4, 4), (SHEET_W // 2, 300), (MARGIN + 30, MARGIN + HEADER + 500)):
        print(f"  px{p} = {sheet.get_at(p)[:3]}")
    scar = sum(1 for x in range(SHEET_W) for y in range(SHEET_H)
               if sheet.get_at((x, y))[0] > 90 and sheet.get_at((x, y))[1] < 90
               and sheet.get_at((x, y))[2] < 80)
    print(f"  scarlet-ish px = {scar}")


if __name__ == "__main__":
    main()
