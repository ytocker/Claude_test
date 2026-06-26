"""BASKETBALL — orange sphere with the black seam pattern parcel cosmetic.

The identity is basketball-orange crossed by the black SEAMS: a vertical
meridian, a horizontal equator, and the two bowed side seams (an 8-panel read).
Orange + the seam cross is unmistakable and survives grayscale because the seams
are near-black against a mid-value orange.

22px read tradeoffs (WHY): the full curved-panel seam set aliases to mud, so the
seams commit to a vertical line + a horizontal line + ONE tall-narrow ellipse
whose left/right arcs read as the two bowed side seams — masked to the sphere so
they curve away at the rim. Volume is baked like the other balls: dark outline
first, a light->shade orange body, an upper-left highlight, a lower-right shade
crescent. A warm keyline rim is the NIGHT lifeline.
"""
import pygame

ORANGE = (224, 122, 34)        # basketball orange — the mid-value body
ORANGE_HI = (242, 162, 78)     # lit upper-left
ORANGE_SH = (168, 85, 26)      # lower-right shade
ORANGE_SH2 = (134, 64, 18)     # deep rim shade so the sphere turns
SEAM = (32, 26, 20)            # near-black seams — the signature
OUTLINE = (22, 18, 12)         # dark, drawn first + inflated: reads on day sky
KEYLINE = (250, 196, 120)      # warm rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = cy = S // 2
    R = 16

    pygame.draw.circle(surf, OUTLINE, (cx, cy), R + 2)
    # Orange shell with baked volume.
    pygame.draw.circle(surf, ORANGE_SH2, (cx, cy), R)
    pygame.draw.circle(surf, ORANGE_SH, (cx - 1, cy - 1), R - 1)
    pygame.draw.circle(surf, ORANGE, (cx - 3, cy - 3), R - 3)

    # Seams on their own layer, MIN-masked to the sphere so the side arcs curve
    # away at the rim instead of running straight off the edge.
    seams = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.line(seams, SEAM, (cx - R, cy), (cx + R, cy), 2)          # equator
    pygame.draw.line(seams, SEAM, (cx, cy - R), (cx, cy + R), 2)          # meridian
    ew = int(R * 0.78)
    pygame.draw.ellipse(seams, SEAM,                                       # side seams
                        pygame.Rect(cx - ew, cy - R, 2 * ew, 2 * R), 2)
    smask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255), (cx, cy), R - 1)
    seams.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(seams, (0, 0))

    # Lower-right shade crescent over shell + seams for a unified sphere gradient.
    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shade, (60, 30, 8, 70), (cx + 5, cy + 6), R)
    shmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shmask, (255, 255, 255, 255), (cx, cy), R - 1)
    shade.blit(shmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))

    # Upper-left specular highlight.
    hi = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hi, (255, 232, 190, 150), (cx - 5, cy - 6), 4)
    pygame.draw.circle(hi, ORANGE_HI, (cx - 6, cy - 7), 2)
    hmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hmask, (255, 255, 255, 255), (cx, cy), R - 2)
    hi.blit(hmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hi, (0, 0))

    pygame.draw.circle(surf, KEYLINE, (cx, cy), R, 1)
    return pygame.transform.smoothscale(surf, (22, 22))
