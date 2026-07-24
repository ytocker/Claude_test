"""
Smooth-taper logcabin weave — V14
Identical to V12 round_2 in every way EXCEPT: each of the 5 courses
has its own x-span, narrowing by 2px per side per course (42→40→36→32→28px).
No hard step — one gradual taper from wide rim to tight base.
"""
import os, sys, math
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
import game.parrot as parrot_mod
import game.hud as hud_module
from game.scenes import App

PANEL_DARK   = (12, 8, 38)
GOLD_BRIGHT  = (240, 192, 64)
OUTER_SHADOW = (4, 4, 12)
TWIG_BRIGHT  = (160, 110, 55)
TWIG_MID     = (110, 75, 35)
TWIG_DARK    = (70, 45, 18)

STICK_COL = (130, 90, 42)
STICK_HI  = (170, 120, 60)
STICK_SH  = (80, 55, 22)

COURSE_TOP = (180, 130, 65)
COURSE_BOT = (80, 55, 22)
HOLLOW_COL = (50, 35, 14)

CX      = 31
CY_LIST = [73, 113]
VERTS   = [22, 40]

_src  = parrot_mod._get_frames()[1]
_ih   = 34
_iw   = max(1, int(_src.get_width() * _ih / _src.get_height()))
_bird = pygame.transform.smoothscale(_src, (_iw, _ih))

# ── The only change from V12: each course has a unique width ──────────────────
# Course widths: 42 → 40 → 36 → 32 → 28 px (2px narrower each side per step)
# CX=31, so left = CX − half, right = CX + half
COURSES = [
    (2,  TWIG_BRIGHT, 10, 52, 2),   # course 0 — 42px  (±21 from CX)
    (6,  TWIG_MID,   11, 51, 2),    # course 1 — 40px  (±20)
    (10, TWIG_BRIGHT, 13, 49, 2),   # course 2 — 36px  (±18)
    (14, TWIG_MID,   15, 47, 2),    # course 3 — 32px  (±16)
    (18, TWIG_BRIGHT, 17, 45, 3),   # course 4 — 28px  (±14) deepest sag
]

STICK_WINS = {
    (0, 22): True,  (0, 40): False,
    (1, 22): False, (1, 40): True,
    (2, 22): True,  (2, 40): False,
    (3, 22): False, (3, 40): True,
    (4, 22): True,  (4, 40): False,
}

_STICK_X_OFFSET = (-1, 0, 1, 2)


def _cy_sag(x, x1, x2, base_y, sag):
    half_w = (x2 - x1) / 2.0
    if half_w <= 0:
        return base_y
    t = ((x - x1) / half_w) - 1.0
    return base_y + int(round(sag * (1.0 - t * t)))


def _draw_stick_row(surf, vx, y):
    surf.set_at((vx - 1, y), STICK_HI)
    surf.set_at((vx,     y), STICK_COL)
    surf.set_at((vx + 1, y), STICK_COL)
    surf.set_at((vx + 2, y), STICK_SH)


def _draw_stick_span(surf, vx, y1, y2):
    for y in range(y1, y2 + 1):
        _draw_stick_row(surf, vx, y)


def _draw_course_col(surf, x, x1, x2, base_y, sag, mid_col):
    y = _cy_sag(x, x1, x2, base_y, sag)
    surf.set_at((x, y),     COURSE_TOP)
    surf.set_at((x, y + 1), mid_col)
    surf.set_at((x, y + 2), mid_col)
    surf.set_at((x, y + 3), COURSE_BOT)


def _draw_course_full(surf, x1, x2, base_y, sag, mid_col, skip_xs):
    skip_set = set()
    for sx in skip_xs:
        for dx in _STICK_X_OFFSET:
            skip_set.add(sx + dx)
    for x in range(x1, x2 + 1):
        if x not in skip_set:
            _draw_course_col(surf, x, x1, x2, base_y, sag, mid_col)


def _draw_course_at_vx(surf, vx, x1, x2, base_y, sag, mid_col):
    for dx in _STICK_X_OFFSET:
        x = vx + dx
        if x1 <= x <= x2:
            _draw_course_col(surf, x, x1, x2, base_y, sag, mid_col)


