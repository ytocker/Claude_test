"""
Biome / time-of-day palettes.

A single `phase` float in [0, 1) cycles through day → golden hour → sunset →
dusk → night → predawn → sunrise → day. The phase is driven by **real elapsed
gameplay seconds** — one full cycle every CYCLE_SECONDS seconds — so the
visuals evolve with time, not with score. The player sees the full cycle in
a long run regardless of how fast they score.

Pillar palette keys describe the sandstone columns plus the foliage that
crowns them:
  stone_light / stone_mid / stone_dark   — body sandstone gradient
  stone_accent                           — warm highlight band on the sunlit side
  foliage_top / foliage_mid / foliage_dark — plants on the cap
  foliage_accent                         — flower / berry / bright leaf tip
"""
from __future__ import annotations
import math

from game.draw import lerp_color


# ── keyframes ────────────────────────────────────────────────────────────────
# phase -> palette dict. Phases MUST be sorted ascending (0..1).

_KEYFRAMES: list[tuple[float, dict]] = [
    (0.00000, dict(  # DAY — bright cyan sky, warm tan sandstone, lush green canopy
        sky_top=(40, 110, 200),
        sky_mid=(90, 170, 230),
        sky_bot=(170, 220, 245),
        horizon=(255, 240, 200),
        mtn_far=(80, 120, 170),
        mtn_near=(55, 95, 145),
        ground_top=(80, 200, 80),
        ground_mid=(40, 150, 40),
        stone_light=(225, 195, 155),
        stone_mid=(175, 140, 105),
        stone_dark=(95, 70, 55),
        stone_accent=(255, 220, 170),
        foliage_top=(140, 220, 110),
        foliage_mid=(70, 170, 75),
        foliage_dark=(30, 100, 50),
        foliage_accent=(255, 240, 120),
        star_alpha=0,
    )),
    (0.23125, dict(  # GOLDEN HOUR — amber warmth
        sky_top=(80, 120, 200),
        sky_mid=(220, 175, 140),
        sky_bot=(255, 210, 160),
        horizon=(255, 220, 140),
        mtn_far=(130, 110, 150),
        mtn_near=(85, 75, 115),
        ground_top=(120, 190, 80),
        ground_mid=(80, 135, 50),
        stone_light=(240, 200, 145),
        stone_mid=(200, 150, 90),
        stone_dark=(110, 70, 40),
        stone_accent=(255, 225, 155),
        foliage_top=(180, 210, 90),
        foliage_mid=(130, 170, 60),
        foliage_dark=(70, 100, 40),
        foliage_accent=(255, 200, 80),
        star_alpha=0,
    )),
    (0.36250, dict(  # SUNSET — rose stone, autumn canopy
        sky_top=(90, 50, 130),
        sky_mid=(230, 95, 120),
        sky_bot=(255, 160, 90),
        horizon=(255, 200, 120),
        mtn_far=(90, 60, 120),
        mtn_near=(55, 35, 85),
        ground_top=(150, 105, 110),
        ground_mid=(95, 60, 80),
        stone_light=(240, 170, 155),
        stone_mid=(190, 105, 110),
        stone_dark=(100, 45, 60),
        stone_accent=(255, 210, 170),
        foliage_top=(210, 150, 90),
        foliage_mid=(150, 95, 65),
        foliage_dark=(85, 45, 40),
        foliage_accent=(255, 160, 80),
        star_alpha=20,
    )),
    (0.51250, dict(  # DUSK — lavender stone, teal foliage
        sky_top=(25, 20, 70),
        sky_mid=(70, 45, 130),
        sky_bot=(170, 95, 140),
        horizon=(255, 150, 140),
        mtn_far=(45, 30, 85),
        mtn_near=(25, 15, 55),
        ground_top=(80, 70, 110),
        ground_mid=(45, 35, 75),
        stone_light=(180, 160, 200),
        stone_mid=(110, 95, 150),
        stone_dark=(55, 40, 80),
        stone_accent=(220, 200, 240),
        foliage_top=(120, 160, 150),
        foliage_mid=(60, 100, 110),
        foliage_dark=(25, 50, 70),
        foliage_accent=(180, 220, 200),
        star_alpha=130,
    )),
    (0.64375, dict(  # NIGHT — moonlit cool stone, dark teal canopy
        sky_top=(5, 8, 30),
        sky_mid=(15, 25, 70),
        sky_bot=(35, 55, 115),
        horizon=(170, 190, 255),
        mtn_far=(25, 35, 75),
        mtn_near=(15, 20, 50),
        ground_top=(35, 60, 75),
        ground_mid=(20, 40, 55),
        stone_light=(150, 170, 210),
        stone_mid=(80, 100, 150),
        stone_dark=(30, 45, 85),
        stone_accent=(200, 225, 255),
        foliage_top=(80, 130, 130),
        foliage_mid=(35, 80, 90),
        foliage_dark=(10, 35, 55),
        foliage_accent=(160, 220, 230),
        star_alpha=235,
    )),
    (0.79375, dict(  # PREDAWN — cool pink stone, muted canopy
        sky_top=(30, 30, 80),
        sky_mid=(70, 60, 140),
        sky_bot=(200, 130, 180),
        horizon=(255, 200, 210),
        mtn_far=(55, 50, 110),
        mtn_near=(30, 25, 70),
        ground_top=(80, 95, 130),
        ground_mid=(45, 60, 95),
        stone_light=(220, 175, 200),
        stone_mid=(155, 110, 150),
        stone_dark=(75, 50, 90),
        stone_accent=(255, 210, 225),
        foliage_top=(130, 155, 130),
        foliage_mid=(70, 105, 95),
        foliage_dark=(35, 60, 60),
        foliage_accent=(200, 220, 180),
        star_alpha=90,
    )),
    (0.90625, dict(  # SUNRISE — peach stone, fresh canopy
        sky_top=(50, 100, 180),
        sky_mid=(255, 150, 150),
        sky_bot=(255, 220, 170),
        horizon=(255, 235, 180),
        mtn_far=(135, 105, 150),
        mtn_near=(85, 70, 110),
        ground_top=(130, 190, 120),
        ground_mid=(85, 140, 75),
        stone_light=(255, 205, 175),
        stone_mid=(215, 150, 125),
        stone_dark=(130, 75, 70),
        stone_accent=(255, 230, 195),
        foliage_top=(170, 220, 130),
        foliage_mid=(95, 170, 90),
        foliage_dark=(45, 110, 60),
        foliage_accent=(255, 210, 130),
        star_alpha=0,
    )),
    (1.00000, dict(  # loop back to DAY
        sky_top=(40, 110, 200),
        sky_mid=(90, 170, 230),
        sky_bot=(170, 220, 245),
        horizon=(255, 240, 200),
        mtn_far=(80, 120, 170),
        mtn_near=(55, 95, 145),
        ground_top=(80, 200, 80),
        ground_mid=(40, 150, 40),
        stone_light=(225, 195, 155),
        stone_mid=(175, 140, 105),
        stone_dark=(95, 70, 55),
        stone_accent=(255, 220, 170),
        foliage_top=(140, 220, 110),
        foliage_mid=(70, 170, 75),
        foliage_dark=(30, 100, 50),
        foliage_accent=(255, 240, 120),
        star_alpha=0,
    )),
]


