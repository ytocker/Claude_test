"""10 procedural full-band SKY designs for Skybit's biome backdrop.

The shipped sky is a flat 4-stop vertical gradient. This set explores ten
genuinely distinct repaints that rise to the branch's shan-shui / ink art
direction while still reading correctly through all 7 times of day. Each
function PAINTS the whole sky region (0..ground_y) onto an opaque surface,
so the gradient base lives inside the variant rather than being assumed.

Drop-in signature for every variant::

    def draw_sky_<name>(surf, w, h, ground_y, palette, phase): ...

`palette` is the already-blended biome dict (sky_top/sky_mid/sky_bot/
horizon/mtn_*/ground_*/stone_*/foliage_*/star_alpha). New disc / glow
tints are read DEFENSIVELY via `palette.get(key, default_derived_from_
existing_keys)` so the candidates run against the CURRENT biome keyframes
unchanged — no biome.py edits required this round. `phase` (0..1) drives
sun/moon disc placement and the day/night branch.

Constraints honoured: pure pygame ops (line/circle/polygon/ellipse/blit,
SRCALPHA scratch surfaces, BLEND_ADD glows), reuse of
game.draw.make_gradient_surface / lerp_color helpers, no surfarray, no
gfxdraw, no full-surface set_at loops.

Research anchors:
  Shan-shui atmospheric perspective + negative-space mist:
    https://www.newworldencyclopedia.org/entry/Shan_shui
  Ruyi / lingzhi scalloped cloud bands (yunjian, xiangyun):
    https://en.wikipedia.org/wiki/Xiangyun_(Auspicious_clouds)
    https://en.wikipedia.org/wiki/Yunjian
"""
from __future__ import annotations

import math
import pygame

from game.draw import (
    make_gradient_surface,
    lerp_color,
    lerp_color_multi,
)


# ── shared helpers ───────────────────────────────────────────────────────────

def _is_night(palette) -> bool:
    """Luminance gate on sky_top — the deep-blue night/dusk keyframes sit
    well under this threshold, so one test routes both the disc choice and
    the warm-vs-cool accent for every variant."""
    t = palette['sky_top']
    lum = (t[0] * 299 + t[1] * 587 + t[2] * 114) / 1000
    return lum < 60


def _star_alpha(palette) -> int:
    return int(palette.get('star_alpha', 0))


def _base_gradient(surf, w, ground_y, palette, top_bias=0.0):
    """Paint the project's canonical 4-stop vertical sky as the opaque base.
    `top_bias` lets a variant darken the zenith slightly for extra value
    range without inventing a palette key."""
    top = palette['sky_top']
    if top_bias:
        top = lerp_color(top, (0, 0, 0), top_bias)
    stops = [
        (0.0, top),
        (0.45, palette['sky_mid']),
        (0.85, palette['sky_bot']),
        (1.0, palette['horizon']),
    ]
    grad = make_gradient_surface(w, ground_y, stops)
    surf.blit(grad, (0, 0))


def _sun_color(palette):
    """Warm disc tint. Derived from horizon (already warm at most phases)
    pushed toward white so the disc core reads as a light source."""
    return palette.get('sun_color', lerp_color(palette['horizon'], (255, 255, 240), 0.45))


def _moon_color(palette):
    return palette.get('moon_color', lerp_color(palette['horizon'], (235, 240, 255), 0.6))


def _glow_color(palette):
    """Atmospheric glow tint around the luminary — horizon hue, lightened."""
    return palette.get('glow_color', lerp_color(palette['horizon'], (255, 250, 235), 0.25))


def _cloud_tint(palette):
    """Soft body tint for cloud strata — sky_bot lifted toward white by day,
    toward the cool horizon by night so banks don't glow against deep blue."""
    if _is_night(palette):
        return palette.get('cloud_tint', lerp_color(palette['sky_bot'], palette['horizon'], 0.5))
    return palette.get('cloud_tint', lerp_color(palette['sky_bot'], (255, 255, 255), 0.6))


