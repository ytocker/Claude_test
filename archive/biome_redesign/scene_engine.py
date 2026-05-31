"""
Shared scene-rendering engine for the biome exploration.

One parameterized engine, ten data specs: every candidate biome is a `BiomeSpec`
(its own palette keyframes + silhouette params + signature/foliage callbacks),
and `paint_scene` always draws the same back-to-front layer stack. Distinctness
comes from DATA, not forked scene code — so 10 worlds cost ~4-5 tiny new motif
painters plus parameter tuning, not 10x duplicated scenes.

Exploration-only: nothing here is imported by the live game. It reuses the
production primitives in `game.draw` / `game.pillar_variants` (the harness puts
the repo root on sys.path) and the ported OKLab sky engine `sky_field`.

All draw code is pure-Pygame / pygbag-safe (fill, blit, draw.*, SRCALPHA,
BLEND_ADD) — no surfarray/gfxdraw/numpy/per-pixel set_at loops.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Optional

import pygame

import sky_field as sf
from game.draw import make_gradient_surface, lerp_color, make_glow_surface


# ── palette authoring (mirrors game/biome.py's smoothstep interpolation) ──────

def _blend(a: dict, b: dict, t: float) -> dict:
    """Lerp two palette dicts: color tuples via lerp_color, scalars linearly.
    Keys present in only one side pass through unchanged so a biome can omit
    keys it doesn't use."""
    out = {}
    for k in a:
        va = a[k]
        vb = b.get(k, va)
        if isinstance(va, tuple) and isinstance(vb, tuple):
            out[k] = lerp_color(va, vb, t)
        elif isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            out[k] = va + (vb - va) * t
        else:
            out[k] = va
    for k in b:
        out.setdefault(k, b[k])
    return out


def make_palette(keyframes):
    """Return a `palette_for_phase(phase)` closure for a biome's own keyframes
    = sorted list of (phase, dict). Identical model to game/biome.py: smoothstep
    eased blend between the two surrounding anchors, wrapping at 1.0."""
    kf = sorted(keyframes, key=lambda p: p[0])
    # Ensure the cycle closes: if no anchor at >=1.0, append a wrap of the first.
    if kf[-1][0] < 1.0:
        kf = kf + [(1.0, kf[0][1])]

    def palette_for_phase(phase: float) -> dict:
        phase = phase % 1.0
        for i in range(len(kf) - 1):
            t0, p0 = kf[i]
            t1, p1 = kf[i + 1]
            if t0 <= phase <= t1:
                span = t1 - t0
                t = (phase - t0) / span if span > 0 else 0.0
                t = t * t * (3 - 2 * t)  # smoothstep
                return _blend(p0, p1, t)
        return dict(kf[0][1])

    return palette_for_phase


def to_draw_palette(pal: dict) -> dict:
    """Add `stone_*` aliases (from `struct_*`) and any missing legacy keys so the
    existing palette-driven draw fns in game.* consume a biome dict unchanged."""
    out = dict(pal)
    out.setdefault('stone_light', pal.get('struct_light', (200, 195, 185)))
    out.setdefault('stone_mid', pal.get('struct_mid', (150, 140, 130)))
    out.setdefault('stone_dark', pal.get('struct_dark', (90, 82, 75)))
    out.setdefault('stone_accent', pal.get('struct_accent', (120, 110, 100)))
    out.setdefault('foliage_top', pal.get('foliage_top', (90, 150, 70)))
    out.setdefault('foliage_mid', pal.get('foliage_mid', (60, 115, 50)))
    out.setdefault('foliage_dark', pal.get('foliage_dark', (35, 75, 35)))
    out.setdefault('foliage_accent', pal.get('foliage_accent', (160, 200, 120)))
    return out


# ── parameter schemas ─────────────────────────────────────────────────────────

@dataclass
class SkyParams:
    """Eased stop positions + dither for the sky_field bake. Stops read the
    palette's sky_top/mid/bot/horizon; positions let a biome compress the grade
    toward the horizon. zenith_dark deepens the very top a touch."""
    positions: tuple = (0.0, 0.30, 0.62, 0.85, 1.0)
    dither_amp: float = 2.0
    zenith_dark: float = 0.06


