"""Review render for the `loose-twig-veil` nest concept.

Standalone on purpose: the live HUD is left untouched until the design loop
picks a winner, so today's slot code is mirrored here verbatim as the
BEFORE baseline and the concept is a second, independent draw function.
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
                        surf.set_at((x,y_cross+1),_NEST_TWIG_DARK); surf.set_at((x,y_cross+2),_NEST_TWIG_DARK)
            else:
                for dy in (-1,4):
                    surf.set_at((vx,y_cross+dy),_NEST_TWIG_DARK); surf.set_at((vx+1,y_cross+dy),_NEST_TWIG_DARK)

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
    courses=[(r(2),_NEST_TWIG_BRIGHT,cx-r(21),cx+r(21),max(1,r(2))),(r(6),_NEST_TWIG_MID,cx-r(20),cx+r(20),max(1,r(2))),(r(10),_NEST_TWIG_BRIGHT,cx-r(18),cx+r(18),max(1,r(2))),(r(14),_NEST_TWIG_MID,cx-r(16),cx+r(16),max(1,r(2))),(r(18),_NEST_TWIG_BRIGHT,cx-r(14),cx+r(14),max(1,r(3)))]
    vxL,vxR=verts
    stick_wins={(ci,vxL):(ci%2==0) for ci in range(5)}; stick_wins.update({(ci,vxR):(ci%2==1) for ci in range(5)})
    rim_rect=(cx-r(21),-r(5),r(42),max(4,r(12))); stick_bottom=r(18); hollow=(cx-r(11),r(16),r(22),max(2,r(3)))
    src=parrot._get_frames()[1]; bird_h=34; bird_w=max(1,int(src.get_width()*bird_h/src.get_height()))
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


# ── AFTER: split-shell-rim base + loose-twig veil ────────────────────────────

def _shadow_px(surf, x, y, alpha):
    """One alpha-blended pixel; blit is the only path that composites correctly
    on both plain and SRCALPHA destinations."""
    dot = pygame.Surface((1, 1), pygame.SRCALPHA)
    dot.fill((*_NEST_TWIG_DARK, alpha))
    surf.blit(dot, (x, y))


def _front_arc_y(x, ecx, ecy, a, b):
    """Bottom-half rim y at column x, or None outside the ellipse."""
    t = (x - ecx) / float(a)
    if abs(t) > 1.0:
        return None
    return ecy + b * math.sqrt(max(0.0, 1.0 - t * t))


def _draw_spur(surf, p0, p1, col):
    pygame.draw.line(surf, col, p0, p1)
    # Tips read as fine tapering straw only if the last pixel goes dark.
    surf.set_at(p1, _NEST_TWIG_DARK)


def draw_slot_after(surf, cy, alive):
    verts,courses,stick_wins,rim_rect,stick_bottom,hollow,bird,bird_w,bird_h = P
    cx=_NEST_CX
    rx,ry_off,rw,rh=rim_rect
    pygame.draw.ellipse(surf,(0,0,0),(rx,cy+ry_off,rw,rh))
    # Thicker back rim reads as the far wall of a bowl rather than a hairline.
    back_w = 3 if alive else 2
    pygame.draw.arc(surf,_NEST_TWIG_BRIGHT,(rx,cy+ry_off,rw,rh),0,math.pi,back_w)
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

    if not alive:
        return

    ecx = rx + rw / 2.0
    ecy = cy + ry_off + rh / 2.0
    a, b = rw / 2.0, rh / 2.0
    bx0, bx1 = cx - bird_w // 2, cx - bird_w // 2 + bird_w - 1

    # Front half of the rim, after the bird, so the bowl wraps its belly.
    pygame.draw.arc(surf,_NEST_TWIG_BRIGHT,(rx,cy+ry_off,rw,rh),math.pi,2*math.pi,2)
    # Contact shadow only where the front rim overlaps the bird — that is the
    # only place a cast shadow would land.
    by0 = cy - bird_h // 2 + 5
    for x in range(bx0, bx1 + 1):
        fy = _front_arc_y(x, ecx, ecy, a - 1.0, b - 1.0)
        if fy is None:
            continue
        sy = int(round(fy)) + 1
        if bird.get_at((x - bx0, sy - by0))[3] < 128:
            continue
        _shadow_px(surf, x, sy, 140)

    # Two loose strands sagging across the chest. Kept under cy-2 so the eye
    # and beak stay unobstructed.
    for pts in (
        [(cx - 15, cy + 0), (cx - 1, cy + 3), (cx + 13, cy + 1)],
        [(cx - 13, cy + 6), (cx + 1, cy + 9), (cx + 15, cy + 7)],
    ):
        pygame.draw.lines(surf, _NEST_TWIG_MID, False, pts)

    # Splayed straw shooting past the silhouette — the irregular fringe is what
    # sells "nest" more than any clean rim edge does.
    spurs = [
        ((cx - 16, cy + 2),  (cx - 20, cy - 1), _NEST_TWIG_BRIGHT),
        ((cx + 16, cy + 3),  (cx + 21, cy + 0), _NEST_TWIG_MID),
        ((cx - 14, cy + 9),  (cx - 18, cy + 12), _NEST_TWIG_BRIGHT),
        ((cx + 15, cy + 7),  (cx + 19, cy + 5), _NEST_TWIG_MID),
        ((cx - 9,  cy + 20), (cx - 12, cy + 23), _NEST_TWIG_BRIGHT),
        ((cx + 9,  cy + 20), (cx + 12, cy + 23), _NEST_TWIG_MID),
        ((cx + 1,  cy + 21), (cx + 3,  cy + 24), _NEST_TWIG_BRIGHT),
    ]
    for p0, p1, col in spurs:
        _draw_spur(surf, p0, p1, col)


# ── Review sheet ─────────────────────────────────────────────────────────────

SKY = (136, 183, 197)
PANEL = (70, 90)
PANEL_CY = 42
ZOOM = 10
CROP = pygame.Rect(6, PANEL_CY - 17, 52, 46)


def _panel(fn, alive):
    s = pygame.Surface(PANEL)
    s.fill(SKY)
    fn(s, PANEL_CY, alive)
    return s


def _empty_diff():
    a = pygame.Surface(PANEL); a.fill(SKY); draw_slot_before(a, PANEL_CY, False)
    c = pygame.Surface(PANEL); c.fill(SKY); draw_slot_after(c, PANEL_CY, False)
    n = 0
    for y in range(PANEL[1]):
        for x in range(PANEL[0]):
            if a.get_at((x, y)) != c.get_at((x, y)):
                n += 1
    return n


def main():
    diff = _empty_diff()
    print("empty-state pixel diff: %d" % diff)

    f_lab = pygame.font.SysFont("dejavusans", 12)
    f_hd = pygame.font.SysFont("dejavusans", 15, bold=True)

    labels = ["TODAY - alive", "TODAY - empty", "VEIL - alive", "VEIL - empty"]
    panels = [_panel(draw_slot_before, True), _panel(draw_slot_before, False),
              _panel(draw_slot_after, True), _panel(draw_slot_after, False)]

    zoom_src = []
    for fn in (draw_slot_before, draw_slot_after):
        s = pygame.Surface(PANEL); s.fill(SKY); fn(s, PANEL_CY, True)
        zoom_src.append(s.subsurface(CROP).copy())
    zw, zh = CROP.w * ZOOM, CROP.h * ZOOM
    zooms = [pygame.transform.scale(z, (zw, zh)) for z in zoom_src]

    gap = 10
    pad = 16
    row2_w = zw * 2 + gap
    W = row2_w + pad * 2
    row1_y = pad + 26
    row2_y = row1_y + PANEL[1] + 46
    H = row2_y + zh + 24

    sheet = pygame.Surface((W, H))
    sheet.fill((26, 30, 40))

    t = f_hd.render("loose-twig-veil  -  round 1", True, (240, 226, 190))
    sheet.blit(t, (pad, pad))
    t = f_lab.render("empty-state pixel diff vs today: %d" % diff, True,
                     (150, 220, 150) if diff == 0 else (230, 120, 120))
    sheet.blit(t, (W - pad - t.get_width(), pad + 3))

    step = PANEL[0] + 12
    x0 = (W - (step * 4 - 12)) // 2
    for i, (p, lab) in enumerate(zip(panels, labels)):
        px = x0 + i * step
        sheet.blit(p, (px, row1_y))
        pygame.draw.rect(sheet, (70, 78, 92), (px, row1_y, *PANEL), 1)
        lt = f_lab.render(lab, True, (200, 208, 220))
        sheet.blit(lt, (px + (PANEL[0] - lt.get_width()) // 2, row1_y + PANEL[1] + 4))

    for i, (z, lab) in enumerate(zip(zooms, ["BEFORE - alive (10x)", "AFTER - alive (10x)"])):
        px = pad + i * (zw + gap)
        sheet.blit(z, (px, row2_y))
        pygame.draw.rect(sheet, (70, 78, 92), (px, row2_y, zw, zh), 1)
        lt = f_lab.render(lab, True, (200, 208, 220))
        sheet.blit(lt, (px, row2_y - 16))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("saved %s (%dx%d)" % (out, W, H))


if __name__ == "__main__":
    main()
