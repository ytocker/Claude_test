#!/usr/bin/env python3
"""
glass round 2 — steeper streaks, droplet shape, specular rake, refraction,
edge scatter, arc warm-tint, dotted-rail fade near death marker.

Implements every art-director critique note from round 1:
  1. Rebuilt specular rake: 8-14px wide gaussian cross-section, slight curve,
     corner-to-corner off canvas, shallower angle, BLEND_ADD
  2. Streaks steepened to 25-45° off vertical; apex steeper, bottom shallower
  3. Droplet head + tapered tail: bead at leading lower-right end, alpha ramp
     from bead (peak) to nothing at trailing end, varied widths (1/2/3-4px)
  4. Refraction at horizon where fat runners cross: nudge horizon columns ±2-3px
  5. Edge scatter/bloom: perimeter vignette + top sky bloom + side mid-edge glow
  6. Dotted secondary arc fades to near-zero within ~40px of death marker
  7. Arc warm tint: +10R +5G on flown-arc gold, very-soft bloom behind it

Technical:
  Canvas 360×640, SS=3 (draw at 1080×1920, smoothscale to 1×).
  Vanilla pygame 2.6.1 — no .gaussian_blur(), no .box_blur(), not pygame-ce.
  soft_glow(radius,color,peak,falloff): radial dist, premultiplied RGB, BLEND_ADD.
"""
import os
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color, lerp_color_multi

W, H   = 360, 640
SS     = 3
HORIZON_Y = 430

FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
_fonts: dict = {}

# ── palette ──────────────────────────────────────────────────────────────────
INK    = (6, 8, 14)
GOLD   = (255, 206, 92)
CREAM  = (246, 240, 230)
COOL   = (150, 168, 196)
SLATE  = (58, 62, 82)
SCRIM  = (26, 22, 34)
GEYSER_C = (146, 232, 255)
CLOWN_C  = (255, 118, 196)
RAIN_C   = (150, 190, 255)
SNOW_C   = (222, 244, 255)

# ── arc geometry ─────────────────────────────────────────────────────────────
CX, CY, R = 180, 430, 175
R_INNER   = 159
EASE_P    = 0.652


def ease(p):
    return max(0.0, min(1.0, p)) ** EASE_P


def pos_u(u, radius=R):
    a = math.pi * (1.0 - u)
    return (CX + radius * math.cos(a), CY - radius * math.sin(a))


def arc_pos(p, radius=R):
    return pos_u(ease(p), radius)


# ── run data ─────────────────────────────────────────────────────────────────
DEATH_PHASE  = 0.184
DEATH_PILLAR = 25
DAY_N        = 1
TIME_ALIVE   = 47
PHASE_LABEL  = "DAY"

CLOWN_PHASE = 0.403
RAIN_PHASE  = 0.430
SNOW_PHASE  = 0.820

DEATH_X, DEATH_Y = arc_pos(DEATH_PHASE)


# ── text / chrome helpers ─────────────────────────────────────────────────────

def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


def text(surf, s, size, center=None, midleft=None, midright=None,
         color=CREAM, shadow=(0, 0, 0, 150), track=0):
    f = font(size)
    if track:
        glyphs = [f.render(ch, True, color) for ch in s]
        tw = sum(g.get_width() for g in glyphs) + track * (len(s) - 1)
        th = f.get_height()
        img = pygame.Surface((max(1, tw), th), pygame.SRCALPHA)
        x = 0
        for ch, g in zip(s, glyphs):
            img.blit(g, (x, 0))
            x += g.get_width() + track
    else:
        img = f.render(s, True, color)
    rect = img.get_rect()
    if center:
        rect.center = center
    elif midleft:
        rect.midleft = midleft
    elif midright:
        rect.midright = midright
    if shadow:
        sh = img.copy()
        sh.fill((*shadow[:3], 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow[3])
        surf.blit(sh, (rect.x + 1, rect.y + 1))
    surf.blit(img, rect)
    return rect


def chip(surf, rect, radius=6, fill=(18, 15, 24), alpha=234,
         border=CREAM, border_a=54):
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s, (*fill, alpha), s.get_rect(), border_radius=radius)
    if border_a:
        pygame.draw.rect(s, (*border, border_a), s.get_rect(), width=1,
                         border_radius=radius)
    surf.blit(s, rect.topleft)


