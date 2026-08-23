"""Exploration render for the `split-shell-rim` nest concept.

Standalone review-sheet generator: it duplicates the shipped nest drawing
code so the exploration can diverge from `game/hud.py` without touching the
live HUD until a direction is chosen.
"""
import os, sys, math
os.environ.setdefault('SDL_VIDEODRIVER', 'offscreen')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, '/home/user/skybit')
import pygame
pygame.init()
import game.parrot as parrot

# Constants
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

SKY = (136, 183, 197)


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
    for y in range(y1, y2+1):
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
        for dx in _NEST_STICK_X_OFF:
            skip_set.add(sx+dx)
    for x in range(x1, x2+1):
        if x not in skip_set:
            _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col)

def _nest_course_at_vx(surf, vx, x1, x2, base_y, sag, mid_col):
    for dx in _NEST_STICK_X_OFF:
        x = vx+dx
        if x1 <= x <= x2:
            _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col)

def _nest_stick_at_course(surf, vx, x1, x2, base_y, sag):
    y_top = _nest_cy_sag(vx, x1, x2, base_y, sag)
    for y in range(y_top, y_top+4):
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
        skip = [vx for (cii, vx), wins in stick_wins.items() if cii==ci and wins]
        _nest_course_full(surf, x1, x2, base_y, sag, col, skip_xs=skip)
        for (cii, vx), wins in stick_wins.items():
            if cii==ci and not wins:
                _nest_course_at_vx(surf, vx, x1, x2, base_y, sag, col)

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
    bird_h = 34
    bird_w = max(1, int(src.get_width() * bird_h / src.get_height()))
    bird = pygame.transform.smoothscale(src, (bird_w, bird_h))
    return verts, courses, stick_wins, rim_rect, stick_bottom, hollow, bird, bird_w, bird_h


P = _make_nest_params()


# ── BEFORE: today's shipped slot ─────────────────────────────────────────────

def draw_slot_before(surf, cy, alive):
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


# ── AFTER: split-shell-rim ───────────────────────────────────────────────────

_SPLIT_X = 13   # columns nearer than this read as the near wall of the vessel


def _nest_course_split(surf, x1, x2, base_y, sag, mid_col, skip_xs, outer):
    """Half of one woven course: `outer` picks the far shoulders vs the near span.

    Splitting the same course by x lets the shoulders sit behind the bird while
    the near span crosses in front of it, which is what sells the thickness.
    """
    skip_set = set()
    for sx in skip_xs:
        for dx in _NEST_STICK_X_OFF:
            skip_set.add(sx+dx)
    for x in range(x1, x2+1):
        if x in skip_set:
            continue
        if (abs(x - _NEST_CX) > _SPLIT_X) == outer:
            _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col)


def _nest_weave_split(surf, cy, ci_range, courses, stick_wins, outer):
    for ci in ci_range:
        offset, col, x1, x2, sag = courses[ci]
        base_y = cy + offset
        skip = [vx for (cii, vx), wins in stick_wins.items() if cii==ci and wins]
        _nest_course_split(surf, x1, x2, base_y, sag, col, skip, outer)
        if not outer:
            for (cii, vx), wins in stick_wins.items():
                if cii==ci and not wins:
                    _nest_course_at_vx(surf, vx, x1, x2, base_y, sag, col)


def _lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _front_arc_pixels(rim_rect, cy):
    """Bottom half of the rim ellipse as (x, y) columns, outermost row first."""
    rx, ry_off, rw, rh = rim_rect
    ecx = rx + (rw - 1) / 2.0
    ecy = cy + ry_off + (rh - 1) / 2.0
    a = (rw - 1) / 2.0
    b = (rh - 1) / 2.0
    out = []
    for x in range(rx, rx + rw):
        t = (x - ecx) / a
        if abs(t) > 1.0:
            continue
        y = ecy + b * math.sqrt(max(0.0, 1.0 - t * t))
        out.append((x, int(round(y)), min(1.0, abs(t))))
    return out


