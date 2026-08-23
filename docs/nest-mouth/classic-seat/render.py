"""classic-seat: the pure occlusion fix — nothing else changes.

Black opening, bird at today's height, but the whole front wall and lip now
correctly occlude the bird's lower body, and no course crosses the opening.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import _model3d as m3
import pygame

def _interior(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, ry, rw, rh))

def draw_slot(surf, cy, alive):
    m3.draw_crib(surf, cy, alive, _interior)

if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/classic-seat/pair.png')
