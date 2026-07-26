"""
`scorched-afterburn` — hurt-parrot concept exploration (standalone, not wired in).

Elemental damage: the bird came through the fire. This concept owns the *tail*
— no other hurt concept touches it — so the injury is legible from the
silhouette alone, before any surface detail resolves. Each feather burns back
by a different fraction, producing a staggered fan whose ragged silhouette reads
immediately as fire damage rather than a smaller healthy tail.

Everything else is a surface read carried by *value contrast*, not by hue:
soot patches are a warm grey-brown that would vanish against BIRD_RED on its
own, so each one gets a 1-2 px ember rim on its tail-facing edge — the bright
lip is the only part that survives the 1x downscale, and it also tells the
direction the fire came from. Ember orange is rationed to those rims; a mass
of ember-gold on the body would read as a KFC/coin pickup FX rather than
damage.
"""
import math
import os, sys

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()

SPRITE_W, SPRITE_H = 64, 60
_HURT_ANGLES = (10, -5, -20, -35)

# Base macaw palette, mirrored from game/draw.py so this sheet stands alone.
BIRD_RED    = (240,  55,  55)
BIRD_RED_D  = (170,  25,  25)
BIRD_WING   = ( 40, 100, 255)
BIRD_WING_D = ( 20,  55, 180)
BIRD_TIP    = ( 50, 220, 100)
BIRD_BELLY  = (255, 170,  50)
BIRD_BEAK   = (255, 185,   0)
BIRD_BEAK_D = (200, 130,   0)

SHADE_BLACK = ( 15,  15,  25)
SHADE_FRAME = (255, 200,  50)
SHADE_GLINT = (255, 255, 255)
SHADE_TINT  = ( 35,  55,  90)

SOOT       = ( 80,  45,  28)   # warm grey-brown burn centre
SOOT_ASH   = (118,  78,  52)   # lifted ash heart inside a patch
EMBER      = (255, 150,  60)   # 1-2 px leading edge, rear/tail-facing side
CHAR       = ( 58,  36,  28)   # burnt-back tail tips
LID_COLOR  = (170,  25,  25)   # squint lid — bright enough to read against black lens

# The healthy bird's own four-feather fan is kept intact so the only thing that
# changed about the tail is the burn. Feathers burn by different fractions so
# the staggered tips read as fire damage; a uniform shortening reads as a
# smaller healthy tail.
TAIL_COLORS  = ((200,  30,  40), (240,  95,  40), (255, 160,  55), (255, 220,  80))
FEATHER_BURN = (0.65, 0.10, 0.80, 0.40)   # fraction burnt away per feather — stagger ≥8px

# Index of the least-burnt (longest) feather — the notch lives here only.
_LONGEST_FEATHER = FEATHER_BURN.index(min(FEATHER_BURN))


def _aaellipse(surf, color, center, rx, ry):
    cx, cy = center
    pygame.draw.ellipse(surf, color, (cx - rx, cy - ry, rx * 2, ry * 2))


def _add_outline(src, outline_color=(20, 12, 18, 220)):
    pad = 2
    w, h = src.get_size()
    mask = pygame.mask.from_surface(src, threshold=8)
    sil  = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    out  = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == dy == 0:
                continue
            out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _burnt_feather(pts, burn_frac, add_notch=False):
    """Return a feather polygon burnt back by burn_frac with optional notch.

    Tip corners shift toward their root corners along the feather axis.
    On the longest feather only, a single deep notch (≥5px wide, 4px deep) is
    cut into the outer third of the tip edge — one cut reads as crumbled
    material; seven cuts at ~1.65px pitch all bridge shut under the 2px outline.
    """
    tl, tr, br, bl = pts
    tip_t = _lerp(tl, tr, burn_frac)
    tip_b = _lerp(bl, br, burn_frac)

    if add_notch:
        # Inward axis from tip toward root, for notch depth direction.
        dx, dy = tr[0] - tl[0], tr[1] - tl[1]
        L = max(1e-3, math.hypot(dx, dy))
        ax, ay = dx / L, dy / L

        # Notch center at outer third of tip edge (near tip_t).
        nc = _lerp(tip_b, tip_t, 0.67)

        # Unit vector along the tip edge for notch half-width placement.
        ex, ey = tip_t[0] - tip_b[0], tip_t[1] - tip_b[1]
        eL = max(1e-3, math.hypot(ex, ey))
        ex, ey = ex / eL, ey / eL

        n_left = (nc[0] - ex * 2.5, nc[1] - ey * 2.5)
        n_right = (nc[0] + ex * 2.5, nc[1] + ey * 2.5)
        # Notch bites 4px inward (toward root) so it survives outline dilation.
        n_deep = (nc[0] + ax * 4, nc[1] + ay * 4)

        edge = [tip_b, n_left, n_deep, n_right, tip_t]
    else:
        edge = [tip_b, tip_t]

    return [*edge, tr, br]


