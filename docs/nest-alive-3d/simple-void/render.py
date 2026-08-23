"""simple-void: empty nest shows a parrot-shaped black void.

Sole change vs. today's shipped slot (draw_slot_before):
  alive=False  →  blit the parrot's alpha silhouette as pure black (0,0,0)
                  instead of the dark-brown hollow rectangle.

The void is shaped exactly like the bird, reads as the deep cup interior.
The alive state is completely unchanged.
"""
import os, sys, math
os.environ.setdefault('SDL_VIDEODRIVER', 'offscreen')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, '/home/user/skybit')
import pygame
import pygame.surfarray
pygame.init()
import game.parrot as parrot

# ── Constants (verbatim from game/hud.py) ────────────────────────────────────

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


# ── Nest helpers (verbatim from game/hud.py) ─────────────────────────────────

def _nest_cy_sag(x, x1, x2, base_y, sag):
    half_w = (x2 - x1) / 2.0
    if half_w <= 0: return base_y
    t = ((x - x1) / half_w) - 1.0
    return base_y + int(round(sag * (1.0 - t * t)))


def _nest_stick_row(surf, vx, y):
    surf.set_at((vx-1, y), _NEST_STICK_HI)
    surf.set_at((vx,   y), _NEST_STICK_COL)
    surf.set_at((vx+1, y), _NEST_STICK_COL)
    surf.set_at((vx+2, y), _NEST_STICK_SH)


def _nest_stick_span(surf, vx, y1, y2):
    for y in range(y1, y2 + 1):
        _nest_stick_row(surf, vx, y)


def _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col):
    y = _nest_cy_sag(x, x1, x2, base_y, sag)
    surf.set_at((x, y),   _NEST_COURSE_TOP)
    surf.set_at((x, y+1), mid_col)
    surf.set_at((x, y+2), mid_col)
    surf.set_at((x, y+3), _NEST_COURSE_BOT)


def _nest_course_full(surf, x1, x2, base_y, sag, mid_col, skip_xs):
    skip_set = set()
    for sx in skip_xs:
        for dx in _NEST_STICK_X_OFF: skip_set.add(sx + dx)
    for x in range(x1, x2 + 1):
        if x not in skip_set:
            _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col)


def _nest_course_at_vx(surf, vx, x1, x2, base_y, sag, mid_col):
    for dx in _NEST_STICK_X_OFF:
        x = vx + dx
        if x1 <= x <= x2:
            _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col)


def _nest_stick_at_course(surf, vx, x1, x2, base_y, sag):
    y_top = _nest_cy_sag(vx, x1, x2, base_y, sag)
    for y in range(y_top, y_top + 4):
        _nest_stick_row(surf, vx, y)


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
                    surf.set_at((vx,   y_cross+dy), _NEST_TWIG_DARK)
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


# ── Draw functions ────────────────────────────────────────────────────────────

