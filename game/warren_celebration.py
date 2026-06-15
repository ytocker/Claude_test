"""Warren roll-result celebration — the chosen design "E".

A high-res jester PRIZE-WHEEL (8 plum/lime wedges, crisp gold rim, three cardinal
gold studs, a cream hub holding the rolled N as the hero) crowned by the staff's
full mini-clown BAUBLE (4-point bell cap + lime belled ruff + grinning face),
seated low so the face touches the round frame. A GHOST roll re-skins the wheel to
a cool cyan/periwinkle. Ported into game/ (no tools/ import) so it ships in both
build targets; warren_demo renders it once per roll and pop-scales the bitmap.
"""
import math

import pygame

from game import hud
from game.draw import _shade_c
from game.pillar_staff import (
    PLUM, PLUM_DK, LIME, LIME_DK, GOLD, GOLD_HI, GOLD_DK, CREAM,
    _mini_clown_face, _marotte_ruff,
)

# Taller-than-wide popup so the tall jester cap clears the top of the canvas.
DW, DH = 264, 360
WHEEL_A, WHEEL_B = PLUM, LIME
WHEEL_A_G, WHEEL_B_G = (120, 220, 210), (150, 174, 255)   # ghost: cool cyan/periwinkle


def _wheel(canvas, c, R, ss, wedges, col_a, col_b, *, spin=0.42, rim=None,
           rim_w=6, cy=None):
    """A radiating two-colour prize-wheel rosette with hairline keylines + an
    optional crisp gold rim. `cy` seats it low so a tall bauble can crown the top."""
    cy = c if cy is None else cy
    step = math.tau / wedges
    for i in range(wedges):
        a0 = spin + i * step
        a1 = a0 + step
        col = col_a if i % 2 == 0 else col_b
        pygame.draw.polygon(canvas, col, [
            (c, cy),
            (c + math.cos(a0) * R, cy + math.sin(a0) * R),
            (c + math.cos(a1) * R, cy + math.sin(a1) * R)])
    for i in range(wedges):
        a = spin + i * step
        pygame.draw.line(canvas, _shade_c(PLUM_DK, -10), (c, cy),
                         (c + math.cos(a) * R, cy + math.sin(a) * R), max(1, ss))
    if rim is not None:
        pygame.draw.circle(canvas, _shade_c(rim, -45), (c, cy), R, max(2, int((rim_w + 2) * ss)))
        pygame.draw.circle(canvas, rim, (c, cy), R, max(2, int(rim_w * ss)))
        pygame.draw.circle(canvas, GOLD_HI, (c, cy), R - int(rim_w * 0.5 * ss), max(1, ss))


def _gold_stud(canvas, cx, cy, r, ss, col=GOLD):
    """A solid domed gold rivet/stud: dark seat + lit dome + a top-left pip — a
    single bold disc that survives the downscale where a belled tip would mud."""
    pygame.draw.circle(canvas, _shade_c(col, -55), (int(cx), int(cy)), int(r))
    pygame.draw.circle(canvas, col, (int(cx), int(cy)), int(r - ss))
    pygame.draw.circle(canvas, GOLD_HI, (int(cx - r * 0.34), int(cy - r * 0.34)),
                       max(1, int(r * 0.3)))


def _num_block(canvas, c, ncy, roll, ss, *, size=88, num_col=CREAM, edge_col=PLUM,
               shadow_a=110, edge_w=5):
    """The hero rolled number — vendored bold font with a soft drop shadow + a
    thick outline ring, the fill re-stamped LAST so the digit counters stay open."""
    nf = hud._font(int(size * ss), True)
    num = nf.render(str(roll), True, num_col)
    edge = nf.render(str(roll), True, edge_col)
    shadow = nf.render(str(roll), True, (0, 0, 0))
    shadow.set_alpha(shadow_a)
    canvas.blit(shadow, shadow.get_rect(center=(c + 3 * ss, ncy + 5 * ss)))
    o = edge_w * ss
    for ang in range(0, 360, 15):
        ox = math.cos(math.radians(ang)) * o
        oy = math.sin(math.radians(ang)) * o
        canvas.blit(edge, edge.get_rect(center=(c + ox, ncy + oy)))
    canvas.blit(num, num.get_rect(center=(c, ncy)))