def _draw_tail(surf):
    for i, (c, burn) in enumerate(zip(TAIL_COLORS, FEATHER_BURN)):
        pts = [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2),
        ]
        poly = _burnt_feather(pts, burn, add_notch=(i == _LONGEST_FEATHER))
        pygame.draw.polygon(surf, c, poly)
        # Char as a 1px open polyline on the tip edge only. A 2px closed polygon
        # would dilate under the outline pass and bridge the notch shut; an open
        # stroke stays narrow and keeps the notch geometry visible.
        tip_edge = poly[:len(poly) - 2]
        if len(tip_edge) >= 2:
            pygame.draw.lines(surf, CHAR, False, tip_edge, 1)
    pygame.draw.line(surf, BIRD_RED_D, (7, 27), (18, 31), 1)
    pygame.draw.line(surf, BIRD_RED_D, (9, 33), (20, 35), 1)


def _build_wing(angle_deg):
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    d = pygame.draw
    d.polygon(w, (0, 0, 0, 110), [(24, 26), (46, 14), (50, 30), (34, 44), (18, 40)])
    d.polygon(w, BIRD_WING,      [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)])
    d.polygon(w, BIRD_WING_D,    [(24, 24), (32, 42), (18, 36)])
    d.polygon(w, BIRD_TIP,       [(44, 13), (50, 18), (48, 28)])
    d.polygon(w, (255, 200, 60), [(42, 18), (48, 22), (46, 28), (40, 24)])
    d.line(w, BIRD_WING_D,   (26, 25), (42, 18), 2)
    d.line(w, BIRD_WING_D,   (28, 30), (44, 25), 2)
    d.line(w, BIRD_WING_D,   (30, 34), (46, 32), 2)
    d.line(w, (170, 210, 255), (25, 25), (41, 15), 1)
    return pygame.transform.rotate(w, angle_deg)


# Two body patches only, all vertices x≥18 so soot stays on chest/body and
# cannot repaint the tail fan. Ember crescent is made by stamping each patch
# 2px toward the tail first; whatever the soot body doesn't cover is a ≥12px
# crescent on the rear-facing side, showing where the fire came from.
_SOOT_PATCHES = (
    [(18, 27), (21, 22), (27, 21), (29, 26), (24, 30), (18, 32)],
    [(18, 37), (23, 34), (27, 37), (25, 42), (19, 43), (18, 41)],
)


def _draw_soot(surf):
    """Burn patches composited over the wing and clipped to the silhouette.

    Under the wing they vanished on the upstroke frames — and fire that caught
    the breast would have caught the coverts on the way past anyway, so
    carrying the soot across the wing is both the truthful read and the only
    one that holds for all four frames.

    The ember crescent is made by stamping the same polygon 2 px toward the
    tail first: whatever the soot body does not cover is left as a crescent on
    the rear-facing side, which is where the fire came from.
    """
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
    for poly in _SOOT_PATCHES:
        rim = [(x - 2, y) for x, y in poly]
        d.polygon(layer, EMBER, rim)
        d.polygon(layer, SOOT, poly)
        # A smaller inner shape keeps the patch from reading as one flat decal.
        # Ash is drawn *lighter* than the burn, not darker: a near-black heart
        # punches a hole in the bird's value structure, while a grey heart
        # ringed by darker char still reads as depth and costs nothing.
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        d.polygon(layer, SOOT_ASH,
                  [(cx + (x - cx) * 0.5, cy + (y - cy) * 0.5) for x, y in poly])

    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            if layer.get_at((x, y))[3] > 8 and surf.get_at((x, y))[3] > 8:
                surf.set_at((x, y), layer.get_at((x, y)))


def _draw_sunglasses(surf, cx, cy):
    r = 6
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)
    d = pygame.draw
    d.circle(surf, SHADE_FRAME, left, r + 1)
    d.circle(surf, SHADE_FRAME, right, r + 1)
    d.circle(surf, SHADE_BLACK, left, r)
    d.circle(surf, SHADE_BLACK, right, r)
    tint = pygame.Surface((r * 2, r), pygame.SRCALPHA)
    d.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (left[0] - r, left[1] - r + 1))
    surf.blit(tint, (right[0] - r, right[1] - r + 1))
    d.circle(surf, SHADE_GLINT, (right[0] - 2, right[1] - 3), 2)
    d.circle(surf, (255, 255, 255, 200), (right[0] + 2, right[1] + 1), 1)
    d.line(surf, SHADE_FRAME, (left[0] + r, left[1]), (right[0] - r, right[1]), 2)
    d.line(surf, SHADE_FRAME,
           (left[0] - r + 1, left[1] - r + 2), (right[0] + r - 1, right[1] - r + 2), 1)
    return left, r


