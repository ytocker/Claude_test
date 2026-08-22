"""Shared nest helpers for the cup-mouth concept renders.

Verbatim helper block from docs/nest-alive-3d/patched-void/render.py plus a
small assembly API so each concept only writes its own mouth treatment.
"""
import os, sys, math
os.environ.setdefault('SDL_VIDEODRIVER', 'offscreen')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, '/home/user/skybit')
import pygame
pygame.init()
import game.parrot as parrot

_NEST_S           = 0.80
_NEST_CX          = 31
_NEST_TWIG_BRIGHT = (160, 110, 55)
_NEST_TWIG_MID    = (110,  75, 35)
_NEST_TWIG_DARK   = ( 70,  45, 18)
_NEST_STICK_COL   = (130,  90, 42)
_NEST_STICK_HI    = (170, 120, 60)
_NEST_STICK_SH    = ( 80,  55, 22)
_NEST_COURSE_TOP  = (180, 130, 65)
_NEST_COURSE_BOT  = ( 80,  55, 22)
_NEST_HOLLOW_COL  = ( 50,  35, 14)
_NEST_STICK_X_OFF = (-1, 0, 1, 2)
SKY = (136, 183, 197)

def _nest_cy_sag(x, x1, x2, base_y, sag):
    half_w = (x2 - x1) / 2.0
    if half_w <= 0: return base_y
    t = ((x - x1) / half_w) - 1.0
    return base_y + int(round(sag * (1.0 - t * t)))

def _nest_stick_row(surf, vx, y):
    surf.set_at((vx-1, y), _NEST_STICK_HI); surf.set_at((vx, y), _NEST_STICK_COL)
    surf.set_at((vx+1, y), _NEST_STICK_COL); surf.set_at((vx+2, y), _NEST_STICK_SH)

def _nest_stick_span(surf, vx, y1, y2):
    for y in range(y1, y2 + 1): _nest_stick_row(surf, vx, y)

def _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col):
    y = _nest_cy_sag(x, x1, x2, base_y, sag)
    surf.set_at((x, y), _NEST_COURSE_TOP); surf.set_at((x, y+1), mid_col)
    surf.set_at((x, y+2), mid_col); surf.set_at((x, y+3), _NEST_COURSE_BOT)

def _nest_course_full(surf, x1, x2, base_y, sag, mid_col, skip_xs):
    skip_set = set()
    for sx in skip_xs:
        for dx in _NEST_STICK_X_OFF: skip_set.add(sx + dx)
    for x in range(x1, x2 + 1):
        if x not in skip_set: _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col)

def _nest_course_at_vx(surf, vx, x1, x2, base_y, sag, mid_col):
    for dx in _NEST_STICK_X_OFF:
        x = vx + dx
        if x1 <= x <= x2: _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col)

def _nest_stick_at_course(surf, vx, x1, x2, base_y, sag):
    y_top = _nest_cy_sag(vx, x1, x2, base_y, sag)
    for y in range(y_top, y_top + 4): _nest_stick_row(surf, vx, y)

def _nest_notches(surf, cy, courses, stick_wins):
    for ci, (offset, col, x1, x2, sag) in enumerate(courses):
        base_y = cy + offset
        for (cii, vx), wins in stick_wins.items():
            if cii != ci: continue
            y_cross = _nest_cy_sag(vx, x1, x2, base_y, sag)
            if wins:
                for x in [vx-2, vx+3]:
                    if x1 <= x <= x2:
                        surf.set_at((x, y_cross+1), _NEST_TWIG_DARK)
                        surf.set_at((x, y_cross+2), _NEST_TWIG_DARK)
            else:
                for dy in (-1, 4):
                    surf.set_at((vx, y_cross+dy), _NEST_TWIG_DARK)
                    surf.set_at((vx+1, y_cross+dy), _NEST_TWIG_DARK)

def _nest_weave(surf, cy, ci_range, courses, stick_wins):
    for ci in ci_range:
        offset, col, x1, x2, sag = courses[ci]
        base_y = cy + offset
        skip = [vx for (cii, vx), wins in stick_wins.items() if cii == ci and wins]
        _nest_course_full(surf, x1, x2, base_y, sag, col, skip_xs=skip)
        for (cii, vx), wins in stick_wins.items():
            if cii == ci and not wins:
                _nest_course_at_vx(surf, vx, x1, x2, base_y, sag, col)

