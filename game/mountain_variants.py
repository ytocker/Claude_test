"""Mountain-rendering variants used for design exploration.

Each ``draw_mountains_vN`` function is a drop-in replacement for
``game.draw.draw_mountains`` — same signature, same parallax scrolling,
same biome-palette integration via ``far_color`` / ``near_color``. The
helper functions at the top are shared by multiple variants.
"""
from __future__ import annotations

import math
import random

import pygame


# ── shared helpers ─────────────────────────────────────────────────────────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    """Linear blend between two RGB tuples; t=0 → a, t=1 → b."""
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, delta):
    """Add a flat amount to every channel (positive = lighter)."""
    return (_clamp(c[0] + delta), _clamp(c[1] + delta), _clamp(c[2] + delta))


_SKY_TINT = (200, 210, 230)


def _back_tint(far_color):
    """Same back-layer tint used by the original draw_mountains."""
    return _mix(far_color, _SKY_TINT, 0.5)


def _is_warm_phase(near_color):
    """Heuristic: warm-tinted palettes (sunset / sunrise / golden hour) have
    red >= blue. Used by variants that want to swing rim-light direction or
    intensity at the warm phases."""
    return near_color[0] >= near_color[2]


# ── V1: detailed classic ───────────────────────────────────────────────────
# Same sine-wave silhouette as today, plus snow caps, dotted rocks, a
# rim-light edge on the near layer at warm phases, and a darker shadow
# stripe along the base of the near layer.

