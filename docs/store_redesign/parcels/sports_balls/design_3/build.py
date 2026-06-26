"""TENNIS BALL — neon yellow-green sphere with the white curved seam.

The identity is the neon tennis colour plus the single signature white SEAM that
wavers down the ball like a stretched S. The colour alone reads "tennis", and the
white curve confirms it; both survive grayscale because the white seam is the
brightest mark on a mid-value body.

22px read tradeoffs (WHY): the seam is built as a wavy vertical polyline (a sine
down the ball) rather than fussy facet curves, so one bold committed S-curve
carries the read. A 1px darker green shadow rides under the white so the seam
reads recessed. Volume is baked like the other balls (outline, light->shade body,
upper-left highlight, lower-right shade). A cool keyline rim is the NIGHT lifeline.
"""
import math
import pygame

YEL = (206, 226, 70)           # neon tennis yellow-green — the body
YEL_HI = (230, 244, 120)       # lit upper-left
YEL_SH = (158, 184, 50)        # lower-right shade
YEL_SH2 = (120, 144, 36)       # deep rim shade
SEAM = (244, 247, 232)         # white seam — the signature curve
SEAM_SH = (120, 144, 36)       # darker green shadow under the seam
OUTLINE = (58, 68, 20)         # dark olive, drawn first + inflated: day read
KEYLINE = (210, 236, 150)      # cool rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = cy = S // 2
    R = 16

    pygame.draw.circle(surf, OUTLINE, (cx, cy), R + 2)
    pygame.draw.circle(surf, YEL_SH2, (cx, cy), R)
    pygame.draw.circle(surf, YEL_SH, (cx - 1, cy - 1), R - 1)
    pygame.draw.circle(surf, YEL, (cx - 3, cy - 3), R - 3)

    # White seam: a wavy vertical line (sine down the ball), masked to the sphere.
    seams = pygame.Surface((S, S), pygame.SRCALPHA)
    amp = R * 0.62
    pts = []
    for i in range(0, 41):
        t = i / 40.0                      # 0..1 top->bottom
        y = cy - R + t * 2 * R
        x = cx + amp * math.sin(t * math.pi * 2 - math.pi / 2)
        pts.append((x, y))
    pygame.draw.lines(seams, SEAM_SH, False, [(p[0] + 1, p[1] + 1) for p in pts], 3)
    pygame.draw.lines(seams, SEAM, False, pts, 3)
    smask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255), (cx, cy), R - 2)
    seams.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(seams, (0, 0))

    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shade, (40, 50, 12, 70), (cx + 5, cy + 6), R)
    shmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shmask, (255, 255, 255, 255), (cx, cy), R - 1)
    shade.blit(shmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))

    hi = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hi, (240, 250, 180, 150), (cx - 5, cy - 6), 4)
    pygame.draw.circle(hi, YEL_HI, (cx - 6, cy - 7), 2)
    hmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hmask, (255, 255, 255, 255), (cx, cy), R - 2)
    hi.blit(hmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hi, (0, 0))

    pygame.draw.circle(surf, KEYLINE, (cx, cy), R, 1)
    return pygame.transform.smoothscale(surf, (22, 22))
