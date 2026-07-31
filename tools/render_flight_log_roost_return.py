#!/usr/bin/env python3
"""
roost-return  ·  flight-log progress screen  ·  round 1

The thesis: a run summary that reads as a *place the bird came home to*
rather than a chart of what she failed to reach.

Four rules carry it:

1. No container. The screen is one full-bleed night scene, so the stats sit
   inside the world instead of on a panel floating above it.
2. One light source, earned. Every ember in the rising column is a pillar the
   player actually cleared, so progress is literally the only thing glowing.
   Nothing on screen depicts the run that did not happen.
3. The dark sky above the column is the unreached day, and it is left empty on
   purpose — an invitation with room in it, not an empty progress bar.
4. Exactly one scarlet accent in the whole frame (the falling feather at the
   top of the column). With no competing warm-red anywhere, the death point
   needs no label to be found.

The horizon strip is kept under 8% of the canvas and under 90 alpha: it has to
say "dawn is coming" without becoming a second subject that fights the perch.
"""
import os
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
OUT_DIR = os.path.join(ROOT, "docs", "flight_log_screen", "roost_return")
OUT_PATH = os.path.join(OUT_DIR, "round_1.png")

W, H = 360, 640
SS = 3

# ── palette ──────────────────────────────────────────────────────────────────
SHEET_BG = (8, 8, 20)
GOLD = (240, 192, 64)
GOLD_DIM = (216, 184, 85)
GOLD_HOT = (255, 236, 186)
SCARLET = (172, 40, 32)
SCARLET_LIT = (214, 92, 74)
SCARLET_DEEP = (104, 22, 18)
SILHOUETTE = (20, 16, 12)
FAR_WING = (31, 25, 20)

SKY_STOPS = [
    (0.00, (5, 6, 15)),
    (0.42, (9, 10, 22)),
    (0.74, (16, 15, 30)),
    (1.00, (26, 22, 36)),
]

# Dawn read straight off the biome's sunrise family: cyan overhead, amber at
# the band's waist, rose where it meets the ground.
DAWN_STOPS = [
    (0.00, (84, 142, 168)),
    (0.46, (238, 186, 116)),
    (1.00, (214, 122, 112)),
]

# ── scene geometry ───────────────────────────────────────────────────────────
BAND_TOP, BAND_BOT = 556, 604          # 48px = 7.5% of the canvas
FAR_RIDGE_Y = 594
NEAR_RIDGE_Y = 608
LANDMARK_BASE = 596

PILLAR_X0, PILLAR_X1 = 230, 302
PILLAR_TOP = 470

BIRD_FX, BIRD_FY = 248, 476            # the foot the silhouette is built around
COL_X = 288
COL_BASE_Y = 464

LANDMARK_X = [24, 84, 128, 168, 200]

STAT_LEFT = 22
LABEL_Y = 418
NUM_TOP = 432
NUM_CAP = 94                           # hero numeral cap height (brief: >= 90)
NUM_MAX_W = 172                        # keeps a 3-figure score clear of the perch
SUB_Y = 546

_fonts: dict = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(a, b, t):
    return (int(lerp(a[0], b[0], t)), int(lerp(a[1], b[1], t)),
            int(lerp(a[2], b[2], t)))


def lerp_multi(stops, t):
    t = max(0.0, min(1.0, t))
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if t <= p1:
            span = max(1e-6, p1 - p0)
            return lerp_color(c0, c1, (t - p0) / span)
    return stops[-1][1]


