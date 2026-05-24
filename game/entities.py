"""
Game entities: Bird, Pipe, Coin, Mushroom, Particle, FloatText.
All drawing is smooth (gradients, alpha, glows) — no pixel art.

Pipes are sandstone pillars topped with living vegetation, re-tinted by the
active biome palette. Coins are slow-rotating metallic gold discs with
embossed detail.
"""
import math
import random
import pygame

from game.config import (
    W, H, GRAVITY, FLAP_V, MAX_FALL,
    BIRD_X, BIRD_R, PIPE_W, COIN_R, POWERUP_R, GROUND_Y,
)
from game.draw import (
    blit_glow,
    rounded_rect, lerp_color,
    COIN_GOLD, COIN_DARK,
    MUSH_CAP, MUSH_CAP2, MUSH_SPOT, MUSH_STEM,
    PARTICLE_GOLD, PARTICLE_ORNG, PARTICLE_WHT, PARTICLE_CRIM,
    NEAR_BLACK, WHITE,
)
from game import parrot
from game.pillar_variants import draw_pillar_pair
from game.dollar_coin_glyphs import draw_coin_font_bold as _draw_dollar_coin
from game.surprise_box_variants import draw_cross as _draw_surprise_box

# ── SURPRISE power-up gift box (rendered at 2× then smoothscaled, cached) ───
_surprise_sprite: "pygame.Surface | None" = None

def _get_surprise_sprite() -> "pygame.Surface":
    global _surprise_sprite
    if _surprise_sprite is None:
        scratch = pygame.Surface((64, 64), pygame.SRCALPHA)
        _draw_surprise_box(scratch, 32, 32)
        target = 2 * POWERUP_R + 12   # leave the bow + drop-shadow room
        _surprise_sprite = pygame.transform.smoothscale(scratch, (target, target))
    return _surprise_sprite


# ── GROW power-up parrot (scaled in-game sprite, cached) ─────────────────────
_grow_parrot: "pygame.Surface | None" = None

def _get_grow_parrot() -> "pygame.Surface":
    global _grow_parrot
    if _grow_parrot is None:
        src = parrot.FRAMES[1]
        target_w = 26
        ratio = target_w / src.get_width()
        target_h = int(src.get_height() * ratio)
        _grow_parrot = pygame.transform.smoothscale(src, (target_w, target_h))
    return _grow_parrot


# ── GROW power-up icon (velvet witch-hat) ────────────────────────────────────
# Tall conical Liberty-Cap silhouette with a curled scalloped rim, slim
# bulbed ivory stem, cream ornaments. Body is static — built once at 5×
# supersample then smoothscaled and cached. The pulsing halo behind it is
# redrawn each frame.

_GROW_SS = 5                                 # supersample factor
_GROW_CAP_W, _GROW_CAP_H = 22, 24            # cap footprint in display px
_GROW_STEM_W, _GROW_STEM_H = 20, 22          # stem footprint in display px
_GROW_VELVET_OUTLINE = ( 60,  15,  25)
_GROW_VELVET_RIM_HI  = (220, 120, 130)
_GROW_VELVET_SHEEN   = (220, 130, 150, 130)
_GROW_SPOT_HALO      = (195, 165, 110)
_GROW_SPOT_HI        = (255, 250, 220)
_GROW_STEM_OUTLINE   = (150, 120,  90)
_GROW_STEM_HI        = (255, 250, 230)
_GROW_HALO_RGB       = (180,  90, 110)
_GROW_HALO_RADIUS    = 46                    # round-8 V3 pick

# Spot positions as fractions of (CAP_W, CAP_H) — same canonical layout
# the picker rounds used for the witch-hat family.
_GROW_ORNAMENT_SLOTS = (
    (0.50, 0.18),
    (0.62, 0.42),
    (0.40, 0.62),
    (0.70, 0.72),
)

