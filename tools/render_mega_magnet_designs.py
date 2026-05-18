"""Render 5 MEGA MAGNET ("vacuum") activation-effect mockups for review.

The existing `vacuum` secret powerup (game/world.py:1262) is internally
the Mega Magnet: on pickup it snaps every uncollected coin on screen
to the bird over VACUUM_TRAVEL_TIME (0.4 s). This script proposes five
alternative on-activation visuals — what the screen does during that
0.4 s window — so we can pick a direction before touching the live code.

Each design is rendered as:
  * a single 360×640 "peak frame" hero shot (mid-animation, ~t=0.5)
  * a 4-frame motion strip (t=0.0, 0.33, 0.66, 1.0) showing the arc

A contact sheet places all five peaks side by side for at-a-glance review.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_mega_magnet_designs.py
"""

import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OUT = os.path.join(_REPO, "docs", "mega_magnet_designs")
os.makedirs(_OUT, exist_ok=True)

# ── viewport & palette mirrored from game/config.py + game/draw.py ──────────
W, H = 360, 640
BIRD_R = 14

SKY_TOP = (12, 18, 55)
SKY_MID = (25, 60, 130)
SKY_BOT = (40, 140, 210)
GROUND_TOP = (60, 190, 60)
GROUND_MID = (30, 140, 30)
GROUND_BOT = (80, 50, 20)
PIPE_HILIGHT = (110, 240, 110)
PIPE_MID = (45, 185, 45)
PIPE_DARK = (20, 100, 20)
COIN_GOLD = (255, 210, 20)
COIN_LIGHT = (255, 245, 120)
COIN_DARK = (200, 140, 0)
BIRD_RED = (240, 55, 55)
BIRD_BEAK = (255, 185, 0)
WHITE = (255, 255, 255)
UI_GOLD = (255, 215, 0)
UI_CREAM = (245, 230, 200)
UI_RED = (230, 40, 40)

GROUND_Y = 540  # top of ground band
BIRD_X, BIRD_Y = 110, 320

# Coins frozen at their "snapshot" positions (where they were when vacuum
# fired). Indexed across the screen at varying radii from the bird so the
# pull paths read distinctly. (sx, sy, glyph) — glyph is "C" for coin, "$"
# for a dollar variant (existing skin) for visual variety.
COIN_SNAPSHOTS = [
    (260, 200, "C"),
    (300, 290, "$"),
    (240, 380, "C"),
    (300, 440, "C"),
    (200, 250, "$"),
    (180, 460, "C"),
    (270, 130, "C"),
    (150, 410, "$"),
]


# ── primitive scene helpers ─────────────────────────────────────────────────


def _vgrad(surf, top, bot, y0, y1):
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / h
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t))
        pygame.draw.line(surf, c, (0, y0 + i), (W, y0 + i))


def draw_scene(surf):
    """Sky + ground + two pipes — neutral backdrop for every variant."""
    _vgrad(surf, SKY_TOP, SKY_MID, 0, 280)
    _vgrad(surf, SKY_MID, SKY_BOT, 280, GROUND_Y)
    _vgrad(surf, GROUND_TOP, GROUND_BOT, GROUND_Y, H)
    pygame.draw.line(surf, GROUND_MID, (0, GROUND_Y + 1), (W, GROUND_Y + 1), 2)
    # Two pipes framing the action — entry pipe behind bird, next pipe ahead.
    for px, gap_y in ((40, 340), (320, 280)):
        pipe_w = 56
        _draw_pipe(surf, px, gap_y, pipe_w, 110)


def _draw_pipe(surf, x, gap_y, w, gap_h):
    half = gap_h // 2
    # Top column
    top_r = pygame.Rect(x, 0, w, gap_y - half)
    bot_r = pygame.Rect(x, gap_y + half, w, GROUND_Y - (gap_y + half))
    for r in (top_r, bot_r):
        pygame.draw.rect(surf, PIPE_MID, r)
        pygame.draw.rect(surf, PIPE_DARK, r, 2)
        pygame.draw.line(surf, PIPE_HILIGHT, (r.x + 6, r.y), (r.x + 6, r.bottom), 3)
    # Caps
    cap_top = pygame.Rect(x - 4, gap_y - half - 14, w + 8, 14)
    cap_bot = pygame.Rect(x - 4, gap_y + half, w + 8, 14)
    for cap in (cap_top, cap_bot):
        pygame.draw.rect(surf, PIPE_MID, cap)
        pygame.draw.rect(surf, PIPE_DARK, cap, 2)


