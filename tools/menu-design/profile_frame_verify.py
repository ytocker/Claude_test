"""Clearance gate for the connected-tag options.

Everything here is measured off rasterised masks, never off bounding boxes:
the earlier "2px clip" reading came from Pip's bbox, while his actual drawn
silhouette had 32 pixels outside the frame. Ropes are re-derived from
draw_signchain's own anchor/endpoint maths and rasterised with the same
rope() call the menu uses, so a "clear" verdict here is clear on screen.

    python3 tools/menu-design/profile_frame_verify.py
"""
import math
import os
import sys

_ROOT = "/home/user/skybit"
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tools", "menu-design"))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import numpy as np                                # noqa: E402
import pygame                                     # noqa: E402
import profile_frame_connected as PFC             # noqa: E402

B = PFC.B
W, H = PFC.W, PFC.H
pygame.init()


def _pts(surf):
    m = pygame.mask.from_surface(surf, 8)
    return np.array(m.outline() or [], dtype=float), m


def _opaque(surf):
    a = pygame.surfarray.array_alpha(surf).astype(np.int16)
    ys, xs = np.nonzero(a.T > 8)
    return np.stack([xs, ys], 1).astype(float)


def min_gap(a, b, chunk=400):
    """Nearest-neighbour distance between two opaque point sets, minus one
    pixel: two pixels that touch are 1.0 apart by centre but 0 px clear."""
    best = 1e9
    for i in range(0, len(a), chunk):
        d = np.hypot(a[i:i + chunk, None, 0] - b[None, :, 0],
                     a[i:i + chunk, None, 1] - b[None, :, 1])
        best = min(best, float(d.min()))
    return best - 1.0


def pip_points():
    from game.entities import Bird
    bird = Bird()
    bird.frame_t = 0.0
    bird.x, bird.y = B.PIP_CX, B.PIP_CY
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    bird.draw(s)
    return _opaque(s)


def rope_polylines():
    """The two rope columns, straight out of draw_signchain's own formula."""
    cloud = B.cloud_rect()
    bw, bh = 172, 44
    dx = -10 if B.VARIANT in ("B", "C") else 0
    cx, cy, ang = 112 + dx, 386, -3.0
    rad = math.radians(-ang)
    anchors = [(min(max(x, cloud.left + 14), cloud.right - 14), B.CLOUD_ANCHOR_Y)
               for x in B.CLOUD_HOOK_X]
    out = []
    for sgn, apt in zip((-1, 1), anchors):
        ox = sgn * (bw * 0.36)
        hx = cx + ox * math.cos(rad)
        hy = cy + ox * math.sin(rad) - bh * 0.5
        x0, y0 = apt
        out.append([(x0 + (hx - x0) * (i / 12),
                     y0 + (hy - y0) * (i / 12) + math.sin(math.pi * i / 12) * 5)
                    for i in range(13)])
    return out


def rope_x_at(poly, y):
    """Interpolate the drawn polyline (not an idealised catenary) at row y."""
    for (xa, ya), (xb, yb) in zip(poly, poly[1:]):
        if ya <= y <= yb:
            t = (y - ya) / (yb - ya) if yb != ya else 0.0
            return xa + (xb - xa) * t
    return None


def rope_points():
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    for poly in rope_polylines():
        pygame.draw.lines(s, (200, 170, 120, 255), False, poly, 4)
    return _opaque(s)


def gold_points(fn):
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    fn(s)
    return _opaque(s)


def report():
    pip = pip_points()
    ropes = rope_points()
    polys = rope_polylines()
    plank_top = 386 - (44 / 2 * math.cos(math.radians(3))
                       + 172 / 2 * math.sin(math.radians(3)))
    print(f"Pip silhouette: {len(pip):.0f} opaque px, "
          f"x{pip[:,0].min():.0f}..{pip[:,0].max():.0f} "
          f"y{pip[:,1].min():.0f}..{pip[:,1].max():.0f}")
    print(f"STORE plank top edge y={plank_top:.1f}\n")

    for key in PFC.ORDER:
        fn, slug, thesis, _crop = PFC.OPTIONS[key]
        gold = gold_points(fn)
        gp = min_gap(pip, gold)
        gr = min_gap(ropes, gold)
        low = gold[:, 1].max()
        print(f"[{key}] {slug}")
        print(f"    gold px         : {len(gold):.0f}   "
              f"bbox x{gold[:,0].min():.0f}..{gold[:,0].max():.0f} "
              f"y{gold[:,1].min():.0f}..{gold[:,1].max():.0f}")
        print(f"    Pip SILHOUETTE  : {gp:+.1f} px clear "
              f"({'OK' if gp >= 6 else 'FAIL'})")
        print(f"    rope mask (2-D) : {gr:+.1f} px clear "
              f"({'OK' if gr >= 4 else 'FAIL'})")
        for y in (316, 322, 330, 340, 350):
            row = gold[gold[:, 1] == y]
            if not len(row):
                print(f"      y{y}: no gold on this row")
                continue
            lx, rx = row[:, 0].min(), row[:, 0].max()
            l_r = rope_x_at(polys[0], y)
            r_r = rope_x_at(polys[1], y)
            lg = lx - (l_r + 2) if l_r is not None else None
            rg = (r_r - 2) - rx if r_r is not None else None
            print(f"      y{y}: gold x{lx:.0f}..{rx:.0f} | L-rope "
                  f"x{l_r:.1f} gap {lg:+.1f} | R-rope x{r_r:.1f} gap {rg:+.1f}")
        print(f"    lowest gold y   : {low:.0f}  "
              f"(plank {plank_top - low:+.1f} px below)"
              f" {'OK' if low < plank_top - 4 else 'FAIL'}")
        print(f"    right-most gold : x{gold[:,0].max():.0f} "
              f"{'OK' if gold[:,0].max() <= 168 else 'FAIL (cap 168)'}\n")


if __name__ == "__main__":
    report()
