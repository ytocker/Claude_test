"""Render 5 visual-design mockups for the RAILS UP power-up.

Each mockup is a 720x1280 (2x of the in-game 360x640) frame showing the
same staged scene — sky, ground, 3 sandstone pillars in a gentle stagger,
and Pip the parrot grinding the centre rail — with a different rail
visual treatment painted on top.

The mechanic isn't changing: rail spans the next 3 pillar tops, Pip's
feet snap to the rail, a flap releases it. This script is design
exploration for the *look* of that rail.

Run:  python docs/railway_powerup_design/render_mockups.py
Outputs 5 PNGs next to this script.
"""
from __future__ import annotations

import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))  # required for some surface ops

HERE = os.path.dirname(os.path.abspath(__file__))

# 2x the in-game canvas so PNGs are crisp on a github file view.
SCALE = 2
W, H = 360 * SCALE, 640 * SCALE
GROUND_Y = 595 * SCALE
PIPE_W = 58 * SCALE
BIRD_X = 90 * SCALE

# Sandstone palette lifted from the game's pillar look.
SAND_DK = (130, 80, 50)
SAND_MD = (175, 115, 70)
SAND_LT = (215, 165, 110)
SAND_HI = (240, 205, 150)

SKY_TOP = (96, 145, 195)
SKY_MID = (185, 200, 200)
SKY_BOT = (240, 210, 180)

UI_GOLD = (240, 195, 70)
UI_ORANGE = (240, 130, 60)
UI_CREAM = (250, 240, 215)
UI_RED = (200, 60, 55)
WHITE = (255, 255, 255)


# ──────────────────────────────────────────────────────────────────────────────
# Shared scene scaffolding
# ──────────────────────────────────────────────────────────────────────────────

def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_sky(surf):
    """Three-stop vertical gradient (dawn → noon → dusk).

    Matches the daylight phase of game/biome.py so the mockup reads as the
    same world.
    """
    mid = int(GROUND_Y * 0.62)
    for y in range(H):
        if y < mid:
            c = _lerp(SKY_TOP, SKY_MID, y / mid)
        else:
            c = _lerp(SKY_MID, SKY_BOT, (y - mid) / max(1, H - mid))
        pygame.draw.line(surf, c, (0, y), (W, y))


def draw_ground(surf):
    """Sand band + a single layer of pebble silhouettes for a horizon line."""
    pygame.draw.rect(surf, (200, 150, 100), pygame.Rect(0, GROUND_Y, W, H - GROUND_Y))
    pygame.draw.rect(surf, (170, 120, 75), pygame.Rect(0, GROUND_Y, W, 6))
    rng = random.Random(7)
    for _ in range(50):
        x = rng.randint(0, W)
        r = rng.randint(2, 6)
        y = GROUND_Y + rng.randint(20, 70)
        pygame.draw.circle(surf, (155, 105, 65), (x, y), r)


def draw_pillar(surf, x, gap_y, gap_h, accent=None):
    """Sandstone pillar pair — top column hanging down, bottom column standing.

    Approximation of the game's pillar_variants silhouettes — enough to
    place the rail correctly. accent (optional) tints the top edge of the
    lower pillar for the rail-design variants that want a glow halo seam.
    """
    top_h = gap_y - gap_h // 2
    bot_y = gap_y + gap_h // 2
    bot_h = GROUND_Y - bot_y

    # Top pillar (ceiling-hung)
    top_rect = pygame.Rect(x, 0, PIPE_W, top_h)
    _draw_pillar_body(surf, top_rect, flipped=True)

    # Bottom pillar (floor-standing)
    bot_rect = pygame.Rect(x, bot_y, PIPE_W, bot_h)
    _draw_pillar_body(surf, bot_rect, flipped=False)

    if accent is not None:
        # Subtle 2px halo along the top edge of the lower pillar — sells the
        # idea that the rail is energising the rock.
        glow = pygame.Surface((PIPE_W + 24, 14), pygame.SRCALPHA)
        for i, a in ((0, 60), (1, 110), (2, 170)):
            pygame.draw.rect(glow, (*accent, a),
                             pygame.Rect(12 - i, 6 - i, PIPE_W + i * 2, 4))
        surf.blit(glow, (x - 12, bot_y - 6), special_flags=pygame.BLEND_RGBA_ADD)


