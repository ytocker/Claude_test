"""BASEBALL — white sphere with the two red curved stitch seams.

The identity is white + the red STITCHING: two facing curved seams with little
red stitch ticks. It stays distinct from the soccer ball (which is white with
BLACK panels) because here the marks are thin RED curves, not black blocks.

22px read tradeoffs (WHY): the two seams are parametric curves bowing apart down
the ball ("( )"), drawn as a red line with short perpendicular stitch ticks — a
fussy stitch count vanishes, so a few bold ticks per seam carry the "stitched"
read. Volume is baked like the other balls (outline, light->shade body, upper-
left highlight, lower-right shade). A cool keyline rim is the NIGHT lifeline.
"""
import math
import pygame

WHITE = (244, 242, 236)        # shell white — the bright body
WHITE_HI = (255, 255, 255)     # upper-left specular
SHADE = (206, 202, 192)        # lower-right shade
SHADE2 = (176, 172, 162)       # deep rim shade
STITCH = (210, 58, 48)         # red stitching — the signature
STITCH_D = (162, 38, 32)       # darker red for the seam line under the ticks
OUTLINE = (42, 38, 32)         # dark, drawn first + inflated: day read
KEYLINE = (150, 196, 232)      # cool rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = cy = S // 2
    R = 16

    pygame.draw.circle(surf, OUTLINE, (cx, cy), R + 2)
    pygame.draw.circle(surf, SHADE2, (cx, cy), R)
    pygame.draw.circle(surf, SHADE, (cx - 1, cy - 1), R - 1)
    pygame.draw.circle(surf, WHITE, (cx - 3, cy - 3), R - 3)

    seams = pygame.Surface((S, S), pygame.SRCALPHA)

    def _seam(side):
        # A vertical curve bowing toward `side` (-1 left, +1 right). Returns the
        # point list + the local tangent-normal for stitch ticks.
        off = side * R * 0.16
        bow = side * R * 0.62
        pts = []
        for i in range(0, 25):
            t = i / 24.0
            y = cy - (R - 2) + t * 2 * (R - 2)
            x = cx + off + bow * math.sin(t * math.pi)
            pts.append((x, y))
        return pts

    for side in (-1, 1):
        pts = _seam(side)
        pygame.draw.lines(seams, STITCH_D, False, pts, 2)
        # Stitch ticks: short perpendicular dashes along the seam, alternating.
        for j in range(2, len(pts) - 2, 3):
            x, y = pts[j]
            px, py = pts[j - 1]
            dx, dy = x - px, y - py
            n = math.hypot(dx, dy) or 1
            nx, ny = -dy / n, dx / n           # normal
            k = 2.2 * (1 if (j // 3) % 2 == 0 else -1)
            pygame.draw.line(seams, STITCH,
                             (x - nx * k, y - ny * k),
                             (x + nx * k * 0.3, y + ny * k * 0.3), 1)

    smask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255), (cx, cy), R - 2)
    seams.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(seams, (0, 0))

    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shade, (60, 56, 48, 70), (cx + 5, cy + 6), R)
    shmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shmask, (255, 255, 255, 255), (cx, cy), R - 1)
    shade.blit(shmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))

    hi = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hi, (255, 255, 255, 150), (cx - 5, cy - 6), 4)
    pygame.draw.circle(hi, WHITE_HI, (cx - 6, cy - 7), 2)
    hmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hmask, (255, 255, 255, 255), (cx, cy), R - 2)
    hi.blit(hmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hi, (0, 0))

    pygame.draw.circle(surf, KEYLINE, (cx, cy), R, 1)
    return pygame.transform.smoothscale(surf, (22, 22))