@dataclass
class RidgeParams:
    """One terrain layer. The silhouette family is chosen by the post-processors
    (jag/spike/flat_top/notch) applied to the per-x sinusoid-sum height."""
    base_h: float                      # mean height above ground_y, fraction of ground_y
    octaves: tuple                     # ((freq, amp), ...) summed sinusoids
    parallax: float                    # scroll multiplier (far ~.06 .. near ~.28)
    color_key: str                     # palette key for the fill color
    jag: float = 0.0                   # >0 adds rocky high-freq teeth
    spike: float = 0.0                 # >0 narrow vertical karst towers
    flat_top: float = 0.0              # >0 quantizes peaks to mesa plateaus (px step)
    notch: float = 0.0                 # >0 carves a central crater dip (fraction)
    snow_line: Optional[float] = None  # if set, fill above this y-fraction with snow_tint
    seed: int = 0


@dataclass
class GroundParams:
    top_key: str = 'ground_top'
    mid_key: str = 'ground_mid'
    bot_key: str = 'ground_bot'


@dataclass
class BiomeSpec:
    name: str
    note: str
    keyframes: list                    # [(phase, palette_dict), ...]
    sky: SkyParams
    ridges: list                       # [RidgeParams far, mid, near]
    signature: Optional[Callable] = None   # signature(surf, ctx)
    foliage: Optional[Callable] = None     # foliage(surf, ctx)
    atmosphere: Optional[Callable] = None  # atmosphere(surf, ctx) drawn over sky
    ground: GroundParams = field(default_factory=GroundParams)

    def __post_init__(self):
        self._pal = make_palette(self.keyframes)

    def palette_for_phase(self, phase):
        return self._pal(phase)


# ── ridge generator (generalizes game/draw.py:draw_mountains) ─────────────────

def _ridge_height(x, gp: RidgeParams, ground_y, w):
    """Per-x height above ground_y for one ridge, in pixels, before clamping."""
    h = gp.base_h * ground_y
    for f, a in gp.octaves:
        h += math.sin(x * f + gp.seed) * a
    if gp.jag:
        # rocky teeth: rectified high-freq adds sharp upward spikes
        h += abs(math.sin(x * 0.09 + gp.seed)) * (gp.jag * ground_y * 0.18)
    if gp.spike:
        # Slender karst spires (Guilin towers): a higher-frequency rectified
        # sine raised to a high power gives narrow, well-separated vertical
        # fingers rather than one broad dome. A second offset sine varies their
        # height so they don't read as a regular comb.
        s = math.sin(x * 0.045 + gp.seed * 1.7)
        if s > 0:
            vary = 0.7 + 0.3 * math.sin(x * 0.013 + gp.seed)
            h += (s ** 6) * gp.spike * ground_y * 0.42 * vary
    if gp.notch:
        # caldera rim: subtract a broad gaussian dip near the horizontal centre
        d = (x - w * 0.5) / (w * 0.5)
        h -= math.exp(-(d * d) / 0.06) * gp.notch * ground_y * 0.45
    if gp.flat_top:
        h = round(h / gp.flat_top) * gp.flat_top
    return h


def draw_ridge(surf, scroll, ground_y, w, color, gp: RidgeParams, snow_tint=None):
    pts = [(0, ground_y)]
    snow_pts = []
    snow_y = (gp.snow_line * ground_y) if gp.snow_line is not None else None
    for x in range(0, w + 1, 2):
        sx = x + scroll * gp.parallax
        h = _ridge_height(sx, gp, ground_y, w)
        y = int(ground_y - h)
        pts.append((x, y))
        if snow_y is not None and y < snow_y:
            snow_pts.append((x, y))
    pts.append((w, ground_y))
    pygame.draw.polygon(surf, color, pts)
    # Snow caps: re-walk the silhouette above the snow line and fill the cap
    # with snow_tint clipped to the ridge top.
    if snow_y is not None and snow_pts and snow_tint is not None:
        cap = [(snow_pts[0][0], snow_y)]
        cap += snow_pts
        cap += [(snow_pts[-1][0], snow_y)]
        if len(cap) >= 3:
            pygame.draw.polygon(surf, snow_tint, cap)


# ── render context handed to signature / foliage / atmosphere callbacks ───────

@dataclass
class SceneCtx:
    surf: pygame.Surface
    w: int
    h: int
    ground_y: int
    phase: float
    scroll: float
    pal: dict          # raw biome palette at this stage
    dpal: dict         # to_draw_palette(pal) — has stone_* aliases for legacy fns


# ── the scene painter ─────────────────────────────────────────────────────────

# A fixed scroll so every tile composites the same world layout — only the
# biome + stage change across the grid, which is what's under review.
DEFAULT_SCROLL = 760.0