def draw_mountains_v1(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far_color = far_color or (35, 45, 100)
    near_color = near_color or (22, 30, 72)
    back_color = _back_tint(far_color)

    pts_back, pts_far, pts_near = [(0, ground_y)], [(0, ground_y)], [(0, ground_y)]
    near_heights: list[tuple[int, int]] = []  # (x, peak_y) sampled for caps
    far_heights: list[tuple[int, int]] = []
    for x in range(0, w + 1, 2):
        bx = x + scroll * 0.06
        hb = int(105 + math.sin(bx * 0.008) * 32 + math.sin(bx * 0.023 + 2.1) * 14)
        pts_back.append((x, ground_y - hb))

        fx = x + scroll * 0.15
        hf = int(80 + math.sin(fx * 0.012) * 42 + math.sin(fx * 0.031) * 22)
        pts_far.append((x, ground_y - hf))
        far_heights.append((x, ground_y - hf))

        nx = x + scroll * 0.28
        hn = int(55 + math.sin(nx * 0.019 + 1.4) * 34 + math.sin(nx * 0.047 + 0.7) * 16)
        pts_near.append((x, ground_y - hn))
        near_heights.append((x, ground_y - hn))

    for pts in (pts_back, pts_far, pts_near):
        pts.append((w, ground_y))
    pygame.draw.polygon(surf, back_color, pts_back)
    pygame.draw.polygon(surf, far_color, pts_far)
    pygame.draw.polygon(surf, near_color, pts_near)

    # Snow caps on the tallest near peaks. We find local maxima by scanning
    # the sampled heights, then paint a small near-white triangle on top.
    snow = _mix(near_color, (245, 248, 255), 0.85)
    n = len(near_heights)
    for i in range(2, n - 2):
        y = near_heights[i][1]
        # local minimum in y == local maximum in height
        if (y < near_heights[i - 1][1] and y < near_heights[i - 2][1]
                and y < near_heights[i + 1][1] and y < near_heights[i + 2][1]
                and (ground_y - y) > 60):
            x = near_heights[i][0]
            cap = [(x - 6, y + 5), (x, y - 1), (x + 6, y + 4)]
            pygame.draw.polygon(surf, snow, cap)

    # A few snow caps on the far layer too (smaller, tinted closer to far).
    far_snow = _mix(far_color, (235, 240, 250), 0.7)
    for i in range(3, len(far_heights) - 3, 5):
        y = far_heights[i][1]
        if (y < far_heights[i - 2][1] and y < far_heights[i + 2][1]
                and (ground_y - y) > 90):
            x = far_heights[i][0]
            pygame.draw.polygon(surf, far_snow,
                                [(x - 4, y + 4), (x, y - 1), (x + 4, y + 3)])

    # Dotted rocks along the near silhouette (just below the ridge).
    rng = random.Random(int(scroll) // 4)
    dark = _shade(near_color, -20)
    for _ in range(12):
        i = rng.randrange(4, n - 4)
        x = near_heights[i][0]
        y = near_heights[i][1] + rng.randint(8, 26)
        if y < ground_y - 4:
            pygame.draw.circle(surf, dark, (x, y), 2)

    # Rim-light: 1-px highlight along the top of the near ridge at warm
    # biome phases.
    if _is_warm_phase(near_color):
        rim = _mix(near_color, (255, 230, 190), 0.6)
        for i in range(1, n):
            x0, y0 = near_heights[i - 1]
            x1, y1 = near_heights[i]
            pygame.draw.line(surf, rim, (x0, y0 - 1), (x1, y1 - 1), 1)

    # Shadow stripe along the base of the near layer — adds weight to the
    # foreground without obscuring pillars.
    base_band = pygame.Surface((w, 10), pygame.SRCALPHA)
    base_band.fill((0, 0, 0, 35))
    surf.blit(base_band, (0, ground_y - 10))


# ── V2: misty layered ridges ───────────────────────────────────────────────
# Same sine-wave family, expanded from 3 → 6 parallax bands. Each band
# fades further toward the sky tint, producing strong atmospheric depth.

def draw_mountains_v2(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far_color = far_color or (35, 45, 100)
    near_color = near_color or (22, 30, 72)

    bands = 6
    # Speeds interpolated from 0.04 (deepest) → 0.30 (nearest).
    # Heights interpolated from very low (~50) → tall (~90).
    # Amplitudes scale with depth too so distant ridges are gentler.
    for i in range(bands):
        depth = i / (bands - 1)  # 0 = deepest, 1 = nearest
        speed = 0.04 + depth * 0.26
        base_h = 50 + depth * 40
        amp_a = 18 + depth * 28
        amp_b = 6 + depth * 18
        freq_a = 0.006 + depth * 0.012
        freq_b = 0.018 + depth * 0.025
        phase_a = i * 0.7
        phase_b = i * 1.9 + 2.0

        color = _mix(_SKY_TINT, near_color, 0.18 + depth * 0.82)
        # Mid bands lean toward far_color for warm/cool palette spread.
        color = _mix(color, far_color, 0.25 * (1.0 - abs(depth - 0.6)))

        pts = [(0, ground_y)]
        for x in range(0, w + 1, 2):
            sx = x + scroll * speed
            h = int(base_h
                    + math.sin(sx * freq_a + phase_a) * amp_a
                    + math.sin(sx * freq_b + phase_b) * amp_b)
            pts.append((x, ground_y - h))
        pts.append((w, ground_y))
        pygame.draw.polygon(surf, color, pts)


# ── V3: low-poly faceted peaks ─────────────────────────────────────────────
# Triangular peaks built from explicit polygons. Each peak has a lit face
# and a shadow face; midtone fills the gaps. Gives a crisp vector look.

def _v3_layer(surf, ground_y, w, scroll, speed, base_h, peak_w, jitter,
              color_mid, color_lit, color_shadow, seed_off):
    """Draw one layer of faceted triangular peaks."""
    # Peaks are anchored to world-x so they scroll smoothly. The "world"
    # repeats every (peak_w * many) so we just generate enough to cover
    # the screen with margin.
    world_x_start = scroll * speed
    first = int(world_x_start // peak_w) - 1
    last = int((world_x_start + w) // peak_w) + 2

    # Build a polyline of peak/valley vertices first, then fill triangles
    # between consecutive peaks to form lit/shadow faces.
    verts: list[tuple[int, int]] = []
    for k in range(first, last + 1):
        # deterministic jitter per peak index
        rng = random.Random(k * 73856093 ^ seed_off)
        wx = k * peak_w + rng.uniform(-peak_w * 0.2, peak_w * 0.2)
        h = base_h + rng.uniform(-jitter, jitter)
        # Valleys halfway between peaks, deeper for taller peaks.
        valley_wx = wx - peak_w * 0.5
        valley_h = max(8, base_h * 0.35 + rng.uniform(-jitter * 0.4, jitter * 0.2))
        verts.append((valley_wx - world_x_start, ground_y - valley_h))
        verts.append((wx - world_x_start, ground_y - h))
    # Close the silhouette so we can paint a base midtone underneath
    # before stamping facets on top.
    sil = [(verts[0][0], ground_y)] + verts + [(verts[-1][0], ground_y)]
    pygame.draw.polygon(surf, color_mid, sil)

    # Now stamp lit/shadow facets. Each peak (odd-indexed vertex) gets a
    # left facet (shadow) from valley→peak, and a right facet (lit) from
    # peak→next valley.
    for i in range(1, len(verts) - 1, 2):
        peak = verts[i]
        left_valley = verts[i - 1]
        right_valley = verts[i + 1] if i + 1 < len(verts) else (peak[0] + peak_w * 0.5, ground_y)
        # Shadow face (left of peak)
        pygame.draw.polygon(surf, color_shadow,
                            [left_valley, peak, (peak[0], ground_y)])
        # Lit face (right of peak)
        pygame.draw.polygon(surf, color_lit,
                            [peak, right_valley, (peak[0], ground_y)])


def draw_mountains_v3(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far_color = far_color or (35, 45, 100)
    near_color = near_color or (22, 30, 72)
    back_color = _back_tint(far_color)

    warm = _is_warm_phase(near_color)
    # Warm bias for lit face at golden hour / sunset / sunrise; cool at night.
    lit_tint = (255, 220, 170) if warm else (190, 200, 230)

    # back layer — very pale, gentle peaks
    _v3_layer(surf, ground_y, w, scroll,
              speed=0.06, base_h=95, peak_w=90, jitter=18,
              color_mid=back_color,
              color_lit=_mix(back_color, lit_tint, 0.45),
              color_shadow=_shade(back_color, -15),
              seed_off=11)
    # far layer — medium peaks
    _v3_layer(surf, ground_y, w, scroll,
              speed=0.15, base_h=95, peak_w=70, jitter=24,
              color_mid=far_color,
              color_lit=_mix(far_color, lit_tint, 0.55),
              color_shadow=_shade(far_color, -22),
              seed_off=23)
    # near layer — taller / sharper peaks
    _v3_layer(surf, ground_y, w, scroll,
              speed=0.28, base_h=80, peak_w=58, jitter=30,
              color_mid=near_color,
              color_lit=_mix(near_color, lit_tint, 0.55),
              color_shadow=_shade(near_color, -28),
              seed_off=37)


# ── V4: forested hills + distant range ─────────────────────────────────────
# Rounded foreground hills with scattered pine silhouettes, plus a taller
# snow-capped range peeking up behind. Most character lives in the trees.

def _v4_pine(surf, x, base_y, height, color):
    """A small triangular pine silhouette pointing up."""
    half = max(2, height // 3)
    pygame.draw.polygon(surf, color,
                        [(x, base_y - height),
                         (x - half, base_y),
                         (x + half, base_y)])
    # Trunk hint
    pygame.draw.line(surf, color, (x, base_y), (x, base_y + 1), 1)


def draw_mountains_v4(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far_color = far_color or (35, 45, 100)
    near_color = near_color or (22, 30, 72)
    back_color = _back_tint(far_color)

    # ── BACK: snow-capped distant range (sharper triangles) ──
    back_speed = 0.05
    pts_back = [(0, ground_y)]
    peaks: list[tuple[int, int]] = []
    range_step = 55
    range_phase = scroll * back_speed
    first = int(range_phase // range_step) - 1
    last = int((range_phase + w) // range_step) + 2
    pts_back = [(0, ground_y)]
    prev_x = 0
    for k in range(first, last + 1):
        rng = random.Random(k * 2654435761 & 0xFFFFFFFF)
        wx = k * range_step + rng.uniform(-12, 12)
        sx = wx - range_phase
        h = 95 + rng.uniform(-20, 25)
        valley_h = 50 + rng.uniform(-10, 10)
        # Left valley
        pts_back.append((sx - range_step * 0.5, ground_y - valley_h))
        # Peak
        pts_back.append((sx, ground_y - h))
        peaks.append((int(sx), int(ground_y - h)))
        prev_x = sx
    pts_back.append((w, ground_y))
    pygame.draw.polygon(surf, back_color, pts_back)

    # Snow caps on the back range
    snow = _mix(back_color, (240, 245, 255), 0.85)
    for px, py in peaks:
        if -10 < px < w + 10:
            pygame.draw.polygon(surf, snow,
                                [(px - 5, py + 6), (px, py - 1), (px + 5, py + 5)])

    # ── FAR: rolling mid hills (rounded, sine-based) ──
    far_pts = [(0, ground_y)]
    far_heights: list[tuple[int, int]] = []
    far_speed = 0.14
    for x in range(0, w + 1, 2):
        fx = x + scroll * far_speed
        h = int(60 + math.sin(fx * 0.013) * 22 + math.sin(fx * 0.029 + 1.7) * 10)
        far_pts.append((x, ground_y - h))
        far_heights.append((x, ground_y - h))
    far_pts.append((w, ground_y))
    pygame.draw.polygon(surf, far_color, far_pts)

    # ── NEAR: rolling foreground hills with pine trees ──
    near_pts = [(0, ground_y)]
    near_heights: list[tuple[int, int]] = []
    near_speed = 0.28
    for x in range(0, w + 1, 2):
        nx = x + scroll * near_speed
        h = int(42 + math.sin(nx * 0.017) * 18 + math.sin(nx * 0.041 + 0.6) * 8)
        near_pts.append((x, ground_y - h))
        near_heights.append((x, ground_y - h))
    near_pts.append((w, ground_y))
    pygame.draw.polygon(surf, near_color, near_pts)

    # Pine silhouettes on the near layer. Spaced every ~24 px in world-x so
    # they scroll consistently. Color is darker than near so they pop.
    tree_color = _shade(near_color, -22)
    tree_step = 22
    tree_phase = scroll * near_speed
    first_t = int(tree_phase // tree_step) - 1
    last_t = int((tree_phase + w) // tree_step) + 2
    for k in range(first_t, last_t + 1):
        rng = random.Random((k * 1103515245 + 12345) & 0xFFFFFFFF)
        wx = k * tree_step + rng.uniform(-6, 6)
        sx = int(wx - tree_phase)
        if 0 <= sx < w:
            # Find ridge height at this sx (sampled near_heights are step=2)
            idx = min(len(near_heights) - 1, max(0, sx // 2))
            ridge_y = near_heights[idx][1]
            ht = rng.randint(7, 14)
            _v4_pine(surf, sx, ridge_y + 4, ht, tree_color)


# ── V5: painterly stylised peaks ───────────────────────────────────────────
# Jittered ridge lines (not pure sine), cross-hatched shadow flank, soft
# rim-light glow on the lit side, faint texture noise.

def _v5_ridge(surf, scroll, ground_y, w, speed, base_h, amp, freq, jitter_seed,
              fill_color, shadow_color, rim_color, hatch=True):
    """Render one painterly ridge band with shadow hatching and rim glow."""
    pts = [(0, ground_y)]
    heights: list[tuple[int, int]] = []
    # Use deterministic jitter so the line stays the same across frames at
    # the same scroll. Sampling at step=3 gives a slightly chunky feel.
    step = 3
    for x in range(0, w + 1, step):
        sx = x + scroll * speed
        # Jitter via sin-of-prime sums — looks hand-drawn vs pure sine.
        j = (math.sin(sx * 0.071 + jitter_seed) * 4.0
             + math.sin(sx * 0.193 + jitter_seed * 1.6) * 2.0)
        h = int(base_h + math.sin(sx * freq) * amp + j)
        pts.append((x, ground_y - h))
        heights.append((x, ground_y - h))
    pts.append((w, ground_y))
    pygame.draw.polygon(surf, fill_color, pts)

    # Shadow flank: a translucent darker fill applied just below the ridge
    # on the "left" side (since light comes from the right in this style).
    if hatch:
        shadow_surf = pygame.Surface((w, ground_y), pygame.SRCALPHA)
        # Build a band from ridge down ~22 px, then mask to the silhouette.
        for i in range(1, len(heights)):
            x0, y0 = heights[i - 1]
            x1, y1 = heights[i]
            # If this segment slopes down to the right (left flank of a
            # peak), draw a hatch line into shadow_surf.
            if y1 > y0:
                for d in (4, 9, 14):
                    pygame.draw.line(shadow_surf,
                                     (shadow_color[0], shadow_color[1],
                                      shadow_color[2], 70),
                                     (x0 + d, y0 + d),
                                     (x1 + d, y1 + d), 1)
        surf.blit(shadow_surf, (0, 0))

    # Rim glow: 2-px soft highlight along the top edge, brightest where
    # the ridge faces right (slope rises to the right).
    glow = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    for i in range(1, len(heights)):
        x0, y0 = heights[i - 1]
        x1, y1 = heights[i]
        # Slope rising right ↔ y decreasing as x increases.
        if y1 <= y0:
            a = 140
            pygame.draw.line(glow,
                             (rim_color[0], rim_color[1], rim_color[2], a),
                             (x0, y0 - 1), (x1, y1 - 1), 2)
    surf.blit(glow, (0, 0))


def draw_mountains_v5(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far_color = far_color or (35, 45, 100)
    near_color = near_color or (22, 30, 72)
    back_color = _back_tint(far_color)

    warm = _is_warm_phase(near_color)
    rim_tint = (255, 225, 180) if warm else (210, 220, 245)

    _v5_ridge(surf, scroll, ground_y, w,
              speed=0.06, base_h=100, amp=28, freq=0.010,
              jitter_seed=0.7,
              fill_color=back_color,
              shadow_color=_shade(back_color, -10),
              rim_color=_mix(back_color, rim_tint, 0.4),
              hatch=False)
    _v5_ridge(surf, scroll, ground_y, w,
              speed=0.15, base_h=80, amp=38, freq=0.013,
              jitter_seed=1.9,
              fill_color=far_color,
              shadow_color=_shade(far_color, -25),
              rim_color=_mix(far_color, rim_tint, 0.55),
              hatch=True)
    _v5_ridge(surf, scroll, ground_y, w,
              speed=0.28, base_h=58, amp=34, freq=0.018,
              jitter_seed=3.1,
              fill_color=near_color,
              shadow_color=_shade(near_color, -30),
              rim_color=_mix(near_color, rim_tint, 0.65),
              hatch=True)

    # Faint paper-grain noise over the whole mountain band.
    noise = pygame.Surface((w, 140), pygame.SRCALPHA)
    rng = random.Random(int(scroll) // 6)
    for _ in range(220):
        nx = rng.randrange(0, w)
        ny = rng.randrange(0, 140)
        a = rng.randint(8, 22)
        noise.set_at((nx, ny), (240, 235, 220, a))
    surf.blit(noise, (0, ground_y - 140))


# ── dispatcher ─────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_mountains_v1,
    2: draw_mountains_v2,
    3: draw_mountains_v3,
    4: draw_mountains_v4,
    5: draw_mountains_v5,
}

VARIANT_NAMES = {
    1: "Detailed Classic",
    2: "Misty Layered Ridges",
    3: "Low-Poly Faceted Peaks",
    4: "Forested Hills + Distant Range",
    5: "Painterly Stylised Peaks",
}
