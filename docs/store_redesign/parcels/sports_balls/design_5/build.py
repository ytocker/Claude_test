"""AMERICAN FOOTBALL — brown prolate ball with white laces parcel cosmetic.

The only non-round ball, so it wins on SILHOUETTE: a pointed brown oval. The
identity is that oval + the white LACES across the centre and the white end
STRIPES near each tip. Brown + the lace marks reads "gridiron" at a glance and
the oval keeps it distinct from every round ball at true size.

22px read tradeoffs (WHY): the ball is a horizontal ellipse (pointed ends), with
volume baked the same way as the spheres (dark outline, light->shade body,
upper-left highlight). The laces are a short white bar with a few cross-ticks —
fussy stitching vanishes, so a few bold ticks carry it — flanked by two short
white end stripes. A warm keyline rim is the NIGHT lifeline.
"""
import pygame

BROWN = (138, 84, 42)          # pigskin brown — the body
BROWN_HI = (176, 116, 64)      # lit upper-left
BROWN_SH = (96, 54, 24)        # lower-right shade
BROWN_SH2 = (74, 40, 16)       # deep rim shade
LACE = (242, 238, 226)         # white laces + end stripes — the signature
LACE_SH = (190, 184, 168)      # lace shadow
OUTLINE = (40, 22, 10)         # dark, drawn first + inflated: day read
KEYLINE = (236, 196, 140)      # warm rim — the NIGHT lifeline


def _ell(surf, color, cx, cy, rx, ry):
    pygame.draw.ellipse(surf, color, pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2))


def build(mode="normal") -> pygame.Surface:
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = cy = S // 2
    RX, RY = 17, 11               # prolate: wider than tall, held off the edges

    # Outline (inflated ellipse) for the DAY silhouette read.
    _ell(surf, OUTLINE, cx, cy, RX + 2, RY + 2)
    # Brown body with baked volume (concentric offset ellipses lit up-left).
    _ell(surf, BROWN_SH2, cx, cy, RX, RY)
    _ell(surf, BROWN_SH, cx - 1, cy - 1, RX - 1, RY - 1)
    _ell(surf, BROWN, cx - 2, cy - 2, RX - 3, RY - 3)

    marks = pygame.Surface((S, S), pygame.SRCALPHA)
    # Two short white END STRIPES near each pointed tip.
    pygame.draw.line(marks, LACE, (cx - RX + 4, cy - 4), (cx - RX + 4, cy + 4), 2)
    pygame.draw.line(marks, LACE, (cx + RX - 4, cy - 4), (cx + RX - 4, cy + 4), 2)
    # Central LACES: a short horizontal white bar + cross-ticks.
    pygame.draw.line(marks, LACE_SH, (cx - 6, cy + 1), (cx + 6, cy + 1), 3)
    pygame.draw.line(marks, LACE, (cx - 6, cy), (cx + 6, cy), 2)
    for lx in range(-5, 7, 3):
        pygame.draw.line(marks, LACE, (cx + lx, cy - 2), (cx + lx, cy + 2), 1)
    mmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.ellipse(mmask, (255, 255, 255, 255),
                        pygame.Rect(cx - RX + 1, cy - RY + 1, (RX - 1) * 2, (RY - 1) * 2))
    marks.blit(mmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(marks, (0, 0))

    # Lower-right shade for a unified gradient.
    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    _ell(shade, (50, 26, 8, 70), cx + 4, cy + 4, RX, RY)
    shmask = pygame.Surface((S, S), pygame.SRCALPHA)
    _ell(shmask, (255, 255, 255, 255), cx, cy, RX - 1, RY - 1)
    shade.blit(shmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))

    # Upper-left highlight.
    hi = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hi, (200, 150, 100, 140), (cx - 6, cy - 5), 4)
    pygame.draw.circle(hi, BROWN_HI, (cx - 7, cy - 5), 2)
    hmask = pygame.Surface((S, S), pygame.SRCALPHA)
    _ell(hmask, (255, 255, 255, 255), cx, cy, RX - 2, RY - 2)
    hi.blit(hmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hi, (0, 0))

    pygame.draw.ellipse(surf, KEYLINE,
                        pygame.Rect(cx - RX, cy - RY, RX * 2, RY * 2), 1)
    return pygame.transform.smoothscale(surf, (22, 22))
