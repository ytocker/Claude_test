"""Round-2 review render for the `dizzy-dazed` hurt-parrot skin.

Two halves to the look, deliberately kept apart:

* Baked into the 64x60 frame — a compressed flap range and cream daze
  spirals painted onto the shade lenses. Body colours stay stock; the
  read comes from posture plus the eye cue.
* Composited AFTER rotation — the orbiting stars. They must not tumble
  with Pip's dive tilt, which is exactly what baking them in would do,
  so the ring is drawn in screen space over the finished frame.

Star legibility is carried by a hard dark rim and full opacity rather
than by an alpha ramp: a translucent star vanishes into a cloud or a
night sky, and the ring has to read identically in both.

Nothing here is wired into the game; `get_skin_frame` is monkey-patched
for the duration of the shot only.
"""
import math
import os
import random
import sys

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()

import game.parrot as parrot_mod
from game.draw import (
    BIRD_RED, BIRD_RED_D, BIRD_BELLY, BIRD_BEAK, BIRD_BEAK_D,
)
from game.scenes import App

OUT_DIR = "/home/user/skybit/docs/hurt-parrot-v1/dizzy-dazed"
os.makedirs(OUT_DIR, exist_ok=True)
OUT = f"{OUT_DIR}/round_2.png"

_aaellipse = parrot_mod._aaellipse

# Cream-white, not coin gold (255,210,70) — gold at this size on this
# sky reads as a collectible and players would try to fly into it.
STAR_FILL = (255, 245, 215)
# Near-black plum: the only colour that keeps a value edge against both
# the noon sky and the night gradient without going flat grey.
STAR_RIM = (55, 15, 20)
STAR_BEVEL = (230, 180, 110)
SPIRAL_FILL = (240, 235, 215)

# Head ellipse in sprite space, straight out of `_build_frame`.
HEAD_C = (47, 21)
HEAD_RY = 11
SPRITE_C = (parrot_mod.SPRITE_W / 2.0, parrot_mod.SPRITE_H / 2.0)

ORBIT_RX, ORBIT_RY = 13.0, 5.0
ORBIT_TILT_DEG = 15.0
ORBIT_GAP = 26.0          # clearance above the crown silhouette
# Quarter-turn offset so the ring always shows two near + two far stars;
# on-axis phases would collapse two of them to an ambiguous mid depth.
ORBIT_PHASE = 45.0
# The HUD badges own the top of the canvas; the ring ducks under them.
HUD_FLOOR_Y = 56


def _rot_about(pt, origin, deg):
    """Rotate in sprite/screen space (y grows downward), so a positive
    `deg` here is a visually clockwise turn."""
    a = math.radians(deg)
    dx, dy = pt[0] - origin[0], pt[1] - origin[1]
    return (origin[0] + dx * math.cos(a) - dy * math.sin(a),
            origin[1] + dx * math.sin(a) + dy * math.cos(a))


def _draw_daze_spiral(surf, cx, cy, r=3.0, turns=2.0, color=SPIRAL_FILL):
    """Two-turn spiral glint, sampled rather than blitted so it stays a
    single procedural primitive at any lens size."""
    pts = []
    steps = 44
    for i in range(steps + 1):
        t = i / steps
        a = t * turns * math.tau
        rr = t * r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    pygame.draw.lines(surf, color, False,
                      [(int(round(x)), int(round(y))) for x, y in pts], 1)


def _draw_dazed_shades(surf, cx, cy):
    """Stock aviators with the sunlight glints swapped for spirals — the
    universal cartoon signal that the eyes behind them are spinning."""
    parrot_mod._draw_sunglasses(surf, cx, cy)
    r_outer = 6
    for lens in ((cx - 4, cy), (cx + 6, cy - 1)):
        # Repaint the lens body to erase the stock glints; the gold rim
        # painted by `_draw_sunglasses` survives underneath.
        pygame.draw.circle(surf, parrot_mod.SHADE_BLACK, lens, r_outer)
        tint = pygame.Surface((r_outer * 2, r_outer), pygame.SRCALPHA)
        pygame.draw.ellipse(tint, (*parrot_mod.SHADE_TINT, 130),
                            tint.get_rect())
        surf.blit(tint, (lens[0] - r_outer, lens[1] - r_outer + 1))
        _draw_daze_spiral(surf, lens[0], lens[1])


