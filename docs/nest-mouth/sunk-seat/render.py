"""sunk-seat: the bird sits 4px deeper — only head and shoulders above the lip.

Same correct occlusion as classic-seat; the deeper seat makes the containment
unmistakable: most of the body is swallowed by the cup.
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
    m3.draw_crib(surf, cy, alive, _interior, bird_dy=4)

if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/sunk-seat/pair.png')
