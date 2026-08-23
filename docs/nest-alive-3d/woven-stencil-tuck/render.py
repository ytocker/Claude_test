"""woven-stencil-tuck — round 1 exploration render.

Standalone: mirrors game/hud.py's nest slot drawing so the concept can be
judged against today's art without touching the live HUD.
"""

import os, sys, math
os.environ.setdefault('SDL_VIDEODRIVER', 'offscreen')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, '/home/user/skybit')
import pygame
pygame.init()
import game.parrot as parrot

_NEST_S          = 0.80
_NEST_CX         = 31
_NEST_CY         = 73
_NEST_TWIG_BRIGHT  = (160, 110, 55)
_NEST_TWIG_MID     = (110, 75, 35)
_NEST_TWIG_DARK    = (70, 45, 18)
_NEST_STICK_COL    = (130, 90, 42)
_NEST_STICK_HI     = (170, 120, 60)
_NEST_STICK_SH     = (80,  55, 22)
_NEST_COURSE_TOP   = (180, 130, 65)
_NEST_COURSE_BOT   = (80,  55, 22)
_NEST_HOLLOW_COL   = (50,  35, 14)
_NEST_STICK_X_OFF  = (-1, 0, 1, 2)


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
                        surf.set_at((x, y_cross+1), _NEST_TWIG_DARK); surf.set_at((x, y_cross+2), _NEST_TWIG_DARK)
            else:
                for dy in (-1, 4):
                    surf.set_at((vx, y_cross+dy), _NEST_TWIG_DARK); surf.set_at((vx+1, y_cross+dy), _NEST_TWIG_DARK)


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

_TUCK_RAMP = None


def _tuck_ramp(w, h, blit_dy):
    """Vertical alpha ramp that dissolves the bird's belly into the bowl.

    Cached because it only depends on the fixed mini-Pip geometry; a hard
    elliptical clip would shear the head and shoulders, which is exactly the
    silhouette this concept wants to keep overhanging the rim.
    """
    global _TUCK_RAMP
    if _TUCK_RAMP is not None:
        return _TUCK_RAMP
    strip = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        dy = y + blit_dy          # offset of this row from the slot's cy
        if dy <= 1:
            a = 255
        elif dy >= 6:
            a = 0
        elif dy == 2:
            a = 153
        else:
            a = int(round(153 * (6 - dy) / 4.0))
        pygame.draw.line(strip, (255, 255, 255, a), (0, y), (w - 1, y))
    _TUCK_RAMP = strip
    return strip


def draw_slot_after(surf, cy, alive):
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
        bx, by = cx - bw // 2, cy - bh // 2 + 5
        faded = pygame.Surface((bw, bh), pygame.SRCALPHA)
        faded.blit(bird, (0, 0))
        faded.blit(_tuck_ramp(bw, bh, by - cy), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(faded, (bx, by))

        # Warm occlusion inside the front lip reads as depth; a grey shadow
        # here would fight the sandstone-warm palette of the whole HUD.
        ao = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.arc(ao, (*_NEST_TWIG_DARK, 110),
                        (rx + 1, cy + ry_off + 1, rw - 2, rh - 2),
                        math.pi, 2 * math.pi, 2)
        surf.blit(ao, (0, 0))

        pygame.draw.arc(surf, _NEST_TWIG_BRIGHT, (rx, cy + ry_off, rw, rh),
                        math.pi, 2 * math.pi, 3)
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


# ------------------------------------------------------------- REVIEW PNG ----

SKY  = (136, 183, 197)
BOX  = (70, 90)
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
    Z = 10
    zb = pygame.transform.scale(before_a, (BOX[0] * Z, BOX[1] * Z))
    za = pygame.transform.scale(after_a,  (BOX[0] * Z, BOX[1] * Z))

    gap  = 10
    zoom_w = zb.get_width() * 2 + gap
    W = zoom_w + 60
    top_h = 40 + BOX[1] + 24
    H = top_h + 28 + zb.get_height() + 30

    out = pygame.Surface((W, H))
    out.fill((26, 22, 34))

    title = font.render("woven-stencil-tuck  -  round 1", True, (240, 232, 210))
    out.blit(title, (30, 10))

    x = 30
    for lbl, srf in minis:
        out.blit(srf, (x, 40))
        out.blit(fontS.render(lbl, True, (210, 200, 185)), (x, 40 + BOX[1] + 4))
        x += BOX[0] + 24

    zy = top_h + 20
    out.blit(fontS.render("10x  BEFORE (alive)", True, (210, 200, 185)), (30, zy - 16))
    out.blit(fontS.render("10x  AFTER (alive)", True, (250, 214, 140)),
             (30 + zb.get_width() + gap, zy - 16))
    out.blit(zb, (30, zy))
    out.blit(za, (30 + zb.get_width() + gap, zy))

    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(out, dest)

    e_b = panel(draw_slot_before, False)
    e_a = panel(draw_slot_after,  False)
    diff = sum(1 for yy in range(BOX[1]) for xx in range(BOX[0])
               if e_b.get_at((xx, yy)) != e_a.get_at((xx, yy)))
    print("empty-state pixel diff:", diff)
    print("saved:", dest, out.get_size())


if __name__ == "__main__":
    main()
