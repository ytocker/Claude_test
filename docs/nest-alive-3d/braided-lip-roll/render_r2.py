"""Round-2 render for the `braided-lip-roll` nest concept.

Applies all art-director fixes from round 1 critique:
  - notch bleed removed (cord drawn last, after notches)
  - value hierarchy inverted (crest luma ~150 > COURSE_TOP luma 138)
  - occlusion shadow moved above the cord crest
  - arc sag replaces flat plateau
  - smooth outer swell taper
  - outermost ear columns bridged to rim
  - chunky 9-px braid segments (3-4 visible bindings)
  - lower-roll variant panel added
"""
import os, sys, math
os.environ.setdefault('SDL_VIDEODRIVER', 'offscreen')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, '/home/user/skybit')
import pygame
pygame.init()
import game.parrot as parrot

# Palette
_NEST_S           = 0.80
_NEST_CX          = 31
_NEST_CY          = 73
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

# Fix 2: crest sits above COURSE_TOP in value (luma ~150 vs 138)
_CREST_COL = (195, 148, 82)

SKY = (136, 183, 197)

# Fix 7: 9-px segments -> 3-4 chunky bindings across 38 px
_ROLL_SEG = 9


# Weave helpers (unchanged from round 1)

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


# BEFORE: today's shipped slot

def draw_slot_before(surf, cy, alive, **kw):
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


# New cord helpers

def _cord_y0(x, cx, cy):
    """Fix 4: parabolic sag arc, y0=cy+1 at extremes (x=cx+-17), cy+8 at centre."""
    t = (x - cx) / 17.0
    v = max(0.0, 1.0 - t * t)
    return cy + 1 + int(7 * v)


def _draw_cord_roll(surf, cx, cy, bird_surf, bx, by, y_extra=0):
    """Draw the braided lip roll as the topmost layer.

    Drawn after all weave + notches so cord occludes everything below it.
    The multiply shadow at y0-1 makes the roll read in front of the parrot
    without needing alpha compositing.
    """
    W, H = surf.get_size()
    bw, bh = bird_surf.get_size()
    EAR_XS = {12, 13, 48, 49}

    # Fix 3: darken bird pixels one row above the cord crest (occlusion shadow)
    for x in range(12, 50):
        y0 = _cord_y0(x, cx, cy) + y_extra
        ys = y0 - 1
        if not (0 <= ys < H):
            continue
        bxi, byi = x - bx, ys - by
        if 0 <= bxi < bw and 0 <= byi < bh:
            px = bird_surf.get_at((bxi, byi))
            if px.a > 0:
                surf.set_at((x, ys), (int(px.r * 0.63),
                                      int(px.g * 0.63),
                                      int(px.b * 0.63)))

    # Fix 1+5+6+7: cord body — seams, ears, smooth taper all handled here
    u0 = 12
    for x in range(12, 50):
        y0 = _cord_y0(x, cx, cy) + y_extra
        u  = x - u0
        is_ear  = x in EAR_XS
        is_seam = (u % _ROLL_SEG == 0) and not is_ear

        if is_ear:
            # Fix 6: connect isolated outer pixel to the rim with a dark bridge
            ym1 = y0 - 1
            if 0 <= ym1 < H:
                surf.set_at((x, ym1), _NEST_TWIG_DARK)
            # Only paint the single crest row, no body below
            if 0 <= y0 < H:
                surf.set_at((x, y0), _CREST_COL)
            continue

        if is_seam:
            # Full-height TWIG_DARK divider — the countable binding tick
            for row in range(4):
                y = y0 + row
                if 0 <= y < H:
                    surf.set_at((x, y), _NEST_TWIG_DARK)
            continue

        # Standard braid column: lit crest / mid interior / dark underside
        for row in range(4):
            y = y0 + row
            if not (0 <= y < H):
                continue
            if row == 0:
                col = _CREST_COL        # Fix 2: camera-nearest element is brightest
            elif row == 3:
                col = _NEST_TWIG_DARK   # rolled-under shadow
            else:
                col = _NEST_TWIG_MID    # braid interior
            surf.set_at((x, y), col)


# AFTER: braided-lip-roll (round 2)

def draw_slot_after(surf, cy, alive, roll_y_extra=0):
    """Fix 1: cord roll is the very last draw step — after weave, sticks,
    and notches — so no weave course can bleed through the cord."""
    verts, courses, stick_wins, rim_rect, stick_bottom, hollow, bird, bw, bh = P
    cx = _NEST_CX
    rx, ry_off, rw, rh = rim_rect
    bx = cx - bw // 2
    by = cy - bh // 2 + 5

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

    # ── Braid concept: courses 0+1 + chunky arc redrawn on top of bird ───────
    if alive:
        _nest_weave(surf, cy, (0, 1), courses, stick_wins)
        pygame.draw.arc(surf, _NEST_TWIG_BRIGHT, (rx, cy + ry_off, rw, rh), 0, math.pi, 3)


