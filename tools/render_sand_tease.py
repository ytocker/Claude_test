"""SANDSTORM tease design round — 5 distinctive GROUND-UP dust-devils,
each a different visual LANGUAGE (not a reskin of the crude haboob).

Tease concept #2: the storm first announces itself with spinning
dust-devils lifting off the desert floor between the mountains, before
any wall. Five techniques to pick a LOOK from:

  1 bloom    volumetric soft-bloom column (painterly haze lobes)
  2 ribbon   helical airflow ribbons spiralling up the column
  3 swarm    granular particle swarm along a parametric vortex
  4 cel      bold cel/graphic swirl with clean edges + gust crescents
  5 wisp     turbulent feathery smoke-wisp vortex

Each is rendered at SS=4 then smoothscaled (smooth edges), kept
semi-transparent + subtle (it's a tease). Output: a comparison sheet,
individual full-frame panels, and a zoom crop per devil.

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_sand_tease
"""
import os
import math
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H, GROUND_Y, BIRD_X
from game.entities import Bird
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground
from game.weather import SAND_HORIZON

pygame.init()
pygame.display.set_mode((W, H))

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "wind_themes", "sandstorm", "tease")
os.makedirs(OUT_DIR, exist_ok=True)

SS = 4                       # supersample for smooth devils
TEASE_PHASE = 0.08           # bright day sky, early in the rise

# devil bounding canvas (display px) — base centred at the bottom
DW, DH = 220, 340
BASE_LX, BASE_LY = DW // 2, DH - 14    # local base anchor (display)


# ── small math helpers ───────────────────────────────────────────────────────
def smoothstep(a, b, x):
    if x <= a:
        return 0.0
    if x >= b:
        return 1.0
    t = (x - a) / (b - a)
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_col(c1, c2, t):
    return (int(lerp(c1[0], c2[0], t)),
            int(lerp(c1[1], c2[1], t)),
            int(lerp(c1[2], c2[2], t)))


_DISC_CACHE: dict = {}