def _build_dizzy_frame(wing_angle_deg):
    """Ports `parrot._build_frame` so the shades can be replaced in place;
    everything else is stock geometry."""
    surf = pygame.Surface((parrot_mod.SPRITE_W, parrot_mod.SPRITE_H),
                          pygame.SRCALPHA)

    tail_colors = [
        (200,  30,  40),
        (240,  95,  40),
        (255, 160,  55),
        (255, 220,  80),
    ]
    for i, c in enumerate(tail_colors):
        pygame.draw.polygon(surf, c, [
            (2 + i * 3, 26 + i * 2),
            (14 + i, 24 + i),
            (20 + i, 30 + i * 2),
            (6 + i * 3, 36 + i * 2),
        ])
    pygame.draw.line(surf, BIRD_RED_D, (4, 27), (18, 31), 1)
    pygame.draw.line(surf, BIRD_RED_D, (6, 33), (20, 35), 1)

    _aaellipse(surf, (120, 20, 25), (34, 35), 19, 14)
    _aaellipse(surf, BIRD_RED, (32, 32), 19, 14)
    _aaellipse(surf, (255, 100, 100), (30, 29), 13, 8)
    _aaellipse(surf, BIRD_BELLY, (28, 38), 12, 6)
    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 230, 230, 160), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    wing = parrot_mod._build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    _aaellipse(surf, (150, 15, 20), (48, 23), 12, 11)
    _aaellipse(surf, BIRD_RED, HEAD_C, 12, 11)
    _aaellipse(surf, (255, 130, 130), (44, 24), 4, 3)
    _aaellipse(surf, (255, 170, 170), (46, 16), 7, 3)

    _draw_dazed_shades(surf, 50, 20)

    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, BIRD_BEAK, beak_pts)
    pygame.draw.polygon(surf, BIRD_BEAK_D, beak_pts, 1)
    pygame.draw.line(surf, (255, 230, 150), (55, 22), (59, 24), 1)
    pygame.draw.line(surf, BIRD_BEAK_D, (52, 24), (58, 25), 1)

    pygame.draw.line(surf, BIRD_BEAK_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, BIRD_BEAK_D, (34, 45), (36, 49), 2)

    return surf


# Compressed flap range — a dazed bird beats shallower than a healthy one.
HURT_ANGLES = (10, -5, -20, -35)
_hurt_frames = [parrot_mod._add_outline(_build_dizzy_frame(a))
                for a in HURT_ANGLES]
_hurt_rot_cache = {}


def get_hurt_parrot(frame_idx, tilt_deg):
    fi = int(frame_idx) % 4
    key = (fi, int(round(tilt_deg / 3.0)) * 3)
    if key not in _hurt_rot_cache:
        # Sign matches `parrot.get_parrot` exactly — negating it would pitch
        # Pip nose-up on a dive and the pose would lie about the physics.
        _hurt_rot_cache[key] = pygame.transform.rotozoom(
            _hurt_frames[fi], key[1], 1.0)
    return _hurt_rot_cache[key]


def _star_points(cx, cy, r, scale=1.0):
    pts = []
    for i in range(5):
        a = math.radians(-90 + i * 72)
        pts.append((cx + r * scale * math.cos(a), cy + r * scale * math.sin(a)))
        ai = math.radians(-90 + i * 72 + 36)
        pts.append((cx + r * scale * 0.42 * math.cos(ai),
                    cy + r * scale * 0.42 * math.sin(ai)))
    return [(int(round(x)), int(round(y))) for x, y in pts]


