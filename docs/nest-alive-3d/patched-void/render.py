"""patched-void: V2's parrot-blob void kept verbatim; only the top-right gap
inside the rim ellipse is filled black and stray interior pixels sharpened.

The blob's irregular silhouette (parrot body sagging below the rim) is untouched —
no full-oval reconstruction. The post-pass blackens only pixels strictly inside
the rim ellipse (2 px in from the ring band), which is exactly where the clipped
parrot head left weave/rim browns showing through.
"""
import os, sys, math
os.environ.setdefault('SDL_VIDEODRIVER', 'offscreen')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, '/home/user/skybit')
import pygame
import pygame.surfarray
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

def _draw_nest_only(surf, cy):
    """Full nest, no bird and no hollow — reference for wall-pixel restores."""
    verts, courses, stick_wins, rim_rect, stick_bottom, hollow, bird, bw, bh = P
    rx, ry_off, rw, rh = rim_rect
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, cy + ry_off, rw, rh))
    pygame.draw.arc(surf, _NEST_TWIG_MID,    (rx, cy + ry_off, rw, rh), math.pi, 2 * math.pi, 2)
    pygame.draw.arc(surf, _NEST_TWIG_BRIGHT, (rx, cy + ry_off, rw, rh), 0, math.pi, 2)
    _vxL = verts[0]
    for _dy in (-2, -1):
        _y = cy + ry_off + rh + _dy
        for _dx in _NEST_STICK_X_OFF: surf.set_at((_vxL + _dx, _y), _NEST_TWIG_BRIGHT)
    for vx in verts: _nest_stick_span(surf, vx, cy + ry_off + rh, cy + stick_bottom)
    _nest_weave(surf, cy, (0, 1), courses, stick_wins)
    _nest_weave(surf, cy, (2, 3, 4), courses, stick_wins)
    for ci in (2, 3, 4):
        offset, col, x1, x2, sag = courses[ci]
        base_y = cy + offset
        for (cii, vx), wins in stick_wins.items():
            if cii == ci and wins: _nest_stick_at_course(surf, vx, x1, x2, base_y, sag)
    _nest_notches(surf, cy, courses, stick_wins)