def draw_slot_after(surf, cy, alive):
    verts, courses, stick_wins, rim_rect, stick_bottom, hollow, bird, bw, bh = P
    cx = _NEST_CX
    rx, ry_off, rw, rh = rim_rect
    bx, by = cx - bw // 2, cy - bh // 2 + 5

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
        surf.blit(bird, (bx, by))
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

    # ── Split concept: near-side courses + arc redrawn on top of bird ────────
    if alive:
        _nest_weave_split(surf, cy, (0, 1), courses, stick_wins, outer=False)
        pygame.draw.arc(surf, _NEST_TWIG_BRIGHT, (rx, cy + ry_off, rw, rh), 0, math.pi, 2)


# ── Sheet composition ────────────────────────────────────────────────────────

PANEL_W, PANEL_H = 70, 100
CROP = pygame.Rect(0, 6, 70, 90)
ZOOM_SRC = pygame.Rect(8, 64, 46, 34)
ZOOM = 10


def render_panel(fn, alive):
    s = pygame.Surface((PANEL_W, PANEL_H))
    s.fill(SKY)
    fn(s, _NEST_CY, alive)
    return s


def diff_count(a, b):
    n = 0
    for y in range(a.get_height()):
        for x in range(a.get_width()):
            if a.get_at((x, y)) != b.get_at((x, y)):
                n += 1
    return n


def zoomed(panel):
    sub = panel.subsurface(ZOOM_SRC).copy()
    return pygame.transform.scale(sub, (ZOOM_SRC.w * ZOOM, ZOOM_SRC.h * ZOOM))


def main():
    font = pygame.font.SysFont('dejavusans', 14, bold=True)
    small = pygame.font.SysFont('dejavusans', 12)

    p_before_a = render_panel(draw_slot_before, True)
    p_before_e = render_panel(draw_slot_before, False)
    p_after_a  = render_panel(draw_slot_after,  True)
    p_after_e  = render_panel(draw_slot_after,  False)

    empty_diff = diff_count(p_before_e, p_after_e)
    alive_diff = diff_count(p_before_a, p_after_a)
    rows = sorted({y for y in range(PANEL_H)
                   for x in range(PANEL_W)
                   if p_before_e.get_at((x, y)) != p_after_e.get_at((x, y))})
    print(f"empty-state pixel diff: {empty_diff}")
    print(f"alive-state pixel diff: {alive_diff}")
    if rows:
        print(f"empty-diff rows (cy={_NEST_CY}): {rows} "
              f"-> cy{rows[0]-_NEST_CY:+d} .. cy{rows[-1]-_NEST_CY:+d}")

    zb, za = zoomed(p_before_a), zoomed(p_after_a)
    zw, zh = zb.get_size()

    margin, gap = 20, 10
    top_w = 4 * PANEL_W + 3 * gap
    bot_w = 2 * zw + gap
    W = max(top_w, bot_w) + 2 * margin
    y_title = margin
    y_top_lbl = y_title + 24
    y_top = y_top_lbl + 16
    y_bot_lbl = y_top + CROP.h + 26
    y_bot = y_bot_lbl + 16
    H = y_bot + zh + margin

    sheet = pygame.Surface((W, H))
    sheet.fill((28, 30, 34))
    sheet.blit(font.render("split-shell-rim  -  round 1", True, (240, 235, 225)),
               (margin, y_title))

    labels = ["today / alive", "today / empty", "concept / alive", "concept / empty"]
    x0 = (W - top_w) // 2
    for i, (p, lbl) in enumerate(zip([p_before_a, p_before_e, p_after_a, p_after_e], labels)):
        x = x0 + i * (PANEL_W + gap)
        sheet.blit(small.render(lbl, True, (185, 190, 200)), (x, y_top_lbl))
        sheet.blit(p, (x, y_top), CROP)

    x1 = (W - bot_w) // 2
    sheet.blit(small.render("BEFORE  alive  (10x)", True, (185, 190, 200)), (x1, y_bot_lbl))
    sheet.blit(small.render("AFTER  alive  (10x)", True, (255, 214, 120)), (x1 + zw + gap, y_bot_lbl))
    sheet.blit(zb, (x1, y_bot))
    sheet.blit(za, (x1 + zw + gap, y_bot))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'round_1.png')
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == '__main__':
    main()
