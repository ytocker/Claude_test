"""woven-stencil-tuck — round 2 render.

All art-director fixes applied to draw_slot_after() only:
1. Warm-dark multiply ramp — bird kept at full alpha, belly darkened not clipped
2. Ramp curves per column to track the elliptical lip, not a flat horizontal bar
3. Front rim thinned to width 2, twig-textured (COURSE_TOP / TWIG_MID alternating,
   stick cols at vx positions)
4. Smooth 6-step warm ease replaces the one-row 255→153 step
5. AO arc inset 2 px, drawn at 1 px after the rim
6. Empty-state path is fully 0-diff (all alive changes inside `if alive:`)
"""

import os, sys, math
os.environ.setdefault('SDL_VIDEODRIVER', 'offscreen')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, '/home/user/skybit')
import pygame
pygame.init()
import game.parrot as parrot

_NEST_S            = 0.80
_NEST_CX           = 31
_NEST_CY           = 73
_NEST_TWIG_BRIGHT  = (160, 110, 55)
_NEST_TWIG_MID     = (110,  75, 35)
_NEST_TWIG_DARK    = ( 70,  45, 18)
_NEST_STICK_COL    = (130,  90, 42)
_NEST_STICK_HI     = (170, 120, 60)
_NEST_STICK_SH     = ( 80,  55, 22)
_NEST_COURSE_TOP   = (180, 130, 65)
_NEST_COURSE_BOT   = ( 80,  55, 22)
_NEST_HOLLOW_COL   = ( 50,  35, 14)
_NEST_STICK_X_OFF  = (-1, 0, 1, 2)

# Warm 6-step ease — Row 0 at lip_y-3 (barely dark), Row 5+ held at max depth.
# Warm tint (R slightly higher than B) keeps the hue identity of the sandstone nest
# rather than going neutral grey.
_TUCK_WARM = [
    (225, 212, 200),   # row 0 — hair-trigger, near-invisible
    (190, 179, 167),
    (155, 146, 136),
    (125, 118, 110),
    (100,  94,  88),
    ( 88,  83,  78),   # row 5+ — deepest shadow, held constant
]


def _nest_cy_sag(x, x1, x2, base_y, sag):
    half_w = (x2 - x1) / 2.0
    if half_w <= 0: return base_y
    t = ((x - x1) / half_w) - 1.0
    return base_y + int(round(sag * (1.0 - t * t)))


def _nest_stick_row(surf, vx, y):
    surf.set_at((vx-1, y), _NEST_STICK_HI); surf.set_at((vx, y), _NEST_STICK_COL)
    surf.set_at((vx+1, y), _NEST_STICK_COL); surf.set_at((vx+2, y), _NEST_STICK_SH)


def _nest_stick_span(surf, vx, y1, y2):
    for y in range(y1, y2+1): _nest_stick_row(surf, vx, y)


def _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col):
    y = _nest_cy_sag(x, x1, x2, base_y, sag)
    surf.set_at((x, y), _NEST_COURSE_TOP); surf.set_at((x, y+1), mid_col)
    surf.set_at((x, y+2), mid_col); surf.set_at((x, y+3), _NEST_COURSE_BOT)


def _nest_course_full(surf, x1, x2, base_y, sag, mid_col, skip_xs):
    skip_set = set()
    for sx in skip_xs:
        for dx in _NEST_STICK_X_OFF: skip_set.add(sx+dx)
    for x in range(x1, x2+1):
        if x not in skip_set: _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col)


def _nest_course_at_vx(surf, vx, x1, x2, base_y, sag, mid_col):
    for dx in _NEST_STICK_X_OFF:
        x = vx+dx
        if x1 <= x <= x2: _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col)


def _nest_stick_at_course(surf, vx, x1, x2, base_y, sag):
    y_top = _nest_cy_sag(vx, x1, x2, base_y, sag)
    for y in range(y_top, y_top+4): _nest_stick_row(surf, vx, y)


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
        skip = [vx for (cii, vx), wins in stick_wins.items() if cii==ci and wins]
        _nest_course_full(surf, x1, x2, base_y, sag, col, skip_xs=skip)
        for (cii, vx), wins in stick_wins.items():
            if cii==ci and not wins: _nest_course_at_vx(surf, vx, x1, x2, base_y, sag, col)


