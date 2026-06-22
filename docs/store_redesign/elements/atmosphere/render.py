"""
CONSTELLATION store — ATMOSPHERE element (the night-sky canvas).

This is the backdrop every store card sits on: a multi-stop indigo->violet
nebula, a soft central violet bloom + edge vignette for depth, a three-strata
starfield (faint far dust, mid stars, a few bright 4-point sparkle stars) and
tapered gold constellation hairlines with glowing node stars.

Authored resolution-independently at SS=4 (the THEME crispness lever) and
downscaled once to 360x640 so multi-stop gradients stay band-free and every
hairline/sparkle resolves clean. Pure pygame, both build targets safe.

Reuses the constellation_hi pipeline DNA: `multistop_v`, `soft_glow`, the
SS metric helper, the locked BG_STOPS + NEBULA_GLOW from THEME.

Deliberately calm: it must read as a premium backdrop, NOT compete with the
cards that land on top. Variants trade bloom intensity / star density /
constellation prominence so the art-director can pick the right restraint.
"""
import os
import sys
import math
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from game.draw import lerp_color
from game.hud import _font, _GOLD_BRIGHT


# ── supersample (THEME lever) ─────────────────────────────────────────────────
SS = 4
DW, DH = W * SS, H * SS


def m(v):
    return int(round(v * SS))


def font(size):
    return _font(max(1, int(round(size * SS))), True)


# ── palette (locked CONSTELLATION bg stops + central bloom) ───────────────────
BG_STOPS = [
    (0.00, (6, 7, 24)),
    (0.30, (11, 11, 40)),
    (0.55, (18, 16, 58)),
    (0.78, (26, 20, 72)),
    (1.00, (14, 12, 46)),
]
NEBULA_GLOW = (70, 60, 150)
GOLD_NODE = (255, 234, 180)        # node-star core
GOLD_THREAD = (208, 182, 118)      # constellation hairline tint
STAR_TINTS = [(255, 252, 240), (220, 226, 255), (255, 240, 210)]


# ── reused primitives (constellation_hi DNA) ──────────────────────────────────
def multistop_v(w, h, stops):
    """Vertical multi-stop gradient — per-row lerp so there is no banding."""
    surf = pygame.Surface((w, h))
    n = len(stops)
    for y in range(h):
        f = y / max(1, h - 1)
        seg = 0
        while seg < n - 2 and f > stops[seg + 1][0]:
            seg += 1
        t0, c0 = stops[seg]
        t1, c1 = stops[seg + 1]
        local = 0.0 if t1 == t0 else (f - t0) / (t1 - t0)
        pygame.draw.line(surf, lerp_color(c0, c1, max(0.0, min(1.0, local))),
                         (0, y), (w - 1, y))
    return surf