def soft_glow(radius, color, peak=110, falloff=2.0):
    """Additive glow — RGB premultiplied by brightness, blit with BLEND_ADD.
    BLEND_ADD ignores source alpha, so we premultiply the RGB channels directly
    rather than using an alpha ramp (which would blit as a flat disc)."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        f = (1 - (r / radius) ** falloff) * (peak / 255.0)
        s_col = (int(color[0] * f), int(color[1] * f), int(color[2] * f), 255)
        pygame.draw.circle(s, s_col, (c, c), r)
    return s


def alpha_line(surf, rgba, p0, p1, width=1):
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


# ── LAYER 1 · behind the canopy ──────────────────────────────────────────────

SKY_STOPS = [
    (0.00, (14, 18, 40)),
    (0.34, (30, 34, 62)),
    (0.62, (72, 62, 82)),
    (0.86, (150, 106, 90)),
    (1.00, (206, 150, 98)),
]

GROUND_STOPS = [
    (0.00, (58, 40, 34)),
    (0.28, (40, 29, 27)),
    (1.00, (14, 12, 16)),
]


def draw_backdrop(surf):
    """Sky above horizon, dark ground below, low amber bloom at horizon."""
    for y in range(HORIZON_Y):
        c = lerp_color_multi(SKY_STOPS, y / (HORIZON_Y - 1))
        pygame.draw.line(surf, c, (0, y), (W - 1, y))
    gh = H - HORIZON_Y
    for i in range(gh):
        c = lerp_color_multi(GROUND_STOPS, i / (gh - 1))
        pygame.draw.line(surf, c, (0, HORIZON_Y + i), (W - 1, HORIZON_Y + i))

    bloom = pygame.Surface((W, 40), pygame.SRCALPHA)
    for x in range(W):
        fx = 1.0 - 0.55 * min(1.0, abs(x - 128) / 240.0)
        for i in range(38):
            f = 0.30 * fx * (1 - i / 38) ** 2.1
            bloom.set_at((x, 37 - i),
                         (int(228 * f), int(158 * f), int(96 * f), 255))
    surf.blit(bloom, (0, HORIZON_Y - 38), special_flags=pygame.BLEND_ADD)
    pygame.draw.line(surf, (196, 146, 100), (0, HORIZON_Y - 1), (W - 1, HORIZON_Y - 1))
    pygame.draw.line(surf, (26, 20, 20), (0, HORIZON_Y), (W - 1, HORIZON_Y))


# ── AD note 4 · refraction where fat runners cross horizon ───────────────────

def apply_refraction(surf, fat_streaks_1x):
    """Nudge horizon pixel columns left/right inside each fat runner's x-band.

    A water-filled bead acts as a cylinder lens: it shifts the image sideways
    rather than magnifying it vertically.  The effect is subtle (2-3px) but
    breaks the razor-sharp horizon line in a physically plausible way.
    """
    tmp = surf.copy()
    rng_ref = random.Random(99)
    horiz_band = range(HORIZON_Y - 4, HORIZON_Y + 8)
    for sk in fat_streaks_1x:
        y_top = sk["y"]
        y_bot = y_top + sk["length"]
        if not (y_top < HORIZON_Y < y_bot):
            continue
        t = (HORIZON_Y - y_top) / sk["length"]
        x_at = sk["x"] + sk["lean"] * t
        half_w = sk["half_w"] + 1
        offset = rng_ref.choice([-3, -2, 2, 3])
        for col_x in range(int(x_at - half_w), int(x_at + half_w + 1)):
            if 0 <= col_x < W:
                for row_y in horiz_band:
                    if 0 <= row_y < H:
                        src_x = max(0, min(W - 1, col_x + offset))
                        surf.set_at((col_x, row_y), tmp.get_at((src_x, row_y)))


# ── AD note 6+7 · arc: warm tint, dotted-rail fade, soft bloom ───────────────

def draw_arc_behind(surf):
    """The r7 arc geometry at ~40% presence, with round-2 enhancements:

    - Dotted secondary arc fades to near-zero within 40px of the death marker
      (critique note 6 — clears air around the hero element).
    - Flown arc gets +10R +5G warm tint to read as refracted through moisture
      (critique note 7).
    - Very-soft BLEND_ADD bloom runs along the flown arc path, peak ~15
      (critique note 7 — makes arc glow through the rain layer).
    """
    u_death = ease(DEATH_PHASE)

    # AD7 — warm bloom behind the flown arc (drawn direct to surf, below lines)
    for i in range(32):
        u = u_death * i / 32
        bx, by = pos_u(u)
        g = soft_glow(10, (255, 200, 90), peak=15, falloff=2.0)
        surf.blit(g, (int(bx) - 11, int(by) - 11), special_flags=pygame.BLEND_ADD)

    lay = pygame.Surface((W, H), pygame.SRCALPHA)

    # Cool remainder of the day
    steps = 120
    for i in range(steps):
        u0 = u_death + (1.0 - u_death) * i / steps
        u1 = u_death + (1.0 - u_death) * (i + 1) / steps
        t = i / (steps - 1)
        a = int(96 - 54 * t)
        pygame.draw.line(lay, (*SLATE, a), pos_u(u0), pos_u(u1), 4)
        pygame.draw.line(lay, (*COOL, int(a * 0.85)), pos_u(u0), pos_u(u1), 2)

    # AD6 — dotted event rail with fade near death marker
    for i in range(0, 181):
        u = i / 180
        x, y = pos_u(u, R_INNER)
        dist_to_death = math.hypot(x - DEATH_X, y - DEATH_Y)
        # Fade to near-zero within 40px radius of death point
        fade = max(0.0, min(1.0, (dist_to_death - 8.0) / 32.0))
        base_a = 62 if u <= u_death else 26
        a = int(base_a * fade)
        if a > 0:
            col = (255, 226, 176, a) if u <= u_death else (176, 190, 214, a)
            pygame.draw.circle(lay, col, (int(x), int(y)), 1)

    # AD7 — flown arc, warm gold tint (+10R +5G relative to GOLD baseline)
    warm_lo = (224, 153, 74)   # was (214, 148, 74)
    warm_hi = (255, 219, 158)  # was (255, 214, 158); R already clamped at 255
    for i in range(72):
        u0 = u_death * i / 72
        u1 = u_death * (i + 1) / 72
        t = i / 71
        col = lerp_color(warm_lo, warm_hi, t ** 0.75)
        pygame.draw.line(lay, (*col, int(120 + 60 * t)), pos_u(u0), pos_u(u1),
                         int(3 + 2 * t))
    for i in range(72):
        u0 = u_death * i / 72
        u1 = u_death * (i + 1) / 72
        t = i / 71
        pygame.draw.line(lay, (255, 249, 218, int(60 + 70 * t)),
                         pos_u(u0), pos_u(u1), 1)

    # Terminals
    lx, ly = pos_u(0.0)
    pygame.draw.polygon(lay, (255, 226, 168, 150),
                        [(lx, ly - 4), (lx + 3, ly), (lx, ly + 4), (lx - 3, ly)])
    rx, ry = pos_u(1.0)
    pygame.draw.polygon(lay, (*COOL, 130),
                        [(rx, ry - 5), (rx + 4, ry), (rx, ry + 5), (rx - 4, ry)])

    surf.blit(lay, (0, 0))


UNREACHED = [
    (CLOWN_PHASE, R_INNER, CLOWN_C),
    (RAIN_PHASE, R_INNER - 22, RAIN_C),
    (SNOW_PHASE, R_INNER, SNOW_C),
]


def draw_events_behind(surf):
    """Phase events as dim hue-tinted dots behind the rain layer."""
    lay = pygame.Surface((W, H), pygame.SRCALPHA)
    gx, gy = arc_pos(0.167, R_INNER)
    pygame.draw.circle(lay, (*GEYSER_C, 150), (int(gx), int(gy)), 3)
    pygame.draw.circle(lay, (*GEYSER_C, 70),  (int(gx), int(gy)), 6, width=1)
    for p, rad, col in UNREACHED:
        x, y = arc_pos(p, rad)
        pygame.draw.circle(lay, (*col, 62), (int(x), int(y)), 6, width=1)
        if rad != R_INNER:
            ax, ay = arc_pos(p, R_INNER)
            pygame.draw.line(lay, (*col, 34), (ax, ay), (x, y), 1)
    surf.blit(lay, (0, 0))
    for p, rad, col in UNREACHED:
        x, y = arc_pos(p, rad)
        text(surf, "?", 11, center=(int(x), int(y)),
             color=tuple(c // 3 for c in col), shadow=None)


# ── streak generation (shared by canopy + refraction) ────────────────────────

def generate_streaks():
    """Pre-generate all 110 streak records at SS and 1x coordinates.

    Fat runners (8-9 of them) cross ~1/3 of the screen height and are used
    by apply_refraction() as well as draw_canopy().

    Angles steepened per AD note 2:
      apex  (top 33%)  → 38-45° from vertical
      mid   (33-66%)   → 30-40°
      lower (66-100%)  → 25-35°

    lean_sign: 70% rightward, 30% leftward (variable crosswind feel).
    """
    rng  = random.Random(42)
    SW, SH = W * SS, H * SS
    fat_count = 0
    streaks   = []

    for i in range(110):
        x_ss      = rng.uniform(-10, SW + 10)
        bias_roll = rng.random()
        y_ss      = rng.uniform(0, SH * 0.66) if bias_roll < 0.72 \
                    else rng.uniform(SH * 0.66, SH)

        # Always consume the fat-roll for a deterministic RNG sequence
        fat_roll = rng.random()
        is_fat   = (fat_count < 9) and (i >= 10) and (fat_roll < 0.22)

        if is_fat:
            fat_count  += 1
            # Fat runners cross at least 1/3 of screen height
            length_ss  = rng.uniform(SH / 3.0, SH / 2.5)
            # 3-4px wide at 1x  →  9-12 SS pixels
            wid_ss     = rng.choice([9, 12])
            alpha_peak = rng.randint(35, 55)
        else:
            # Regular streaks: same length envelope as round 1
            length_ss  = rng.uniform(20, 90)
            # 1px most (65%), 2px some (35%) at 1x  →  3 or 6 SS px
            wid_ss     = 3 if rng.random() < 0.65 else 6
            alpha_peak = rng.randint(18, 50)

        # Angle from vertical: steeper at apex, shallower toward bottom
        y_frac = y_ss / SH
        if y_frac < 0.33:
            angle_deg = rng.uniform(38, 45)
        elif y_frac < 0.66:
            angle_deg = rng.uniform(30, 40)
        else:
            angle_deg = rng.uniform(25, 35)

        angle_rad = math.radians(angle_deg)
        lean_sign = 1 if rng.random() < 0.70 else -1
        lean_ss   = int(length_ss * math.tan(angle_rad)) * lean_sign

        streaks.append({
            # SS-space (for canopy drawing)
            "x": x_ss, "y": y_ss,
            "length": length_ss, "lean": lean_ss,
            "wid": wid_ss, "alpha_peak": alpha_peak, "is_fat": is_fat,
            # 1x-space (for refraction)
            "x_1x": x_ss / SS, "y_1x": y_ss / SS,
            "length_1x": length_ss / SS, "lean_1x": lean_ss / SS,
            "half_w": wid_ss / (2.0 * SS),
        })

    return streaks


# ── LAYER 2 · the canopy ─────────────────────────────────────────────────────

def draw_canopy(surf, streaks):
    """110 rain streaks on one 3× SRCALPHA surface, resolved with smoothscale.

    AD notes 2+3 implemented here:
      - Steep angles (25-45° from vertical, from generate_streaks()).
      - Each streak tapers from bright bead at the leading lower-right end
        to invisible at the trailing upper end.
      - Width variety: most 1px, some 2px, 8-9 fat runners 3-4px.
    """
    lay = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)

    for sk in streaks:
        # Tail (upper) → bead (lower-right) in SS coordinates
        x0 = sk["x"]
        y0 = sk["y"]
        x1 = x0 + sk["lean"]
        y1 = y0 + sk["length"]
        wid        = sk["wid"]
        alpha_peak = sk["alpha_peak"]
        is_fat     = sk["is_fat"]

        # Segment count: enough for a smooth alpha ramp
        seg_count = max(6, int(sk["length"] / 10)) if not is_fat \
                    else max(14, int(sk["length"] / 8))

        # Draw taper from tail (t=0, alpha=0) to bead (t=1, alpha_peak)
        for seg in range(seg_count):
            t  = seg / (seg_count - 1)    # 0 = tail, 1 = bead
            a  = int(alpha_peak * (t ** 0.65))
            if a < 2:
                continue
            px0 = int(x0 + (x1 - x0) * max(0, t - 1 / seg_count))
            py0 = int(y0 + (y1 - y0) * max(0, t - 1 / seg_count))
            px1 = int(x0 + (x1 - x0) * t)
            py1 = int(y0 + (y1 - y0) * t)
            pygame.draw.line(lay, (*RAIN_C, a), (px0, py0), (px1, py1),
                             max(1, wid))

        # Bright bead at the leading end
        bead_r = max(1, wid // 2 + 2)
        bead_a = min(255, alpha_peak + 30)
        pygame.draw.circle(lay, (*SNOW_C, bead_a),
                           (int(x1), int(y1)), bead_r)
        # Specular highlight on bead (1px brighter kernel)
        if bead_r > 1:
            pygame.draw.circle(lay, (255, 255, 255, min(255, bead_a + 20)),
                               (int(x1) - 1, int(y1) - 1), max(1, bead_r - 1))

    # Standalone sessile beads (water that has stopped running)
    rng_bead = random.Random(17)
    for _ in range(20):
        bx = rng_bead.uniform(0, W * SS)
        by = rng_bead.uniform(0, H * SS * 0.9)
        br = rng_bead.choice([3, 4, 5, 6])
        pygame.draw.circle(lay, (*SNOW_C, 60), (int(bx), int(by)), br)

    surf.blit(pygame.transform.smoothscale(lay, (W, H)), (0, 0))


# ── AD note 1 · rebuilt specular rake ────────────────────────────────────────

def draw_specular(surf):
    """Wide raking specular highlight.

    AD note 1 requirements:
    - 8-14px wide at 1x output
    - Peak alpha ~14 (additive channels, not transparency)
    - Runs corner-to-corner off canvas edges
    - Gaussian cross-section: bright ~1px core, soft 5-6px shoulders at half α
    - Slight curve (convex canopy curves away from viewer → midpoint bows down)
    - Shallower angle than streaks (~22° from horizontal vs streaks at 55-65°)
    - NOT parallel to leader line (~48° from horizontal)

    Implementation: layered polylines at 3× SS from outside-in (wide/faint →
    narrow/bright), smoothscaled to 1×, BLEND_ADD.
    """
    sw, sh = W * SS, H * SS

    # Endpoints: off-canvas left-edge to off-canvas right-edge
    # Slope ≈ (780-120)/(1320-(-240)) = 660/1560 ≈ 0.42 → ~22.8° from horizontal
    x0_ss, y0_ss = -240,  120
    x1_ss, y1_ss = sw + 240, 780

    # Slight downward bow at the midpoint (curved canopy effect)
    # Straight midpoint: (540, 450) → bowed to (540, 498) = 48px SS lower
    mid_x = (x0_ss + x1_ss) / 2
    mid_y = (y0_ss + y1_ss) / 2 + 48

    # Build quadratic bezier polyline
    steps = 64
    pts = []
    for i in range(steps + 1):
        t  = i / steps
        qx = (1 - t) ** 2 * x0_ss + 2 * t * (1 - t) * mid_x + t ** 2 * x1_ss
        qy = (1 - t) ** 2 * y0_ss + 2 * t * (1 - t) * mid_y + t ** 2 * y1_ss
        pts.append((int(qx), int(qy)))

    lay = pygame.Surface((sw, sh), pygame.SRCALPHA)

    if len(pts) > 1:
        # Gaussian profile: draw from wide/faint to narrow/bright.
        # Each pass overwrites the center of the previous, building a smooth ramp.
        # Colors are the additive RGB amounts that land on the 1x canvas after
        # smoothscale.  BLEND_ADD adds these RGB values directly (alpha ignored).
        #
        # Target 1x profile (measured from centre):
        #   outer shoulder  (±7-12 px at 1x = ±21-36 SS)  → add +5
        #   inner shoulder  (±4-7 px at 1x = ±12-21 SS)   → add +9
        #   body            (±2-4 px at 1x = ±6-12 SS)    → add +14
        #   core            (±1-2 px at 1x = ±3-6 SS)     → add +22
        #   bright spike    (center 1 SS px)               → add +30
        for color, width_ss in [
            ((5,  5,  6,  255), 72),   # outer shoulder  ≈ 12px at 1x each side
            ((9,  9,  10, 255), 42),   # inner shoulder  ≈  7px at 1x each side
            ((14, 14, 16, 255), 24),   # body            ≈  4px at 1x each side
            ((22, 22, 24, 255),  9),   # core            ≈  1.5px at 1x each side
            ((30, 30, 33, 255),  3),   # bright spike    ≈  0.5px at 1x
        ]:
            for j in range(len(pts) - 1):
                pygame.draw.line(lay, color, pts[j], pts[j + 1], width_ss)

    scaled = pygame.transform.smoothscale(lay, (W, H))
    surf.blit(scaled, (0, 0), special_flags=pygame.BLEND_ADD)


# ── AD note 5 · edge scatter and bloom ───────────────────────────────────────

def draw_vignette_and_bloom(surf):
    """Perimeter treatment — three layers.

    1. Corner vignette (dark, opaque overlay): drawn at 90×160, smoothscaled.
    2. Top-edge sky bloom (additive, sky light scattering through droplets):
       drawn at 36×8, smoothscaled to 360×80.
    3. Mid-edge side glow (very faint additive brightening at left/right centres):
       drawn at 5×64, smoothscaled to 25×640.

    Small source sizes avoid 230k+ set_at calls — the softness is free from
    smoothscale rather than per-pixel feathering.
    """
    # ── 1. corner vignette ───────────────────────────────────────────────────
    vw, vh = 90, 160
    v = pygame.Surface((vw, vh), pygame.SRCALPHA)
    cx_v, cy_v = vw / 2, vh / 2
    md = math.hypot(cx_v, cy_v)
    for y in range(vh):
        for x in range(vw):
            d = math.hypot(x - cx_v, y - cy_v) / md
            a = int(160 * max(0.0, (d - 0.35) / 0.65) ** 1.8)
            if a:
                v.set_at((x, y), (4, 6, 14, a))
    surf.blit(pygame.transform.smoothscale(v, (W, H)), (0, 0))

    # ── 2. top-edge sky bloom ────────────────────────────────────────────────
    tb_w, tb_h = 36, 8
    top_bloom = pygame.Surface((tb_w, tb_h), pygame.SRCALPHA)
    for y in range(tb_h):
        fall = (1 - y / tb_h) ** 2.8
        for x in range(tb_w):
            cx_d = abs(x - tb_w / 2) / (tb_w / 2)
            ef = (1 - cx_d * 0.65) * fall * 0.08
            if ef > 0.002:
                top_bloom.set_at(
                    (x, y),
                    (int(180 * ef), int(200 * ef), int(255 * ef), 255)
                )
    surf.blit(
        pygame.transform.smoothscale(top_bloom, (W, 80)),
        (0, 0),
        special_flags=pygame.BLEND_ADD
    )

    # ── 3. mid-edge side glow ────────────────────────────────────────────────
    sb_w, sb_h = 5, 64
    side_bloom_src = pygame.Surface((sb_w, sb_h), pygame.SRCALPHA)
    for x in range(sb_w):
        fx = (1 - x / sb_w) ** 3.0 * 0.055
        for y in range(sb_h):
            ym = abs(y - sb_h * 0.5) / (sb_h * 0.5)  # 0=mid, 1=edge
            fy = fx * max(0.0, 1 - ym * 1.2)
            if fy > 0.002:
                side_bloom_src.set_at(
                    (x, y),
                    (int(155 * fy), int(175 * fy), int(228 * fy), 255)
                )
    scaled_left = pygame.transform.smoothscale(side_bloom_src, (25, H))
    # Right side: mirror horizontally
    scaled_right = pygame.transform.flip(scaled_left, True, False)
    surf.blit(scaled_left,  (0, 0),      special_flags=pygame.BLEND_ADD)
    surf.blit(scaled_right, (W - 25, 0), special_flags=pygame.BLEND_ADD)


# ── death marker · in front of the canopy ────────────────────────────────────

def draw_death(surf):
    dx, dy = int(DEATH_X), int(DEATH_Y)
    for rad, col, peak in ((22, (255, 176, 74), 70),
                           (14, (255, 206, 92), 50),
                           (8,  (255, 232, 168), 35)):
        g = soft_glow(rad, col, peak=peak, falloff=2.0)
        surf.blit(g, (dx - rad - 1, dy - rad - 1), special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(surf, (*INK, 255), (dx, dy), 8)
    pygame.draw.circle(surf, GOLD, (dx, dy), 6)
    pygame.draw.circle(surf, (252, 246, 232), (dx - 1, dy - 1), 3)

    f10, f8 = font(10), font(8)
    body = f"PILLAR {DEATH_PILLAR}  ·  {PHASE_LABEL} 18.4%"
    cw = max(f10.size("ENDED HERE")[0], f8.size(body)[0]) + 20
    cr = pygame.Rect(0, 0, cw, 34)
    cr.topleft = (132, 322)

    alpha_line(surf, (10, 8, 14, 190), (dx + 6, dy + 7), (cr.x - 1, cr.y + 7), 3)
    alpha_line(surf, (255, 214, 140, 225), (dx + 6, dy + 6), (cr.x - 2, cr.y + 6), 1)

    chip(surf, cr, radius=7, alpha=238, border_a=72)
    text(surf, "ENDED HERE", 10, midleft=(cr.x + 10, cr.y + 11),
         color=GOLD, shadow=None)
    text(surf, body, 8, midleft=(cr.x + 10, cr.y + 24), color=CREAM, shadow=None)


# ── chrome ────────────────────────────────────────────────────────────────────

def draw_banner(surf):
    pygame.draw.rect(surf, SCRIM, (0, 0, W, 74))
    fade = pygame.Surface((W, 10), pygame.SRCALPHA)
    for i in range(10):
        fade.fill((*SCRIM, int(238 * (1 - i / 10) ** 1.4)), pygame.Rect(0, i, W, 1))
    surf.blit(fade, (0, 74))
    alpha_line(surf, (255, 206, 92, 150), (0, 74), (W - 1, 74), 1)
    text(surf, f"FLIGHT LOG  ·  DAY {DAY_N}", 21, center=(W // 2, 28),
         color=GOLD, track=3, shadow=None)
    text(surf, f"PILLAR {DEATH_PILLAR}   ·   0:{TIME_ALIVE:02d}", 12,
         center=(W // 2, 55), color=CREAM, shadow=None)


def draw_back(surf):
    pr = pygame.Rect(0, 0, 122, 36)
    pr.center = (180, 597)
    sh = pygame.Surface((pr.w + 8, pr.h + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 100), sh.get_rect(), border_radius=21)
    surf.blit(sh, (pr.x - 4, pr.y - 1))
    grad = pygame.Surface(pr.size, pygame.SRCALPHA)
    for y in range(pr.h):
        grad.fill(
            lerp_color((255, 228, 172), (226, 168, 96), y / (pr.h - 1)) + (255,),
            pygame.Rect(0, y, pr.w, 1)
        )
    mask = pygame.Surface(pr.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=18)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, pr.topleft)
    pygame.draw.rect(surf, (110, 68, 38), pr, width=1, border_radius=18)
    text(surf, "BACK", 13, center=(pr.centerx, pr.centery),
         color=(66, 40, 20), shadow=None, track=2)


# ── screen ────────────────────────────────────────────────────────────────────

def render_screen():
    surf = pygame.Surface((W, H))

    # Pre-generate streak data: shared between refraction + canopy drawing
    streaks = generate_streaks()
    fat_streaks_1x = [
        {
            "x":      sk["x_1x"],
            "y":      sk["y_1x"],
            "length": sk["length_1x"],
            "lean":   sk["lean_1x"],
            "half_w": sk["half_w"],
        }
        for sk in streaks if sk["is_fat"]
    ]

    # ── Layer 1 — world seen through glass ────────────────────────────────────
    draw_backdrop(surf)
    apply_refraction(surf, fat_streaks_1x)   # nudge horizon before arc
    draw_arc_behind(surf)                    # arc bloom then arc lines
    draw_events_behind(surf)

    # ── Layer 2 — the canopy ──────────────────────────────────────────────────
    draw_canopy(surf, streaks)
    draw_specular(surf)
    draw_vignette_and_bloom(surf)

    # ── In front of the glass ─────────────────────────────────────────────────
    draw_death(surf)

    # ── Chrome (always crisp) ─────────────────────────────────────────────────
    draw_banner(surf)
    draw_back(surf)

    return surf


def main():
    surf = render_screen()
    out = "/home/user/skybit/docs/flight_log_arc_v2/glass/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(surf, out)
    loaded = pygame.image.load(out)
    print(f"saved {out}  {loaded.get_size()}")


if __name__ == "__main__":
    main()