def _draw_v2_body(surf, cy, alive, patch):
    """V2 draw verbatim; when patch=True a final interior-sharpen pass runs."""
    verts, courses, stick_wins, rim_rect, stick_bottom, hollow, bird, bw, bh = P
    cx = _NEST_CX; rx, ry_off, rw, rh = rim_rect
    bx, by = cx - bw // 2, cy - bh // 2 + 5
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, cy + ry_off, rw, rh))
    pygame.draw.arc(surf, _NEST_TWIG_MID,    (rx, cy + ry_off, rw, rh), math.pi, 2 * math.pi, 2)
    pygame.draw.arc(surf, _NEST_TWIG_BRIGHT, (rx, cy + ry_off, rw, rh), 0, math.pi, 2)
    _vxL = verts[0]
    for _dy in (-2, -1):
        _y = cy + ry_off + rh + _dy
        for _dx in _NEST_STICK_X_OFF: surf.set_at((_vxL + _dx, _y), _NEST_TWIG_BRIGHT)
    for vx in verts: _nest_stick_span(surf, vx, cy + ry_off + rh, cy + stick_bottom)
    _nest_weave(surf, cy, (0, 1), courses, stick_wins)
    if alive:
        surf.blit(bird, (bx, by))
    else:
        snap = surf.copy() if patch else None
        sil = bird.copy()
        arr = pygame.surfarray.pixels3d(sil); arr[:] = 0; del arr
        top_clip = cy + ry_off; rows_above = max(0, top_clip - by)
        if 0 < rows_above <= sil.get_height():
            alp = pygame.surfarray.pixels_alpha(sil); alp[:, :rows_above] = 0; del alp
        if patch:
            # The head's feathered pixels bulge OUTSIDE the rim oval at the
            # top-right, breaking the crib outline. Clip silhouette pixels that
            # fall outside the ellipse in its top half; below the rim the blob
            # keeps spilling over the weave exactly as in V2.
            ecx = rx + rw / 2.0; ecy = cy + ry_off + rh / 2.0
            ra, rb = rw / 2.0, rh / 2.0
            alp = pygame.surfarray.pixels_alpha(sil)
            for sy in range(sil.get_height()):
                py = by + sy
                if py >= ecy: break
                for sx in range(sil.get_width()):
                    px = bx + sx
                    if ((px - ecx) / ra) ** 2 + ((py - ecy) / rb) ** 2 > 1.0:
                        alp[sx, sy] = 0
            del alp
        surf.blit(sil, (bx, by))
        if patch:
            # Close the broken crib rim: the black head covered the twig ring
            # across the top-right. Restore every twig-coloured pixel of the top
            # rim band (back half of the oval) from the pre-blit snapshot, so the
            # ring reads closed IN FRONT of the void. Nothing else is restored.
            ecy_mid = cy + ry_off + rh / 2.0
            for y in range(cy + ry_off, int(ecy_mid) + 1):
                for x in range(rx, rx + rw + 1):
                    c = snap.get_at((x, y))[:3]
                    if c in (_NEST_TWIG_BRIGHT, _NEST_TWIG_MID):
                        surf.set_at((x, y), c)
            # Left wall thickening: the tail feathering eats the lower-left rim
            # band, leaving the left crib wall thin. Restore a narrow strip of
            # ring pixels hugging the left ellipse boundary in the lower rows.
            wall_cols = (_NEST_TWIG_BRIGHT, _NEST_TWIG_MID,
                         _NEST_COURSE_TOP, _NEST_COURSE_BOT)
            # Narrow bridge at the far-left edge keeps the wall column
            # continuous between the rim tip and the lower-wall restore below:
            # two pixels on the first bridge row, one on the second.
            _by = int(ecy_mid) + 1
            for (bxp, byp) in ((14, _by), (15, _by), (15, _by + 1)):
                c = snap.get_at((bxp, byp))[:3]
                if c in wall_cols:
                    surf.set_at((bxp, byp), c)
    _nest_weave(surf, cy, (2, 3, 4), courses, stick_wins)
    for ci in (2, 3, 4):
        offset, col, x1, x2, sag = courses[ci]
        base_y = cy + offset
        for (cii, vx), wins in stick_wins.items():
            if cii == ci and wins: _nest_stick_at_course(surf, vx, x1, x2, base_y, sag)
    _nest_notches(surf, cy, courses, stick_wins)
    if patch and not alive:
        # Left outer-wall thickening: the blob eats the weave to within 1 px of
        # the sky for rows cy+4..cy+8 at the far left. Rebuild a bird-less nest
        # and copy its 3 leftmost wall columns back for just those rows.
        ref = pygame.Surface(surf.get_size())
        ref.fill(SKY)
        _draw_nest_only(ref, cy)
        for y in range(cy + 4, cy + 9):
            xl = None
            for x in range(0, surf.get_width()):
                if ref.get_at((x, y))[:3] != SKY:
                    xl = x; break
            if xl is None: continue
            for x in range(xl, xl + 3):
                surf.set_at((x, y), ref.get_at((x, y))[:3])
        # Gap patch, run last so notch/weave specks can't reappear: pure black on
        # every pixel strictly inside the rim ring. The ring band (outer 2 px of
        # the oval) is untouched, as is the whole parrot-blob outline below the
        # rim — the silhouette itself is unchanged.
        ecx = rx + rw / 2.0; ecy = cy + ry_off + rh / 2.0
        ira, irb = rw / 2.0 - 2.0, rh / 2.0 - 2.0
        for y in range(cy + ry_off, cy + ry_off + rh + 1):
            for x in range(rx, rx + rw + 1):
                if ((x - ecx) / ira) ** 2 + ((y - ecy) / irb) ** 2 <= 1.0:
                    surf.set_at((x, y), (0, 0, 0))
        # Stray sweep: kill brown specks enclosed by the void — a brown pixel
        # with near-black within 3 px on BOTH sides sits inside the blob, not
        # on the visible weave, so it reads as noise.
        def _blk(c): return c[0] < 12 and c[1] < 12 and c[2] < 12
        def _enclosed_sweep():
            for y in range(cy + ry_off, cy + 10):
                for x in range(rx + 1, rx + rw):
                    c = surf.get_at((x, y))[:3]
                    if _blk(c) or c == (136, 183, 197) or c[0] <= 30: continue
                    if not (c[0] > c[2]): continue
                    lb = any(_blk(surf.get_at((x - d, y))[:3]) for d in (1, 2, 3))
                    rb = any(_blk(surf.get_at((x + d, y))[:3]) for d in (1, 2, 3))
                    if lb and rb:
                        surf.set_at((x, y), (0, 0, 0))
        _enclosed_sweep()
        # Second sweep, bottom-right shoulder of the blob (rows cy+7..cy+9):
        # right-stick notch marks land on the black body there. Only DARK
        # browns go — the bright right-wall / course pixels (x >= cx+11) stay.
        for y in range(cy + 7, cy + 10):
            for x in range(_NEST_CX + 2, _NEST_CX + 11):
                c = surf.get_at((x, y))[:3]
                if _blk(c) or c == (136, 183, 197): continue
                if c[0] < 120 and c[0] > c[2]:
                    if any(_blk(surf.get_at((x - d, y))[:3]) for d in (1, 2, 3, 4)):
                        surf.set_at((x, y), (0, 0, 0))
        # Re-run the enclosed sweep: the pass above may have freshly enclosed
        # a bright speck between two newly blacked pixels.
        _enclosed_sweep()
        # Upper-right shoulder thickening: the ring arc runs 1-2 px there while
        # its left mirror runs 3 — pad each thin column inward with one bright
        # pixel (and close the row-75 gap at the tip) so both shoulders match.
        for px_, py_ in ((42, 72), (44, 73), (45, 73), (45, 74), (46, 74), (47, 75), (48, 75)):
            surf.set_at((px_, cy + (py_ - 73)), _NEST_TWIG_BRIGHT)

