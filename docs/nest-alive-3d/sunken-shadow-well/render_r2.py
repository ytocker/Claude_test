"""Round-2 render for `sunken-shadow-well`.

Fixes applied from art-director round-1 critique:
  1. alpha threshold raised to >= 160  (kills dirty notch + floating warm specks)
  2. ramp retargeted to the visible bird band  (TOP=-6, FULL=+5, BOT=+10)
  3. warm tinted multiply replaces neutral grey  (R:255→200 G:236→160 B:214→120)
     with a luma-30 floor so the darkest bird pixels never go muddy
  4. front lip at (205,155,90) luma-156, 2-px centre / 1-px ends, plus a 1-px
     contact-shadow line immediately under where the lip crosses bird pixels
  5. AO arc moved to 0→π (far wall) for lit-rim / dark-far-wall / lit-head stack
  6. third sheet row: night sky (35,55,115) 10× BEFORE/AFTER to verify depth survives
"""
import os, sys, math
os.environ.setdefault('SDL_VIDEODRIVER', 'offscreen')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, '/home/user/skybit')
import pygame
pygame.init()
import game.parrot as parrot

# ── Palette + geometry (matches shipped HUD) ─────────────────────────────────

_NEST_S            = 0.80
_NEST_CX           = 31
_NEST_CY           = 73
_NEST_TWIG_BRIGHT  = (160, 110, 55)
_NEST_TWIG_MID     = (110, 75, 35)
_NEST_TWIG_DARK    = (70, 45, 18)
_NEST_STICK_COL    = (130, 90, 42)
_NEST_STICK_HI     = (170, 120, 60)
_NEST_STICK_SH     = (80, 55, 22)
_NEST_COURSE_TOP   = (180, 130, 65)
_NEST_COURSE_BOT   = (80, 55, 22)
_NEST_HOLLOW_COL   = (50, 35, 14)
_NEST_STICK_X_OFF  = (-1, 0, 1, 2)

SKY       = (136, 183, 197)
SKY_NIGHT = (35, 55, 115)


# ── Shared nest weave (identical to the shipped HUD) ─────────────────────────

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
        for dx in _NEST_STICK_X_OFF:
            skip_set.add(sx + dx)
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
    rim_rect    = (cx-r(21), -r(5), r(42), max(4, r(12)))
    stick_bottom = r(18)
    hollow      = (cx-r(11), r(16), r(22), max(2, r(3)))
    src    = parrot._get_frames()[1]
    bird_h = 34
    bird_w = max(1, int(src.get_width() * bird_h / src.get_height()))
    bird   = pygame.transform.smoothscale(src, (bird_w, bird_h))
    return (verts, courses, stick_wins, rim_rect, stick_bottom, hollow,
            bird, bird_w, bird_h)


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


# ── AFTER: sunken-shadow-well  (round 2) ─────────────────────────────────────

# Ramp retargeted so the falloff covers the bird's visible band only.
_WELL_TOP_DY  = -6   # shoulder line — still fully lit here
_WELL_FULL_DY = +5   # 2/3 down the visible bird — floor reached here
_WELL_BOT_DY  = +10  # hold from here down

_LIP_COL  = (205, 155, 90)   # luma ~156 — brighter than COURSE_TOP luma ~138
_WELL_CACHE = None


def _blend_px(surf, x, y, col, alpha):
    base = surf.get_at((x, y))
    t = alpha / 255.0
    surf.set_at((x, y), (
        int(round(base[0] + (col[0] - base[0]) * t)),
        int(round(base[1] + (col[1] - base[1]) * t)),
        int(round(base[2] + (col[2] - base[2]) * t)),
        base[3],
    ))