def _draw_pillar_body(surf, rect, flipped):
    """Two-tone sandstone column with a wider cap and ribbon highlight."""
    cap_h = 16 * SCALE
    # Body
    body = pygame.Rect(rect.x + 4, rect.y, rect.w - 8, rect.h)
    pygame.draw.rect(surf, SAND_MD, body)
    # Vertical ribbon highlight
    rib = pygame.Rect(rect.x + 10, rect.y, 6, rect.h)
    pygame.draw.rect(surf, SAND_LT, rib)
    # Dark seam right edge
    seam = pygame.Rect(rect.x + rect.w - 12, rect.y, 4, rect.h)
    pygame.draw.rect(surf, SAND_DK, seam)
    # Cap
    if flipped:
        cap = pygame.Rect(rect.x, rect.bottom - cap_h, rect.w, cap_h)
    else:
        cap = pygame.Rect(rect.x, rect.y, rect.w, cap_h)
    pygame.draw.rect(surf, SAND_DK, cap)
    pygame.draw.rect(surf, SAND_LT, cap.inflate(-8, -6))
    pygame.draw.rect(surf, SAND_HI, cap.inflate(-16, -10))


def draw_bird(surf, x, y, *, beak_dir=1, tint=None):
    """Lightweight Pip — round red body, tail wedge, beak, eye, single wing.

    `tint` overlays an additive colour (used by the Maglev design to push
    Pip into a cool cyan glow while he hovers above the rail).
    """
    r = 14 * SCALE
    body_col = (220, 60, 55)
    wing_col = (180, 35, 35)
    belly_col = (245, 220, 215)

    # Cool/warm tint halo, drawn first so the bird's silhouette stays
    # crisp on top of it.
    if tint is not None:
        glow = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
        for i in range(8, 0, -1):
            pygame.draw.circle(glow, (*tint, 8),
                               (r * 3, r * 3), r + i * 3)
        surf.blit(glow, (x - r * 3, y - r * 3),
                  special_flags=pygame.BLEND_RGBA_ADD)

    # Body
    pygame.draw.circle(surf, body_col, (x, y), r)
    pygame.draw.circle(surf, (140, 25, 25), (x, y), r, 2)
    # Belly
    pygame.draw.ellipse(surf, belly_col,
                        pygame.Rect(x - r + 4, y - 2, r * 2 - 8, r + 4))
    # Wing
    wing_rect = pygame.Rect(x - 6, y - 2, r + 4, r - 2)
    pygame.draw.ellipse(surf, wing_col, wing_rect)
    pygame.draw.ellipse(surf, (90, 20, 20), wing_rect, 2)
    # Tail
    pygame.draw.polygon(surf, body_col, [
        (x - r + 2, y - 4), (x - r - 8, y), (x - r + 2, y + 4),
    ])
    # Beak (orange triangle)
    bx = x + r * beak_dir
    pygame.draw.polygon(surf, (240, 165, 50), [
        (bx, y - 4), (bx + 10 * beak_dir, y), (bx, y + 4),
    ])
    # Eye
    eye_x = x + (r - 6) * beak_dir
    pygame.draw.circle(surf, WHITE, (eye_x, y - 5), 4)
    pygame.draw.circle(surf, (20, 20, 30), (eye_x + beak_dir, y - 5), 2)



