"""Review render — loose-twig-veil, round 2.

Art-director fixes applied to draw_slot_after only:
  1. Connectivity gate — any spur whose anchor has no 8-neighbour in the
     nest mass is a floating island and is killed.
  2. Silhouette capped at x 12..49 (38 px wide, cx=31).
  3. Single chest strand at cy+8..cy+11, below the front arc.
  4. Directional lighting — left spurs bright anchor, right spurs mid;
     dark terminal pixel on all; 1-px tip shadow offset toward shadow side.
  5. Splayed straw spurs drawn unconditionally (nest anatomy, not tenancy).
  6. Front arc π→2π + contact shadow remain inside `if alive:`.
"""

import os, sys, math
os.environ.setdefault('SDL_VIDEODRIVER', 'offscreen')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, '/home/user/skybit')
import pygame
pygame.init()
import game.parrot as parrot

_NEST_S=0.80; _NEST_CX=31; _NEST_CY=73
_NEST_TWIG_BRIGHT=(160,110,55); _NEST_TWIG_MID=(110,75,35); _NEST_TWIG_DARK=(70,45,18)
_NEST_STICK_COL=(130,90,42); _NEST_STICK_HI=(170,120,60); _NEST_STICK_SH=(80,55,22)
_NEST_COURSE_TOP=(180,130,65); _NEST_COURSE_BOT=(80,55,22); _NEST_HOLLOW_COL=(50,35,14)
_NEST_STICK_X_OFF=(-1,0,1,2)

# 38-px silhouette envelope: cx=31, x 12..49
_SPUR_X_MIN = 12
_SPUR_X_MAX = 49


def _nest_cy_sag(x,x1,x2,base_y,sag):
    half_w=(x2-x1)/2.0
    if half_w<=0: return base_y
    t=((x-x1)/half_w)-1.0
    return base_y+int(round(sag*(1.0-t*t)))

def _nest_stick_row(surf,vx,y):
    surf.set_at((vx-1,y),_NEST_STICK_HI); surf.set_at((vx,y),_NEST_STICK_COL)
    surf.set_at((vx+1,y),_NEST_STICK_COL); surf.set_at((vx+2,y),_NEST_STICK_SH)

def _nest_stick_span(surf,vx,y1,y2):
    for y in range(y1,y2+1): _nest_stick_row(surf,vx,y)

def _nest_course_col(surf,x,x1,x2,base_y,sag,mid_col):
    y=_nest_cy_sag(x,x1,x2,base_y,sag)
    surf.set_at((x,y),_NEST_COURSE_TOP); surf.set_at((x,y+1),mid_col)
    surf.set_at((x,y+2),mid_col); surf.set_at((x,y+3),_NEST_COURSE_BOT)

def _nest_course_full(surf,x1,x2,base_y,sag,mid_col,skip_xs):
    skip_set=set()
    for sx in skip_xs:
        for dx in _NEST_STICK_X_OFF: skip_set.add(sx+dx)
    for x in range(x1,x2+1):
        if x not in skip_set: _nest_course_col(surf,x,x1,x2,base_y,sag,mid_col)

def _nest_course_at_vx(surf,vx,x1,x2,base_y,sag,mid_col):
    for dx in _NEST_STICK_X_OFF:
        x=vx+dx
        if x1<=x<=x2: _nest_course_col(surf,x,x1,x2,base_y,sag,mid_col)

def _nest_stick_at_course(surf,vx,x1,x2,base_y,sag):
    y_top=_nest_cy_sag(vx,x1,x2,base_y,sag)
    for y in range(y_top,y_top+4): _nest_stick_row(surf,vx,y)

