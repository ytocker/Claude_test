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
    UI_GOLD, UI_ORANGE, UI_CREAM,
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


# Key contour points (sprite-rel x, y, depth-weight) along Pip's
# rear upper surface, tail tip → base of neck. He faces +x (right),
# so the tailwind piles snow on everything facing -x. Weight =
# how deep the snow gets there: heaviest on the broad rump/back,
# tapering on the thin tail + the front. Centre = (0,0); sprite is
# 68×64, body bbox x∈[-31,33] y∈[-26,22].
_SNOW_CONTOUR_KEY = (
    (-31.0,  7.0, 0.78),   # tail tip
    (-26.0,  1.0, 0.95),   # tail upper edge
    (-20.0, -3.0, 1.00),   # rump  (deepest)
    (-13.0, -6.6, 1.00),   # back start
    (-6.0,  -7.8, 0.92),   # back hump crest
    (0.0,   -7.4, 0.72),   # back toward neck
    (6.0,   -5.6, 0.40),   # neck base (taper out front)
)
_SNOW_CONTOUR = None       # densely-sampled, built lazily


def _build_snow_contour():
    pts = []
    key = _SNOW_CONTOUR_KEY
    sub = 4
    for i in range(len(key) - 1):
        x0, y0, w0 = key[i]
        x1, y1, w1 = key[i + 1]
        for s in range(sub):
            t = s / sub
            pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t,
                        w0 + (w1 - w0) * t))
    pts.append(key[-1])
    return pts


def _draw_snow_cap(surf, cx, cy, load, scale=1.0, tilt=0.0):
    """Snow over Pip's whole windward rear (tail, rump, back) during
    the squall. Two phases that crossfade with `load` (0..1):

      * Just settling (low load) → a FEW tiny snow specks dotted on
        his rear. (Avoids a thin polygon reading as a drawn line.)
      * Building up → a SOLID accumulated drift: one filled polygon
        whose bottom follows his rear body surface and whose top is
        that surface pushed up by the snow depth (∝ load, deepest
        on the rump/back, gently lumpy), with a soft top highlight
        + cool contact shadow so it reads as real piled snow.

    Depth + opacity scale with load so it accumulates in and melts
    off cleanly. Lumps/specks are deterministic (no per-frame
    randomness → never shimmer). +x is forward, centre (0,0)."""
    global _SNOW_CONTOUR
    load = max(0.0, min(1.0, load))
    if load <= 0.02:
        return
    if _SNOW_CONTOUR is None:
        _SNOW_CONTOUR = _build_snow_contour()
    sc = scale
    cos_t = math.cos(math.radians(tilt))
    sin_t = math.sin(math.radians(tilt))

    def tf(x, y):
        rx = x * cos_t - y * sin_t
        ry = x * sin_t + y * cos_t
        return (cx + rx * sc, cy + ry * sc)

    # Crossfade: specks dominate the early settle; the solid drift
    # fades in as the snow builds (handoff complete by load≈0.40).
    speck_w = max(0.0, min(1.0, (0.40 - load) / 0.30))
    drift_w = max(0.0, min(1.0, (load - 0.20) / 0.20))

    # ── Solid accumulated drift ──────────────────────────────────
    if drift_w > 0.01:
        SS = 3
        maxdepth = 17.0
        bottom, top = [], []
        for i, (x, y, wt) in enumerate(_SNOW_CONTOUR):
            bottom.append(tf(x, y))
            lump = 0.82 + 0.18 * math.cos(i * 0.9) * math.cos(i * 0.37)
            d = load * maxdepth * wt * max(0.2, lump)
            top.append(tf(x - d * 0.22, y - d))
        poly = bottom + top[::-1]
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        minx = min(xs) - 3
        maxx = max(xs) + 3
        miny = min(ys) - 3
        maxy = max(ys) + 6             # pad for the contact shadow
        w = int(maxx - minx)
        h = int(maxy - miny)
        if w >= 2 and h >= 2:
            scratch = pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)

            def to_ss(pts, dy=0.0):
                return [(int((px - minx) * SS), int((py - miny + dy) * SS))
                        for px, py in pts]

            fill_a = int(min(248, 160 + load * 90) * drift_w)
            if fill_a > 4:
                pygame.draw.lines(scratch, (138, 160, 198, int(fill_a * 0.5)),
                                  False, to_ss(bottom, dy=1.8), max(2, 2 * SS))
                pygame.draw.polygon(scratch, (236, 243, 252, fill_a),
                                    to_ss(poly))
                # Soft top highlight — alpha scales with depth so it
                # never reads as a hard drawn line when the drift is
                # still shallow.
                hi_a = int(min(255, fill_a + 6) * min(1.0, load * 1.3))
                if hi_a > 6:
                    pygame.draw.lines(scratch, (255, 255, 255, hi_a),
                                      False, to_ss(top), max(2, 2 * SS))
                small = pygame.transform.smoothscale(scratch, (w, h))
                surf.blit(small, (int(minx), int(miny)))

    # ── Early-settle specks ──────────────────────────────────────
    if speck_w > 0.01:
        n = int(2 + load * 14)
        a = int(min(235, 150 + load * 85) * speck_w)
        if a > 8 and n > 0:
            pts = _SNOW_CONTOUR
            specks = []
            for i in range(n):
                # deterministic spread, biased toward the rear (small t)
                t = ((i * 0.61803398875) % 1.0) ** 1.3
                fi = t * (len(pts) - 1)
                i0 = int(fi)
                f = fi - i0
                x0, y0, _w0 = pts[i0]
                x1, y1, _w1 = pts[min(i0 + 1, len(pts) - 1)]
                bx = x0 + (x1 - x0) * f
                by = y0 + (y1 - y0) * f
                jx = math.cos(i * 2.39) * 2.4
                jy = -1.4 - abs(math.sin(i * 1.71)) * (1.4 + load * 3.0)
                px, py = tf(bx + jx, by + jy)
                rr = max(1, int(round((1.0 + (1 if i % 3 == 0 else 0)) * sc)))
                specks.append((px, py, rr))
            sx = [s[0] for s in specks]
            sy = [s[1] for s in specks]
            rmax = max(s[2] for s in specks)
            ox = int(min(sx) - rmax - 2)
            oy = int(min(sy) - rmax - 2)
            sw = int(max(sx) - min(sx) + 2 * rmax + 4)
            sh = int(max(sy) - min(sy) + 2 * rmax + 4)
            if sw >= 1 and sh >= 1:
                dots = pygame.Surface((sw, sh), pygame.SRCALPHA)
                for px, py, rr in specks:
                    pygame.draw.circle(dots, (255, 255, 255, a),
                                       (int(px - ox), int(py - oy)), rr)
                surf.blit(dots, (ox, oy))


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


# ── Phoenix halos (one per variant) ──────────────────────────────────────────

