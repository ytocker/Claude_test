"""DESIGN PICK: 5 variants of where Pip's squall-snow sits, each
fixing two issues — head snow must sit ON his crown (not float
off to the upper-left) and the drift must cover his TAIL. Renders
ONE comparison sheet; nothing in the game changes until a variant
is chosen.

Each variant is just a different flake POOL. We set the live
module global game.entities._SNOW_POOL and call Bird.draw, so the
panels use the EXACT shipped render path (soft discs, tilt, dy
shading) — what you see is what shipping that pool looks like.

Output: docs/screenshots/wind_themes/snow_back/placements_sheet.png

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
      python -m tools.render_snow_placements
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import game.entities as E
from game.entities import Bird

pygame.init()
pygame.display.set_mode((360, 640))

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "wind_themes", "snow_back")
os.makedirs(OUT_DIR, exist_ok=True)

A1, A2 = 0.7548776662, 0.5698402910        # R2 low-discrepancy seq


def _line_fn(key):
    """Piecewise-linear y(x) over key points (ascending x)."""
    def f(x):
        if x <= key[0][0]:
            return key[0][1]
        if x >= key[-1][0]:
            return key[-1][1]
        for j in range(len(key) - 1):
            x0, y0 = key[j]
            x1, y1 = key[j + 1]
            if x0 <= x <= x1:
                t = (x - x0) / (x1 - x0)
                return y0 + (y1 - y0) * t
        return key[-1][1]
    return f


def band(pool, key, x_lo, x_hi, y_lo, y_hi, along, *,
         dy_cull=-1.0, dy_full=3.0, dy_end=8.0, wmul=1.0, M=160,
         seed=0, wind_rear=True, face_guard=False):
    """Scatter flakes in a band that RESTS ON the line `key` (x in
    [x_lo,x_hi]). dy = y - line(x); flake centres sit just BELOW
    the top contour (dy>0) so the soft discs rest on the body and
    their tops form the snow height — almost none above the line,
    so the snow doesn't float. `face_guard` culls flakes over the
    sunglasses. Appends (x,y,dy,w) to `pool`."""
    line = _line_fn(key)
    for i in range(M):
        u = (0.5 + A1 * (i + 1 + seed)) % 1.0
        v = (0.5 + A2 * (i + 1 + seed)) % 1.0
        x = x_lo + u * (x_hi - x_lo)
        y = y_lo + v * (y_hi - y_lo)
        if face_guard and x > 13.0 and y > -17.0:
            continue
        dy = y - line(x)
        if dy < dy_cull:
            continue
        if dy < 0.0:                       # tiny crest just at the edge
            wy = max(0.0, 1.0 + dy / (-dy_cull)) * 0.6
        elif dy <= dy_full:
            wy = 1.0
        else:
            wy = max(0.0, 1.0 - (dy - dy_full) / (dy_end - dy_full))
        wind = (1.0 + max(0.0, -x) / 55.0) if wind_rear else 1.0
        noise = 0.78 + 0.22 * ((math.sin((i + seed) * 12.9898)
                                * 43758.5453) % 1.0)
        w = along(x) * wy * wind * noise * wmul
        if w > 0.001:
            pool.append((x, y, dy, w))


def crown(pool, *, cx=10.0, top=-25.0, curve=0.09, x_lo=4.0, x_hi=16.0,
          y_lo=-29.0, y_hi=-17.0, dy_cull=-1.0, dy_full=1.5, dy_end=4.5,
          wmul=0.82, M=80, seed=900):
    """Snow cap RESTING ON the crown (green hat) — dome line top at
    cx, flake centres just below it so the cap sits on the head
    instead of floating above. Stays clear of the sunglasses."""
    def crown_y(x):
        return top + curve * (x - cx) ** 2

    def along(x):
        w = 1.0
        if x > x_hi - 3.0:
            w *= max(0.18, 1.0 - (x - (x_hi - 3.0)) / 3.0)
        if x < x_lo + 2.0:
            w *= max(0.30, 1.0 - ((x_lo + 2.0) - x) / 2.0)
        return w

    for i in range(M):
        u = (0.5 + A1 * (i + 1 + seed)) % 1.0
        v = (0.5 + A2 * (i + 1 + seed)) % 1.0
        x = x_lo + u * (x_hi - x_lo)
        y = y_lo + v * (y_hi - y_lo)
        dy = y - crown_y(x)
        if dy < dy_cull:
            continue
        # Hard guard: never spill onto the sunglasses/face.
        if x > 13.0 and y > -17.0:
            continue
        if dy < 0.0:
            wy = max(0.0, 1.0 + dy / (-dy_cull)) * 0.6
        elif dy <= dy_full:
            wy = 1.0
        else:
            wy = max(0.0, 1.0 - (dy - dy_full) / (dy_end - dy_full))
        wind = 1.0 + max(0.0, -(x - cx)) / 45.0
        noise = 0.78 + 0.22 * ((math.sin((i + seed) * 12.9898)
                                * 43758.5453) % 1.0)
        w = along(x) * wy * wind * noise * wmul
        if w > 0.001:
            pool.append((x, y, dy, w))
    return pool


# Calibrated upper-silhouette key points (sprite-rel, centre 0,0).
TAIL_BACK = [
    (-31.0, -2.0),   # tail tip (upper edge)
    (-25.0, -4.0),   # tail upper
    (-19.0, -6.0),   # rump
    (-12.0, -8.0),   # back
    (-5.0,  -8.5),   # back crest
    (2.0,   -8.0),   # back/shoulder
    (8.0,   -9.0),   # shoulder
]
# Continuous line that climbs the nape onto the crown-top.
TAIL_TO_CROWN = TAIL_BACK + [(11.0, -15.0), (13.0, -22.0), (15.5, -22.0)]


def _sort(pool):
    pool.sort(key=lambda p: p[3], reverse=True)
    return pool


# ── Chosen (disconnected) baseline, for reference ────────────────────────────

def v4_chosen():
    """The shipped placement: heavy back drift + a separate crown
    cap, with a GAP at the nape between them."""
    p = []
    band(p, TAIL_BACK, -29.5, 6.0, -11.0, 11.0,
         along=lambda x: (max(0.6, 1.0 - (-29.0 - x) / 4.0) if x < -29 else
                          (max(0.4, 1.0 - (x - 3.0) / 4.0) if x > 3.0 else 1.0)),
         dy_cull=-1.5, dy_full=4.0, dy_end=10.0, wmul=1.2, M=300)
    crown(p, cx=16.0, x_lo=10.0, x_hi=22.0,
          wmul=1.0, M=110, dy_cull=-1.5, dy_full=2.5, dy_end=6.0)
    return _sort(p)


# ── CONNECTED variants — back + head joined into ONE layer ───────────────────
# A continuous line from the tail tip, over the back, UP the nape,
# onto the crown. Snow accumulates along it so the two regions
# merge into a single drift as the storm worsens. The 5 versions
# vary the bridge over the nape (thin ridge → full merge → high
# arc → low saddle) and the overall amount.

CONT_LINE = [
    (-31.0, -2.0), (-25.0, -4.0), (-19.0, -6.0), (-12.0, -8.0),
    (-5.0,  -8.5), (2.0,  -8.0),  (8.0,  -9.0),
    (11.0, -15.0), (14.0, -21.0), (17.0, -22.0),   # nape → crown
]
# A higher/lower nape routing for the arc / saddle variants.
CONT_HIGH = CONT_LINE[:7] + [(10.0, -16.0), (12.0, -22.0), (15.0, -24.0),
                             (18.0, -23.0)]
CONT_SADDLE = CONT_LINE[:7] + [(11.0, -12.0), (13.0, -18.0), (16.0, -22.0),
                               (19.0, -22.0)]


def _cont_along(tail_tip=-29.0, head_end=15.0):
    def along(x):
        if x < tail_tip:
            return max(0.55, 1.0 - (tail_tip - x) / 4.0)
        if x > head_end:
            return max(0.4, 1.0 - (x - head_end) / 4.0)
        return 1.0
    return along


def cv1_smooth():
    """One even continuous layer, tail → back → nape → crown."""
    p = []
    band(p, CONT_LINE, -29.5, 18.0, -29.0, 11.0, along=_cont_along(),
         dy_cull=-1.5, dy_full=3.5, dy_end=9.0, wmul=1.05, M=340,
         face_guard=True)
    return _sort(p)


def cv2_heavy():
    """One thick continuous blanket — the deepest, fullest merge."""
    p = []
    band(p, CONT_LINE, -29.5, 18.0, -30.0, 12.0, along=_cont_along(),
         dy_cull=-1.5, dy_full=5.0, dy_end=11.0, wmul=1.3, M=380,
         face_guard=True)
    return _sort(p)


def cv3_bridge():
    """Keep the chosen back + crown shapes, but add a NAPE BRIDGE so
    they connect (subtle seam, mostly the shipped look)."""
    p = v4_chosen()
    # bridge band over the nape, joining shoulder→crown
    band(p, [(6.0, -9.0), (9.0, -13.0), (12.0, -18.0), (15.0, -21.0)],
         5.0, 15.0, -24.0, -7.0,
         along=lambda x: 1.0, dy_cull=-1.0, dy_full=3.0, dy_end=7.0,
         wmul=1.0, M=90, seed=500, face_guard=True)
    return _sort(p)


def cv4_high_arc():
    """Continuous, with the connection arcing HIGH over the neck —
    snow piled up bridging at the top."""
    p = []
    band(p, CONT_HIGH, -29.5, 19.0, -30.0, 11.0,
         along=_cont_along(head_end=16.0),
         dy_cull=-1.5, dy_full=4.0, dy_end=10.0, wmul=1.15, M=360,
         face_guard=True)
    return _sort(p)


def cv5_low_saddle():
    """Continuous, but the bridge follows the neck dip closely — a
    low saddle of snow draped from back to head."""
    p = []
    band(p, CONT_SADDLE, -29.5, 19.0, -28.0, 11.0,
         along=_cont_along(head_end=16.0),
         dy_cull=-1.5, dy_full=3.0, dy_end=8.0, wmul=1.0, M=320,
         face_guard=True)
    return _sort(p)


VARIANTS = [
    ("1  CONTINUOUS smooth",  cv1_smooth),
    ("2  CONTINUOUS heavy",   cv2_heavy),
    ("3  BRIDGE (chosen+join)", cv3_bridge),
    ("4  HIGH-ARC bridge",    cv4_high_arc),
    ("5  LOW-SADDLE drape",   cv5_low_saddle),
    ("0  CURRENT (gap)",      v4_chosen),
]


def render_pip(pool, load, zoom):
    if pool is None:
        E._SNOW_POOL = E._build_snow_pool()
    else:
        E._SNOW_POOL = pool
    b = Bird()
    b.x = 34
    b.y = 32
    b.vy = 0
    b.snow_load = load
    cell = pygame.Surface((68, 64), pygame.SRCALPHA)
    b.draw(cell, 0, 0)
    return pygame.transform.scale(cell, (68 * zoom, 64 * zoom))


def main():
    cols, rows = 3, 2
    Z = 6
    pw, ph = 68 * Z, 64 * Z
    margin, label_h = 14, 26
    sheet_w = pw * cols + margin * (cols + 1)
    sheet_h = (ph + label_h) * rows + margin * (rows + 1)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((40, 56, 78))
    font = pygame.font.SysFont("Arial", 15, bold=True)

    for i, (label, fn) in enumerate(VARIANTS):
        pool = fn() if fn else None
        full = render_pip(pool, 0.95, Z)
        inset = render_pip(pool, 0.5, 2)        # small mid-load build
        c, r = i % cols, i // cols
        x = margin + c * (pw + margin)
        y = margin + r * (ph + label_h + margin)
        pygame.draw.rect(sheet, (70, 90, 120), (x - 2, y - 2, pw + 4, ph + 4), 2)
        sheet.blit(full, (x, y))
        pygame.draw.rect(sheet, (220, 235, 255),
                         (x + 6, y + 6, inset.get_width() + 2,
                          inset.get_height() + 2), 1)
        sheet.blit(inset, (x + 7, y + 7))
        sheet.blit(font.render(label, True, (240, 246, 255)),
                   (x + (pw - font.size(label)[0]) // 2, y + ph + 5))

    out = os.path.join(OUT_DIR, "connect_sheet.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
