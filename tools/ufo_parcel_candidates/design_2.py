"""BUBBLE SCOUT — a Close-Encounters little scout for the MINI UFO redesign.

The clear glass dome is the hero, not the hull: a big-eyed grey pilot sits
inside a hemisphere that sits on a bold slate saucer. The whole read is
weighted LOW because the sprite rides 12px below Pip's centre, so the top
quarter is eaten by the bird's belly — the alien eyes are the charm hook and
must survive at 22px, so they live in the clear lower band near dome-centre.
At true 22px anti-aliased mush disappears, so the disc, eyes, and hover-rim
are all built from hard-edged primitives that keep a crisp silhouette.
"""
import pygame
from game.parrot import _aaellipse

SIZE = 22
SS = 44

HULL      = (183, 198, 208)   # slate saucer
HULL_HI   = (220, 235, 242)   # crown rim-light
HULL_D    = (140, 155, 165)   # underside tint
GLASS     = (207, 243, 255)   # dome fill
GLASS_HI  = (230, 250, 255)   # crescent highlight
UGLOW     = (140, 240, 138)   # anti-gravity under-glow (soft halo)
UGLOW_BRIGHT = (79, 215, 77)  # crisp hover-rim
OUTLINE   = (27, 39, 48)
KEYLINE   = (42, 52, 64)       # cool charcoal keyline so the pale hull reads on day-blue
HEAD      = (145, 168, 178)
EYE_BLOCK = (4, 6, 8)          # near-black; a solid rect survives 2× downscale where a circle mushes out
DOME_LO   = (100, 118, 130)    # darkened lower dome for value structure


def build(mode="normal"):
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)

    cx = SS // 2
    disc_cy = 31          # saucer low so the whole ship clears Pip's belly
    dome_cy = 24          # dome sits on the disc; eyes read just below its centre
    disc_rx, disc_ry = 15, 8
    dome_rx, dome_ry = 10, 12

    # --- Soft green under-halo, drawn first so it reads as a diffuse aura ---
    glow = pygame.Surface((SS, SS), pygame.SRCALPHA)
    _aaellipse(glow, (*UGLOW, 60), (cx, disc_cy + 4), disc_rx + 4, disc_ry + 2)
    s.blit(glow, (0, 0))

    # --- Cool charcoal keyline around the whole dome+disc silhouette so the
    # pale grey-blue hull doesn't near-vanish against day-blue sky. ---
    _aaellipse(s, KEYLINE, (cx, dome_cy), dome_rx + 2, dome_ry + 2)
    _aaellipse(s, KEYLINE, (cx, disc_cy), disc_rx + 2, disc_ry + 2)

    # --- Dark silhouette halo baked around the disc for day-sky contrast ---
    _aaellipse(s, OUTLINE, (cx, disc_cy), disc_rx + 2, disc_ry + 2)

    # --- Bold slate saucer disc: lighter crown, darker underside lip ---
    _aaellipse(s, HULL_D, (cx, disc_cy + 1), disc_rx, disc_ry)
    _aaellipse(s, HULL,   (cx, disc_cy - 1), disc_rx, disc_ry - 1)

    # --- Hard equator highlight + dark under-edge define the disc silhouette. ---
    pygame.draw.line(s, HULL,    (cx - disc_rx + 2, disc_cy),
                                 (cx + disc_rx - 2, disc_cy), 2)
    pygame.draw.line(s, OUTLINE, (cx - disc_rx + 2, disc_cy + disc_ry - 1),
                                 (cx + disc_rx - 2, disc_cy + disc_ry - 1), 1)
    # Bright top rim-light across the brim so it reads as a crisp symmetric disc.
    pygame.draw.line(s, HULL_HI, (cx - disc_rx + 3, disc_cy - disc_ry + 1),
                                 (cx + disc_rx - 3, disc_cy - disc_ry + 1), 2)

    # --- Crisp bright-green hover-ring drawn AFTER the disc so it hangs BELOW
    # the hull as a separate anti-gravity ring, not a moss mound on the brim. ---
    pygame.draw.ellipse(s, UGLOW_BRIGHT,
        pygame.Rect(cx - disc_rx, disc_cy - disc_ry + 4, disc_rx * 2, disc_ry * 2), 2)

    # --- Dome outline ring + a first thin glass wash BEFORE the pilot ---
    # Laying most of the glass under the alien keeps the eyes crisp on top;
    # only a light film goes over him so he still reads as "behind glass."
    _aaellipse(s, OUTLINE, (cx, dome_cy), dome_rx + 1, dome_ry + 1)
    # Two-pass dome value: darkened lower half, then bright upper glass crown.
    _aaellipse(s, DOME_LO, (cx, dome_cy + 3), dome_rx, dome_ry - 2)
    _aaellipse(s, GLASS,   (cx, dome_cy - 2), dome_rx, dome_ry - 3)
    glass = pygame.Surface((SS, SS), pygame.SRCALPHA)
    _aaellipse(glass, (*GLASS, 110), (cx, dome_cy), dome_rx, dome_ry)
    s.blit(glass, (0, 0))

    # --- Alien pilot over most of the glass so the eyes punch through ---
    _aaellipse(s, HEAD, (cx, dome_cy + 3), 6, 7)
    # Near-black eye BLOCKS: a solid rect survives 2× downscale to a clean 2×3
    # block where an anti-aliased circle would smear into the head. The charm hook.
    for ex, ey in ((cx - 4, dome_cy + 1), (cx + 4, dome_cy + 1)):
        pygame.draw.rect(s, EYE_BLOCK, pygame.Rect(ex - 2, ey - 3, 4, 6))
        pygame.draw.rect(s, (255, 255, 255), pygame.Rect(ex - 1, ey - 2, 1, 1))

    # --- A faint top film of glass so the pilot still sits behind the dome ---
    film = pygame.Surface((SS, SS), pygame.SRCALPHA)
    _aaellipse(film, (*GLASS, 55), (cx, dome_cy - 3), dome_rx, dome_ry - 5)
    s.blit(film, (0, 0))

    # --- Bright crescent highlight on the dome's upper-left curve ---
    hi = pygame.Surface((SS, SS), pygame.SRCALPHA)
    _aaellipse(hi, (*GLASS_HI, 210), (cx - 4, dome_cy - 4), 3, 5)
    _aaellipse(hi, (*GLASS_HI, 0),   (cx - 3, dome_cy - 3), 2, 4)
    s.blit(hi, (0, 0))

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
