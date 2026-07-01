"""BUBBLE SCOUT — a Close-Encounters little scout for the MINI UFO redesign.

The clear glass dome is the hero, not the hull: a big-eyed grey pilot sits
inside a hemisphere that dwarfs a thin slate saucer. The whole read is
weighted LOW because the sprite rides 12px below Pip's centre, so the top
quarter is eaten by the bird's belly — the alien eyes are the charm hook and
must survive at 22px, so they live in the clear lower band near dome-centre.
"""
import pygame
from game.parrot import _aaellipse

SIZE = 22
SS = 44

HULL      = (183, 198, 208)   # slate saucer
HULL_D    = (140, 155, 165)   # underside tint
GLASS     = (207, 243, 255)   # dome fill
GLASS_HI  = (230, 250, 255)   # crescent highlight
UGLOW     = (140, 240, 138)   # anti-gravity under-glow
OUTLINE   = (27, 39, 48)
EYE       = (14, 20, 24)
HEAD      = (122, 143, 151)


def build(mode="normal"):
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)

    cx = SS // 2
    disc_cy = 33          # saucer low so the whole ship clears Pip's belly
    dome_cy = 24          # dome sits on the disc; eyes read just below its centre
    disc_rx, disc_ry = 15, 5
    dome_rx, dome_ry = 10, 12

    # --- Green anti-gravity halo under the rim (no downward beam column) ---
    # Concentric fading rings read as a soft hover glow rather than a spotlight.
    for r_extra, a in ((6, 40), (3, 70), (1, 110)):
        glow = pygame.Surface((SS, SS), pygame.SRCALPHA)
        _aaellipse(glow, (*UGLOW, a), (cx, disc_cy + 3),
                   disc_rx + r_extra, disc_ry + r_extra // 2)
        s.blit(glow, (0, 0))

    # --- Dark silhouette halo baked around the disc for day-sky contrast ---
    _aaellipse(s, OUTLINE, (cx, disc_cy), disc_rx + 2, disc_ry + 2)

    # --- Slate saucer disc: lighter crown, darker underside lip ---
    _aaellipse(s, HULL_D, (cx, disc_cy + 1), disc_rx, disc_ry)
    _aaellipse(s, HULL,   (cx, disc_cy - 1), disc_rx, disc_ry - 1)

    # --- Dome outline ring + a first thin glass wash BEFORE the pilot ---
    # Laying most of the glass under the alien keeps the eyes crisp on top;
    # only a light film goes over him so he still reads as "behind glass."
    _aaellipse(s, OUTLINE, (cx, dome_cy), dome_rx + 1, dome_ry + 1)
    glass = pygame.Surface((SS, SS), pygame.SRCALPHA)
    _aaellipse(glass, (*GLASS, 150), (cx, dome_cy), dome_rx, dome_ry)
    s.blit(glass, (0, 0))

    # --- Alien pilot over most of the glass so the eyes punch through ---
    _aaellipse(s, HEAD, (cx, dome_cy + 3), 7, 8)
    # Two big almond eyes near dome-centre — the read-zone charm hook.
    _aaellipse(s, EYE, (cx - 4, dome_cy + 1), 3, 3)
    _aaellipse(s, EYE, (cx + 4, dome_cy + 1), 3, 3)

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