def draw_star(surf, cx, cy, r, near, alpha=255):
    """Depth is read from radius and rim weight only. Fading the far stars
    instead would let them dissolve into a cloud or a night gradient, and a
    ring that half-disappears stops reading as a ring."""
    pts = _star_points(cx, cy, r)
    pygame.draw.polygon(surf, (*STAR_FILL, alpha), pts)
    pygame.draw.polygon(surf, (*STAR_RIM, alpha), pts, 2 if near else 1)
    if near:
        # Warm bevel inside the rim, not replacing it: it gives the big
        # stars a lit edge without spending the silhouette's dark border.
        pygame.draw.polygon(surf, (*STAR_BEVEL, alpha),
                            _star_points(cx, cy, r, 0.68), 1)


def star_ring_centre(bx, by, tilt):
    hx, hy = _rot_about(HEAD_C, SPRITE_C, -tilt)
    cx = bx + (hx - SPRITE_C[0])
    cy = by + (hy - SPRITE_C[1]) - HEAD_RY - ORBIT_GAP
    if cy - ORBIT_RY - 8 < HUD_FLOOR_Y:
        cy = HUD_FLOOR_Y + ORBIT_RY + 8
    return cx, cy


def draw_star_ring(surf, bx, by, tilt, phase_deg=ORBIT_PHASE):
    """Elliptical ring of 4 stars over the crown, drawn in SCREEN space.

    Anchored off the head ellipse rotated by Pip's dive tilt, so the ring
    follows the head without inheriting its roll — a ring that tumbled
    with the sprite would read as debris, not as dizziness."""
    cx, cy = star_ring_centre(bx, by, tilt)

    stars = []
    for i in range(4):
        a = math.radians(phase_deg + i * 90.0)
        ox, oy = ORBIT_RX * math.cos(a), ORBIT_RY * math.sin(a)
        ox, oy = _rot_about((ox, oy), (0.0, 0.0), ORBIT_TILT_DEG)
        stars.append((math.sin(a), cx + ox, cy + oy))

    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    # Painter's order: far stars first so the near ones overlap them.
    for depth, sx, sy in sorted(stars):
        near = depth > 0.0
        draw_star(layer, sx, sy, 5.0 if near else 3.0, near,
                  255 if near else 235)
    surf.blit(layer, (0, 0))
    return [(sx, sy, 5.0 if d > 0 else 3.0) for d, sx, sy in stars]


# ---------------------------------------------------------------- review sheet

def _blit_bird(surf, bx, by, tilt, fi=1, ring=True):
    spr = get_hurt_parrot(fi, tilt)
    surf.blit(spr, spr.get_rect(center=(bx, by)).topleft)
    if ring:
        draw_star_ring(surf, bx, by, tilt)


def _zoom(src, rect, factor):
    sub = src.subsurface(src.get_rect().clip(rect)).copy()
    return pygame.transform.scale(
        sub, (sub.get_width() * factor, sub.get_height() * factor))


def _label(surf, text, x, y, size=15, color=(235, 235, 240)):
    f = pygame.font.SysFont("dejavusans", size, bold=True)
    t = f.render(text, True, color)
    surf.blit(t, (x, y))
    return t.get_height()


_orig = parrot_mod.get_skin_frame
parrot_mod.get_skin_frame = lambda skin_id, fi, tilt: get_hurt_parrot(fi, tilt)

# Pillar/coin/ambient spawns roll off the global RNG, so the review shot
# is only reproducible if the seed is pinned before the world exists.
random.seed(11)

app = App()
app._start_play()
w = app.world

for _ in range(190):
    if w.bird.y > 300:
        w.flap()
    w.update(1 / 60.0)
for _ in range(600):
    if w.bird.y > 300:
        w.flap()
    w.update(1 / 60.0)
    if -16.0 < w.bird.tilt_deg < 4.0 and 250 < w.bird.y < 340:
        break
else:
    raise SystemExit("no level-ish pose found — reseed")

w.lives_remaining = 0
try:
    w.bird.on_last_life = True
except AttributeError:
    w.bird.__dict__["on_last_life"] = True

app._render()
draw_star_ring(app.screen, w.bird.x, w.bird.y, w.bird.tilt_deg)
shot = app.screen.copy()
parrot_mod.get_skin_frame = _orig

