"""Round-1 review render for the `dizzy-dazed` hurt-parrot skin.

Two halves to the look, deliberately kept apart:

* Baked into the 64x60 frame — a compressed flap range, a beak nudged
  down-right (a slack jaw), and a tail fanned wider than Pip ever holds
  it. Body colours stay stock; the read comes from posture only.
* Composited AFTER rotation — the orbiting stars. They must not tumble
  with Pip's dive tilt, which is exactly what baking them in would do,
  so the ring is drawn in screen space over the finished frame.

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
OUT = f"{OUT_DIR}/round_1.png"

_aaellipse = parrot_mod._aaellipse

# Cream-white, not coin gold (255,210,70) — gold at this size on this
# sky reads as a collectible and players would try to fly into it.
STAR_FILL = (255, 245, 215)
STAR_OUTLINE = (230, 180, 110)

# Head ellipse in sprite space, straight out of `_build_frame`.
HEAD_C = (47, 21)
HEAD_RY = 11
SPRITE_C = (parrot_mod.SPRITE_W / 2.0, parrot_mod.SPRITE_H / 2.0)

TAIL_ROOT = (20, 32)
TAIL_SPLAY_DEG = 3.0

ORBIT_RX, ORBIT_RY = 13.0, 5.0
ORBIT_TILT_DEG = 15.0
ORBIT_GAP = 18.0          # clearance above the crown, per the brief


def _rot_about(pt, origin, deg):
    """Rotate in sprite/screen space (y grows downward), so a positive
    `deg` here is a visually clockwise turn."""
    a = math.radians(deg)
    dx, dy = pt[0] - origin[0], pt[1] - origin[1]
    return (origin[0] + dx * math.cos(a) - dy * math.sin(a),
            origin[1] + dx * math.sin(a) + dy * math.cos(a))


def _build_dizzy_frame(wing_angle_deg):
    """Ports `parrot._build_frame` rather than overpainting it: the beak
    nudge and the tail splay both MOVE existing geometry, and painting
    over the original would leave its silhouette poking out."""
    surf = pygame.Surface((parrot_mod.SPRITE_W, parrot_mod.SPRITE_H),
                          pygame.SRCALPHA)

    tail_colors = [
        (200,  30,  40),
        (240,  95,  40),
        (255, 160,  55),
        (255, 220,  80),
    ]
    for i, c in enumerate(tail_colors):
        pts = [
            (2 + i * 3, 26 + i * 2),
            (14 + i, 24 + i),
            (20 + i, 30 + i * 2),
            (6 + i * 3, 36 + i * 2),
        ]
        # Fan pivots on the tail root so the wedges stay joined to the
        # body while the outer ones swing furthest.
        splay = (i - 1.5) * TAIL_SPLAY_DEG
        pygame.draw.polygon(
            surf, c, [_rot_about(p, TAIL_ROOT, splay) for p in pts])
    pygame.draw.line(surf, BIRD_RED_D,
                     _rot_about((4, 27), TAIL_ROOT, -3.0),
                     _rot_about((18, 31), TAIL_ROOT, -3.0), 1)
    pygame.draw.line(surf, BIRD_RED_D,
                     _rot_about((6, 33), TAIL_ROOT, 3.0),
                     _rot_about((20, 35), TAIL_ROOT, 3.0), 1)

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

    parrot_mod._draw_sunglasses(surf, 50, 20)

    # Beak dropped 1 right / 2 down — a jaw hanging slightly open.
    beak_pts = [(56, 23), (62, 26), (59, 30), (53, 28)]
    pygame.draw.polygon(surf, BIRD_BEAK, beak_pts)
    pygame.draw.polygon(surf, BIRD_BEAK_D, beak_pts, 1)
    pygame.draw.line(surf, (255, 230, 150), (56, 24), (60, 26), 1)
    pygame.draw.line(surf, BIRD_BEAK_D, (53, 26), (59, 27), 1)

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


def draw_star(surf, cx, cy, r, fill, outline):
    pts = []
    for i in range(5):
        a = math.radians(-90 + i * 72)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        ai = math.radians(-90 + i * 72 + 36)
        pts.append((cx + r * 0.42 * math.cos(ai), cy + r * 0.42 * math.sin(ai)))
    ipts = [(int(round(x)), int(round(y))) for x, y in pts]
    pygame.draw.polygon(surf, fill, ipts)
    pygame.draw.polygon(surf, outline, ipts, 1)


def draw_star_ring(surf, bird, phase_deg=0.0):
    """Elliptical ring of 4 stars over the crown, drawn in SCREEN space.

    Anchored off the head ellipse rotated by Pip's dive tilt, so the ring
    follows the head without inheriting its roll — a ring that tumbled
    with the sprite would read as debris, not as dizziness."""
    tilt = bird.tilt_deg
    hx, hy = _rot_about(HEAD_C, SPRITE_C, -tilt)
    cx = bird.x + (hx - SPRITE_C[0])
    cy = bird.y + (hy - SPRITE_C[1]) - HEAD_RY - ORBIT_GAP

    stars = []
    for i in range(4):
        a = math.radians(phase_deg + i * 90.0)
        ox, oy = ORBIT_RX * math.cos(a), ORBIT_RY * math.sin(a)
        ox, oy = _rot_about((ox, oy), (0.0, 0.0), ORBIT_TILT_DEG)
        depth = (math.sin(a) + 1.0) * 0.5      # 0 = far side, 1 = near
        stars.append((depth, cx + ox, cy + oy))

    # Depth is carried by size + opacity on a scratch layer. Darkening the
    # fill instead would turn the far stars grey-brown, and a dirty star
    # reads as a stain rather than as distance.
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    # Painter's order: far stars first so the near ones overlap them.
    for depth, sx, sy in sorted(stars):
        r = 3.0 + 2.0 * depth
        alpha = int(165 + 90 * depth)
        draw_star(layer, sx, sy, r,
                  (*STAR_FILL, alpha), (*STAR_OUTLINE, alpha))
    surf.blit(layer, (0, 0))


_orig = parrot_mod.get_skin_frame
parrot_mod.get_skin_frame = lambda skin_id, fi, tilt: get_hurt_parrot(fi, tilt)

# Pillar/coin/ambient spawns roll off the global RNG, so the review shot
# is only reproducible if the seed is pinned before the world exists.
random.seed(11)

app = App()
app._start_play()
w = app.world

# Scroll the world in so the shot has pillars, coins and terrain rather
# than an empty opener sky, then hold for a frame where Pip is near the
# top of a flap arc: a full-dive pose hides the head under the tilt and
# buries the star ring in the sprite.
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
draw_star_ring(app.screen, w.bird)
pygame.image.save(app.screen, OUT)
parrot_mod.get_skin_frame = _orig
print(f"Saved: {OUT}  bird at ({w.bird.x:.0f},{w.bird.y:.0f}) "
      f"tilt={w.bird.tilt_deg:.1f} score={w.score}")
