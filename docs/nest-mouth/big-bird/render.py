"""big-bird: same crib, 25% larger parrot — the bird dominates the nest.

Pure scale change: the sprite grows from 34px to 42px tall, so head, chest
and wings tower over the unchanged crib.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import _model3d as m3
import pygame

_BH = 42
_BW = max(1, int(nb.BW * _BH / nb.BH))
_BIG = pygame.transform.smoothscale(nb.BIRD, (_BW, _BH))

def _interior(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, ry, rw, rh))

def draw_slot(surf, cy, alive):
    m3.draw_crib(surf, cy, alive, _interior, bird_img=_BIG)

if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/big-bird/pair.png')