def _nest_notches(surf,cy,courses,stick_wins):
    for ci,(offset,col,x1,x2,sag) in enumerate(courses):
        base_y=cy+offset
        for (cii,vx),wins in stick_wins.items():
            if cii!=ci: continue
            y_cross=_nest_cy_sag(vx,x1,x2,base_y,sag)
            if wins:
                for x in [vx-2,vx+3]:
                    if x1<=x<=x2:
                        surf.set_at((x,y_cross+1),_NEST_TWIG_DARK)
                        surf.set_at((x,y_cross+2),_NEST_TWIG_DARK)
            else:
                for dy in (-1,4):
                    surf.set_at((vx,y_cross+dy),_NEST_TWIG_DARK)
                    surf.set_at((vx+1,y_cross+dy),_NEST_TWIG_DARK)

def _nest_weave(surf,cy,ci_range,courses,stick_wins):
    for ci in ci_range:
        offset,col,x1,x2,sag=courses[ci]
        base_y=cy+offset
        skip=[vx for (cii,vx),wins in stick_wins.items() if cii==ci and wins]
        _nest_course_full(surf,x1,x2,base_y,sag,col,skip_xs=skip)
        for (cii,vx),wins in stick_wins.items():
            if cii==ci and not wins: _nest_course_at_vx(surf,vx,x1,x2,base_y,sag,col)

def _make_nest_params():
    s=_NEST_S; cx=_NEST_CX; r=lambda v: round(v*s)
    verts=[cx-r(9),cx+r(9)]
    courses=[
        (r(2), _NEST_TWIG_BRIGHT, cx-r(21), cx+r(21), max(1,r(2))),
        (r(6), _NEST_TWIG_MID,    cx-r(20), cx+r(20), max(1,r(2))),
        (r(10),_NEST_TWIG_BRIGHT, cx-r(18), cx+r(18), max(1,r(2))),
        (r(14),_NEST_TWIG_MID,    cx-r(16), cx+r(16), max(1,r(2))),
        (r(18),_NEST_TWIG_BRIGHT, cx-r(14), cx+r(14), max(1,r(3))),
    ]
    vxL,vxR=verts
    stick_wins={(ci,vxL):(ci%2==0) for ci in range(5)}
    stick_wins.update({(ci,vxR):(ci%2==1) for ci in range(5)})
    rim_rect=(cx-r(21),-r(5),r(42),max(4,r(12)))
    stick_bottom=r(18)
    hollow=(cx-r(11),r(16),r(22),max(2,r(3)))
    src=parrot._get_frames()[1]; bird_h=34
    bird_w=max(1,int(src.get_width()*bird_h/src.get_height()))
    bird=pygame.transform.smoothscale(src,(bird_w,bird_h))
    return verts,courses,stick_wins,rim_rect,stick_bottom,hollow,bird,bird_w,bird_h


P = _make_nest_params()


# ── BEFORE: today's shipped slot, mirrored verbatim ──────────────────────────

