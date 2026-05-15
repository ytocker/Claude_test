"""Mountain-rendering variants used for design exploration.

Each ``draw_mountains_vN`` function is a drop-in replacement for
``game.draw.draw_mountains`` — same signature, same parallax scrolling.
Unlike the original, each variant has its OWN inherent palette and shape
language. The biome ``far_color`` / ``near_color`` is applied at the end
as a thin ambient overlay so the mountain identity dominates while the
scene still feels right at day/sunset/night.
"""
from __future__ import annotations

import math
import random

import pygame


# ── shared helpers ─────────────────────────────────────────────────────────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, delta):
    return (_clamp(c[0] + delta), _clamp(c[1] + delta), _clamp(c[2] + delta))


def _brightness(c) -> float:
    """0..1 estimate of how 'bright' a biome colour is."""
    return min(1.0, (c[0] + c[1] + c[2]) / 510.0)


def _warmth(c) -> float:
    """Positive if the colour is warm-leaning (sunset/sunrise/golden)."""
    return (c[0] - c[2]) / 255.0


def _ambient_overlay(surf, ground_y, w, near_color):
    """Apply a translucent overlay that:
      • darkens the mountains at night-leaning biomes,
      • adds a warm wash at sunset/sunrise.
    The overlay covers only the mountain band so the rest of the scene is
    unaffected.
    """
    b = _brightness(near_color)
    band = pygame.Surface((w, ground_y), pygame.SRCALPHA)

    if b < 0.6:
        # Darken: fade toward the dark near_color.
        alpha = int(160 * (0.6 - b))
        band.fill((near_color[0] // 3, near_color[1] // 3,
                   near_color[2] // 3, alpha))

    w_amt = _warmth(near_color)
    if w_amt > 0.05:
        alpha = int(min(85, w_amt * 220))
        warm = pygame.Surface((w, ground_y), pygame.SRCALPHA)
        warm.fill((255, 150, 90, alpha))
        band.blit(warm, (0, 0))

    surf.blit(band, (0, 0))


# ── V1: Crystal Geode Spires ───────────────────────────────────────────────

_V1_BACK = (60, 70, 120)
_V1_MID_SHARDS = [(80, 150, 200), (100, 110, 200), (140, 90, 190)]
_V1_NEAR_SHARDS = [
    (110, 230, 240),  # cyan
    (170, 110, 230),  # violet
    (230, 130, 220),  # magenta
    (130, 240, 200),  # mint
    (210, 180, 255),  # lilac
    (240, 220, 130),  # gold tip
]


def _v1_shard(surf, base_x, base_y, height, width, color, lit_dir):
    """Single crystal shard: triangle silhouette + lit facet + bright tip."""
    half = width // 2
    apex = (base_x, base_y - height)
    left = (base_x - half, base_y)
    right = (base_x + half, base_y)

    # Base shadow side
    shadow = _shade(color, -55)
    pygame.draw.polygon(surf, shadow, [apex, left, right])

    # Lit facet: triangle from apex down one side
    lit = _mix(color, (255, 255, 255), 0.55)
    mid_x = base_x + (half - 2) * lit_dir
    pygame.draw.polygon(surf, color, [apex, (mid_x, base_y), right if lit_dir > 0 else left])
    pygame.draw.polygon(surf, lit, [apex, (mid_x, base_y),
                                    (base_x, base_y - 2)])

    # Bright tip
    tip = _mix(color, (255, 255, 255), 0.85)
    pygame.draw.polygon(surf, tip,
                        [apex,
                         (base_x - 2, base_y - height + 6),
                         (base_x + 2, base_y - height + 6)])

    # Inner glow (subtle additive blob near base)
    glow = pygame.Surface((width + 8, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(glow,
                        (color[0], color[1], color[2], 90),
                        glow.get_rect())
    surf.blit(glow, (base_x - (width + 8) // 2, base_y - 8))


def draw_mountains_v1(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far_color = far_color or (50, 60, 110)
    near_color = near_color or (30, 40, 80)

    # ── BACK: distant crystal silhouette (smooth) ──
    pts = [(0, ground_y)]
    for x in range(0, w + 1, 3):
        sx = x + scroll * 0.06
        h = int(100 + math.sin(sx * 0.013) * 28 + math.sin(sx * 0.031 + 1.2) * 14)
        pts.append((x, ground_y - h))
    pts.append((w, ground_y))
    pygame.draw.polygon(surf, _V1_BACK, pts)

    # ── MID: jagged crystal cluster (medium shards) ──
    mid_step = 38
    mid_phase = scroll * 0.15
    first = int(mid_phase // mid_step) - 1
    last = int((mid_phase + w) // mid_step) + 2
    for k in range(first, last + 1):
        rng = random.Random(k * 2654435761 & 0xFFFFFFFF)
        wx = k * mid_step + rng.uniform(-8, 8)
        sx = int(wx - mid_phase)
        ht = rng.randint(55, 95)
        wd = rng.randint(20, 32)
        col = rng.choice(_V1_MID_SHARDS)
        lit = rng.choice((-1, 1))
        if -wd < sx < w + wd:
            _v1_shard(surf, sx, ground_y, ht, wd, col, lit)

    # ── NEAR: tall hero shards in vivid colours ──
    near_step = 46
    near_phase = scroll * 0.28
    first = int(near_phase // near_step) - 1
    last = int((near_phase + w) // near_step) + 2
    near_centers: list[tuple[int, int, int]] = []  # (x, base_y, height)
    for k in range(first, last + 1):
        rng = random.Random((k * 73856093 + 19349663) & 0xFFFFFFFF)
        wx = k * near_step + rng.uniform(-10, 10)
        sx = int(wx - near_phase)
        ht = rng.randint(75, 130)
        wd = rng.randint(22, 38)
        col = _V1_NEAR_SHARDS[k % len(_V1_NEAR_SHARDS)]
        lit = rng.choice((-1, 1))
        if -wd < sx < w + wd:
            _v1_shard(surf, sx, ground_y, ht, wd, col, lit)
            near_centers.append((sx, ground_y - ht, ht))

    # ── Sparkles in the air above the shards ──
    sparkle_rng = random.Random(int(scroll) // 5)
    for _ in range(40):
        sx = sparkle_rng.randrange(0, w)
        sy = sparkle_rng.randrange(ground_y - 180, ground_y - 30)
        sz = sparkle_rng.choice((1, 1, 2))
        a = sparkle_rng.randint(140, 230)
        pygame.draw.circle(surf, (255, 255, 255, a)[:3], (sx, sy), sz)

    _ambient_overlay(surf, ground_y, w, near_color)


# ── V2: Sakura Blossom Hills ───────────────────────────────────────────────

_V2_BACK = (210, 180, 205)
_V2_MID = (200, 140, 165)
_V2_NEAR_GRASS = (135, 170, 110)
_V2_TRUNK = (75, 50, 40)
_V2_BLOSSOM = (255, 180, 205)
_V2_BLOSSOM_HI = (255, 230, 235)
_V2_BLOSSOM_DARK = (220, 130, 170)


def _v2_cherry_tree(surf, base_x, base_y, scale=1.0):
    """Cherry tree: brown trunk + pom-pom pink canopy with two highlight blobs."""
    trunk_h = int(18 * scale)
    canopy_r = int(14 * scale)
    # Trunk
    pygame.draw.line(surf, _V2_TRUNK,
                     (base_x, base_y),
                     (base_x, base_y - trunk_h), max(1, int(2 * scale)))
    # Branches
    pygame.draw.line(surf, _V2_TRUNK,
                     (base_x, base_y - trunk_h + 4),
                     (base_x - 5, base_y - trunk_h - 2), 1)
    pygame.draw.line(surf, _V2_TRUNK,
                     (base_x, base_y - trunk_h + 2),
                     (base_x + 5, base_y - trunk_h - 4), 1)
    # Canopy: 3 overlapping circles
    cy = base_y - trunk_h - 4
    pygame.draw.circle(surf, _V2_BLOSSOM_DARK,
                       (base_x - canopy_r // 2, cy + 1), canopy_r)
    pygame.draw.circle(surf, _V2_BLOSSOM_DARK,
                       (base_x + canopy_r // 2, cy + 1), canopy_r)
    pygame.draw.circle(surf, _V2_BLOSSOM_DARK,
                       (base_x, cy - canopy_r // 3), canopy_r)
    pygame.draw.circle(surf, _V2_BLOSSOM,
                       (base_x - canopy_r // 2, cy), canopy_r - 2)
    pygame.draw.circle(surf, _V2_BLOSSOM,
                       (base_x + canopy_r // 2, cy), canopy_r - 2)
    pygame.draw.circle(surf, _V2_BLOSSOM,
                       (base_x, cy - canopy_r // 3), canopy_r - 2)
    # Highlights
    pygame.draw.circle(surf, _V2_BLOSSOM_HI,
                       (base_x - canopy_r // 2 - 2, cy - 4), max(2, canopy_r // 3))
    pygame.draw.circle(surf, _V2_BLOSSOM_HI,
                       (base_x + canopy_r // 4, cy - canopy_r // 3 - 3),
                       max(2, canopy_r // 4))


def draw_mountains_v2(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far_color = far_color or (50, 60, 110)
    near_color = near_color or (30, 40, 80)

    # ── BACK: pale distant hills ──
    pts = [(0, ground_y)]
    for x in range(0, w + 1, 3):
        sx = x + scroll * 0.06
        h = int(95 + math.sin(sx * 0.010) * 22 + math.sin(sx * 0.027 + 0.8) * 10)
        pts.append((x, ground_y - h))
    pts.append((w, ground_y))
    pygame.draw.polygon(surf, _V2_BACK, pts)

    # Scatter distant blossom dots on back hills
    rng = random.Random(int(scroll) // 4 + 11)
    for _ in range(45):
        sx = rng.randrange(0, w)
        sy = ground_y - rng.randint(35, 100)
        pygame.draw.circle(surf, _V2_BLOSSOM, (sx, sy), 1)

    # ── MID: dusty rose hills ──
    pts = [(0, ground_y)]
    mid_heights: list[tuple[int, int]] = []
    for x in range(0, w + 1, 3):
        sx = x + scroll * 0.15
        h = int(70 + math.sin(sx * 0.014) * 26 + math.sin(sx * 0.033 + 1.4) * 12)
        pts.append((x, ground_y - h))
        mid_heights.append((x, ground_y - h))
    pts.append((w, ground_y))
    pygame.draw.polygon(surf, _V2_MID, pts)

    # Distant cherry trees on mid hills (smaller)
    mid_tree_step = 38
    mid_tree_phase = scroll * 0.15
    first = int(mid_tree_phase // mid_tree_step) - 1
    last = int((mid_tree_phase + w) // mid_tree_step) + 2
    for k in range(first, last + 1):
        rng = random.Random((k * 1103515245 + 12345) & 0xFFFFFFFF)
        wx = k * mid_tree_step + rng.uniform(-10, 10)
        sx = int(wx - mid_tree_phase)
        if 0 <= sx < w:
            idx = min(len(mid_heights) - 1, max(0, sx // 3))
            ridge_y = mid_heights[idx][1]
            _v2_cherry_tree(surf, sx, ridge_y + 4, scale=0.55)

    # ── NEAR: green foreground hills with cherry trees ──
    pts = [(0, ground_y)]
    near_heights: list[tuple[int, int]] = []
    for x in range(0, w + 1, 3):
        sx = x + scroll * 0.28
        h = int(48 + math.sin(sx * 0.018) * 20 + math.sin(sx * 0.041 + 0.5) * 9)
        pts.append((x, ground_y - h))
        near_heights.append((x, ground_y - h))
    pts.append((w, ground_y))
    pygame.draw.polygon(surf, _V2_NEAR_GRASS, pts)

    # Hero cherry trees on near hills
    near_tree_step = 28
    near_tree_phase = scroll * 0.28
    first = int(near_tree_phase // near_tree_step) - 1
    last = int((near_tree_phase + w) // near_tree_step) + 2
    for k in range(first, last + 1):
        rng = random.Random((k * 2654435761 + 7) & 0xFFFFFFFF)
        wx = k * near_tree_step + rng.uniform(-6, 6)
        sx = int(wx - near_tree_phase)
        if 0 <= sx < w:
            idx = min(len(near_heights) - 1, max(0, sx // 3))
            ridge_y = near_heights[idx][1]
            _v2_cherry_tree(surf, sx, ridge_y + 4, scale=1.0)

    # ── Drifting petals in the air ──
    rng = random.Random(int(scroll) // 7)
    for _ in range(35):
        px = rng.randrange(0, w)
        py = rng.randrange(ground_y - 200, ground_y - 30)
        pygame.draw.ellipse(surf, _V2_BLOSSOM,
                            (px, py, 4, 2))
        if rng.random() < 0.4:
            pygame.draw.ellipse(surf, _V2_BLOSSOM_HI,
                                (px, py, 2, 1))

    _ambient_overlay(surf, ground_y, w, near_color)


# ── V3: Candy Land ─────────────────────────────────────────────────────────

_V3_MINT_HILL = (170, 230, 180)
_V3_MINT_HILL_DK = (130, 200, 150)
_V3_PEPPERMINT_W = (255, 245, 240)
_V3_PEPPERMINT_R = (240, 90, 110)
_V3_FROST = (255, 255, 255)
_V3_GUMDROP_COLORS = [(255, 130, 180), (255, 230, 100), (210, 150, 230),
                      (130, 220, 230), (255, 180, 110)]
_V3_LOLLIPOP_COLORS = [(255, 100, 130), (110, 200, 255), (255, 220, 80),
                       (180, 130, 255)]
_V3_SPRINKLE_COLORS = [(255, 100, 130), (110, 200, 255), (255, 220, 80),
                       (180, 130, 255), (130, 230, 130), (255, 160, 80)]


def _v3_peppermint_cone(surf, base_x, base_y, height, width):
    """Striped peppermint candy cone: red and white diagonal stripes."""
    half = width // 2
    # Build silhouette polygon
    apex = (base_x, base_y - height)
    left = (base_x - half, base_y)
    right = (base_x + half, base_y)

    # Clip to the silhouette by drawing all stripes onto a temp surface
    # the size of the cone bbox, then mask via the polygon.
    bbox_w = width + 2
    bbox_h = height + 2
    temp = pygame.Surface((bbox_w, bbox_h), pygame.SRCALPHA)
    # Base fill = white
    pygame.draw.polygon(temp, _V3_PEPPERMINT_W,
                        [(half + 1, 1),
                         (1, bbox_h - 1),
                         (bbox_w - 1, bbox_h - 1)])
    # Diagonal red stripes
    stripe_spacing = 8
    for offset in range(-bbox_h, bbox_w + bbox_h, stripe_spacing):
        pygame.draw.line(temp, _V3_PEPPERMINT_R,
                         (offset, 0),
                         (offset + bbox_h, bbox_h),
                         3)
    # Re-mask: redraw silhouette outline with the cone shape clipped via
    # an alpha mask. Easier: just blit then redraw the silhouette polygon
    # in WHITE then re-draw red stripes constrained to the polygon. Skip
    # that and just blit the textured rect, accepting bleed outside — we
    # mask by re-drawing the silhouette outline.
    mask = pygame.Surface((bbox_w, bbox_h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(half + 1, 1),
                         (1, bbox_h - 1),
                         (bbox_w - 1, bbox_h - 1)])
    masked = pygame.Surface((bbox_w, bbox_h), pygame.SRCALPHA)
    masked.blit(temp, (0, 0))
    masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(masked, (base_x - half - 1, base_y - height - 1))

    # Frosting cap (white blob with drip on one side)
    cap_w = max(4, width - 6)
    pygame.draw.ellipse(surf, _V3_FROST,
                        (base_x - cap_w // 2, base_y - height - 4,
                         cap_w, 9))
    pygame.draw.circle(surf, _V3_FROST,
                       (base_x - cap_w // 3, base_y - height + 2), 3)


def _v3_gumdrop(surf, base_x, base_y, width, color):
    """Rounded gumdrop hill with shine and sprinkles."""
    half = width // 2
    height = int(width * 0.65)
    pygame.draw.ellipse(surf, _shade(color, -25),
                        (base_x - half, base_y - height, width, height * 2))
    pygame.draw.ellipse(surf, color,
                        (base_x - half + 1, base_y - height + 1,
                         width - 2, height * 2 - 2))
    # Highlight
    pygame.draw.ellipse(surf, _mix(color, (255, 255, 255), 0.55),
                        (base_x - half + 3, base_y - height + 2,
                         width // 3, height // 2))
    # Sprinkles
    rng = random.Random(base_x * 37 + width)
    for _ in range(int(width * 0.3)):
        sx = base_x + rng.randint(-half + 2, half - 2)
        sy = base_y - rng.randint(2, height - 2)
        c = rng.choice(_V3_SPRINKLE_COLORS)
        pygame.draw.line(surf, c, (sx, sy), (sx + 2, sy), 1)


def _v3_lollipop(surf, base_x, base_y, height, color):
    """Lollipop tree: white stick + swirl candy disc."""
    pygame.draw.line(surf, (255, 250, 250),
                     (base_x, base_y), (base_x, base_y - height), 2)
    r = 7
    cy = base_y - height
    pygame.draw.circle(surf, (255, 255, 255), (base_x, cy), r + 1)
    pygame.draw.circle(surf, color, (base_x, cy), r)
    # Swirl
    for i in range(3):
        a = i * 2.1
        for k in range(8):
            ang = a + k * 0.6
            radius = k * 0.7
            px = int(base_x + math.cos(ang) * radius)
            py = int(cy + math.sin(ang) * radius)
            pygame.draw.circle(surf, _V3_PEPPERMINT_W, (px, py), 1)


def draw_mountains_v3(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far_color = far_color or (50, 60, 110)
    near_color = near_color or (30, 40, 80)

    # ── BACK: pale mint hills with sprinkle dots ──
    pts = [(0, ground_y)]
    back_heights: list[tuple[int, int]] = []
    for x in range(0, w + 1, 3):
        sx = x + scroll * 0.06
        h = int(85 + math.sin(sx * 0.012) * 22 + math.sin(sx * 0.029 + 1.0) * 10)
        pts.append((x, ground_y - h))
        back_heights.append((x, ground_y - h))
    pts.append((w, ground_y))
    pygame.draw.polygon(surf, _V3_MINT_HILL, pts)

    # Sprinkles on back hills
    rng = random.Random(int(scroll) // 4 + 3)
    for _ in range(35):
        idx = rng.randrange(0, len(back_heights))
        bx, by = back_heights[idx]
        sy = by + rng.randint(4, 30)
        if sy < ground_y - 3:
            c = rng.choice(_V3_SPRINKLE_COLORS)
            pygame.draw.line(surf, c, (bx, sy), (bx + 2, sy), 1)

    # ── MID: peppermint cone peaks ──
    cone_step = 56
    cone_phase = scroll * 0.15
    first = int(cone_phase // cone_step) - 1
    last = int((cone_phase + w) // cone_step) + 2
    for k in range(first, last + 1):
        rng = random.Random((k * 1442695040888963407) & 0xFFFFFFFF)
        wx = k * cone_step + rng.uniform(-8, 8)
        sx = int(wx - cone_phase)
        ht = rng.randint(65, 105)
        wd = rng.randint(32, 50)
        if -wd < sx < w + wd:
            _v3_peppermint_cone(surf, sx, ground_y, ht, wd)

    # ── NEAR: gumdrop hills + lollipop trees ──
    # Foreground green slope first
    pts = [(0, ground_y)]
    near_heights: list[tuple[int, int]] = []
    for x in range(0, w + 1, 3):
        sx = x + scroll * 0.28
        h = int(34 + math.sin(sx * 0.020) * 14 + math.sin(sx * 0.047 + 0.3) * 6)
        pts.append((x, ground_y - h))
        near_heights.append((x, ground_y - h))
    pts.append((w, ground_y))
    pygame.draw.polygon(surf, _V3_MINT_HILL_DK, pts)

    # Gumdrops
    gum_step = 44
    gum_phase = scroll * 0.28
    first = int(gum_phase // gum_step) - 1
    last = int((gum_phase + w) // gum_step) + 2
    for k in range(first, last + 1):
        rng = random.Random((k * 73856093 + 19) & 0xFFFFFFFF)
        wx = k * gum_step + rng.uniform(-6, 6)
        sx = int(wx - gum_phase)
        if 0 <= sx < w:
            idx = min(len(near_heights) - 1, max(0, sx // 3))
            ridge_y = near_heights[idx][1]
            wd = rng.randint(22, 36)
            col = rng.choice(_V3_GUMDROP_COLORS)
            _v3_gumdrop(surf, sx, ridge_y + 6, wd, col)

    # Lollipop trees (sparser, between gumdrops)
    lolly_step = 38
    lolly_phase = scroll * 0.28
    first = int(lolly_phase // lolly_step) - 1
    last = int((lolly_phase + w) // lolly_step) + 2
    for k in range(first, last + 1):
        rng = random.Random((k * 2654435761 + 31337) & 0xFFFFFFFF)
        if rng.random() < 0.55:
            continue
        wx = k * lolly_step + 20 + rng.uniform(-4, 4)
        sx = int(wx - lolly_phase)
        if 0 <= sx < w:
            idx = min(len(near_heights) - 1, max(0, sx // 3))
            ridge_y = near_heights[idx][1]
            ht = rng.randint(18, 28)
            col = rng.choice(_V3_LOLLIPOP_COLORS)
            _v3_lollipop(surf, sx, ridge_y + 2, ht, col)

    _ambient_overlay(surf, ground_y, w, near_color)


# ── V4: Volcanic Range ─────────────────────────────────────────────────────

_V4_ROCK_BACK = (45, 35, 55)
_V4_ROCK_MID = (30, 22, 38)
_V4_ROCK_NEAR = (18, 14, 24)
_V4_LAVA_HOT = (255, 220, 80)
_V4_LAVA_MID = (255, 130, 40)
_V4_LAVA_DEEP = (200, 60, 30)
_V4_EMBER = (255, 200, 80)
_V4_SMOKE = (130, 110, 110)


def _v4_jagged_layer(surf, scroll, ground_y, w, speed, base_h, jitter, rock_color,
                     peak_step, seed_off, with_lava=False):
    """A jagged dark rocky silhouette. Returns peak (x, y) pairs."""
    phase = scroll * speed
    first = int(phase // peak_step) - 1
    last = int((phase + w) // peak_step) + 2
    pts = [(0, ground_y)]
    peaks: list[tuple[int, int]] = []
    # Use multiple sub-points between peaks to add jaggedness
    for k in range(first, last + 1):
        rng = random.Random((k * 73856093 ^ seed_off) & 0xFFFFFFFF)
        wx = k * peak_step + rng.uniform(-peak_step * 0.2, peak_step * 0.2)
        sx_peak = int(wx - phase)
        h = base_h + rng.uniform(-jitter, jitter)
        # valley before peak
        valley_x = sx_peak - peak_step // 2 + rng.randint(-4, 4)
        valley_h = max(15, base_h * 0.35 + rng.uniform(-jitter * 0.5, 0))
        pts.append((valley_x, ground_y - valley_h))
        # mid-rise jaggies
        for j in range(2):
            jx = valley_x + (sx_peak - valley_x) * (j + 1) // 3
            jh = valley_h + (h - valley_h) * (j + 1) / 3 + rng.uniform(-6, 6)
            pts.append((jx, ground_y - jh))
        pts.append((sx_peak, ground_y - int(h)))
        peaks.append((sx_peak, int(ground_y - h)))
    pts.append((w, ground_y))
    pygame.draw.polygon(surf, rock_color, pts)

    if with_lava:
        # Lava cracks: glowing veins radiating from peak down the rock face
        for px, py in peaks:
            if not (-30 < px < w + 30):
                continue
            rng = random.Random(px * 991)
            for _ in range(2):
                x1, y1 = px + rng.randint(-6, 6), py + rng.randint(2, 8)
                x2, y2 = x1 + rng.randint(-12, 12), y1 + rng.randint(20, 50)
                if y2 > ground_y - 2:
                    y2 = ground_y - 2
                pygame.draw.line(surf, _V4_LAVA_DEEP, (x1, y1), (x2, y2), 3)
                pygame.draw.line(surf, _V4_LAVA_MID, (x1, y1), (x2, y2), 1)
            # Bright crater
            pygame.draw.circle(surf, _V4_LAVA_DEEP, (px, py + 2), 4)
            pygame.draw.circle(surf, _V4_LAVA_MID, (px, py + 2), 3)
            pygame.draw.circle(surf, _V4_LAVA_HOT, (px, py + 2), 1)

    return peaks


def draw_mountains_v4(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far_color = far_color or (50, 60, 110)
    near_color = near_color or (30, 40, 80)

    _v4_jagged_layer(surf, scroll, ground_y, w,
                     speed=0.06, base_h=95, jitter=18,
                     rock_color=_V4_ROCK_BACK, peak_step=70, seed_off=11)
    _v4_jagged_layer(surf, scroll, ground_y, w,
                     speed=0.15, base_h=85, jitter=24,
                     rock_color=_V4_ROCK_MID, peak_step=60, seed_off=23,
                     with_lava=True)
    near_peaks = _v4_jagged_layer(surf, scroll, ground_y, w,
                                  speed=0.28, base_h=70, jitter=28,
                                  rock_color=_V4_ROCK_NEAR, peak_step=54,
                                  seed_off=37, with_lava=True)

    # Smoke plumes from peak tops
    smoke = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    for px, py in near_peaks:
        if not (-20 < px < w + 20):
            continue
        rng = random.Random(px * 8675309)
        for i in range(5):
            drift = rng.randint(-4, 6)
            r = 6 + i * 3
            cy = py - 8 - i * 9
            a = max(0, 90 - i * 18)
            pygame.draw.circle(smoke,
                               (_V4_SMOKE[0], _V4_SMOKE[1], _V4_SMOKE[2], a),
                               (px + drift, cy), r)
    surf.blit(smoke, (0, 0))

    # Ember sparks rising
    rng = random.Random(int(scroll) // 3)
    for _ in range(35):
        ex = rng.randrange(0, w)
        ey = rng.randrange(ground_y - 150, ground_y - 20)
        sz = rng.choice((1, 1, 2))
        pygame.draw.circle(surf, _V4_EMBER, (ex, ey), sz)
    # Brighter sparks (additive feel)
    glow_layer = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    for _ in range(10):
        ex = rng.randrange(0, w)
        ey = rng.randrange(ground_y - 100, ground_y - 10)
        pygame.draw.circle(glow_layer, (255, 180, 60, 120), (ex, ey), 3)
        pygame.draw.circle(glow_layer, (255, 230, 130, 200), (ex, ey), 1)
    surf.blit(glow_layer, (0, 0))

    # Lava pool at the base (thin glowing strip)
    pool = pygame.Surface((w, 6), pygame.SRCALPHA)
    for x in range(0, w, 2):
        h = int(2 + math.sin((x + scroll * 0.4) * 0.05) * 1.5)
        pool.fill((255, 100, 30, 0))
        pygame.draw.line(pool, (255, 130, 40, 160),
                         (x, 6 - h), (x, 6), 1)
    # The above only fills last column — replace with a simpler glow band:
    pool = pygame.Surface((w, 5), pygame.SRCALPHA)
    pool.fill((255, 110, 40, 90))
    surf.blit(pool, (0, ground_y - 4))

    _ambient_overlay(surf, ground_y, w, near_color)


# ── V5: Mushroom Fairy Forest ──────────────────────────────────────────────

_V5_FOREST_BACK = (45, 30, 75)
_V5_FOREST_MID = (65, 45, 100)
_V5_FLOOR = (40, 70, 55)
_V5_STEM = (245, 230, 200)
_V5_STEM_SHADE = (200, 180, 150)
_V5_CAPS = [
    (230, 70, 70),   # red
    (90, 150, 230),  # blue
    (180, 100, 220), # purple
    (110, 210, 200), # teal
    (255, 160, 90),  # orange
    (230, 100, 170), # pink
]


def _v5_mushroom(surf, base_x, base_y, scale, cap_color, seed):
    """Mushroom with stem, dome cap, and white spots."""
    rng = random.Random(seed)
    stem_w = max(3, int(6 * scale))
    stem_h = int(30 * scale)
    cap_w = int(28 * scale)
    cap_h = int(18 * scale)

    # Stem (rounded rectangle)
    pygame.draw.rect(surf, _V5_STEM_SHADE,
                     (base_x - stem_w // 2 - 1, base_y - stem_h,
                      stem_w + 2, stem_h),
                     border_radius=max(1, stem_w // 2))
    pygame.draw.rect(surf, _V5_STEM,
                     (base_x - stem_w // 2, base_y - stem_h,
                      stem_w, stem_h - 2),
                     border_radius=max(1, stem_w // 2))
    # Cap (dome = ellipse cropped at midline)
    cap_y = base_y - stem_h - cap_h // 3
    pygame.draw.ellipse(surf, _shade(cap_color, -30),
                        (base_x - cap_w // 2, cap_y - cap_h,
                         cap_w, cap_h * 2))
    pygame.draw.ellipse(surf, cap_color,
                        (base_x - cap_w // 2 + 1, cap_y - cap_h + 1,
                         cap_w - 2, cap_h * 2 - 2))
    # Cover bottom half by stamping a rectangle of the background — instead,
    # we crop the cap to a dome by drawing a flat rect under it that
    # matches the layer's background. Simpler: just leave the full ellipse,
    # it reads fine.

    # Highlight on cap (lighter mix)
    pygame.draw.ellipse(surf, _mix(cap_color, (255, 255, 255), 0.5),
                        (base_x - cap_w // 3, cap_y - cap_h + 1,
                         cap_w // 3, cap_h // 2))

    # White spots on cap
    n_spots = rng.randint(3, 5)
    for _ in range(n_spots):
        sx_off = rng.randint(-cap_w // 2 + 4, cap_w // 2 - 4)
        sy_off = rng.randint(-cap_h, -2)
        spot_r = max(1, int(2 * scale))
        pygame.draw.circle(surf, (255, 250, 245),
                           (base_x + sx_off, cap_y + sy_off), spot_r)

    # Gill hint under cap
    pygame.draw.line(surf, _shade(cap_color, -50),
                     (base_x - cap_w // 3, cap_y + 1),
                     (base_x + cap_w // 3, cap_y + 1), 1)


def draw_mountains_v5(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far_color = far_color or (50, 60, 110)
    near_color = near_color or (30, 40, 80)

    # ── BACK: dark forest silhouette ──
    pts = [(0, ground_y)]
    for x in range(0, w + 1, 3):
        sx = x + scroll * 0.06
        h = int(105 + math.sin(sx * 0.012) * 24 + math.sin(sx * 0.029 + 0.7) * 14)
        pts.append((x, ground_y - h))
    pts.append((w, ground_y))
    pygame.draw.polygon(surf, _V5_FOREST_BACK, pts)

    # Tree silhouettes (thin verticals)
    rng = random.Random(int(scroll) // 4 + 9)
    for _ in range(20):
        tx = rng.randrange(0, w)
        th = rng.randint(35, 75)
        pygame.draw.line(surf, _shade(_V5_FOREST_BACK, -10),
                         (tx, ground_y), (tx, ground_y - th), 2)

    # ── MID: medium red-cap mushrooms ──
    mid_step = 44
    mid_phase = scroll * 0.15
    first = int(mid_phase // mid_step) - 1
    last = int((mid_phase + w) // mid_step) + 2
    # mid forest band
    pts = [(0, ground_y)]
    for x in range(0, w + 1, 3):
        sx = x + scroll * 0.15
        h = int(70 + math.sin(sx * 0.014) * 18 + math.sin(sx * 0.032 + 1.2) * 10)
        pts.append((x, ground_y - h))
    pts.append((w, ground_y))
    pygame.draw.polygon(surf, _V5_FOREST_MID, pts)

    for k in range(first, last + 1):
        rng = random.Random((k * 1442695 + 7) & 0xFFFFFFFF)
        wx = k * mid_step + rng.uniform(-8, 8)
        sx = int(wx - mid_phase)
        if -20 < sx < w + 20:
            scale = rng.uniform(0.55, 0.8)
            col = _V5_CAPS[k % len(_V5_CAPS)]
            _v5_mushroom(surf, sx, ground_y - 35, scale, col, k * 99)

    # ── NEAR: forest floor + giant hero mushrooms ──
    floor_pts = [(0, ground_y)]
    floor_heights = []
    for x in range(0, w + 1, 3):
        sx = x + scroll * 0.28
        h = int(30 + math.sin(sx * 0.020) * 10 + math.sin(sx * 0.045) * 5)
        floor_pts.append((x, ground_y - h))
        floor_heights.append((x, ground_y - h))
    floor_pts.append((w, ground_y))
    pygame.draw.polygon(surf, _V5_FLOOR, floor_pts)

    near_step = 50
    near_phase = scroll * 0.28
    first = int(near_phase // near_step) - 1
    last = int((near_phase + w) // near_step) + 2
    for k in range(first, last + 1):
        rng = random.Random((k * 2654435761 + 17) & 0xFFFFFFFF)
        wx = k * near_step + rng.uniform(-10, 10)
        sx = int(wx - near_phase)
        if -30 < sx < w + 30:
            idx = min(len(floor_heights) - 1, max(0, sx // 3))
            base_y = floor_heights[idx][1] + 2
            scale = rng.uniform(0.9, 1.4)
            col = _V5_CAPS[(k * 3) % len(_V5_CAPS)]
            _v5_mushroom(surf, sx, base_y, scale, col, k * 211)

    # ── Glowing fireflies ──
    fire_layer = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    rng = random.Random(int(scroll) // 6)
    for _ in range(28):
        fx = rng.randrange(0, w)
        fy = rng.randrange(ground_y - 200, ground_y - 30)
        pygame.draw.circle(fire_layer, (255, 240, 120, 80), (fx, fy), 4)
        pygame.draw.circle(fire_layer, (255, 250, 200, 220), (fx, fy), 1)
    surf.blit(fire_layer, (0, 0))

    _ambient_overlay(surf, ground_y, w, near_color)


# ── dispatcher ─────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_mountains_v1,
    2: draw_mountains_v2,
    3: draw_mountains_v3,
    4: draw_mountains_v4,
    5: draw_mountains_v5,
}

VARIANT_NAMES = {
    1: "Crystal Geode Spires",
    2: "Sakura Blossom Hills",
    3: "Candy Land",
    4: "Volcanic Range",
    5: "Mushroom Fairy Forest",
}