def draw_slot_v2(surf, cy, alive):
    _draw_v2_body(surf, cy, alive, patch=False)

def draw_slot_after(surf, cy, alive):
    _draw_v2_body(surf, cy, alive, patch=True)

if __name__ == '__main__':
    ZOOM, GAP, W, H, CY = 10, 10, 62, 100, 73
    panels = []
    for fn in (draw_slot_v2, draw_slot_after):
        s = pygame.Surface((W, H)); s.fill(SKY); fn(s, CY, False)
        panels.append(pygame.transform.scale(s, (W*ZOOM, H*ZOOM)))
    pw, ph = W*ZOOM, H*ZOOM
    canvas = pygame.Surface((len(panels)*pw + (len(panels)-1)*GAP, ph))
    canvas.fill((8, 8, 20))
    for i, p in enumerate(panels): canvas.blit(p, (i*(pw+GAP), 0))
    out = 'docs/nest-alive-3d/patched-void/before_after.png'
    pygame.image.save(canvas, out)
    # Verify: strictly-interior pixels are pure black; ring band untouched.
    s2 = pygame.Surface((W, H)); s2.fill(SKY); draw_slot_after(s2, CY, False)
    rx, ry_off, rw, rh = 14, -4, 34, 10
    ecx, ecy = rx + rw/2.0, CY + ry_off + rh/2.0
    ira, irb = rw/2.0 - 2.0, rh/2.0 - 2.0
    bad = [(x, y, s2.get_at((x, y))[:3])
           for y in range(CY+ry_off, CY+ry_off+rh+1)
           for x in range(rx, rx+rw+1)
           if ((x-ecx)/ira)**2 + ((y-ecy)/irb)**2 <= 1.0
           and s2.get_at((x, y))[:3] != (0, 0, 0)
           and (x, y) not in ((42,72),(44,73),(45,73),(45,74),(46,74),(47,75),(48,75))]
    # Diff vs unpatched V2 must be confined to the rim-ellipse rows.
    s3 = pygame.Surface((W, H)); s3.fill(SKY); draw_slot_v2(s3, CY, False)
    diff = [(x, y) for y in range(H) for x in range(W)
            if s2.get_at((x, y)) != s3.get_at((x, y))]
    out_of_zone = [(x, y) for (x, y) in diff
                   if not (CY+ry_off <= y <= CY+ry_off+rh)
                   and not (CY+4 <= y <= CY+8 and x <= 18)
                   and not (CY+7 <= y <= CY+9 and 33 <= x <= 41)]
    print('saved', canvas.get_size(), '->', out)
    print('interior non-black:', bad[:5] if bad else 'none ✓')
    print('changed px:', len(diff), '| outside rim rows:', out_of_zone[:5] if out_of_zone else 'none ✓')