def float_text(surf, txt, x, y, base_col, *, size=32):
    """Pickup label — vertical gradient fill + thick outline + sparkles.

    Mirrors the FloatText `style="powerup"` look from game/hud.py so the
    mockup reads like the real game's pickup notification.
    """
    f = pygame.font.SysFont("Arial", size * SCALE, bold=True)
    base = f.render(txt, True, base_col)

    # Gradient fill: top 40% toward white → base_col at bottom.
    bw, bh = base.get_size()
    grad = pygame.Surface((bw, bh), pygame.SRCALPHA)
    light = _lerp(base_col, WHITE, 0.45)
    for yy in range(bh):
        c = _lerp(light, base_col, yy / max(1, bh - 1))
        pygame.draw.line(grad, c, (0, yy), (bw, yy))
    body = base.copy()
    body.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Outline: 8-direction offsets of base re-tinted dark.
    dark = tuple(max(0, c // 4) for c in base_col)
    outline = f.render(txt, True, dark)
    for ox, oy in ((-3, 0), (3, 0), (0, -3), (0, 3),
                   (-2, -2), (-2, 2), (2, -2), (2, 2)):
        surf.blit(outline, (x - bw // 2 + ox, y - bh // 2 + oy))
    surf.blit(body, (x - bw // 2, y - bh // 2))

    # 8 sparkles around the label.
    rng = random.Random(hash(txt) & 0xFFFF)
    for _ in range(8):
        sx = x + rng.randint(-bw, bw)
        sy = y + rng.randint(-bh, bh)
        sr = rng.randint(3, 6)
        pygame.draw.circle(surf, UI_CREAM, (sx, sy), sr)
        pygame.draw.circle(surf, WHITE, (sx, sy), sr - 2)


def draw_label_band(surf, idx, title, tagline):
    """Bottom-of-frame caption: number, name, 2-line summary."""
    band_h = 95 * SCALE
    band = pygame.Surface((W, band_h), pygame.SRCALPHA)
    pygame.draw.rect(band, (15, 20, 30, 230), pygame.Rect(0, 0, W, band_h))
    pygame.draw.rect(band, UI_GOLD, pygame.Rect(0, 0, W, 4))

    f_num = pygame.font.SysFont("Arial", 22 * SCALE, bold=True)
    f_title = pygame.font.SysFont("Arial", 22 * SCALE, bold=True)
    f_tag = pygame.font.SysFont("Arial", 12 * SCALE)

    band.blit(f_num.render(f"0{idx}", True, UI_GOLD), (16 * SCALE, 8 * SCALE))
    band.blit(f_title.render(title, True, WHITE), (60 * SCALE, 8 * SCALE))

    # Greedy word-wrap. Width budget is W minus L/R padding.
    pad = 16 * SCALE
    avail = W - 2 * pad
    words = tagline.split()
    lines: list[str] = []
    current = ""
    for w in words:
        candidate = (current + " " + w).strip()
        if f_tag.size(candidate)[0] <= avail:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)

    for li, line in enumerate(lines[:3]):
        band.blit(f_tag.render(line, True, (200, 210, 230)),
                  (pad, (38 + li * 16) * SCALE))

    surf.blit(band, (0, H - band_h))


def base_scene():
    """Sky + ground + 3 staggered pillars + grinding Pip on the centre pipe.

    Returns the surface and the rail endpoints [(x0, y0), (x1, y1), ...]
    so each design variant can paint over them.
    """
    surf = pygame.Surface((W, H))
    draw_sky(surf)
    draw_ground(surf)

    # 3 pillars in a gentle vertical stagger so the rail-bridges slope.
    # x values are game-space; multiplied by SCALE to fit the 720-wide mockup
    # (PIPE_W is 58 game-px so pillar 3's right edge sits at 290+58=348 < 360).
    # Gap-y kept low (235-300) so the top pillars are short and the "RAILS UP!"
    # pickup label has clean sky above the gaps.
    pipe_data = [
        # (x, gap_y, gap_h)
        ( 50 * SCALE, 285 * SCALE, 170 * SCALE),
        (170 * SCALE, 235 * SCALE, 170 * SCALE),
        (290 * SCALE, 300 * SCALE, 170 * SCALE),
    ]
    rail_points = []
    for x, gap_y, gap_h in pipe_data:
        rail_y_left = gap_y + gap_h // 2
        rail_points.append((x, rail_y_left))
        rail_points.append((x + PIPE_W, rail_y_left))

    return surf, pipe_data, rail_points


# ──────────────────────────────────────────────────────────────────────────────
# Variant 1 — Neon Grind
# ──────────────────────────────────────────────────────────────────────────────

def render_neon_grind(out_path):
    """Cyan + magenta neon dual-rail, motion-blur streak, electric arcs.

    Aesthetic: Tron / Sonic Frontiers grind rail. Reads as energy, not metal.
    No ties — instead, dotted current pulses run *along* the rail.
    """
    surf, pipes, rails = base_scene()
    for x, gap_y, gap_h in pipes:
        draw_pillar(surf, x, gap_y, gap_h, accent=(80, 220, 255))

    cyan = (90, 230, 255)
    magenta = (255, 90, 220)

    # Motion-blur streak — wide soft trail behind the bird's grind path,
    # extending all the way through the rail.
    streak = pygame.Surface((W, H), pygame.SRCALPHA)
    for i, alpha in enumerate((20, 35, 60, 100, 160)):
        thickness = 18 * SCALE - i * 3
        _draw_rail_polyline(streak, rails, cyan, thickness, alpha)
    surf.blit(streak, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Dual neon rails — magenta below, cyan above, hot-white core line.
    _draw_rail_polyline(surf, rails, magenta, 8, 200, offset_y=4)
    _draw_rail_polyline(surf, rails, cyan, 6, 230, offset_y=-2)
    _draw_rail_polyline(surf, rails, WHITE, 2, 255, offset_y=0)

    # Pulse markers travelling along the rail (3 hot dots).
    for j, t in enumerate((0.18, 0.48, 0.78)):
        px, py = _rail_lerp(rails, t)
        pygame.draw.circle(surf, WHITE, (px, py), 10)
        pygame.draw.circle(surf, cyan, (px, py), 6)

    # Electric arcs jutting up off the rail at each pillar seam.
    rng = random.Random(11)
    for i in (1, 3):  # seams between pillars (rail bridge mid-points)
        bx = rails[i][0]
        by = rails[i][1]
        for _ in range(4):
            zig = [(bx, by)]
            cy = by
            for k in range(4):
                bx += rng.randint(-12, 12)
                cy -= rng.randint(8, 14)
                zig.append((bx, cy))
            pygame.draw.lines(surf, magenta, False, zig, 2)
            pygame.draw.lines(surf, WHITE, False, zig, 1)

    # Pip grinding the centre rail — feet sit on the middle pillar's top.
    bird_cx = (rails[2][0] + rails[3][0]) // 2
    bird_cy = rails[2][1] - 14 * SCALE
    draw_bird(surf, bird_cx, bird_cy, beak_dir=1)
    # Cyan ground-sparks at his feet.
    for _ in range(14):
        sx = bird_cx + rng.randint(-30, 30)
        sy = rails[2][1] + rng.randint(-4, 10)
        pygame.draw.circle(surf, cyan, (sx, sy), rng.randint(2, 4))

    float_text(surf, "RAILS UP!", bird_cx, bird_cy - 110 * SCALE,
               cyan, size=30)

    draw_label_band(surf, 1, "NEON GRIND",
                    "Tron-style energy rail — cyan + magenta dual line, "
                    "pulse markers run the track, arcs at every joint.")
    pygame.image.save(surf, out_path)


# ──────────────────────────────────────────────────────────────────────────────
# Variant 2 — Steampunk Brass
# ──────────────────────────────────────────────────────────────────────────────

def render_steampunk_brass(out_path):
    """Riveted copper rail on dark-walnut ties, hissing steam at joints.

    Aesthetic: 1880s industrial. Believable physical hardware — bolts,
    rivets, oil. Warm palette anchored to the existing UI_GOLD.
    """
    surf, pipes, rails = base_scene()
    for x, gap_y, gap_h in pipes:
        draw_pillar(surf, x, gap_y, gap_h)

    brass_dk = (110, 65, 25)
    brass = (200, 140, 55)
    brass_hi = (255, 215, 130)
    copper_dk = (140, 55, 25)
    copper_hi = (235, 150, 90)
    walnut = (55, 35, 22)
    walnut_hi = (110, 70, 40)

    # Walnut ties laid every 14 px along the whole polyline (not per-segment
    # so the bridges across gaps keep ties too — looks like one continuous
    # railroad).
    _draw_ties(surf, rails, color_dk=walnut, color_hi=walnut_hi,
               spacing=14 * SCALE, length=20 * SCALE, thickness=6 * SCALE)

    # Twin brass rails — drawn as two parallel polylines for the
    # left/right rails (4 px gauge), each with a copper undershadow.
    _draw_rail_polyline(surf, rails, copper_dk, 5, 255, offset_y=4)
    _draw_rail_polyline(surf, rails, copper_dk, 5, 255, offset_y=-3)
    _draw_rail_polyline(surf, rails, brass, 4, 255, offset_y=3)
    _draw_rail_polyline(surf, rails, brass, 4, 255, offset_y=-2)
    _draw_rail_polyline(surf, rails, brass_hi, 2, 255, offset_y=2)
    _draw_rail_polyline(surf, rails, brass_hi, 2, 255, offset_y=-1)

    # Brass rivets every 22 px along each rail.
    for offset_y in (3, -2):
        for t in (i / 18 for i in range(19)):
            rx, ry = _rail_lerp(rails, t)
            pygame.draw.circle(surf, brass_dk, (rx, ry + offset_y), 4)
            pygame.draw.circle(surf, brass_hi, (rx - 1, ry + offset_y - 1), 2)

    # Steam puffs hissing at the 2 bridge seams (between pillars).
    for i in (1, 3):
        sx, sy = rails[i]
        _draw_steam_puff(surf, sx + 8, sy - 6, scale=1.2)
        _draw_steam_puff(surf, sx + 24, sy - 24, scale=0.9)
        _draw_steam_puff(surf, sx - 10, sy - 20, scale=0.7)

    # Oil drip trail under the centre pipe rail.
    drip_x = (rails[2][0] + rails[3][0]) // 2
    drip_y = rails[2][1] + 8
    for k in range(5):
        pygame.draw.circle(surf, (35, 25, 18),
                           (drip_x - 4, drip_y + k * 6 * SCALE), 3 - k // 2)

    # Pip with a tiny conductor cap.
    bird_cx = (rails[2][0] + rails[3][0]) // 2
    bird_cy = rails[2][1] - 14 * SCALE
    draw_bird(surf, bird_cx, bird_cy, beak_dir=1)
    _draw_conductor_cap(surf, bird_cx, bird_cy - 22 * SCALE)

    float_text(surf, "RAILS UP!", bird_cx, bird_cy - 110 * SCALE,
               brass, size=30)

    draw_label_band(surf, 2, "STEAMPUNK BRASS",
                    "1880s industrial — riveted copper rails on walnut ties, "
                    "steam puffs at the joins, conductor cap on Pip.")
    pygame.image.save(surf, out_path)


# ──────────────────────────────────────────────────────────────────────────────
# Variant 3 — Coin Track
# ──────────────────────────────────────────────────────────────────────────────

def render_coin_track(out_path):
    """The rail itself is a chain of fused gold coins.

    Earned interaction: every 0.5 s of contact, a coin lifts off the rail
    and flies into Pip's tally. Reads as 'the track is paying you'.
    """
    surf, pipes, rails = base_scene()
    for x, gap_y, gap_h in pipes:
        draw_pillar(surf, x, gap_y, gap_h, accent=(255, 220, 90))

    # Soft gold underglow along the whole polyline so the coins look hot.
    glow = pygame.Surface((W, H), pygame.SRCALPHA)
    for i, a in ((6, 30), (4, 60), (2, 110)):
        _draw_rail_polyline(glow, rails, UI_GOLD, 14 * SCALE - i * 2, a)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Coin chain — 20 coins distributed along the polyline.
    coin_count = 22
    for k in range(coin_count):
        t = k / (coin_count - 1)
        cx, cy = _rail_lerp(rails, t)
        # Slight bob so it doesn't read as a flat barcode.
        cy += int(math.sin(k * 0.7) * 1.5 * SCALE)
        _draw_dollar_coin(surf, cx, cy, spin_phase=k * 0.5)

    # 3 coins LIFTING off the rail — gone-into-bird animation snapshot.
    bird_cx = (rails[2][0] + rails[3][0]) // 2
    bird_cy = rails[2][1] - 14 * SCALE
    for k, t in enumerate((0.55, 0.62, 0.70)):
        sx, sy = _rail_lerp(rails, t)
        # Coin lerps toward bird.
        f = 0.30 + k * 0.18
        fx = int(sx + (bird_cx - sx) * f)
        fy = int(sy + (bird_cy - sy) * f) - k * 8 * SCALE
        _draw_dollar_coin(surf, fx, fy, spin_phase=k * 1.1, scale=0.85)
        # Streak from rail to coin.
        pygame.draw.line(surf, (255, 230, 130, 200), (sx, sy), (fx, fy), 2)

    # Soft gold halo drawn BEFORE the bird so Pip stays readable on top.
    halo = pygame.Surface((80 * SCALE, 80 * SCALE), pygame.SRCALPHA)
    for i in range(8, 0, -1):
        pygame.draw.circle(halo, (*UI_GOLD, 8),
                           (40 * SCALE, 40 * SCALE), 22 * SCALE + i * 4)
    surf.blit(halo, (bird_cx - 40 * SCALE, bird_cy - 40 * SCALE),
              special_flags=pygame.BLEND_RGBA_ADD)
    draw_bird(surf, bird_cx, bird_cy, beak_dir=1)

    # "+1" floats above the bird (a coin just got collected).
    f = pygame.font.SysFont("Arial", 26 * SCALE, bold=True)
    txt = f.render("+1", True, UI_GOLD)
    surf.blit(txt, (bird_cx - txt.get_width() // 2,
                    bird_cy - 60 * SCALE))

    float_text(surf, "RAILS UP!", bird_cx, bird_cy - 130 * SCALE,
               UI_GOLD, size=30)

    draw_label_band(surf, 3, "COIN TRACK",
                    "Rail is a chain of fused $ coins — Pip earns +1 every "
                    "half-second of contact. Risk/reward grind.")
    pygame.image.save(surf, out_path)


# ──────────────────────────────────────────────────────────────────────────────
# Variant 4 — Western Trestle
# ──────────────────────────────────────────────────────────────────────────────

def render_western_trestle(out_path):
    """Weathered wooden railroad trestle — pine timbers + iron spikes.

    Aesthetic: Red Dead / Spaghetti Western. The rail is dusty, scarred,
    physical. A sunset wash over the sky pushes the palette warm.
    """
    surf, pipes, rails = base_scene()

    # Push the sky toward sunset — a warm tint applied with normal alpha
    # over the upper half so the cool sky shifts amber without bleaching.
    wash = pygame.Surface((W, H), pygame.SRCALPHA)
    horizon = int(GROUND_Y * 0.95)
    for y in range(horizon):
        # Bottom of horizon is hot (sunset glow); fades upward to dusk-violet.
        t = y / horizon
        r = int(255 - 30 * t)
        g = int(140 - 40 * t)
        b = int(90 + 40 * t)
        a = int(150 * (1 - t * 0.6))
        pygame.draw.line(wash, (r, g, b, a), (0, y), (W, y))
    surf.blit(wash, (0, 0))

    for x, gap_y, gap_h in pipes:
        draw_pillar(surf, x, gap_y, gap_h)

    pine_dk = (75, 50, 28)
    pine = (135, 90, 50)
    pine_hi = (180, 130, 75)
    iron_dk = (50, 45, 45)
    iron = (110, 100, 95)
    iron_hi = (180, 170, 165)

    # Wooden ties (weathered planks) every 18 px.
    _draw_ties(surf, rails, color_dk=pine_dk, color_hi=pine_hi,
               spacing=18 * SCALE, length=24 * SCALE, thickness=6 * SCALE,
               wood_grain=True)

    # Iron rails — duller than brass, with chips and rust.
    _draw_rail_polyline(surf, rails, iron_dk, 7, 255, offset_y=4)
    _draw_rail_polyline(surf, rails, iron_dk, 7, 255, offset_y=-4)
    _draw_rail_polyline(surf, rails, iron, 5, 255, offset_y=4)
    _draw_rail_polyline(surf, rails, iron, 5, 255, offset_y=-4)
    _draw_rail_polyline(surf, rails, iron_hi, 2, 255, offset_y=3)
    _draw_rail_polyline(surf, rails, iron_hi, 2, 255, offset_y=-5)

    # Hex-headed spikes at tie ends.
    rng = random.Random(31)
    for t in (i / 24 for i in range(25)):
        rx, ry = _rail_lerp(rails, t)
        if rng.random() < 0.5:
            continue
        for off in (-9 * SCALE, 9 * SCALE):
            pygame.draw.circle(surf, iron_dk, (rx, ry + off), 4)
            pygame.draw.circle(surf, iron_hi, (rx - 1, ry + off - 1), 2)

    # Rust patches and chips on the rails.
    rust = (170, 80, 35)
    for t in (rng.random() for _ in range(18)):
        rx, ry = _rail_lerp(rails, t)
        pygame.draw.circle(surf, rust, (rx, ry + 3), rng.randint(2, 4))

    # Tumbleweed silhouettes — placed above the label band so they read in
    # the mockup. In-game they'd live on the ground.
    _draw_tumbleweed(surf, 30 * SCALE, 500 * SCALE, scale=0.9)
    _draw_tumbleweed(surf, 330 * SCALE, 515 * SCALE, scale=0.7)

    # Pip kicks up dust under his feet.
    bird_cx = (rails[2][0] + rails[3][0]) // 2
    bird_cy = rails[2][1] - 14 * SCALE
    for _ in range(18):
        dx = bird_cx + rng.randint(-26, 18)
        dy = rails[2][1] + rng.randint(-2, 16)
        pygame.draw.circle(surf, (220, 195, 155), (dx, dy),
                           rng.randint(3, 7))
        pygame.draw.circle(surf, (255, 230, 195), (dx, dy),
                           rng.randint(1, 3))
    draw_bird(surf, bird_cx, bird_cy, beak_dir=1)

    float_text(surf, "RAILS UP!", bird_cx, bird_cy - 110 * SCALE,
               (220, 150, 80), size=30)

    draw_label_band(surf, 4, "WESTERN TRESTLE",
                    "Frontier-railroad timber + iron spikes — dust under "
                    "Pip's feet, sunset wash, tumbleweeds drifting past.")
    pygame.image.save(surf, out_path)


# ──────────────────────────────────────────────────────────────────────────────
# Variant 5 — Maglev Ion
# ──────────────────────────────────────────────────────────────────────────────

def render_maglev_ion(out_path):
    """Sci-fi levitation rail — Pip hovers 6 px above a cyan ion beam.

    Aesthetic: futuristic / Tron-light-cycle. No ties, no rivets — just a
    single hot containment line with vertical containment posts and an
    ion-shower beneath. Pip is haloed cyan to signal the levitation.
    """
    surf, pipes, rails = base_scene()
    for x, gap_y, gap_h in pipes:
        draw_pillar(surf, x, gap_y, gap_h, accent=(80, 230, 255))

    cyan = (80, 230, 255)
    cyan_hot = (180, 245, 255)
    deep = (40, 100, 200)

    # Ion shower BELOW the rail — soft falling cyan sparkles.
    rng = random.Random(101)
    for _ in range(120):
        t = rng.random()
        rx, ry = _rail_lerp(rails, t)
        ix = rx + rng.randint(-6, 6)
        iy = ry + rng.randint(4, 40)
        a = max(30, 220 - (iy - ry) * 4)
        spark = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(spark, (*cyan, a), (3, 3), 3)
        surf.blit(spark, (ix - 3, iy - 3))

    # Containment beam underglow — wide soft cyan.
    underglow = pygame.Surface((W, H), pygame.SRCALPHA)
    for i, a in ((10, 25), (6, 60), (3, 120)):
        _draw_rail_polyline(underglow, rails, cyan, 14 * SCALE - i, a)
    surf.blit(underglow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Vertical containment posts at each pillar edge — short cyan studs
    # rising 18 px above the rail.
    for px, py in rails:
        pygame.draw.line(surf, deep, (px, py), (px, py - 18 * SCALE), 3)
        pygame.draw.line(surf, cyan, (px, py), (px, py - 18 * SCALE), 1)
        pygame.draw.circle(surf, cyan_hot, (px, py - 18 * SCALE), 4)

    # Containment beam — single hot line, no ties.
    _draw_rail_polyline(surf, rails, deep, 6, 255, offset_y=2)
    _draw_rail_polyline(surf, rails, cyan, 4, 255, offset_y=0)
    _draw_rail_polyline(surf, rails, cyan_hot, 2, 255, offset_y=-1)
    _draw_rail_polyline(surf, rails, WHITE, 1, 255, offset_y=-1)

    # Pip floats 12 px ABOVE the rail (vs. all other variants where his
    # feet are ON it).
    bird_cx = (rails[2][0] + rails[3][0]) // 2
    bird_cy = rails[2][1] - 28 * SCALE
    draw_bird(surf, bird_cx, bird_cy, beak_dir=1, tint=cyan)

    # Cyan tether arc from feet to rail.
    feet = (bird_cx, bird_cy + 14 * SCALE)
    rail_pt = (bird_cx, rails[2][1])
    pygame.draw.line(surf, cyan_hot, feet, rail_pt, 3)
    pygame.draw.line(surf, WHITE, feet, rail_pt, 1)
    pygame.draw.circle(surf, cyan_hot, rail_pt, 6)
    pygame.draw.circle(surf, WHITE, rail_pt, 3)

    float_text(surf, "RAILS UP!", bird_cx, bird_cy - 110 * SCALE,
               cyan, size=30)

    draw_label_band(surf, 5, "MAGLEV ION",
                    "Pip hovers 6 px above a cyan containment beam — ion "
                    "shower trails downward, no ties, sci-fi clean.")
    pygame.image.save(surf, out_path)


# ──────────────────────────────────────────────────────────────────────────────
# Shared rail-polyline + ornament helpers
# ──────────────────────────────────────────────────────────────────────────────

def _draw_rail_polyline(surf, rails, color, thickness, alpha, *, offset_y=0):
    """Draw a polyline through every rail point with given thickness/alpha.

    The rails list interleaves left-edge and right-edge of each pillar so a
    single polyline through it gives 3 on-pipe segments + 2 bridge
    segments.
    """
    pts = [(x, y + offset_y) for x, y in rails]
    if alpha >= 255:
        pygame.draw.lines(surf, color, False, pts, thickness)
    else:
        layer = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.lines(layer, (*color, alpha), False, pts, thickness)
        surf.blit(layer, (0, 0))


def _rail_lerp(rails, t):
    """Return (x, y) at parametric t∈[0,1] along the full rail polyline."""
    # Cumulative arc length.
    segs = []
    total = 0.0
    for i in range(len(rails) - 1):
        x0, y0 = rails[i]
        x1, y1 = rails[i + 1]
        d = math.hypot(x1 - x0, y1 - y0)
        segs.append(d)
        total += d
    target = t * total
    acc = 0.0
    for i, d in enumerate(segs):
        if acc + d >= target:
            f = (target - acc) / max(1.0, d)
            x0, y0 = rails[i]
            x1, y1 = rails[i + 1]
            return int(x0 + (x1 - x0) * f), int(y0 + (y1 - y0) * f)
        acc += d
    return rails[-1]


def _draw_ties(surf, rails, *, color_dk, color_hi, spacing, length, thickness,
               wood_grain=False):
    """Lay perpendicular ties along the polyline."""
    segs = []
    total = 0.0
    for i in range(len(rails) - 1):
        x0, y0 = rails[i]
        x1, y1 = rails[i + 1]
        d = math.hypot(x1 - x0, y1 - y0)
        segs.append(d)
        total += d
    n = max(1, int(total / spacing))
    for k in range(n + 1):
        t = k / n
        # find segment + perp normal
        target = t * total
        acc = 0.0
        for i, d in enumerate(segs):
            if acc + d >= target:
                f = (target - acc) / max(1.0, d)
                x0, y0 = rails[i]
                x1, y1 = rails[i + 1]
                cx = int(x0 + (x1 - x0) * f)
                cy = int(y0 + (y1 - y0) * f)
                # perpendicular unit vector (rotate seg 90°)
                dx = x1 - x0
                dy = y1 - y0
                seg_len = max(1.0, math.hypot(dx, dy))
                nx = -dy / seg_len
                ny = dx / seg_len
                tie_len = length // 2
                p0 = (int(cx + nx * tie_len), int(cy + ny * tie_len))
                p1 = (int(cx - nx * tie_len), int(cy - ny * tie_len))
                pygame.draw.line(surf, color_dk, p0, p1, thickness)
                # highlight stripe
                hi0 = (int(cx + nx * tie_len * 0.55),
                       int(cy + ny * tie_len * 0.55))
                hi1 = (int(cx - nx * tie_len * 0.55),
                       int(cy - ny * tie_len * 0.55))
                pygame.draw.line(surf, color_hi, hi0, hi1,
                                 max(1, thickness - 3))
                if wood_grain:
                    # Two short darker grain strokes parallel to the tie.
                    g0 = (int(cx + nx * tie_len * 0.8 + dx / seg_len * 1),
                          int(cy + ny * tie_len * 0.8 + dy / seg_len * 1))
                    g1 = (int(cx - nx * tie_len * 0.8 + dx / seg_len * 1),
                          int(cy - ny * tie_len * 0.8 + dy / seg_len * 1))
                    pygame.draw.line(surf, color_dk, g0, g1, 1)
                break
            acc += d


def _draw_steam_puff(surf, cx, cy, *, scale=1.0):
    """Soft white cloud puff with 4 lobes — sells the 'hissing joint'."""
    layer = pygame.Surface((int(60 * scale * SCALE), int(40 * scale * SCALE)),
                           pygame.SRCALPHA)
    lw, lh = layer.get_size()
    for ox, oy, r in (
        (lw // 2 - 6, lh // 2, 14),
        (lw // 2 + 6, lh // 2 - 4, 12),
        (lw // 2, lh // 2 - 8, 10),
        (lw // 2 + 12, lh // 2, 9),
    ):
        for i in range(4, 0, -1):
            pygame.draw.circle(layer, (255, 255, 255, 35 + i * 20),
                               (ox, oy),
                               int(r * scale * SCALE * (1 + i * 0.05)))
        pygame.draw.circle(layer, (255, 255, 255, 220), (ox, oy),
                           int(r * scale * SCALE))
    surf.blit(layer, (cx - lw // 2, cy - lh // 2))


def _draw_conductor_cap(surf, cx, cy):
    """Tiny pillbox conductor cap on the bird's head — brass band + visor."""
    body = (35, 30, 25)
    band = (200, 140, 55)
    hi = (255, 215, 130)
    cap = pygame.Rect(cx - 12, cy - 8, 24, 14)
    pygame.draw.rect(surf, body, cap, border_radius=2)
    pygame.draw.rect(surf, band, pygame.Rect(cap.x, cap.y + 8, cap.w, 4))
    pygame.draw.rect(surf, hi, pygame.Rect(cap.x + 2, cap.y + 9, cap.w - 4, 1))
    # Visor
    pygame.draw.rect(surf, body, pygame.Rect(cap.x - 4, cap.y + 10, cap.w + 8, 3),
                     border_radius=1)


def _draw_dollar_coin(surf, cx, cy, *, spin_phase=0.0, scale=1.0):
    """Gold disc with embossed $ — same family as game/dollar_coin_glyphs.

    spin_phase squashes the disc horizontally to fake a rotating coin.
    """
    w_scale = abs(math.cos(spin_phase))
    rw = max(2, int(11 * scale * SCALE * (0.35 + 0.65 * w_scale)))
    rh = int(11 * scale * SCALE)
    rim = pygame.Rect(cx - rw, cy - rh, rw * 2, rh * 2)
    pygame.draw.ellipse(surf, (140, 90, 25), rim)
    pygame.draw.ellipse(surf, (240, 195, 70), rim.inflate(-3, -3))
    pygame.draw.ellipse(surf, (255, 230, 130), rim.inflate(-6, -8))
    # $ glyph
    if w_scale > 0.5 and rh > 6:
        try:
            f = pygame.font.SysFont("Arial", int(rh * 1.6), bold=True)
            txt = f.render("$", True, (120, 70, 15))
            tw, th = txt.get_size()
            if w_scale < 1.0:
                txt = pygame.transform.scale(txt, (max(1, int(tw * w_scale)), th))
            surf.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))
        except Exception:
            pass


def _draw_tumbleweed(surf, cx, cy, *, scale=1.0):
    """Beige snarl of dry-grass loops. Silhouette only."""
    r = int(14 * scale * SCALE)
    rng = random.Random(int(cx))
    base = (165, 130, 80)
    pygame.draw.circle(surf, (130, 95, 55), (cx, cy), r)
    for _ in range(14):
        ang = rng.uniform(0, math.tau)
        rr = rng.uniform(r * 0.4, r * 0.9)
        x0 = int(cx + math.cos(ang) * rr)
        y0 = int(cy + math.sin(ang) * rr)
        x1 = int(cx + math.cos(ang + 0.6) * rr * 1.1)
        y1 = int(cy + math.sin(ang + 0.6) * rr * 1.1)
        pygame.draw.line(surf, base, (x0, y0), (x1, y1), 2)


# ──────────────────────────────────────────────────────────────────────────────
# Driver
# ──────────────────────────────────────────────────────────────────────────────

def main():
    targets = [
        ("01_neon_grind.png", render_neon_grind),
        ("02_steampunk_brass.png", render_steampunk_brass),
        ("03_coin_track.png", render_coin_track),
        ("04_western_trestle.png", render_western_trestle),
        ("05_maglev_ion.png", render_maglev_ion),
    ]
    for name, fn in targets:
        path = os.path.join(HERE, name)
        fn(path)
        print(f"  wrote {name}")
    print(f"\nAll 5 mockups saved to {HERE}")


if __name__ == "__main__":
    main()