def _draw_phoenix_fire_halo(surf, x, y, frame_t):
    """Classic / ember / ashes fire halo: 3 concentric circles, layered
    red→orange→gold, pulsing on `frame_t`."""
    halo = pygame.Surface((96, 96), pygame.SRCALPHA)
    cyc = 0.5 + 0.5 * math.sin(frame_t * 0.7)
    base_a = int(90 + 70 * cyc)
    for r_glow, col in (
        (44, (255,  80,  30, base_a // 4)),
        (32, (255, 140,  40, base_a // 2)),
        (22, (255, 210,  90, base_a)),
    ):
        pygame.draw.circle(halo, col, (48, 48), r_glow)
    surf.blit(halo, (x - 48, y - 48))


# Cache for the static (un-rotated) sun-ray template so we only paint it once.
_phoenix_sun_template: "pygame.Surface | None" = None


def _get_phoenix_sun_template() -> "pygame.Surface":
    """8-spoke sun-ray template — rotated per frame in Bird.draw to give
    the impression of a slowly turning halo. Pre-painted once, never
    mutated, so rotating it is cheap."""
    global _phoenix_sun_template
    if _phoenix_sun_template is None:
        size = 108
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2
        # Outer pale-gold rays
        ray_r_outer = 52
        ray_r_inner = 26
        for i in range(8):
            ang = i * (math.tau / 8)
            cos_a, sin_a = math.cos(ang), math.sin(ang)
            # Each ray is a triangle from a small base near the inner
            # ring out to a sharp tip at ray_r_outer.
            tip = (c + cos_a * ray_r_outer, c + sin_a * ray_r_outer)
            # Perpendicular axis for the base width.
            px, py = -sin_a, cos_a
            base_l = (c + cos_a * ray_r_inner + px * 6,
                      c + sin_a * ray_r_inner + py * 6)
            base_r = (c + cos_a * ray_r_inner - px * 6,
                      c + sin_a * ray_r_inner - py * 6)
            pygame.draw.polygon(s, (255, 230, 130, 130), (tip, base_l, base_r))
        _phoenix_sun_template = s
    return _phoenix_sun_template


def _draw_phoenix_solar_halo(surf, x, y, frame_t):
    """Solar halo: rotating 8-spoke sun template + golden core glow +
    orbiting embers around Pip. Reads as 'blessing of the sun.'"""
    tpl = _get_phoenix_sun_template()
    rot = pygame.transform.rotate(tpl, (frame_t * 18) % 360)
    rrect = rot.get_rect(center=(int(x), int(y)))
    surf.blit(rot, rrect.topleft)
    # Golden core
    core = pygame.Surface((44, 44), pygame.SRCALPHA)
    cyc = 0.5 + 0.5 * math.sin(frame_t * 1.3)
    a = int(140 + 60 * cyc)
    pygame.draw.circle(core, (255, 240, 180, a // 2), (22, 22), 20)
    pygame.draw.circle(core, (255, 250, 220, a),      (22, 22), 12)
    surf.blit(core, (int(x) - 22, int(y) - 22))
    # Six orbiting embers on a circular path.
    for i in range(6):
        ang = (frame_t * 1.2 + i * (math.tau / 6)) % math.tau
        ex = x + math.cos(ang) * 30
        ey = y + math.sin(ang) * 30
        pygame.draw.circle(surf, (255, 230, 130), (int(ex), int(ey)), 2)
        pygame.draw.circle(surf, (255, 250, 220), (int(ex), int(ey)), 1)


def _draw_phoenix_mythic_halo(surf, x, y, frame_t):
    """Mythic halo: larger fire halo than classic, with a fourth outer
    ring + denser inner core so the storybook phoenix reads as a bigger
    bird mid-air."""
    halo = pygame.Surface((116, 116), pygame.SRCALPHA)
    cyc = 0.5 + 0.5 * math.sin(frame_t * 0.7)
    base_a = int(110 + 80 * cyc)
    for r_glow, col in (
        (56, (255,  60,  20, base_a // 5)),
        (44, (255, 110,  40, base_a // 3)),
        (32, (255, 170,  60, base_a // 2)),
        (22, (255, 230, 130, base_a)),
    ):
        pygame.draw.circle(halo, col, (58, 58), r_glow)
    surf.blit(halo, (int(x) - 58, int(y) - 58))


def _draw_phoenix_fenghuang_halo(surf, x, y, frame_t):
    """Cooler iridescent halo for the Eastern fenghuang variant —
    teal-blue outer wash with gold inner core, no fiery red. Reads as
    a jeweled aura rather than a fire halo."""
    halo = pygame.Surface((110, 110), pygame.SRCALPHA)
    cyc = 0.5 + 0.5 * math.sin(frame_t * 0.6)
    base_a = int(90 + 70 * cyc)
    for r_glow, col in (
        (52, ( 40,  80, 140, base_a // 4)),
        (40, ( 60, 130, 170, base_a // 3)),
        (28, (110, 200, 210, base_a // 2)),
        (18, (255, 200,  80, base_a)),
    ):
        pygame.draw.circle(halo, col, (55, 55), r_glow)
    surf.blit(halo, (int(x) - 55, int(y) - 55))


def _draw_phoenix_royal_halo(surf, x, y, frame_t):
    """Giant white-hot sunburst halo for the Royal variant — matches
    the in-sprite halo-crown's pure-white core fading to crimson at
    the rim. Larger than every other halo so the bird reads as the
    sun itself."""
    halo = pygame.Surface((140, 140), pygame.SRCALPHA)
    cyc = 0.5 + 0.5 * math.sin(frame_t * 0.7)
    base_a = int(120 + 90 * cyc)
    for r_glow, col in (
        (66, (200,  40,  20, base_a // 6)),
        (54, (255,  90,  30, base_a // 4)),
        (42, (255, 160,  50, base_a // 3)),
        (30, (255, 230, 130, base_a // 2)),
        (18, (255, 250, 220, base_a)),
    ):
        pygame.draw.circle(halo, col, (70, 70), r_glow)
    surf.blit(halo, (int(x) - 70, int(y) - 70))


# ── Hand-painted phoenix pickup body ────────────────────────────────────────
# A proper phoenix silhouette for the in-world pickup: layered flame wings
# sweeping outward, a long flame plume tail, multi-layer crown of fire,
# and a glowing body. Renders at ~48 px tall around (cx, cy) — bigger and
# more detailed than the classic icon so it reads at game resolution.

_PHOENIX_PICKUP_PALETTES = {
    "classic": dict(
        flame=[(120, 18, 26), (215, 55, 30), (255, 130, 40),
               (255, 215, 85), (255, 245, 180)],
        body=[(130, 30, 30), (230, 65, 40), (255, 150, 60), (255, 215, 110)],
        crown=[(240, 100, 30), (255, 200, 80), (255, 245, 180)],
        eye_glow=False,
    ),
    "solar": dict(
        flame=[(180, 95, 30), (240, 170, 50), (255, 220, 100),
               (255, 245, 170), (255, 252, 230)],
        body=[(170, 110, 40), (245, 195, 70), (255, 230, 150), (255, 248, 215)],
        crown=[(220, 150, 50), (255, 220, 110), (255, 252, 230)],
        eye_glow=True,
    ),
}
_PHOENIX_PICKUP_PALETTES["ember"]  = _PHOENIX_PICKUP_PALETTES["classic"]
_PHOENIX_PICKUP_PALETTES["ashes"]  = _PHOENIX_PICKUP_PALETTES["classic"]
_PHOENIX_PICKUP_PALETTES["mythic"] = dict(_PHOENIX_PICKUP_PALETTES["classic"])
_PHOENIX_PICKUP_PALETTES["mythic"]["eye_glow"] = True
_PHOENIX_PICKUP_PALETTES["mythic"]["crown"]    = [
    (220, 80, 30), (255, 180, 70), (255, 252, 220)
]


def _draw_phoenix_pickup_body(surf, cx, cy, variant: str, pulse: float):
    """Hand-painted phoenix pickup silhouette: long flame tail, sweeping
    flame wings, layered crown of fire, and a glowing body — visibly a
    phoenix rather than a tinted parrot. Variant-driven palette swap
    only; layout is shared. Flicker animates via `pulse`."""
    pal = _PHOENIX_PICKUP_PALETTES.get(variant, _PHOENIX_PICKUP_PALETTES["classic"])
    f = pal["flame"]
    b = pal["body"]
    crown = pal["crown"]
    fl = int(math.sin(pulse * 4.0) * 1)        # flame flicker

    # ── 1. Long flame plume tail (multi-layered, trailing back-left)
    # Outermost = deepest crimson, innermost = white-hot.
    tail_layers = [
        (f[0], [(cx - 8, cy - 4), (cx - 24, cy - 8), (cx - 28, cy + 2),
                (cx - 22, cy + 12), (cx - 12, cy + 14), (cx - 6, cy + 8)]),
        (f[1], [(cx - 8, cy - 3), (cx - 20, cy - 5), (cx - 24, cy + 2),
                (cx - 19, cy + 10), (cx - 11, cy + 11), (cx - 6, cy + 7)]),
        (f[2], [(cx - 8, cy - 2), (cx - 16, cy - 2), (cx - 19, cy + 3),
                (cx - 15, cy + 8), (cx - 9, cy + 9), (cx - 6, cy + 5)]),
        (f[3], [(cx - 8, cy - 1), (cx - 12, cy + 0), (cx - 14, cy + 3),
                (cx - 11, cy + 6), (cx - 7, cy + 4)]),
    ]
    for col, pts in tail_layers:
        pygame.draw.polygon(surf, col, pts)
    # White-hot core line through the tail
    pygame.draw.line(surf, f[4], (cx - 22, cy + 3), (cx - 7, cy + 2), 1)
    # Secondary upper plume curling up over the back
    pygame.draw.polygon(surf, f[0], [
        (cx - 5, cy - 6), (cx - 14, cy - 14 + fl), (cx - 9, cy - 6),
    ])
    pygame.draw.polygon(surf, f[1], [
        (cx - 5, cy - 5), (cx - 12, cy - 12 + fl), (cx - 8, cy - 5),
    ])
    pygame.draw.polygon(surf, f[2], [
        (cx - 5, cy - 4), (cx - 10, cy - 10 + fl), (cx - 7, cy - 4),
    ])

    # ── 2. Sweeping flame wings (above and below the body)
    # Upper wing — sweeps up-left
    for col, pts in (
        (f[0], [(cx - 4, cy - 2), (cx + 4, cy - 14 - fl),
                (cx + 12, cy - 18 - fl), (cx + 14, cy - 10),
                (cx + 6, cy - 6), (cx, cy - 4)]),
        (f[1], [(cx - 2, cy - 2), (cx + 5, cy - 12 - fl),
                (cx + 11, cy - 14 - fl), (cx + 12, cy - 8),
                (cx + 5, cy - 5), (cx, cy - 4)]),
        (f[2], [(cx + 0, cy - 2), (cx + 6, cy - 10 - fl),
                (cx + 10, cy - 11 - fl), (cx + 10, cy - 6),
                (cx + 4, cy - 5)]),
        (f[3], [(cx + 1, cy - 2), (cx + 7, cy - 8 - fl),
                (cx + 9, cy - 8 - fl), (cx + 6, cy - 4)]),
    ):
        pygame.draw.polygon(surf, col, pts)
    # Lower wing — sweeps down-left
    for col, pts in (
        (f[0], [(cx - 2, cy + 4), (cx + 6, cy + 14 + fl),
                (cx + 13, cy + 12 + fl), (cx + 12, cy + 4),
                (cx + 4, cy + 2)]),
        (f[1], [(cx + 0, cy + 4), (cx + 7, cy + 11 + fl),
                (cx + 11, cy + 9 + fl), (cx + 10, cy + 4)]),
        (f[2], [(cx + 2, cy + 4), (cx + 7, cy + 8 + fl),
                (cx + 9, cy + 7 + fl), (cx + 8, cy + 4)]),
    ):
        pygame.draw.polygon(surf, col, pts)

    # ── 3. Body (molten-gold gradient)
    pygame.draw.ellipse(surf, b[0], pygame.Rect(cx - 11, cy - 5, 22, 16))
    pygame.draw.ellipse(surf, b[1], pygame.Rect(cx - 10, cy - 4, 20, 14))
    pygame.draw.ellipse(surf, b[2], pygame.Rect(cx -  8, cy - 3, 14,  9))
    pygame.draw.ellipse(surf, b[3], pygame.Rect(cx -  6, cy + 0, 10,  6))

    # ── 4. Head (tucked above and slightly forward of the body)
    pygame.draw.ellipse(surf, b[0], pygame.Rect(cx + 2, cy - 12, 14, 13))
    pygame.draw.ellipse(surf, b[1], pygame.Rect(cx + 3, cy - 11, 12, 11))
    pygame.draw.ellipse(surf, b[2], pygame.Rect(cx + 4, cy - 10,  7,  5))

    # ── 5. Multi-layer crown of fire above the head
    for fx_off, fy_top, hw, hh in (
        (cx + 9, cy - 22 + fl, 4, 10),  # tallest centre
        (cx + 5, cy - 18 + fl, 3,  7),
        (cx + 13, cy - 18 + fl, 3, 7),
        (cx + 2, cy - 14 + fl, 2,  4),
        (cx + 16, cy - 14 + fl, 2, 4),
    ):
        base_y = fy_top + hh
        pygame.draw.polygon(surf, crown[0], [
            (fx_off - hw, base_y), (fx_off + hw, base_y), (fx_off, fy_top)])
        pygame.draw.polygon(surf, crown[1], [
            (fx_off - max(1, hw - 1), base_y - 1),
            (fx_off + max(1, hw - 1), base_y - 1),
            (fx_off, fy_top + 3)])
        pygame.draw.polygon(surf, crown[2], [
            (fx_off - max(1, hw // 2), base_y - 2),
            (fx_off + max(1, hw // 2), base_y - 2),
            (fx_off, fy_top + 5)])

    # ── 6. Eye (with optional glow)
    pygame.draw.circle(surf, (255, 250, 220), (cx + 10, cy - 7), 2)
    pygame.draw.circle(surf, ( 20,  10,  10), (cx + 10, cy - 7), 1)
    if pal.get("eye_glow"):
        glow = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 240, 160, 220), (5, 5), 4)
        pygame.draw.circle(glow, (255, 255, 230, 255), (5, 5), 2)
        surf.blit(glow, (cx + 10 - 5, cy - 7 - 5),
                  special_flags=pygame.BLEND_RGBA_ADD)

    # ── 7. Beak
    pygame.draw.polygon(surf, (255, 200, 60), [
        (cx + 14, cy - 6), (cx + 18, cy - 5), (cx + 14, cy - 3)])
    pygame.draw.polygon(surf, ( 140, 90, 20), [
        (cx + 14, cy - 6), (cx + 18, cy - 5), (cx + 14, cy - 3)], 1)

    # ── 8. Body ember sparks
    for ox, oy in ((-8, -8), (-2, -10), (6, -8), (12, 0),
                   (10, 8), (-2, 12), (-14, 6), (-18, -2)):
        pygame.draw.circle(surf, f[3], (cx + ox, cy + oy), 1)


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

# Cache of vertical gradient surfaces keyed on (width, height, top, bot)
# rounded to 0.02 so we don't churn the cache as biome phase ticks. ~50
# entries max per typical sprite size.
_LIGHT_GRADIENT_CACHE: "dict[tuple, pygame.Surface]" = {}


def _get_light_gradient(w: int, h: int,
                       top: float, bot: float) -> pygame.Surface:
    """Vertical gradient surface (w x h): top row at brightness `top`,
    bottom row at brightness `bot`, linear interp between. Used as a
    BLEND_RGBA_MULT mask so the sprite's RGB is multiplied by the
    gradient. Cached by quantised (top, bot) so building is one-shot
    per bucket."""
    key = (w, h, round(top, 2), round(bot, 2))
    cached = _LIGHT_GRADIENT_CACHE.get(key)
    if cached is not None:
        return cached
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    # Per-scanline solid colour — one horizontal line per row, so this
    # stays O(h) draw calls instead of O(w*h) set_at calls.
    inv_h = 1.0 / max(1, h - 1)
    for y in range(h):
        t = y * inv_h
        v = top + (bot - top) * t
        v = max(0.0, min(1.0, v))
        c = int(255 * v)
        pygame.draw.line(grad, (c, c, c, 255), (0, y), (w - 1, y))
    _LIGHT_GRADIENT_CACHE[key] = grad
    return grad


def _apply_ambient_light(sprite: pygame.Surface,
                         top_level: float,
                         bot_level: float) -> pygame.Surface:
    """Return a copy of `sprite` whose RGB is multiplied by a vertical
    gradient — `top_level` at the top edge, `bot_level` at the bottom,
    interpolated per row. This produces a directional shadow (light
    from above) instead of a flat uniform darken; reads as natural
    dusk/night shading where the top of Pip still catches the
    skylight but his underside falls into shadow. Alpha is preserved
    via the gradient's alpha=255, so the silhouette stays crisp."""
    if top_level >= 0.999 and bot_level >= 0.999:
        return sprite
    out = sprite.copy()
    w, h = out.get_size()
    grad = _get_light_gradient(w, h, top_level, bot_level)
    out.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return out


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
        # Visual scale eases toward GROW_SCALE while grow_active and back
        # to 1.0 when it clears. Collisions snap; only the visible sprite eases.
        self.grow_scale = 1.0
        self.triple_active = False
        self.ghost_pulse = 0.0    # advances while ghost_active for fade effect
        # Secret late-game powerup flags (timer state lives on World).
        self.skateboard_active = False
        # PHOENIX: fiery skin while phoenix_active; the death-revive is
        # owned by World._die().
        self.phoenix_active = False
        # Backflip trick: ticks down while a 360° spin animation plays.
        self.backflip_t = 0.0
        self.backflip_dur = 0.0
        # Kickflip trick (2 slow taps): the deck spins 360° under Pip
        # while he stays upright. Animation is shorter than backflip
        # so the trick feels like a quick board-flick, not a body spin.
        self.kickflip_t = 0.0
        self.kickflip_dur = 0.0
        # Heelflip trick (2 very-slow taps): mirror of the kickflip —
        # the deck spins 360° in the OPPOSITE direction.
        self.heelflip_t = 0.0
        self.heelflip_dur = 0.0
        # Pop Shuvit trick (2 medium taps): the deck does a 180° flat-
        # spin around its vertical axis. Visual is a horizontal
        # scale-X = cos(p·π) on the rendered board.
        self.popshuvit_t = 0.0
        self.popshuvit_dur = 0.0
        # Random-grind: when Pip lands on the ground / a pillar top
        # in skateboard mode, World rolls a 0.25 probability and
        # picks one of {'nose', 'tail'}; the board+Pip tilt
        # ∓15° to fake a nose-only / tail-only grind. Cleared
        # when Pip lifts off the surface.
        self.grind_type = None
        # Weather → Pip. World writes shiver_x/y (visual jitter under heavy
        # rain / lightning) and flap_dampen (0..WEATHER_FLAP_DAMPEN_MAX,
        # subtracted from FLAP_V on the next tap so storms feel like the
        # wind is pushing Pip down).
        self.shiver_x = 0.0
        self.shiver_y = 0.0
        self.flap_dampen = 0.0
        # Headwind lean — leftward visual x-offset (negative)
        # written by World._apply_weather_effects each frame
        # while the predawn wind event is active. Visual-only;
        # collisions use Bird.x which stays at BIRD_X.
        self.wind_lean = 0.0
        # Snow accumulation on Pip's back during the snow squall
        # (0..1). Integrated by World from storm intensity — lags
        # the storm so it keeps building a little past the peak,
        # then melts off. Drives the snow-drift overlay in draw().
        self.snow_load = 0.0
        # X-Ray Sparks flash. Set to 0.5 s by World._fire_storm_jolt
        # when the real strike lands on Pip; Bird.draw alternates Pip's
        # sprite between the normal frame and a skeleton-overlay frame
        # at ~10 Hz while this timer is > 0.
        self.skeleton_flash_t = 0.0

    @property
    def tilt_deg(self):
        t = max(-0.5, min(0.75, self.vy / 500.0))
        base = -t * 55.0
        # GRIND: while a random grind is active, tilt Pip's whole
        # body so it matches the board (nose down for a nose grind,
        # nose up for a tail grind). ±18° was the version that
        # "looked better" before the upright + parrot-legs detour.
        if self.grind_type == "nose":
            base += -18.0
        elif self.grind_type == "tail":
            base += 18.0
        # During a backflip, ride a full 360° rotation on top of the base
        # tilt. pygame's rotate is modulo-360 internally so values beyond
        # the normal clamp are fine.
        # Smootherstep easing (6t⁵ − 15t⁴ + 10t³) — zero acceleration at
        # both endpoints — so the spin eases in (slow start), ramps
        # through 180° at the midpoint, then eases out. The flat tail
        # also closes the 360° loop to within ~0.03° at the last frame,
        # so the post-flip transition back to velocity-banked posture
        # is visually seamless ("lands on Pip's normal posture").
        # The velocity-banked `base` term is also blended OUT as the
        # flip progresses (`base_blend = 1 - eased`) so Pip exits the
        # spin in a flat horizontal posture rather than nose-down
        # under a falling vy.
        if self.backflip_t > 0 and self.backflip_dur > 0:
            p = 1.0 - self.backflip_t / self.backflip_dur
            eased = p * p * p * (p * (p * 6.0 - 15.0) + 10.0)
            return base * (1.0 - eased) + eased * 360.0
        return base

    def flap(self, gravity_sign=1):
        if self.alive:
            self.vy = FLAP_V * (1.0 - self.flap_dampen) * gravity_sign
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
        self.backflip_t = max(0.0, self.backflip_t - dt)
        self.kickflip_t = max(0.0, self.kickflip_t - dt)
        self.heelflip_t = max(0.0, self.heelflip_t - dt)
        self.popshuvit_t = max(0.0, self.popshuvit_t - dt)
        self.skeleton_flash_t = max(0.0, self.skeleton_flash_t - dt)
        if self.ghost_active:
            self.ghost_pulse += dt * 2.4

        from game.config import GROW_SCALE, GROW_TRANSITION
        target_g = GROW_SCALE if self.grow_active else 1.0
        step_g = (GROW_SCALE - 1.0) * (dt / GROW_TRANSITION)
        if self.grow_scale < target_g:
            self.grow_scale = min(target_g, self.grow_scale + step_g)
        elif self.grow_scale > target_g:
            self.grow_scale = max(target_g, self.grow_scale - step_g)

    def draw(self, surf, shake_x=0, shake_y=0, flipped=False,
             light_level=1.0, light_gradient=None):
        from game.config import GROW_SCALE
        # Weather shiver: world-driven per-frame jitter under heavy rain /
        # lightning. Visual only — kept out of the physics shake_x/shake_y
        # path so collision is unaffected.
        shake_x += self.shiver_x + self.wind_lean
        shake_y += self.shiver_y
        frame_idx = int(self.frame_t) % len(parrot.FRAMES)
        # When flipped (reverse-gravity buff), negate the tilt so a rising
        # bird's head still leads in the direction of motion after the
        # vertical mirror is applied below.
        tilt = -self.tilt_deg if flipped else self.tilt_deg
        has_combo = (self.kfc_active or self.ghost_active or self.triple_active)
        # Hi-res grow sprite is only valid when at the GROW_SCALE peak AND
        # no combo overlay is active. Mid-transition or combo'd, we fall
        # through to the normal base sprite and smoothscale it by the eased
        # grow_scale so the size change reads as a transformation rather
        # than a teleport.
        use_grow_hires = (not has_combo
                          and self.grow_scale >= GROW_SCALE - 1e-3)
        # Combo-aware sprite cascade. The four reachable stacks each have
        # a dedicated themed sprite so no powerup is silently lost; check
        # combos before single-mode flags so e.g. kfc+triple picks the
        # crispy-hat sprite instead of falling through to plain kfc.
        # X-RAY SPARKS wins over EVERYTHING (including phoenix) — the
        # storm-jolt strike is a special, momentary event and during
        # the 3.5 s flash Pip's normal/powered-up identity is
        # overridden by the classic Looney-Tunes electrocution
        # silhouette. Two-phase timing:
        #   * First 0.5 s — SOLID skeleton hold (no strobe) so the
        #     X-ray view is unmistakably readable.
        #   * Last 3.0 s — slow strobe with 0.30 s per segment
        #     (same frequency as before, just longer total period):
        #     10 segments alternating skel/norm/skel/norm/.../norm
        #     so the player clearly sees Pip swap between his
        #     skeleton and his normal sprite FIVE full times before
        #     the flash releases into scorch wisps.
        skeleton_visible = False
        if self.skeleton_flash_t > 0.0:
            if self.skeleton_flash_t > 3.0:
                # Solid hold phase — first 0.5 s of the 3.5 s window
                skeleton_visible = True
            else:
                # Strobe phase — last 3.0 s, segment = 0.30 s
                elapsed_strobe = 3.0 - self.skeleton_flash_t
                bucket = int(elapsed_strobe / 0.30)
                skeleton_visible = (bucket % 2 == 0)
        if skeleton_visible:
            img = parrot.get_skeleton_parrot(frame_idx, tilt)
        elif self.phoenix_active:
            img = parrot.get_phoenix_parrot(frame_idx, tilt)
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
        elif use_grow_hires:
            # Hi-res grow-mode bird: pre-built at full grow display size
            # by `parrot._build_grow_frame` (round-9 v3 = 3× supersample
            # → 1.5× downscale). Used only at the GROW_SCALE peak so the
            # smoothscale-up blur is avoided once the transition completes.
            img = parrot.get_grow_parrot(frame_idx, tilt)
        else:
            img = parrot.get_parrot(frame_idx, tilt)
        if self.grow_scale > 1.0 and not use_grow_hires:
            # Mid-transition (any sprite) or peak + combo (no hi-res combo
            # frames yet): smoothscale by the eased grow_scale.
            w, h = img.get_size()
            s = self.grow_scale
            img = pygame.transform.smoothscale(img, (int(w * s), int(h * s)))
        if flipped:
            img = pygame.transform.flip(img, False, True)
        if self.ghost_active and not skeleton_visible:
            # Faded breathing: alpha oscillates ~90..170 over a slow sine,
            # so the ghost reads as clearly translucent and ethereal.
            # Suppressed during the X-Ray Sparks flash — the bright bone
            # silhouette should read at full opacity even if Pip is
            # currently in ghost mode.
            img = img.copy()
            pulse = 0.5 + 0.5 * math.sin(self.ghost_pulse)
            img.set_alpha(int(90 + pulse * 80))
        # PHOENIX: halo style varies by PHOENIX_VARIANT.
        #   classic / ember / ashes — layered red→orange→gold fire halo.
        #   solar  — rotating 8-spoke sun ray + gold core, plus orbiting
        #            embers around Pip.
        #   mythic — bigger, more saturated fire halo with extra outer
        #            ring so the storybook phoenix reads as larger-than-life.
        if self.phoenix_active and self.skeleton_flash_t <= 0.0:
            from game.config import PHOENIX_VARIANT as _PV
            hx, hy = self.x + shake_x, self.y + shake_y
            if _PV == "solar":
                _draw_phoenix_solar_halo(surf, hx, hy, self.frame_t)
            elif _PV in ("mythic", "imperial", "blaze", "sunburst",
                         "twin", "swift", "grand",
                         "soar", "rise", "stoop", "dive", "eternal",
                         "eternal_warm", "eternal_soft", "eternal_dawn",
                         "eternal_friend", "eternal_lite"):
                # Imperial + fire-fenghuang hybrids + wide-wing v2
                # + less-creepy Eternal iterations share the mythic halo.
                _draw_phoenix_mythic_halo(surf, hx, hy, self.frame_t)
            elif _PV == "fenghuang":
                _draw_phoenix_fenghuang_halo(surf, hx, hy, self.frame_t)
            elif _PV == "royal":
                _draw_phoenix_royal_halo(surf, hx, hy, self.frame_t)
            elif _PV in ("dragon", "comet"):
                # Dragon and Comet skip the halo — Dragon has its own
                # flame mane in-sprite, Comet's trail particles cover
                # the same visual role.
                pass
            else:  # classic / ember / ashes
                _draw_phoenix_fire_halo(surf, hx, hy, self.frame_t)
        cx_int = int(self.x + shake_x)
        cy_int = int(self.y + shake_y)
        # X-Ray Sparks rim glow — a TIGHT coloured trim drawn
        # directly on Pip's silhouette edge using the boundary
        # points from pygame.mask.from_surface(img).outline().
        # No dilation, no offset blits, no halo rings — just a
        # multi-stroke polyline centred on the silhouette contour
        # so only ~half of each stroke shows outside Pip's body
        # (the inner half is covered when his sprite blits on
        # top). 3 stacked widths give a coloured gradient rim:
        # outer purple → cyan → bright white core. Pulse-modulated
        # alpha at ~5 Hz for the electric breathing. Drawn BEFORE
        # the bird sprite so the inner half of each stroke is
        # cleanly hidden by the blit.
        rect_pre = img.get_rect(center=(cx_int, cy_int))
        if self.skeleton_flash_t > 0.0:
            pulse = 0.5 + 0.5 * math.sin(self.frame_t * 30.0)
            try:
                sil_mask = pygame.mask.from_surface(img, threshold=20)
                outline_pts = sil_mask.outline(every=1)
                if len(outline_pts) >= 2:
                    base_x, base_y = rect_pre.topleft
                    # Render strokes into a scratch SRCALPHA surface
                    # sized to the sprite so we can apply a single
                    # pulse alpha across the whole rim coherently.
                    glow = pygame.Surface(img.get_size(),
                                          pygame.SRCALPHA)
                    # Closed polyline along the silhouette contour
                    for width, col in (
                        (5, (180, 100, 255)),  # outer purple glow
                        (3, (140, 220, 255)),  # cyan mid
                        (1, (255, 255, 255)),  # bright white core
                    ):
                        pygame.draw.lines(glow, col, True,
                                          outline_pts, width)
                    a_pulsed = int(220 * (0.6 + 0.4 * pulse))
                    glow.set_alpha(max(0, min(255, a_pulsed)))
                    surf.blit(glow, (base_x, base_y))
            except (pygame.error, AttributeError):
                # Older pygame builds without mask.outline — skip
                # the aura rather than fall back to circles (which
                # is exactly the look we're moving AWAY from).
                pass
        # Biome ambient-light: vertical-gradient multiply onto Pip's
        # sprite so the top edge catches more light and the underside
        # falls into shadow. Falls back to a uniform tint if only the
        # legacy `light_level` scalar was passed.
        if light_gradient is not None:
            top_l, bot_l = light_gradient
            if top_l < 0.999 or bot_l < 0.999:
                img = _apply_ambient_light(img, top_l, bot_l)
        elif light_level < 0.999:
            img = _apply_ambient_light(img, light_level, light_level)
        r = img.get_rect(center=(cx_int, cy_int))
        surf.blit(img, r.topleft)
        # Snow drift on Pip's back — the tailwind deposits snow on
        # his dorsal surface during the squall. Drawn right on top
        # of the body sprite (below helmet/parcel), scaled by the
        # current grow_scale so it tracks his size.
        if self.snow_load > 0.02 and not skeleton_visible:
            _draw_snow_cap(surf, cx_int, cy_int, self.snow_load,
                           self.grow_scale, tilt)
        # X-Ray Sparks ARCS — longer jagged mini-bolts crackling
        # OUTWARD from Pip's silhouette while the flash timer is
        # active. Each arc starts on the silhouette perimeter and
        # zig-zags ~10-14 px outward with random perpendicular
        # jitter — reads as real electricity discharging from his
        # body rather than static sparkles. Drawn AFTER the bird
        # sprite so they pop on top of the silhouette + aura. New
        # angles each frame so the discharge feels alive.
        if self.skeleton_flash_t > 0.0:
            n_arcs = 5
            inner_r = 20.0
            for k in range(n_arcs):
                ang = random.uniform(0, math.tau)
                # Start at silhouette perimeter
                ox = cx_int + math.cos(ang) * inner_r
                oy = cy_int + math.sin(ang) * inner_r
                # End point outward: 10-14 px further
                end_r = inner_r + random.uniform(10, 14)
                ex = cx_int + math.cos(ang) * end_r
                ey = cy_int + math.sin(ang) * end_r
                # Midpoint with perpendicular jitter for zig-zag
                mid_r = (inner_r + end_r) * 0.5
                perp = ang + math.pi / 2
                jitter = random.uniform(-3.5, 3.5)
                mx = (cx_int + math.cos(ang) * mid_r
                      + math.cos(perp) * jitter)
                my = (cy_int + math.sin(ang) * mid_r
                      + math.sin(perp) * jitter)
                # 2-segment mini-bolt: cyan outer + white core
                pts = ((int(ox), int(oy)), (int(mx), int(my)),
                       (int(ex), int(ey)))
                pygame.draw.lines(surf, (140, 220, 255), False,
                                  pts, 3)
                pygame.draw.lines(surf, (255, 255, 255), False,
                                  pts, 1)
                # Bright tip glint at the discharge end
                pygame.draw.circle(surf, (255, 255, 255),
                                   (int(ex), int(ey)), 2)
                pygame.draw.circle(surf, (140, 220, 255),
                                   (int(ex), int(ey)), 3, 1)
        # SKATEBOARD helmet — a small dome on top of Pip's head with a chinstrap.
        if self.skateboard_active:
            self._draw_helmet(surf, self.x + shake_x, self.y + shake_y, flipped)

        # Parcel — Pip's permanent companion. Tucked below his centre with
        # a tilt-aware offset so it banks with him; mode-coloured to match
        # the active palette; alpha-breathes in ghost mode; grow-scaled.
        # SKATEBOARD: parcel transforms into a tiny skateboard. The original
        # parcel hitbox is disabled in world.py for the duration.
        if self.skateboard_active:
            self._draw_skateboard(surf, self.x + shake_x, self.y + shake_y, flipped)
            return
        if self.kfc_active:
            mode = "kfc"
        elif self.ghost_active:
            mode = "ghost"
        elif self.triple_active:
            mode = "triple"
        else:
            mode = "normal"
        parcel = parrot.get_parcel(mode)
        from game.config import PARCEL_Y_OFFSET
        scale = self.grow_scale
        if scale != 1.0:
            pw, ph = parcel.get_size()
            parcel = pygame.transform.smoothscale(
                parcel, (max(1, int(pw * scale)), max(1, int(ph * scale))))
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
        if self.ghost_active:
            parcel_rot = parcel_rot.copy()
            parcel_rot.set_alpha(int(90 + pulse * 80))
        # Darken the parcel under the same ambient light as the bird so
        # the pair reads as one silhouette under shared lighting.
        if light_gradient is not None:
            top_l, bot_l = light_gradient
            if top_l < 0.999 or bot_l < 0.999:
                parcel_rot = _apply_ambient_light(
                    parcel_rot, top_l, bot_l)
        elif light_level < 0.999:
            parcel_rot = _apply_ambient_light(
                parcel_rot, light_level, light_level)
        pr = parcel_rot.get_rect(center=(self.x + shake_x + offset.x,
                                         self.y + shake_y + offset.y))
        surf.blit(parcel_rot, pr.topleft)

    # ── Secret-powerup wearable overlays ────────────────────────────────────
    def _draw_helmet(self, surf, cx, cy, flipped):
        """Side-view punk-mohawk skater helmet (variant 4 from the
        v5_powerups design pass) — half-dome with a flat horizontal
        rim, a single bone fin running front-to-back along the top,
        chrome rim band, side skull decal, and a single FRONT-temple
        chinstrap dropping past the cheek to a buckle UNDER the chin.
        Palette kit-matched to `_draw_skateboard`:
          • dome fill / vent / outlines = deck fill   (10, 10, 18)
          • dome highlight              = wheel ring  (50, 50, 60)
          • chrome rim band             = deck outline (200, 200, 210)
          • bone fin / skull            = deck skull  (240, 240, 230)
          • chinstrap                   = OUT (15, 15, 22) — matches dome
          • adjuster / clip outline     = chrome     (200, 200, 210)
          • side-release clip body      = wheel centre (200, 50, 50)
        Anchor (+18, -10) chosen by self-critique iteration so the
        helmet sits naturally on Pip's crown. The helm surface is
        extended below the rim (drop=28) so the chinstrap can route
        past the jaw to a buckle at Pip's chin without clipping.

        4× SUPERSAMPLE: all painting happens at 4× resolution, the
        rotated result is smoothscale'd down before blit. Gives
        anti-aliased edges on the dome curve, mohawk fin polygon,
        skull decal ellipse, chinstrap lines and clip — much
        smoother than pixel-snapped pygame primitives at the native
        24×15 helm size."""
        s = 1.0
        SS = 4  # supersample factor
        # Logical (native) dimensions — coords below are conceptual
        # and get multiplied by SS for the actual paint surface.
        hw_n = int(24 * s)
        hh_n = int(15 * s)
        pad_n = 4
        drop_n = int(28 * s)
        # Supersampled paint dimensions.
        hw = hw_n * SS
        hh = hh_n * SS
        pad = pad_n * SS
        drop = drop_n * SS
        helm = pygame.Surface(
            (hw + pad * 2, hh + pad * 2 + drop), pygame.SRCALPHA)

        # Top-half dome — flat horizontal rim line at y = pad + hh.
        # Drawing the ellipse at 4× resolution produces a much
        # smoother curve before smoothscale-down.
        full = pygame.Surface((hw, hh * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(full, (10, 10, 18),
                            pygame.Rect(0, 0, hw, hh * 2))
        helm.blit(full, (pad, pad), area=pygame.Rect(0, 0, hw, hh))
        # Forward-upper-quadrant highlight only — Pip faces right.
        if hw > 9 * SS and hh > 5 * SS:
            hl_w = hw - 8 * SS
            hl_h = hh - 4 * SS
            hl = pygame.Surface((hl_w, hl_h), pygame.SRCALPHA)
            pygame.draw.ellipse(hl, (50, 50, 60),
                                pygame.Rect(0, 0, hl_w, hl_h))
            helm.blit(hl, (pad + 4 * SS, pad + 1 * SS),
                      area=pygame.Rect(hl_w // 2, 0,
                                       hl_w // 2, hl_h // 2 + 1))

        # Bone mohawk fin — SINGLE side-profile sail running front to
        # back along the dome top. Polygon vertices upscaled SS.
        fin = [
            (pad + 3 * SS,             pad + 1 * SS),
            (pad + hw // 2 - 2 * SS,   pad - 3 * SS),
            (pad + hw // 2 + 3 * SS,   pad - 2 * SS),
            (pad + hw - 4 * SS,        pad + 2 * SS),
        ]
        pygame.draw.polygon(helm, (240, 240, 230), fin)
        pygame.draw.polygon(helm, (10, 10, 18), fin, SS)
        for sx in (pad + hw // 2 - 3 * SS, pad + hw // 2 + 2 * SS):
            spike = [(sx, pad - 2 * SS),
                     (sx + 1 * SS, pad - 5 * SS),
                     (sx + 2 * SS, pad - 2 * SS)]
            pygame.draw.polygon(helm, (240, 240, 230), spike)
            pygame.draw.polygon(helm, (10, 10, 18), spike, SS)

        # Single side vent on the visible panel.
        pygame.draw.line(helm, (10, 10, 18),
                         (pad + hw // 2 - 2 * SS, pad + hh - 3 * SS),
                         (pad + hw // 2 + 2 * SS, pad + hh - 3 * SS), SS)
        # Chrome rim band — straight horizontal at the rim line.
        pygame.draw.rect(helm, (200, 200, 210),
                         pygame.Rect(pad - 1 * SS, pad + hh - 1 * SS,
                                     hw + 2 * SS, 2 * SS))
        # Side skull decal near the rear of the dome.
        sk_w = max(3 * SS, int(5 * s * SS))
        sk_h = max(2 * SS, int(4 * s * SS))
        sk = pygame.Rect(0, 0, sk_w, sk_h)
        sk.center = (pad + hw // 2 - 5 * SS, pad + hh - 4 * SS)
        pygame.draw.ellipse(helm, (240, 240, 230), sk)
        pygame.draw.ellipse(helm, (10, 10, 18), sk, SS)

        # Chinstrap — N4 from commit 8464059 + R5 right strap.
        # Coords at native resolution then multiplied by SS.
        OUT     = (15, 15, 22)
        CHROME  = (200, 200, 210)
        BUCKLE  = (200, 50, 50)
        STRAP   = OUT
        rim_y = pad + hh + 1 * SS
        front_anchor = (8 * SS, rim_y)
        rear_anchor  = (4 * SS, rim_y)
        junction     = (6 * SS, 30 * SS)
        clip_centre  = (14 * SS, 37 * SS)
        pygame.draw.line(helm, STRAP, front_anchor, junction, 2 * SS)
        pygame.draw.line(helm, STRAP, rear_anchor,  junction, 2 * SS)
        pygame.draw.line(helm, STRAP, junction, clip_centre, 2 * SS)
        # Plastic adjuster slider at the ear junction.
        adj = pygame.Rect(junction[0] - 1 * SS, junction[1] - 1 * SS,
                          3 * SS, 2 * SS)
        pygame.draw.rect(helm, (30, 30, 40), adj)
        pygame.draw.rect(helm, CHROME, adj, SS)
        # Side-release clip at the chin.
        clip = pygame.Rect(clip_centre[0] - 2 * SS,
                           clip_centre[1] - 2 * SS, 5 * SS, 4 * SS)
        pygame.draw.rect(helm, BUCKLE, clip)
        pygame.draw.rect(helm, OUT, clip, SS)
        pygame.draw.line(helm, OUT,
                         (clip.x + 2 * SS, clip.y),
                         (clip.x + 2 * SS, clip.bottom - 1 * SS), SS)
        # RIGHT chinstrap (R5).
        pygame.draw.line(helm, STRAP, clip_centre, (22 * SS, 35 * SS),
                         2 * SS)

        # Anchor block — first scale helm DOWN to native resolution
        # (smoothscale gives the anti-aliased edges), then rotate
        # and blit as before. Rotating after scale-down keeps the
        # surface size small for the transform.
        native_size = (hw_n + pad_n * 2,
                       hh_n + pad_n * 2 + drop_n)
        helm = pygame.transform.smoothscale(helm, native_size)
        tilt = -self.tilt_deg if flipped else self.tilt_deg
        y_off = 10 * s if flipped else -10 * s
        offset = pygame.math.Vector2(18 * s, y_off)
        offset = offset.rotate(-tilt)
        rotated = pygame.transform.rotate(helm, tilt)
        if flipped:
            rotated = pygame.transform.flip(rotated, False, True)
        r = rotated.get_rect(center=(int(cx + offset.x),
                                     int(cy + offset.y)))
        surf.blit(rotated, r.topleft)

    def _draw_skateboard(self, surf, cx, cy, flipped):
        """Skull skateboard under Pip's feet — black deck with a chrome
        outline, white skull centred, white crossbones diagonals. Cream
        wheels with red bullseye. Matches the skull helmet (kit).

        4× SUPERSAMPLE — same approach as `_draw_helmet`. The deck's
        rounded corners, the skull ellipse, the wheel circles, the
        crossbone diagonals all benefit from the smoother curves /
        anti-aliased edges that come from painting at 4× then
        smoothscale-down.
        """
        from game.config import PARCEL_Y_OFFSET
        s = 1.0
        SS = 4
        # Native (logical) dimensions.
        board_w_n = int(48 * s)
        deck_h_n  = max(4, int(7 * s))
        pad_n     = 10
        native_w  = board_w_n + pad_n * 2
        native_h  = deck_h_n * 5 + pad_n * 2
        # Supersampled paint dimensions.
        board_w = board_w_n * SS
        deck_h  = deck_h_n * SS
        pad     = pad_n * SS

        y_off = -PARCEL_Y_OFFSET * s if flipped else PARCEL_Y_OFFSET * s
        offset = pygame.math.Vector2(0, y_off + 4 * s)
        offset = offset.rotate(-(self.tilt_deg if not flipped else -self.tilt_deg))
        bx = cx + offset.x
        by = cy + offset.y
        board_surf = pygame.Surface(
            (board_w + pad * 2, deck_h * 5 + pad * 2), pygame.SRCALPHA)
        bsx = board_surf.get_width() // 2
        bsy = board_surf.get_height() // 2 - 2 * SS
        deck = pygame.Rect(0, 0, board_w, deck_h)
        deck.center = (bsx, bsy)
        # Chrome outline + black fill.
        pygame.draw.rect(board_surf, (200, 200, 210), deck,
                         border_radius=3 * SS)
        pygame.draw.rect(board_surf, (10, 10, 18),
                         deck.inflate(-2 * SS, -2 * SS),
                         border_radius=2 * SS)
        # Crossbones diagonals.
        pygame.draw.line(board_surf, (235, 235, 225),
                         (deck.left + 4 * SS, deck.top + 1 * SS),
                         (deck.right - 4 * SS, deck.bottom - 1 * SS), SS)
        pygame.draw.line(board_surf, (235, 235, 225),
                         (deck.left + 4 * SS, deck.bottom - 1 * SS),
                         (deck.right - 4 * SS, deck.top + 1 * SS), SS)
        # Skull logo at deck centre.
        sk_w = max(5 * SS, int(7 * s * SS))
        sk_h = max(3 * SS, int(5 * s * SS))
        sk_rect = pygame.Rect(0, 0, sk_w, sk_h)
        sk_rect.center = (bsx, deck.centery - 1 * SS)
        pygame.draw.ellipse(board_surf, (240, 240, 230), sk_rect)
        pygame.draw.ellipse(board_surf, (10, 10, 18), sk_rect, SS)
        eye_y = sk_rect.centery - 1 * SS
        pygame.draw.circle(board_surf, (10, 10, 18),
                           (sk_rect.centerx - 1 * SS, eye_y), 1 * SS)
        pygame.draw.circle(board_surf, (10, 10, 18),
                           (sk_rect.centerx + 1 * SS, eye_y), 1 * SS)
        # Trucks + cream wheels with red bullseye.
        truck_h = max(1 * SS, int(2 * s * SS))
        wheel_r = max(2 * SS, int(3 * s * SS))
        spin = self.frame_t * 4.0
        for sign in (-1, 1):
            tx = bsx + sign * int(board_w * 0.32) - 3 * SS
            pygame.draw.rect(board_surf, (60, 60, 70),
                             (tx, deck.bottom, 6 * SS, truck_h))
            wx = bsx + sign * int(board_w * 0.32)
            wy = deck.bottom + truck_h + wheel_r
            pygame.draw.circle(board_surf, (50, 50, 60), (wx, wy),
                               wheel_r + 1 * SS)
            pygame.draw.circle(board_surf, (245, 240, 230), (wx, wy),
                               wheel_r)
            pygame.draw.circle(board_surf, (200, 50, 50), (wx, wy), 1 * SS)
            sx_p = wx + int(math.cos(spin + sign * 1.0) * wheel_r * 0.6)
            sy_p = wy + int(math.sin(spin + sign * 1.0) * wheel_r * 0.6)
            pygame.draw.line(board_surf, (180, 50, 50), (wx, wy),
                             (sx_p, sy_p), SS)
        # Smoothscale down to native size BEFORE rotation so the
        # rotated bitmap stays small (cheaper transform).
        board_surf = pygame.transform.smoothscale(board_surf,
                                                  (native_w, native_h))
        tilt = -self.tilt_deg if flipped else self.tilt_deg
        # KICKFLIP — 360° board-only spin layered on top of Pip's
        # tilt. Pip himself stays at his normal velocity-banked
        # posture (tilt_deg excludes kickflip); only the board
        # rotates, which sells the "flick the deck under your
        # feet" trick.
        if self.kickflip_t > 0 and self.kickflip_dur > 0:
            p = 1.0 - self.kickflip_t / self.kickflip_dur
            eased = p * p * p * (p * (p * 6.0 - 15.0) + 10.0)
            tilt += eased * 360.0
        # HEELFLIP — mirror of kickflip, board spins −360°.
        if self.heelflip_t > 0 and self.heelflip_dur > 0:
            p = 1.0 - self.heelflip_t / self.heelflip_dur
            eased = p * p * p * (p * (p * 6.0 - 15.0) + 10.0)
            tilt -= eased * 360.0
        rotated = pygame.transform.rotate(board_surf, tilt)
        # POP SHUVIT — horizontal scale-X = cos(p·π) on top of
        # whatever rotation is in `rotated`. Board flattens edge-on
        # at p=0.5 then flips and returns. Done AFTER rotation so
        # the scale tracks the (rotated) board's bounding box.
        if self.popshuvit_t > 0 and self.popshuvit_dur > 0:
            p_ps = 1.0 - self.popshuvit_t / self.popshuvit_dur
            scale_x = math.cos(p_ps * math.pi)
            abs_scale = max(abs(scale_x), 0.02)
            rw, rh = rotated.get_size()
            rotated = pygame.transform.scale(
                rotated, (max(1, int(rw * abs_scale)), rh))
            if scale_x < 0:
                rotated = pygame.transform.flip(rotated,
                                                True, False)
        if flipped:
            rotated = pygame.transform.flip(rotated, False, True)
        r = rotated.get_rect(center=(int(bx), int(by)))
        surf.blit(rotated, r.topleft)


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
        # SKATEBOARD: True when a Ramp is spawned on this pipe's
        # lower-pillar top. Pipe.draw forwards this to
        # draw_pillar_pair which then overpaints the crown
        # vegetation so it doesn't poke through the ramp.
        self.has_ramp = False
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
        draw_pillar_pair(surf, self.top_rect, self.bot_rect, palette,
                         self.seed, skip_bot_crown=self.has_ramp)

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


class Ramp:
    """SKATEBOARD ramp — a wooden wedge sitting on top of a pillar
    that Pip can skate up while the SKATEBOARD powerup is active.
    Shape ``/|`` : the slope rises LEFT→RIGHT and the vertical
    kicker face is on the RIGHT. ``base_y`` is the y of the
    bottom edge of the wedge — defaults to GROUND_Y for legacy
    placement on the floor, otherwise set to the host pipe's
    ``gap_y + gap_h/2`` so the ramp perches on the lower pillar's
    top."""

    def __init__(self, x: float, w: float, h: float,
                 base_y: float | None = None):
        from game.config import GROUND_Y as _GY
        self.x = x      # left edge of the wedge (ground side)
        self.w = w      # horizontal extent
        self.h = h      # peak height (top-right corner above base_y)
        self.base_y = _GY if base_y is None else base_y

    def off_screen(self) -> bool:
        return self.x + self.w + 8 < 0

    def surface_y_at(self, px: float) -> float:
        """Top surface y at world x. Outside the wedge footprint
        returns ``base_y`` (no rise). At ramp.x (left/foot) returns
        the base; at ramp.x + ramp.w (right/kicker) returns the
        peak."""
        if px < self.x or px > self.x + self.w:
            return self.base_y
        t = (px - self.x) / self.w   # 0 at left (base), 1 at right (peak)
        return self.base_y - self.h * t

    def draw(self, surf, palette=None):
        WOOD     = (140, 100, 65)
        WOOD_DK  = (95,  70,  45)
        WOOD_HI  = (200, 165, 105)
        EDGE     = (40,  25,  18)
        x0 = int(self.x)
        x1 = int(self.x + self.w)
        y0 = int(self.base_y)
        y_top = y0 - int(self.h)
        # Filled wedge — vertical kicker on the RIGHT side.
        pts = [(x0, y0), (x1, y0), (x1, y_top)]
        pygame.draw.polygon(surf, WOOD, pts)
        # Diagonal highlight band along the skating surface
        # (bottom-left to top-right).
        pygame.draw.line(surf, WOOD_HI, (x0 + 1, y0 - 1),
                         (x1 - 1, y_top + 1), 2)
        # Dark base shadow strip along the bottom edge.
        pygame.draw.line(surf, WOOD_DK, (x0, y0), (x1, y0), 2)
        # Plank seams — vertical lines on the slope face.
        for frac in (0.33, 0.66):
            xp = int(self.x + self.w * frac)
            yp = int(self.base_y - self.h * frac)
            pygame.draw.line(surf, WOOD_DK, (xp, yp + 1), (xp, y0 - 1), 1)
        # Outline.
        pygame.draw.polygon(surf, EDGE, pts, 1)
        # Kicker-face highlight (vertical right edge).
        pygame.draw.line(surf, WOOD_HI, (x1 - 1, y_top + 2),
                         (x1 - 1, y0 - 1), 1)


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
        # Weather wobble (visual-only horizontal jitter). World writes
        # this each frame based on rain_intensity — amplitude scales
        # linearly with intensity so coins barely tremor at first
        # drizzle and shake visibly at peak storm. Pure left-right;
        # no vertical wobble, no real position drift.
        self.weather_dx = 0.0
        # Random phase so coins don't sway in lockstep.
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
    """
    def __init__(self, x, y, kind="triple"):
        self.x = x
        self.y = y
        self.kind = kind
        self.collected = False
        self.pulse = 0.0
        # GENIE LAMP — when a player picks up a genie, World spawns
        # GENIE_OFFER_COUNT alternate powerup pickups in the play
        # field with this flag set. Picking up any one cancels the
        # others (see World._cull_genie_offers_except).
        self.is_genie_offer = False

    def update(self, dt):
        self.pulse += dt * 3.5

    def draw(self, surf):
        if self.kind == "triple":
            _draw_dollar_coin(surf, int(self.x), int(self.y), pulse=self.pulse)
        elif self.kind == "magnet":
            self._draw_magnet(surf)
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
        # ── Secret late-game powerups (intentionally not in powerup_help.py) ──
        elif self.kind == "skateboard":
            self._draw_skateboard_icon(surf)
        elif self.kind == "heist":
            self._draw_heist_icon(surf)
        elif self.kind == "lottery":
            self._draw_lottery_icon(surf)
        elif self.kind == "phoenix":
            self._draw_phoenix_icon(surf)
        elif self.kind == "genie":
            self._draw_genie_icon(surf)

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

    # ── SECRET LATE-GAME POWER-UP ICONS ─────────────────────────────────────

    def _draw_skateboard_icon(self, surf):
        """SKATEBOARD pickup token (variant S4 — Jolly Roger): bone
        skull centred over two crossed skateboard decks in an X
        shape, in the in-world kit palette (black + chrome + bone
        + red). NO halo — clean silhouette on the world.

        Painted at 6× supersample then smoothscale'd down to a 72×72
        native footprint — ~30 % larger and finer-edged than the
        earlier 4× / 56 px iteration."""
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.0) * 2)

        # Kit palette (matches _draw_helmet / _draw_skateboard).
        DOME   = (10, 10, 18)
        CHROME = (200, 200, 210)
        BONE   = (240, 240, 230)
        CREAM  = (245, 240, 230)
        RED    = (200, 50, 50)

        SS = 6
        NATIVE_W = NATIVE_H = 96
        big = pygame.Surface((NATIVE_W * SS, NATIVE_H * SS),
                             pygame.SRCALPHA)
        bx = big.get_width() // 2
        by = big.get_height() // 2

        # Two crossed skateboard decks behind the skull, ±35°. Deck
        # height bumped 6 SS → 9 SS so the X shape reads as bold,
        # chunky crossbones rather than thin bars behind the skull.
        for angle in (35, -35):
            sub_w = 46 * SS
            sub_h = 9 * SS
            sub = pygame.Surface(
                (sub_w + 4 * SS, sub_h + 4 * SS), pygame.SRCALPHA)
            d = pygame.Rect(0, 0, sub_w, sub_h)
            d.center = (sub.get_width() // 2, sub.get_height() // 2)
            pygame.draw.rect(sub, CHROME, d, border_radius=2 * SS)
            pygame.draw.rect(sub, DOME,
                             d.inflate(-2 * SS, -2 * SS),
                             border_radius=SS)
            # Wheel dot at each end of the deck.
            for sign in (-1, 1):
                wx = d.centerx + sign * (sub_w // 2 - 3 * SS)
                pygame.draw.circle(sub, CREAM, (wx, d.centery),
                                   int(3 * SS))
                pygame.draw.circle(sub, RED, (wx, d.centery),
                                   int(1.4 * SS))
            rotated = pygame.transform.rotate(sub, angle)
            big.blit(rotated, rotated.get_rect(center=(bx, by)))

        # Bone skull centred over the crossed decks. Skull sized
        # 27 × 22 SS (V1 base). Eyes / nose / mouth all anchored
        # to FRACTIONS of skull height so they sit cleanly inside
        # the ellipse.
        SK_W = 27
        SK_H = 22
        sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
        sk.center = (bx, by - SS)
        pygame.draw.ellipse(big, BONE, sk)
        pygame.draw.ellipse(big, DOME, sk, int(1.2 * SS))
        # Eye sockets — at 0.36 fractional y, radius + offset scale
        # with skull width.
        eye_r = int(SK_W * SS * 0.108)
        eye_x_off = int(SK_W * SS * 0.20)
        eye_y = sk.top + int(SK_H * SS * 0.36)
        for ex in (sk.centerx - eye_x_off,
                   sk.centerx + eye_x_off):
            pygame.draw.circle(big, DOME, (ex, eye_y), eye_r)
        # Nose triangle — fixed dimensions (±SS half-width, 2.5 SS
        # tall) anchored at 0.55 fractional y.
        nose_top_y = sk.top + int(SK_H * SS * 0.55)
        nose_bot_y = nose_top_y + int(2.5 * SS)
        pygame.draw.polygon(big, DOME, [
            (sk.centerx - SS, nose_top_y),
            (sk.centerx + SS, nose_top_y),
            (sk.centerx,      nose_bot_y),
        ])
        # Single black horizontal mouth bar at jaw_y = 0.78 of
        # skull height (B2 pick: 12 SS span × 1.4 SS stroke).
        jaw_y = sk.top + int(SK_H * SS * 0.78)
        span = 12 * SS
        pygame.draw.line(big, DOME,
                         (sk.centerx - span // 2, jaw_y),
                         (sk.centerx + span // 2, jaw_y),
                         max(1, int(1.4 * SS)))

        # Smoothscale down to native size for anti-aliased edges.
        icon = pygame.transform.smoothscale(big, (NATIVE_W, NATIVE_H))
        surf.blit(icon, icon.get_rect(center=(cx, cy)))

    def _draw_heist_icon(self, surf):
        """Planked-oak treasure chest pickup token. The pickup uses the
        same chest art as the carried-buff render, so the player can
        read 'I'm about to grab the thing I'll be carrying' in one
        glance. No halo behind it — clean silhouette on the world."""
        from game.treasure_box_variants import draw_chest_at
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.2) * 2)
        # The shared chest renderer paints at native size (~42×30). The
        # PowerUp footprint is 28 px, so this is a touch larger than the
        # collision circle — same overflow the kfc/grow icons use to
        # read clearly against a noisy background.
        draw_chest_at(surf, cx, cy)

    def _draw_lottery_icon(self, surf):
        """Scratch-off lottery card ("B5" — three big match-3 cells +
        tiny LUCKY chip). Gold body with a chrome perimeter, dashed
        dark-gold inner stroke, a red LUCKY chip riding the top edge,
        and 3 large silver scratch cells each with a single "?" so
        the "scratch ticket" reads strongly even at icon scale.

        Painted at 6× supersample on a 56×42 native canvas. Rotation
        happens at supersample BEFORE smoothscale so the chrome rim
        stays a uniform-thickness parallel border on all 4 sides
        (rotating at native creates per-side aliasing). No drop
        shadow — the live shadow leaked an asymmetric gray tail at
        the bottom-right when the ticket tilted."""
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
            # Paint to a sub-surface so the diagonal hatch can't bleed
            # past the cell rect onto the gold body.
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
            tmp.blit(mask, (0, 0),
                     special_flags=pygame.BLEND_RGBA_MIN)
            sub.blit(tmp, (0, 0))
            hatch = pygame.Surface(rect.size, pygame.SRCALPHA)
            for off in range(-rect.height, rect.width,
                              max(8, rect.height // 6)):
                pygame.draw.line(hatch, (180, 185, 200, 90),
                                 (off, 0),
                                 (off + rect.height, rect.height),
                                 max(1, rect.height // 60))
            hatch.blit(mask, (0, 0),
                       special_flags=pygame.BLEND_RGBA_MIN)
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

        # ── card chassis (gold body + chrome perimeter + dashed
        #     inner stroke). No drop shadow. ──
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

        # ── LUCKY chip riding the top edge ──
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

        # ── 3 large scratch cells below the chip ──
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

        # Rotate at supersample then smoothscale down so the tilted
        # edges stay clean and the chrome rim sits as a uniform-
        # thickness parallel border on all 4 sides. ±5° tilt.
        tilt = math.sin(self.pulse * 0.7) * 5
        rotated = pygame.transform.rotate(big, tilt)
        rw, rh = rotated.get_size()
        final = pygame.transform.smoothscale(rotated,
                                              (rw // SS, rh // SS))
        surf.blit(final, final.get_rect(center=(cx, cy)))

    def _draw_genie_icon(self, surf):
        """In-world genie lamp pickup — Amber Crystal cut-glass lamp
        with diamond facets, gold rim collar, multi-gem stopper
        (emerald + sapphire + ruby), gold torus handle with an amber
        centre gem, gold foot ring with emerald gem dots, dark-navy
        outline glow for sky-colour separation, smoke + sparkles.
        The full Amber Crystal design from
        `tools/render_a1_lamp_variants.py` is rendered once at SS=8
        and cached in `game._lamp_assets`; per frame we just tilt +
        bob + blit the cached sprite."""
        from game._lamp_assets import get_lamp_sprite

        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.9) * 2)
        sprite = get_lamp_sprite(target_height=52)
        # Gentle tilt for the "alive" feel — same idiom as the old
        # brass lamp's ±3° sway.
        tilt = math.sin(self.pulse * 0.8) * 3
        rotated = pygame.transform.rotate(sprite, tilt)
        surf.blit(rotated, rotated.get_rect(center=(cx, cy)))

    def _draw_phoenix_icon(self, surf):
        """In-world phoenix pickup — a hand-painted phoenix with sweeping
        flame wings, long flame plume tail, and crown of fire. Variant
        adornments (sun rays for solar, ember trail for ember, egg for
        ashes) are layered on top of the shared phoenix base."""
        from game.config import PHOENIX_VARIANT as _PV
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.9) * 2)
        grandiose = {"imperial", "fenghuang", "dragon", "comet", "royal",
                     "blaze", "sunburst", "twin", "swift", "grand",
                     "soar", "rise", "stoop", "dive", "eternal",
                     "eternal_warm", "eternal_soft", "eternal_dawn",
                     "eternal_friend", "eternal_lite"}
        # 1. Variant-specific halo behind everything
        if _PV == "solar":
            self._draw_phoenix_icon_solar_halo(surf, cx, cy)
        elif _PV in ("mythic", "imperial", "royal", "blaze", "sunburst",
                     "twin", "swift", "grand",
                     "soar", "rise", "stoop", "dive", "eternal",
                     "eternal_warm", "eternal_soft", "eternal_dawn",
                     "eternal_friend", "eternal_lite"):
            self._draw_phoenix_icon_mythic_halo(surf, cx, cy)
        elif _PV == "fenghuang":
            self._draw_phoenix_icon_fenghuang_halo(surf, cx, cy)
        elif _PV in ("dragon", "comet"):
            # No halo — these variants carry their identity in-sprite.
            pass
        else:
            self._draw_phoenix_icon_fire_halo(surf, cx, cy)
        # 2. Ember pre-trail (variant 3 only) — drawn behind the bird
        if _PV == "ember":
            for dx, sz, alpha in ((10, 3, 220), (16, 2, 160),
                                  (22, 2, 110), (28, 1, 70)):
                pygame.draw.circle(surf, (255, 200,  90, alpha),
                                   (cx - 18 - dx, cy + 6), sz)
        # 3. Body — grandiose variants render the actual sprite scaled
        #    down so the pickup looks identical to what Pip becomes.
        if _PV in grandiose:
            from game import parrot
            sprite = parrot.get_phoenix_parrot(0, 0.0, variant=_PV)
            sw, sh = sprite.get_size()
            # Scale to about 56 px wide so the pickup remains a sensible
            # ~32 px footprint after the wings (which can extend ±40 px
            # from the body) are folded into the icon.
            scale = 56 / max(sw, sh)
            new_w = max(1, int(sw * scale))
            new_h = max(1, int(sh * scale))
            scaled = pygame.transform.smoothscale(sprite, (new_w, new_h))
            surf.blit(scaled,
                      scaled.get_rect(center=(cx, cy)).topleft)
        else:
            # Classic / solar / ember / mythic / ashes use the hand-
            # painted compact pickup body (different style from the
            # grandiose sprites by design).
            _draw_phoenix_pickup_body(surf, cx, cy, _PV, self.pulse)
        # 4. Egg accessory (ashes only) — small egg under the bird
        if _PV == "ashes":
            pygame.draw.ellipse(surf, (130, 100,  60),
                                pygame.Rect(cx - 5, cy + 14, 10, 8))
            pygame.draw.ellipse(surf, (245, 230, 190),
                                pygame.Rect(cx - 4, cy + 14, 8, 6))
            pygame.draw.line(surf, ( 80,  60,  30),
                             (cx - 2, cy + 17), (cx + 1, cy + 19), 1)
            pygame.draw.line(surf, ( 80,  60,  30),
                             (cx + 1, cy + 19), (cx + 3, cy + 17), 1)

    def _draw_phoenix_icon_fire_halo(self, surf, cx, cy):
        halo = pygame.Surface((64, 64), pygame.SRCALPHA)
        cyc = 0.5 + 0.5 * math.sin(self.pulse * 1.4)
        a = int(85 + 80 * cyc)
        pygame.draw.circle(halo, (255,  60,  20, a // 4), (32, 32), 30)
        pygame.draw.circle(halo, (255, 130,  40, a // 3), (32, 32), 22)
        pygame.draw.circle(halo, (255, 200,  80, a // 2), (32, 32), 14)
        pygame.draw.circle(halo, (255, 240, 160, a),      (32, 32),  6)
        surf.blit(halo, (cx - 32, cy - 32))

    def _draw_phoenix_icon_solar_halo(self, surf, cx, cy):
        tpl = _get_phoenix_sun_template()
        rot = pygame.transform.rotate(tpl, (self.pulse * 22) % 360)
        rrect = rot.get_rect(center=(cx, cy))
        surf.blit(rot, rrect.topleft)
        cyc = 0.5 + 0.5 * math.sin(self.pulse * 1.6)
        a = int(150 + 60 * cyc)
        pygame.draw.circle(surf, (255, 240, 180, a // 2), (cx, cy), 14)
        pygame.draw.circle(surf, (255, 250, 220, a),      (cx, cy),  8)

    def _draw_phoenix_icon_mythic_halo(self, surf, cx, cy):
        halo = pygame.Surface((72, 72), pygame.SRCALPHA)
        cyc = 0.5 + 0.5 * math.sin(self.pulse * 1.4)
        a = int(100 + 90 * cyc)
        pygame.draw.circle(halo, (255,  60,  20, a // 5), (36, 36), 34)
        pygame.draw.circle(halo, (255, 130,  40, a // 3), (36, 36), 25)
        pygame.draw.circle(halo, (255, 200,  80, a // 2), (36, 36), 17)
        pygame.draw.circle(halo, (255, 245, 180, a),      (36, 36),  9)
        surf.blit(halo, (cx - 36, cy - 36))

    def _draw_phoenix_icon_fenghuang_halo(self, surf, cx, cy):
        """Cool teal-and-gold halo for the Eastern fenghuang pickup —
        matches the in-game Fenghuang halo."""
        halo = pygame.Surface((72, 72), pygame.SRCALPHA)
        cyc = 0.5 + 0.5 * math.sin(self.pulse * 1.2)
        a = int(90 + 80 * cyc)
        pygame.draw.circle(halo, ( 40,  80, 140, a // 4), (36, 36), 32)
        pygame.draw.circle(halo, ( 60, 130, 170, a // 3), (36, 36), 24)
        pygame.draw.circle(halo, (110, 200, 210, a // 2), (36, 36), 16)
        pygame.draw.circle(halo, (255, 200,  80, a),      (36, 36),  9)
        surf.blit(halo, (cx - 36, cy - 36))

    # ── Phoenix icon variants ───────────────────────────────────────

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


# ── TreasureCoinParticle ─────────────────────────────────────────────────────

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


class TreasureCoinParticle:
    """Spinning gold doubloon that pops up out of the treasure box on
    each flap, arcs upward briefly, then falls back under gravity. The
    score gain happens instantly in World — this is pure visual feedback
    so the player SEES the coins they just earned jump out of the lid."""

    __slots__ = ("x", "y", "vx", "vy", "life", "life_max", "spin", "spin_rate", "r")

    def __init__(self, x, y, vx, vy, *, life=0.65, r=7, spin_rate=8.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.life_max = life
        # Random starting spin phase so the 2 coins from a single flap
        # aren't squeezed to the same width.
        self.spin = random.uniform(0, math.tau)
        self.spin_rate = spin_rate
        self.r = r

    def update(self, dt):
        # Slightly lighter than the default Particle gravity (900) so the
        # coin hangs at the apex a beat longer — reads as a deliberate
        # "pop" rather than a quick toss.
        self.vy += 760.0 * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.spin += self.spin_rate * dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        from game.draw import COIN_DARK, COIN_LIGHT, lerp_color
        t = max(0.0, self.life / self.life_max)
        # Hold full alpha for the first half of life, then fade.
        alpha = int(255 * min(1.0, t * 2.0))
        r = self.r
        # Spinning squeeze on the horizontal axis (same recipe as the
        # in-world Coin sprite — keeps the look consistent).
        cos_s = math.cos(self.spin)
        squeeze = max(0.12, abs(cos_s))
        w = max(2, int(r * 2 * squeeze))
        h = r * 2
        disc = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
        # Dark outline
        pygame.draw.ellipse(disc, (12, 6, 4, alpha),
                            pygame.Rect(0, 0, w + 2, h + 2))
        # Rope-rim
        pygame.draw.ellipse(disc, (*COIN_DARK, alpha),
                            pygame.Rect(1, 1, w, h))
        # Vertical-gradient face
        inner = pygame.Rect(2, 2, max(0, w - 2), max(0, h - 2))
        if inner.w > 0 and inner.h > 0:
            for y in range(inner.h):
                ti = y / max(1, inner.h - 1)
                col = lerp_color(COIN_LIGHT, COIN_DARK, ti)
                pygame.draw.line(disc, (*col, alpha),
                                 (inner.x, inner.y + y),
                                 (inner.x + inner.w - 1, inner.y + y))
            # Top sheen arc when the coin is close to face-on
            if abs(cos_s) > 0.5 and inner.w >= 4:
                pygame.draw.arc(disc, (255, 235, 150, alpha),
                                pygame.Rect(2, 2, inner.w, inner.h - 2),
                                math.radians(40), math.radians(140), 1)
        surf.blit(disc, (int(self.x) - disc.get_width() // 2,
                         int(self.y) - disc.get_height() // 2))


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


# ── GenieShineParticle ───────────────────────────────────────────────────────


def _lazy_import_genie_design():
    """Import the consolidated genie-design module (palette, helpers,
    body-part drawing functions). The data lives in game/_genie_assets.py
    instead of tools/ because the deploy workflow strips tools/ from
    the bundle — if we imported from tools at runtime, the deployed
    build would crash on Genie pickup with ImportError.

    All five tool modules' contents are consolidated into a single
    namespace, so the returned 5-tuple just re-binds the same module
    five times. (The 5-tuple shape is kept so existing callers
    `_ref, _legs, _arms, _shines, _carpets = _lazy_import_genie_design()`
    keep working.)"""
    if hasattr(_lazy_import_genie_design, "_cached"):
        return _lazy_import_genie_design._cached
    from game import _genie_assets as _ga
    cache = (_ga, _ga, _ga, _ga, _ga)
    _lazy_import_genie_design._cached = cache
    return cache


class GenieShineParticle:
    """A bright pixie-star shine launched from the genie's palm that
    flies to a target (x, y) and on arrival spawns the offer PowerUp +
    a reveal poof + a sparkle chime. The "wish" travels through the
    air visibly instead of teleporting in.

    Lives only as long as the flight (~0.30 s). Drawn as the classic
    4-point gold pixie star with a white diamond core (the v1 shine
    design picked by the user)."""

    __slots__ = ("x", "y", "_sx", "_sy", "_tx", "_ty",
                 "kind", "world", "_t", "duration", "_fired",
                 "_spin")

    def __init__(self, start_x, start_y, target_x, target_y,
                 kind, world):
        self.x = self._sx = float(start_x)
        self.y = self._sy = float(start_y)
        self._tx = float(target_x)
        self._ty = float(target_y)
        self.kind = kind
        self.world = world
        self._t = 0.0
        self.duration = 0.55
        self._fired = False
        # Pre-rolled spin offset so each shine rotates slightly
        # differently in flight.
        import random as _r
        self._spin = _r.uniform(0, math.pi * 2)

    def update(self, dt):
        self._t += dt
        if self._t >= self.duration:
            if not self._fired:
                self._on_arrive()
                self._fired = True
            return
        k = self._t / self.duration
        # Ease-out: fast start, slow arrival so the shine "settles"
        # onto the target instead of slamming.
        e = 1.0 - (1.0 - k) ** 2
        self.x = self._sx + (self._tx - self._sx) * e
        self.y = self._sy + (self._ty - self._sy) * e
        # Light vertical arc — peak ~12 px above the straight line
        # at the midpoint of the flight.
        arc = math.sin(k * math.pi) * 12.0
        self.y -= arc

    def alive(self):
        return self._t < self.duration

    def _on_arrive(self):
        # Spawn the offer + reveal poof + chime at the target.
        offer = PowerUp(self._tx, self._ty, kind=self.kind)
        offer.is_genie_offer = True
        self.world.powerups.append(offer)
        self.world._spawn_genie_reveal_poof(self._tx, self._ty)
        try:
            from game import audio
            audio._play("coin_triple", 0.55)
        except Exception:
            pass

    def draw(self, surf):
        # Render the LITERAL shine #1 (classic pixie star) from
        # tools/render_a1_shine_variants.shine_1_classic_pixie at the
        # particle's current world position. Same art as the static
        # palm shines on the GenieCharacter so the shine "detaches"
        # visually. We draw onto a small per-particle supersample
        # surface and smoothscale it down to retain crispness.
        _ref, _legs, _arms, _shines, _carpets = _lazy_import_genie_design()
        SS = _ref.SS
        size_n = 32           # native px square — fits a full pixie star
        big = pygame.Surface((size_n * SS, size_n * SS), pygame.SRCALPHA)
        # The shine function draws at (px, py) in the supersample
        # canvas — put it at the centre.
        _shines.shine_1_classic_pixie(big,
                                      (size_n * SS) // 2,
                                      (size_n * SS) // 2)
        scaled = pygame.transform.smoothscale(big, (size_n, size_n))
        rect = scaled.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(scaled, rect.topleft)


# ── GenieCharacter ───────────────────────────────────────────────────────────

class GenieCharacter:
    """Conjured genie that hovers ahead of Pip and casts the three Genie
    offer powerups one beat at a time. Procedural sprite drawn in the
    same brass + mauve palette as the lamp (entities.py PowerUp lamp
    icon) — translucent so it reads as summoned smoke given form.

    Five phases driven by ``_t / DURATION``:
      RISE      (0.00–0.85) fade in + scale 0.3→1.0 + smoke trails
      CAST      (0.85–1.10) arms raise; at 1.10 ALL 3 offers POOF
                            into existence simultaneously
      HOLD      (1.10–2.60) genie stays put; user has ~1.5 s to
                            manoeuvre to whichever offer they want
      VANISH    (2.60–3.30) collapse into smoke + fade out

    The genie is STATIONARY (vx=0). It hovers at its spawn point
    while the world scrolls past, so the offers (spawned at the
    moment of cast at genie-relative world coords) scroll naturally
    toward Pip.

    World owns ``self.genie_actors``; each tick calls ``update(dt)``
    and ``draw(surf)``. ``alive()`` returns False when the vanish
    phase completes so World sweeps it from the list."""

    DURATION       = 3.30
    RISE_END       = 0.85
    CAST_BEAT      = 1.10        # single moment — all 3 offers poof
    VANISH_START   = 2.60        # ~1.5 s hold after cast for user
    VANISH_END     = 3.30

    def __init__(self, x, y, vx, offers, world):
        # offers: list of (kind, target_y) triples, ordered by cast index.
        # world: back-reference so each cast beat can call the world's
        # poof helper and append the spawned PowerUp.
        self.x, self.y = float(x), float(y)
        self.vx = vx
        self.offers = list(offers)            # consumed front-to-back
        self.world = world
        self._t = 0.0
        self._fired = False                   # single cast moment
        self._vanished = False                # vanish-swirl spawned once
        self._tail_clock = 0.0                # spawn smoke trails on RISE
        self._dead = False                    # set early when picked
        # Pre-render the full body once — arms no longer animate per
        # beat (the shine particles handle the cast effect), so a
        # cached supersample sprite is far cheaper to redraw each
        # frame than rebuilding the whole figure 60×/s.
        # Body is rendered AT the reference's exact dimensions
        # (W=320, H=460, SS=6) so the mouth + face + everything is
        # pixel-for-pixel identical to a1_shine_1_v1.png. For
        # gameplay-canvas reasons the rendered sprite is then
        # smoothscaled DOWN by _display_scale before being blit, so
        # the genie occupies a reasonable fraction of the 360-wide
        # game window (~50%) rather than 89%.
        self._native_w = 320
        self._native_h = 460
        self._ss = 6
        self._display_scale = 0.34         # 320 → 109 px wide on screen (~30%)
        # Palm offsets in REFERENCE native px from the genie's centre.
        # draw_offering_arms_with_shine puts wrists at (cx ± 54, 214),
        # palms just past the cuff at (cx ± 58, 210). Canvas centre
        # is at (160, 230), so palm offset = (±58, -20).
        # _palm_world_pos applies _display_scale when computing the
        # in-game palm position.
        self._palm_dx = 58
        self._palm_dy = -20
        self._cached_body = self._render_body_supersample()

    # ── public API ───────────────────────────────────────────────────────
    def update(self, dt):
        self.x += self.vx * dt
        self._t += dt
        # Single cast moment — all 3 offers materialise at once with
        # big simultaneous poofs.
        if (not self._fired) and self._t >= self.CAST_BEAT:
            self._fire_all()
            self._fired = True
        # Wispy smoke trails off the tail during RISE.
        if self._t < self.RISE_END:
            self._tail_clock += dt
            while self._tail_clock >= 0.08:
                self._tail_clock -= 0.08
                self._spawn_tail_wisp()
        # Vanish — final swirl of cloud puffs at the transition.
        if ((not self._vanished) and (not self._dead)
                and self._t >= self.VANISH_START):
            self._spawn_vanish_swirl()
            self._vanished = True

    def alive(self):
        return (not self._dead) and self._t < self.VANISH_END

    def kill(self):
        # Called when the player picks one of the offers before the
        # genie finishes casting — stop spawning anything else.
        self._dead = True

    # ── internals ────────────────────────────────────────────────────────
    def palm_world_pos(self, side):
        """World-space (x, y) of the genie's palm. ``side`` is -1 for
        left, +1 for right. Used to launch shine particles from the
        correct origin. Applies the display-scale so the offset
        matches what's actually drawn on screen, not the
        reference-native dimensions."""
        ds = self._display_scale
        return (self.x + side * self._palm_dx * ds,
                self.y + self._palm_dy * ds)

    def _fire_all(self):
        """Single cast moment — spawn ALL 3 offer powerups + their
        reveal poofs + one combined chime simultaneously. Replaces
        the previous per-offer beat schedule so the user sees all
        three choices at once with a clear, coordinated POOF and
        has time to manoeuvre to whichever they want.

        Offers spawn FAR AHEAD of Pip (independent of the genie's
        own position — the genie can hover close to the parrot
        while still summoning the powerups out at the right edge
        of the screen). Centre x = bird.x + 220 puts the three
        offers (spread by GENIE_OFFER_X_STEP) at world x ≈ 250 /
        310 / 370 — visible from spawn and giving the user ~1.0–
        1.75 s of horizontal travel before each one reaches Pip."""
        if self._dead:
            return
        import random as _r
        # Each offer gets its OWN (x, y) — no fixed column pattern.
        # _pick_offer_positions ensures:
        #   - all offers are far from the parrot (≥ 200 px)
        #   - offers don't cluster (≥ 90 px from each other)
        #   - none sits inside a pillar body
        #   - x is varied (180-280 px ahead of Pip) and y jitters
        #     ±30 px around the assigned slot so the layout reads
        #     as "scattered choices" rather than "stiff column".
        slot_ys = [oy for _, oy in self.offers]
        positions = self._pick_offer_positions(slot_ys)
        for (kind, _slot_y), (ox, oy) in zip(self.offers, positions):
            offer = PowerUp(ox, oy, kind=kind)
            offer.is_genie_offer = True
            self.world.powerups.append(offer)
            self.world._spawn_genie_reveal_poof(ox, oy)
        # Single combined chime — louder than per-beat since this is
        # the one big cast moment of the cinematic.
        try:
            from game import audio
            audio._play("coin_triple", 0.95)
        except Exception:
            pass
        # Bright flash burst at the genie's centre so the cast moment
        # also reads on the GENIE, not just at the three offer sites.
        gx_centre = int(self.x)
        gy_centre = int(self.y)
        for _ in range(14):
            ang = _r.uniform(0, math.pi * 2)
            sp = _r.uniform(80, 180)
            self.world.particles.append(CloudPuff(
                gx_centre, gy_centre,
                math.cos(ang) * sp, math.sin(ang) * sp - 40,
                _r.uniform(0.30, 0.50),
                6, 16,
                _r.choice([(255, 240, 175), (255, 220, 130),
                           (240, 200, 250), (255, 255, 245)]),
            ))

    def _pick_offer_positions(self, slot_ys):
        """Pick a unique (x, y) for each offer such that:
           - the offer is FAR FROM THE PARROT (≥ MIN_PARROT_DIST px)
           - offers don't cluster (≥ MIN_OFFER_DIST from each other)
           - none lands inside a pillar body
           - x is varied (no fixed column pattern) and y jitters
             ±Y_JITTER around the assigned slot for a "scattered
             choices" feel rather than a stiff line.

        Uses rejection sampling: try random candidates within the
        valid zone for each slot, accept the first that satisfies
        every constraint. Falls back to a deterministic safe spot
        if 40 attempts can't satisfy the constraints (pathological
        pillar / parrot layout)."""
        from game.config import PIPE_W
        import random as _r
        bird_x = self.world.bird.x
        bird_y = self.world.bird.y
        pipe_half = PIPE_W / 2
        offer_half = 18
        clearance = pipe_half + offer_half + 6
        # X range relative to bird: 180-280 px ahead (world x ≈ 270-370,
        # i.e. the right third of the 360-wide screen).
        X_MIN_AHEAD, X_MAX_AHEAD = 180, 280
        Y_JITTER = 30
        MIN_PARROT_DIST = 200
        MIN_OFFER_DIST  = 90
        positions = []
        for slot_y in slot_ys:
            picked = None
            for _ in range(40):
                x = bird_x + _r.randint(X_MIN_AHEAD, X_MAX_AHEAD)
                y = slot_y + _r.randint(-Y_JITTER, Y_JITTER)
                # Must be far from the parrot (euclidean)
                dx, dy = x - bird_x, y - bird_y
                if dx * dx + dy * dy < MIN_PARROT_DIST * MIN_PARROT_DIST:
                    continue
                # Must not cluster with other already-picked offers
                too_close = False
                for px, py in positions:
                    if (x - px) * (x - px) + (y - py) * (y - py) < \
                            MIN_OFFER_DIST * MIN_OFFER_DIST:
                        too_close = True
                        break
                if too_close:
                    continue
                # Must clear pillars: a pillar at this x blocks unless
                # its gap covers y
                blocked = False
                for p in self.world.pipes:
                    if abs(p.x - x) < clearance:
                        gap_top = p.gap_y - p.gap_h / 2
                        gap_bot = p.gap_y + p.gap_h / 2
                        if not (gap_top <= y <= gap_bot):
                            blocked = True
                            break
                if blocked:
                    continue
                picked = (x, y)
                break
            if picked is None:
                # Fallback — deterministic safe spot far ahead, no
                # jitter, at the slot's exact y. Last-resort if the
                # rejection loop failed.
                picked = (bird_x + 230, slot_y)
            positions.append(picked)
        return positions

    def _spawn_tail_wisp(self):
        import random as _r
        from game import entities as _e  # avoid name shadow
        # Lavender wisps drifting down-left off the tail anchor.
        cx = self.x - 14
        cy = self.y + 38
        for _ in range(2):
            vx = -_r.uniform(20, 50) + self.vx * 0.3
            vy = _r.uniform(10, 30)
            life = _r.uniform(0.35, 0.55)
            color = _r.choice([(230, 220, 250), (215, 200, 240),
                               (200, 180, 230)])
            self.world.particles.append(_e.CloudPuff(
                cx, cy, vx, vy, life, 3, 11, color))

    def _spawn_vanish_swirl(self):
        import random as _r
        from game import entities as _e
        for _ in range(14):
            ang = _r.uniform(0, math.pi * 2)
            sp  = _r.uniform(40, 110)
            vx  = math.cos(ang) * sp
            vy  = math.sin(ang) * sp - _r.uniform(20, 60)
            life = _r.uniform(0.30, 0.55)
            color = _r.choice([(230, 220, 250), (215, 200, 240),
                               (250, 235, 200)])
            self.world.particles.append(_e.CloudPuff(
                self.x, self.y, vx, vy, life, 5, 16, color))

    # ── render ───────────────────────────────────────────────────────────
    def draw(self, surf):
        # Compute phase-driven values for the simplified
        # rise / hold / vanish state machine.
        t = self._t
        # cast_arm / cast_k are kept for API compatibility with the
        # cached body sprite but no longer do anything — the body
        # is pre-rendered statically in the offering pose.
        cast_arm = -1
        cast_k = 0.0
        if t < self.RISE_END:
            # Scale 0.3 → 1.0, alpha 0 → 210, bob upward 10 px.
            k = t / self.RISE_END
            scale = 0.3 + 0.7 * (1 - (1 - k) ** 2)        # ease-out
            alpha = int(210 * k)
            bob   = -10 * (1 - k)
        elif t < self.VANISH_START:
            # Hold steady: full scale + alpha. Visible floating bob —
            # ±5 px at ~1 Hz so the genie reads as hovering, not static.
            scale = 1.0
            alpha = 210
            bob   = math.sin(t * 4.5) * 5.0
        else:
            # Vanish: shrink + fade, drift up slightly.
            k = (t - self.VANISH_START) / (self.VANISH_END - self.VANISH_START)
            scale = 1.0 - 0.4 * k
            alpha = int(210 * (1 - k))
            bob   = -18 * k
        if alpha <= 2:
            return
        self._blit_sprite(surf, alpha, scale, bob, cast_arm, cast_k)

    def _blit_sprite(self, surf, alpha, scale, bob, cast_arm, cast_k):
        """Apply the cached body sprite at the current scale + alpha +
        sway. The cached body bakes in the whole locked design (lotus
        body + offering arms + palm shines + face + headband etc.);
        per-frame we only do smoothscale + rotate + alpha + blit, which
        is far cheaper than rebuilding the figure every tick."""
        eff = scale * self._display_scale
        out_w = max(2, int(self._native_w * eff))
        out_h = max(2, int(self._native_h * eff))
        scaled = pygame.transform.smoothscale(self._cached_body,
                                              (out_w, out_h))
        sway = math.sin(self._t * 1.4) * 3.0
        rotated = pygame.transform.rotate(scaled, sway)
        rotated.set_alpha(alpha)
        rect = rotated.get_rect(center=(int(self.x), int(self.y + bob)))
        surf.blit(rotated, rect.topleft)

    # ── body render (called once in __init__, cached) ────────────────────
    def _render_body_supersample(self):
        """Build the full A1 lotus-genie body into a supersample
        surface by calling the EXACT same drawing functions used by
        the reference design tool chain. Result is pixel-for-pixel
        identical to docs/screenshots/genie_designs/a1_shine_1_v1.png
        (variant 2 v5 + classic pixie shines). NO re-derivation of
        coordinates — every s(N) value is the tool's literal value."""
        _ref, _legs, _arms, _shines, _carpets = _lazy_import_genie_design()
        SS = _ref.SS         # 6
        W = _ref.W           # 320
        H = _ref.H           # 460
        big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
        cx = (W * SS) // 2
        # Composition follows tools/render_a1_carpet_variants.render_figure
        # for the locked Royal velvet carpet (no central medallion).
        # The smoke aura is replaced by the carpet — the genie now
        # sits on a high-end velvet rug instead of floating above
        # an atmospheric pad.
        _carpets.draw_carpet_royal(big, cx)
        _legs.draw_crossed_legs_ankle_cross(big, cx)   # locked variant 2 lotus
        _ref.draw_torso(big, cx)
        _ref.draw_neck(big, cx)
        head_cy = _ref.s(60)
        head_r = _ref.s(40)
        _ref.draw_head(big, cx, head_cy, head_r)
        _ref.draw_face(big, cx, head_cy)
        _ref.draw_earrings(big, cx, head_cy, head_r)
        _ref.draw_topknot_and_headband(big, cx, head_cy, head_r)
        _ref.draw_sash(big, cx)
        _shines.draw_offering_arms_with_shine(
            big, cx, _shines.shine_1_classic_pixie)
        return big

    # The legacy hand-rebuilt body method (replaced by the literal
    # tool-composer above) is preserved here as _legacy_render only
    # to keep the line numbers below intact during the diff. It is
    # never called.

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


# Per-trick fill + halftone-dot colours for the SKATEBOARD comic
# bubble that replaces the old gradient float-text. Base hues are
# pulled from the existing float-text colours so each trick keeps
# its identity colour; dot colours are a darker variant for
# Lichtenstein contrast inside the burst.
TRICK_BUBBLE_PALETTE = {
    "BACKFLIP!":   ((110, 230, 110), ( 30,  90,  40)),
    "KICKFLIP!":   ((120, 200, 235), ( 30,  70, 130)),
    "HEELFLIP!":   ((170, 140, 230), ( 70,  40, 130)),
    "POP SHUVIT!": ((230, 130, 180), (120,  30,  90)),
    "NOSE GRIND!": ((255, 215, 110), (180, 120,  30)),
    "TAIL GRIND!": ((255, 215, 110), (180, 120,  30)),
}


class TrickBubble:
    """SKATEBOARD trick name rendered as a tilted comic halftone-burst
    bubble (matches the D5 chorus + E3 score visual vocabulary). The
    bubble surface is pre-rendered once on construction (label and
    tilt are immutable) and cached as `_surf`; `draw` just blits it
    with a per-frame alpha derived from the bubble's remaining life.

    Lifetime ~1.4 s: snappy POP-IN at full alpha (no fade-in delay)
    + 0.4 s linear fade-out so stacking bubbles appear immediately
    and exit gracefully when their life runs out."""

    __slots__ = ("x", "y", "life", "life_max", "_surf")

    def __init__(self, label, x, y, tilt_deg=0.0, life=1.4):
        from game.skateboard_fx import (
            _halftone_filled_burst, _gradient_text, INK,
        )
        self.x = x
        self.y = y
        self.life = life
        self.life_max = life
        base, dot = TRICK_BUBBLE_PALETTE.get(
            label, ((255, 220, 30), (230, 60, 50)))
        font_size = 16
        font = _get_float_font(font_size)
        tw, _th = font.size(label)
        ro = max(50, tw // 2 + 16)
        ri = max(28, ro - 24)
        # Sub-surface big enough for the burst + rotation slack.
        sw = sh = ro * 2 + 24
        bsurf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        bcx, bcy = sw // 2, sh // 2
        _halftone_filled_burst(bsurf, bcx, bcy, ro, ri, spikes=10,
                                dot_col=dot, base_col=base)
        txt = _gradient_text(label, font_size,
                              top_col=(255, 250, 240),
                              bot_col=base,
                              outline=INK, outline_w=3)
        bsurf.blit(txt, txt.get_rect(center=(bcx, bcy)))
        if abs(tilt_deg) > 0.5:
            bsurf = pygame.transform.rotate(bsurf, tilt_deg)
        self._surf = bsurf

    def update(self, dt):
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        if self.life > 0.4:
            alpha = 255
        elif self.life > 0:
            alpha = int(255 * (self.life / 0.4))
        else:
            alpha = 0
        self._surf.set_alpha(alpha)
        surf.blit(self._surf, self._surf.get_rect(
            center=(int(self.x), int(self.y))))


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