def _draw_squint(surf, center, r):
    """Heavy lid dropped over the top ~40% of the rear lens, drawn after the
    sunglasses so it paints over the gold arc.

    Killing the gold rim arc is what makes the eye read as clamped shut; a lid
    drawn before the arc leaves the shiny rim above it and the whole thing reads
    as an open eye with a tint. LID_COLOR=(170,25,25) has lum≈68 vs the black
    lens lum≈16 — it's a legible dark-red contrast rather than an invisible
    near-black smear.
    """
    cx, cy = center
    size = (r + 2) * 2
    lid = pygame.Surface((size, size), pygame.SRCALPHA)
    lc = r + 2
    top = lc - r
    pygame.draw.polygon(lid, LID_COLOR, [
        (0, top), (size, top),
        (size, top + int(r * 2 * 0.60)), (0, top + int(r * 2 * 0.34)),
    ])
    # Clip the polygon to the lens circle so the lid has a clean arc lower edge.
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (lc, lc), r)
    lid.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(lid, (cx - lc, cy - lc))
    # A lash line one value up from the body keeps the lid edge readable.
    pygame.draw.line(surf, (90, 22, 18),
                     (cx - r + 1, cy - r + int(r * 2 * 0.34) - 1),
                     (cx + r - 1, cy - r + int(r * 2 * 0.57) - 1), 1)


def _build_hurt_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d = pygame.draw

    _draw_tail(surf)

    _aaellipse(surf, (120, 20, 25),   (34, 35), 19, 14)
    _aaellipse(surf, BIRD_RED,        (32, 32), 19, 14)
    _aaellipse(surf, (255, 100, 100), (30, 29), 13,  8)
    _aaellipse(surf, BIRD_BELLY,      (28, 38), 12,  6)
    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    d.ellipse(sheen, (255, 230, 230, 160), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    _draw_soot(surf)

    _aaellipse(surf, (150, 15, 20),   (48, 23), 12, 11)
    _aaellipse(surf, BIRD_RED,        (47, 21), 12, 11)
    _aaellipse(surf, (255, 130, 130), (44, 24),  4,  3)
    _aaellipse(surf, (255, 170, 170), (46, 16),  7,  3)

    # Squint drawn after sunglasses so the lid paints over the gold rim arc,
    # which is what makes the eye read as shut rather than just tinted.
    left, r = _draw_sunglasses(surf, 50, 20)
    _draw_squint(surf, left, r)

    beak = [(55, 21), (61, 24), (58, 28), (52, 26)]
    d.polygon(surf, BIRD_BEAK, beak)
    d.polygon(surf, BIRD_BEAK_D, beak, 1)
    d.line(surf, (255, 230, 150), (55, 22), (59, 24), 1)
    d.line(surf, BIRD_BEAK_D, (52, 24), (58, 25), 1)

    d.line(surf, BIRD_BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BIRD_BEAK_D, (34, 45), (36, 49), 2)

    return surf


def build_frames():
    return [_add_outline(_build_hurt_frame(a)) for a in _HURT_ANGLES]


def _count(frame, pred, x0=0):
    n = 0
    for x in range(x0, frame.get_width()):
        for y in range(frame.get_height()):
            r, g, b, a = frame.get_at((x, y))
            if a > 8 and pred(r, g, b):
                n += 1
    return n


def _tail_extent(frame):
    for x in range(frame.get_width()):
        for y in range(20, 52):
            if frame.get_at((x, y))[3] > 8:
                return x
    return frame.get_width()


def _tip_x_positions(raw_frame):
    """Return the x position of each feather tip for stagger verification."""
    tips = []
    for i, burn in enumerate(FEATHER_BURN):
        tl = (2 + i * 3, 26 + i * 2)
        tr = (14 + i,    24 + i)
        bl = (6 + i * 3, 36 + i * 2)
        br = (20 + i,    30 + i * 2)
        tip_t = _lerp(tl, tr, burn)
        tip_b = _lerp(bl, br, burn)
        tips.append(min(tip_t[0], tip_b[0]))
    return tips


if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    raw    = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    frames = [_add_outline(f) for f in raw]

    # x >= 24 keeps the ember probe off the tail and the orange belly, both of
    # which sit inside a naive R/G threshold.
    for i, f in enumerate(raw):
        soot  = _count(f, lambda r, g, b: r < 120 and g < 80 and b < 90, 12)
        ember = _count(f, lambda r, g, b: r > 200 and 100 < g < 180, 24)
        bright = _count(f, lambda r, g, b: r > 200 and g > 120 and b < 100)
        print(f"frame {i}: soot={soot} (need >=20)  ember_rim={ember} "
              f"(need 30-45)  bright_feather_px={bright}  "
              f"tail_leftmost_x={_tail_extent(f)} (healthy=2)")

    tips = _tip_x_positions(raw[0])
    stagger = max(tips) - min(tips)
    print(f"feather tip x positions: {[round(x,1) for x in tips]}")
    print(f"stagger range: {stagger:.1f}px (need >=8)")
    assert stagger >= 8, f"stagger {stagger:.1f}px < 8px"

    NIGHT = (8, 8, 20)
    fw, fh = frames[0].get_size()
    strip = pygame.Surface((fw * len(frames), fh))
    strip.fill(NIGHT)
    for i, f in enumerate(frames):
        strip.blit(f, (i * fw, 0))

    out_path = os.path.join(OUT_DIR, "round_2.png")
    pygame.image.save(strip, out_path)
    print(f"Saved {strip.get_width()}x{strip.get_height()} -> {out_path}")
