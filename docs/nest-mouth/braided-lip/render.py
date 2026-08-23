"""braided-lip: fat rolled twig lip swallows the oval tips; small central opening.

The thin 2px ring becomes a 3-4px braided band (alternating strand colours
around the oval). The black mouth shrinks to a small almond in the middle, so
no black wedges ever reach the tips. The lip is drawn in front of the bird —
the parrot sits tucked inside the roll.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import pygame

LIP_IN = 0.55   # inner edge of the lip band (normalized elliptical radius)

_TOP_STRANDS = [nb._NEST_TWIG_BRIGHT, nb._NEST_STICK_HI, nb._NEST_COURSE_TOP]
_BOT_STRANDS = [nb._NEST_TWIG_MID, nb._NEST_STICK_COL, nb._NEST_TWIG_DARK]


def _lip_color(px, py, ecx, ecy, ra, rb):
    ang = math.atan2((py - ecy) / rb, (px - ecx) / ra)
    idx = int(((ang + math.pi) / (2 * math.pi)) * 22) % 3
    return (_TOP_STRANDS if py < ecy else _BOT_STRANDS)[idx]


def _draw_lip(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    for y in range(ry, ry + rh + 1):
        for x in range(rx - 1, rx + rw + 2):
            t = nb.t_ell(x, y, ecx, ecy, ra, rb)
            # The second condition swallows fill pixels pygame's ellipse rasterizer
            # puts outside the mathematical oval at the flat top/bottom rows.
            if LIP_IN <= t <= 1.04 or (LIP_IN <= t < 1.6 and surf.get_at((x, y))[:3] == (0, 0, 0)):
                surf.set_at((x, y), _lip_color(x, y, ecx, ecy, ra, rb))


def draw_slot(surf, cy, alive):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, ry, rw, rh))
    _draw_lip(surf, cy)
    nb.sticks_weave01(surf, cy)
    if alive:
        surf.blit(nb.BIRD, (nb.CX - nb.BW // 2, cy - nb.BH // 2 + 5))
    else:
        sil, bx, by = nb.make_black_sil(cy)
        surf.blit(sil, (bx, by))
    # Lip rolls in front of whatever sits in the cup.
    _draw_lip(surf, cy)
    nb.front_chrome(surf, cy)


if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/braided-lip/pair.png')