def _draw_stick_at_course(surf, vx, x1, x2, base_y, sag):
    y_top = _cy_sag(vx, x1, x2, base_y, sag)
    for y in range(y_top, y_top + 4):
        _draw_stick_row(surf, vx, y)


def _draw_back_rim(surf, cy):
    pygame.draw.arc(surf, TWIG_BRIGHT,
                    (10, cy - 5, 42, 12), 0, math.pi, 2)


def _draw_notches(surf, cy, ci_range):
    for ci in ci_range:
        offset, col, x1, x2, sag = COURSES[ci]
        base_y = cy + offset
        for vx in VERTS:
            y_cross = _cy_sag(vx, x1, x2, base_y, sag)
            if STICK_WINS[(ci, vx)]:
                for x in [vx - 2, vx + 3]:
                    if x1 <= x <= x2:
                        surf.set_at((x, y_cross + 1), TWIG_DARK)
                        surf.set_at((x, y_cross + 2), TWIG_DARK)
            else:
                for dy in (-1, 4):
                    surf.set_at((vx,     y_cross + dy), TWIG_DARK)
                    surf.set_at((vx + 1, y_cross + dy), TWIG_DARK)


def _weave_courses(surf, cy, ci_range):
    for ci in ci_range:
        offset, col, x1, x2, sag = COURSES[ci]
        base_y = cy + offset
        skip = [vx for vx in VERTS if STICK_WINS[(ci, vx)]]
        _draw_course_full(surf, x1, x2, base_y, sag, col, skip_xs=skip)
        for vx in VERTS:
            if not STICK_WINS[(ci, vx)]:
                _draw_course_at_vx(surf, vx, x1, x2, base_y, sag, col)


def draw_slot(surf, cx, cy, alive):
    _draw_back_rim(surf, cy)
    for vx in VERTS:
        _draw_stick_span(surf, vx, cy, cy + 18)
    _weave_courses(surf, cy, (0, 1))

    if alive:
        surf.blit(_bird, (cx - _iw // 2, cy - _ih // 2 + 5))
    else:
        pygame.draw.rect(surf, HOLLOW_COL, (cx - 11, cy + 16, 22, 3))

    _weave_courses(surf, cy, (2, 3, 4))
    for ci in (2, 3, 4):
        offset, col, x1, x2, sag = COURSES[ci]
        base_y = cy + offset
        for vx in VERTS:
            if STICK_WINS[(ci, vx)]:
                _draw_stick_at_course(surf, vx, x1, x2, base_y, sag)
    _draw_notches(surf, cy, range(5))


def _draw(surf, lives_remaining, lives_total, cy=106):
    pygame.draw.rect(surf, OUTER_SHADOW, (1, 56, 60, 82), 1, border_radius=6)
    pygame.draw.rect(surf, PANEL_DARK,   (2, 57, 58, 80),    border_radius=5)
    pygame.draw.rect(surf, GOLD_BRIGHT,  (2, 57, 58, 80), 1, border_radius=5)
    for i, cy_s in enumerate(CY_LIST[:max(lives_total, 2)]):
        draw_slot(surf, CX, cy_s, i < lives_remaining)


hud_module._draw_pip_lives_row = _draw
hud_module._PIP_ICON_ALIVE = None
hud_module._PIP_ICON_SPENT = None

OUT_DIR = "/home/user/skybit/docs/lives-display-v14/smooth-taper-weave"
OUT     = f"{OUT_DIR}/round_1.png"

app = App()
app._start_play()
app.world.lives_remaining = 1
app._render()
pygame.image.save(app.screen, OUT)
print(f"Saved: {OUT}")

from PIL import Image
img   = Image.open(OUT)
pix   = img.load()
count = sum(1 for y in range(58, 92) for x in range(0, 63)
            if pix[x, y][0] > 150 and pix[x, y][1] < 110)
print(f"Bird-red pixels: {count} (need >20)")
assert count > 20, f"FAIL: only {count}"
print("PASS")