def text(surf, s, size, color, topleft=None, center=None, midleft=None,
         track=0, alpha=255, shadow=(0, 0, 0, 150)):
    f = font(size)
    if track:
        # pygame exposes no tracking control, and these small gold labels only
        # read as signage when the letters are spaced.
        glyphs = [f.render(ch, True, color) for ch in s]
        tw = sum(g.get_width() for g in glyphs) + track * (len(s) - 1)
        img = pygame.Surface((max(1, tw), f.get_height()), pygame.SRCALPHA)
        x = 0
        for g in glyphs:
            img.blit(g, (x, 0))
            x += g.get_width() + track
    else:
        img = f.render(s, True, color)
    rect = img.get_rect()
    if topleft:
        rect.topleft = topleft
    elif center:
        rect.center = center
    elif midleft:
        rect.midleft = midleft
    if shadow:
        sh = img.copy()
        sh.fill((*shadow[:3], 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow[3])
        surf.blit(sh, (rect.x + 1, rect.y + 1))
    if alpha < 255:
        img = img.copy()
        img.set_alpha(alpha)
    surf.blit(img, rect)
    return rect


def soft_glow(radius, color, peak=110, falloff=2.0):
    """Additive halo with the falloff premultiplied into RGB.

    BLEND_ADD ignores the source alpha channel, so an alpha-ramped disc would
    land as a flat hard-edged circle.
    """
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        f = (1.0 - (r / radius) ** falloff) * (peak / 255.0)
        pygame.draw.circle(
            s, (int(color[0] * f), int(color[1] * f), int(color[2] * f), 255),
            (c, c), r)
    return s


def add_glow(dst, cx, cy, radius, color, peak, falloff=2.0):
    g = soft_glow(radius, color, peak, falloff)
    dst.blit(g, (int(cx) - radius - 1, int(cy) - radius - 1),
             special_flags=pygame.BLEND_ADD)


def falloff_mask(center, radius, inner=255, outer=40, gamma=1.3, cell=8):
    """Canvas-sized radial alpha ramp, built at 1/cell scale then stretched.

    The low-res grid keeps the canvas aspect exactly, so the ramp stays
    circular after the stretch — a square scratch surface would smear it into
    an ellipse and put the brightest rim light nowhere near the light source.
    """
    gw, gh = W // cell, H // cell
    m = pygame.Surface((gw, gh), pygame.SRCALPHA)
    cx, cy, rr = center[0] / cell, center[1] / cell, radius / cell
    for y in range(gh):
        for x in range(gw):
            t = min(1.0, math.hypot(x - cx, y - cy) / rr) ** gamma
            m.set_at((x, y), (255, 255, 255, int(lerp(inner, outer, t))))
    return m


def rim_light(shape, dx, dy, color, alpha=255):
    """Crescent of light along one contour of `shape`.

    Derived by subtracting the silhouette from a copy of itself pushed away
    from the light, which keeps the rim exactly on the shape's edge — a stroked
    outline drifts off it wherever the polygon is concave.
    """
    mask = pygame.mask.from_surface(shape, threshold=8)
    lit = mask.to_surface(setcolor=(*color, alpha), unsetcolor=(0, 0, 0, 0))
    cut = mask.to_surface(setcolor=(0, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
    lit.blit(cut, (dx, dy), special_flags=pygame.BLEND_RGBA_SUB)
    return lit


# ── sky ──────────────────────────────────────────────────────────────────────

def draw_sky(surf):
    for y in range(H):
        surf.fill(lerp_multi(SKY_STOPS, y / (H - 1)), pygame.Rect(0, y, W, 1))

    # Corner falloff, built small and scaled: it pulls the frame edges toward
    # black so the ember column keeps the only bright verticals.
    vg = pygame.Surface((24, 42), pygame.SRCALPHA)
    for y in range(42):
        for x in range(24):
            d = math.hypot((x - 11.5) / 11.5, (y - 26.0) / 26.0)
            a = int(96 * min(1.0, max(0.0, d - 0.45) / 0.85) ** 1.6)
            vg.set_at((x, y), (0, 0, 0, a))
    surf.blit(pygame.transform.smoothscale(vg, (W, H)), (0, 0))


def draw_stars(surf):
    rnd = random.Random(9184)
    for _ in range(64):
        x = rnd.randrange(4, W - 4)
        y = rnd.randrange(14, 440)
        # Faint and cool, so they describe depth without reading as embers.
        a = rnd.randint(18, 74) * (1.0 - y / 620.0)
        c = rnd.choice([(198, 210, 236), (226, 224, 236), (176, 196, 226)])
        lay = pygame.Surface((3, 3), pygame.SRCALPHA)
        pygame.draw.circle(lay, (*c, int(a)), (1, 1), 1 if rnd.random() < 0.22 else 0)
        surf.blit(lay, (x - 1, y - 1))


def draw_horizon_band(surf, sun_phase):
    band_h = BAND_BOT - BAND_TOP
    band = pygame.Surface((W, band_h), pygame.SRCALPHA)
    for y in range(band_h):
        t = y / (band_h - 1)
        c = lerp_multi(DAWN_STOPS, t)
        # Weighted hard toward the ridge: the landmarks stand in the upper two
        # thirds of the strip and need darker sky behind them to read.
        band.fill((*c, int(88 * t ** 2.1)), pygame.Rect(0, y, W, 1))
    surf.blit(band, (0, BAND_TOP))

    sun_x = int(sun_phase * W)
    sun_y = 592
    # Tight halo on purpose: a wide one merges with the lit landmarks either
    # side of it and the horizon becomes one undifferentiated smear.
    add_glow(surf, sun_x, sun_y, 15, (255, 196, 120), 38, 2.2)
    add_glow(surf, sun_x, sun_y, 7, (255, 224, 168), 66, 1.7)
    pygame.draw.circle(surf, (255, 226, 158), (sun_x, sun_y), 4)
    return sun_x, sun_y


def ridge_y(x, base, amp, freq, phase):
    return base + amp * math.sin(x * freq + phase) + amp * 0.4 * math.sin(x * freq * 2.7 + 1.9)


def draw_terrain(surf):
    far = [(x, ridge_y(x, FAR_RIDGE_Y, 3.0, 0.021, 0.4)) for x in range(0, W + 1, 4)]
    pygame.draw.polygon(surf, (17, 16, 26), far + [(W, H), (0, H)])
    near = [(x, ridge_y(x, NEAR_RIDGE_Y, 5.0, 0.013, 2.6)) for x in range(0, W + 1, 4)]
    pygame.draw.polygon(surf, (9, 8, 14), near + [(W, H), (0, H)])


# ── landmarks ────────────────────────────────────────────────────────────────

def lm_geyser(ov, cx, base, col, filled):
    pts = [(cx - 5, base), (cx + 5, base), (cx + 1, base - 20), (cx, base - 27)]
    if filled:
        pygame.draw.polygon(ov, col, [(p[0] * SS, p[1] * SS) for p in pts])
    else:
        pygame.draw.polygon(ov, col, [(p[0] * SS, p[1] * SS) for p in pts], SS)
    for ddx, ddy in ((-5, -5), (-3, -8), (3, -8), (5, -4)):
        pygame.draw.line(ov, col, ((cx) * SS, (base - 26) * SS),
                         ((cx + ddx) * SS, (base - 26 + ddy) * SS), SS)


def lm_lamp(ov, cx, base, col, filled):
    w = SS if not filled else 2 * SS
    pygame.draw.line(ov, col, (cx * SS, base * SS), (cx * SS, (base - 21) * SS), w)
    pygame.draw.line(ov, col, ((cx - 4) * SS, (base - 19) * SS),
                     ((cx + 4) * SS, (base - 19) * SS), SS)
    if filled:
        pygame.draw.circle(ov, col, (cx * SS, (base - 25) * SS), int(3.6 * SS))
    else:
        pygame.draw.circle(ov, col, (cx * SS, (base - 25) * SS), int(3.6 * SS), SS)
    pygame.draw.line(ov, col, ((cx - 4) * SS, base * SS),
                     ((cx + 4) * SS, base * SS), SS)


def lm_clown(ov, cx, base, col, filled):
    pts = [(cx - 11, base), (cx + 11, base), (cx, base - 20)]
    if filled:
        pygame.draw.polygon(ov, col, [(p[0] * SS, p[1] * SS) for p in pts])
    else:
        pygame.draw.polygon(ov, col, [(p[0] * SS, p[1] * SS) for p in pts], SS)
    pygame.draw.line(ov, col, (cx * SS, (base - 19) * SS), (cx * SS, (base - 28) * SS), SS)
    flag = [(cx, base - 28), (cx + 7, base - 25), (cx, base - 23)]
    pygame.draw.polygon(ov, col, [(p[0] * SS, p[1] * SS) for p in flag])


def lm_rain(ov, cx, base, col, filled):
    w = 2 * SS if filled else SS
    pygame.draw.arc(ov, col, pygame.Rect((cx - 11) * SS, (base - 28) * SS,
                                         22 * SS, 14 * SS),
                    0.0, math.pi, w)
    for i in range(5):
        x = cx - 8 + i * 4
        pygame.draw.line(ov, col, (x * SS, (base - 18) * SS),
                         ((x - 3) * SS, base * SS), SS)


def lm_snow(ov, cx, base, col, filled):
    pts = [(cx - 15, base), (cx - 8, base - 12), (cx - 4, base - 7),
           (cx + 2, base - 18), (cx + 8, base - 8), (cx + 15, base)]
    if filled:
        pygame.draw.polygon(ov, col, [(p[0] * SS, p[1] * SS) for p in pts])
    else:
        pygame.draw.polygon(ov, col, [(p[0] * SS, p[1] * SS) for p in pts], SS)
    pygame.draw.line(ov, col, ((cx - 1) * SS, (base - 15) * SS),
                     ((cx + 2) * SS, (base - 18) * SS), SS)
    pygame.draw.line(ov, col, ((cx + 2) * SS, (base - 18) * SS),
                     ((cx + 5) * SS, (base - 14) * SS), SS)


LANDMARKS = [lm_geyser, lm_lamp, lm_clown, lm_rain, lm_snow]


def draw_landmarks(surf, reached):
    glyphs = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    for fn, cx, ok in zip(LANDMARKS, LANDMARK_X, reached):
        col = (246, 228, 190, 204) if ok else (162, 176, 200, 77)
        fn(glyphs, cx, LANDMARK_BASE, col, ok)

    # Both states sit on the dawn strip, and a 1px unreached outline at 30%
    # dissolves into it without a keyline behind. Dilating the glyph mask keeps
    # the halo exactly on the shape, including the rain hatch.
    ink = pygame.mask.from_surface(glyphs, threshold=10).to_surface(
        setcolor=(4, 5, 10, 185), unsetcolor=(0, 0, 0, 0))
    ov = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    for dx in (-2, 0, 2):
        for dy in (-2, 0, 2):
            ov.blit(ink, (dx, dy))
    ov.blit(glyphs, (0, 0))
    surf.blit(pygame.transform.smoothscale(ov, (W, H)), (0, 0))

    # A reached landmark is a place she stood in; the faint warm lift under it
    # is what separates "visited" from "merely drawn brighter".
    for cx, ok in zip(LANDMARK_X, reached):
        if ok:
            add_glow(surf, cx, LANDMARK_BASE - 9, 10, (255, 206, 140), 18, 2.4)


# ── perch ────────────────────────────────────────────────────────────────────

CAP_PROFILE = [(0, 16), (7, 9), (16, 6), (26, 3), (37, 1), (46, 6), (54, 0),
               (63, 5), (72, 11)]


def cap_y(local_x):
    """Broken-top profile of the pillar, interpolated between the chipped
    corners so the bird's feet and the ember mouth land on the real stone."""
    pts = CAP_PROFILE
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        if local_x <= x1:
            t = (local_x - x0) / max(1e-6, (x1 - x0))
            return PILLAR_TOP + lerp(y0, y1, max(0.0, t))
    return PILLAR_TOP + pts[-1][1]


def build_pillar(ov):
    pw = PILLAR_X1 - PILLAR_X0
    top = [(PILLAR_X0 + x, PILLAR_TOP + y) for x, y in CAP_PROFILE]
    body = top + [(PILLAR_X1, H), (PILLAR_X0, H)]
    pygame.draw.polygon(ov, (28, 24, 26, 255), [(p[0] * SS, p[1] * SS) for p in body])

    # Vertical falloff: the stone goes to near-black at the base so the pillar
    # dissolves into the ground silhouette instead of ending in a hard line.
    shade = pygame.Surface((pw * SS, (H - PILLAR_TOP) * SS), pygame.SRCALPHA)
    for y in range(0, (H - PILLAR_TOP) * SS, SS):
        t = y / ((H - PILLAR_TOP) * SS)
        shade.fill((0, 0, 0, int(190 * t ** 0.8)), pygame.Rect(0, y, pw * SS, SS))
    clip = ov.subsurface(pygame.Rect(PILLAR_X0 * SS, PILLAR_TOP * SS,
                                     pw * SS, (H - PILLAR_TOP) * SS))
    mask = pygame.mask.from_surface(clip, threshold=8)
    keep = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    shade.blit(keep, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ov.blit(shade, (PILLAR_X0 * SS, PILLAR_TOP * SS))

    # Course seams — three is enough to say "stacked block" at this value range.
    for sy in (508, 552, 590):
        pygame.draw.line(ov, (10, 9, 12, 190), (PILLAR_X0 * SS, sy * SS),
                         (PILLAR_X1 * SS, sy * SS), SS)

    # The crack the light comes out of.
    crack = [(284, 471), (281, 486), (285, 498), (280, 512), (283, 527)]
    pygame.draw.lines(ov, (8, 7, 10, 230),
                      False, [(p[0] * SS, p[1] * SS) for p in crack], 2 * SS)
    pygame.draw.lines(ov, (196, 138, 58, 108),
                      False, [((p[0] - 1) * SS, p[1] * SS) for p in crack], SS)

    # Chipped rubble on the cap and a couple of fallen chips below the lip.
    for cx, cy, r in ((240, 486, 3), (260, 480, 2), (296, 492, 2)):
        pygame.draw.circle(ov, (24, 20, 22, 255), (cx * SS, cy * SS), r * SS)
    for cx, cy, r in ((216, 542, 2), (310, 566, 2), (221, 588, 3)):
        pygame.draw.circle(ov, (18, 16, 20, 255), (cx * SS, cy * SS), r * SS)


def build_bird(ov):
    """Settled macaw: folded wings, ruffled nape, tail hung over the broken lip.

    Everything is one near-black mass except the far wing, which is a single
    step lighter — without that break the folded wing disappears and the bird
    reads as a bag.
    """
    fx, fy = BIRD_FX, BIRD_FY

    def P(pts):
        return [((fx + x) * SS, (fy + y) * SS) for x, y in pts]

    def C(x, y, r):
        return ((fx + x) * SS, (fy + y) * SS), int(r * SS)

    # Tail — the long diagonal that stops the silhouette reading as an egg.
    pygame.draw.polygon(ov, (*SILHOUETTE, 255),
                        P([(-11, -19), (-3, -14), (-26, 12), (-33, 13),
                           (-31, 6), (-16, -11)]))
    pygame.draw.line(ov, (10, 8, 8, 255), P([(-14, -14)])[0],
                     P([(-29, 9)])[0], SS)

    # Far wing, one value step up.
    pygame.draw.polygon(ov, (*FAR_WING, 255),
                        P([(6, -33), (-6, -35), (-19, -28), (-25, -16),
                           (-19, -7), (-6, -5), (4, -12)]))

    # Body.
    pygame.draw.ellipse(ov, (*SILHOUETTE, 255),
                        pygame.Rect((fx - 20) * SS, (fy - 31) * SS,
                                    35 * SS, 28 * SS))
    # Head + ruffled nape.
    c, r = C(12, -31, 10.5)
    pygame.draw.circle(ov, (*SILHOUETTE, 255), c, r)
    for i, (rx, ry, rr) in enumerate(((3, -40, 4), (9, -43, 4.5), (16, -41, 4),
                                      (20, -37, 3.5))):
        cc, crr = C(rx, ry, rr)
        pygame.draw.circle(ov, (*SILHOUETTE, 255), cc, crr)
    # Beak — hooked, the one shape that says macaw at 30px.
    pygame.draw.polygon(ov, (*SILHOUETTE, 255),
                        P([(19, -35), (28, -33), (30, -28), (25, -24),
                           (20, -26)]))
    pygame.draw.polygon(ov, (10, 8, 8, 255),
                        P([(25, -24), (30, -28), (28, -22)]))

    # Near wing, folded, with a scalloped trailing edge for the ruffle.
    pygame.draw.polygon(ov, (*SILHOUETTE, 255),
                        P([(9, -31), (-3, -32), (-16, -25), (-22, -14),
                           (-15, -6), (-2, -5), (7, -12)]))
    for sx, sy, sr in ((-18, -9, 3.2), (-11, -6, 3.4), (-4, -5, 3.2),
                       (2, -7, 2.8)):
        cc, crr = C(sx, sy, sr)
        pygame.draw.circle(ov, (*SILHOUETTE, 255), cc, crr)
    pygame.draw.lines(ov, (12, 10, 10, 220), False,
                      P([(4, -27), (-8, -22), (-16, -15)]), SS)

    # Feet gripping the broken lip.
    for tx in (-4, 4):
        pygame.draw.line(ov, (*SILHOUETTE, 255),
                         P([(tx, -6)])[0], P([(tx, 1)])[0], 2 * SS)
        pygame.draw.line(ov, (*SILHOUETTE, 255),
                         P([(tx, 1)])[0], P([(tx + 4, 2)])[0], 2 * SS)
        pygame.draw.line(ov, (*SILHOUETTE, 255),
                         P([(tx, 1)])[0], P([(tx - 3, 2)])[0], 2 * SS)

    # Eye — a dot of the ember's own colour, so the light has a witness.
    cc, crr = C(15, -33, 1.5)
    pygame.draw.circle(ov, (238, 196, 96, 210), cc, crr)


def draw_perch(surf):
    # Backlight first, under the silhouette. A near-black bird on a near-black
    # sky has no shape without it — the column has to lift the air behind her
    # before she can be cut out of it.
    add_glow(surf, 266, 452, 46, (255, 172, 98), 16, 2.4)
    add_glow(surf, 284, 462, 30, (255, 186, 110), 18, 2.2)

    ov = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    build_pillar(ov)
    build_bird(ov)

    # Rim light comes off the ember column, up and to the right of the perch,
    # so the crescent sits on the head, breast and the pillar's right arris,
    # then dies out down the shaft and along the tail.
    # Offset is mostly horizontal: the column is a tall source standing beside
    # her, so right-facing contours take the light and up-facing ones only
    # graze it. A even diagonal offset lit her whole back, which read as a
    # second light behind the bird.
    rim = rim_light(ov, -2 * SS, 1 * SS, GOLD, 240)
    ramp = falloff_mask((COL_X, COL_BASE_Y - 18), 80, inner=255, outer=18,
                        gamma=1.05)
    rim.blit(pygame.transform.smoothscale(ramp, rim.get_size()), (0, 0),
             special_flags=pygame.BLEND_RGBA_MULT)
    ov.blit(rim, (0, 0))

    surf.blit(pygame.transform.smoothscale(ov, (W, H)), (0, 0))
    # Light leaking out of the crack, laid after the stone so it reads as
    # escaping rather than painted on. Kept low: the stone has to stay a dark
    # mass, or the bird loses the ground it is silhouetted against.
    add_glow(surf, 282, 477, 20, (255, 178, 84), 30, 2.3)
    add_glow(surf, 260, 472, 30, (255, 168, 92), 13, 2.6)


# ── ember column ─────────────────────────────────────────────────────────────

def ember_positions(count, spacing):
    rnd = random.Random(4242)
    out = []
    for i in range(count):
        # Per-index drift stops the column collapsing into a drawn line: it has
        # to read as N separate sources standing in for N separate pillars.
        out.append((COL_X + rnd.uniform(-6, 6), COL_BASE_Y - i * spacing))
    return out


def draw_embers(surf, positions, anchor_every=None):
    n = len(positions)
    for i, (x, y) in enumerate(positions):
        t = i / max(1, n - 1)
        a = lerp(1.0, 0.60, t)
        anchor = anchor_every and i > 0 and (i + 1) % anchor_every == 0
        halo_r = 13 if anchor else 8
        peak = int((92 if anchor else 62) * a)
        add_glow(surf, x, y, halo_r, (255, 186, 78), peak, 2.0)
        if anchor:
            ring = pygame.Surface((22, 22), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*GOLD, int(70 * a)), (11, 11), 7, 1)
            surf.blit(ring, (int(x) - 11, int(y) - 11))
        core = pygame.Surface((14, 14), pygame.SRCALPHA)
        cr = 3.0 if anchor else 2.2
        pygame.draw.circle(core, (*GOLD, int(255 * a)), (7, 7), int(cr) + 1)
        pygame.draw.circle(core, (*GOLD_HOT, int(255 * a)), (7, 7), max(1, int(cr) - 1))
        surf.blit(core, (int(x) - 7, int(y) - 7))


def draw_feather(surf, x, y):
    """The death marker. Elongated, canted off vertical so it reads as falling,
    and the only scarlet anywhere in the frame.

    It lands inside the ember glow, so it carries its own dark keyline —
    without one a 5px-wide scarlet shape is eaten by the warm bloom behind it.
    """
    fw, fh = 5, 16
    pad = 3
    s = pygame.Surface((fw * SS + pad * 2, fh * SS + pad * 2), pygame.SRCALPHA)
    cxs = s.get_width() / 2.0
    left, right = [], []
    steps = 26
    for i in range(steps + 1):
        t = i / steps
        yy = pad + t * fh * SS
        half = (fw * SS / 2.0) * (math.sin(math.pi * t) ** 0.66) * (1.0 - 0.42 * t)
        left.append((cxs - half, yy))
        right.append((cxs + half, yy))
    pygame.draw.polygon(s, (*SCARLET, 255), left + right[::-1])
    pygame.draw.line(s, (*SCARLET_DEEP, 235), (cxs, pad + 4), (cxs, pad + fh * SS), SS)
    pygame.draw.lines(s, (*SCARLET_LIT, 235), False, right[3:-5], SS)

    small = pygame.transform.smoothscale(s, (fw + pad, fh + pad))
    keyed = pygame.Surface((small.get_width() + 2, small.get_height() + 2),
                           pygame.SRCALPHA)
    ink = pygame.mask.from_surface(small, threshold=20).to_surface(
        setcolor=(10, 4, 6, 200), unsetcolor=(0, 0, 0, 0))
    for dx in (0, 1, 2):
        for dy in (0, 1, 2):
            keyed.blit(ink, (dx, dy))
    keyed.blit(small, (1, 1))
    rot = pygame.transform.rotozoom(keyed, -30, 1.0)
    surf.blit(rot, (int(x) - rot.get_width() // 2, int(y) - rot.get_height() // 2))


# ── stat block ───────────────────────────────────────────────────────────────

def hero_numeral(value):
    """Gold-gradient numeral set digit-by-digit on its own ink boxes.

    Two reasons not to render the string whole: font metrics leave enough
    leading to throw the block off by 20px, and the default sidebearings make a
    three-digit score wide enough to collide with the perch. Setting the ink
    boxes with one fixed optical gap keeps the cap height at spec while a
    "180" still clears the pillar.
    """
    f = font(150)
    digits = []
    for ch in str(value):
        img = f.render(ch, True, (255, 255, 255))
        box = img.get_bounding_rect()
        g = pygame.Surface(box.size, pygame.SRCALPHA)
        g.blit(img, (-box.x, -box.y))
        digits.append(g)
    src_cap = max(g.get_height() for g in digits)
    scale = NUM_CAP / src_cap
    gap = max(2, int(NUM_CAP * 0.11))
    scaled = [pygame.transform.smoothscale(
        g, (max(1, int(g.get_width() * scale)), max(1, int(g.get_height() * scale))))
        for g in digits]
    total = sum(g.get_width() for g in scaled) + gap * (len(scaled) - 1)
    glyph = pygame.Surface((total, NUM_CAP), pygame.SRCALPHA)
    x = 0
    for g in scaled:
        glyph.blit(g, (x, NUM_CAP - g.get_height()))
        x += g.get_width() + gap
    if total > NUM_MAX_W:
        # Condense rather than shrink: the cap height is the spec, and a
        # four-figure score must still clear the perch on the right.
        glyph = pygame.transform.smoothscale(glyph, (NUM_MAX_W, NUM_CAP))

    grad = pygame.Surface(glyph.get_size(), pygame.SRCALPHA)
    gw, gh = grad.get_size()
    for y in range(gh):
        t = y / max(1, gh - 1)
        c = lerp_multi([(0.0, (255, 232, 168)), (0.55, (240, 192, 64)),
                        (1.0, (176, 118, 38))], t)
        grad.fill((*c, 255), pygame.Rect(0, y, gw, 1))
    grad.blit(glyph, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return grad


def draw_stats(surf, pillar, sub):
    text(surf, "PILLAR", 12, GOLD_DIM, topleft=(STAT_LEFT, LABEL_Y), track=4,
         alpha=210, shadow=(0, 0, 0, 120))
    num = hero_numeral(pillar)
    # A weak bloom ties the numeral to the ember light instead of leaving it as
    # UI pasted on a night sky. Radius is capped rather than tracking the digit
    # count, or a three-digit score washes warm light across the whole horizon.
    add_glow(surf, STAT_LEFT + num.get_width() // 2, NUM_TOP + NUM_CAP // 2,
             88, (120, 84, 30), 22, 2.6)
    sh = num.copy()
    sh.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sh.set_alpha(150)
    surf.blit(sh, (STAT_LEFT + 3, NUM_TOP + 3))
    surf.blit(num, (STAT_LEFT, NUM_TOP))
    text(surf, sub, 14, GOLD_DIM, topleft=(STAT_LEFT + 2, SUB_Y), track=1,
         alpha=225, shadow=(0, 0, 0, 140))


# ── screen ───────────────────────────────────────────────────────────────────

def render_run(run):
    surf = pygame.Surface((W, H))
    draw_sky(surf)
    draw_stars(surf)
    draw_horizon_band(surf, run["phase"])
    draw_landmarks(surf, run["reached"])
    draw_terrain(surf)
    draw_perch(surf)

    pos = ember_positions(run["embers"], run["spacing"])
    draw_embers(surf, pos, run.get("anchor_every"))
    fx, fy = pos[-1]
    draw_feather(surf, fx + 11, fy - 4)

    draw_stats(surf, run["pillar"], run["sub"])
    return surf


RUN_A = dict(pillar=25, sub="DAY 1 · 0:47", phase=0.184, embers=25, spacing=9.5,
             reached=[True, False, False, False, False],
             caption="RUN A · PILLAR 25 · 1 EMBER / PILLAR")
RUN_B = dict(pillar=180, sub="DAY 2 · 5:30", phase=0.292, embers=36, spacing=8.6,
             reached=[True, True, True, True, True], anchor_every=10,
             caption="RUN B · PILLAR 180 · 1 EMBER / 5 PILLARS")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    panels = [render_run(RUN_A), render_run(RUN_B)]

    margin, gap, header_h, cap_h = 8, 8, 34, 20
    sw = margin * 2 + W * 2 + gap
    sh = margin + header_h + H + cap_h + margin
    sheet = pygame.Surface((sw, sh))
    sheet.fill(SHEET_BG)

    text(sheet, "ROOST RETURN · ROUND 1", 18, GOLD,
         center=(sw // 2, margin + header_h // 2), track=2, shadow=None)

    for i, p in enumerate(panels):
        x = margin + i * (W + gap)
        y = margin + header_h
        sheet.blit(p, (x, y))
        pygame.draw.rect(sheet, (96, 78, 40), (x - 1, y - 1, W + 2, H + 2), 1)
        cap = [RUN_A, RUN_B][i]["caption"]
        text(sheet, cap, 11, GOLD_DIM, center=(x + W // 2, y + H + cap_h // 2),
             track=1, alpha=200, shadow=None)

    pygame.image.save(sheet, OUT_PATH)
    print(f"saved {OUT_PATH} {sheet.get_size()}")
    for name, xy in (("sheet bg", (4, 4)),
                     ("A sky top", (margin + 180, margin + header_h + 30)),
                     ("A ember base", (margin + int(COL_X), margin + header_h + COL_BASE_Y)),
                     ("A numeral", (margin + 40, margin + header_h + NUM_TOP + 60)),
                     ("A horizon", (margin + 300, margin + header_h + 590)),
                     ("B ember base", (margin + W + gap + int(COL_X),
                                       margin + header_h + COL_BASE_Y))):
        print(f"  {name:14s} {xy} -> {sheet.get_at(xy)[:3]}")


if __name__ == "__main__":
    main()