def _jester_bauble(canvas, cx, hy, hr, ss):
    """The staff's mini-clown bauble head: a 4-point bell-tipped jester CAP, the
    lime belled RUFF, and the grinning FACE. Cap offsets are authored for
    hr = 13*ss, so they scale by u = hr / (13*ss)."""
    u = hr / (13.0 * ss)
    base_y = hy - hr + int(1 * ss)
    span = max(2, int(8 * ss * u))
    for (dx, dy, col) in [(-30, -8, PLUM_DK), (30, -6, PLUM_DK),
                          (-19, -29, LIME_DK), (19, -27, GOLD_DK)]:
        bxp = cx + int(dx * ss * u)
        byp = base_y + int(dy * ss * u)
        tri = [(cx - span, base_y + int(2 * ss)),
               (cx + span, base_y + int(2 * ss)), (bxp, byp)]
        pygame.draw.polygon(canvas, col, tri)
        pygame.draw.polygon(canvas, _shade_c(col, 50),
                            [(cx - span, base_y + int(2 * ss)),
                             (cx, base_y + int(2 * ss)), (bxp, byp)])
        pygame.draw.polygon(canvas, _shade_c(col, -60), tri, max(1, int(1.4 * ss)))
        br = max(2, int(3.4 * ss * u))
        pygame.draw.circle(canvas, GOLD, (int(bxp), int(byp)), br)
        pygame.draw.circle(canvas, GOLD_DK, (int(bxp), int(byp)), br, max(1, int(ss)))
    _marotte_ruff(canvas, cx, hy + hr - int(2 * ss), int(hr * 1.05), ss, LIME, lobes=9)
    _mini_clown_face(canvas, cx, hy, hr, ss, expr="grin")


def render(roll, ghost=False, ss=4, b_hr_ss=28):
    """Render design E into a `DW*ss x DH*ss` SRCALPHA surface. Returns
    (surface, DW, DH); the caller downscales to true size + pop-scales it.
    `b_hr_ss` is the clown-bauble head radius (ss-px) — the face/topper size."""
    hdw, hdh = DW * ss, DH * ss
    cx = hdw // 2
    canvas = pygame.Surface((hdw, hdh), pygame.SRCALPHA)

    R = int(hdw * 0.27)
    wcy = int(hdh * 0.60)
    a_col, b_col = (WHEEL_A_G, WHEEL_B_G) if ghost else (WHEEL_A, WHEEL_B)
    _wheel(canvas, cx, R, ss, 8, a_col, b_col, spin=0.42, rim=GOLD, rim_w=7, cy=wcy)
    # three side/bottom cardinal studs; the TOP one is replaced by the bauble.
    for i in range(1, 4):
        a = i * math.tau / 4 - math.pi / 2
        sx = cx + math.cos(a) * (R + int(2 * ss))
        sy = wcy + math.sin(a) * (R + int(2 * ss))
        _gold_stud(canvas, sx, sy, int(11 * ss), ss)
    # cream hub + hero number, scaled to the wheel.
    hub_r = int(R * 0.62)
    pygame.draw.circle(canvas, PLUM, (cx, wcy), hub_r + int(4 * ss))
    pygame.draw.circle(canvas, GOLD, (cx, wcy), hub_r + int(4 * ss), max(2, int(2 * ss)))
    pygame.draw.circle(canvas, CREAM, (cx, wcy), hub_r)
    pygame.draw.circle(canvas, PLUM, (cx, wcy), hub_r, max(2, int(2 * ss)))
    num_size = max(46, int(96 * R / int(hdw * 0.40)))
    _num_block(canvas, cx, wcy, roll, ss, size=num_size,
               num_col=PLUM, edge_col=CREAM, edge_w=4)
    # the full clown bauble crowns the top, seated so the face touches the rim.
    b_hr = int(b_hr_ss * ss)
    b_hy = (wcy - R) - int(0.95 * b_hr)
    _jester_bauble(canvas, cx, b_hy, b_hr, ss)
    return canvas, DW, DH