def draw_bird(surf, x, y, glow_col=None, glow_r=0):
    """Simplified red parrot circle with beak. Optional aura halo."""
    if glow_col is not None and glow_r > 0:
        halo = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
        for i in range(8, 0, -1):
            a = int(40 * (i / 8))
            pygame.draw.circle(halo, (*glow_col, a),
                               (glow_r + 2, glow_r + 2),
                               int(glow_r * i / 8))
        surf.blit(halo, (x - glow_r - 2, y - glow_r - 2),
                  special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.circle(surf, BIRD_RED, (x, y), BIRD_R)
    pygame.draw.circle(surf, (170, 25, 25), (x, y), BIRD_R, 2)
    # Belly
    pygame.draw.circle(surf, (255, 170, 50), (x + 1, y + 4), 6)
    # Beak
    pygame.draw.polygon(surf, BIRD_BEAK,
                        [(x + BIRD_R - 2, y - 3),
                         (x + BIRD_R + 8, y),
                         (x + BIRD_R - 2, y + 3)])
    # Eye
    pygame.draw.circle(surf, WHITE, (x + 4, y - 4), 3)
    pygame.draw.circle(surf, (0, 0, 0), (x + 5, y - 4), 1)


def draw_coin(surf, x, y, glyph="C", scale=1.0, trail=None, trail_col=None):
    """A small gold coin, optionally with a motion trail behind it."""
    r = int(7 * scale)
    if trail and trail_col is not None:
        for i, (tx, ty) in enumerate(trail):
            a = int(160 * (1 - i / max(1, len(trail))))
            t_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(t_surf, (*trail_col, a),
                               (r + 2, r + 2), max(1, r - i // 2))
            surf.blit(t_surf, (tx - r - 2, ty - r - 2),
                      special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.circle(surf, COIN_DARK, (x, y), r + 1)
    pygame.draw.circle(surf, COIN_GOLD, (x, y), r)
    pygame.draw.circle(surf, COIN_LIGHT, (x - 2, y - 2), max(1, r - 3))
    if glyph == "$":
        font = pygame.font.SysFont(None, max(10, r * 2))
        t = font.render("$", True, COIN_DARK)
        surf.blit(t, t.get_rect(center=(x, y)))


def lerp(a, b, t):
    return a + (b - a) * t


# ── path helpers (where coins are during the pull) ──────────────────────────


def coin_xy_linear(sx, sy, bx, by, t):
    return lerp(sx, bx, t), lerp(sy, by, t)


def coin_xy_spiral(sx, sy, bx, by, t, twist=2.2):
    # Decaying spiral: radial pull with a rotational component.
    dx, dy = sx - bx, sy - by
    base_a = math.atan2(dy, dx)
    base_r = math.hypot(dx, dy)
    a = base_a + twist * t
    r = base_r * (1 - t)
    return bx + math.cos(a) * r, by + math.sin(a) * r


def coin_xy_orbit_decay(sx, sy, bx, by, t):
    dx, dy = sx - bx, sy - by
    base_a = math.atan2(dy, dx)
    base_r = math.hypot(dx, dy)
    # Tighter spiral than the cyclone variant — orbital decay flavour.
    a = base_a + 3.1 * (t ** 0.85)
    r = base_r * ((1 - t) ** 1.4)
    return bx + math.cos(a) * r, by + math.sin(a) * r


# ── 1. SOLAR SHOCKWAVE — radial pulse with golden spokes ────────────────────


def render_solar_shockwave(surf, t):
    """Bold expanding gold rings + radial spoke trails. Solar palette."""
    bx, by = BIRD_X, BIRD_Y
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    # Subtle warm wash to focus the eye.
    overlay.fill((255, 200, 60, int(36 * (1 - abs(0.5 - t) * 1.6))))
    surf.blit(overlay, (0, 0))
    # 3 nested shockwave rings, staggered. Radius grows from 0 to ~520 px.
    for delay, col, width in ((0.00, (255, 230, 120), 6),
                              (0.12, (255, 200, 60), 4),
                              (0.24, (255, 170, 30), 3)):
        local = max(0.0, min(1.0, (t - delay) / max(1e-3, 1 - delay)))
        if local <= 0:
            continue
        r = int(520 * local)
        a = int(220 * (1 - local) ** 0.7)
        if a <= 0:
            continue
        ring = pygame.Surface((W + 40, H + 40), pygame.SRCALPHA)
        pygame.draw.circle(ring, (*col, a), (bx + 20, by + 20), r, width)
        surf.blit(ring, (-20, -20), special_flags=pygame.BLEND_RGBA_ADD)
    # 16 radial spoke trails fading outward — sun-ray feel.
    spokes = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(16):
        ang = i * (math.tau / 16)
        for k in range(8):
            r1 = 20 + k * 16
            r2 = r1 + 12
            x1, y1 = bx + math.cos(ang) * r1, by + math.sin(ang) * r1
            x2, y2 = bx + math.cos(ang) * r2, by + math.sin(ang) * r2
            a = int(150 * (1 - k / 8) * (1 - t * 0.5))
            pygame.draw.line(spokes, (255, 230, 130, a),
                             (x1, y1), (x2, y2), 2)
    surf.blit(spokes, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # Coins pulled linearly toward bird with short spoke trails.
    for sx, sy, glyph in COIN_SNAPSHOTS:
        cx, cy = coin_xy_linear(sx, sy, bx, by, t)
        trail = []
        for k in range(1, 5):
            tk = max(0.0, t - 0.04 * k)
            tx, ty = coin_xy_linear(sx, sy, bx, by, tk)
            trail.append((int(tx), int(ty)))
        draw_coin(surf, int(cx), int(cy), glyph,
                  trail=trail, trail_col=(255, 230, 130))
    # Bright core flash on bird.
    core = pygame.Surface((90, 90), pygame.SRCALPHA)
    flash_a = int(220 * (1 - abs(0.4 - t) * 1.6))
    flash_a = max(0, flash_a)
    pygame.draw.circle(core, (255, 250, 200, flash_a), (45, 45), 36)
    pygame.draw.circle(core, (255, 230, 100, min(255, flash_a + 30)),
                       (45, 45), 22)
    surf.blit(core, (bx - 45, by - 45), special_flags=pygame.BLEND_RGBA_ADD)
    draw_bird(surf, bx, by, glow_col=(255, 220, 80), glow_r=22)


# ── 2. GOLDEN CYCLONE — spiraling tornado, evolves the existing icon ────────


def render_golden_cyclone(surf, t):
    """Funnel of swirling gold particles; coins corkscrew inward."""
    bx, by = BIRD_X, BIRD_Y
    # Soft amber wash, peaks mid-animation.
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((230, 160, 30, int(28 * math.sin(math.pi * t))))
    surf.blit(overlay, (0, 0))
    # Three nested swirl bands of particles.
    swirl = pygame.Surface((W, H), pygame.SRCALPHA)
    rng = random.Random(7)
    for band_idx, (r_base, count, col) in enumerate((
            (110, 40, (255, 230, 120)),
            (75,  32, (255, 200, 60)),
            (45,  24, (255, 170, 30)))):
        for j in range(count):
            jitter = rng.uniform(-8, 8)
            ang0 = rng.uniform(0, math.tau)
            ang = ang0 + t * (4.5 + band_idx * 0.6) + band_idx * 0.5
            rr = max(6, r_base + jitter - 30 * t)
            x = bx + math.cos(ang) * rr
            y = by + math.sin(ang) * rr * 0.85  # vertical squash
            a = int(180 * (1 - t * 0.3))
            pygame.draw.circle(swirl, (*col, a), (int(x), int(y)),
                               rng.choice((1, 2, 2, 3)))
    surf.blit(swirl, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # Three rotating elliptical bands — funnel skeleton.
    for i, (rw, rh, alpha, phase) in enumerate((
            (105, 88, 130, 0.0),
            (78, 66, 150, 0.7),
            (52, 44, 170, 1.4))):
        ang_deg = math.degrees(t * 7 + phase) + 18 * i
        band = pygame.Surface((rw * 2 + 8, rh * 2 + 8), pygame.SRCALPHA)
        pygame.draw.ellipse(band, (255, 220, 120, alpha),
                            pygame.Rect(2, 2, rw * 2, rh * 2), 3)
        pygame.draw.ellipse(band, (255, 240, 200, alpha // 2),
                            pygame.Rect(4, 4, rw * 2 - 4, rh * 2 - 4), 1)
        rot = pygame.transform.rotate(band, ang_deg)
        surf.blit(rot, rot.get_rect(center=(bx, by - 4)),
                  special_flags=pygame.BLEND_RGBA_ADD)
    # Coins follow a spiral inward — each leaves a curving trail.
    for sx, sy, glyph in COIN_SNAPSHOTS:
        cx, cy = coin_xy_spiral(sx, sy, bx, by, t, twist=2.8)
        trail = []
        for k in range(1, 6):
            tk = max(0.0, t - 0.035 * k)
            tx, ty = coin_xy_spiral(sx, sy, bx, by, tk, twist=2.8)
            trail.append((int(tx), int(ty)))
        draw_coin(surf, int(cx), int(cy), glyph,
                  trail=trail, trail_col=(255, 215, 80))
    draw_bird(surf, bx, by, glow_col=(255, 200, 60), glow_r=20)


# ── 3. ELECTROMAGNETIC FIELD — sci-fi lightning to each coin ────────────────


def _jagged_polyline(rng, x1, y1, x2, y2, segs=6, jitter=10):
    pts = [(x1, y1)]
    for i in range(1, segs):
        t = i / segs
        cx = lerp(x1, x2, t) + rng.uniform(-jitter, jitter)
        cy = lerp(y1, y2, t) + rng.uniform(-jitter, jitter)
        pts.append((cx, cy))
    pts.append((x2, y2))
    return pts


def render_electromagnetic_field(surf, t):
    """Cyan lightning bolts arc from bird to each coin; tech HUD vibe."""
    bx, by = BIRD_X, BIRD_Y
    # Cool ozone tint pulses on activation.
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((60, 180, 230, int(40 * math.sin(math.pi * t))))
    surf.blit(overlay, (0, 0))
    # Faint hexagonal field grid behind bird — readable as "field".
    grid = pygame.Surface((W, H), pygame.SRCALPHA)
    hex_r = 18
    for hy in range(by - 140, by + 140, int(hex_r * 1.5)):
        for hx in range(bx - 140, bx + 220, int(hex_r * math.sqrt(3))):
            offset = (hy // int(hex_r * 1.5)) % 2
            cx = hx + (0 if offset == 0 else int(hex_r * math.sqrt(3) / 2))
            dist = math.hypot(cx - bx, hy - by)
            if dist > 160:
                continue
            a = int(80 * (1 - dist / 160) * (1 - t * 0.4))
            pts = [(cx + math.cos(math.pi / 6 + math.pi / 3 * k) * hex_r,
                    hy + math.sin(math.pi / 6 + math.pi / 3 * k) * hex_r)
                   for k in range(6)]
            pygame.draw.polygon(grid, (80, 220, 240, a), pts, 1)
    surf.blit(grid, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # Lightning bolt from bird to each coin's current position.
    rng = random.Random(int(t * 60))
    bolts = pygame.Surface((W, H), pygame.SRCALPHA)
    for sx, sy, glyph in COIN_SNAPSHOTS:
        cx, cy = coin_xy_linear(sx, sy, bx, by, t)
        # Glow halo
        for w, a in ((6, 70), (3, 160), (1, 240)):
            pts = _jagged_polyline(rng, bx, by, cx, cy, segs=7, jitter=9)
            pygame.draw.lines(bolts, (160, 240, 255, a), False, pts, w)
        # Hot white core
        pts = _jagged_polyline(rng, bx, by, cx, cy, segs=7, jitter=4)
        pygame.draw.lines(bolts, (240, 250, 255, 250), False, pts, 1)
    surf.blit(bolts, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # Coins themselves — short cyan trails to match.
    for sx, sy, glyph in COIN_SNAPSHOTS:
        cx, cy = coin_xy_linear(sx, sy, bx, by, t)
        trail = []
        for k in range(1, 4):
            tk = max(0.0, t - 0.04 * k)
            tx, ty = coin_xy_linear(sx, sy, bx, by, tk)
            trail.append((int(tx), int(ty)))
        draw_coin(surf, int(cx), int(cy), glyph,
                  trail=trail, trail_col=(140, 230, 255))
    # Bird core: cyan-white electric flash.
    core = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.circle(core, (180, 240, 255, 200), (40, 40), 30)
    pygame.draw.circle(core, (240, 255, 255, 220), (40, 40), 16)
    surf.blit(core, (bx - 40, by - 40), special_flags=pygame.BLEND_RGBA_ADD)
    draw_bird(surf, bx, by, glow_col=(120, 220, 255), glow_r=22)


# ── 4. GRAVITY WELL — cosmic implosion with orbital decay ───────────────────


def render_gravity_well(surf, t):
    """Dark accretion disc + curving orbital paths. Cosmic palette."""
    bx, by = BIRD_X, BIRD_Y
    # Vignette to focus attention on the well.
    vign = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(60, 0, -1):
        a = int(140 * (1 - i / 60))
        pygame.draw.circle(vign, (5, 5, 25, a),
                           (bx, by), 60 + i * 8)
    surf.blit(vign, (0, 0))
    # Accretion disc: dark purple-blue with magenta corona.
    well_r = int(56 + 14 * math.sin(math.pi * t))
    well = pygame.Surface((well_r * 2 + 20, well_r * 2 + 20), pygame.SRCALPHA)
    # Corona rings
    for i in range(8, 0, -1):
        rr = int(well_r * i / 8)
        col = (
            int(lerp(40, 220, i / 8)),
            int(lerp(20, 70, i / 8)),
            int(lerp(80, 200, i / 8)),
        )
        a = int(200 * (1 - (i / 8) ** 0.7))
        pygame.draw.circle(well, (*col, a), (well_r + 10, well_r + 10), rr)
    # Black core
    pygame.draw.circle(well, (5, 5, 20, 255),
                       (well_r + 10, well_r + 10), max(8, well_r - 20))
    # Bright accretion edge
    pygame.draw.circle(well, (255, 200, 255, 220),
                       (well_r + 10, well_r + 10), well_r - 18, 2)
    surf.blit(well, (bx - well_r - 10, by - well_r - 10))
    # Spiraling tracer dots — sense of orbiting matter.
    tracers = pygame.Surface((W, H), pygame.SRCALPHA)
    rng = random.Random(42)
    for j in range(70):
        ang = rng.uniform(0, math.tau) + t * 4.5
        r = rng.uniform(20, 130) * (1 - t * 0.6)
        x = bx + math.cos(ang) * r
        y = by + math.sin(ang) * r * 0.95
        col = (rng.choice(((220, 160, 255), (180, 120, 240), (140, 220, 255))))
        pygame.draw.circle(tracers, (*col, 200), (int(x), int(y)), 1)
    surf.blit(tracers, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # Coins on orbital-decay paths.
    for sx, sy, glyph in COIN_SNAPSHOTS:
        cx, cy = coin_xy_orbit_decay(sx, sy, bx, by, t)
        trail = []
        for k in range(1, 6):
            tk = max(0.0, t - 0.03 * k)
            tx, ty = coin_xy_orbit_decay(sx, sy, bx, by, tk)
            trail.append((int(tx), int(ty)))
        draw_coin(surf, int(cx), int(cy), glyph,
                  trail=trail, trail_col=(220, 160, 255))
    draw_bird(surf, bx, by, glow_col=(200, 130, 255), glow_r=24)


# ── 5. HORSESHOE STRIKE — cartoony classic horseshoe stamp ──────────────────


def _draw_horseshoe(surf, cx, cy, scale, alpha):
    """Classic red+white U-shaped horseshoe magnet, alpha-blended.

    Built as a single filled polygon (outer U traced clockwise, then inner U
    traced counter-clockwise) so there are no cutout-blend artifacts.
    """
    R_out = 30 * scale
    R_in = 18 * scale
    leg_h = 26 * scale
    s_w = int(R_out * 2 + 12)
    s_h = int(R_out + leg_h + 14)
    s = pygame.Surface((s_w, s_h), pygame.SRCALPHA)
    ox, oy = s_w // 2, int(R_out + 6)  # center inside scratch surf
    # Trace the U as a single closed polygon: outer arc (left→top→right),
    # down right outer leg, across to right inner pole, inner arc back
    # (right→top→left), down left inner leg, back out to left outer tip.
    # Sweep θ from 0 to π with dx = -R·cos θ, dy = -R·sin θ so the arc's
    # apex sits ABOVE oy (smaller y in screen-y-down).
    pts = []
    steps = 48
    for i in range(steps + 1):
        ang = math.pi * i / steps
        pts.append((ox - R_out * math.cos(ang),
                    oy - R_out * math.sin(ang)))
    pts.append((ox + R_out, oy + leg_h))
    pts.append((ox + R_in, oy + leg_h))
    for i in range(steps + 1):
        ang = math.pi - (math.pi * i / steps)
        pts.append((ox - R_in * math.cos(ang),
                    oy - R_in * math.sin(ang)))
    pts.append((ox - R_in, oy + leg_h))
    pts.append((ox - R_out, oy + leg_h))
    pygame.draw.polygon(s, (220, 30, 30, alpha), pts)
    pygame.draw.polygon(s, (90, 0, 0, alpha), pts, 2)
    # White pole caps under each leg
    pole_w = int((R_out - R_in))
    pole_h = int(10 * scale)
    py = int(oy + leg_h - 2)
    for lx in (int(ox - R_out), int(ox + R_in)):
        cap = pygame.Rect(lx, py, pole_w, pole_h)
        pygame.draw.rect(s, (245, 245, 245, alpha), cap)
        pygame.draw.rect(s, (90, 0, 0, alpha), cap, 2)
    # N/S labels (only readable at larger scale)
    if scale >= 1.2:
        font = pygame.font.SysFont(None, max(10, int(14 * scale)))
        for label, lx in (("N", int(ox - R_out) + pole_w // 2),
                          ("S", int(ox + R_in) + pole_w // 2)):
            t = font.render(label, True, (60, 60, 60))
            s.blit(t, t.get_rect(center=(lx, py + pole_h // 2)))
    surf.blit(s, s.get_rect(center=(cx, cy)))


def render_horseshoe_strike(surf, t):
    """Giant cartoon horseshoe stamps in; gold speed-line streaks."""
    bx, by = BIRD_X, BIRD_Y
    # Brief flash on impact at start, then fades.
    flash_a = int(180 * max(0, 1 - t * 1.6))
    if flash_a > 0:
        flash = pygame.Surface((W, H), pygame.SRCALPHA)
        flash.fill((255, 255, 230, flash_a))
        surf.blit(flash, (0, 0))
    # Speed-line streaks from coin start positions toward bird.
    streaks = pygame.Surface((W, H), pygame.SRCALPHA)
    for sx, sy, _ in COIN_SNAPSHOTS:
        cx, cy = coin_xy_linear(sx, sy, bx, by, t)
        # Bold gold streak with darker outline.
        for w, col, a in ((6, (90, 60, 0), 200),
                          (4, (255, 200, 30), 230),
                          (2, (255, 250, 200), 250)):
            pygame.draw.line(streaks, (*col, a),
                             (sx, sy), (cx, cy), w)
    surf.blit(streaks, (0, 0))
    # Comic-style starburst behind the bird — spiky, transient.
    burst = pygame.Surface((W, H), pygame.SRCALPHA)
    burst_outer = int(120 + 20 * math.sin(math.pi * t))
    burst_inner = int(burst_outer * 0.55)
    burst_a = int(140 * math.sin(math.pi * t))
    points = []
    for i in range(20):
        ang = i * (math.tau / 20) - math.pi / 2
        rr = burst_outer if i % 2 == 0 else burst_inner
        points.append((bx + math.cos(ang) * rr, by + math.sin(ang) * rr))
    pygame.draw.polygon(burst, (255, 240, 80, max(0, burst_a)), points)
    pygame.draw.polygon(burst, (220, 30, 30, max(0, burst_a + 60)), points, 3)
    surf.blit(burst, (0, 0))
    # The horseshoe itself: enters from above, settles on bird, then pops.
    if t < 0.35:
        # Enter
        ease = t / 0.35
        scale = 0.6 + 1.4 * ease
        cy_offset = -120 * (1 - ease)
        alpha = int(255 * ease)
        _draw_horseshoe(surf, bx, by + cy_offset, scale, alpha)
    elif t < 0.75:
        # Pulse
        beat = 0.5 + 0.5 * math.sin((t - 0.35) * math.pi * 6)
        scale = 1.8 + 0.25 * beat
        _draw_horseshoe(surf, bx, by, scale, 255)
    else:
        # Settle / fade
        ease = (1 - t) / 0.25
        scale = 1.8 + 0.4 * ease
        alpha = int(255 * ease)
        _draw_horseshoe(surf, bx, by, scale, alpha)
    # Comic "POW!" word marker
    if 0.15 < t < 0.85:
        font = pygame.font.SysFont(None, 44)
        pow_t = font.render("CLICK!", True, (255, 240, 80))
        # Drop shadow
        sh = font.render("CLICK!", True, (90, 0, 0))
        surf.blit(sh, sh.get_rect(center=(bx + 92, by - 50)))
        surf.blit(pow_t, pow_t.get_rect(center=(bx + 90, by - 52)))
    # Coins drawn last so they sit in front of the streaks.
    for sx, sy, glyph in COIN_SNAPSHOTS:
        cx, cy = coin_xy_linear(sx, sy, bx, by, t)
        draw_coin(surf, int(cx), int(cy), glyph)


# ── compositing & output ────────────────────────────────────────────────────


DESIGNS = (
    ("01_solar_shockwave",       "Solar Shockwave",       render_solar_shockwave),
    ("02_golden_cyclone",        "Golden Cyclone",        render_golden_cyclone),
    ("03_electromagnetic_field", "Electromagnetic Field", render_electromagnetic_field),
    ("04_gravity_well",          "Gravity Well",          render_gravity_well),
    ("05_horseshoe_strike",      "Horseshoe Strike",      render_horseshoe_strike),
)


def _label_banner(surf, title):
    band = pygame.Surface((W, 36), pygame.SRCALPHA)
    band.fill((0, 0, 0, 170))
    pygame.draw.line(band, (255, 215, 0), (0, 35), (W, 35), 2)
    font = pygame.font.SysFont(None, 28)
    t = font.render(title, True, (255, 240, 200))
    band.blit(t, t.get_rect(midleft=(12, 18)))
    surf.blit(band, (0, 0))


def render_frame(render_fn, t):
    surf = pygame.Surface((W, H))
    draw_scene(surf)
    render_fn(surf, t)
    return surf


def main():
    pygame.init()
    pygame.font.init()

    # Hero (peak) frames at t≈0.55 — past the kinetic midpoint so coins are
    # visibly partway home but the effect is still at full power.
    for slug, title, fn in DESIGNS:
        hero = render_frame(fn, 0.55)
        _label_banner(hero, title)
        pygame.image.save(hero, os.path.join(_OUT, f"{slug}.png"))

    # Motion strips: 4 frames (t = 0, .33, .66, 1.0) side by side.
    for slug, title, fn in DESIGNS:
        strip = pygame.Surface((W * 4, H))
        for i, tn in enumerate((0.0, 0.33, 0.66, 1.0)):
            frame = render_frame(fn, tn)
            font = pygame.font.SysFont(None, 22)
            stamp = pygame.Surface((W, 22), pygame.SRCALPHA)
            stamp.fill((0, 0, 0, 160))
            t_label = font.render(f"t={tn:.2f}", True, (255, 230, 130))
            stamp.blit(t_label, t_label.get_rect(midleft=(8, 11)))
            frame.blit(stamp, (0, H - 22))
            strip.blit(frame, (W * i, 0))
        _label_banner(strip, f"{title} — motion strip")
        pygame.image.save(strip, os.path.join(_OUT, f"{slug}_strip.png"))

    # Contact sheet: all 5 peaks side by side.
    sheet = pygame.Surface((W * 5, H))
    for i, (slug, title, fn) in enumerate(DESIGNS):
        frame = render_frame(fn, 0.55)
        _label_banner(frame, title)
        sheet.blit(frame, (W * i, 0))
    pygame.image.save(sheet, os.path.join(_OUT, "00_contact_sheet.png"))

    print(f"wrote {len(DESIGNS) * 2 + 1} images to {_OUT}")


if __name__ == "__main__":
    main()
