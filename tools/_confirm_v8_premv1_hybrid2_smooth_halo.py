"""Per-pixel replacement for store_cards._alpha_aura.

The stock aura stacks `layers` concentric filled circles, so the composite
alpha jumps at every circle edge — at 24 layers over a ~108-logical-px halo
the rings are ~4.5px apart and clearly readable. This rebuilds the same
cumulative profile analytically (alpha compositing in log space) with each
ring boundary feathered across one layer step, then blits it as a single
RGBA surface: identical colour, identical strength, no visible rings.
"""
import numpy as np
import pygame


def smooth_aura(surf, cx, cy, radius, color, peak=27, layers=15):
    side = radius * 2 + 2
    yy, xx = np.mgrid[0:side, 0:side]
    d = np.hypot(xx - (radius + 1), yy - (radius + 1))

    step = radius / layers
    log_keep = np.zeros((side, side), dtype=np.float64)
    for i in range(layers, 0, -1):
        r_i = int(radius * i / layers)
        a_i = int(peak * (1 - (i - 1) / layers) ** 1.6)
        if r_i <= 0 or a_i <= 0:
            continue
        w = np.clip((r_i - d) / step + 0.5, 0.0, 1.0)
        log_keep += w * np.log1p(-a_i / 255.0)

    alpha = np.rint(255.0 * (1.0 - np.exp(log_keep))).astype(np.uint8)
    g = pygame.Surface((side, side), pygame.SRCALPHA)
    rgb = pygame.surfarray.pixels3d(g)
    rgb[..., 0], rgb[..., 1], rgb[..., 2] = color[0], color[1], color[2]
    del rgb
    pygame.surfarray.pixels_alpha(g)[:, :] = alpha.T
    surf.blit(g, (cx - radius - 1, cy - radius - 1))
