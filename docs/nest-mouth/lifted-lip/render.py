"""lifted-lip: bird perched 2px higher, 2px lit front lip selling the near edge.

Correct occlusion; the brighter, thicker lip is the strongest depth cue —
the bird's chest clearly disappears behind it.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import _model3d as m3
import pygame

def _interior(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.ellipse(surf, (20, 13, 5), (rx, ry, rw, rh))

def draw_slot(surf, cy, alive):
    m3.draw_crib(surf, cy, alive, _interior, bird_dy=-2, lip_px=2,
                 lip_color=nb._NEST_STICK_HI)

if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/lifted-lip/pair.png')