def _disc_xy(w, ground_y, phase):
    """Map phase (0..1) to a luminary position arcing across the sky.

    phase 0 (day) → high mid; the arc dips toward the horizon around
    sunset/sunrise and rides low/offset at night. The x sweep is gentle so
    the disc never collides with the canvas edges at 360 px wide."""
    # A single cosine arc: highest near day, lowest near night.
    ax = w * (0.30 + 0.45 * (0.5 + 0.5 * math.sin(phase * math.tau - 1.2)))
    arc = math.sin(phase * math.tau + 0.4)  # +1 high, -1 low
    ay = ground_y * (0.52 - 0.34 * arc)
    return int(ax), int(ay)


def _radial_glow(surf, cx, cy, radius, color, alpha_center=150, falloff=1.9):
    """Local additive radial glow drawn into a scratch surface then blitted
    BLEND_ADD — same pattern as draw.make_glow_surface but inlined so a
    variant can pick its own falloff without polluting the global glow
    cache with one-off keys."""
    size = radius * 2 + 2
    g = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        if a <= 0:
            continue
        pygame.draw.circle(g, (*color, a), (c, c), r)
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_ADD)


def _scatter_stars(surf, w, ground_y, palette):
    """Re-create the shipped star sprinkle so night variants keep parity
    with the live sky. Seeded by w only, like the original, so star layout
    is phase-stable."""
    sa = _star_alpha(palette)
    if sa <= 0:
        return
    import random as _r
    rng = _r.Random(w * 7919)
    band = int(ground_y * 0.72)
    n = 60 if sa > 180 else 30
    for _ in range(n):
        sx = rng.randint(0, w - 1)
        sy = rng.randint(0, band)
        sz = rng.choice((1, 1, 1, 2))
        pygame.draw.circle(surf, (255, 255, 255, sa), (sx, sy), sz)
    for _ in range(6):
        sx = rng.randint(0, w - 1)
        sy = rng.randint(0, band)
        pygame.draw.circle(surf, (255, 240, 200, min(255, sa + 20)), (sx, sy), 2)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 1 — Shan-shui ink wash
# Layered atmospheric perspective: stacked soft ink-diffusion bands of
# decreasing density toward the zenith, with a negative-space mist gap that
# floats above the horizon so distance reads as void rather than gradient.
#   https://www.newworldencyclopedia.org/entry/Shan_shui
# ─────────────────────────────────────────────────────────────────────────────

