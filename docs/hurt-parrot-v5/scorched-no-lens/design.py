"""
`scorched-no-lens` — scorched-afterburn variant, one lens missing.

Built on scorched-afterburn: burnt tail fan, soot patches with ember rims — but
the left aviator lens is gone. The gold ring frame remains (it warped, the lens
popped out), and Pip's own bare eye shows through the hollow opening. The eye is
the exact same one the store's NO SHADES skin (skin_shades_none) reveals: creamy
facial patch, faint feather streaks, dark maroon iris, near-black pupil ring, and
a single white glint. Nothing custom or horror-adjacent — just the bird looking
back through an empty frame.

The right lens stays exactly as in scorched-afterburn — intact, tinted, glinting
— so the asymmetry is the whole read. One eye hidden in shadow, one looking
straight back at you.
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

SOOT      = ( 80,  45,  28)
SOOT_ASH  = (118,  78,  52)
EMBER     = (255, 150,  60)
CHAR      = ( 58,  36,  28)

TAIL_COLORS  = ((200,  30,  40), (240,  95,  40), (255, 160,  55), (255, 220,  80))
FEATHER_BURN = (0.65, 0.10, 0.80, 0.40)
_LONGEST_FEATHER = FEATHER_BURN.index(min(FEATHER_BURN))

_SOOT_PATCHES = (
    [(18, 27), (21, 22), (27, 21), (29, 26), (24, 30), (18, 32)],
    [(18, 37), (23, 34), (27, 37), (25, 42), (19, 43), (18, 41)],
)


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
    tl, tr, br, bl = pts
    tip_t = _lerp(tl, tr, burn_frac)
    tip_b = _lerp(bl, br, burn_frac)
    if add_notch:
        dx, dy = tr[0] - tl[0], tr[1] - tl[1]
        L = max(1e-3, math.hypot(dx, dy))
        ax, ay = dx / L, dy / L
        nc = _lerp(tip_b, tip_t, 0.67)
        ex, ey = tip_t[0] - tip_b[0], tip_t[1] - tip_b[1]
        eL = max(1e-3, math.hypot(ex, ey))
        ex, ey = ex / eL, ey / eL
        n_left  = (nc[0] - ex * 2.5, nc[1] - ey * 2.5)
        n_right = (nc[0] + ex * 2.5, nc[1] + ey * 2.5)
        n_deep  = (nc[0] + ax * 4,   nc[1] + ay * 4)
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
    d.line(w, BIRD_WING_D,    (26, 25), (42, 18), 2)
    d.line(w, BIRD_WING_D,    (28, 30), (44, 25), 2)
    d.line(w, BIRD_WING_D,    (30, 34), (46, 32), 2)
    d.line(w, (170, 210, 255), (25, 25), (41, 15), 1)
    return pygame.transform.rotate(w, angle_deg)


def _draw_soot(surf):
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
    for poly in _SOOT_PATCHES:
        rim = [(x - 2, y) for x, y in poly]
        d.polygon(layer, EMBER, rim)
        d.polygon(layer, SOOT, poly)
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        d.polygon(layer, SOOT_ASH,
                  [(cx + (x - cx) * 0.5, cy + (y - cy) * 0.5) for x, y in poly])
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            if layer.get_at((x, y))[3] > 8 and surf.get_at((x, y))[3] > 8:
                surf.set_at((x, y), layer.get_at((x, y)))


def _draw_sunglasses_one_lens(surf, cx, cy):
    """Right lens intact; left lens ring only — eye drawn through the opening.

    The left gold ring frame is still closed (the lens popped out, the frame
    warped inward slightly). The exposed eye sits at the same centre as the old
    lens: iris (r=4) + pupil (r=2) + single warm glint. No tint layer — the
    fire-lit iris is the only colour inside the ring. The ring is drawn last so
    the gold arc stamps cleanly over the iris edge.
    """
    r = 6
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)
    d = pygame.draw

    # ── right lens: fully intact ─────────────────────────────────────────────
    d.circle(surf, SHADE_FRAME, right, r + 1)
    d.circle(surf, SHADE_BLACK, right, r)
    tint = pygame.Surface((r * 2, r), pygame.SRCALPHA)
    d.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (right[0] - r, right[1] - r + 1))
    d.circle(surf, SHADE_GLINT, (right[0] - 2, right[1] - 3), 2)
    d.circle(surf, (255, 255, 255, 200), (right[0] + 2, right[1] + 1), 1)

    # Brow bar connects both rims as normal.
    d.line(surf, SHADE_FRAME, (left[0] + r, left[1]), (right[0] - r, right[1]), 2)
    d.line(surf, SHADE_FRAME,
           (left[0] - r + 1, left[1] - r + 2), (right[0] + r - 1, right[1] - r + 2), 1)

    # ── left lens: ring only, authentic bare-eye inside ─────────────────────
    # Eye drawn before the gold ring so the rim stamps cleanly over the edge.
    # Identical to parrot._draw_eye / the NO SHADES store skin, offset to lx,ly.
    lx, ly = left
    _aaellipse(surf, (250, 243, 236), (lx, ly), 6, 5)          # facial patch
    d.line(surf, (236, 210, 205), (lx-5, ly-2), (lx+5, ly-2), 1)
    d.line(surf, (236, 210, 205), (lx-5, ly+2), (lx+5, ly+2), 1)
    d.circle(surf, ( 40,  26,  30), (lx+1, ly), 3)             # iris
    d.circle(surf, ( 15,  10,  12), (lx+1, ly), 3, 1)          # pupil ring
    d.circle(surf, (255, 255, 255), (lx, ly-1), 1)             # glint

    # Gold ring stamps over the iris edge — 2 px wide annulus only, no fill.
    d.circle(surf, SHADE_FRAME, left, r + 1, 2)

    return left, r


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

    _draw_sunglasses_one_lens(surf, 50, 20)

    beak = [(55, 21), (61, 24), (58, 28), (52, 26)]
    d.polygon(surf, BIRD_BEAK, beak)
    d.polygon(surf, BIRD_BEAK_D, beak, 1)
    d.line(surf, (255, 230, 150), (55, 22), (59, 24), 1)
    d.line(surf, BIRD_BEAK_D, (52, 24), (58, 25), 1)

    d.line(surf, BIRD_BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BIRD_BEAK_D, (34, 45), (36, 49), 2)

    return surf


if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    raw    = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    frames = [_add_outline(f) for f in raw]

    BG = (8, 8, 20)
    fw, fh = frames[0].get_size()
    strip = pygame.Surface((fw * len(frames), fh))
    strip.fill(BG)
    for i, f in enumerate(frames):
        strip.blit(f, (i * fw, 0))

    out_path = os.path.join(OUT_DIR, "round_2.png")
    pygame.image.save(strip, out_path)
    print(f"Saved {strip.get_width()}x{strip.get_height()} -> {out_path}")
