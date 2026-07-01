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
HEAD      = (145, 168, 178)


def build(mode="normal"):
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)

    cx = SS // 2
    disc_cy = 31          # saucer low so the whole ship clears Pip's belly
    dome_cy = 24          # dome sits on the disc; eyes read just below its centre
    disc_rx, disc_ry = 15, 8
    dome_rx, dome_ry = 10, 12

    # --- Crisp bright-green hover-rim UNDER the disc, drawn first so the disc
    # overlaps it cleanly and it reads as an anti-gravity ring, not a blob. ---
    pygame.draw.ellipse(s, UGLOW_BRIGHT,
        pygame.Rect(cx - disc_rx, disc_cy - disc_ry, disc_rx * 2, disc_ry * 2), 2)
    glow = pygame.Surface((SS, SS), pygame.SRCALPHA)
    _aaellipse(glow, (*UGLOW, 60), (cx, disc_cy + 4), disc_rx + 4, disc_ry + 2)
    s.blit(glow, (0, 0))

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
    # Bright rim-light on the disc crown.
    pygame.draw.line(s, HULL_HI, (cx - disc_rx + 4, disc_cy - disc_ry + 1),
                                 (cx + disc_rx - 4, disc_cy - disc_ry + 1), 1)

    # --- Dome outline ring + a first thin glass wash BEFORE the pilot ---
    # Laying most of the glass under the alien keeps the eyes crisp on top;
    # only a light film goes over him so he still reads as "behind glass."
    _aaellipse(s, OUTLINE, (cx, dome_cy), dome_rx + 1, dome_ry + 1)
    glass = pygame.Surface((SS, SS), pygame.SRCALPHA)
    _aaellipse(glass, (*GLASS, 150), (cx, dome_cy), dome_rx, dome_ry)
    s.blit(glass, (0, 0))

    # --- Alien pilot over most of the glass so the eyes punch through ---
    _aaellipse(s, HEAD, (cx, dome_cy + 3), 6, 7)
    # Two solid near-black eyes with a white pixel between them — the charm hook.
    # Solid circles stay crisp at 22px where anti-aliased ellipses turn to mush.
    pygame.draw.circle(s, (0, 0, 0), (cx - 4, dome_cy + 2), 2)
    pygame.draw.circle(s, (0, 0, 0), (cx + 4, dome_cy + 2), 2)
    # White glints inside each eye.
    pygame.draw.circle(s, (255, 255, 255), (cx - 5, dome_cy + 1), 1)
    pygame.draw.circle(s, (255, 255, 255), (cx + 3, dome_cy + 1), 1)

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