# One full day-cycle every CYCLE_SECONDS seconds of gameplay.
# The day phase spans 0.00 -> 0.23125 = 74s; the remaining six phases
# (golden hour through sunrise) each preserve their original 300s-cycle
# wall-clock durations. Extending the cycle past 320 should shift the
# non-day keyframes proportionally — don't change CYCLE_SECONDS alone.
CYCLE_SECONDS = 320.0


def phase_for_time(elapsed_seconds: float) -> float:
    """Return a phase in [0,1). t=0 lands exactly on the DAY keyframe so
    the first 30+ seconds of a run sit in bright daylight before the
    transition toward golden hour starts to read on screen."""
    return (elapsed_seconds / CYCLE_SECONDS) % 1.0


def _blend(a: dict, b: dict, t: float) -> dict:
    out = {}
    for k in a:
        va, vb = a[k], b[k]
        if isinstance(va, tuple):
            out[k] = lerp_color(va, vb, t)
        else:
            out[k] = va + (vb - va) * t
    return out


def palette_for_phase(phase: float) -> dict:
    """Interpolate the biome palette for a phase in [0,1)."""
    phase = phase % 1.0
    for i in range(len(_KEYFRAMES) - 1):
        t0, p0 = _KEYFRAMES[i]
        t1, p1 = _KEYFRAMES[i + 1]
        if t0 <= phase <= t1:
            span = t1 - t0
            t = (phase - t0) / span if span > 0 else 0.0
            t = t * t * (3 - 2 * t)  # smoothstep
            return _blend(p0, p1, t)
    return dict(_KEYFRAMES[0][1])