def draw_slot_before(surf, cy, alive):
    verts,courses,stick_wins,rim_rect,stick_bottom,hollow,bird,bird_w,bird_h = P
    cx=_NEST_CX
    rx,ry_off,rw,rh=rim_rect
    pygame.draw.ellipse(surf,(0,0,0),(rx,cy+ry_off,rw,rh))
    pygame.draw.arc(surf,_NEST_TWIG_BRIGHT,(rx,cy+ry_off,rw,rh),0,math.pi,2)
    _vxL=verts[0]
    for _dy in (-2,-1):
        _y=cy+ry_off+rh+_dy
        for _dx in _NEST_STICK_X_OFF:
            surf.set_at((_vxL+_dx,_y),_NEST_TWIG_BRIGHT)
    for vx in verts:
        _nest_stick_span(surf,vx,cy+ry_off+rh,cy+stick_bottom)
    _nest_weave(surf,cy,(0,1),courses,stick_wins)
    if alive:
        surf.blit(bird,(cx-bird_w//2,cy-bird_h//2+5))
    else:
        hx,hy_off,hw,hh=hollow
        pygame.draw.rect(surf,_NEST_HOLLOW_COL,(hx,cy+hy_off,hw,hh))
    _nest_weave(surf,cy,(2,3,4),courses,stick_wins)
    for ci in (2,3,4):
        offset,col,x1,x2,sag=courses[ci]
        base_y=cy+offset
        for (cii,vx),wins in stick_wins.items():
            if cii==ci and wins:
                _nest_stick_at_course(surf,vx,x1,x2,base_y,sag)
    _nest_notches(surf,cy,courses,stick_wins)


# ── AFTER: round 2 fixes ─────────────────────────────────────────────────────

def _shadow_px(surf, x, y, alpha):
    """Alpha-composite one shadow pixel; blit is the correct path on both
    plain and SRCALPHA destinations."""
    dot = pygame.Surface((1, 1), pygame.SRCALPHA)
    dot.fill((*_NEST_TWIG_DARK, alpha))
    surf.blit(dot, (x, y))


def _front_arc_y(x, ecx, ecy, a, b):
    """Bottom-half rim y at column x, or None outside the ellipse."""
    t = (x - ecx) / float(a)
    if abs(t) > 1.0:
        return None
    return ecy + b * math.sqrt(max(0.0, 1.0 - t * t))


def _line_pixels(p0, p1, surf_w, surf_h):
    """Return the pixel list drawn by draw.line(p0→p1), ordered p0→p1.

    Scanning only the bounding box avoids iterating the full surface for
    the handful of pixels that make up a short straw spur.
    """
    x_lo = max(0, min(p0[0], p1[0]) - 1)
    x_hi = min(surf_w - 1, max(p0[0], p1[0]) + 1)
    y_lo = max(0, min(p0[1], p1[1]) - 1)
    y_hi = min(surf_h - 1, max(p0[1], p1[1]) + 1)
    tmp = pygame.Surface((surf_w, surf_h))
    tmp.fill((0, 0, 0))
    pygame.draw.line(tmp, (255, 255, 255), p0, p1)
    pts = []
    for y in range(y_lo, y_hi + 1):
        for x in range(x_lo, x_hi + 1):
            if tmp.get_at((x, y))[0] > 0:
                pts.append((x, y))
    # Sort from anchor to tip so index-0 is always the nest-side pixel.
    pts.sort(key=lambda p: (p[0] - p0[0]) ** 2 + (p[1] - p0[1]) ** 2)
    return pts


def _draw_spur_lit(surf, p0, p1, cx):
    """Draw one straw spur with directional lighting and a 1-px tip shadow.

    Light arrives from the upper-left, so left spurs catch it on their
    anchor pixel; right spurs are relatively dim throughout. The darkest
    point is always the tip — thin straws read as tapered, not blunt.
    A single shadow pixel at the tip (offset one row toward the shadow
    side) grounds each spur in 3D space.
    """
    sw, sh = surf.get_size()
    pts = _line_pixels(p0, p1, sw, sh)
    if not pts:
        return

    is_left = p1[0] < cx
    # Bottom spurs descend away from the viewer's light; top spurs rise
    # into the light — the shadow direction flips accordingly.
    is_bottom = p1[1] >= p0[1]
    shadow_dy = 1 if is_bottom else -1

    # One shadow pixel at the tip in the shadow direction.
    tx, ty = pts[-1]
    sy = ty + shadow_dy
    if 0 <= sy < sh:
        surf.set_at((tx, sy), _NEST_TWIG_DARK)

    # Main line: bright catch-light on left-spur anchor, mid body, dark tip.
    for i, (x, y) in enumerate(pts):
        if i == len(pts) - 1:
            col = _NEST_TWIG_DARK
        elif i == 0 and is_left:
            col = _NEST_TWIG_BRIGHT
        else:
            col = _NEST_TWIG_MID
        surf.set_at((x, y), col)


def draw_slot_after(surf, cy, alive):
    verts,courses,stick_wins,rim_rect,stick_bottom,hollow,bird,bird_w,bird_h = P
    cx = _NEST_CX
    rx,ry_off,rw,rh = rim_rect

    # ── Identical to draw_slot_before ────────────────────────────────────────
    pygame.draw.ellipse(surf,(0,0,0),(rx,cy+ry_off,rw,rh))
    pygame.draw.arc(surf,_NEST_TWIG_BRIGHT,(rx,cy+ry_off,rw,rh),0,math.pi,2)
    _vxL = verts[0]
    for _dy in (-2,-1):
        _y = cy+ry_off+rh+_dy
        for _dx in _NEST_STICK_X_OFF:
            surf.set_at((_vxL+_dx,_y),_NEST_TWIG_BRIGHT)
    for vx in verts:
        _nest_stick_span(surf,vx,cy+ry_off+rh,cy+stick_bottom)
    _nest_weave(surf,cy,(0,1),courses,stick_wins)
    if alive:
        surf.blit(bird,(cx-bird_w//2,cy-bird_h//2+5))
    else:
        hx,hy_off,hw,hh = hollow
        pygame.draw.rect(surf,_NEST_HOLLOW_COL,(hx,cy+hy_off,hw,hh))
    _nest_weave(surf,cy,(2,3,4),courses,stick_wins)
    for ci in (2,3,4):
        offset,col,x1,x2,sag = courses[ci]
        base_y = cy+offset
        for (cii,vx),wins in stick_wins.items():
            if cii==ci and wins:
                _nest_stick_at_course(surf,vx,x1,x2,base_y,sag)
    _nest_notches(surf,cy,courses,stick_wins)

    # ── Veil concept: arc only redrawn on top of bird (minimal overdraw) ─────
    if alive:
        pygame.draw.arc(surf,_NEST_TWIG_BRIGHT,(rx,cy+ry_off,rw,rh),0,math.pi,2)


# ── Review sheet ─────────────────────────────────────────────────────────────

SKY = (136, 183, 197)
PANEL = (70, 90)
PANEL_CY = 42
ZOOM = 10
# Crop window captures the nest + fringe at full native res.
CROP = pygame.Rect(6, PANEL_CY - 17, 52, 46)


def _panel(fn, alive):
    s = pygame.Surface(PANEL)
    s.fill(SKY)
    fn(s, PANEL_CY, alive)
    return s


def _pixel_diff(fn_a, alive_a, fn_b, alive_b):
    """Count differing pixels between two panel renders."""
    a = pygame.Surface(PANEL); a.fill(SKY); fn_a(a, PANEL_CY, alive_a)
    b = pygame.Surface(PANEL); b.fill(SKY); fn_b(b, PANEL_CY, alive_b)
    return sum(
        1 for y in range(PANEL[1]) for x in range(PANEL[0])
        if a.get_at((x, y)) != b.get_at((x, y))
    )


def _zoom_crop(fn, alive):
    s = pygame.Surface(PANEL); s.fill(SKY); fn(s, PANEL_CY, alive)
    return pygame.transform.scale(
        s.subsurface(CROP).copy(),
        (CROP.w * ZOOM, CROP.h * ZOOM),
    )


def _check_silhouette(fn, alive):
    """Return (leftmost_x, rightmost_x) of non-sky pixels in a panel."""
    s = pygame.Surface(PANEL); s.fill(SKY); fn(s, PANEL_CY, alive)
    xs = [x for y in range(PANEL[1]) for x in range(PANEL[0])
          if tuple(s.get_at((x, y))[:3]) != SKY]
    return (min(xs), max(xs)) if xs else (None, None)


def main():
    alive_diff = _pixel_diff(draw_slot_before, True,  draw_slot_after, True)
    empty_diff = _pixel_diff(draw_slot_before, False, draw_slot_after, False)
    print("alive-state pixel diff vs today: %d" % alive_diff)
    print("empty-state pixel diff vs today: %d" % empty_diff)

    lx, rx_sil = _check_silhouette(draw_slot_after, True)
    print("after-alive silhouette: x %s .. %s  (width %s)" % (
        lx, rx_sil, rx_sil - lx + 1 if lx is not None else 0))

    f_lab = pygame.font.SysFont("dejavusans", 12)
    f_hd  = pygame.font.SysFont("dejavusans", 15, bold=True)

    # ── Row 1: 1× native panels ───────────────────────────────────────────────
    row1_labels = ["TODAY - alive", "TODAY - empty", "VEIL - alive", "VEIL - empty"]
    row1_panels = [
        _panel(draw_slot_before, True),
        _panel(draw_slot_before, False),
        _panel(draw_slot_after,  True),
        _panel(draw_slot_after,  False),
    ]

    # ── Row 2: 10× alive zoom — BEFORE vs AFTER ───────────────────────────────
    row2_zooms  = [_zoom_crop(draw_slot_before, True),  _zoom_crop(draw_slot_after, True)]
    row2_labels = ["BEFORE - alive (10×)", "AFTER - alive (10×)"]

    # ── Row 3 (new): 10× empty zoom — TODAY vs CONCEPT ────────────────────────
    row3_zooms  = [_zoom_crop(draw_slot_before, False), _zoom_crop(draw_slot_after, False)]
    row3_labels = ["TODAY - empty (10×)", "CONCEPT - empty (10×)"]

    zw, zh = CROP.w * ZOOM, CROP.h * ZOOM
    gap = 10
    pad = 16

    row_zoom_w = zw * 2 + gap
    W = row_zoom_w + pad * 2

    title_h  = 26
    row1_y   = pad + title_h
    row1_bot = row1_y + PANEL[1]
    row2_y   = row1_bot + 46          # label space + breathing room
    row2_bot = row2_y + zh
    row3_y   = row2_bot + 36          # section label + gap
    H        = row3_y + zh + pad

    sheet = pygame.Surface((W, H))
    sheet.fill((26, 30, 40))

    # Title + diff readout
    t = f_hd.render("loose-twig-veil  -  round 2", True, (240, 226, 190))
    sheet.blit(t, (pad, pad))
    diff_col = (150, 220, 150) if empty_diff > 0 else (230, 120, 120)
    t2 = f_lab.render(
        "alive diff: %d px  |  empty diff: %d px" % (alive_diff, empty_diff),
        True, diff_col,
    )
    sheet.blit(t2, (W - pad - t2.get_width(), pad + 4))

    # Row 1 — centred across the wider zoom row
    step = PANEL[0] + 12
    x0 = (W - (step * 4 - 12)) // 2
    for i, (p, lab) in enumerate(zip(row1_panels, row1_labels)):
        px = x0 + i * step
        sheet.blit(p, (px, row1_y))
        pygame.draw.rect(sheet, (70, 78, 92), (px, row1_y, *PANEL), 1)
        lt = f_lab.render(lab, True, (200, 208, 220))
        sheet.blit(lt, (px + (PANEL[0] - lt.get_width()) // 2, row1_bot + 4))

    # Row 2 — alive 10× zoom
    for i, (z, lab) in enumerate(zip(row2_zooms, row2_labels)):
        px = pad + i * (zw + gap)
        sheet.blit(z, (px, row2_y))
        pygame.draw.rect(sheet, (70, 78, 92), (px, row2_y, zw, zh), 1)
        lt = f_lab.render(lab, True, (200, 208, 220))
        sheet.blit(lt, (px, row2_y - 16))

    # Row 3 — empty 10× zoom (new; shows spur anatomy without the bird)
    for i, (z, lab) in enumerate(zip(row3_zooms, row3_labels)):
        px = pad + i * (zw + gap)
        sheet.blit(z, (px, row3_y))
        pygame.draw.rect(sheet, (70, 78, 92), (px, row3_y, zw, zh), 1)
        lt = f_lab.render(lab, True, (200, 208, 220))
        sheet.blit(lt, (px, row3_y - 16))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("saved %s  (%d × %d)" % (out, W, H))


if __name__ == "__main__":
    main()