# Cone polygon vertex helpers (computed at SS resolution).
def _grow_cone_outline_pts():
    SS = _GROW_SS
    W, H = _GROW_CAP_W, _GROW_CAP_H
    return [
        (W // 2 * SS, 0),
        (int(W * 0.86 * SS), int(H * 0.78 * SS)),
        (int(W * 0.95 * SS), int(H * 0.92 * SS)),
        (int(W * 0.05 * SS), int(H * 0.92 * SS)),
        (int(W * 0.14 * SS), int(H * 0.78 * SS)),
    ]

def _grow_cone_body_pts():
    SS = _GROW_SS
    W, H = _GROW_CAP_W, _GROW_CAP_H
    return [
        (W // 2 * SS, 1 * SS),
        (int(W * 0.82 * SS), int(H * 0.78 * SS)),
        (int(W * 0.91 * SS), int(H * 0.90 * SS)),
        (int(W * 0.09 * SS), int(H * 0.90 * SS)),
        (int(W * 0.18 * SS), int(H * 0.78 * SS)),
    ]

def _grow_cone_hi_pts():
    SS = _GROW_SS
    W, H = _GROW_CAP_W, _GROW_CAP_H
    return [
        (W // 2 * SS - 1 * SS,           1 * SS),
        (int(W * 0.32 * SS),             int(H * 0.55 * SS)),
        (int(W * 0.22 * SS),             int(H * 0.85 * SS)),
        (int(W * 0.34 * SS),             int(H * 0.85 * SS)),
        (int(W * 0.42 * SS),             int(H * 0.55 * SS)),
    ]


_grow_body_sprite: "pygame.Surface | None" = None
_grow_body_offset: "tuple[int, int] | None" = None

def _get_grow_body_sprite() -> "tuple[pygame.Surface, int, int]":
    """Build the static witch-hat body sprite (cap + stem + sheen + spots)
    once, return it plus the (dx, dy) offset from the powerup centre to
    the sprite's top-left corner."""
    global _grow_body_sprite, _grow_body_offset
    if _grow_body_sprite is not None and _grow_body_offset is not None:
        return _grow_body_sprite, _grow_body_offset[0], _grow_body_offset[1]

    SS = _GROW_SS
    CAP_W, CAP_H = _GROW_CAP_W, _GROW_CAP_H
    STEM_W, STEM_H = _GROW_STEM_W, _GROW_STEM_H

    # Sprite footprint: cap (22 wide × 24 tall) sits above stem
    # (20 wide × 22 tall). Stem extends below the cap base by a few px.
    # Origin (0,0) of the sprite corresponds to the top-left of the cap.
    sprite_w = max(CAP_W, STEM_W) + 2
    sprite_h = CAP_H + STEM_H + 4
    big = pygame.Surface((sprite_w * SS, sprite_h * SS), pygame.SRCALPHA)

    # Cap origin at (1, 0) in display coords → (1*SS, 0) in big coords.
    cap_ox = 1 * SS
    cap_oy = 0

    # Stem origin at (2, CAP_H + 2) in display coords (centred under cap).
    stem_ox = 2 * SS
    stem_oy = (CAP_H + 2) * SS

    # ── Stem ──────────────────────────────────────────────────────────
    stem_pts = [
        (8 * SS,  0 * SS),
        (12 * SS, 0 * SS),
        (13 * SS, 12 * SS),
        (15 * SS, 18 * SS),
        (10 * SS, 21 * SS),
        ( 5 * SS, 18 * SS),
        ( 7 * SS, 12 * SS),
    ]
    stem_pts_offset = [(p[0] + stem_ox, p[1] + stem_oy) for p in stem_pts]
    pygame.draw.polygon(big, MUSH_STEM,           stem_pts_offset)
    pygame.draw.polygon(big, _GROW_STEM_OUTLINE,  stem_pts_offset, width=SS)
    pygame.draw.line(
        big, _GROW_STEM_HI,
        (9 * SS + stem_ox, 2 * SS + stem_oy),
        (9 * SS + stem_ox, 18 * SS + stem_oy), SS,
    )

    # ── Cap (cone) ────────────────────────────────────────────────────
    def _shift(pts, ox, oy):
        return [(p[0] + ox, p[1] + oy) for p in pts]

    pygame.draw.polygon(big, _GROW_VELVET_OUTLINE,
                        _shift(_grow_cone_outline_pts(), cap_ox, cap_oy))
    pygame.draw.polygon(big, MUSH_CAP,
                        _shift(_grow_cone_body_pts(),    cap_ox, cap_oy))
    pygame.draw.polygon(big, MUSH_CAP2,
                        _shift(_grow_cone_hi_pts(),      cap_ox, cap_oy))

    # Curled scalloped rim
    rim_w = int(CAP_W * 0.86 * SS)
    rim_x = int(CAP_W * 0.07 * SS) + cap_ox
    rim_y = int(CAP_H * 0.93 * SS) + cap_oy
    rim_count = 5
    curl_w = rim_w // rim_count
    for i in range(rim_count):
        center = (rim_x + i * curl_w + curl_w // 2, rim_y)
        pygame.draw.circle(big, MUSH_CAP,             center, curl_w // 2)
        pygame.draw.circle(big, _GROW_VELVET_OUTLINE, center, curl_w // 2, SS)
        pygame.draw.circle(big, _GROW_VELVET_RIM_HI,
                           (center[0] - curl_w // 5, center[1] - curl_w // 5),
                           max(1, curl_w // 4))

    # Velvet inner sheen blob — alpha ellipse masked to the cone shape.
    sheen = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, _GROW_VELVET_SHEEN,
                        pygame.Rect(int(CAP_W * 0.34 * SS) + cap_ox,
                                    int(CAP_H * 0.16 * SS) + cap_oy,
                                    int(CAP_W * 0.20 * SS),
                                    int(CAP_H * 0.42 * SS)))
    cone_mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(cone_mask, (255, 255, 255, 255),
                        _shift(_grow_cone_body_pts(), cap_ox, cap_oy))
    sheen.blit(cone_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))

    # Cream-butter spots
    for fx_frac, fy_frac in _GROW_ORNAMENT_SLOTS:
        fx = int(CAP_W * fx_frac * SS) + cap_ox
        fy = int(CAP_H * fy_frac * SS) + cap_oy
        r_body = 2.0
        pygame.draw.circle(big, _GROW_SPOT_HALO, (fx, fy),
                           int((r_body + 0.4) * SS))
        pygame.draw.circle(big, MUSH_SPOT, (fx, fy), int(r_body * SS))
        pygame.draw.circle(big, _GROW_SPOT_HI,
                           (fx - SS // 2, fy - SS // 2), max(1, SS // 2))

    sprite = pygame.transform.smoothscale(big, (sprite_w, sprite_h))

    # Offset from the in-world (cx, cy) anchor to the sprite's top-left.
    # The original mushroom anchor placed the cap at (cx - 15, cy - 12)
    # and the stem at (cx - 7, cy). The new icon centres the cap
    # horizontally on cx and lets the stem hang from there. We want the
    # icon's centre of mass roughly aligned with (cx, cy) so the existing
    # POWERUP_R collision feels right.
    dx = -sprite_w // 2 + 1                              # centre horizontally
    dy = -CAP_H + 2                                       # cap top above cy
    _grow_body_sprite = sprite
    _grow_body_offset = (dx, dy)
    return sprite, dx, dy


def _draw_grow_halo(surf, cx, cy, pulse,
                    color_rgb=_GROW_HALO_RGB,
                    radius=_GROW_HALO_RADIUS,
                    falloff=2.2,
                    peak_y_off=-2):
    """Smooth radial halo (~60 concentric circles, quadratic falloff).
    `pulse` drives the brightness pulse; same curve as the picker rounds."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.2)
    max_alpha = int(140 + 25 * pulse_t)
    steps = max(60, radius * 2)
    w = radius * 2 + 4
    halo = pygame.Surface((w, w), pygame.SRCALPHA)
    hcx = hcy = w // 2
    for i in range(steps):
        r = max(0, radius - (i * radius) // steps)
        if r <= 0:
            break
        t = i / max(1, steps - 1)
        a = int(max_alpha * (t ** falloff))
        if a > 0:
            pygame.draw.circle(halo, (*color_rgb, a), (hcx, hcy), r)
    surf.blit(halo, (cx - hcx, cy - hcy + peak_y_off))


# ── KFC logo sprite (lazy-loaded once at first draw) ─────────────────────────
_kfc_sprite: "pygame.Surface | None" = None

def _get_kfc_sprite() -> "pygame.Surface":
    global _kfc_sprite
    if _kfc_sprite is None:
        import os
        r         = POWERUP_R + 2
        logo_size = int(r * 2.4)
        path      = os.path.join(os.path.dirname(__file__), "assets", "kfc_logo.jpg")
        raw = pygame.image.load(path)
        # Crop to square (center crop on the wider axis)
        rw, rh = raw.get_size()
        side = min(rw, rh)
        crop = pygame.Surface((side, side))
        crop.blit(raw, (-(rw - side) // 2, -(rh - side) // 2))
        # Scale 38% larger so the white outer ring is pushed outside the circle mask
        zoomed_size = int(logo_size * 1.38)
        scaled = pygame.transform.smoothscale(crop, (zoomed_size, zoomed_size))
        # Convert to SRCALPHA so the circle mask can punch out corners
        logo = pygame.Surface((logo_size, logo_size), pygame.SRCALPHA)
        offset = (logo_size - zoomed_size) // 2
        logo.blit(scaled, (offset, offset))
        mask = pygame.Surface((logo_size, logo_size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255),
                           (logo_size // 2, logo_size // 2), logo_size // 2)
        logo.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        _kfc_sprite = logo
    return _kfc_sprite


# ── GHOST power-up sprite (procedural, cached on first draw) ────────────────
# Holographic foil body (diagonal pearl-pink → cyan → mint → ivory) inside a
# 0.5-px black hairline outline + crisp eyes + soft sheen.
_ghost_sprite: "pygame.Surface | None" = None
_GHOST_HEAD_OFFSET_X = 16   # head-circle centre x in the sprite
_GHOST_HEAD_OFFSET_Y = 14   # head-circle centre y in the sprite


def _get_ghost_sprite() -> "pygame.Surface":
    global _ghost_sprite
    if _ghost_sprite is not None:
        return _ghost_sprite

    SS = 16                                   # high-res super-sample for
                                              # genuinely smooth perimeter
    PAD = 2
    GW, GH = (28 + PAD * 2), (36 + PAD * 2)   # 32 × 40 final-px
    sw, sh = GW * SS, GH * SS
    big = pygame.Surface((sw, sh), pygame.SRCALPHA)

    # Geometry in supersampled units
    gcx = (14 + PAD) * SS
    gcy = (12 + PAD) * SS
    hr  = 12 * SS
    body_y2 = (26 + PAD) * SS

    # Build the full silhouette as a SINGLE perimeter polygon (head
    # semicircle → right side → angular scallop → left side). This lets
    # us stroke the outline with a fast line+circle pass instead of the
    # offset-stack (which scales O(SS²) and would be ~1 G pixel-ops at
    # SS=16). Same angular V-bumps as before, just rendered cleanly.
    perimeter = []
    n_arc = 64                                # head arc resolution
    for i in range(n_arc + 1):
        theta = math.pi - i * math.pi / n_arc
        x = gcx + hr * math.cos(theta)
        y = gcy - hr * math.sin(theta)
        perimeter.append((int(x), int(y)))
    # Right side down to body bottom
    perimeter.append((gcx + hr, body_y2))
    # Angular scallop — symmetric, uniform-width waves, traced
    # right-to-left through 7 control points.
    bump_y   = (GH - 4) * SS
    indent_y = body_y2 + 4 * SS
    x_left   = (1 + PAD) * SS
    x_right  = (28 - 2 + PAD) * SS
    span_x   = x_right - x_left
    scallop_lr = [
        (x_left + i * span_x // 6,
         body_y2 if i in (0, 6) else (bump_y if i % 2 == 1 else indent_y))
        for i in range(7)
    ]
    perimeter.extend(reversed(scallop_lr))
    # Left side back up to head's leftmost point
    perimeter.append((gcx - hr, gcy))

    OUTLINE_COLOR = (0, 0, 0)
    # 0.5-px hairline. SS=16 means t_big=8 super-pixels = exactly 0.5 final
    # pixels of visible outline (line stroke runs both sides of the
    # perimeter; the inner half is covered by the gradient blit below, so
    # only the outer half is visible).
    THICKNESS_PX  = 0.5
    t_big = int(THICKNESS_PX * SS)

    # 1) Outline ring — stroke each perimeter edge as a thick line, plus a
    #    circle at every vertex so corners join cleanly without gaps. This
    #    is O(N) in perimeter length, not O(SS²) like the offset-stack.
    for i in range(len(perimeter)):
        p1 = perimeter[i]
        p2 = perimeter[(i + 1) % len(perimeter)]
        pygame.draw.line(big, OUTLINE_COLOR, p1, p2, t_big * 2)
    for p in perimeter:
        pygame.draw.circle(big, OUTLINE_COLOR, p, t_big)

    # 2) Silhouette mask — single filled polygon traced from the same
    #    perimeter, so it lines up with the outline ring above to the pixel.
    mask = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), perimeter)

    # 3) Holographic foil body — diagonal multi-stop gradient. Build a
    #    1-D gradient strip of length sw+sh once, then per row blit a
    #    sw-wide slice of it starting at offset y. Avoids per-pixel
    #    set_at over the full sw×sh canvas.
    stops = [
        (0.00, (240, 215, 255)),  # pale lavender
        (0.30, (255, 220, 240)),  # pearl pink
        (0.55, (220, 240, 255)),  # cyan
        (0.80, (215, 255, 235)),  # mint
        (1.00, (245, 245, 220)),  # warm ivory
    ]
    diag_len = sw + sh
    strip = pygame.Surface((diag_len, 1), pygame.SRCALPHA)
    for xx in range(diag_len):
        t = xx / max(1, diag_len - 1)
        if t <= stops[0][0]:
            col = stops[0][1]
        elif t >= stops[-1][0]:
            col = stops[-1][1]
        else:
            col = stops[-1][1]
            for i in range(len(stops) - 1):
                a_pos, a_col = stops[i]
                b_pos, b_col = stops[i + 1]
                if a_pos <= t <= b_pos:
                    u = (t - a_pos) / max(1e-6, b_pos - a_pos)
                    col = (
                        int(a_col[0] + (b_col[0] - a_col[0]) * u),
                        int(a_col[1] + (b_col[1] - a_col[1]) * u),
                        int(a_col[2] + (b_col[2] - a_col[2]) * u),
                    )
                    break
        strip.set_at((xx, 0), col + (245,))
    grad = pygame.Surface((sw, sh), pygame.SRCALPHA)
    for yy in range(sh):
        slice_rect = pygame.Rect(yy, 0, sw, 1)
        grad.blit(strip, (0, yy), area=slice_rect)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(grad, (0, 0))

    # 4) Soft white sheen on the upper portion for the foil shimmer.
    sheen = pygame.Surface((sw, sh), pygame.SRCALPHA)
    sy0 = gcy - hr
    sy1 = gcy + int(hr * 0.5)
    for yy in range(sy0, sy1):
        t = (yy - sy0) / max(1, sy1 - sy0)
        a = int(150 * (1.0 - t) ** 1.5)
        if a > 0:
            pygame.draw.line(sheen, (255, 255, 255, a), (0, yy), (sw, yy))
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))

    # 5) Eyes
    EYE_W    = (252, 254, 255, 255)
    EYE_IRIS = (50, 110, 220, 255)
    EYE_PUP  = (12,  18,  60, 255)
    for ex_off in (-5, 5):
        ex = gcx + ex_off * SS
        ey = gcy - 1 * SS
        pygame.draw.circle(big, EYE_W,    (ex,         ey        ), int(3.5 * SS))
        pygame.draw.circle(big, EYE_IRIS, (ex + SS,    ey + SS    ), int(2.5 * SS))
        pygame.draw.circle(big, EYE_PUP,  (ex + SS,    ey + SS    ), max(1, SS))
        pygame.draw.circle(big, (255, 255, 255, 220),
                           (ex - SS, ey - 2 * SS), max(1, SS // 2))

    _ghost_sprite = pygame.transform.smoothscale(big, (GW, GH))
    return _ghost_sprite


# Default pillar palette (fallback when no biome provided).
_DEFAULT_PILLAR = {
    'stone_light':     (225, 195, 155),
    'stone_mid':       (175, 140, 105),
    'stone_dark':      (95, 70, 55),
    'stone_accent':    (255, 220, 170),
    'foliage_top':     (140, 220, 110),
    'foliage_mid':     (70, 170, 75),
    'foliage_dark':    (30, 100, 50),
    'foliage_accent':  (255, 240, 120),
}


# ── Bird ─────────────────────────────────────────────────────────────────────

# Key points (sprite-rel x, y) tracing Pip's rear upper surface,
# tail tip → base of neck — the "snow line" that the accumulation
# hugs. He faces +x (right), so the tailwind piles snow on
# everything facing -x. Centre = (0,0); sprite is 68×64, body
# bbox x∈[-31,33] y∈[-26,22]. Used only to weight where flakes
# settle — there is NO fixed silhouette; the drift shape emerges
# from the accumulated flakes.
_SNOW_LINE_KEY = (
    (-31.0, -2.0),   # tail tip (upper edge)
    (-25.0, -4.0),   # tail upper
    (-19.0, -6.0),   # rump
    (-12.0, -8.0),   # back
    (-5.0,  -8.5),   # back crest
    (2.0,   -8.0),   # back/shoulder
    (8.0,   -9.0),   # shoulder
    (11.0, -15.0),   # nape (climbs)
    (16.5, -19.5),   # crown approach
    (19.0, -21.0),   # crown — head reaches right
)

_SNOW_DISC_CACHE: dict = {}
_SNOW_POOL = None


def _snow_disc(radius, color, alpha):
    """Cached soft round flake (opaque centre → soft rim). The
    drift is built by overlapping many of these, so the snow mass
    is emergent + organic rather than a drawn shape."""
    radius = max(1, int(round(radius)))
    ab = max(16, min(255, (int(alpha) // 16) * 16))
    key = (radius, ab, color)
    cached = _SNOW_DISC_CACHE.get(key)
    if cached is not None:
        return cached
    d = radius * 2 + 2
    surf = pygame.Surface((d, d), pygame.SRCALPHA)
    c = radius + 1
    steps = max(3, radius)
    for i in range(steps, 0, -1):
        rr = max(1, int(radius * i / steps))
        frac = i / steps
        a = int(ab * (1.0 - frac) ** 1.25)
        pygame.draw.circle(surf, (*color, a), (c, c), rr)
    _SNOW_DISC_CACHE[key] = surf
    return surf


def _build_snow_pool():
    """Pre-compute a fixed pool of candidate snowflake slots over
    Pip's rear, each with a position + a 'snowiness' weight (how
    readily snow settles there — high on the windward back/rump,
    tapering to the front, tail tip + into the body). Sorted
    snowiest-first so the renderer can activate the top-K as the
    load grows: a few flakes at the snowiest spots first, then
    spreading + overlapping into a full drift. Built once."""
    key = _SNOW_LINE_KEY

    def line_y(x):
        if x <= key[0][0]:
            return key[0][1]
        if x >= key[-1][0]:
            return key[-1][1]
        for j in range(len(key) - 1):
            x0, y0 = key[j]
            x1, y1 = key[j + 1]
            if x0 <= x <= x1:
                f = (x - x0) / (x1 - x0)
                return y0 + (y1 - y0) * f
        return key[-1][1]

    A1, A2 = 0.7548776662, 0.5698402910    # R2 low-discrepancy seq
    pool = []

    # ── ONE continuous drift (tail → back → nape → crown) ────────
    # A single band along the whole snow line, so the snow reads as
    # one connected layer (not back/crown patches). Volume is shaped
    # by region: a fuller bridge over the nape, the head reaching
    # right onto the crown ("head-forward" pick). The face guard
    # keeps the head snow off the sunglasses.
    def prof(x):
        if x < -20.0:                      # tail
            return 0.85
        if x <= 4.0:                       # body
            return 1.0
        if x <= 12.0:                      # bridge / nape — extra volume
            return 1.25
        return 1.2                         # head crown (prominent, righter)

    def along(x):
        taper = max(0.5, 1.0 - (-29.0 - x) / 4.0) if x < -29.0 else 1.0
        return taper * prof(x)

    x_lo, x_hi = -29.5, 20.5
    y_lo, y_hi = -24.0, 6.0
    M = 1050
    for i in range(M):
        u = (0.5 + A1 * (i + 1)) % 1.0
        v = (0.5 + A2 * (i + 1)) % 1.0
        x = x_lo + u * (x_hi - x_lo)
        y = y_lo + v * (y_hi - y_lo)
        if x > 13.0 and y > -17.0:         # never spill onto the face/lenses
            continue
        dy = y - line_y(x)                 # distance below the snow line
        if dy < -1.5:                      # barely any above the line (no float)
            continue
        if dy < 0.0:
            wy = max(0.0, 1.0 + dy / 1.5) * 0.6
        elif dy <= 6.0:
            wy = 1.0
        else:
            wy = max(0.0, 1.0 - (dy - 6.0) / 6.0)
        wind = 1.0 + max(0.0, -x) / 55.0   # slight windward (rear) bias
        noise = 0.78 + 0.22 * ((math.sin(i * 12.9898) * 43758.5453) % 1.0)
        w = along(x) * wy * wind * noise * 1.4
        if w <= 0.001:
            continue
        pool.append((x, y, dy, w))

    # Activation order for the buildup (the renderer lights the
    # first-K as load grows). Sort PATCHY: primarily by distance
    # from the perimeter (|dy|) so snow coats the top edge first,
    # minus weight so windward high-spots seed early and merge —
    # an organic perimeter-first build. (The full set, hence the
    # peak frame, is unchanged — only the order differs.)
    pool.sort(key=lambda p: abs(p[2]) * 1.3 - p[3] * 3.0)
    return pool


def _draw_snow_cap(surf, cx, cy, load, scale=1.0, tilt=0.0):
    """Snow accumulating over Pip's whole windward rear (tail, rump,
    back) during the squall, built as an emergent FLAKE FIELD: as
    `load` (0..1) rises, more flakes settle — starting at the
    snowiest spots — and grow, overlapping into a solid drift. No
    predefined silhouette, so it evolves naturally from a sparse
    dusting to a full drift and melts back the same way. Flakes are
    a fixed deterministic pool, so the snow never shimmers. Cool
    underside + bright top tiers give the drift volume. +x is
    forward (right), centre at (0,0)."""
    global _SNOW_POOL
    load = max(0.0, min(1.0, load))
    if load <= 0.02:
        return
    if _SNOW_POOL is None:
        _SNOW_POOL = _build_snow_pool()
    pool = _SNOW_POOL
    sc = scale
    # Rotate the flake field the SAME visual direction as the
    # sprite. parrot.get_parrot uses pygame.transform.rotozoom,
    # which rotates COUNTER-clockwise for +tilt; the standard
    # matrix in screen space (y-down) goes clockwise, so we negate
    # the angle to match — otherwise the drift counter-rotates and
    # slides off Pip's back during flaps/dives.
    ang = math.radians(-tilt)
    cos_t = math.cos(ang)
    sin_t = math.sin(ang)

    def tf(x, y):
        rx = x * cos_t - y * sin_t
        ry = x * sin_t + y * cos_t
        return (cx + rx * sc, cy + ry * sc)

    # How many flakes are active + how big they are — both grow with
    # load, so a few flecks build organically into a packed drift.
    k = int(len(pool) * min(1.0, load * 1.12))
    if k < 1:
        k = 1
    active = pool[:k]
    base_r = (1.3 + load * 3.7) * sc       # dusting fleck → fat drift blob
    fade = min(1.0, (load - 0.02) / 0.05)  # gentle fade-in at the very start

    items = []
    rmax = 1
    for x, y, dy, w in active:
        px, py = tf(x, y)
        r = max(1, int(round(base_r * (0.72 + 0.5 * w))))
        items.append((px, py, r, dy))
        if r > rmax:
            rmax = r
    xs = [it[0] for it in items]
    ys = [it[1] for it in items]
    ox = int(min(xs) - rmax - 2)
    oy = int(min(ys) - rmax - 2)
    w_px = int(max(xs) - min(xs) + 2 * rmax + 4)
    h_px = int(max(ys) - min(ys) + 2 * rmax + 4)
    if w_px < 2 or h_px < 2:
        return
    scratch = pygame.Surface((w_px, h_px), pygame.SRCALPHA)
    a_white = int(225 * fade)
    a_cool = int(195 * fade)
    for px, py, r, dy in items:
        # Tier the flake colour by how low it sits in the pile:
        # bright white on top, off-white body, cool shadowed
        # underside — gives the emergent drift top-lit volume.
        if dy < 0.5:
            col, a = (255, 255, 255), a_white
        elif dy <= 4.0:
            col, a = (238, 245, 253), a_white
        else:
            col, a = (196, 212, 232), a_cool
        disc = _snow_disc(r, col, a)
        scratch.blit(disc, (int(px - ox - disc.get_width() / 2),
                            int(py - oy - disc.get_height() / 2)))
    surf.blit(scratch, (ox, oy))


class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = H * 0.42
        self.vy = 0.0
        self.alive = True
        self.frame_t = 0.0
        self.flap_boost = 0.0
        self.kfc_active = False
        self.ghost_active = False
        self.grow_active = False
        self.triple_active = False
        self.ghost_pulse = 0.0    # advances while ghost_active for fade effect
        # Shrink: collision-relevant flag flips at activation; the
        # visible sprite scale eases between 1.0 and SHRINK_SCALE over
        # SHRINK_TRANSITION seconds so the morph reads on screen.
        self.shrink_active = False
        self.shrink_scale = 1.0
        # Cart / rail state. cart_active gates pipe-spawn suppression
        # and the rail-pillar bookkeeping; cart_locked gates the
        # RAIL_SCROLL_MULT scroll boost and means Pip is physically on
        # the cart. Both clear at _end_rail_ride.
        self.cart_active = False
        self.cart_locked = False
        # Local slope of the rail segment Pip is currently riding,
        # written by World._snap_cart_to_rail. Drives the cart sprite
        # rotation in scenes._draw_cart_on_bird so the wagon tilts
        # with the polyline curvature.
        self.cart_tilt_deg = 0.0

        # Weather event state (visual-only):
        #   wind_lean       — rightward x-offset under the predawn tailwind
        #   snow_load       — 0..1 snow drift accumulated on Pip's back
        #   skeleton_flash_t — X-Ray Sparks timer set when lightning strikes
        self.wind_lean = 0.0
        self.snow_load = 0.0
        self.skeleton_flash_t = 0.0
        # Rain shiver (visual-only) + flap dampen (real, the "wind pushes
        # me down" cue) under heavy rain. Written by World._apply_weather_effects.
        self.shiver_x = 0.0
        self.shiver_y = 0.0
        self.flap_dampen = 0.0

    @property
    def tilt_deg(self):
        # Clamp the downward dive so a fast-falling bird doesn't read as
        # already crashing (REVIEW.md feedback).
        t = max(-0.5, min(0.75, self.vy / 500.0))
        return -t * 55.0

    def flap(self, gravity_sign=1):
        if self.alive:
            # Heavy rain dampens lift slightly — the "wind pushing me
            # down" cue (flap_dampen is 0 outside heavy weather).
            self.vy = FLAP_V * gravity_sign * (1.0 - self.flap_dampen)
            self.flap_boost = 0.45

    def update(self, dt, gravity_sign=1):
        new_vy = self.vy + GRAVITY * gravity_sign * dt
        if gravity_sign >= 0:
            self.vy = min(new_vy, MAX_FALL)
        else:
            self.vy = max(new_vy, -MAX_FALL)
        self.y += self.vy * dt

        base_hz = 9.0 + self.flap_boost * 20.0
        if self.vy < -100:
            base_hz += 3.0
        elif self.vy > 200:
            base_hz = max(3.0, base_hz - 4.0)
        self.frame_t = (self.frame_t + dt * base_hz)
        self.flap_boost = max(0.0, self.flap_boost - dt * 1.8)
        if self.ghost_active:
            self.ghost_pulse += dt * 2.4
        # X-Ray Sparks flash decays over its 3.5 s window (set by the
        # storm-jolt lightning strike).
        self.skeleton_flash_t = max(0.0, self.skeleton_flash_t - dt)
        # Ease shrink_scale toward its target (SHRINK_SCALE while active,
        # 1.0 otherwise) over SHRINK_TRANSITION seconds. Collisions snap on
        # frame 1 via World.bird_radius — only the visible sprite eases.
        from game.config import SHRINK_SCALE, SHRINK_TRANSITION
        target = SHRINK_SCALE if self.shrink_active else 1.0
        if self.shrink_scale != target:
            step = (1.0 - SHRINK_SCALE) * dt / SHRINK_TRANSITION
            if self.shrink_scale > target:
                self.shrink_scale = max(target, self.shrink_scale - step)
            else:
                self.shrink_scale = min(target, self.shrink_scale + step)

    def draw(self, surf, shake_x=0, shake_y=0, flipped=False):
        # Weather visual offsets (collision unaffected): tailwind pushes
        # Pip rightward; heavy-rain shiver jitters him.
        shake_x += self.wind_lean + self.shiver_x
        shake_y += self.shiver_y
        frame_idx = int(self.frame_t) % len(parrot.FRAMES)
        # When flipped (reverse-gravity buff), negate the tilt so a rising
        # bird's head still leads in the direction of motion after the
        # vertical mirror is applied below.
        tilt = -self.tilt_deg if flipped else self.tilt_deg
        # X-Ray Sparks (storm-jolt strike): a 3.5 s flash where Pip strobes
        # between his skeleton and his normal sprite — first 0.5 s a solid
        # skeleton hold, then 3.0 s of strobe at 0.30 s per segment.
        skeleton_visible = False
        if self.skeleton_flash_t > 0.0:
            if self.skeleton_flash_t > 3.0:
                skeleton_visible = True
            else:
                bucket = int((3.0 - self.skeleton_flash_t) / 0.30)
                skeleton_visible = (bucket % 2 == 0)
        # Combo-aware sprite cascade. The four reachable stacks each have
        # a dedicated themed sprite so no powerup is silently lost; check
        # combos before single-mode flags so e.g. kfc+triple picks the
        # crispy-hat sprite instead of falling through to plain kfc.
        # X-Ray Sparks overrides every sprite during the flash.
        if skeleton_visible:
            img = parrot.get_skeleton_parrot(frame_idx, tilt)
        elif self.kfc_active and self.ghost_active and self.triple_active:
            img = parrot.get_kfc_ghost_hat_parrot(frame_idx, tilt)
        elif self.kfc_active and self.ghost_active:
            img = parrot.get_kfc_ghost_parrot(frame_idx, tilt)
        elif self.kfc_active and self.triple_active:
            img = parrot.get_kfc_hat_parrot(frame_idx, tilt)
        elif self.ghost_active and self.triple_active:
            img = parrot.get_ghost_hat_parrot(frame_idx, tilt)
        elif self.kfc_active:
            img = parrot.get_fried_parrot(frame_idx, tilt)
        elif self.ghost_active:
            img = parrot.get_ghost_parrot(frame_idx, tilt)
        elif self.triple_active:
            img = parrot.get_hat_parrot(frame_idx, tilt)
        elif self.grow_active:
            # Hi-res grow-mode bird: pre-built at full grow display size by
            # `parrot._build_grow_frame` (round-9 v3 = 3× supersample → 1.5×
            # downscale). Skips the smoothscale-up that produced the prior
            # blur. Combo modes (kfc / ghost / triple + grow) still use
            # the legacy upscale below — they pre-empt this branch.
            img = parrot.get_grow_parrot(frame_idx, tilt)
        else:
            img = parrot.get_parrot(frame_idx, tilt)
        if self.grow_active and (self.kfc_active or self.ghost_active
                                  or self.triple_active):
            # Combo + grow: smoothscale-up the variant sprite. No hi-res
            # combo frames yet; this preserves correctness at the cost of
            # the same upscale blur the base bird used to have.
            from game.config import GROW_SCALE
            w, h = img.get_size()
            img = pygame.transform.smoothscale(
                img, (int(w * GROW_SCALE), int(h * GROW_SCALE)))
        # Shrink eases the sprite down on top of whichever combo sprite
        # was chosen. Skipped while grow is animating up (the two buffs
        # don't stack — activator clears the other timer), but still
        # works mid-easing on activation/expiry.
        if self.shrink_scale != 1.0 and not self.grow_active:
            sw, sh = img.get_size()
            img = pygame.transform.smoothscale(
                img,
                (max(1, int(sw * self.shrink_scale)),
                 max(1, int(sh * self.shrink_scale))),
            )
        if flipped:
            img = pygame.transform.flip(img, False, True)
        if self.ghost_active and not skeleton_visible:
            # Faded breathing: alpha oscillates ~90..170 over a slow sine,
            # so the ghost reads as clearly translucent and ethereal.
            # Suppressed during the X-Ray flash so the bones read solid.
            img = img.copy()
            pulse = 0.5 + 0.5 * math.sin(self.ghost_pulse)
            img.set_alpha(int(90 + pulse * 80))
        cx_int = int(self.x + shake_x)
        cy_int = int(self.y + shake_y)
        # X-Ray Sparks rim glow — a tight silhouette-edge trim
        # (outer purple → cyan → white core) traced from the sprite's
        # mask outline and drawn BEFORE the sprite so only the outer
        # half shows; pulse-modulated at ~5 Hz.
        if self.skeleton_flash_t > 0.0:
            rim_pulse = 0.5 + 0.5 * math.sin(self.frame_t * 30.0)
            try:
                sil_mask = pygame.mask.from_surface(img, threshold=20)
                outline_pts = sil_mask.outline(every=1)
                if len(outline_pts) >= 2:
                    rect_pre = img.get_rect(center=(cx_int, cy_int))
                    glow = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                    for width, col in (
                        (5, (180, 100, 255)),
                        (3, (140, 220, 255)),
                        (1, (255, 255, 255)),
                    ):
                        pygame.draw.lines(glow, col, True, outline_pts, width)
                    glow.set_alpha(max(0, min(255, int(220 * (0.6 + 0.4 * rim_pulse)))))
                    surf.blit(glow, rect_pre.topleft)
            except (pygame.error, AttributeError):
                pass
        r = img.get_rect(center=(cx_int, cy_int))
        surf.blit(img, r.topleft)
        # Snow drift on Pip's back — the tailwind deposits snow on his
        # dorsal surface during the squall; drawn over the body sprite.
        if self.snow_load > 0.02 and not skeleton_visible:
            from game.config import GROW_SCALE as _GS
            _body_scale = (_GS if self.grow_active else 1.0) * self.shrink_scale
            _draw_snow_cap(surf, cx_int, cy_int, self.snow_load, _body_scale, tilt)
        # X-Ray Sparks arcs — jagged cyan/white mini-bolts discharging
        # outward from Pip's silhouette while the flash is active.
        if self.skeleton_flash_t > 0.0:
            inner_r = 20.0
            for _k in range(5):
                ang = random.uniform(0, math.tau)
                ox = cx_int + math.cos(ang) * inner_r
                oy = cy_int + math.sin(ang) * inner_r
                end_r = inner_r + random.uniform(10, 14)
                ex = cx_int + math.cos(ang) * end_r
                ey = cy_int + math.sin(ang) * end_r
                mid_r = (inner_r + end_r) * 0.5
                perp = ang + math.pi / 2
                jitter = random.uniform(-3.5, 3.5)
                mx = cx_int + math.cos(ang) * mid_r + math.cos(perp) * jitter
                my = cy_int + math.sin(ang) * mid_r + math.sin(perp) * jitter
                pts = ((int(ox), int(oy)), (int(mx), int(my)), (int(ex), int(ey)))
                pygame.draw.lines(surf, (140, 220, 255), False, pts, 3)
                pygame.draw.lines(surf, (255, 255, 255), False, pts, 1)
                pygame.draw.circle(surf, (255, 255, 255), (int(ex), int(ey)), 2)
                pygame.draw.circle(surf, (140, 220, 255), (int(ex), int(ey)), 3, 1)

        # Parcel — Pip's permanent companion. Tucked below his centre with
        # a tilt-aware offset so it banks with him; mode-coloured to match
        # the active palette; alpha-breathes in ghost mode; grow-scaled.
        if self.kfc_active:
            mode = "kfc"
        elif self.ghost_active:
            mode = "ghost"
        elif self.triple_active:
            mode = "triple"
        else:
            mode = "normal"
        parcel = parrot.get_parcel(mode)
        from game.config import GROW_SCALE, PARCEL_Y_OFFSET
        scale = GROW_SCALE if self.grow_active else 1.0
        if scale != 1.0:
            pw, ph = parcel.get_size()
            parcel = pygame.transform.smoothscale(
                parcel, (int(pw * scale), int(ph * scale)))
        # When reverse-gravity is active, the parcel mirrors with Pip:
        # the sprite flips vertically, the y-offset negates so the parcel
        # rides ABOVE Pip's centre, and the tilt direction inverts so the
        # parcel banks the same way as the flipped bird.
        if flipped:
            parcel = pygame.transform.flip(parcel, False, True)
        y_off = -PARCEL_Y_OFFSET * scale if flipped else PARCEL_Y_OFFSET * scale
        parcel_tilt = -self.tilt_deg if flipped else self.tilt_deg
        offset = pygame.math.Vector2(0, y_off)
        offset = offset.rotate(-parcel_tilt)
        # Rotate the parcel sprite to match tilt so the gift bow keeps
        # pointing "up" relative to Pip's local frame.
        parcel_rot = pygame.transform.rotate(parcel, parcel_tilt)
        if self.ghost_active and not skeleton_visible:
            parcel_rot = parcel_rot.copy()
            parcel_rot.set_alpha(int(90 + pulse * 80))
        pr = parcel_rot.get_rect(center=(self.x + shake_x + offset.x,
                                         self.y + shake_y + offset.y))
        surf.blit(parcel_rot, pr.topleft)


# ── Pipe (nature pillar) ─────────────────────────────────────────────────────

class Pipe:
    """Sandstone pillar column. Each instance picks one of 8 visual variants
    (original + 7 sketched picks) deterministically from its seed, so the
    vegetation and ornament arrangement is stable across frames."""

    def __init__(self, x: float, gap_y: float, gap_h: float):
        self.x = x
        self.gap_y = gap_y
        self.gap_h = gap_h
        self.scored = False
        self.is_rush = False
        # Per-pipe sticky flag: set at spawn (if KFC was active when this pipe
        # was created) or retroactively when the powerup is picked up. Once
        # True it stays True for the rest of the pipe's life and gates the
        # one-time gap_h widening at activation so a second KFC pickup
        # doesn't compound the boost. The KFC *visual* is gated separately
        # on world.kfc_timer > 0 (see Pipe.draw) so the pillar reverts to
        # stone at timer=0 alongside the fries mountain + fried Pip; only
        # the wider gap outlives the timer.
        self.is_kfc = False
        # Per-instance random seed → chooses variant + stable decoration seed
        self.seed = random.randint(0, 0xFFFFFF)
        # KFC re-skin is deterministic per pipe (seed + gap_y + gap_h all
        # stable for a Pipe's lifetime) and never animates, so we render
        # it once on first KFC frame and blit the bitmap each frame after.
        # Without this every visible KFC pillar was allocating ~8
        # SRCALPHA surfaces + running pygame.transform per frame —
        # the dominant source of KFC-mode lag.
        self._kfc_cache: "pygame.Surface | None" = None
        self._kfc_cache_dx = 0  # x-offset between blit corner and self.x

    @property
    def top_rect(self):
        return pygame.Rect(int(self.x), 0, PIPE_W, int(self.gap_y - self.gap_h / 2))

    @property
    def bot_rect(self):
        top = int(self.gap_y + self.gap_h / 2)
        return pygame.Rect(int(self.x), top, PIPE_W, GROUND_Y - top)

    def off_screen(self):
        return self.x + PIPE_W + 8 < 0

    def collides_circle(self, cx, cy, r):
        return self.top_rect.colliderect(pygame.Rect(cx - r, cy - r, r * 2, r * 2)) or \
               self.bot_rect.colliderect(pygame.Rect(cx - r, cy - r, r * 2, r * 2))

    def draw(self, surf, palette=None, kfc_visual=False):
        palette = palette or _DEFAULT_PILLAR
        if self.is_kfc and kfc_visual:
            if self._kfc_cache is None:
                self._build_kfc_cache(palette)
            surf.blit(self._kfc_cache,
                      (int(self.x) + self._kfc_cache_dx, 0))
            return
        draw_pillar_pair(surf, self.top_rect, self.bot_rect, palette, self.seed)

    def _build_kfc_cache(self, palette):
        """Render the KFC pillar pair onto a per-instance SRCALPHA
        surface once; subsequent frames blit the bitmap at the current
        scrolling x. Margin covers buckets / hot-dog tilts / corn-dog
        rotation that overhang the PIPE_W column."""
        from game.pillar_kfc import draw_pillar_pair_kfc
        margin = 64
        cache_w = PIPE_W + margin * 2
        cache_h = GROUND_Y
        cache = pygame.Surface((cache_w, cache_h), pygame.SRCALPHA)
        local_top = pygame.Rect(margin, 0,
                                PIPE_W, int(self.gap_y - self.gap_h / 2))
        local_bot_top = int(self.gap_y + self.gap_h / 2)
        local_bot = pygame.Rect(margin, local_bot_top,
                                PIPE_W, GROUND_Y - local_bot_top)
        draw_pillar_pair_kfc(cache, local_top, local_bot, palette, self.seed)
        self._kfc_cache = cache
        self._kfc_cache_dx = -margin


# ── Coin ─────────────────────────────────────────────────────────────────────

_COIN_FACE_CACHE: "pygame.Surface | None" = None
_TRIPLE_COIN_FACE_CACHE: "pygame.Surface | None" = None


def _get_coin_face() -> pygame.Surface:
    """Build the face-on coin sprite once at 8x super-sample. Layers:
    dark-amber outline, a twisted-rope rim (alternating dark/light
    segments around the perimeter), a vertical gold gradient body, an
    embossed parrot silhouette, and a soft upper-left specular highlight.
    Smoothscaled per frame to apply the coin-spin squeeze, so the rope
    rim stays visible across every frame of the rotation animation."""
    global _COIN_FACE_CACHE
    if _COIN_FACE_CACHE is not None:
        return _COIN_FACE_CACHE
    SS = 8
    # Cache at 4x display so the per-frame spin smoothscale is the AA pass.
    DISPLAY_D = COIN_R * 2 + 4
    CACHE_MUL = 4
    final_d = DISPLAY_D * CACHE_MUL
    size = final_d * SS
    # U scales the parrot with the cache; SS stays for 1-px AA margins only.
    U = SS * CACHE_MUL
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    r_outer = size // 2 - SS
    r_outline = max(SS * 2, r_outer // 6)
    r_body = r_outer - r_outline

    GOLD_HI    = (255, 232, 130)
    GOLD_MID   = (240, 195,  55)
    GOLD_LO    = (190, 130,  20)
    OUTLINE_DK = ( 95,  50,   0)
    OUTLINE_LT = (150,  90,  10)
    EMBOSS     = (130,  80,   0)
    EMBOSS_DK  = ( 90,  50,   0)
    EMBOSS_HI  = (180, 120,  10)
    DARK_AMBER = ( 75,  35,   0)
    LITE_AMBER = (210, 165,  50)

    # 1) Bold double-band outline.
    pygame.draw.circle(surf, OUTLINE_DK, (cx, cy), r_outer)
    pygame.draw.circle(surf, OUTLINE_LT, (cx, cy), r_outer - SS)

    # 2) Vertical gradient body, masked to the inner circle.
    body_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    y0, y1 = cy - r_body, cy + r_body
    for yy in range(y0, y1 + 1):
        t = (yy - y0) / max(1, (y1 - y0))
        if t < 0.4:
            u = t / 0.4
            col = (
                int(GOLD_HI[0]  + (GOLD_MID[0] - GOLD_HI[0])  * u),
                int(GOLD_HI[1]  + (GOLD_MID[1] - GOLD_HI[1])  * u),
                int(GOLD_HI[2]  + (GOLD_MID[2] - GOLD_HI[2])  * u),
            )
        else:
            u = (t - 0.4) / 0.6
            col = (
                int(GOLD_MID[0] + (GOLD_LO[0]  - GOLD_MID[0]) * u),
                int(GOLD_MID[1] + (GOLD_LO[1]  - GOLD_MID[1]) * u),
                int(GOLD_MID[2] + (GOLD_LO[2]  - GOLD_MID[2]) * u),
            )
        pygame.draw.line(body_surf, col, (0, yy), (size, yy))
    body_mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(body_mask, (255, 255, 255, 255), (cx, cy), r_body)
    body_surf.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body_surf, (0, 0))

    # 3) Twisted-rope rim — alternating dark/light arcs around the perimeter.
    n_segs = 22
    ring_r = r_outer - r_outline // 2
    seg_w = max(SS * 3, r_outline + SS)
    for i in range(n_segs):
        ang = i * (math.tau / n_segs)
        ang_next = (i + 1) * (math.tau / n_segs)
        mid = (ang + ang_next) / 2
        sx = cx + math.cos(mid) * ring_r
        sy = cy + math.sin(mid) * ring_r
        seg_len = int((math.tau / n_segs) * ring_r * 0.95)
        seg = pygame.Surface((seg_len, seg_w), pygame.SRCALPHA)
        col       = DARK_AMBER if i % 2 == 0 else LITE_AMBER
        highlight = LITE_AMBER if i % 2 == 0 else GOLD_HI
        pygame.draw.ellipse(seg, col, seg.get_rect())
        pygame.draw.ellipse(seg, highlight, seg.get_rect().inflate(-SS, -SS))
        rotated = pygame.transform.rotate(seg, -math.degrees(mid))
        r_rect = rotated.get_rect(center=(int(sx), int(sy)))
        surf.blit(rotated, r_rect.topleft)

    # 4) Embossed parrot silhouette inside the rope rim.
    #    Flying-pose, head pointing left. Body + tail + tucked wing +
    #    head + hooked beak + eye dot. Two emboss tones (mid + dark)
    #    plus a gold highlight give the figure enough volume to read
    #    as a bird at the 26 px coin size, instead of a flat blob.

    # Body — oval, slightly elongated horizontally.
    pygame.draw.ellipse(surf, EMBOSS,
                        (cx - 2 * U, cy - 1 * U, 7 * U, 5 * U))

    # Tail — tapered fan extending right past the body.
    pygame.draw.polygon(surf, EMBOSS,
                        [(cx + 4 * U, cy + 0 * U),
                         (cx + 7 * U, cy + 1 * U),
                         (cx + 6 * U, cy + 3 * U),
                         (cx + 4 * U, cy + 2 * U)])

    # Wing — darker tucked shape on the body (lower-right of body),
    # suggests a folded wing in flight.
    pygame.draw.polygon(surf, EMBOSS_DK,
                        [(cx + 0 * U, cy + 0 * U),
                         (cx + 3 * U, cy + 0 * U),
                         (cx + 4 * U, cy + 2 * U),
                         (cx + 1 * U, cy + 3 * U)])

    # Head — circle, upper-left.
    head_cx, head_cy = cx - 1 * U, cy - 3 * U
    pygame.draw.circle(surf, EMBOSS, (head_cx, head_cy), 3 * U)

    # Beak — main hooked triangle pointing left.
    pygame.draw.polygon(surf, EMBOSS,
                        [(cx - 3 * U, cy - 3 * U),
                         (cx - 6 * U, cy - 2 * U),
                         (cx - 3 * U, cy - 1 * U)])
    # Beak shadow — small darker wedge under the hook for curvature.
    pygame.draw.polygon(surf, EMBOSS_DK,
                        [(cx - 5 * U, cy - 2 * U),
                         (cx - 6 * U, cy - 2 * U),
                         (cx - 4 * U, cy - 1 * U)])

    # Eye — small bright dot on the head (replaces the original
    # floating "highlight" with a positioned eye that gives the bird
    # a face).
    pygame.draw.circle(surf, GOLD_HI,
                       (head_cx + U // 2, head_cy - U // 2),
                       max(1, U // 2))

    # 5) Specular highlight crescent on the upper-left, masked to body.
    hl = pygame.Surface((size, size), pygame.SRCALPHA)
    hl_rect = pygame.Rect(cx - r_body + r_body // 5,
                          cy - r_body + r_body // 6,
                          int(r_body * 1.1), int(r_body * 0.5))
    pygame.draw.ellipse(hl, (255, 255, 235, 110), hl_rect)
    hl.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hl, (0, 0))

    _COIN_FACE_CACHE = pygame.transform.smoothscale(surf, (final_d, final_d))
    return _COIN_FACE_CACHE


def _get_coin_face_triple() -> pygame.Surface:
    """3X-mode coin face: same rim/body/rope/specular as the standard coin,
    but the embossed parrot is replaced by a large `$` in the original
    EMBOSS amber. Reads as struck into the gold body, same recipe the
    parrot uses (flat amber on gold, no outline, no shadow). Cached
    identically to _get_coin_face."""
    global _TRIPLE_COIN_FACE_CACHE
    if _TRIPLE_COIN_FACE_CACHE is not None:
        return _TRIPLE_COIN_FACE_CACHE
    SS = 8
    DISPLAY_D = COIN_R * 2 + 4
    CACHE_MUL = 4
    final_d = DISPLAY_D * CACHE_MUL
    size = final_d * SS
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    r_outer = size // 2 - SS
    r_outline = max(SS * 2, r_outer // 6)
    r_body = r_outer - r_outline

    GOLD_HI    = (255, 232, 130)
    GOLD_MID   = (240, 195,  55)
    GOLD_LO    = (190, 130,  20)
    OUTLINE_DK = ( 95,  50,   0)
    OUTLINE_LT = (150,  90,  10)
    DARK_AMBER = ( 75,  35,   0)
    LITE_AMBER = (210, 165,  50)
    EMBOSS     = (130,  80,   0)

    # Layers 1-3 + 5: rim, gradient body, rope rim, specular highlight —
    # identical to _get_coin_face (parrot section omitted; `$` stamped
    # post-smoothscale at display resolution for crisp Liberation-Sans
    # rendering).
    pygame.draw.circle(surf, OUTLINE_DK, (cx, cy), r_outer)
    pygame.draw.circle(surf, OUTLINE_LT, (cx, cy), r_outer - SS)

    body_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    y0, y1 = cy - r_body, cy + r_body
    for yy in range(y0, y1 + 1):
        t = (yy - y0) / max(1, (y1 - y0))
        if t < 0.4:
            u = t / 0.4
            col = (
                int(GOLD_HI[0]  + (GOLD_MID[0] - GOLD_HI[0])  * u),
                int(GOLD_HI[1]  + (GOLD_MID[1] - GOLD_HI[1])  * u),
                int(GOLD_HI[2]  + (GOLD_MID[2] - GOLD_HI[2])  * u),
            )
        else:
            u = (t - 0.4) / 0.6
            col = (
                int(GOLD_MID[0] + (GOLD_LO[0]  - GOLD_MID[0]) * u),
                int(GOLD_MID[1] + (GOLD_LO[1]  - GOLD_MID[1]) * u),
                int(GOLD_MID[2] + (GOLD_LO[2]  - GOLD_MID[2]) * u),
            )
        pygame.draw.line(body_surf, col, (0, yy), (size, yy))
    body_mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(body_mask, (255, 255, 255, 255), (cx, cy), r_body)
    body_surf.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body_surf, (0, 0))

    n_segs = 22
    ring_r = r_outer - r_outline // 2
    seg_w = max(SS * 3, r_outline + SS)
    for i in range(n_segs):
        ang = i * (math.tau / n_segs)
        ang_next = (i + 1) * (math.tau / n_segs)
        mid = (ang + ang_next) / 2
        sx = cx + math.cos(mid) * ring_r
        sy = cy + math.sin(mid) * ring_r
        seg_len = int((math.tau / n_segs) * ring_r * 0.95)
        seg = pygame.Surface((seg_len, seg_w), pygame.SRCALPHA)
        col       = DARK_AMBER if i % 2 == 0 else LITE_AMBER
        highlight = LITE_AMBER if i % 2 == 0 else GOLD_HI
        pygame.draw.ellipse(seg, col, seg.get_rect())
        pygame.draw.ellipse(seg, highlight, seg.get_rect().inflate(-SS, -SS))
        rotated = pygame.transform.rotate(seg, -math.degrees(mid))
        r_rect = rotated.get_rect(center=(int(sx), int(sy)))
        surf.blit(rotated, r_rect.topleft)

    hl = pygame.Surface((size, size), pygame.SRCALPHA)
    hl_rect = pygame.Rect(cx - r_body + r_body // 5,
                          cy - r_body + r_body // 6,
                          int(r_body * 1.1), int(r_body * 0.5))
    pygame.draw.ellipse(hl, (255, 255, 235, 110), hl_rect)
    hl.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hl, (0, 0))

    face = pygame.transform.smoothscale(surf, (final_d, final_d))

    # Stamp `$` at display resolution, 3× super-sampled for crisp edges.
    import pathlib as _pl
    glyph_size = 80
    SS_G = 3
    fpath = str(_pl.Path(__file__).parent / "assets" / "LiberationSans-Bold.ttf")
    f = pygame.font.Font(fpath, glyph_size * SS_G)
    big = f.render("$", True, EMBOSS)
    bw, bh = big.get_size()
    glyph = pygame.transform.smoothscale(big, (bw // SS_G, bh // SS_G))
    fcx = fcy = face.get_width() // 2
    face.blit(glyph, glyph.get_rect(center=(fcx, fcy + 1)).topleft)

    _TRIPLE_COIN_FACE_CACHE = face
    return _TRIPLE_COIN_FACE_CACHE


class Coin:
    """Spinning gold parrot medallion. Built once at 4x super-sample with a
    bold dark outline + vertical gold gradient + embossed parrot + soft
    specular highlight (matches the +1/+3 float-text style guidelines:
    gradient, outline, sparkle). Squeezed horizontally per frame by
    |cos(spin)|. Sparkle twinkles flash near the coin in the spin cycle."""

    SPIN_RATE = 1.1  # ≈ 5.7 seconds per full rotation

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.spin = random.uniform(0, math.tau)
        self.collected = False
        self.float_t = random.uniform(0, math.tau)
        # Random sparkle phase per-coin so they don't all twinkle in sync.
        self._sparkle_phase = random.uniform(0, math.tau)
        # Weather: rain shakes coins left-right (visual-only x offset).
        self.weather_dx = 0.0
        self._weather_phase = random.uniform(0, math.tau)

    def update(self, dt):
        self.spin = (self.spin + dt * self.SPIN_RATE) % math.tau
        self.float_t += dt

    def draw(self, surf, kfc_active=False, triple_active=False):
        cx = int(self.x + self.weather_dx)
        cy = int(self.y + math.sin(self.float_t * 2.2) * 2)

        # During KFC: coins look like a tilted french fry instead of a gold
        # disc. The fry uses the same footprint as the coin so collisions
        # stay aligned, but it doesn't spin (fries don't really spin like
        # a disc — they just bob).
        if kfc_active:
            from game.kfc_fries import draw_tilted
            draw_tilted(surf, cx, cy, t=self.float_t)
            return

        # Spin animation: the cached face is smoothscaled horizontally by
        # |cos(spin)| every frame, so the rope rim, outline, gradient, and
        # embossed parrot/$ are all preserved across every angle of the
        # rotation — including near-edge-on slivers. A small floor on the
        # squeeze (10% width) keeps the edge-on frame readable instead of
        # collapsing to a 1-px line.
        cos_s = math.cos(self.spin)
        r = COIN_R
        squeeze = max(0.10, abs(cos_s))
        face = _get_coin_face_triple() if triple_active else _get_coin_face()
        # Source is 4x display; downsample target is on-screen size, not face size.
        display_h = COIN_R * 2 + 4
        display_w = max(2, int(display_h * squeeze))
        squeezed = pygame.transform.smoothscale(face, (display_w, display_h))
        rect = squeezed.get_rect(center=(cx, cy))
        surf.blit(squeezed, rect.topleft)

        # Sparkle twinkles — 2 small white dots near the coin that flash
        # on/off out of phase. Only render when mostly face-on so they
        # don't drift around a flat sliver.
        if abs(cos_s) > 0.6:
            for i, (dx, dy) in enumerate(((-r - 2, -r + 1), (r + 2, r - 1))):
                phase = self._sparkle_phase + i * math.pi
                t = 0.5 + 0.5 * math.sin(self.float_t * 3.0 + phase)
                if t > 0.7:
                    a = int(255 * (t - 0.7) / 0.3)
                    star = pygame.Surface((6, 6), pygame.SRCALPHA)
                    pygame.draw.circle(star, (255, 250, 220, a), (3, 3), 2)
                    pygame.draw.circle(star, (255, 255, 255, a), (3, 3), 1)
                    surf.blit(star, (cx + dx - 3, cy + dy - 3))


# ── PowerUp ──────────────────────────────────────────────────────────────────

# Lazy-initialized high-resolution cache for the "reverse" power-up icon —
# two purple arrows (up on the left, down on the right) on a fully transparent
# background. Rendered once at 4x super-sampling and smoothscaled down so the
# arrow edges read clean at any size. Reused for both the in-world pickup and
# the HUD active-buff badge.
_REVERSE_ICON_CACHE: "dict[int, pygame.Surface]" = {}


def _build_reverse_icon(out_diameter: int) -> pygame.Surface:
    """Premium icon: holographic iridescent panel inside a pearl-violet frame
    with two thick gradient purple chevrons (up + down). Built at 4x super-
    sampling and smoothscaled down for crisp edges on any background."""
    SS = 4
    size = out_diameter * SS
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    # ── Palette ─────────────────────────────────────────────────────────
    OUTLINE      = (20, 12, 55)         # outer dark indigo hairline
    FRAME        = (195, 175, 240)      # pearl-violet frame stroke
    FRAME_HL     = (255, 255, 255)      # tiny top-edge highlight
    INSET_SHADOW = (0, 0, 0, 38)        # soft inner shadow under the frame
    HOLO_STOPS   = (
        (240, 220, 240),                # top-left: pale pink
        (210, 220, 245),                # mid: lavender-blue
        (215, 240, 240),                # bottom-right: mint cyan
    )
    ARROW_TOP    = (175, 100, 230)
    ARROW_MID    = (130, 55, 200)
    ARROW_BOT    = (75, 25, 145)
    ARROW_OUT    = (35, 10, 70)
    SHEEN        = (255, 255, 255, 80)

    radius   = SS * 11                 # squircle-style corners
    inset    = SS                      # 1-px outer outline gap
    frame_t  = SS * 2                  # frame stroke = 2 final-px

    panel = pygame.Rect(inset, inset, size - inset * 2, size - inset * 2)

    # 1) Outer 1-px dark hairline.
    pygame.draw.rect(surf, OUTLINE, panel, border_radius=radius)
    # 2) Pearl-violet frame fill.
    pygame.draw.rect(surf, FRAME, panel.inflate(-SS * 2, -SS * 2),
                     border_radius=radius - SS)
    # 3) Holographic diagonal gradient panel inside the frame.
    inner = panel.inflate(-(frame_t + SS) * 2, -(frame_t + SS) * 2)
    inner_radius = max(2, radius - frame_t - SS)
    grad = pygame.Surface((size, size), pygame.SRCALPHA)
    for y in range(inner.top, inner.bottom + 1):
        for x in range(inner.left, inner.right + 1):
            t = ((x - inner.left) / max(1, inner.width)
                 + (y - inner.top) / max(1, inner.height)) / 2
            if t < 0.5:
                u = t / 0.5
                col = (
                    int(HOLO_STOPS[0][0] + (HOLO_STOPS[1][0] - HOLO_STOPS[0][0]) * u),
                    int(HOLO_STOPS[0][1] + (HOLO_STOPS[1][1] - HOLO_STOPS[0][1]) * u),
                    int(HOLO_STOPS[0][2] + (HOLO_STOPS[1][2] - HOLO_STOPS[0][2]) * u),
                )
            else:
                u = (t - 0.5) / 0.5
                col = (
                    int(HOLO_STOPS[1][0] + (HOLO_STOPS[2][0] - HOLO_STOPS[1][0]) * u),
                    int(HOLO_STOPS[1][1] + (HOLO_STOPS[2][1] - HOLO_STOPS[1][1]) * u),
                    int(HOLO_STOPS[1][2] + (HOLO_STOPS[2][2] - HOLO_STOPS[1][2]) * u),
                )
            grad.set_at((x, y), col)
    inner_mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(inner_mask, (255, 255, 255, 255), inner,
                     border_radius=inner_radius)
    grad.blit(inner_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (0, 0))

    # 4) Soft inner shadow inside the panel — gives the panel a recessed feel.
    shadow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, INSET_SHADOW, inner,
                     border_radius=inner_radius, width=SS)
    surf.blit(shadow_surf, (0, 0))

    # 5) Top-edge highlight on the frame.
    pygame.draw.line(surf, FRAME_HL,
                     (panel.left + radius, panel.top + SS),
                     (panel.right - radius, panel.top + SS),
                     max(1, SS // 2))

    # ── Arrows: thick filled chevrons with vertical gradient + sheen ───
    pad_x = max(SS * 5, panel.width // 6)
    pad_y = max(SS * 5, panel.height // 7)
    area = panel.inflate(-pad_x * 2, -pad_y * 2)

    col_w = area.width // 2
    lx = area.left + col_w // 2
    rx = area.right - col_w // 2
    head_h  = area.height * 42 // 100
    shaft_w = area.width * 17 // 100
    head_w  = shaft_w * 26 // 10

    def silhouette(col_x, *, point_up, expand=0):
        e = expand
        sw = shaft_w + e * 2
        hw = head_w + e * 2
        if point_up:
            tip  = (col_x, area.top - e)
            base = area.bottom + e
            sh_y = area.top + head_h - e // 3
            return [
                tip,
                (col_x + hw // 2, sh_y),
                (col_x + sw // 2, sh_y),
                (col_x + sw // 2, base),
                (col_x - sw // 2, base),
                (col_x - sw // 2, sh_y),
                (col_x - hw // 2, sh_y),
            ]
        else:
            tip  = (col_x, area.bottom + e)
            base = area.top - e
            sh_y = area.bottom - head_h + e // 3
            return [
                tip,
                (col_x - hw // 2, sh_y),
                (col_x - sw // 2, sh_y),
                (col_x - sw // 2, base),
                (col_x + sw // 2, base),
                (col_x + sw // 2, sh_y),
                (col_x + hw // 2, sh_y),
            ]

    def draw_arrow(col_x, *, point_up):
        # Outline.
        pygame.draw.polygon(surf, ARROW_OUT,
                            silhouette(col_x, point_up=point_up, expand=SS))
        # Vertical gradient body, scanline-masked.
        body = silhouette(col_x, point_up=point_up, expand=0)
        body_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        ys = [p[1] for p in body]
        y0, y1 = min(ys), max(ys)
        for y in range(y0, y1 + 1):
            t = (y - y0) / max(1, (y1 - y0))
            if not point_up:
                t = 1.0 - t
            if t < 0.4:
                u = t / 0.4
                col = (
                    int(ARROW_TOP[0] + (ARROW_MID[0] - ARROW_TOP[0]) * u),
                    int(ARROW_TOP[1] + (ARROW_MID[1] - ARROW_TOP[1]) * u),
                    int(ARROW_TOP[2] + (ARROW_MID[2] - ARROW_TOP[2]) * u),
                )
            else:
                u = (t - 0.4) / 0.6
                col = (
                    int(ARROW_MID[0] + (ARROW_BOT[0] - ARROW_MID[0]) * u),
                    int(ARROW_MID[1] + (ARROW_BOT[1] - ARROW_MID[1]) * u),
                    int(ARROW_MID[2] + (ARROW_BOT[2] - ARROW_MID[2]) * u),
                )
            pygame.draw.line(body_surf, col, (0, y), (size, y))
        mask = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), body)
        body_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(body_surf, (0, 0))

        # Glossy sheen across the arrow head.
        sheen = pygame.Surface((size, size), pygame.SRCALPHA)
        if point_up:
            sy0, sy1 = area.top, area.top + head_h * 9 // 10
        else:
            sy0, sy1 = area.bottom - head_h * 9 // 10, area.bottom
        for y in range(min(sy0, sy1), max(sy0, sy1) + 1):
            t = (y - sy0) / max(1, (sy1 - sy0))
            if not point_up:
                t = 1.0 - t
            a = int(SHEEN[3] * (1.0 - t) ** 1.4)
            if a > 0:
                pygame.draw.line(sheen, (*SHEEN[:3], a), (0, y), (size, y))
        sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(sheen, (0, 0))

    draw_arrow(lx, point_up=True)
    draw_arrow(rx, point_up=False)

    return pygame.transform.smoothscale(surf, (out_diameter, out_diameter))


def _get_reverse_icon(diameter: int = (POWERUP_R + 8) * 2) -> pygame.Surface:
    cached = _REVERSE_ICON_CACHE.get(diameter)
    if cached is None:
        cached = _build_reverse_icon(diameter)
        _REVERSE_ICON_CACHE[diameter] = cached
    return cached


class PowerUp:
    """A collectible buff. `kind` selects visuals and pickup effect:
       triple   — red mushroom, 3x coin value for TRIPLE_DURATION
       magnet   — red horseshoe, pulls coins in for MAGNET_DURATION
       slowmo   — purple hourglass, 0.5x world scroll for SLOWMO_DURATION
       kfc      — KFC bucket, fried-chicken parrot mode for KFC_DURATION
       ghost    — phantom, phase-through pipes for GHOST_DURATION
       grow     — Mario mushroom, scaled-up parrot for GROW_DURATION
       reverse  — purple double-arrow, flips Pip's gravity for REVERSE_DURATION
       surprise — gold "?" block; resolves at pickup to one of the seven
                  effects above (the matching sound plays, no separate
                  surprise sound).
       shrink   — red-velvet mushroom; bird scales to SHRINK_SCALE
       rail     — train ticket; cart ride over RAIL_PILLAR_COUNT pillars
       lottery  — scratch card; rolls a tier and applies its coin delta
    """
    def __init__(self, x, y, kind="triple"):
        self.x = x
        self.y = y
        self.kind = kind
        self.collected = False
        self.pulse = 0.0

    def update(self, dt):
        self.pulse += dt * 3.5

    def draw(self, surf):
        if self.kind == "triple":
            _draw_dollar_coin(surf, int(self.x), int(self.y), pulse=self.pulse)
        elif self.kind == "magnet":
            self._draw_magnet(surf)
        elif self.kind == "megamagnet":
            self._draw_megamagnet(surf)
        elif self.kind == "slowmo":
            self._draw_slowmo(surf)
        elif self.kind == "kfc":
            self._draw_kfc(surf)
        elif self.kind == "ghost":
            self._draw_ghost(surf)
        elif self.kind == "grow":
            self._draw_mushroom(surf)    # mushroom icon (Mario super-mushroom feel)
        elif self.kind == "reverse":
            self._draw_reverse(surf)
        elif self.kind == "surprise":
            self._draw_surprise(surf)
        elif self.kind == "shrink":
            self._draw_shrink_mushroom(surf)
        elif self.kind == "rail":
            self._draw_rail_icon(surf)
        elif self.kind == "lottery":
            self._draw_lottery_icon(surf)

    # ── sprite variants ─────────────────────────────────────────────────────
    def _draw_mushroom(self, surf):
        cx = int(self.x)
        cy = int(self.y)
        _draw_grow_halo(surf, cx, cy, self.pulse)
        sprite, dx, dy = _get_grow_body_sprite()
        surf.blit(sprite, (cx + dx, cy + dy))

    def _draw_surprise(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.7) * 2)
        sprite = _get_surprise_sprite()
        surf.blit(sprite, sprite.get_rect(center=(cx, cy)))

    def _draw_magnet(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.1) * 3)   # float bob

        outer_r = 13
        inner_r = 6
        arch_cy = cy - 3
        leg_bot = cy + 12

        # Build the horseshoe on an SRCALPHA scratch surface so the hollow
        # can be punched cleanly with alpha=0 overdraw.
        sz  = 42
        scx = sz // 2
        scy = outer_r + 4

        scratch = pygame.Surface((sz, sz), pygame.SRCALPHA)

        # Dark shadow rim
        pygame.draw.circle(scratch, (80, 5, 8), (scx, scy), outer_r + 2)
        pygame.draw.rect(scratch, (80, 5, 8),
                         (scx - outer_r - 2, scy,
                          (outer_r + 2) * 2, leg_bot - arch_cy + 4))

        # Vivid crimson body
        RED_HI = (235, 35, 45)
        pygame.draw.circle(scratch, RED_HI, (scx, scy), outer_r + 1)
        pygame.draw.rect(scratch, RED_HI,
                         (scx - outer_r - 1, scy,
                          (outer_r + 1) * 2, leg_bot - arch_cy + 3))

        # No upper specular sheen — the body keeps a clean uniform red.

        # Highlight rings
        pygame.draw.circle(scratch, (255, 95, 95), (scx, scy), inner_r + 1, 2)
        pygame.draw.circle(scratch, (255, 85, 85), (scx, scy), outer_r, 2)

        # Punch inner hollow
        pygame.draw.circle(scratch, (0, 0, 0, 0), (scx, scy), inner_r)
        # Punch gap between legs
        pygame.draw.rect(scratch, (0, 0, 0, 0),
                         (scx - inner_r, scy, inner_r * 2, sz - scy))

        surf.blit(scratch, (cx - scx, arch_cy - scy))

        # Chrome pole tips
        left_cx  = cx - inner_r - (outer_r - inner_r) // 2
        right_cx = cx + inner_r + (outer_r - inner_r) // 2
        arm_w    = outer_r - inner_r
        for tip_cx in (left_cx, right_cx):
            pygame.draw.rect(surf, (40, 42, 60),
                             (tip_cx - arm_w // 2 - 1, leg_bot - 4, arm_w + 2, 9),
                             border_radius=4)
            pygame.draw.rect(surf, (195, 210, 232),
                             (tip_cx - arm_w // 2,     leg_bot - 3, arm_w,     7),
                             border_radius=3)
            pygame.draw.rect(surf, (238, 246, 255),
                             (tip_cx - arm_w // 2 + 1, leg_bot - 3, arm_w - 2, 3),
                             border_radius=2)

        # Animated lightning arc between poles
        arc_y0  = leg_bot + 6
        arc_pts = [(left_cx, arc_y0)]
        for i in range(1, 6):
            t = i / 6
            x = int(left_cx + (right_cx - left_cx) * t)
            y = int(arc_y0 + math.sin(self.pulse * 11 + i * 1.7) * 4)
            arc_pts.append((x, y))
        arc_pts.append((right_cx, arc_y0))
        arc_surf = pygame.Surface((right_cx - left_cx + 8, 16), pygame.SRCALPHA)
        shifted = [(p[0] - left_cx + 4, p[1] - arc_y0 + 4) for p in arc_pts]
        if len(shifted) >= 2:
            pygame.draw.lines(arc_surf, (100, 195, 255, 200), False, shifted, 2)
        surf.blit(arc_surf, (left_cx - 4, arc_y0 - 4))

        # Extra lightning bolts radiating outward from each pole tip,
        # crackling with self.pulse so the magnet feels actively powered.
        YELLOW = (255, 220,  60)
        WHITE  = (255, 250, 220)

        def _bolt(target, pts, thick_outer, thick_inner):
            if len(pts) < 2:
                return
            pygame.draw.lines(target, YELLOW, False, pts, thick_outer)
            pygame.draw.lines(target, WHITE,  False, pts, max(1, thick_inner))

        for sign, tip_cx in ((-1, left_cx), (+1, right_cx)):
            tip_y = leg_bot + 1
            jitter = math.sin(self.pulse * 9 + (0 if sign < 0 else math.pi / 3))

            # Down-and-outward bolt
            _bolt(surf,
                  [
                      (tip_cx,                 tip_y),
                      (tip_cx + sign * 4,      tip_y + 2),
                      (tip_cx + sign * 1,      tip_y + 4 + int(jitter)),
                      (tip_cx + sign * 5,      tip_y + 6),
                  ],
                  thick_outer=2, thick_inner=1)

            # Sideways crackle
            _bolt(surf,
                  [
                      (tip_cx + sign * 1,      tip_y - 1),
                      (tip_cx + sign * 4,      tip_y),
                      (tip_cx + sign * 2,      tip_y + 2),
                      (tip_cx + sign * 6,      tip_y + 1),
                  ],
                  thick_outer=2, thick_inner=1)

            # Bright dot at the pole tip — discharge origin
            pygame.draw.circle(surf, WHITE,  (tip_cx, tip_y), 2)
            pygame.draw.circle(surf, YELLOW, (tip_cx, tip_y), 1)

    # Megamagnet sprite — the late-game upgrade form of `magnet`.
    # Beefier crimson body (outer_r 13->14, inner_r 6->5, arm width
    # 7->9 px), copper coil wraps down each arm, thick cyan zigzag
    # arc between the pole tips, and glowing yellow-white discharge
    # balls at each pole. Locked-in spec from
    # tools/snapshot_megamagnet_final.py (see
    # docs/screenshots/powerups/megamagnet/icon_final.png).
    def _draw_megamagnet(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.1) * 3)

        OUTER_R, INNER_R = 14, 5
        ARM_W = OUTER_R - INNER_R   # = 9
        # Coil cluster has the legacy 11 px width (HALF_SPAN=5) and is
        # shifted outward asymmetrically — the half-pixel rounding in
        # left_cx puts the legacy tip_cx 0.5 px inside the arm centre,
        # so the left arm wants 1 extra px outward to read centred.
        HALF_SPAN = 5
        LEFT_SHIFT, RIGHT_SHIFT = 2, 1
        BALL_R = 3
        BALL_HALO_R = 7

        arch_cy = cy - 3
        leg_bot = cy + 13

        # Build the horseshoe on an SRCALPHA scratch surface so the
        # hollow can be punched cleanly with alpha=0 overdraw.
        sz = 52
        scx = sz // 2
        scy = OUTER_R + 4

        scratch = pygame.Surface((sz, sz), pygame.SRCALPHA)
        pygame.draw.circle(scratch, (80, 5, 8), (scx, scy), OUTER_R + 2)
        pygame.draw.rect(scratch, (80, 5, 8),
                         (scx - OUTER_R - 2, scy,
                          (OUTER_R + 2) * 2, leg_bot - arch_cy + 4))
        RED_HI = (235, 35, 45)
        pygame.draw.circle(scratch, RED_HI, (scx, scy), OUTER_R + 1)
        pygame.draw.rect(scratch, RED_HI,
                         (scx - OUTER_R - 1, scy,
                          (OUTER_R + 1) * 2, leg_bot - arch_cy + 3))
        pygame.draw.circle(scratch, (255, 95, 95), (scx, scy), INNER_R + 1, 2)
        pygame.draw.circle(scratch, (255, 85, 85), (scx, scy), OUTER_R, 2)
        pygame.draw.circle(scratch, (0, 0, 0, 0), (scx, scy), INNER_R)
        pygame.draw.rect(scratch, (0, 0, 0, 0),
                         (scx - INNER_R, scy, INNER_R * 2, sz - scy))
        surf.blit(scratch, (cx - scx, arch_cy - scy))

        left_cx = cx - INNER_R - ARM_W // 2
        right_cx = cx + INNER_R + ARM_W // 2
        for tip_cx in (left_cx, right_cx):
            pygame.draw.rect(surf, (40, 42, 60),
                             (tip_cx - ARM_W // 2 - 1, leg_bot - 4,
                              ARM_W + 2, 9), border_radius=4)
            pygame.draw.rect(surf, (195, 210, 232),
                             (tip_cx - ARM_W // 2, leg_bot - 3,
                              ARM_W, 7), border_radius=3)
            pygame.draw.rect(surf, (238, 246, 255),
                             (tip_cx - ARM_W // 2 + 1, leg_bot - 3,
                              ARM_W - 2, 3), border_radius=2)

        # Copper coil — 4 wraps per arm with alternating-dip lines.
        COPPER_LO = (110, 55, 14)
        COPPER_HI = (220, 130, 55)
        COPPER_HI_HL = (255, 225, 160)
        for tip_cx, shift in ((left_cx - LEFT_SHIFT, 0),
                              (right_cx + RIGHT_SHIFT, 0)):
            for i in range(4):
                wy = cy + 2 + i * 3
                left_x = tip_cx - HALF_SPAN
                right_x = tip_cx + HALF_SPAN
                mid_x = tip_cx
                dip = 1 if (i % 2 == 0) else -1
                pygame.draw.lines(surf, COPPER_LO, False,
                                  [(left_x, wy + 1),
                                   (mid_x, wy + 1 + dip),
                                   (right_x, wy + 1)], 2)
                pygame.draw.lines(surf, COPPER_HI, False,
                                  [(left_x, wy),
                                   (mid_x, wy + dip),
                                   (right_x, wy)], 1)
                pygame.draw.line(surf, COPPER_HI_HL,
                                 (left_x + 1, wy), (mid_x - 1, wy))

        # Beefy 4 px-thick cyan zigzag arc + yellow-white discharge balls.
        y0 = leg_bot + 7
        arc_pts = [(left_cx, y0)]
        for i in range(1, 6):
            t = i / 6
            ax = int(left_cx + (right_cx - left_cx) * t)
            ay = int(y0 + math.sin(self.pulse * 11 + i * 1.7) * 5)
            arc_pts.append((ax, ay))
        arc_pts.append((right_cx, y0))
        arc_surf = pygame.Surface(
            (right_cx - left_cx + 16, 20), pygame.SRCALPHA)
        shifted = [(p[0] - left_cx + 8, p[1] - y0 + 8) for p in arc_pts]
        pygame.draw.lines(arc_surf, (110, 195, 255, 230), False, shifted, 4)
        pygame.draw.lines(arc_surf, (220, 240, 255, 255), False, shifted, 2)
        surf.blit(arc_surf, (left_cx - 8, y0 - 8))

        for tip_cx in (left_cx, right_cx):
            ball_cy = leg_bot + 2
            glow = pygame.Surface((BALL_HALO_R * 2 + 2, BALL_HALO_R * 2 + 2),
                                  pygame.SRCALPHA)
            gcx = BALL_HALO_R + 1
            for r in range(BALL_HALO_R, 0, -1):
                tt = r / BALL_HALO_R
                a = int(180 * (1 - tt * 0.85))
                pygame.draw.circle(glow, (130, 210, 255, a), (gcx, gcx), r)
            surf.blit(glow, (tip_cx - gcx, ball_cy - gcx))
            pygame.draw.circle(surf, (255, 230, 100),
                               (tip_cx, ball_cy), BALL_R)
            pygame.draw.circle(surf, (255, 255, 240),
                               (tip_cx, ball_cy), max(1, BALL_R - 2))

    def _draw_slowmo(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.7) * 3)
        R = POWERUP_R  # 14

        # Clock face on scratch SRCALPHA surface for clean edges
        PAD = 2
        D = (R + PAD) * 2
        g = pygame.Surface((D, D), pygame.SRCALPHA)
        gc = (D // 2, D // 2)

        # Outer shadow ring
        pygame.draw.circle(g, (15, 0, 35, 200), gc, R + 1)
        # Bezel: two rings for a bevelled metallic look
        pygame.draw.circle(g, (195, 135, 255, 255), gc, R)
        pygame.draw.circle(g, (130, 70, 195, 255), gc, R - 1)
        # Deep purple face
        pygame.draw.circle(g, (42, 10, 70, 255), gc, R - 2)
        # Slightly lighter inner face
        pygame.draw.circle(g, (62, 20, 98, 255), gc, R - 4)

        # Top-left specular highlight
        hl = pygame.Surface((D, D), pygame.SRCALPHA)
        pygame.draw.circle(hl, (255, 230, 255, 60), (gc[0] - 2, gc[1] - 3), R - 5)
        g.blit(hl, (0, 0))

        # Tick marks: 4 major (every 3rd) + 8 minor
        for i in range(12):
            ang = math.pi * 2 * i / 12 - math.pi / 2
            major = (i % 3 == 0)
            r_out = R - 2
            r_in  = r_out - (3 if major else 2)
            x1 = gc[0] + math.cos(ang) * r_out
            y1 = gc[1] + math.sin(ang) * r_out
            x2 = gc[0] + math.cos(ang) * r_in
            y2 = gc[1] + math.sin(ang) * r_in
            col = (230, 200, 255, 240) if major else (165, 125, 210, 160)
            pygame.draw.line(g, col, (int(x1), int(y1)), (int(x2), int(y2)),
                             2 if major else 1)

        # Hour hand — short, thick, slow
        hr_ang = self.pulse * 0.15 - math.pi / 2
        hx = int(gc[0] + math.cos(hr_ang) * (R - 7))
        hy = int(gc[1] + math.sin(hr_ang) * (R - 7))
        pygame.draw.line(g, (250, 225, 255, 255), gc, (hx, hy), 3)

        # Minute hand — long, thinner
        min_ang = self.pulse * 1.1 - math.pi / 2
        mx = int(gc[0] + math.cos(min_ang) * (R - 4))
        my = int(gc[1] + math.sin(min_ang) * (R - 4))
        pygame.draw.line(g, (200, 155, 255, 255), gc, (mx, my), 2)

        # Sweep hand — thinnest, amber, fastest (adds drama)
        sec_ang = self.pulse * 3.8 - math.pi / 2
        sx = int(gc[0] + math.cos(sec_ang) * (R - 3))
        sy = int(gc[1] + math.sin(sec_ang) * (R - 3))
        pygame.draw.line(g, (255, 185, 60, 215), gc, (sx, sy), 1)

        # Center pin
        pygame.draw.circle(g, (255, 240, 255, 255), gc, 2)
        pygame.draw.circle(g, (155, 95, 220, 255), gc, 1)

        surf.blit(g, (cx - D // 2, cy - D // 2))


    def _draw_kfc(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.9) * 2.5)
        r  = POWERUP_R + 2

        # KFC logo (real image, pre-scaled & circle-clipped)
        logo = _get_kfc_sprite()
        surf.blit(logo, (cx - logo.get_width() // 2, cy - logo.get_height() // 2))

    def _draw_ghost(self, surf):
        cx = int(self.x)
        # Supernatural wafting bob: two overlaid frequencies
        cy = int(self.y + math.sin(self.pulse * 0.9) * 4
                        + math.sin(self.pulse * 1.8) * 1.5)
        sprite = _get_ghost_sprite()
        # Sprite was built so the head-circle centre sits at sprite-local
        # (_GHOST_HEAD_OFFSET_X, _GHOST_HEAD_OFFSET_Y); align it to (cx, cy).
        surf.blit(sprite,
                  (cx - _GHOST_HEAD_OFFSET_X, cy - _GHOST_HEAD_OFFSET_Y))


    def _draw_grow(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.2) * 2)

        GREEN_HI  = ( 50, 220, 100)
        GREEN_MID = ( 38, 190,  85)
        GREEN_OUT = ( 28, 160,  70)

        # ── Tall green block-arrow as the backdrop ──────────────────────────
        head_w  = 22
        shaft_w = 9
        total_h = 32
        head_h  = int(total_h * 0.42)
        top_y    = cy - total_h // 2
        head_bot = top_y + head_h
        bot_y    = cy + total_h // 2
        pts_out = [
            (cx,                  top_y),
            (cx + head_w // 2,    head_bot),
            (cx + shaft_w // 2,   head_bot),
            (cx + shaft_w // 2,   bot_y),
            (cx - shaft_w // 2,   bot_y),
            (cx - shaft_w // 2,   head_bot),
            (cx - head_w // 2,    head_bot),
        ]
        pygame.draw.polygon(surf, GREEN_OUT, pts_out)
        pts_in = [
            (cx,                      top_y + 2),
            (cx + head_w // 2 - 2,    head_bot - 1),
            (cx + shaft_w // 2 - 1,   head_bot - 1),
            (cx + shaft_w // 2 - 1,   bot_y - 1),
            (cx - shaft_w // 2 + 1,   bot_y - 1),
            (cx - shaft_w // 2 + 1,   head_bot - 1),
            (cx - head_w // 2 + 2,    head_bot - 1),
        ]
        pygame.draw.polygon(surf, GREEN_HI, pts_in)
        # Highlight band on the left edge of the shaft
        pygame.draw.line(surf, GREEN_MID,
                         (cx - shaft_w // 2 + 2, head_bot + 1),
                         (cx - shaft_w // 2 + 2, bot_y - 2), 2)

        # ── Real in-game parrot, scaled down, on top of the arrow ───────────
        bird = _get_grow_parrot()
        surf.blit(bird, (cx - bird.get_width() // 2, cy - bird.get_height() // 2))

    def _draw_reverse(self, surf):
        cx = int(self.x)
        cy = int(self.y)
        # Breathing scale gives the pickup life without any background.
        breath = 0.5 + 0.5 * math.sin(self.pulse)
        scale = 1.0 + 0.06 * breath
        icon = _get_reverse_icon()
        if scale != 1.0:
            iw, ih = icon.get_size()
            icon = pygame.transform.smoothscale(
                icon, (int(iw * scale), int(ih * scale)))
        surf.blit(icon, (cx - icon.get_width() // 2,
                         cy - icon.get_height() // 2))

    def _draw_shrink_mushroom(self, surf):
        """Sibling-to-GROW mushroom in red velvet: wide flat parasol disc on
        a flared flat-bottomed stem, cream-butter spots, magenta pulsing
        halo. Reads as the same fungal family as GROW; the silhouette is
        the only thing that distinguishes the two pickups at glance."""
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.1) * 2)
        _draw_grow_halo(surf, cx, cy, self.pulse,
                        color_rgb=_GROW_HALO_RGB, radius=40, peak_y_off=0)
        sprite = _get_shrink_body_sprite()
        surf.blit(sprite, sprite.get_rect(center=(cx, cy)))

    def _draw_rail_icon(self, surf):
        """RAIL pickup — Victorian engraved train ticket (RT2): sepia
        paper card with a thick black outer perimeter, a lighter
        engraved inner border, a small "TRAIN" caption, and a
        detailed steam-locomotive silhouette centred on the card."""
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.0) * 2)

        SS = 6
        NATIVE_W, NATIVE_H = 48, 36
        sw, sh = NATIVE_W * SS, NATIVE_H * SS
        big = pygame.Surface((sw, sh), pygame.SRCALPHA)

        SEPIA      = (228, 210, 170)
        CREAM      = (238, 225, 195)
        NEAR_BLACK = ( 18,  14,  10)
        INK        = ( 30,  25,  20)

        card = pygame.Rect(3 * SS, 3 * SS, sw - 6 * SS, sh - 6 * SS)
        pygame.draw.rect(big, SEPIA, card)
        pygame.draw.rect(big, NEAR_BLACK, card, max(2, int(SS * 1.4)))
        inner = card.inflate(-int(SS * 3.5), -int(SS * 3.5))
        pygame.draw.rect(big, NEAR_BLACK, inner, max(1, int(SS * 0.6)))

        def locomotive(loco_cx, loco_cy, scale=1.0):
            boiler_w = int(SS * 14 * scale)
            boiler_h = int(SS * 6 * scale)
            boiler = pygame.Rect(0, 0, boiler_w, boiler_h)
            boiler.midright = (loco_cx + int(SS * 7 * scale), loco_cy)
            pygame.draw.rect(big, INK, boiler,
                             border_radius=max(1, int(SS * 0.7 * scale)))
            cab_w = int(SS * 5 * scale)
            cab_h = int(SS * 7.5 * scale)
            cab = pygame.Rect(0, 0, cab_w, cab_h)
            cab.midright = (boiler.left, loco_cy)
            pygame.draw.rect(big, INK, cab,
                             border_radius=max(1, int(SS * 0.5 * scale)))
            roof = pygame.Rect(0, 0, cab_w + int(SS * 1.2 * scale),
                                max(1, int(SS * 0.8 * scale)))
            roof.midbottom = (cab.centerx, cab.top + max(1, SS // 3))
            pygame.draw.rect(big, INK, roof)
            stack_w = max(2, int(SS * 1.6 * scale))
            stack_h = max(3, int(SS * 3.2 * scale))
            stack_x = (boiler.right - int(SS * 3.5 * scale) - stack_w // 2)
            stack = pygame.Rect(stack_x, boiler.top - stack_h, stack_w, stack_h)
            pygame.draw.rect(big, INK, stack)
            flare = pygame.Rect(0, 0, int(stack_w * 1.8),
                                 max(1, int(SS * 0.6 * scale)))
            flare.midbottom = (stack.centerx, stack.top)
            pygame.draw.rect(big, INK, flare)
            wheel_r = max(3, int(SS * 2.6 * scale))
            gap = max(1, int(SS * 0.4 * scale))
            wheel_cy = boiler.bottom + wheel_r + gap
            ground_y = wheel_cy + wheel_r
            wheel_xs = (
                boiler.left + int(boiler.width * 0.05),
                boiler.left + int(boiler.width * 0.72),
            )
            cow_top_inner = boiler.bottom - max(1, int(SS * 0.4 * scale))
            cow_outer_x = boiler.right + int(SS * 4 * scale)
            cow_bot_y = ground_y - max(1, int(SS * 0.5 * scale))
            cow_top_outer_y = cow_top_inner + int(SS * 1.5 * scale)
            cow_pts = [
                (boiler.right, cow_top_inner),
                (cow_outer_x, cow_top_outer_y),
                (cow_outer_x, cow_bot_y),
                (boiler.right, cow_bot_y - int(SS * 0.6 * scale)),
            ]
            pygame.draw.polygon(big, INK, cow_pts)
            for f in (0.30, 0.55, 0.80):
                vx = cow_pts[0][0] + int((cow_pts[1][0] - cow_pts[0][0]) * f)
                v_top = cow_top_inner + int(SS * 1 * scale * f)
                v_bot = cow_bot_y - max(1, SS // 3)
                pygame.draw.line(big, CREAM, (vx, v_top), (vx, v_bot),
                                 max(1, SS // 3))
            rod_h = max(2, int(SS * 1.0 * scale))
            rod_y = wheel_cy - int(wheel_r * 0.35) - rod_h // 2
            pygame.draw.rect(big, INK,
                             (wheel_xs[0], rod_y,
                              wheel_xs[1] - wheel_xs[0], rod_h))
            for wx in wheel_xs:
                pygame.draw.circle(big, INK, (wx, wheel_cy), wheel_r)
                for ang_deg in (0, 60, 120, 180, 240, 300):
                    ang = math.radians(ang_deg)
                    x2 = wx + math.cos(ang) * (wheel_r - SS // 2)
                    y2 = wheel_cy + math.sin(ang) * (wheel_r - SS // 2)
                    pygame.draw.line(big, CREAM, (wx, wheel_cy),
                                     (int(x2), int(y2)),
                                     max(1, int(SS * 0.45 * scale)))
                pygame.draw.circle(big, CREAM, (wx, wheel_cy),
                                   max(1, int(SS * 0.7 * scale)))
                pygame.draw.circle(big, INK, (wx, wheel_cy), wheel_r,
                                   max(1, int(SS * 0.35 * scale)))
                pygame.draw.circle(big, CREAM,
                                   (wx, rod_y + rod_h // 2),
                                   max(1, int(SS * 0.6 * scale)))

        f_hdr = _get_float_font(int(SS * 9))
        f_hdr.set_bold(True)
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            hdr = f_hdr.render("TRAIN", True, NEAR_BLACK)
            big.blit(hdr, hdr.get_rect(
                center=(card.centerx + dx,
                         card.top + int(SS * 6.5) + dy)))

        locomotive(card.centerx, card.centery + int(SS * 3.5), scale=1.15)

        tilt = math.sin(self.pulse * 0.7) * 4
        rotated = pygame.transform.rotate(big, tilt)
        rw, rh = rotated.get_size()
        final = pygame.transform.smoothscale(rotated, (rw // SS, rh // SS))
        surf.blit(final, final.get_rect(center=(cx, cy)))

    def _draw_lottery_icon(self, surf):
        """Scratch-off lottery card: gold body with a chrome perimeter,
        a red LUCKY chip riding the top edge, and 3 large silver
        scratch cells each with a single "?"."""
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.8) * 2)

        SS = 6
        NATIVE_W, NATIVE_H = 56, 42
        sw, sh = NATIVE_W * SS, NATIVE_H * SS
        big = pygame.Surface((sw, sh), pygame.SRCALPHA)

        GOLD_HI   = (255, 230, 110)
        GOLD_LO   = (220, 175,  50)
        STROKE    = (110,  75,  10)
        CHROME    = (225, 225, 232)
        SILVER_HI = (245, 245, 252)
        SILVER_LO = (175, 180, 195)
        CREAM     = (255, 245, 200)
        NAVY      = ( 30,  40,  80)
        RED       = (190,  40,  55)
        RED_HI    = (230,  80,  90)

        def vgrad(rect, top_col, bot_col, radius=0):
            tmp = pygame.Surface(rect.size, pygame.SRCALPHA)
            h_ = rect.height
            for y in range(h_):
                t = y / max(1, h_ - 1)
                col = (int(top_col[0] * (1 - t) + bot_col[0] * t),
                       int(top_col[1] * (1 - t) + bot_col[1] * t),
                       int(top_col[2] * (1 - t) + bot_col[2] * t))
                pygame.draw.line(tmp, col, (0, y), (rect.width, y))
            if radius:
                mask = pygame.Surface(rect.size, pygame.SRCALPHA)
                pygame.draw.rect(mask, (255, 255, 255, 255),
                                 mask.get_rect(), border_radius=radius)
                tmp.blit(mask, (0, 0),
                         special_flags=pygame.BLEND_RGBA_MIN)
            big.blit(tmp, rect.topleft)

        def dashed_rect(rect, colour, dash, gap, width):
            def seg(p0, p1):
                x0, y0 = p0
                x1, y1 = p1
                length = math.hypot(x1 - x0, y1 - y0)
                if length <= 0:
                    return
                dx = (x1 - x0) / length
                dy = (y1 - y0) / length
                t = 0.0
                while t < length:
                    t2 = min(t + dash, length)
                    pygame.draw.line(big, colour,
                                     (x0 + dx * t,  y0 + dy * t),
                                     (x0 + dx * t2, y0 + dy * t2),
                                     width)
                    t += dash + gap
            seg((rect.left, rect.top), (rect.right, rect.top))
            seg((rect.right, rect.top), (rect.right, rect.bottom))
            seg((rect.right, rect.bottom), (rect.left, rect.bottom))
            seg((rect.left, rect.bottom), (rect.left, rect.top))

        def silver_cell(rect, radius):
            sub = pygame.Surface(rect.size, pygame.SRCALPHA)
            sub_rect = sub.get_rect()
            tmp = pygame.Surface(rect.size, pygame.SRCALPHA)
            for y in range(rect.height):
                t = y / max(1, rect.height - 1)
                col = (int(SILVER_HI[0] * (1 - t) + SILVER_LO[0] * t),
                       int(SILVER_HI[1] * (1 - t) + SILVER_LO[1] * t),
                       int(SILVER_HI[2] * (1 - t) + SILVER_LO[2] * t))
                pygame.draw.line(tmp, col, (0, y), (rect.width, y))
            mask = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255),
                             mask.get_rect(), border_radius=radius)
            tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            sub.blit(tmp, (0, 0))
            hatch = pygame.Surface(rect.size, pygame.SRCALPHA)
            for off in range(-rect.height, rect.width,
                              max(8, rect.height // 6)):
                pygame.draw.line(hatch, (180, 185, 200, 90),
                                 (off, 0),
                                 (off + rect.height, rect.height),
                                 max(1, rect.height // 60))
            hatch.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            sub.blit(hatch, (0, 0))
            pygame.draw.rect(sub, NAVY, sub_rect,
                             width=max(1, rect.height // 18),
                             border_radius=radius)
            big.blit(sub, rect.topleft)

        def fit_question_mark(panel, text="?", font_frac=0.95,
                               pad_x_frac=0.18, pad_y_frac=0.18):
            max_w = max(1, panel.width
                        - int(panel.width * pad_x_frac * 2))
            max_h = max(1, panel.height
                        - int(panel.height * pad_y_frac * 2))
            size = max(4, int(panel.height * font_frac))
            while size > 6:
                f = _get_float_font(size)
                w_, h_ = f.size(text)
                if w_ <= max_w and h_ <= max_h:
                    break
                size -= 2
            f = _get_float_font(size)
            sh_ = f.render(text, True, STROKE)
            hl  = f.render(text, True, CREAM)
            tx  = f.render(text, True, NAVY)
            tr = tx.get_rect(center=panel.center)
            big.blit(sh_, sh_.get_rect(center=(tr.centerx + 1,
                                                 tr.centery + 1)))
            big.blit(hl, hl.get_rect(center=(tr.centerx,
                                              tr.centery - 1)))
            big.blit(tx, tr)

        card = pygame.Rect(3 * SS, 3 * SS, sw - 6 * SS, sh - 6 * SS)
        vgrad(card, GOLD_HI, GOLD_LO, radius=4 * SS)
        hi_h = card.height // 3
        hi = pygame.Surface((card.width, hi_h), pygame.SRCALPHA)
        for y in range(hi_h):
            a = int(110 * (1.0 - y / hi_h))
            pygame.draw.line(hi, (255, 250, 220, a),
                             (0, y), (hi.get_width(), y))
        big.blit(hi, (card.x, card.y))
        pygame.draw.rect(big, CHROME, card, width=2 * SS,
                         border_radius=4 * SS)
        inner = card.inflate(-4 * SS, -4 * SS)
        dashed_rect(inner, STROKE, dash=4 * SS, gap=3 * SS,
                    width=max(1, SS // 2))

        chip = pygame.Rect(0, 0, 20 * SS, 5 * SS)
        chip.midtop = (inner.centerx, inner.top + 1)
        vgrad(chip, RED_HI, RED, radius=int(SS * 1.5))
        pygame.draw.rect(big, STROKE, chip, max(1, SS // 2),
                         border_radius=int(SS * 1.5))
        fc = _get_float_font(int(chip.height * 0.88))
        sh_ = fc.render("LUCKY", True, STROKE)
        ct  = fc.render("LUCKY", True, CREAM)
        big.blit(sh_, sh_.get_rect(center=(chip.centerx + 1,
                                             chip.centery + 1)))
        big.blit(ct, ct.get_rect(center=chip.center))

        cell_top = chip.bottom + 2 * SS
        cell_bot = inner.bottom - 2 * SS
        cell_h = cell_bot - cell_top
        gap = 1 * SS
        cell_w = (inner.width - 4 * SS - 2 * gap) // 3
        for i in range(3):
            x0 = inner.left + 2 * SS + i * (cell_w + gap)
            cell = pygame.Rect(x0, cell_top, cell_w, cell_h)
            silver_cell(cell, radius=int(SS * 1.5))
            fit_question_mark(cell)

        tilt = math.sin(self.pulse * 0.7) * 5
        rotated = pygame.transform.rotate(big, tilt)
        rw, rh = rotated.get_size()
        final = pygame.transform.smoothscale(rotated, (rw // SS, rh // SS))
        surf.blit(final, final.get_rect(center=(cx, cy)))


# ── Shrink mushroom sprite (sibling to GROW's body sprite) ───────────────────
# Same red velvet palette + cream-butter spots + magenta halo as GROW so
# the two pickups read as one fungal family. Built at supersample then
# smoothscaled and cached.
_SHRINK_SS = 5
_SHRINK_CAP_W,  _SHRINK_CAP_H  = 30, 8
_SHRINK_STEM_W, _SHRINK_STEM_H = 14, 22
_SHRINK_VELVET_OUTLINE = ( 60,  15,  25)
_SHRINK_VELVET_BODY    = MUSH_CAP
_SHRINK_VELVET_HI      = MUSH_CAP2
_SHRINK_SPOT_HALO      = (195, 165, 110)
_SHRINK_STEM_OUTLINE   = (150, 120,  90)
_SHRINK_STEM_HI        = (255, 250, 230)

_SHRINK_ORNAMENT_SLOTS = (
    (0.18, 0.48),
    (0.40, 0.30),
    (0.62, 0.55),
    (0.82, 0.36),
)

_shrink_body_sprite: "pygame.Surface | None" = None

def _get_shrink_body_sprite() -> "pygame.Surface":
    global _shrink_body_sprite
    if _shrink_body_sprite is not None:
        return _shrink_body_sprite
    SS = _SHRINK_SS
    CAP_W, CAP_H = _SHRINK_CAP_W, _SHRINK_CAP_H
    STEM_W, STEM_H = _SHRINK_STEM_W, _SHRINK_STEM_H
    sprite_w = max(CAP_W, STEM_W) + 2
    sprite_h = CAP_H + STEM_H + 4
    big = pygame.Surface((sprite_w * SS, sprite_h * SS), pygame.SRCALPHA)
    cap_ox  = ((sprite_w - CAP_W)  // 2) * SS
    cap_oy  = 0
    stem_ox = ((sprite_w - STEM_W) // 2) * SS
    stem_oy = (CAP_H + 2) * SS

    stem_pts = [
        (int(0.42 * STEM_W * SS), int(0.00 * STEM_H * SS)),
        (int(0.58 * STEM_W * SS), int(0.00 * STEM_H * SS)),
        (int(0.66 * STEM_W * SS), int(0.40 * STEM_H * SS)),
        (int(0.78 * STEM_W * SS), int(0.66 * STEM_H * SS)),
        (int(0.96 * STEM_W * SS), int(0.88 * STEM_H * SS)),
        (int(0.96 * STEM_W * SS), int(1.00 * STEM_H * SS)),
        (int(0.04 * STEM_W * SS), int(1.00 * STEM_H * SS)),
        (int(0.04 * STEM_W * SS), int(0.88 * STEM_H * SS)),
        (int(0.22 * STEM_W * SS), int(0.66 * STEM_H * SS)),
        (int(0.34 * STEM_W * SS), int(0.40 * STEM_H * SS)),
    ]
    stem_pts = [(p[0] + stem_ox, p[1] + stem_oy) for p in stem_pts]
    pygame.draw.polygon(big, MUSH_STEM,            stem_pts)
    pygame.draw.polygon(big, _SHRINK_STEM_OUTLINE, stem_pts, width=SS)
    hi_x = stem_ox + int(0.40 * STEM_W * SS)
    pygame.draw.line(big, _SHRINK_STEM_HI,
                     (hi_x, stem_oy + int(0.10 * STEM_H * SS)),
                     (hi_x, stem_oy + int(0.78 * STEM_H * SS)), SS)

    outer = pygame.Rect(cap_ox, cap_oy, CAP_W * SS, CAP_H * SS)
    inner = outer.inflate(-SS * 2, -SS * 2)
    pygame.draw.ellipse(big, _SHRINK_VELVET_OUTLINE, outer)
    pygame.draw.ellipse(big, _SHRINK_VELVET_BODY,    inner)
    pygame.draw.ellipse(big, _SHRINK_VELVET_HI,
                        pygame.Rect(cap_ox + int(CAP_W * SS * 0.20),
                                    cap_oy + int(CAP_H * SS * 0.10),
                                    int(CAP_W * SS * 0.50),
                                    int(CAP_H * SS * 0.32)))
    pygame.draw.ellipse(big, _SHRINK_VELVET_OUTLINE,
                        pygame.Rect(cap_ox + SS,
                                    cap_oy + int(CAP_H * SS * 0.65),
                                    (CAP_W - 2) * SS,
                                    int(CAP_H * SS * 0.55)))

    for fx_frac, fy_frac in _SHRINK_ORNAMENT_SLOTS:
        fx = cap_ox + int(CAP_W * fx_frac * SS)
        fy = cap_oy + int(CAP_H * fy_frac * SS)
        r_body = 1.7
        pygame.draw.circle(big, _SHRINK_SPOT_HALO, (fx, fy),
                           int((r_body + 0.4) * SS))
        pygame.draw.circle(big, MUSH_SPOT, (fx, fy), int(r_body * SS))
        pygame.draw.circle(big, (255, 250, 220),
                           (fx - SS // 2, fy - SS // 2), max(1, SS // 2))

    _shrink_body_sprite = pygame.transform.smoothscale(big, (sprite_w, sprite_h))
    return _shrink_body_sprite


# Back-compat alias — some callers (e.g. snapshot/playtest scripts) still say Mushroom.
Mushroom = PowerUp


# ── Particle ─────────────────────────────────────────────────────────────────

class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "life_max", "r", "color", "gravity")

    def __init__(self, x, y, vx, vy, life, r, color, gravity=900.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.life_max = life
        self.r = r
        self.color = color
        self.gravity = gravity

    def update(self, dt):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, self.life / self.life_max)
        a = int(255 * t)
        rr = max(1, int(self.r * (0.4 + 0.6 * t)))
        s = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, a), (rr + 1, rr + 1), rr)
        surf.blit(s, (int(self.x - rr - 1), int(self.y - rr - 1)), special_flags=pygame.BLEND_ADD)


# ── CloudPuff ────────────────────────────────────────────────────────────────

class CloudPuff:
    """Expanding, fading cloud circle for the transformation poof effect.
    Uses normal alpha blend (not additive) so it looks like white smoke."""
    __slots__ = ("x", "y", "vx", "vy", "life", "life_max", "r_start", "r_end", "color")

    def __init__(self, x, y, vx, vy, life, r_start, r_end, color):
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.life = self.life_max = life
        self.r_start, self.r_end = r_start, r_end
        self.color = color

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, self.life / self.life_max)          # 1→0 as puff dies
        alpha = int(200 * t)
        r = max(1, int(self.r_start + (self.r_end - self.r_start) * (1.0 - t)))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (r + 1, r + 1), r)
        surf.blit(s, (int(self.x - r - 1), int(self.y - r - 1)))


# ── FloatText ────────────────────────────────────────────────────────────────

_float_font_cache: dict = {}

import os as _os

_FLOAT_FONT_DIR = _os.path.join(_os.path.dirname(__file__), "assets")
_FLOAT_BOLD = _os.path.join(_FLOAT_FONT_DIR, "LiberationSans-Bold.ttf")
# Regular variant retired; see game/hud.py for the rationale. The
# `bold=False` parameter is kept for source-level call-site
# compatibility but all renders now use the Bold face.


def _get_float_font(size, bold=True):
    key = (size, True)
    f = _float_font_cache.get(key)
    if f is None:
        f = pygame.font.Font(_FLOAT_BOLD, size)
        _float_font_cache[key] = f
    return f


class FloatText:
    __slots__ = ("text", "x", "y", "vy", "life", "life_max", "color",
                 "size", "style", "_sparkles")

    def __init__(self, text, x, y, color, size=22, life=1.0, vy=-60,
                 style="plain"):
        self.text = text
        self.x = x
        self.y = y
        self.vy = vy
        self.life = life
        self.life_max = life
        self.color = color
        self.size = size
        self.style = style
        # Pre-computed sparkle offsets (relative to the text center) so
        # they stay stable across frames as the text floats up.
        if style == "powerup":
            rng = random.Random(hash((text, int(x), int(y))) & 0xFFFFFFFF)
            self._sparkles = [
                (rng.randint(-int(size * 1.6), int(size * 1.6)),
                 rng.randint(-int(size * 0.7), int(size * 0.7)))
                for _ in range(8)
            ]
        else:
            self._sparkles = ()

    def update(self, dt):
        self.y += self.vy * dt
        self.vy += 40.0 * dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        if self.style == "powerup":
            self._draw_powerup(surf)
        else:
            self._draw_plain(surf)

    def _draw_plain(self, surf):
        t = max(0.0, self.life / self.life_max)
        a = int(255 * min(1.0, t * 2))
        font = _get_float_font(self.size)
        shadow = font.render(self.text, True, NEAR_BLACK)
        text = font.render(self.text, True, self.color)
        shadow.set_alpha(a)
        text.set_alpha(a)
        r = text.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(shadow, (r.x + 2, r.y + 2))
        surf.blit(text, r.topleft)

    def _draw_powerup(self, surf):
        """Bold gradient fill + thick dark outline + sparkle dots, with the
        gradient derived from `self.color` so each power-up keeps its own
        identity color."""
        life_t = max(0.0, self.life / self.life_max)
        alpha = int(255 * min(1.0, life_t * 2))
        font = _get_float_font(self.size)
        text_surf = font.render(self.text, True, (255, 255, 255))
        bw, bh = text_surf.get_size()
        pad = max(8, self.size // 3)
        comp = pygame.Surface((bw + pad * 2, bh + pad * 2), pygame.SRCALPHA)
        cx = comp.get_width() // 2
        cy = comp.get_height() // 2

        # Drop shadow.
        shadow = font.render(self.text, True, NEAR_BLACK)
        shadow.set_alpha(150)
        comp.blit(shadow, (cx - bw // 2 + 3, cy - bh // 2 + 4))

        # Thick dark outline derived from the base color (lerped toward black).
        col = self.color
        outline_col = (col[0] // 4, col[1] // 4, col[2] // 4)
        outline = font.render(self.text, True, outline_col)
        for ox, oy in ((-3, 0), (3, 0), (0, -3), (0, 3),
                       (-2, -2), (2, -2), (-2, 2), (2, 2)):
            comp.blit(outline, (cx - bw // 2 + ox, cy - bh // 2 + oy))

        # Vertical gradient fill (lighter top → base color bottom),
        # masked to the text shape.
        top_col = (
            int(col[0] + (255 - col[0]) * 0.4),
            int(col[1] + (255 - col[1]) * 0.4),
            int(col[2] + (255 - col[2]) * 0.4),
        )
        grad = pygame.Surface((bw, bh), pygame.SRCALPHA)
        for yy in range(bh):
            t = yy / max(1, bh - 1)
            cc = (
                int(top_col[0] + (col[0] - top_col[0]) * t),
                int(top_col[1] + (col[1] - top_col[1]) * t),
                int(top_col[2] + (col[2] - top_col[2]) * t),
            )
            pygame.draw.line(grad, cc, (0, yy), (bw, yy))
        mask = font.render(self.text, True, (255, 255, 255))
        grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        comp.blit(grad, (cx - bw // 2, cy - bh // 2))

        # Sparkle dots.
        for sx, sy in self._sparkles:
            pygame.draw.circle(comp, (255, 240, 200), (cx + sx, cy + sy), 2)
            pygame.draw.circle(comp, (255, 255, 255), (cx + sx, cy + sy), 1)

        comp.set_alpha(alpha)
        rect = comp.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(comp, rect.topleft)


class FlyingCoinParticle:
    """Full-detail Coin medallion with particle physics. Used by the
    storm jolt so the coins flying off Pip read as the SAME currency
    he just lost — not the smaller doubloons the treasure box uses.
    Wraps an internal Coin so all the gradient / outline / parrot /
    sparkle work is unchanged; this class only adds motion, gravity,
    life, and alpha fade-out."""

    def __init__(self, x, y, vx, vy, *, life=0.95):
        self._coin = Coin(x, y)
        self._coin.spin = random.uniform(0, math.tau)
        self.vx = vx
        self.vy = vy
        self.life = life
        self.life_max = life

    def update(self, dt):
        # Slightly heavier than TreasureCoinParticle so the arc reads
        # like real coins, not a champagne pop.
        self.vy += 800.0 * dt
        self._coin.x += self.vx * dt
        self._coin.y += self.vy * dt
        # Spin faster than a stationary Coin (flung outward = tumbling).
        self._coin.spin = (self._coin.spin + dt * 9.0) % math.tau
        self._coin.float_t += dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, self.life / self.life_max)
        if t >= 0.5:
            # Full opacity during the bright half — draw straight to surf.
            self._coin.draw(surf)
            return
        # Fade phase: render to a transparent buffer, then alpha-blit.
        # Buffer is sized generously so the squeeze + sparkles fit.
        BUF = 48
        scratch = pygame.Surface((BUF, BUF), pygame.SRCALPHA)
        # Trick: temporarily override the coin's x/y to the buffer centre
        # so its own draw places it cleanly inside the scratch surface,
        # then restore.
        saved_x, saved_y = self._coin.x, self._coin.y
        self._coin.x, self._coin.y = BUF // 2, BUF // 2
        self._coin.draw(scratch)
        self._coin.x, self._coin.y = saved_x, saved_y
        scratch.set_alpha(int(255 * (t * 2)))
        surf.blit(scratch, (int(saved_x) - BUF // 2,
                            int(saved_y) - BUF // 2))