def palette_for_time(elapsed_seconds: float) -> dict:
    return palette_for_phase(phase_for_time(elapsed_seconds))


# ── scene ambient light ─────────────────────────────────────────────────────
# A pair of brightness multipliers (top, bottom) that follows the biome
# cycle. The TOP value is the brightness at the top edge of Pip's sprite,
# the BOTTOM value at the bottom edge — a vertical gradient is interpolated
# between them. This reads as "light from above" so dusk/night don't darken
# Pip uniformly; the underside is shadowed while the top still catches
# moonlight. Floor is kept above 0.4 so Pip is always trackable.
#
# Keyframed at the SAME phases as the palette so the dial moves in lockstep
# with the visible sky transitions; linearly interpolated between keyframes.
_LIGHT_GRADIENT_KEYFRAMES = [
    # (phase,    top,   bot)
    (0.00000, (1.00,  1.00)),   # DAY — uniform full bright
    (0.23125, (0.96,  0.88)),   # GOLDEN HOUR — slight underside shadow
    (0.36250, (0.85,  0.65)),   # SUNSET — clearly directional
    (0.51250, (0.70,  0.50)),   # DUSK — strong shadow
    (0.64375, (0.60,  0.40)),   # NIGHT — peak gradient, floor=0.40
    (0.79375, (0.65,  0.50)),   # PREDAWN — light returning, less contrast
    (0.90625, (0.90,  0.80)),   # SUNRISE — almost back to flat
    (1.00000, (1.00,  1.00)),   # wraps to DAY
]


def light_gradient_for_phase(phase: float) -> "tuple[float, float]":
    """(top, bot) brightness multipliers (0..1) at the given biome
    phase. The renderer interpolates linearly between them across the
    sprite's vertical extent to produce the directional shadow."""
    p = phase % 1.0
    for i in range(len(_LIGHT_GRADIENT_KEYFRAMES) - 1):
        p0, v0 = _LIGHT_GRADIENT_KEYFRAMES[i]
        p1, v1 = _LIGHT_GRADIENT_KEYFRAMES[i + 1]
        if p0 <= p <= p1:
            span = max(1e-9, p1 - p0)
            t = (p - p0) / span
            return (v0[0] + (v1[0] - v0[0]) * t,
                    v0[1] + (v1[1] - v0[1]) * t)
    return (1.0, 1.0)


def light_gradient_for_time(elapsed_seconds: float) -> "tuple[float, float]":
    return light_gradient_for_phase(phase_for_time(elapsed_seconds))


# Back-compat: average of the gradient. Kept so callers that want a
# single scalar still work.
def light_level_for_phase(phase: float) -> float:
    top, bot = light_gradient_for_phase(phase)
    return (top + bot) * 0.5


def light_level_for_time(elapsed_seconds: float) -> float:
    return light_level_for_phase(phase_for_time(elapsed_seconds))


# ── cached-palette bucket helpers ────────────────────────────────────────────

PHASE_BUCKETS = 32


def phase_bucket(phase: float) -> int:
    return int((phase % 1.0) * PHASE_BUCKETS) % PHASE_BUCKETS


def bucketed_phase(phase: float) -> float:
    return phase_bucket(phase) / PHASE_BUCKETS