def _disc(r, color, a, falloff):
    """Cached soft radial disc (alpha 0 at rim → a at centre)."""
    r = int(max(1, r))
    key = (r, color, a, round(falloff, 1))
    s = _DISC_CACHE.get(key)
    if s is not None:
        return s
    d = r * 2 + 2
    surf = pygame.Surface((d, d), pygame.SRCALPHA)
    c = r + 1
    steps = max(4, r // 2)
    for i in range(steps, 0, -1):
        rr = max(1, int(r * i / steps))
        frac = i / steps
        aa = int(a * (1.0 - frac) ** falloff)
        if aa > 0:
            pygame.draw.circle(surf, (*color, aa), (c, c), rr)
    _DISC_CACHE[key] = surf
    return surf


def soft_stamp(surf, x, y, r, color, a, falloff=1.5):
    """Blit a soft radial blob — uses alpha compositing so overlapping
    stamps BUILD UP density (drawing circles directly would replace
    alpha and erase neighbours)."""
    a = int(max(0, min(255, a)))
    if a <= 0:
        return
    a = (a // 6) * 6                       # quantise to bound the cache
    sp = _disc(int(max(1, r)), color, a, falloff)
    surf.blit(sp, (int(x) - sp.get_width() // 2, int(y) - sp.get_height() // 2))


def _spine(t, lean, wob_amp, wob_freq, seed, height):
    """Return (x, y) of the column centre at parameter t (0 base→1 top),
    in SS-display coords inside the devil surface."""
    bx = BASE_LX * SS
    by = BASE_LY * SS
    x = bx + lean * t * height + wob_amp * math.sin(t * wob_freq + seed) * (0.3 + t)
    y = by - t * height
    return x, y


def _col_r(t, base_r, col_w, top_w):
    """Radius profile: dense skirt at base, slim column, frayed top."""
    skirt = base_r * math.exp(-t * 8.0)
    body = col_w * (1.0 - 0.22 * t)
    fray = top_w * smoothstep(0.72, 1.0, t)
    return max(body, skirt) + fray


def _blit_devil(surf, big, cx, base_y, scale=1.0, alpha=255):
    """Smoothscale a SS devil surface down and blit so its base anchor
    sits at (cx, base_y). `alpha` (<255) fades the whole column for the
    'emerging' beat."""
    dw = int(DW * scale)
    dh = int(DH * scale)
    small = pygame.transform.smoothscale(big, (dw, dh))
    if alpha < 255:
        small.set_alpha(alpha)
    surf.blit(small, (int(cx - BASE_LX * scale), int(base_y - BASE_LY * scale)))


def _new_big():
    return pygame.Surface((DW * SS, DH * SS), pygame.SRCALPHA)


def _base_pool(big, color, a, w=58, h=20, seed=0):
    """A low, wide kicked-up dust pool at the column base (sells the
    ground-up read + the flare even when the base is behind a ridge)."""
    rng = random.Random(seed)
    bx = BASE_LX * SS
    by = BASE_LY * SS
    for _ in range(34):
        x = bx + rng.uniform(-w, w) * SS * (rng.random() ** 0.5) * (1 if rng.random() < 0.5 else -1)
        y = by - rng.uniform(-2, h) * SS
        r = rng.uniform(5, 13) * SS
        soft_stamp(big, x, y, r, color, int(a * rng.uniform(0.4, 1.0)))


# ── variant 1: volumetric bloom column (SPARSE + SWIRL) ───────────────────────
def devil_bloom(s, seed=11):
    """Airy, broken-up grit column — reads like the frayed TOP of the
    old bloom THROUGHOUT (see-through, gaps), with a clear helical
    swirl (front lobes brighter than back) so rotation reads."""
    rng = random.Random(seed)
    big = _new_big()
    height = (DH - 30) * SS
    lean = 0.07
    body = (176, 128, 82)
    shadow = (118, 84, 50)
    hi = (240, 212, 156)
    _base_pool(big, body, int(120 + s * 60), seed=seed)
    # faint cohesive underlay so the sparse grit reads as ONE column
    # (a ghost trunk), not a disconnected string of puffs
    for i in range(120):
        t = i / 120
        ux, uy = _spine(t, lean, 12 * SS, 3.0, seed, height)
        ur = _col_r(t, 26 * SS, 13 * SS, 9 * SS) * 0.85
        ua = int((30 + s * 28) * (1.0 - smoothstep(0.45, 1.05, t)))
        soft_stamp(big, ux, uy, ur, body, ua, falloff=1.6)
    turns = 2.5
    nlobes = int(170 + s * 150)
    a0 = int(74 + s * 70)
    for i in range(nlobes):
        t = rng.random() ** 0.9                       # fairly even → airy
        sx, sy = _spine(t, lean, 12 * SS, 3.0, seed, height)
        colr = _col_r(t, 30 * SS, 16 * SS, 11 * SS)
        ang = t * turns * 2 * math.pi + rng.uniform(-0.45, 0.45)
        depth = (math.sin(ang) + 1) * 0.5             # 0 back → 1 front
        rr = colr * (0.35 + 0.65 * rng.random())
        x = sx + math.cos(ang) * rr
        y = sy + rng.uniform(-1, 1) * 4 * SS
        lobe = rng.uniform(5, 11) * SS * (1.0 - 0.28 * t)
        a = int(a0 * (0.32 + 0.68 * depth) * (1.0 - smoothstep(0.6, 1.06, t)))
        col = hi if depth > 0.8 else (body if depth > 0.42 else shadow)
        soft_stamp(big, x, y, lobe, col, a, falloff=1.3)
    # extra frayed grit torn off the top
    for _ in range(int(30 * s) + 12):
        t = rng.uniform(0.55, 1.12)
        sx, sy = _spine(min(t, 1.0), lean, 12 * SS, 3.0, seed, height)
        x = sx + rng.uniform(-1, 1) * 30 * SS
        soft_stamp(big, x, sy - rng.uniform(0, 42) * SS,
                   rng.uniform(2, 4) * SS, body, int(a0 * 0.55))
    return big


# ── variant 2: helical airflow ribbons ───────────────────────────────────────
def devil_ribbon(s, seed=22):
    big = _new_big()
    height = (DH - 40) * SS
    lean = 0.08
    turns = 2.6
    low = (178, 134, 88)
    high = (216, 200, 178)
    a0 = int(135 + s * 90)
    _base_pool(big, low, int(150 + s * 70), w=40, seed=seed)
    N = 170
    for rib in range(3):
        ph = rib * (2 * math.pi / 3)
        for i in range(N + 1):
            t = i / N
            sx, sy = _spine(t, lean, 10 * SS, 2.4, seed, height)
            rad = _col_r(t, 26 * SS, 15 * SS, 7 * SS)
            ang = t * turns * 2 * math.pi + ph
            x = sx + math.cos(ang) * rad
            depth = (math.sin(ang) + 1) * 0.5          # 0 back → 1 front
            w = (7 * SS) * (0.4 + 0.6 * depth) * (1.0 - 0.28 * t)
            col = lerp_col(low, high, depth * 0.7 + t * 0.2)
            a = int(a0 * (0.3 + 0.7 * depth) * (1.0 - smoothstep(0.72, 1.06, t)))
            soft_stamp(big, x, sy, w, col, a, falloff=1.1)
    return big


# ── variant 3: granular particle swarm ───────────────────────────────────────
def devil_swarm(s, seed=33):
    rng = random.Random(seed)
    big = _new_big()
    height = (DH - 26) * SS
    lean = 0.12
    tones = [(150, 108, 64), (178, 134, 88), (116, 82, 50), (206, 174, 126)]
    n = int(11000 + s * 8000)
    a0 = 200
    for _ in range(n):
        t = rng.random() ** 1.8                         # denser at base
        sx, sy = _spine(t, lean, 11 * SS, 2.8, seed, height)
        # strong base flare → slim waist → slight fray at top (vortex)
        rad = (44 * SS) * math.exp(-t * 4.2) + (13 * SS) * (1.0 - 0.3 * t) \
            + (9 * SS) * smoothstep(0.7, 1.05, t)
        ang = rng.uniform(0, 2 * math.pi)
        rr = rad * (rng.random() ** 0.5)
        x = sx + math.cos(ang) * rr
        y = sy + math.sin(ang) * rr * 0.5               # elliptical cross-section
        depth = (math.sin(ang) + 1) * 0.5
        a = int(a0 * (0.28 + 0.72 * depth) * (1.0 - smoothstep(0.62, 1.06, t)))
        col = rng.choice(tones)
        pr = max(1, int(rng.uniform(0.8, 1.7) * SS))
        pygame.draw.circle(big, (*col, max(0, min(255, a))), (int(x), int(y)), pr)
    return big


# ── variant 4: cel / graphic swirl ───────────────────────────────────────────
def devil_cel(s, seed=44):
    """Classic cartoon whirlwind: a stack of bold 'swoosh' wind bands,
    widest at the base, narrowing up, each a thick crescent stroke with
    a dark outline + flat fill + a bright top highlight, small gaps of
    sky between them so it reads as spiralling wind (not a solid horn)."""
    big = _new_big()
    height = (DH - 36) * SS
    fill = (200, 162, 108)
    outline = (94, 62, 34)
    hi = (242, 220, 172)
    lean = 0.05
    a = int(210 + s * 45)
    bands = 13

    def band_w(t):
        return (40 * SS) * math.exp(-t * 1.7) + 7 * SS

    def swoosh_pts(cx, cy, w, curve):
        pts = []
        for j in range(9):
            u = j / 8
            px = cx - w + 2 * w * u
            py = cy + math.sin(u * math.pi) * w * curve
            pts.append((int(px), int(py)))
        return pts

    for k in range(bands):
        t = k / (bands - 1)
        sx, sy = _spine(t, lean, 5 * SS, 1.6, seed, height)
        w = band_w(t)
        sx += math.sin(t * 7.0) * w * 0.12              # spiral wobble
        curve = 0.30 if (k % 2 == 0) else 0.22          # alternate dip
        thick = max(3, int((11 * SS) * (1.0 - 0.35 * t)))
        fade = 1.0 - smoothstep(0.8, 1.05, t)
        for col, tk in ((outline, thick + 3 * SS), (fill, thick)):
            seg = pygame.Surface(big.get_size(), pygame.SRCALPHA)
            pts = swoosh_pts(sx, sy, w, curve)
            pygame.draw.lines(seg, (*col, int(a * fade)), False, pts, tk)
            for px, py in (pts[0], pts[-1]):            # round caps
                pygame.draw.circle(seg, (*col, int(a * fade)), (px, py), tk // 2)
            big.blit(seg, (0, 0))
        # bright highlight along the upper edge of the swoosh
        seg = pygame.Surface(big.get_size(), pygame.SRCALPHA)
        hp = [(x, y - thick * 0.4) for x, y in swoosh_pts(sx, sy, w * 0.85, curve)]
        pygame.draw.lines(seg, (*hi, int(a * 0.7 * fade)), False,
                          [(int(x), int(y)) for x, y in hp], max(2, SS))
        big.blit(seg, (0, 0))
    # gust crescents kicking off the base
    bx, bys = BASE_LX * SS, BASE_LY * SS
    for gx in (-1, 1):
        seg = pygame.Surface(big.get_size(), pygame.SRCALPHA)
        pts = swoosh_pts(bx + gx * 46 * SS, bys - 6 * SS, 22 * SS, 0.45 * gx)
        pygame.draw.lines(seg, (*fill, int(a * 0.7)), False, pts, max(2, 4 * SS))
        big.blit(seg, (0, 0))
    return big


# ── variant 5: turbulent smoke-wisp vortex ───────────────────────────────────
def devil_wisp(s, seed=55):
    rng = random.Random(seed)
    big = _new_big()
    height = (DH - 30) * SS
    low = (168, 128, 86)
    paleish = (206, 184, 150)
    a0 = int(80 + s * 60)
    _base_pool(big, low, int(140 + s * 70), w=46, seed=seed)
    filaments = 54
    for f in range(filaments):
        seed_f = seed * 7 + f * 13
        rf = random.Random(seed_f)
        # each filament starts near the base and is torn upward by a
        # turbulent (multi-sine) horizontal field; spread narrows at the
        # base (converges to the ground) and frays wide at the top
        spread = rf.uniform(-1, 1)
        f1 = rf.uniform(2.0, 4.5)
        f2 = rf.uniform(5.0, 9.0)
        amp1 = rf.uniform(8, 22) * SS
        amp2 = rf.uniform(3, 8) * SS
        ph1 = rf.uniform(0, 6.28)
        ph2 = rf.uniform(0, 6.28)
        t_top = rf.uniform(0.55, 1.08)
        steps = 54
        for i in range(steps):
            t = (i / steps) * t_top
            sx, sy = _spine(t, 0.06, 0, 1, seed, height)
            x = sx + spread * (10 + 40 * t) * SS \
                + amp1 * math.sin(t * f1 + ph1) + amp2 * math.sin(t * f2 + ph2)
            r = lerp(8 * SS, 2.5 * SS, t) * (0.55 + 0.45 * rf.random())
            col = lerp_col(low, paleish, t)
            a = int(a0 * (1.0 - smoothstep(0.5, 1.08, t)) * (0.55 + 0.45 * (1 - t)))
            soft_stamp(big, x, sy, r, col, a, falloff=1.1)
    return big


VARIANTS = [
    ("1 bloom",  "volumetric soft-bloom column", devil_bloom),
    ("2 ribbon", "helical airflow ribbons",      devil_ribbon),
    ("3 swarm",  "granular particle swarm",       devil_swarm),
    ("4 cel",    "cel / graphic swirl",           devil_cel),
    ("5 wisp",   "turbulent smoke-wisp",          devil_wisp),
]


# ── A: tiny airborne sand (the new opening beat, drawn over the scene) ────────
AIR_COL = [(208, 178, 126), (184, 144, 98), (162, 122, 80), (222, 198, 152)]


def _grain(surf, x, y, size, col, a):
    """A crisp tiny sand speck (1–2 px) — sharper than a soft disc so it
    reads as a hard little grain, not a fuzzy dot."""
    a = int(max(0, min(255, a)))
    if a <= 0:
        return
    g = pygame.Surface((size, size), pygame.SRCALPHA)
    g.fill((*col, a))
    surf.blit(g, (int(x), int(y)))


def air_motes(surf, s, seed=1):
    """1. Fine drifting motes — sparse specks across the whole sky,
    parallax sizes (far = tiny sharp, near = a touch bigger/softer)."""
    rng = random.Random(seed)
    for _ in range(int(130 + s * 240)):
        x, y = rng.uniform(0, W), rng.uniform(0, GROUND_Y - 24)
        depth = rng.random()
        a = int((80 + s * 120) * (0.45 + 0.55 * depth))
        col = rng.choice(AIR_COL)
        if depth < 0.62:
            _grain(surf, x, y, 1, col, a)
        else:
            soft_stamp(surf, x, y, 2, col, int(a * 0.95))


def air_ground(surf, s, seed=2):
    """2. Low ground-grit — grains lifting off the floor first, dense low
    and thinning upward."""
    rng = random.Random(seed)
    top = GROUND_Y - 230
    for _ in range(int(190 + s * 320)):
        u = rng.random() ** 2.0                       # biased toward ground
        y = lerp(GROUND_Y - 4, top, u)
        x = rng.uniform(0, W)
        a = int((90 + s * 130) * (1.0 - u * 0.8))
        col = rng.choice(AIR_COL)
        _grain(surf, x, y, 1 if rng.random() < 0.65 else 2, col, a)


def air_streaked(surf, s, seed=3):
    """3. Wind-streaked grains — each grain trails a faint short tapered
    motion-streak at a shallow angle (clearly carried by wind)."""
    rng = random.Random(seed)
    for _ in range(int(85 + s * 170)):
        x, y = rng.uniform(0, W), rng.uniform(0, GROUND_Y - 24)
        ln = rng.uniform(4, 10) * (0.6 + s)
        dx, dy = ln, ln * 0.22                        # shallow rightward drift
        a = int(70 + s * 110)
        col = rng.choice(AIR_COL)
        steps = max(2, int(ln))
        for k in range(steps):
            f = k / steps
            _grain(surf, x + dx * f, y + dy * f, 1, col, int(a * (1 - f)))
        _grain(surf, x + dx, y + dy, 2, col, a)        # bright grain head


def air_haze(surf, s, seed=4):
    """4. Suspended shimmer haze — lots of very-low-alpha sub-grains, a
    faint grainy film across the air."""
    rng = random.Random(seed)
    for _ in range(int(620 + s * 950)):
        x, y = rng.uniform(0, W), rng.uniform(0, GROUND_Y - 16)
        a = int((24 + s * 48) * (0.4 + 0.6 * rng.random()))
        _grain(surf, x, y, 1, rng.choice(AIR_COL), a)


def air_clumps(surf, s, seed=5):
    """5. Drifting wisp-clumps — grains gathered into a few loose puffs
    catching the breeze (uneven, not uniform)."""
    rng = random.Random(seed)
    nclumps = 6
    for c in range(nclumps):
        cx = rng.uniform(W * 0.1, W * 0.9)
        cy = rng.uniform(H * 0.22, GROUND_Y - 50)
        spread = rng.uniform(28, 60)
        for _ in range(int(55 + s * 90)):
            # gaussian-ish scatter, drawn out horizontally (drifting)
            x = cx + (rng.random() - rng.random()) * spread * 1.5
            y = cy + (rng.random() - rng.random()) * spread * 0.7
            a = int((64 + s * 110) * (0.5 + 0.5 * rng.random()))
            _grain(surf, x, y, 1 if rng.random() < 0.7 else 2,
                   rng.choice(AIR_COL), a)


AIR_VARIANTS = [
    ("1 motes",    "fine drifting motes",      air_motes),
    ("2 ground",   "low ground-grit",          air_ground),
    ("3 streaked", "wind-streaked grains",     air_streaked),
    ("4 haze",     "suspended shimmer haze",   air_haze),
    ("5 clumps",   "drifting wisp-clumps",     air_clumps),
]


# ── intensity-driven sand field (chosen #2 ground-grit, ramped) ───────────────
def storm_particles(surf, s, seed=7):
    """The sandstorm body as PURE wind-driven sand — NOT snow. No tint,
    no veil, no atmosphere change: just warm grains, more and more as
    `s` grows, streaking rightward with the wind. Starts as a light
    ground-grit layer (option #2) and fills upward + streaks longer as
    it intensifies."""
    rng = random.Random(seed)
    n = int(35 + s * 560)
    exp = lerp(2.6, 1.0, s)                   # ground-hugging → fills sky
    span = lerp(150, GROUND_Y, s)             # how high the grains reach
    streak = s * 15                           # wind-streak length grows
    for _ in range(n):
        x = rng.uniform(-10, W)
        y = (GROUND_Y - 4) - (rng.random() ** exp) * span
        a = int((70 + s * 120) * (0.5 + 0.5 * rng.random()))
        col = rng.choice(AIR_COL)
        ln = 2 + streak * (0.5 + 0.5 * rng.random())
        dx, dy = ln, ln * 0.18                # shallow rightward drift
        steps = max(1, int(ln / 2))
        for k in range(steps):
            f = k / steps
            _grain(surf, x + dx * f, y + dy * f, 1, col, int(a * (1 - f * 0.8)))
        _grain(surf, x + dx, y + dy, 1 if rng.random() < 0.6 else 2, col, a)


def render_phases():
    """Build-up phases: the storm intensifying as wind-driven sand, the
    devil staying BEHIND the mountains (the in-front pass comes later).
    No snow-style tint/veil anywhere."""
    phases = [(0.05, "just starting — light"),
              (0.22, "building"),
              (0.45, "wind picks up"),
              (0.70, "heavy"),
              (0.92, "peak (still behind mtns)")]
    panels = []
    for s, lbl in phases:
        surf, pal = base_sky(TEASE_PHASE)
        # devil BEHIND the mountains; grows in from ~s 0.12
        if s > 0.12:
            ds = min(1.0, (s - 0.12) / 0.62)
            _blit_devil(surf, devil_bloom(0.16 + 0.5 * ds),
                        W * 0.70, GROUND_Y - 32,
                        scale=0.82 + 0.26 * ds, alpha=int(110 + 145 * ds))
        draw_mountains(surf, 0, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
        draw_ground(surf, GROUND_Y, W, H, 0,
                    pal["ground_top"], pal["ground_mid"], (60, 40, 25))
        b = Bird()
        b.x, b.y, b.vy = BIRD_X, int(H * 0.42), 0
        b.draw(surf)
        storm_particles(surf, s)
        panels.append((f"s={s:.2f} — {lbl}", surf))
        pygame.image.save(surf, os.path.join(OUT_DIR, f"phase_{int(s * 100):02d}.png"))
    _grid_sheet(panels, "phases_sheet.png")


# ── scene composite ───────────────────────────────────────────────────────────
def base_sky(phase):
    pal = _biome.palette_for_phase(phase)
    bucket = _biome.phase_bucket(phase)
    surf = pygame.Surface((W, H))
    surf.blit(get_sky_surface_biome(W, H, GROUND_Y, pal, bucket), (0, 0))
    return surf, pal


def full_frame(fn, s=0.26):
    surf, pal = base_sky(TEASE_PHASE)
    big = fn(s)
    # base sits behind the ridge; the tall column rises clearly above it
    _blit_devil(surf, big, W * 0.70, GROUND_Y - 32, scale=1.0)
    draw_mountains(surf, 0, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
    draw_ground(surf, GROUND_Y, W, H, 0,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    b = Bird()
    b.x = BIRD_X
    b.y = int(H * 0.42)
    b.vy = 0
    b.draw(surf)
    return surf


def zoom_panel(fn, s=0.30):
    """Devil over a sky crop, unoccluded, larger — so detail reads."""
    surf, pal = base_sky(TEASE_PHASE)
    draw_ground(surf, GROUND_Y, W, H, 0,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    big = fn(s)
    sc = 1.5
    _blit_devil(surf, big, W * 0.5, GROUND_Y - 6, scale=sc)
    top = max(0, GROUND_Y - 6 - int(DH * sc))
    crop = pygame.Rect(int(W * 0.5 - 140), top, 280, GROUND_Y + 24 - top)
    crop = crop.clip(surf.get_rect())
    return surf.subsurface(crop).copy()


def _scene_base():
    """Sky + mountains + ground + Pip — the shared backdrop for the
    air-sand panels (mountains untouched this session)."""
    surf, pal = base_sky(TEASE_PHASE)
    draw_mountains(surf, 0, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
    draw_ground(surf, GROUND_Y, W, H, 0,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    b = Bird()
    b.x, b.y, b.vy = BIRD_X, int(H * 0.42), 0
    b.draw(surf)
    return surf, pal


def air_frame(fn, s=0.6):
    surf, _ = _scene_base()
    fn(surf, s)                          # tiny sand drawn over the scene
    return surf


def _grid_sheet(panels, out_name):
    margin, label_h = 12, 26
    cols = len(panels)
    sheet = pygame.Surface((cols * (W + margin) + margin,
                            H + label_h + 2 * margin))
    sheet.fill((24, 26, 32))
    font = pygame.font.SysFont("Arial", 13, bold=True)
    for i, (lbl, surf) in enumerate(panels):
        x = margin + i * (W + margin)
        pygame.draw.rect(sheet, (70, 64, 50), (x - 2, margin - 2, W + 4, H + 4), 2)
        sheet.blit(surf, (x, margin))
        sheet.blit(font.render(lbl, True, (235, 220, 190)), (x + 4, margin + H + 4))
    out = os.path.join(OUT_DIR, out_name)
    pygame.image.save(sheet, out)
    print(f"saved {out}  {sheet.get_size()}")


def render_devils():
    panels = []
    for tag, desc, fn in VARIANTS:
        frame = full_frame(fn)
        panels.append((f"{tag} — {desc}", frame))
        pygame.image.save(frame, os.path.join(OUT_DIR, f"tease_{tag.split()[0]}.png"))
        pygame.image.save(zoom_panel(fn),
                          os.path.join(OUT_DIR, f"tease_{tag.split()[0]}_zoom.png"))
    _grid_sheet(panels, "tease_sheet.png")


def render_air():
    panels = []
    for tag, desc, fn in AIR_VARIANTS:
        frame = air_frame(fn)
        panels.append((f"{tag} — {desc}", frame))
        pygame.image.save(frame, os.path.join(OUT_DIR, f"air_{tag.split()[0]}.png"))
    _grid_sheet(panels, "air_sheet.png")


def render_flow():
    """Deliverable B — the teasing sequence: tiny sand first, then the
    revised sparse+swirl devil APPEARS after it. (motes used as the
    placeholder air style until the user picks from air_sheet.)"""
    devil_x, devil_base = W * 0.70, GROUND_Y - 32

    # p1 — only sand in the air
    p1, _ = _scene_base()
    air_motes(p1, 0.55, seed=1)

    # p2 — sand + the devil just emerging (faint, short, forming)
    p2, _ = _scene_base()
    air_motes(p2, 0.5, seed=1)
    _blit_devil(p2, devil_bloom(0.16), devil_x, devil_base, scale=0.8, alpha=120)

    # p3 — devil present (sand thinned as it concentrates into the column)
    p3, _ = _scene_base()
    air_motes(p3, 0.3, seed=1)
    _blit_devil(p3, devil_bloom(0.42), devil_x, devil_base, scale=1.0)

    panels = [("1 — sand in the air", p1),
              ("2 — devil emerges after", p2),
              ("3 — devil present (sparse + swirl)", p3)]
    _grid_sheet(panels, "tease_flow.png")


if __name__ == "__main__":
    render_phases()
