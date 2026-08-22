"""scoop-front: the front wall's top edge scoops deeper in the middle.

The lip curve dips 1.8x lower at the centre — like a worn entry notch —
so the bird's chest shows further down before the wall takes over.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import _model3d as m3
import pygame

def _interior(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, ry, rw, rh))
    # The scooped region below the oval's bottom arc opens onto the interior.
    for x in range(rx, rx + rw + 1):
        y0 = m3.lip_y(x, ecx, ecy, ra, rb, 1.0)
        y1 = m3.lip_y(x, ecx, ecy, ra, rb, 1.8)
        if y0 is None: continue
        for y in range(int(y0), int(y1) + 1):
            surf.set_at((x, y), (0, 0, 0))

def draw_slot(surf, cy, alive):
    m3.draw_crib(surf, cy, alive, _interior, lip_scale=1.8)

if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/scoop-front/pair.png')