def paint_scene(surf, spec: BiomeSpec, w, h, ground_y, phase, scroll=DEFAULT_SCROLL):
    pal = spec.palette_for_phase(phase)
    dpal = to_draw_palette(pal)
    ctx = SceneCtx(surf, w, h, ground_y, phase, scroll, pal, dpal)

    # 1. sky — baked OKLab + dithered gradient from the 4 stage stops
    sky_top = pal.get('sky_top', (40, 110, 200))
    stops_cols = [
        sf.with_value(sky_top, -spec.sky.zenith_dark),
        pal.get('sky_top', sky_top),
        pal.get('sky_mid', (120, 170, 220)),
        pal.get('sky_bot', (200, 220, 240)),
        pal.get('horizon', (245, 235, 215)),
    ]
    stops = list(zip(spec.sky.positions, stops_cols))
    sky = sf.make_sky_field(w, ground_y, stops, dither_amp=spec.sky.dither_amp)
    surf.blit(sky, (0, 0))

    # 2. atmosphere over the sky (clouds / mist / moon) — optional per biome
    if spec.atmosphere:
        spec.atmosphere(ctx)

    # 3-5. ridges far → near
    snow_tint = pal.get('snow_tint', (236, 240, 248))
    for gp in spec.ridges:
        draw_ridge(surf, scroll, ground_y, w, pal.get(gp.color_key, (60, 70, 110)),
                   gp, snow_tint=snow_tint)

    # 6. signature hero structure on the near-ridge baseline
    if spec.signature:
        spec.signature(ctx)

    # 7. ground band
    g_top = pal.get(spec.ground.top_key, (70, 120, 60))
    g_mid = pal.get(spec.ground.mid_key, (45, 90, 45))
    g_bot = pal.get(spec.ground.bot_key, (40, 55, 35))
    gstops = [(0.0, g_top), (0.4, g_mid), (1.0, g_bot)]
    band = make_gradient_surface(w, h - ground_y, gstops)
    surf.blit(band, (0, ground_y))

    # 8. foreground foliage
    if spec.foliage:
        spec.foliage(ctx)

    # 9. night fx — stars gated on star_alpha
    sa = int(pal.get('star_alpha', 0))
    if sa > 0:
        _scatter_stars(surf, w, ground_y, sa)


def _scatter_stars(surf, w, ground_y, sa):
    """Width-seeded star sprinkle (shared layout across stages so stars don't
    jump between adjacent columns)."""
    import random as _r
    rng = _r.Random(w * 7919)
    band = int(ground_y * 0.62)
    n = 50 if sa > 150 else 26
    for _ in range(n):
        sx = rng.randint(0, w - 1)
        sy = rng.randint(0, band)
        r = rng.choice((1, 1, 1, 2))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, sa), (r + 1, r + 1), r)
        surf.blit(s, (sx, sy))


# ── shared atmosphere / glow helpers (lifted for reuse by biome atmospheres) ──

def soft_disc(surf, cx, cy, r, color, glow_alpha=120):
    """A sun/moon disc with a soft halo. Used by night/golden biomes. Halo kept
    tight (≈1.8x) and blitted with NORMAL alpha — BLEND_RGB_ADD ignores the
    per-pixel alpha of a glow surface and would dump the full color as a solid
    bright blob, so the halo must alpha-composite instead."""
    halo = make_glow_surface(int(r * 1.8), color, alpha_center=glow_alpha, falloff=2.8)
    surf.blit(halo, (int(cx - halo.get_width() / 2), int(cy - halo.get_height() / 2)))
    disc = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(disc, color, (r + 1, r + 1), r)
    surf.blit(disc, (int(cx - r), int(cy - r)))


def mist_bands(surf, w, ground_y, color, y0_frac, n=4, alpha=70):
    """Flat, full-width horizontal haze strips with a soft vertical falloff — the
    shan-shui mist read. Strips rather than wide ellipses so the haze stays a
    level band and never curves into a visible dome at the frame edges."""
    layer = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    for k in range(n):
        cy = int(ground_y * (y0_frac + 0.05 * k))
        half = max(2, int(ground_y * (0.045 + 0.012 * (n - k))))
        a0 = alpha * (1 - k / (n + 1))
        for dy in range(-half, half + 1):
            yy = cy + dy
            if 0 <= yy < ground_y:
                a = int(a0 * (1 - abs(dy) / half))
                if a > 0:
                    pygame.draw.line(layer, (*color, a), (0, yy), (w, yy))
    surf.blit(layer, (0, 0))