def draw_sky_inkwash(surf, w, h, ground_y, palette, phase):
    _base_gradient(surf, w, ground_y, palette, top_bias=0.06)
    night = _is_night(palette)

    # Ink tone: at day the wash leans the sky toward a paler graded haze;
    # at night toward a denser indigo so the bands still read as ink.
    deep = lerp_color(palette['sky_top'], (0, 0, 0), 0.18)
    pale = lerp_color(palette['sky_mid'], (255, 255, 255), 0.30 if not night else 0.10)

    # Six diffusion bands, densest low (foreground ridge haze) thinning up.
    # Each band is a soft horizontal ellipse smear — the pomo "broken ink"
    # read comes from overlapping low-alpha sweeps rather than hard stops.
    n_bands = 6
    band_layer = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    for i in range(n_bands):
        t = i / (n_bands - 1)
        by = int(ground_y * (0.30 + 0.62 * t))
        col = lerp_color(pale, deep, t)
        # Lower bands are wider + darker; alpha decays upward so the zenith
        # keeps the negative-space openness shan-shui prizes.
        bh = int(ground_y * (0.10 + 0.05 * (1 - t)))
        a = int(70 * (0.4 + 0.6 * t))
        rect = pygame.Rect(-w // 4, by - bh // 2, int(w * 1.5), bh)
        pygame.draw.ellipse(band_layer, (*col, a), rect)
    surf.blit(band_layer, (0, 0))

    # Negative-space mist gap — a bright horizontal void band just above the
    # horizon where the ridges will sit, the signature "scenery dissolving
    # into mist" move. Tinted by horizon so it carries the time-of-day glow.
    mist = lerp_color(palette['horizon'], (255, 255, 255), 0.35)
    mist_layer = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    my = int(ground_y * 0.78)
    for k in range(5):
        a = int(60 * (1 - k / 5))
        hh = int(ground_y * (0.04 + 0.02 * k))
        pygame.draw.ellipse(mist_layer, (*mist, a),
                            pygame.Rect(-w // 4, my - hh // 2, int(w * 1.5), hh))
    surf.blit(mist_layer, (0, 0))

    _scatter_stars(surf, w, ground_y, palette)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 2 — Ruyi cloud strata
# Horizontal lingzhi/ruyi cloud belts with scalloped, rim-lit lower edges —
# the yunjian "auspicious cloud" band rendered as stacked sky strata.
#   https://en.wikipedia.org/wiki/Yunjian
# ─────────────────────────────────────────────────────────────────────────────

def draw_sky_ruyi_strata(surf, w, h, ground_y, palette, phase):
    _base_gradient(surf, w, ground_y, palette)
    night = _is_night(palette)
    body = _cloud_tint(palette)
    rim = _sun_color(palette) if not night else _moon_color(palette)

    # Three belts at three depths; each is a horizontal band whose lower
    # edge is a chain of ruyi scallops (overlapping arcs) and whose upper
    # edge fades soft. Lower belts are larger-scalloped + denser.
    belts = [
        (0.34, 26, 0.55, 8),
        (0.55, 34, 0.72, 6),
        (0.74, 46, 0.85, 5),
    ]
    for (yf, lobe_r, alpha_f, _depth) in belts:
        cy = int(ground_y * yf)
        layer = pygame.Surface((w, ground_y), pygame.SRCALPHA)
        band_a = int(150 * alpha_f)
        # Soft band body above the scallop line.
        pygame.draw.rect(layer, (*body, band_a),
                         pygame.Rect(0, cy - lobe_r, w, lobe_r))
        # Scalloped lower rim — overlapping lobes give the lingzhi-head
        # ruyi profile; phase shifts the lobe centres per belt so belts
        # don't stack into vertical seams.
        step = int(lobe_r * 1.55)
        off = int((phase * 80 + yf * 120)) % step
        x = -off
        while x < w + lobe_r:
            pygame.draw.circle(layer, (*body, band_a), (x, cy), lobe_r)
            # paired smaller inner lobe for the double-curl ruyi silhouette
            pygame.draw.circle(layer, (*body, band_a),
                               (x + step // 2, cy - lobe_r // 3),
                               int(lobe_r * 0.6))
            x += step
        surf.blit(layer, (0, 0))
        # Rim light tracing the scallop crests — thin bright arcs.
        rim_a = 170 if not night else 110
        x = -off
        while x < w + lobe_r:
            pygame.draw.arc(surf, (*rim, rim_a),
                            pygame.Rect(x - lobe_r, cy - lobe_r,
                                        lobe_r * 2, lobe_r * 2),
                            math.radians(200), math.radians(340), 2)
            x += step

    _scatter_stars(surf, w, ground_y, palette)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 3 — Gold-leaf byōbu folding screen
# Flat stylised colour bands (the byōbu register) + a fine gold-fleck
# shimmer drifting across the surface + a low simplified sun/moon disc.
#   https://en.wikipedia.org/wiki/Folding_screen
# ─────────────────────────────────────────────────────────────────────────────

def draw_sky_goldleaf_byobu(surf, w, h, ground_y, palette, phase):
    night = _is_night(palette)
    # Flat stylised bands — 4 hard registers instead of a smooth gradient,
    # the defining byōbu look. Each band is one flat fill.
    bands = [
        (0.00, 0.30, palette['sky_top']),
        (0.30, 0.55, lerp_color(palette['sky_top'], palette['sky_mid'], 0.7)),
        (0.55, 0.80, palette['sky_mid']),
        (0.80, 1.00, palette['sky_bot']),
    ]
    for (y0, y1, col) in bands:
        pygame.draw.rect(surf, col,
                         pygame.Rect(0, int(ground_y * y0), w,
                                     int(ground_y * (y1 - y0)) + 1))
    # A warm horizon register so the screen sits on a gilded ground line.
    pygame.draw.rect(surf, palette['horizon'],
                     pygame.Rect(0, int(ground_y * 0.93), w,
                                 ground_y - int(ground_y * 0.93) + 1))

    # Low disc — simplified flat sun/moon near the horizon band, the calm
    # focal point of a folding-screen composition.
    dx, dy = _disc_xy(w, ground_y, phase)
    dy = max(dy, int(ground_y * 0.30))
    disc = _moon_color(palette) if night else _sun_color(palette)
    _radial_glow(surf, dx, dy, 46, _glow_color(palette), 90, 2.2)
    pygame.draw.circle(surf, disc, (dx, dy), 22)
    pygame.draw.circle(surf, lerp_color(disc, (255, 255, 255), 0.4), (dx, dy), 22, 2)

    # Gold-fleck shimmer — sparse drifting specks evoking applied gold leaf.
    # Seeded by a coarse phase bucket so flecks drift slowly rather than
    # boiling frame-to-frame. Warm by day, cool-silver by night.
    import random as _r
    fleck = (255, 225, 140) if not night else (200, 215, 235)
    drift = int(phase * 40)
    rng = _r.Random(1337)
    flecks = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    for _ in range(140):
        fx = (rng.randint(0, w - 1) + drift) % w
        fy = rng.randint(0, int(ground_y * 0.92))
        a = rng.randint(40, 130)
        sz = rng.choice((1, 1, 2))
        pygame.draw.circle(flecks, (*fleck, a), (fx, fy), sz)
    surf.blit(flecks, (0, 0))

    _scatter_stars(surf, w, ground_y, palette)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 4 — Sunburst / god-rays
# Soft radial light shafts fanning from the sun/moon disc through haze —
# additive wedges of decreasing alpha, plus a bloomed disc core.
#   https://en.wikipedia.org/wiki/Crepuscular_rays
# ─────────────────────────────────────────────────────────────────────────────

def draw_sky_sunburst(surf, w, h, ground_y, palette, phase):
    _base_gradient(surf, w, ground_y, palette, top_bias=0.04)
    night = _is_night(palette)
    dx, dy = _disc_xy(w, ground_y, phase)
    ray_col = _glow_color(palette) if not night else _moon_color(palette)

    # Radial shafts — long thin additive triangles fanning from the disc.
    # Alternating alpha gives the banded crepuscular-ray rhythm; the fan is
    # biased downward (sky source above haze) like real god-rays.
    rays = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    n_rays = 14
    reach = ground_y * 1.3
    for i in range(n_rays):
        ang = -0.35 + (i / (n_rays - 1)) * (math.pi + 0.7)
        spread = 0.045
        a = 26 if i % 2 == 0 else 14
        p0 = (dx, dy)
        p1 = (dx + math.cos(ang - spread) * reach,
              dy + math.sin(ang - spread) * reach)
        p2 = (dx + math.cos(ang + spread) * reach,
              dy + math.sin(ang + spread) * reach)
        pygame.draw.polygon(rays, (*ray_col, a), [p0, p1, p2])
    surf.blit(rays, (0, 0), special_flags=pygame.BLEND_ADD)

    # Bloomed disc core.
    disc = _moon_color(palette) if night else _sun_color(palette)
    _radial_glow(surf, dx, dy, 60, _glow_color(palette), 120, 2.0)
    pygame.draw.circle(surf, disc, (dx, dy), 18)

    _scatter_stars(surf, w, ground_y, palette)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 5 — Aurora veil
# Additive vertical curtain ribbons (night / predawn) that resolve to a
# clean sky by day. The signature is the rippling colour curtain; it fades
# out as the sky brightens so daytime stays calm.
#   https://en.wikipedia.org/wiki/Aurora
# ─────────────────────────────────────────────────────────────────────────────

def draw_sky_aurora_veil(surf, w, h, ground_y, palette, phase):
    _base_gradient(surf, w, ground_y, palette, top_bias=0.05)
    night = _is_night(palette)
    sa = _star_alpha(palette)

    # Curtain strength keyed to darkness — bright day suppresses the veil to
    # near nothing so the variant "resolves to clean sky" as briefed.
    strength = max(0.0, min(1.0, sa / 235.0))
    if strength > 0.02:
        # Aurora hue: cool green-teal pulled from the foliage accent (which
        # is already an aurora-like teal at night), with a magenta lower
        # fringe from the horizon for the classic two-tone curtain.
        green = palette.get('aurora_color',
                            lerp_color(palette['foliage_accent'], (120, 255, 180), 0.4))
        magenta = lerp_color(palette['horizon'], (210, 120, 220), 0.5)

        veil = pygame.Surface((w, ground_y), pygame.SRCALPHA)
        n_rib = 5
        for r in range(n_rib):
            base_x = int(w * (0.12 + 0.18 * r))
            sway = phase * 60 + r * 30
            # Each ribbon is a column of vertical line segments whose x
            # wavers with a sine ripple — the curtain "fold". Alpha is top-
            # weighted so the ribbon hangs from the zenith.
            for yy in range(int(ground_y * 0.05), int(ground_y * 0.62), 3):
                t = yy / (ground_y * 0.62)
                wob = math.sin(yy * 0.035 + sway * 0.05 + r) * 22
                x = int(base_x + wob)
                col = green if t < 0.6 else lerp_color(green, magenta, (t - 0.6) / 0.4)
                a = int(strength * 90 * (1 - t) * (0.6 + 0.4 * math.sin(yy * 0.12 + r)))
                if a <= 0:
                    continue
                ribbon_w = 10 + int(6 * math.sin(yy * 0.02 + r))
                pygame.draw.line(veil, (*col, a),
                                 (x, yy), (x, yy + 4), max(2, ribbon_w))
        surf.blit(veil, (0, 0), special_flags=pygame.BLEND_ADD)

    _scatter_stars(surf, w, ground_y, palette)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 6 — Gradient-mesh dawn
# Multi-stop painterly mesh: warm/cool counter-change across BOTH axes plus
# a soft bloom at the horizon — the Alto / Monument Valley polish, where the
# sky has horizontal as well as vertical colour drift.
# ─────────────────────────────────────────────────────────────────────────────

def draw_sky_mesh_dawn(surf, w, h, ground_y, palette, phase):
    _base_gradient(surf, w, ground_y, palette)
    night = _is_night(palette)

    # Horizontal counter-change: warm side vs cool side. Pull a warm pole
    # from horizon and a cool pole from sky_top, then paint a soft left-to-
    # right wash that meets the vertical gradient as a diagonal mesh. The
    # warm pole tracks the disc x so dawn light feels directional.
    dx, _dy = _disc_xy(w, ground_y, phase)
    warm = lerp_color(palette['horizon'], (255, 235, 200), 0.2)
    cool = lerp_color(palette['sky_top'], (120, 160, 220), 0.25)

    mesh = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    # Vertical strips of low-alpha colour interpolated by horizontal distance
    # from the warm pole — cheap mesh without per-pixel work.
    strip = 6
    for x in range(0, w, strip):
        hx = abs(x - dx) / w
        col = lerp_color(warm, cool, min(1.0, hx * 1.3))
        a = 55
        pygame.draw.rect(mesh, (*col, a), pygame.Rect(x, 0, strip, ground_y))
    surf.blit(mesh, (0, 0))

    # Soft horizon bloom — a wide low ellipse of warm light, the painterly
    # "sun behind the haze" glow that anchors the composition.
    bloom = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    bcol = _glow_color(palette)
    by = int(ground_y * 0.86)
    for k in range(6):
        a = int(46 * (1 - k / 6))
        bw = int(w * (0.5 + 0.12 * k))
        bh = int(ground_y * (0.10 + 0.05 * k))
        pygame.draw.ellipse(bloom, (*bcol, a),
                            pygame.Rect(dx - bw // 2, by - bh // 2, bw, bh))
    surf.blit(bloom, (0, 0), special_flags=pygame.BLEND_ADD)

    _scatter_stars(surf, w, ground_y, palette)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 7 — Layered cloud banks
# Soft strata at 3 depths with the sun/moon backlighting through the gaps —
# value structure carries the "high end" read; banks are rim-lit where the
# disc sits behind them.
# ─────────────────────────────────────────────────────────────────────────────

def draw_sky_cloud_banks(surf, w, h, ground_y, palette, phase):
    _base_gradient(surf, w, ground_y, palette, top_bias=0.03)
    night = _is_night(palette)
    dx, dy = _disc_xy(w, ground_y, phase)

    # Backlight disc FIRST so the banks occlude it and read as in front.
    disc = _moon_color(palette) if night else _sun_color(palette)
    _radial_glow(surf, dx, dy, 70, _glow_color(palette), 110, 1.9)
    pygame.draw.circle(surf, disc, (dx, dy), 16)

    # Three depth-sorted banks, far/high + pale to near/low + dense. Each is
    # a lumpy horizontal mass of overlapping ellipses; the rim facing the
    # disc gets a bright edge so the backlight reads.
    rim = _sun_color(palette) if not night else _moon_color(palette)
    banks = [
        (0.30, 0.55, 0.22, 110),
        (0.50, 0.75, 0.30, 140),
        (0.70, 1.00, 0.40, 170),
    ]
    import random as _r
    for bi, (yf, dark_f, htf, base_a) in enumerate(banks):
        cy = int(ground_y * yf)
        body = lerp_color(_cloud_tint(palette),
                          palette['sky_top'], dark_f * 0.5)
        layer = pygame.Surface((w, ground_y), pygame.SRCALPHA)
        rng = _r.Random(bi * 911 + 17)
        scroll = int(phase * 50 * (bi + 1))
        n = 7 + bi * 2
        for i in range(n):
            lx = (int(i * w / n) + scroll + rng.randint(-12, 12)) % (w + 80) - 40
            ly = cy + rng.randint(-10, 10)
            lw = rng.randint(50, 95)
            lh = int(ground_y * htf * (0.5 + rng.random() * 0.5))
            pygame.draw.ellipse(layer, (*body, base_a),
                                pygame.Rect(lx - lw, ly - lh // 2, lw * 2, lh))
            # Rim light on the disc-facing side of each lump.
            side = 1 if lx < dx else -1
            pygame.draw.ellipse(layer, (*rim, base_a // 2),
                                pygame.Rect(lx - lw + side * 4, ly - lh // 2 - 2,
                                            lw * 2, lh), 2)
        surf.blit(layer, (0, 0))

    _scatter_stars(surf, w, ground_y, palette)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 8 — Starlit deep sky
# Graded star density + a soft milky band + a crisp moon with a halo. By day
# it collapses to a calm high-altitude blue (stars/moon fade with star_alpha).
# ─────────────────────────────────────────────────────────────────────────────

def draw_sky_starlit_deep(surf, w, h, ground_y, palette, phase):
    _base_gradient(surf, w, ground_y, palette, top_bias=0.10)
    night = _is_night(palette)
    sa = _star_alpha(palette)

    if sa > 0:
        import random as _r
        # Milky band — a diagonal soft swath of faint light + denser star
        # speckle, the galactic core read. Drawn as overlapping low-alpha
        # ellipses on a tilted axis.
        milk = pygame.Surface((w, ground_y), pygame.SRCALPHA)
        mcol = lerp_color(palette['sky_mid'], (210, 215, 245), 0.5)
        band_a = int(sa * 0.22)
        for k in range(10):
            t = k / 9
            mx = int(w * (0.15 + t * 0.7))
            my = int(ground_y * (0.12 + t * 0.45))
            mw = int(w * 0.22)
            mh = int(ground_y * 0.10)
            pygame.draw.ellipse(milk, (*mcol, band_a),
                                pygame.Rect(mx - mw, my - mh, mw * 2, mh * 2))
        surf.blit(milk, (0, 0))

        # Graded star field — density and brightness ramp UP toward the
        # zenith (thinner air, darker sky) so the value structure isn't flat.
        rng = _r.Random(w * 104729)
        band = int(ground_y * 0.80)
        n = 120 if sa > 180 else 60
        for _ in range(n):
            sx = rng.randint(0, w - 1)
            sy = rng.randint(0, band)
            grad = 1.0 - sy / band          # 1 at top
            a = int(sa * (0.35 + 0.65 * grad))
            sz = 2 if (rng.random() < 0.18 * grad + 0.05) else 1
            pygame.draw.circle(surf, (255, 255, 255, a), (sx, sy), sz)
        # A few warm beacon stars near the milky band.
        for _ in range(8):
            sx = rng.randint(int(w * 0.15), int(w * 0.85))
            sy = rng.randint(int(ground_y * 0.12), int(ground_y * 0.55))
            pygame.draw.circle(surf, (255, 235, 200, min(255, sa)), (sx, sy), 2)

        # Crisp moon with a clean halo ring.
        dx, dy = _disc_xy(w, ground_y, phase)
        dy = min(dy, int(ground_y * 0.45))
        moon = _moon_color(palette)
        _radial_glow(surf, dx, dy, 40, _glow_color(palette), 70, 2.4)
        pygame.draw.circle(surf, moon, (dx, dy), 15)
        pygame.draw.circle(surf, lerp_color(moon, palette['sky_top'], 0.25),
                           (dx + 5, dy - 3), 13)  # terminator shading
        pygame.draw.circle(surf, (*moon, 60), (dx, dy), 30, 2)  # halo ring

    _scatter_stars(surf, w, ground_y, palette)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 9 — Vapor / dusk haze
# Stylised dual-tone vapour bands (a warm lower deck + a cool upper deck that
# meet at a soft seam) plus a glowing horizon disc — synthwave-adjacent but
# muted to the biome palette so it stays painterly, not neon.
# ─────────────────────────────────────────────────────────────────────────────

def draw_sky_vapor_haze(surf, w, h, ground_y, palette, phase):
    night = _is_night(palette)
    # Two decks: cool upper (sky_top→sky_mid) and warm lower (sky_bot→
    # horizon), each a smooth sub-gradient, meeting at a luminous seam.
    seam = int(ground_y * 0.62)
    upper = make_gradient_surface(
        w, seam,
        [(0.0, lerp_color(palette['sky_top'], (0, 0, 0), 0.05)),
         (1.0, palette['sky_mid'])])
    lower = make_gradient_surface(
        w, ground_y - seam,
        [(0.0, lerp_color(palette['sky_bot'], (255, 235, 215), 0.15)),
         (1.0, palette['horizon'])])
    surf.blit(upper, (0, 0))
    surf.blit(lower, (0, seam))

    # Glowing seam line — the bright vapour band where the two decks meet.
    seam_col = _glow_color(palette)
    glow = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    for k in range(7):
        a = int(70 * (1 - k / 7))
        hh = 3 + k * 4
        pygame.draw.rect(glow, (*seam_col, a),
                         pygame.Rect(0, seam - hh, w, hh * 2))
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # Horizon glow disc sitting on the seam — a half-sunk vapour sun.
    dx, dy = _disc_xy(w, ground_y, phase)
    dy = max(dy, seam - 6)
    disc = _moon_color(palette) if night else _sun_color(palette)
    _radial_glow(surf, dx, dy, 54, seam_col, 110, 2.0)
    pygame.draw.circle(surf, disc, (dx, dy), 24)
    # Horizontal "scan" cut lines across the disc — the dusk-vapour signature.
    for cy in range(dy - 18, dy + 26, 7):
        pygame.draw.line(surf, lerp_color(palette['sky_bot'], (0, 0, 0), 0.2),
                         (dx - 26, cy), (dx + 26, cy), 2)

    _scatter_stars(surf, w, ground_y, palette)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 10 — Painterly cumulus horizon
# Big calm sky above, soft cumulus masses massed LOW on the horizon. "High
# end" comes from value structure: flat-bottomed, dome-topped clouds with a
# lit cap and a shadowed base, the way real fair-weather cumulus stacks.
# ─────────────────────────────────────────────────────────────────────────────

def draw_sky_cumulus_horizon(surf, w, h, ground_y, palette, phase):
    _base_gradient(surf, w, ground_y, palette)
    night = _is_night(palette)

    # Disc low and warm behind the cloud line.
    dx, dy = _disc_xy(w, ground_y, phase)
    dy = max(dy, int(ground_y * 0.55))
    disc = _moon_color(palette) if night else _sun_color(palette)
    _radial_glow(surf, dx, dy, 50, _glow_color(palette), 90, 2.0)
    pygame.draw.circle(surf, disc, (dx, dy), 14)

    body = _cloud_tint(palette)
    cap = lerp_color(body, (255, 255, 255), 0.35 if not night else 0.0)
    base = lerp_color(body, palette['sky_top'], 0.45)

    import random as _r
    rng = _r.Random(2027)
    # Cumulus line massed low — flat base near 0.80*ground_y, dome tops
    # rising to ~0.58. Each cloud = a flat base rect + stacked dome lobes,
    # lit on top, shadowed underneath, the cumulus value structure.
    base_y = int(ground_y * 0.82)
    scroll = int(phase * 40)
    n = 6
    for i in range(n):
        cx = (int((i + 0.5) * w / n) + scroll) % (w + 120) - 60
        cw = rng.randint(48, 78)
        top = base_y - rng.randint(50, 95)
        layer = pygame.Surface((w, ground_y), pygame.SRCALPHA)
        # Shadowed flat base slab.
        pygame.draw.ellipse(layer, (*base, 200),
                            pygame.Rect(cx - cw, base_y - 14, cw * 2, 28))
        # Dome lobes — three stacked puffs, the tallest centre.
        for (ox, scale_h, lr) in ((-0.5, 0.7, 0.55), (0.0, 1.0, 0.7),
                                  (0.5, 0.65, 0.5)):
            lx = int(cx + ox * cw)
            lr_px = int(cw * lr)
            ly = base_y - int((base_y - top) * scale_h)
            pygame.draw.circle(layer, (*body, 230), (lx, ly), lr_px)
            # Lit cap on the upper portion of each lobe.
            pygame.draw.circle(layer, (*cap, 200),
                               (lx - lr_px // 4, ly - lr_px // 3),
                               max(3, lr_px // 2))
        # Re-seat the shadowed base over the lobes so it stays the darkest.
        pygame.draw.ellipse(layer, (*base, 150),
                            pygame.Rect(cx - cw, base_y - 10, cw * 2, 22))
        surf.blit(layer, (0, 0))

    _scatter_stars(surf, w, ground_y, palette)


# ── registries ───────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_sky_inkwash,
    2: draw_sky_ruyi_strata,
    3: draw_sky_goldleaf_byobu,
    4: draw_sky_sunburst,
    5: draw_sky_aurora_veil,
    6: draw_sky_mesh_dawn,
    7: draw_sky_cloud_banks,
    8: draw_sky_starlit_deep,
    9: draw_sky_vapor_haze,
    10: draw_sky_cumulus_horizon,
}

VARIANT_NAMES = {
    1: "Shan-shui Ink Wash",
    2: "Ruyi Cloud Strata",
    3: "Gold-leaf Byobu Screen",
    4: "Sunburst / God-rays",
    5: "Aurora Veil",
    6: "Gradient-mesh Dawn",
    7: "Layered Cloud Banks",
    8: "Starlit Deep Sky",
    9: "Vapor / Dusk Haze",
    10: "Painterly Cumulus Horizon",
}

VARIANT_NOTES = {
    1: "Layered ink-diffusion bands + negative-space mist gap; pomo broken-ink depth.",
    2: "Lingzhi/ruyi scalloped cloud belts at 3 depths, rim-lit crests (yunjian).",
    3: "Flat byobu colour registers + drifting gold-leaf flecks + low calm disc.",
    4: "Additive crepuscular shafts fanning from a bloomed sun/moon through haze.",
    5: "Night/predawn aurora curtain ribbons; resolves to clean sky by day.",
    6: "Two-axis warm/cool mesh counter-change + soft directional horizon bloom.",
    7: "3-depth cloud banks backlit by the disc; rim-lit gaps carry the value read.",
    8: "Graded star density + milky band + crisp haloed moon; collapses to calm blue.",
    9: "Dual-tone vapour decks with a luminous seam + half-sunk scan-lined disc.",
    10: "Low fair-weather cumulus line, lit caps + shadowed bases; big calm sky above.",
}
