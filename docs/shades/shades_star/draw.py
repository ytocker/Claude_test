"""STAR SHADES — novelty festival party glasses with 5-point STAR lenses.

The star silhouette is the entire read, so the points are kept deliberately
stubby (inner radius ~0.42*outer, not the thin ~0.38 of a "true" rendered
star) and the fill stays a solid tinted polygon: a slender pointy star fills
to nothing and vanishes at the in-game size (eye_w=22), but a bold stubby one
keeps its 5-point silhouette even when each point is only a few pixels.

Every dimension scales off `eye_w` so the same code is a clean glam product
shot at eye_w=96 and a legible overlay over Pip's scarlet head at eye_w=22.
Like the round-shades idiom, the metal "frame" is a slightly-larger star
drawn BEHIND the glass (an outset disc-equivalent) rather than a 1px stroke,
because a stroked star outline stipples and breaks at tiny radii while a
filled backing star is always solid metal. The bridge sits behind both
lenses so the lens polygons overlap it cleanly.
"""
import math
import pygame

_FRAME   = (224, 228, 236)          # cool chrome metal frame
_FRAME_H = (255, 255, 255)          # top catch-light on the chrome
_FRAME_D = (150, 158, 172)          # underside / shadow side of the frame
_TINT_T  = (96, 196, 255)           # electric-blue top of the glass
_TINT_B  = (24, 110, 210)           # deeper blue floor (vertical fade)
_GLINT   = (255, 255, 255)
# Gold alternate kept for an easy re-skin without touching geometry.
_GOLD_T  = (255, 226, 120)
_GOLD_B  = (224, 162, 40)


def _star_points(cx, cy, r_out, r_in, rot=-math.pi / 2):
    """10 vertices of a 5-point star centred at (cx,cy). `rot` puts a point
    straight up (-90deg) so the star reads upright in side profile."""
    pts = []
    for i in range(10):
        ang = rot + i * math.pi / 5
        rad = r_out if i % 2 == 0 else r_in
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    return pts


def _tinted_star(r_out, r_in, top, bot, alpha):
    """Star-clipped glass: a vertical top→bot gradient masked to the star
    polygon. The vertical fade fakes curved tinted glass on the flat lens."""
    size = r_out * 2 + 2
    g = pygame.Surface((size, size), pygame.SRCALPHA)
    span = max(1, size - 1)
    for yy in range(size):
        t = yy / span
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t), alpha)
        pygame.draw.line(g, c, (0, yy), (size, yy))
    clip = pygame.Surface((size, size), pygame.SRCALPHA)
    c2 = r_out + 1
    pygame.draw.polygon(clip, (255, 255, 255, 255),
                        _star_points(c2, c2, r_out, r_in))
    g.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return g, c2


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    r_out = max(5, int(eye_w * 0.30))
    r_in  = max(2, int(r_out * 0.42))
    sep   = max(6, int(eye_w * 0.46))
    # Frame thickness as an outset of the backing star; min 1px so it never
    # disappears, scaling up to a chunky chrome rim on the product shot.
    fw    = max(1, int(eye_w * 0.05))
    near  = (cx + f * (sep // 2), cy)
    far   = (cx - f * (sep // 2), cy)

    # Bridge BEHIND the lenses so the lens stars overlap it; the lower pass is
    # the chrome catch-light beneath the bridge wire.
    by  = cy - max(1, int(r_out * 0.10))
    bx0 = far[0] + f * int(r_in * 1.1)
    bx1 = near[0] - f * int(r_in * 1.1)
    pygame.draw.line(surf, _FRAME_D, (bx0, by + 1), (bx1, by + 1), max(2, fw))
    pygame.draw.line(surf, _FRAME, (bx0, by), (bx1, by), max(1, fw))

    # Temple arm toward the ear (-facing): straight metal wire with a shadow
    # underline so it reads off the scarlet head.
    ex = far[0] - f * (r_out + max(2, int(eye_w * 0.30)))
    ey = cy - max(1, int(eye_w * 0.05))
    hook = (far[0] - f * int(r_out * 0.5), cy)
    pygame.draw.line(surf, _FRAME_D, hook, (ex, ey + 1), max(2, fw))
    pygame.draw.line(surf, _FRAME, hook, (ex, ey), max(1, fw))

    for (lx, ly) in (far, near):
        # Solid star frame = outset chrome star, then the tinted glass star
        # inset by the frame width — always solid metal even at eye_w=22.
        f_out = r_out + fw
        f_in  = r_in + max(1, fw // 2)
        pygame.draw.polygon(surf, _FRAME_D,
                            _star_points(lx, ly + 1, f_out, f_in))
        pygame.draw.polygon(surf, _FRAME,
                            _star_points(lx, ly, f_out, f_in))

        glass, c2 = _tinted_star(r_out, r_in, _TINT_T, _TINT_B, 215)
        surf.blit(glass, (lx - c2, ly - c2))

        # Chrome highlight along the two upper-left point edges so the metal
        # frame catches light and the star silhouette stays crisp.
        sp = _star_points(lx, ly, f_out, f_in)
        if max(2, fw) >= 2:
            pygame.draw.lines(surf, _FRAME_H, False, [sp[8], sp[9], sp[0]],
                              max(1, fw - 1))

    # Single bright glint inside the near lens body — sells the glossy glass.
    pygame.draw.circle(surf, _GLINT,
                       (near[0] - f * (r_in // 2), cy - r_in // 2),
                       max(1, int(eye_w * 0.05)))