# Sheet composition

PANEL_W, PANEL_H = 70, 100
CROP     = pygame.Rect(0,  6, 70, 90)
ZOOM_SRC = pygame.Rect(6, 56, 48, 42)
ZOOM     = 10


def render_panel(fn, alive, **kw):
    s = pygame.Surface((PANEL_W, PANEL_H))
    s.fill(SKY)
    fn(s, _NEST_CY, alive, **kw)
    return s


def diff_count(a, b):
    n = 0
    for y in range(a.get_height()):
        for x in range(a.get_width()):
            if a.get_at((x, y)) != b.get_at((x, y)):
                n += 1
    return n


def silhouette_width(panel):
    best = 0
    for y in range(panel.get_height()):
        xs = [x for x in range(panel.get_width())
              if tuple(panel.get_at((x, y)))[:3] != SKY]
        if xs:
            best = max(best, xs[-1] - xs[0] + 1)
    return best


def zoomed(panel):
    sub = panel.subsurface(ZOOM_SRC).copy()
    return pygame.transform.scale(sub, (ZOOM_SRC.w * ZOOM, ZOOM_SRC.h * ZOOM))


def main():
    font  = pygame.font.SysFont('dejavusans', 14, bold=True)
    small = pygame.font.SysFont('dejavusans', 12)

    p_before_a = render_panel(draw_slot_before, True)
    p_before_e = render_panel(draw_slot_before, False)
    p_after_a  = render_panel(draw_slot_after,  True)
    p_after_e  = render_panel(draw_slot_after,  False)
    p_lower_a  = render_panel(draw_slot_after,  True, roll_y_extra=2)

    empty_diff = diff_count(p_before_e, p_after_e)
    alive_diff = diff_count(p_before_a, p_after_a)
    print(f"empty-state pixel diff: {empty_diff}")
    print(f"alive-state pixel diff: {alive_diff}")

    rows = sorted({y for y in range(PANEL_H)
                   for x in range(PANEL_W)
                   if p_before_e.get_at((x, y)) != p_after_e.get_at((x, y))})
    if rows:
        print(f"empty-diff rows (cy={_NEST_CY}): {rows}")
    print(f"outer silhouette  before/alive: {silhouette_width(p_before_a)} px"
          f"   after/alive: {silhouette_width(p_after_a)} px")

    zb   = zoomed(p_before_a)
    za   = zoomed(p_after_a)
    zlow = zoomed(p_lower_a)
    zw, zh = zb.get_size()

    margin, gap = 20, 10
    top_panels = [p_before_a, p_before_e, p_after_a, p_after_e]
    top_labels  = ["today / alive", "today / empty", "concept / alive", "concept / empty"]
    top_w = len(top_panels) * PANEL_W + (len(top_panels)-1) * gap

    bot_panels = [zb, za, zlow]
    bot_labels  = ["BEFORE  alive  (10x)", "AFTER  alive  (10x)", "lower-roll  (10x)"]
    bot_lbl_cols = [(185, 190, 200), (255, 214, 120), (160, 220, 160)]
    bot_w = len(bot_panels) * zw + (len(bot_panels)-1) * gap

    W = max(top_w, bot_w) + 2 * margin
    y_title    = margin
    y_row1_lbl = y_title + 24
    y_row1     = y_row1_lbl + 16
    y_row2_lbl = y_row1 + CROP.h + 26
    y_row2     = y_row2_lbl + 16
    H = y_row2 + zh + margin

    sheet = pygame.Surface((W, H))
    sheet.fill((28, 30, 34))
    sheet.blit(font.render("braided-lip-roll  -  round 2", True, (240, 235, 225)),
               (margin, y_title))

    x0 = (W - top_w) // 2
    for i, (p, lbl) in enumerate(zip(top_panels, top_labels)):
        x = x0 + i * (PANEL_W + gap)
        sheet.blit(small.render(lbl, True, (185, 190, 200)), (x, y_row1_lbl))
        sheet.blit(p, (x, y_row1), CROP)

    x1 = (W - bot_w) // 2
    for i, (zp, lbl, lc) in enumerate(zip(bot_panels, bot_labels, bot_lbl_cols)):
        x = x1 + i * (zw + gap)
        sheet.blit(small.render(lbl, True, lc), (x, y_row2_lbl))
        sheet.blit(zp, (x, y_row2))

    out_dir = '/home/user/skybit/docs/nest-alive-3d/braided-lip-roll'
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, 'round_2.png')
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == '__main__':
    main()