prev = pygame.image.load(f"{OUT_DIR}/round_1.png").convert()

SHEET = pygame.Surface((1180, 760))
SHEET.fill((26, 26, 32))

_label(SHEET, "dizzy-dazed — ROUND 2", 20, 14, 22, (255, 235, 200))
_label(SHEET, "hard dark rim on every star · no alpha ramp · binary radii 5/3 · "
              "ORBIT_GAP 26 · spiral daze glints · micro-nudges dropped",
       20, 42, 13, (170, 172, 182))

_label(SHEET, "ROUND 1 (prev)", 20, 72, 14, (150, 152, 162))
SHEET.blit(pygame.transform.scale(prev, (270, 480)), (20, 92))

_label(SHEET, "ROUND 2 — in play, 1x", 310, 72, 14)
SHEET.blit(pygame.transform.scale(shot, (270, 480)), (310, 92))

bx, by = int(w.bird.x), int(w.bird.y)
crop = pygame.Rect(bx - 46, by - 62, 92, 76)
_label(SHEET, "head detail, 4x", 610, 72, 14)
SHEET.blit(_zoom(shot, crop, 4), (610, 92))

# Three skies at 1x: the ring has to survive the brightest cloud and the
# darkest night without an alpha ramp to hide behind.
_label(SHEET, "1x on cloud / day / night", 610, 420, 14)
for i, (name, bg) in enumerate((("cloud", (246, 248, 252)),
                                ("day", (108, 176, 228)),
                                ("night", (24, 28, 58)))):
    tile = pygame.Surface((172, 128))
    tile.fill(bg)
    _blit_bird(tile, 86, 82, -8.0)
    SHEET.blit(tile, (610 + i * 182, 442))
    _label(SHEET, name, 610 + i * 182 + 4, 574, 12, (150, 152, 162))

_label(SHEET, "world-up check — ring holds level through the tilt range", 20, 592, 14)
strip = pygame.Surface((1140, 148))
strip.fill((92, 158, 214))
for i, tl in enumerate((-25.0, 0.0, 35.0, 70.0, 88.0)):
    _blit_bird(strip, 120 + i * 228, 92, tl, fi=1)
    f = pygame.font.SysFont("dejavusans", 12, bold=True)
    strip.blit(f.render(f"{tl:+.0f}°", True, (16, 24, 40)),
               (120 + i * 228 - 14, 128))
SHEET.blit(strip, (20, 612))

pygame.image.save(SHEET, OUT)

# ---- verification ----------------------------------------------------------
px = pygame.PixelArray(shot)
cream = gold = 0
for yy in range(max(0, by - 70), min(shot.get_height(), by + 20)):
    for xx in range(max(0, bx - 60), min(shot.get_width(), bx + 60)):
        r, g, b, _ = shot.unmap_rgb(px[xx][yy])
        if 235 <= r <= 255 and 230 <= g <= 250 and 200 <= b <= 225:
            cream += 1
        if 240 <= r <= 255 and 195 <= g <= 215 and 40 <= b <= 80:
            gold += 1
del px

# Clearance: lowest pixel of the near stars vs the topmost drawn pixel of
# the rotated sprite, measured on real pixels rather than the ellipse maths.
probe = pygame.Surface((240, 240), pygame.SRCALPHA)
tl = w.bird.tilt_deg
spr = get_hurt_parrot(1, tl)
probe.blit(spr, spr.get_rect(center=(120, 140)).topleft)
crown_top = min((yy for yy in range(240) for xx in range(240)
                 if probe.get_at((xx, yy))[3] > 40), default=None)
stars = draw_star_ring(pygame.Surface((240, 240), pygame.SRCALPHA),
                       120, 140, tl)
near_low = max(sy + r for sx, sy, r in stars if r > 4)
print(f"Saved: {OUT}")
print(f"bird=({bx},{by}) tilt={tl:.1f} score={w.score}")
print(f"cream_px={cream}  coin_gold_px={gold}")
print(f"crown_top_y={crown_top}  near_star_low_y={near_low:.1f}  "
      f"clearance={crown_top - near_low:.1f}px")