def draw_slot_before(surf, cy, alive):
    """Today's shipped slot — verbatim from game/hud.py _nest_draw_slot."""
    verts, courses, stick_wins, rim_rect, stick_bottom, hollow, bird, bw, bh = P
    cx = _NEST_CX
    rx, ry_off, rw, rh = rim_rect
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, cy + ry_off, rw, rh))
    pygame.draw.arc(surf, _NEST_TWIG_BRIGHT, (rx, cy + ry_off, rw, rh), 0, math.pi, 2)
    _vxL = verts[0]
    for _dy in (-2, -1):
        _y = cy + ry_off + rh + _dy
        for _dx in _NEST_STICK_X_OFF:
            surf.set_at((_vxL + _dx, _y), _NEST_TWIG_BRIGHT)
    for vx in verts:
        _nest_stick_span(surf, vx, cy + ry_off + rh, cy + stick_bottom)
    _nest_weave(surf, cy, (0, 1), courses, stick_wins)
    if alive:
        surf.blit(bird, (cx - bw // 2, cy - bh // 2 + 5))
    else:
        hx, hy_off, hw, hh = hollow
        pygame.draw.rect(surf, _NEST_HOLLOW_COL, (hx, cy + hy_off, hw, hh))
    _nest_weave(surf, cy, (2, 3, 4), courses, stick_wins)
    for ci in (2, 3, 4):
        offset, col, x1, x2, sag = courses[ci]
        base_y = cy + offset
        for (cii, vx), wins in stick_wins.items():
            if cii == ci and wins:
                _nest_stick_at_course(surf, vx, x1, x2, base_y, sag)
    _nest_notches(surf, cy, courses, stick_wins)


def draw_slot_after(surf, cy, alive):
    """Concept: empty nest shows a parrot-shaped black void."""
    verts, courses, stick_wins, rim_rect, stick_bottom, hollow, bird, bw, bh = P
    cx = _NEST_CX
    rx, ry_off, rw, rh = rim_rect
    bx, by = cx - bw // 2, cy - bh // 2 + 5

    pygame.draw.ellipse(surf, (0, 0, 0), (rx, cy + ry_off, rw, rh))
    # Full oval ring: closed outline avoids arc endpoint gaps; front half overdrawn brighter.
    pygame.draw.ellipse(surf, _NEST_TWIG_MID,    (rx, cy + ry_off, rw, rh), 2)
    pygame.draw.arc(surf,    _NEST_TWIG_BRIGHT,  (rx, cy + ry_off, rw, rh), 0, math.pi, 2)
    _vxL = verts[0]
    for _dy in (-2, -1):
        _y = cy + ry_off + rh + _dy
        for _dx in _NEST_STICK_X_OFF:
            surf.set_at((_vxL + _dx, _y), _NEST_TWIG_BRIGHT)
    for vx in verts:
        _nest_stick_span(surf, vx, cy + ry_off + rh, cy + stick_bottom)
    _nest_weave(surf, cy, (0, 1), courses, stick_wins)
    # Re-clear any weave pixels that landed inside the rim ellipse, then restore the ring.
    pygame.draw.ellipse(surf, (0, 0, 0),        (rx, cy + ry_off, rw, rh))
    pygame.draw.ellipse(surf, _NEST_TWIG_MID,   (rx, cy + ry_off, rw, rh), 2)
    pygame.draw.arc(surf,    _NEST_TWIG_BRIGHT, (rx, cy + ry_off, rw, rh), 0, math.pi, 2)

    if alive:
        surf.blit(bird, (bx, by))
    else:
        # Parrot alpha silhouette zeroed to pure black — bird-shaped cup shadow.
        # Clip to rim ellipse so no dark pixels bleed outside the oval boundary.
        sil = bird.copy()
        arr = pygame.surfarray.pixels3d(sil)
        arr[:] = 0
        del arr
        ecx = rx + rw / 2.0
        ecy = cy + ry_off + rh / 2.0
        ra, rb = rw / 2.0, rh / 2.0
        alp = pygame.surfarray.pixels_alpha(sil)
        for sy in range(sil.get_height()):
            for sx in range(sil.get_width()):
                if ((bx + sx - ecx) / ra) ** 2 + ((by + sy - ecy) / rb) ** 2 >= 1.0:
                    alp[sx, sy] = 0
        del alp
        surf.blit(sil, (bx, by))

    _nest_weave(surf, cy, (2, 3, 4), courses, stick_wins)
    for ci in (2, 3, 4):
        offset, col, x1, x2, sag = courses[ci]
        base_y = cy + offset
        for (cii, vx), wins in stick_wins.items():
            if cii == ci and wins:
                _nest_stick_at_course(surf, vx, x1, x2, base_y, sag)
    _nest_notches(surf, cy, courses, stick_wins)
    # Redraw ring on top so it sits above notches and any final overdraw.
    pygame.draw.ellipse(surf, _NEST_TWIG_MID,   (rx, cy + ry_off, rw, rh), 2)
    pygame.draw.arc(surf,    _NEST_TWIG_BRIGHT, (rx, cy + ry_off, rw, rh), 0, math.pi, 2)