def soft_glow(surf, cx, cy, radius, color, peak_alpha, layers=8, gamma=1.8):
    """Additive feathered glow — many layers keep the falloff smooth at SS.
    Used for small point lights (sparkles, node stars) where the additive
    stacking reads as a tight halo."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** gamma)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


def radial_bloom(cx, cy, radius, color, peak_alpha, gamma=2.6):
    """A SINGLE smooth radial bloom field (per-radius alpha, NOT stacked additive
    layers — those step into visible rings + blow the core to white). The alpha
    falls off as (1 - d/r)**gamma from a low peak, so the bloom is a calm violet
    haze that never reads as a hard disc. Returned as its own SRCALPHA surface to
    blit normally over the nebula (alpha-composited, so it tints rather than
    accumulates toward white)."""
    d = radius * 2
    field = pygame.Surface((d, d), pygame.SRCALPHA)
    c = radius
    for rr in range(radius, 0, -1):
        t = rr / radius
        a = int(peak_alpha * (1.0 - t) ** gamma)
        if a <= 0:
            continue
        pygame.draw.circle(field, (*color, a), (c, c), rr)
    out = pygame.Surface((DW, DH), pygame.SRCALPHA)
    out.blit(field, (cx - c, cy - c))
    return out


# ── atmosphere layers ─────────────────────────────────────────────────────────
def _nebula(bloom_peak, bloom_r=200, vig_peak=70):
    """Locked nebula gradient + a soft central violet bloom and an edge vignette.
    The bloom sits a touch above centre (where the grid breathes) so the screen
    has a luminous heart without washing out the card lane. Vignette darkens the
    rim so the eye settles inward — a premium-backdrop tell."""
    surf = pygame.Surface((DW, DH))
    surf.blit(multistop_v(DW, DH, BG_STOPS), (0, 0))
    # broad central bloom — ONE smooth radial field (alpha-composited) so it
    # tints the sky violet rather than stacking additively toward a white disc.
    surf.blit(radial_bloom(DW // 2, int(DH * 0.42), m(bloom_r),
                           NEBULA_GLOW, bloom_peak), (0, 0))
    # radial-ish vignette authored as a vertical falloff toward both edges plus
    # corner darkening, so the rim recedes without a visible ring.
    vig = pygame.Surface((DW, DH), pygame.SRCALPHA)
    cx, cy = DW * 0.5, DH * 0.44
    maxd = math.hypot(cx, cy)
    for y in range(DH):
        dv = abs(y - DH * 0.5) / (DH * 0.5)
        a = int(vig_peak * dv ** 1.5)
        pygame.draw.line(vig, (0, 0, 6, a), (0, y), (DW, y))
    surf.blit(vig, (0, 0))
    # gentle corner AO for the four corners (premium framing, very low alpha)
    corner = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for (ox, oy) in ((0, 0), (DW, 0), (0, DH), (DW, DH)):
        soft_glow(corner, ox, oy, m(150), (0, 0, 8), 90, layers=8, gamma=1.4)
    surf.blit(corner, (0, 0))
    return surf


def _starfield(seed, density=1.0, sparkles=14, sparkle_scale=1.0):
    """Three brightness/size strata for depth + a few 4-point sparkle stars.
    Stratum 1 = faint far dust (tiny, dim), stratum 2 = mid stars, stratum 3 =
    near foreground stars (larger, brighter, each with a faint glow halo).
    The downscale turns the oversized dots into clean sub-pixel points."""
    rnd = random.Random(seed)
    stars = pygame.Surface((DW, DH), pygame.SRCALPHA)
    strata = (
        (int(190 * density), 0.4, 0.9, 26, 80),     # far dust
        (int(78 * density), 0.9, 1.6, 64, 140),     # mid
        (int(26 * density), 1.4, 2.6, 120, 210),    # near
    )
    for idx, (n, rmin, rmax, amin, amax) in enumerate(strata):
        for _ in range(n):
            x = rnd.randint(0, DW)
            y = rnd.randint(0, DH)
            r = m(rnd.uniform(rmin, rmax))
            a = rnd.randint(amin, amax)
            tint = rnd.choice(STAR_TINTS)
            if idx == 2:
                # near stars get a faint halo so they read as glowing points
                soft_glow(stars, x, y, int(r * 2.4), tint, a // 3, layers=4)
            pygame.draw.circle(stars, (*tint, a), (x, y), max(1, int(r)))
    # 4-point sparkle stars — the premium twinkle accents
    for _ in range(sparkles):
        x = rnd.randint(m(18), DW - m(18))
        y = rnd.randint(m(18), DH - m(18))
        L = m(rnd.uniform(3, 6) * sparkle_scale)
        a = rnd.randint(130, 220)
        col = (255, 246, 214, a)
        tw = max(1, m(0.7))
        # long axis + a shorter diagonal cross for a soft 4/8-point glint
        pygame.draw.line(stars, col, (x - L, y), (x + L, y), tw)
        pygame.draw.line(stars, col, (x, y - L), (x, y + L), tw)
        d = int(L * 0.5)
        faint = (255, 246, 214, a // 2)
        pygame.draw.line(stars, faint, (x - d, y - d), (x + d, y + d), max(1, m(0.5)))
        pygame.draw.line(stars, faint, (x - d, y + d), (x + d, y - d), max(1, m(0.5)))
        soft_glow(stars, x, y, m(3.5 * sparkle_scale), (255, 244, 210), 90, layers=5)
        pygame.draw.circle(stars, (255, 252, 240, 240), (x, y), max(1, m(0.9)))
    return stars


def _constellations(thread_alpha=46, node_glow=90, thread_w=0.9):
    """Tapered gold constellation hairlines with glowing node stars. The lines
    fade toward their endpoints (drawn as alpha-stepped segments) so each thread
    reads as a deliberate, drawn-on element — not a stray hard line. Two chains
    plus one bridge, with node stars at every vertex."""
    lines = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pts = [(40, 250), (96, 200), (152, 256), (216, 214), (300, 270),
           (60, 470), (140, 524), (250, 480), (322, 540)]
    chains = [pts[0:5], pts[5:9], [pts[4], pts[7]]]

    def taper_line(a, b):
        # draw the segment as N sub-segments whose alpha eases up at the middle
        # and down at both ends => a hairline that tapers to nothing at vertices.
        ax, ay = m(a[0]), m(a[1])
        bx, by = m(b[0]), m(b[1])
        steps = 28
        for i in range(steps):
            t0 = i / steps
            t1 = (i + 1) / steps
            tm = (t0 + t1) * 0.5
            # ease: bright mid, faint ends
            fade = math.sin(tm * math.pi) ** 0.7
            a_seg = int(thread_alpha * fade)
            if a_seg <= 0:
                continue
            x0 = ax + (bx - ax) * t0
            y0 = ay + (by - ay) * t0
            x1 = ax + (bx - ax) * t1
            y1 = ay + (by - ay) * t1
            pygame.draw.line(lines, (*GOLD_THREAD, a_seg),
                             (x0, y0), (x1, y1), max(1, m(thread_w)))

    for chain in chains:
        for a, b in zip(chain, chain[1:]):
            taper_line(a, b)
    # node stars — glow halo + a small hot core at each unique vertex
    for px, py in dict.fromkeys(pts):
        soft_glow(lines, m(px), m(py), m(3.4), GOLD_NODE, node_glow, layers=5)
        pygame.draw.circle(lines, (*GOLD_NODE, 235), (m(px), m(py)), max(1, m(1.2)))
        pygame.draw.circle(lines, (255, 250, 226, 255), (m(px), m(py)), max(1, m(0.5)))
    return lines


def compose(bloom_peak, density, sparkles, thread_alpha, node_glow,
            seed=70, bloom_r=200, thread_w=0.9, sparkle_scale=1.0):
    """Assemble a full atmosphere canvas at device (SS) resolution."""
    surf = _nebula(bloom_peak, bloom_r=bloom_r)
    surf.blit(_constellations(thread_alpha, node_glow, thread_w),
              (0, 0), special_flags=pygame.BLEND_ADD)
    surf.blit(_starfield(seed, density, sparkles, sparkle_scale),
              (0, 0), special_flags=pygame.BLEND_ADD)
    return surf


def downscale(dev_surf):
    return pygame.transform.smoothscale(dev_surf, (W, H))


# ── variants ──────────────────────────────────────────────────────────────────
# Each trades restraint on a different axis. A is the balanced hero.
VARIANTS = {
    "A_balanced":   dict(bloom_peak=82, density=1.0, sparkles=14,
                         thread_alpha=46, node_glow=90, bloom_r=210),
    "B_deep_calm":  dict(bloom_peak=54, density=0.78, sparkles=9,
                         thread_alpha=34, node_glow=70, bloom_r=185,
                         thread_w=0.8, sparkle_scale=0.9),
    "C_luminous":   dict(bloom_peak=120, density=1.18, sparkles=20,
                         thread_alpha=58, node_glow=120, bloom_r=240,
                         sparkle_scale=1.12),
    "D_constel":    dict(bloom_peak=76, density=0.92, sparkles=15,
                         thread_alpha=78, node_glow=140, bloom_r=205,
                         thread_w=1.05, sparkle_scale=1.0),
}


def _label(surf, text, x, y):
    f = font(9)
    base = f.render(text, True, (255, 255, 255))
    sh = f.render(text, True, (0, 0, 0))
    surf.blit(sh, (x + m(0.8), y + m(0.8)))
    surf.blit(base, (x, y))


def main():
    # render every variant at SS, downscale each to 360x640 crisp
    rendered = {name: downscale(compose(**cfg)) for name, cfg in VARIANTS.items()}

    # sheet: hero (variant A) large on the left, the other three stacked right,
    # all at native 360x640 (SS-crisp). Authored at SS then downscaled so the
    # labels + frames are clean too.
    pad = m(16)
    gap = m(14)
    hero_w, hero_h = m(W), m(H)
    small_w, small_h = m(W * 0.62), m(H * 0.62)
    col2_x = pad + hero_w + gap
    sheet_w = col2_x + small_w + pad
    sheet_h = pad + max(hero_h, small_h * 3 + gap * 2) + m(40) + pad
    sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
    sheet.fill((18, 18, 26, 255))

    title_f = font(14)
    sheet.blit(title_f.render("CONSTELLATION store - ATMOSPHERE (night-sky canvas)",
                              True, (236, 224, 196)), (pad, m(6)))

    top = pad + m(26)

    def framed(img, x, y, w, h, label):
        scaled = pygame.transform.smoothscale(img, (w, h))
        sheet.blit(scaled, (x, y))
        pygame.draw.rect(sheet, (*_GOLD_BRIGHT, 200), (x, y, w, h),
                         width=max(1, m(1)))
        _label(sheet, label, x + m(4), y + h + m(3))

    # hero = balanced
    framed(rendered["A_balanced"], pad, top, hero_w, hero_h,
           "A balanced (hero)  bloom 60 / density 1.0 / sparkle 14 / thread 46")
    # stacked alternates
    names = ["B_deep_calm", "C_luminous", "D_constel"]
    descs = [
        "B deep+calm  low bloom, sparse stars (max card legibility)",
        "C luminous  big bloom, dense stars + sparkles",
        "D constellation-forward  brighter threads + node stars",
    ]
    for i, (nm, ds) in enumerate(zip(names, descs)):
        y = top + i * (small_h + gap + m(16))
        framed(rendered[nm], col2_x, y, small_w, small_h, ds)

    out = pygame.transform.smoothscale(
        sheet, (sheet.get_width() // SS, sheet.get_height() // SS))
    out_path = os.path.join(_HERE, "round_1.png")
    pygame.image.save(out, out_path)
    print("saved", out_path)


if __name__ == "__main__":
    main()
