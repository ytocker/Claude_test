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

def _sky_top_lum(palette) -> float:
    t = palette['sky_top']
    return (t[0] * 299 + t[1] * 587 + t[2] * 114) / 1000


def _is_night(palette) -> bool:
    """Luminance gate on sky_top — the deep-blue night/dusk keyframes sit
    well under this threshold, so one test routes both the disc choice and
    the warm-vs-cool accent for every variant."""
    return _sky_top_lum(palette) < 60


def _night_amount(palette) -> float:
    """Smooth 0..1 night-ness from sky_top luminance — a continuous ramp
    instead of the hard `_is_night` boolean. Because the biome palette is
    already interpolated between keyframes, deriving accents from THIS keeps
    a baked phase-bucket cache continuous: no value step at the luminance
    threshold means no visible pop when adjacent buckets cross-fade."""
    lum = _sky_top_lum(palette)
    # Cool side fully resolved by ~40 (deep night), warm side by ~95 (day).
    return max(0.0, min(1.0, (95.0 - lum) / 55.0))


def _star_alpha(palette) -> int:
    return int(palette.get('star_alpha', 0))


def lerp_scalar(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _lum(color) -> float:
    return (color[0] * 299 + color[1] * 587 + color[2] * 114) / 1000


def _inkwash_night_stars(surf, w, ground_y, palette, nightf) -> None:
    """A small extra star sprinkle for inkwash's dark phases. Separate seed
    from the shared scatter so these don't overlap it, faint and few, and
    scaled by `nightf` so they fade in continuously toward night rather than
    popping at a luminance threshold."""
    if nightf <= 0.02:
        return
    import random as _r
    rng = _r.Random(w * 6271 + 13)
    base = _star_alpha(palette)
    # Lean on the biome star layer for the bulk; this just adds 1-2 faint
    # accents up high where the ink void is emptiest.
    n = 1 + int(round(nightf))
    band = int(ground_y * 0.55)
    for _ in range(n):
        sx = rng.randint(int(w * 0.1), int(w * 0.9))
        sy = rng.randint(int(ground_y * 0.08), band)
        a = int(max(40, base * 0.55) * nightf)
        if a <= 0:
            continue
        pygame.draw.circle(surf, (235, 240, 255, a), (sx, sy), 1)


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


def _soft_disc(surf, cx, cy, radius, color, core_alpha=235):
    """A small soft-edged luminary: a radial alpha falloff from a bright core
    to ~0 at the rim, NOT a hard filled circle. A hard circle leaves a crisp
    edge that ghosts/smears when two adjacent baked phase-buckets cross-fade;
    a feathered disc cross-dissolves cleanly. Drawn into a scratch surface and
    blitted normally so the soft rim composites over the sky underneath."""
    size = radius * 2 + 2
    d = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = r / radius
        # Bright, near-solid core for the inner third; smooth feather outside.
        if t < 0.34:
            a = core_alpha
        else:
            f = (t - 0.34) / 0.66
            a = int(core_alpha * (1 - f) ** 2)
        if a <= 0:
            continue
        pygame.draw.circle(d, (*color, a), (c, c), r)
    surf.blit(d, (cx - radius - 1, cy - radius - 1))


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
    _base_gradient(surf, w, ground_y, palette, top_bias=0.08)

    # Continuous night-ness drives every accent so the baked phase-bucket
    # cache cross-fades without a value step. NO branch on `phase` here — all
    # hue/value choices are smooth functions of the already-interpolated
    # `palette`, which is what keeps adjacent buckets from popping at a seam.
    nightf = _night_amount(palette)

    # Raised band contrast: darker ink low, paler wash high. Wider spread
    # between the two poles than round 1 so the strata read as deliberate
    # ink layering rather than a soft graded haze. The pale-wash lift ramps
    # smoothly down into night instead of snapping at a luminance gate.
    deep = lerp_color(palette['sky_top'], (0, 0, 0), 0.28)
    pale = lerp_color(palette['sky_mid'], (255, 255, 255),
                      lerp_scalar(0.42, 0.16, nightf))

    # A warm horizon wash keyed to the day cycle so sunrise/sunset columns
    # stop reading identical to flat day — the horizon hue (amber/rose at
    # golden hour, cool blue at night) bleeds up into the lowest bands.
    warm = palette['horizon']

    # The mist gap value, computed FIRST so the warm bleed can be capped to
    # stay strictly below it. The carved bright band must remain the single
    # highest value in the frame at every phase (day → night); if the warm
    # sunset bleed climbed past it the frame would flatten.
    mist = lerp_color(palette['horizon'], (255, 255, 255),
                      lerp_scalar(0.5, 0.28, nightf))
    mist_lum = _lum(mist)

    # Five diffusion bands, densest low thinning up. Overlapping low-alpha
    # ellipse smears give the pomo "broken ink" read.
    n_bands = 5
    band_layer = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    for i in range(n_bands):
        t = i / (n_bands - 1)
        by = int(ground_y * (0.28 + 0.58 * t))
        col = lerp_color(pale, deep, t)
        # Low bands pick up the horizon warmth so the cycle reads in colour.
        col = lerp_color(col, warm, 0.30 * t)
        # Cap the warm bleed: hold every band's luminance under the mist gap
        # so the carved band stays the brightest value. At sunset the orange
        # horizon would otherwise lift the low bands above the mist and flatten
        # the frame; darkening toward `deep` only when a band exceeds the cap
        # is a smooth correction (zero when already below it).
        over = _lum(col) - (mist_lum - 12)
        if over > 0:
            col = lerp_color(col, deep, min(0.85, over / 90.0))
        bh = int(ground_y * (0.11 + 0.06 * (1 - t)))
        a = int(95 * (0.35 + 0.65 * t))
        rect = pygame.Rect(-w // 4, by - bh // 2, int(w * 1.5), bh)
        pygame.draw.ellipse(band_layer, (*col, a), rect)
    surf.blit(band_layer, (0, 0))

    # ONE clear light/mist band for the mountains to sit against — a single
    # bright void carved just above the horizon, brighter and tighter than
    # round 1's diffuse smear so the ridges read crisply against it. Warmed
    # at sunrise/sunset, cooled at night. Painted AFTER the bands so it is
    # never dimmed by them — guaranteeing it holds the highest value.
    mist_layer = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    my = int(ground_y * 0.80)
    for k in range(4):
        a = int(95 * (1 - k / 4))
        hh = int(ground_y * (0.03 + 0.022 * k))
        pygame.draw.ellipse(mist_layer, (*mist, a),
                            pygame.Rect(-w // 4, my - hh // 2, int(w * 1.5), hh))
    surf.blit(mist_layer, (0, 0))

    _scatter_stars(surf, w, ground_y, palette)
    # A few extra faint stars on the dark phases so the void doesn't read as
    # empty at night. Count and alpha both ride `nightf`, so the sprinkle
    # fades in smoothly rather than switching on at a threshold.
    _inkwash_night_stars(surf, w, ground_y, palette, nightf)


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

    # Crepuscular shafts must read as ATMOSPHERE behind the pillar plane,
    # never as graphic spokes. So: fewer rays, asymmetric (clustered to one
    # side of the disc, not a symmetric starburst), much lower alpha, and
    # only the lower hemisphere so they fall away below the HUD zone.
    rays = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    reach = ground_y * 1.4
    if night:
        # Night = soft moon-glow with only 2-3 faint shafts, not a burst.
        # Root alpha dropped ~15% so the shaft bases read as light, not
        # opaque spokes anchored on the disc.
        offsets = (0.55, 1.15, 1.7)
        ray_alphas = (8, 6, 5)
    else:
        # Day/golden/dusk = an asymmetric fan: a few shafts skewed to one
        # side so the light feels directional, like sun through a gap. Root
        # alpha dropped ~15% vs round 2 (16/11/14/8/7) for the same reason.
        offsets = (0.35, 0.7, 1.05, 1.55, 2.1)
        ray_alphas = (14, 9, 12, 7, 6)
    side = 1 if (dx < w * 0.5) else -1  # fan AWAY from the nearer edge
    for off, a in zip(offsets, ray_alphas):
        ang = (math.pi * 0.5) + side * off  # base straight down, skewed
        spread = 0.05 + 0.015 * off
        p0 = (dx, dy)
        p1 = (dx + math.cos(ang - spread) * reach,
              dy + math.sin(ang - spread) * reach)
        p2 = (dx + math.cos(ang + spread) * reach,
              dy + math.sin(ang + spread) * reach)
        pygame.draw.polygon(rays, (*ray_col, a), [p0, p1, p2])
    surf.blit(rays, (0, 0), special_flags=pygame.BLEND_ADD)

    # Disc + bloom. The disc is SMALL and SOFT-EDGED (radial alpha falloff to
    # ~0 at the rim) so it cross-dissolves cleanly between baked phase-buckets
    # instead of ghosting a hard circle. `_disc_xy` is a continuous cosine
    # function of `phase`, so the disc centre never step-jumps across buckets.
    # Bloom is capped so the additive core never reaches the upper-third HUD.
    disc = _moon_color(palette) if night else _sun_color(palette)
    if night:
        _radial_glow(surf, dx, dy, 46, _glow_color(palette), 72, 2.2)
        _soft_disc(surf, dx, dy, 13, disc, core_alpha=225)
    else:
        _radial_glow(surf, dx, dy, 54, _glow_color(palette), 95, 2.1)
        _soft_disc(surf, dx, dy, 16, disc, core_alpha=235)

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

    # ONE soft asymmetric warm pool — an off-centre painterly light mass set
    # OPPOSITE the disc, mid-height, so the composition reads as authored
    # (two competing light sources) rather than a default symmetric gradient.
    # Kept low-alpha and away from the upper third so the HUD zone stays calm.
    pool = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    pcol = lerp_color(warm, (255, 245, 220), 0.25 if not night else 0.0)
    px = int(w * (0.78 if dx < w * 0.5 else 0.22))
    py = int(ground_y * 0.50)
    for k in range(6):
        a = int((30 if night else 42) * (1 - k / 6))
        pw = int(w * (0.30 + 0.10 * k))
        ph = int(ground_y * (0.18 + 0.07 * k))
        pygame.draw.ellipse(pool, (*pcol, a),
                            pygame.Rect(px - pw // 2, py - ph // 2, pw, ph))
    surf.blit(pool, (0, 0), special_flags=pygame.BLEND_ADD)

    # Horizon bloom — pushed harder than round 1 (brighter peak, tighter
    # falloff) so it clearly beats the flat gradient it replaces. The
    # painterly "sun behind the haze" glow anchoring the composition.
    bloom = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    bcol = _glow_color(palette)
    by = int(ground_y * 0.86)
    peak = 60 if not night else 40
    for k in range(7):
        a = int(peak * (1 - k / 7))
        bw = int(w * (0.45 + 0.13 * k))
        bh = int(ground_y * (0.08 + 0.05 * k))
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
    # Day keeps the upper deck open (warm bias on the lower deck); night
    # cools the lower bias so the warm vapour read doesn't survive into the
    # deep-blue keyframes where it would look wrong.
    seam = int(ground_y * 0.62)
    upper = make_gradient_surface(
        w, seam,
        [(0.0, lerp_color(palette['sky_top'], (0, 0, 0), 0.05)),
         (1.0, palette['sky_mid'])])
    low_warm = 0.04 if night else 0.15
    lower = make_gradient_surface(
        w, ground_y - seam,
        [(0.0, lerp_color(palette['sky_bot'], (255, 235, 215), low_warm)),
         (1.0, palette['horizon'])])
    surf.blit(upper, (0, 0))
    surf.blit(lower, (0, seam))

    # Luminous horizon seam where the decks meet. The seam holds across all
    # 7 times of day: warm + bright by day, COOLER + DIMMER at night so it
    # reads as a faint moonlit haze line rather than a dusk-only glow.
    if night:
        seam_col = lerp_color(palette['horizon'], (180, 200, 240), 0.4)
        seam_peak, seam_layers = 38, 6
    else:
        seam_col = _glow_color(palette)
        seam_peak, seam_layers = 70, 7
    glow = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    for k in range(seam_layers):
        a = int(seam_peak * (1 - k / seam_layers))
        hh = 3 + k * 4
        pygame.draw.rect(glow, (*seam_col, a),
                         pygame.Rect(0, seam - hh, w, hh * 2))
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # Clean soft disc sitting on the seam — a half-sunk vapour sun/moon.
    # Round 1's scan-lines (CRT/UI artifact) are gone; the disc is now a
    # smooth core wrapped in a soft bloom so it stays painterly.
    dx, dy = _disc_xy(w, ground_y, phase)
    dy = max(dy, seam - 6)
    disc = _moon_color(palette) if night else _sun_color(palette)
    _radial_glow(surf, dx, dy, 54 if not night else 46, seam_col,
                 100 if not night else 70, 2.0)
    pygame.draw.circle(surf, disc, (dx, dy), 24 if not night else 20)
    # A faint inner-light core lifts the disc centre without hard lines.
    pygame.draw.circle(surf, lerp_color(disc, (255, 255, 255), 0.35),
                       (dx, dy), 12 if not night else 10)

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


# ─────────────────────────────────────────────────────────────────────────────
# Hybrid A — God-rays × Vapor
# The strongest two leads fused: Vapor's luminous horizon seam + clean
# half-sunk disc, with God-rays' asymmetric atmospheric shafts rising from
# that disc. The seam grounds the composition; the (few, low-alpha, one-
# sided) shafts add depth without reading as graphic spokes.
# ─────────────────────────────────────────────────────────────────────────────

def draw_sky_godrays_vapor(surf, w, h, ground_y, palette, phase):
    night = _is_night(palette)

    # --- Vapor base: dual decks + luminous seam (carried from #9) ---
    seam = int(ground_y * 0.62)
    upper = make_gradient_surface(
        w, seam,
        [(0.0, lerp_color(palette['sky_top'], (0, 0, 0), 0.05)),
         (1.0, palette['sky_mid'])])
    low_warm = 0.04 if night else 0.15
    lower = make_gradient_surface(
        w, ground_y - seam,
        [(0.0, lerp_color(palette['sky_bot'], (255, 235, 215), low_warm)),
         (1.0, palette['horizon'])])
    surf.blit(upper, (0, 0))
    surf.blit(lower, (0, seam))

    if night:
        seam_col = lerp_color(palette['horizon'], (180, 200, 240), 0.4)
        seam_peak, seam_layers = 36, 6
    else:
        seam_col = _glow_color(palette)
        seam_peak, seam_layers = 64, 7
    glow = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    for k in range(seam_layers):
        a = int(seam_peak * (1 - k / seam_layers))
        hh = 3 + k * 4
        pygame.draw.rect(glow, (*seam_col, a),
                         pygame.Rect(0, seam - hh, w, hh * 2))
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    dx, dy = _disc_xy(w, ground_y, phase)
    dy = max(dy, seam - 6)

    # --- God-rays: asymmetric shafts RISING from the seated disc, fanning
    # upward into the cool deck. Few, low-alpha, skewed one side so they
    # read as bloomed atmosphere off the disc, not a starburst. ---
    ray_col = seam_col if night else _glow_color(palette)
    rays = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    reach = ground_y * 1.1
    side = 1 if (dx < w * 0.5) else -1
    if night:
        offsets, ray_alphas = (0.5, 1.1, 1.7), (8, 6, 5)
    else:
        offsets = (0.3, 0.65, 1.0, 1.5)
        ray_alphas = (15, 10, 12, 7)
    for off, a in zip(offsets, ray_alphas):
        ang = -(math.pi * 0.5) + side * off  # base straight UP, skewed
        spread = 0.05 + 0.015 * off
        p0 = (dx, dy)
        p1 = (dx + math.cos(ang - spread) * reach,
              dy + math.sin(ang - spread) * reach)
        p2 = (dx + math.cos(ang + spread) * reach,
              dy + math.sin(ang + spread) * reach)
        pygame.draw.polygon(rays, (*ray_col, a), [p0, p1, p2])
    surf.blit(rays, (0, 0), special_flags=pygame.BLEND_ADD)

    # Clean bloomed disc — no scan-lines (the #9 fix carried through).
    disc = _moon_color(palette) if night else _sun_color(palette)
    _radial_glow(surf, dx, dy, 54 if not night else 46, seam_col,
                 100 if not night else 70, 2.0)
    pygame.draw.circle(surf, disc, (dx, dy), 24 if not night else 20)
    pygame.draw.circle(surf, lerp_color(disc, (255, 255, 255), 0.35),
                       (dx, dy), 12 if not night else 10)

    _scatter_stars(surf, w, ground_y, palette)


def _aurora_gate(phase) -> float:
    """Aurora ribbon strength as a function of phase, gated so ribbons are
    fully absent by day and only resolve deep dusk→night.

    The dusk keyframe sits at ~0.513 and night at ~0.644. Gating on
    phase>0.6 with a ramp keeps the ribbons OFF through bright sunset/dusk
    (round 1's leak) and fades them up cleanly into night. Phase wraps, so
    predawn (~0.75→0.9) also carries a tail before fading out by sunrise."""
    p = phase % 1.0
    # Ramp 0 at 0.58 → 1 at 0.66, hold through deep night, ramp back down
    # 1 at 0.82 → 0 at 0.90 (predawn fade). Daytime (<0.58, >0.90) = 0.
    if 0.58 <= p <= 0.82:
        return min(1.0, max(0.0, (p - 0.58) / 0.08))
    if 0.82 < p <= 0.90:
        return max(0.0, 1.0 - (p - 0.82) / 0.08)
    return 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Hybrid B — Gradient-mesh base + night-only aurora accent
# The painterly mesh dawn (lead #6) as the all-day base, with an aurora
# curtain that is GATED to deep dusk→night via _aurora_gate(). By day the
# ribbon alpha is exactly 0 (clean mesh); only past phase~0.6 do the
# ribbons resolve, proving the aurora is done correctly.
# ─────────────────────────────────────────────────────────────────────────────

def draw_sky_mesh_aurora(surf, w, h, ground_y, palette, phase):
    # Reuse the refined mesh dawn as the base for all phases.
    draw_sky_mesh_dawn(surf, w, h, ground_y, palette, phase)

    strength = _aurora_gate(phase)
    if strength <= 0.01:
        return  # daytime: clean mesh, no ribbons (the round-1 fix)

    # Aurora hue: cool teal-green from the night foliage accent + a magenta
    # lower fringe from the horizon for the classic two-tone curtain. Kept in
    # the lower-middle band so it never blooms into the upper-third HUD zone.
    green = palette.get('aurora_color',
                        lerp_color(palette['foliage_accent'], (120, 255, 180), 0.4))
    magenta = lerp_color(palette['horizon'], (210, 120, 220), 0.5)

    veil = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    y0, y1 = int(ground_y * 0.20), int(ground_y * 0.62)
    n_rib = 4
    for r in range(n_rib):
        base_x = int(w * (0.16 + 0.22 * r))
        sway = phase * 60 + r * 30
        for yy in range(y0, y1, 3):
            t = (yy - y0) / (y1 - y0)
            wob = math.sin(yy * 0.035 + sway * 0.05 + r) * 22
            x = int(base_x + wob)
            col = green if t < 0.6 else lerp_color(green, magenta, (t - 0.6) / 0.4)
            # Alpha is gated by strength AND tapers top+bottom so the curtain
            # hangs softly rather than as a hard column.
            edge = math.sin(math.pi * t)  # 0 at both ends, 1 mid
            a = int(strength * 75 * edge * (0.6 + 0.4 * math.sin(yy * 0.12 + r)))
            if a <= 0:
                continue
            ribbon_w = 9 + int(5 * math.sin(yy * 0.02 + r))
            pygame.draw.line(veil, (*col, a),
                             (x, yy), (x, yy + 4), max(2, ribbon_w))
    surf.blit(veil, (0, 0), special_flags=pygame.BLEND_ADD)

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
    11: draw_sky_godrays_vapor,
    12: draw_sky_mesh_aurora,
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
    11: "Hybrid A — God-rays x Vapor",
    12: "Hybrid B — Mesh + Night Aurora",
}

VARIANT_NOTES = {
    1: "Layered ink-diffusion bands + negative-space mist gap; pomo broken-ink depth.",
    2: "Lingzhi/ruyi scalloped cloud belts at 3 depths, rim-lit crests (yunjian).",
    3: "Flat byobu colour registers + drifting gold-leaf flecks + low calm disc.",
    4: "Asymmetric few low-alpha shafts behind the pillar plane; soft moon-glow at night.",
    5: "Night/predawn aurora curtain ribbons; resolves to clean sky by day.",
    6: "Two-axis mesh + asymmetric warm pool + pushed horizon bloom; authored not flat.",
    7: "3-depth cloud banks backlit by the disc; rim-lit gaps carry the value read.",
    8: "Graded star density + milky band + crisp haloed moon; collapses to calm blue.",
    9: "Dual-tone vapour decks + clean disc; luminous seam holds warm day / cool night.",
    10: "Low fair-weather cumulus line, lit caps + shadowed bases; big calm sky above.",
    11: "Vapor seam + clean disc fused with asymmetric god-ray shafts rising off the disc.",
    12: "Refined mesh base; aurora gated phase>0.6 — zero by day, resolves dusk->night.",
}

# Round-2 sheet renders ONLY these 6, in the art-director's ranked order.
ROUND2_ORDER = [4, 9, 6, 1, 11, 12]

# Round-3 (final) sheet renders ONLY the 2 finalists, ranked: the winning
# Shan-shui Ink Wash (#1, integration target) first, God-rays (#4) fallback.
ROUND3_ORDER = [1, 4]