def _well_gradient(bird, bw, bh, by, cy):
    """Warm tinted multiply surface, pre-masked to opaque bird pixels.

    Masking to alpha >= 160 rather than > 0 prevents near-transparent fringe
    pixels from producing the warm-speck artefacts seen in round 1.  The warm
    channel targets (R:255→200 G:236→160 B:214→120) attenuate toward a warm
    dark rather than neutral grey, so the hue of each feather is preserved
    while the value drops convincingly.  A per-pixel luma-30 floor prevents
    any already-dark feather detail from going to mud.
    """
    global _WELL_CACHE
    if _WELL_CACHE is not None:
        return _WELL_CACHE
    top  = cy + _WELL_TOP_DY
    bot  = cy + _WELL_BOT_DY
    span = float(_WELL_FULL_DY - _WELL_TOP_DY)   # 11 px
    g    = pygame.Surface((36, bot - top + 1), pygame.SRCALPHA)
    g.fill((255, 255, 255, 255))   # identity multiply by default
    gx0  = _NEST_CX - 18
    for row in range(g.get_height()):
        y = top + row
        t = min(1.0, max(0.0, (y - top) / span))
        # Warm darkening ramp — attenuate toward warm dark, preserve hue
        dark_r = 255 - int(t * (255 - 200))   # 255 → 200
        dark_g = 236 - int(t * (236 - 160))   # 236 → 160
        dark_b = 214 - int(t * (214 - 120))   # 214 → 120  (warm, not grey)
        for gx in range(36):
            sx = gx0 + gx - (_NEST_CX - bw // 2)
            sy = y - by
            if 0 <= sx < bw and 0 <= sy < bh and bird.get_at((sx, sy)).a >= 160:
                bp = bird.get_at((sx, sy))
                # Luma floor: clamp multiply so no bird pixel drops below luma 30
                r2 = bp[0] * dark_r // 255
                g2 = bp[1] * dark_g // 255
                b2 = bp[2] * dark_b // 255
                luma2 = int(0.299 * r2 + 0.587 * g2 + 0.114 * b2)
                if luma2 < 30 and t > 0:
                    boost  = 30.0 / max(1, luma2)
                    dark_r = min(255, int(dark_r * boost))
                    dark_g = min(255, int(dark_g * boost))
                    dark_b = min(255, int(dark_b * boost))
                g.set_at((gx, row), (dark_r, dark_g, dark_b, 255))
    _WELL_CACHE = (g, gx0, top)
    return _WELL_CACHE


def _draw_lip(surf, bird, bw, bh, bx, by, rim_abs):
    """Front lip with variable thickness and a contact-shadow line.

    Two pixels wide at the horizontal centre (cx±6) where the bowl face is
    fullest, tapering to one pixel at the ends.  The thin dark line immediately
    below — drawn only where the lip overlaps a bird pixel — is the highest
    value-per-pixel cue that the rim sits in front of the occupant.
    """
    rx, ry, rw, rh = rim_abs
    ecx  = rx + rw / 2.0
    ecy  = ry + rh / 2.0
    ea   = rw / 2.0
    eb   = rh / 2.0
    cx6l = _NEST_CX - 6
    cx6r = _NEST_CX + 6

    for x in range(rx, rx + rw + 1):
        dx = x - ecx
        if abs(dx) > ea:
            continue
        frac  = math.sqrt(max(0.0, 1.0 - (dx / ea) ** 2))
        y_bot = int(round(ecy + eb * frac))   # lower half of the ellipse
        is_centre = (cx6l <= x <= cx6r)

        # Draw the lip
        surf.set_at((x, y_bot), _LIP_COL)
        if is_centre and y_bot - 1 >= 0:
            surf.set_at((x, y_bot - 1), _LIP_COL)

        # Contact shadow: dark line under the lip where it crosses bird pixels
        y_under = y_bot + 1
        sx = x - bx
        sy = y_under - by
        if 0 <= sx < bw and 0 <= sy < bh and bird.get_at((sx, sy)).a >= 160:
            _blend_px(surf, x, y_under, _NEST_TWIG_DARK, 90)


def draw_slot_after(surf, cy, alive):
    verts, courses, stick_wins, rim_rect, stick_bottom, hollow, bird, bw, bh = P
    cx = _NEST_CX
    rx, ry_off, rw, rh = rim_rect
    rim_abs = (rx, cy + ry_off, rw, rh)
    bx, by  = cx - bw // 2, cy - bh // 2 + 5

    pygame.draw.ellipse(surf, (0, 0, 0), rim_abs)
    pygame.draw.arc(surf, _NEST_TWIG_BRIGHT, rim_abs, 0, math.pi, 2)
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

        # Warm luminance ramp: the bowl swallows the light from the shoulder
        # down.  The gradient surface was pre-masked to bird silhouette only.
        g, gx0, gtop = _well_gradient(bird, bw, bh, by, cy)
        surf.blit(g, (gx0, gtop), special_flags=pygame.BLEND_RGBA_MULT)

        # AO on the far wall (0→π) darkens the back of the bowl so the reader
        # gets the three-value bowl stack: lit rim → dark far wall → lit head.
        ao = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.arc(ao, (*_NEST_TWIG_DARK, 90),
                        (rx + 1, cy + ry_off + 1, rw - 2, rh - 2),
                        0, math.pi, 1)
        surf.blit(ao, (0, 0))

        # Warm bounce off the far wall catches the topmost lit shoulder edge so
        # the occupant separates from the black hollow without an occluder.
        for x in range(bx, bx + bw):
            for y in range(cy - 3, cy):
                sx, sy = x - bx, y - by
                if 0 <= sx < bw and 0 <= sy < bh and bird.get_at((sx, sy)).a >= 160:
                    _blend_px(surf, x, y, _NEST_TWIG_BRIGHT, 90)
                    break

        # Front lip — own value identity, variable width, contact shadow
        _draw_lip(surf, bird, bw, bh, bx, by, rim_abs)
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


# ── Sheet composition ─────────────────────────────────────────────────────────

PANEL_W  = 70
PANEL_H  = 100
CROP     = pygame.Rect(0, 6, 70, 90)
ZOOM_SRC = pygame.Rect(8, 64, 46, 34)
ZOOM     = 10


def render_panel(fn, alive, bg=SKY):
    s = pygame.Surface((PANEL_W, PANEL_H))
    s.fill(bg)
    fn(s, _NEST_CY, alive)
    return s


def diff_count(a, b):
    n = 0
    for y in range(a.get_height()):
        for x in range(a.get_width()):
            if a.get_at((x, y)) != b.get_at((x, y)):
                n += 1
    return n


def zoomed(panel, bg=SKY):
    """Return a 10× zoom of the bird zone on the requested sky background."""
    sub = panel.subsurface(ZOOM_SRC).copy()
    return pygame.transform.scale(sub, (ZOOM_SRC.w * ZOOM, ZOOM_SRC.h * ZOOM))


def main():
    font  = pygame.font.SysFont('dejavusans', 14, bold=True)
    small = pygame.font.SysFont('dejavusans', 12)

    # Day panels
    p_before_a  = render_panel(draw_slot_before, True)
    p_before_e  = render_panel(draw_slot_before, False)
    p_after_a   = render_panel(draw_slot_after,  True)
    p_after_e   = render_panel(draw_slot_after,  False)

    empty_diff  = diff_count(p_before_e, p_after_e)
    alive_diff  = diff_count(p_before_a, p_after_a)
    print(f"empty-state pixel diff: {empty_diff}")
    print(f"alive-state pixel diff: {alive_diff}")
    if empty_diff:
        rows = sorted({y for y in range(PANEL_H) for x in range(PANEL_W)
                       if p_before_e.get_at((x, y)) != p_after_e.get_at((x, y))})
        print(f"empty-diff rows: {rows}")

    # Night panels — same drawing code, different background
    global _WELL_CACHE
    _WELL_CACHE = None   # reset so night render re-evaluates (same result, fresh surface)
    p_before_a_n = render_panel(draw_slot_before, True,  bg=SKY_NIGHT)
    _WELL_CACHE  = None
    p_after_a_n  = render_panel(draw_slot_after,  True,  bg=SKY_NIGHT)

    # 10× zooms
    zb_day   = zoomed(p_before_a)
    za_day   = zoomed(p_after_a)
    zb_night = zoomed(p_before_a_n)
    za_night = zoomed(p_after_a_n)
    zw, zh   = zb_day.get_size()

    margin, gap = 20, 10
    top_w = 4 * PANEL_W + 3 * gap          # 310
    bot_w = 2 * zw + gap                   # 930
    W     = max(top_w, bot_w) + 2 * margin

    y_title     = margin
    y_top_lbl   = y_title    + 24
    y_top       = y_top_lbl  + 16
    y_day_lbl   = y_top      + CROP.h + 26
    y_day       = y_day_lbl  + 16
    y_night_lbl = y_day      + zh + 20
    y_night     = y_night_lbl + 16
    H           = y_night    + zh + margin

    sheet = pygame.Surface((W, H))
    sheet.fill((28, 30, 34))
    sheet.blit(font.render("sunken-shadow-well  -  round 2", True, (240, 235, 225)),
               (margin, y_title))

    # Row 1: 1× native, four panels on day sky
    labels = ["today / alive", "today / empty", "concept / alive", "concept / empty"]
    panels = [p_before_a, p_before_e, p_after_a, p_after_e]
    x0 = (W - top_w) // 2
    for i, (p, lbl) in enumerate(zip(panels, labels)):
        x = x0 + i * (PANEL_W + gap)
        sheet.blit(small.render(lbl, True, (185, 190, 200)), (x, y_top_lbl))
        sheet.blit(p, (x, y_top), CROP)

    # Row 2: 10× zoom, day sky
    x1 = (W - bot_w) // 2
    sheet.blit(small.render("BEFORE  alive  10×  (day)", True, (185, 190, 200)),
               (x1, y_day_lbl))
    sheet.blit(small.render("AFTER  alive  10×  (day)", True, (255, 214, 120)),
               (x1 + zw + gap, y_day_lbl))
    sheet.blit(zb_day, (x1, y_day))
    sheet.blit(za_day, (x1 + zw + gap, y_day))

    # Row 3: 10× zoom, night sky — verifies depth read survives the dark background
    sheet.blit(small.render("BEFORE  alive  10×  (night)", True, (130, 165, 230)),
               (x1, y_night_lbl))
    sheet.blit(small.render("AFTER  alive  10×  (night)", True, (255, 214, 120)),
               (x1 + zw + gap, y_night_lbl))
    sheet.blit(zb_night, (x1, y_night))
    sheet.blit(za_night, (x1 + zw + gap, y_night))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'round_2.png')
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == '__main__':
    main()