def _make_nest_params():
    s = _NEST_S; cx = _NEST_CX; r = lambda v: round(v * s)
    verts = [cx - r(9), cx + r(9)]
    courses = [
        (r(2),  _NEST_TWIG_BRIGHT, cx-r(21), cx+r(21), max(1, r(2))),
        (r(6),  _NEST_TWIG_MID,    cx-r(20), cx+r(20), max(1, r(2))),
        (r(10), _NEST_TWIG_BRIGHT, cx-r(18), cx+r(18), max(1, r(2))),
        (r(14), _NEST_TWIG_MID,    cx-r(16), cx+r(16), max(1, r(2))),
        (r(18), _NEST_TWIG_BRIGHT, cx-r(14), cx+r(14), max(1, r(3))),
    ]
    vxL, vxR = verts
    stick_wins = {(ci, vxL): (ci % 2 == 0) for ci in range(5)}
    stick_wins.update({(ci, vxR): (ci % 2 == 1) for ci in range(5)})
    rim_rect     = (cx-r(21), -r(5), r(42), max(4, r(12)))
    stick_bottom = r(18)
    hollow       = (cx-r(11), r(16), r(22), max(2, r(3)))
    src    = parrot._get_frames()[1]
    bird_h = 34
    bird_w = max(1, int(src.get_width() * bird_h / src.get_height()))
    bird   = pygame.transform.smoothscale(src, (bird_w, bird_h))
    return verts, courses, stick_wins, rim_rect, stick_bottom, hollow, bird, bird_w, bird_h

P = _make_nest_params()
VERTS, COURSES, STICK_WINS, RIM_RECT, STICK_BOTTOM, HOLLOW, BIRD, BW, BH = P
RX, RYOFF, RW, RH = RIM_RECT
CX = _NEST_CX


def geo(cy):
    """Mouth geometry: rect, center, semi-axes."""
    ry = cy + RYOFF
    return RX, ry, RW, RH, RX + RW / 2.0, ry + RH / 2.0, RW / 2.0, RH / 2.0


def t_ell(px, py, ecx, ecy, ra, rb):
    """Normalized elliptical radius: 0 center, 1 on the rim boundary."""
    return math.sqrt(((px - ecx) / ra) ** 2 + ((py - ecy) / rb) ** 2)


def sticks_weave01(surf, cy):
    """Arc-gap fix pixels, vertical sticks, upper weave courses."""
    _vxL = VERTS[0]
    for _dy in (-2, -1):
        _y = cy + RYOFF + RH + _dy
        for _dx in _NEST_STICK_X_OFF: surf.set_at((_vxL + _dx, _y), _NEST_TWIG_BRIGHT)
    for vx in VERTS: _nest_stick_span(surf, vx, cy + RYOFF + RH, cy + STICK_BOTTOM)
    _nest_weave(surf, cy, (0, 1), COURSES, STICK_WINS)


def front_chrome(surf, cy):
    """Lower weave courses, stick crossings, notches — drawn in front."""
    _nest_weave(surf, cy, (2, 3, 4), COURSES, STICK_WINS)
    for ci in (2, 3, 4):
        offset, col, x1, x2, sag = COURSES[ci]
        base_y = cy + offset
        for (cii, vx), wins in STICK_WINS.items():
            if cii == ci and wins: _nest_stick_at_course(surf, vx, x1, x2, base_y, sag)
    _nest_notches(surf, cy, COURSES, STICK_WINS)


def make_black_sil(cy, clip_top_half=True):
    """Parrot-shaped black void sprite + blit pos (rows above rim clipped;
    optionally clipped to the mouth oval in its top half)."""
    bx, by = CX - BW // 2, cy - BH // 2 + 5
    rx, ry, rw, rh, ecx, ecy, ra, rb = geo(cy)
    sil = pygame.Surface((BW, BH), pygame.SRCALPHA)
    for sy in range(BH):
        py = by + sy
        if py < ry: continue
        for sx in range(BW):
            a = BIRD.get_at((sx, sy))[3]
            if a == 0: continue
            px = bx + sx
            if clip_top_half and py < ecy and t_ell(px, py, ecx, ecy, ra, rb) > 1.0:
                continue
            sil.set_at((sx, sy), (0, 0, 0, a))
    return sil, bx, by


def render_pair(draw_slot, out_path, zoom=10, gap=12):
    """Standard concept output: alive | empty at 10x + sky-leak check."""
    W, H, CY = 62, 100, 73
    panels = []
    for alive in (True, False):
        s = pygame.Surface((W, H)); s.fill(SKY)
        draw_slot(s, CY, alive)
        panels.append(pygame.transform.scale(s, (W*zoom, H*zoom)))
    canvas = pygame.Surface((2*W*zoom + gap, H*zoom)); canvas.fill((8, 8, 20))
    canvas.blit(panels[0], (0, 0)); canvas.blit(panels[1], (W*zoom + gap, 0))
    pygame.image.save(canvas, out_path)
    s = pygame.Surface((W, H)); s.fill(SKY)
    draw_slot(s, CY, False)
    rx, ry, rw, rh, ecx, ecy, ra, rb = geo(CY)
    leaks = [(x, y) for y in range(ry, ry + rh + 1) for x in range(rx, rx + rw + 1)
             if t_ell(x, y, ecx, ecy, ra, rb) < 0.92 and s.get_at((x, y))[:3] == SKY]
    print('saved', out_path, '| sky leaks in mouth:', leaks[:4] if leaks else 'none ok')