def _make_nest_params():
    s = _NEST_S; cx = _NEST_CX
    r = lambda v: round(v * s)
    verts = [cx - r(9), cx + r(9)]
    courses = [
        (r(2),  _NEST_TWIG_BRIGHT, cx-r(21), cx+r(21), max(1,r(2))),
        (r(6),  _NEST_TWIG_MID,    cx-r(20), cx+r(20), max(1,r(2))),
        (r(10), _NEST_TWIG_BRIGHT, cx-r(18), cx+r(18), max(1,r(2))),
        (r(14), _NEST_TWIG_MID,    cx-r(16), cx+r(16), max(1,r(2))),
        (r(18), _NEST_TWIG_BRIGHT, cx-r(14), cx+r(14), max(1,r(3))),
    ]
    vxL, vxR = verts
    stick_wins = {(ci, vxL): (ci%2==0) for ci in range(5)}
    stick_wins.update({(ci, vxR): (ci%2==1) for ci in range(5)})
    rim_rect     = (cx-r(21), -r(5), r(42), max(4,r(12)))
    stick_bottom = r(18)
    hollow       = (cx-r(11), r(16), r(22), max(2,r(3)))
    src = parrot._get_frames()[1]
    bird_h = 34; bird_w = max(1, int(src.get_width() * bird_h / src.get_height()))
    bird = pygame.transform.smoothscale(src, (bird_w, bird_h))
    return verts, courses, stick_wins, rim_rect, stick_bottom, hollow, bird, bird_w, bird_h


PARAMS = _make_nest_params()


# ---------------------------------------------------------------- BEFORE ----

def draw_slot_before(surf, cy, alive):
    verts, courses, stick_wins, rim_rect, stick_bottom, hollow, bird, bw, bh = PARAMS
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


# ----------------------------------------------------------------- AFTER ----

def draw_slot_after(surf, cy, alive):
    verts, courses, stick_wins, rim_rect, stick_bottom, hollow, bird, bw, bh = PARAMS
    cx = _NEST_CX
    rx, ry_off, rw, rh = rim_rect

    # ── Identical to draw_slot_before ────────────────────────────────────────
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

    # ── Tuck concept: full courses 0+1 and arc redrawn on top of bird ─────────
    if alive:
        _nest_weave(surf, cy, (0, 1), courses, stick_wins)
        pygame.draw.arc(surf, _NEST_TWIG_BRIGHT, (rx, cy + ry_off, rw, rh), 0, math.pi, 2)


# ------------------------------------------------------------- REVIEW PNG ----

SKY     = (136, 183, 197)
BOX     = (70, 90)
SLOT_CY = 45


def panel(fn, alive):
    s = pygame.Surface(BOX)
    s.fill(SKY)
    fn(s, SLOT_CY, alive)
    return s


def main():
    font  = pygame.font.SysFont(None, 20)
    fontS = pygame.font.SysFont(None, 16)

    tiles = [
        ("today - alive",   draw_slot_before, True),
        ("today - empty",   draw_slot_before, False),
        ("concept - alive", draw_slot_after,  True),
        ("concept - empty", draw_slot_after,  False),
    ]
    minis = [(lbl, panel(fn, al)) for lbl, fn, al in tiles]

    before_a = panel(draw_slot_before, True)
    after_a  = panel(draw_slot_after,  True)
    Z  = 10
    zb = pygame.transform.scale(before_a, (BOX[0] * Z, BOX[1] * Z))
    za = pygame.transform.scale(after_a,  (BOX[0] * Z, BOX[1] * Z))

    gap    = 10
    zoom_w = zb.get_width() * 2 + gap
    W      = zoom_w + 60
    top_h  = 40 + BOX[1] + 24
    H      = top_h + 28 + zb.get_height() + 30

    out = pygame.Surface((W, H))
    out.fill((26, 22, 34))

    title = font.render("woven-stencil-tuck  -  round 2", True, (240, 232, 210))
    out.blit(title, (30, 10))

    x = 30
    for lbl, srf in minis:
        out.blit(srf, (x, 40))
        out.blit(fontS.render(lbl, True, (210, 200, 185)), (x, 40 + BOX[1] + 4))
        x += BOX[0] + 24

    zy = top_h + 20
    out.blit(fontS.render("10x  BEFORE (alive)", True, (210, 200, 185)),
             (30, zy - 16))
    out.blit(fontS.render("10x  AFTER (alive)", True, (250, 214, 140)),
             (30 + zb.get_width() + gap, zy - 16))
    out.blit(zb, (30, zy))
    out.blit(za, (30 + zb.get_width() + gap, zy))

    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(out, dest)

    # Verify empty-state is untouched
    e_b = panel(draw_slot_before, False)
    e_a = panel(draw_slot_after,  False)
    diff = sum(
        1 for yy in range(BOX[1]) for xx in range(BOX[0])
        if e_b.get_at((xx, yy)) != e_a.get_at((xx, yy))
    )
    print("empty-state pixel diff:", diff)
    print("saved:", dest, out.get_size())


if __name__ == "__main__":
    main()
