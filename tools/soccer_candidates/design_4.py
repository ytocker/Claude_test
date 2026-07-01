"""DESIGN 4 — THE ULTRAS CAPTAIN (Soccer / Football, v5).

Scratch exploration only — NOT registered in store_skins.BUILDERS, so
production stays untouched. Pip the scarlet macaw kitted as a SUPERFAN, not
a player: both wings thrown overhead holding a wide team scarf that arcs
above the crown as a huge crescent banner. War-paint face stripes, a small
red bobble beanie, and a short scarf loop at the neck complete the ultra.
There is NO jersey — the raised scarf is the entire identity.

The hero read is the OVERHEAD SCARF: the widest silhouette of all five
soccer designs, held aloft above CROWN_Y (y < 31) so it breaks the bird's
egg outline into a fan-in-the-stands crescent no player kit has. Two-tone
gold + black bands so the club colours survive the 40px downscale, thick
double lines for banner mass, hanging fringe ticks at both ends, and the
red arms reaching up from the head tie the scarf to Pip so it reads "held
overhead", not floating. Everything below is deliberately sparse (neck loop,
minimal boots) so nothing competes with the banner up top.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
BCX, BCY = 32, 52

# Ultras club palette. Gold + black are the scarf/banner club colours, kept
# as the only two-tone up top so the crescent reads as a team scarf; the
# beanie red is a step darker than Pip's scarlet so the cap separates from
# the head; white pompom + war-paint gold are the accent sparks.
_GOLD    = (244, 208, 63)     # scarf / banner gold
_GOLD_D  = (196, 160, 40)     # gold shade so the band reads round at 40px
_BLACK   = (20, 20, 20)       # scarf / banner black
_ARM     = (200, 50, 50)      # raised-arm scarlet (reaching up to the banner)
_ARM_D   = (150, 34, 34)      # arm shadow
_HAT_R   = (140, 20, 20)      # beanie deep red (steps off Pip's scarlet)
_HAT_RIM = (80, 10, 10)       # beanie rim band
_POM     = (245, 245, 245)    # pompom white
_BOOT    = (30, 28, 36)       # dark boots


def _paint(surf, _a):
    # 1 — BOOTS (minimal, dark). Kept tiny at the feet line so the lower body
    #     stays sparse and the eye rides up to the overhead banner. Two small
    #     dark ellipses so the bottom doesn't read empty.
    for fx in (HX - 9, HX + 1):
        pygame.draw.ellipse(surf, _BOOT, (fx - 3, HY + 23, 8, 5))
        pygame.draw.line(surf, (60, 58, 68), (fx - 2, HY + 24), (fx + 3, HY + 24), 1)

    # 2 — NECK SCARF LOOP. A short two-tone scarf section wound at the throat,
    #     echoing the club colours of the overhead banner so the identity is
    #     read twice (neck + overhead) without a jersey.
    pygame.draw.line(surf, _GOLD, (HX - 5, HY + 3), (HX + 5, HY + 3), 3)
    pygame.draw.line(surf, _BLACK, (HX - 4, HY + 6), (HX + 4, HY + 6), 2)

    # 3 — WAR-PAINT FACE STRIPES. Two diagonal gold slashes across the cheeks,
    #     below the eyes and above the beak — the supporter's painted face.
    #     Drawn over the base macaw so they sit on the plumage.
    pygame.draw.line(surf, _GOLD, (HX - 8, HY - 6), (HX - 4, HY - 2), 2)
    pygame.draw.line(surf, _GOLD, (HX + 2, HY - 6), (HX + 6, HY - 2), 2)

    # 4 — BEANIE HAT on the crown. A small deep-red dome sitting on top of the
    #     head with a dark rim band at its base and a white bobble pompom, so
    #     the crown reads as a knitted supporter cap under the banner.
    pygame.draw.ellipse(surf, _HAT_R, (HX - 7, CROWN_Y - 6, 14, 8))
    pygame.draw.line(surf, _HAT_RIM, (HX - 7, CROWN_Y - 1), (HX + 7, CROWN_Y - 1), 2)
    pygame.draw.circle(surf, _POM, (HX, CROWN_Y - 6), 3)
    pygame.draw.circle(surf, (255, 255, 255), (HX - 1, CROWN_Y - 7), 1)  # pompom glint

    # 5 — RAISED ARMS reaching up from the head to each end of the banner, so
    #     the scarf reads as HELD OVERHEAD rather than floating. Scarlet to
    #     match Pip, with a shadow underlay so the thin arm survives at 40px.
    pygame.draw.line(surf, _ARM_D, (HX - 8, CROWN_Y + 3), (HX - 22, CROWN_Y - 4), 3)
    pygame.draw.line(surf, _ARM, (HX - 8, CROWN_Y + 2), (HX - 22, CROWN_Y - 5), 2)
    pygame.draw.line(surf, _ARM_D, (HX + 5, CROWN_Y + 3), (HX + 18, CROWN_Y - 4), 3)
    pygame.draw.line(surf, _ARM, (HX + 5, CROWN_Y + 2), (HX + 18, CROWN_Y - 5), 2)

    # 6 — OVERHEAD SCARF — THE HERO PROP. A wide crescent banner arcing above
    #     the crown (y < 31), spanning nearly the full width of the bird — the
    #     widest silhouette of all five designs. Two-tone: gold on the left,
    #     black on the right, each doubled 4px below for banner thickness, with
    #     hanging fringe ticks at both ends. Drawn LAST so it is fully in front
    #     of the arms and beanie, owning the read.
    # Top band (thick), gold left half + black right half.
    pygame.draw.line(surf, _GOLD_D, (HX - 22, CROWN_Y - 7), (HX, CROWN_Y - 5), 5)  # gold shade underlay
    pygame.draw.line(surf, _GOLD, (HX - 22, CROWN_Y - 8), (HX, CROWN_Y - 6), 5)
    pygame.draw.line(surf, _BLACK, (HX, CROWN_Y - 6), (HX + 18, CROWN_Y - 8), 5)
    # Second parallel band 4px below for scarf thickness.
    pygame.draw.line(surf, _GOLD, (HX - 22, CROWN_Y - 4), (HX, CROWN_Y - 2), 4)
    pygame.draw.line(surf, _BLACK, (HX, CROWN_Y - 2), (HX + 18, CROWN_Y - 4), 4)
    # A slim highlight riding the gold half so the banner reads lit at 40px.
    pygame.draw.line(surf, (255, 236, 150), (HX - 20, CROWN_Y - 8), (HX - 2, CROWN_Y - 6), 1)

    # Fringe ticks hanging down from each end so the scarf reads as knitted
    # cloth, not a painted arc — three at the gold end, three at the black end.
    for i in range(3):
        gx = HX - 22 + i * 2
        pygame.draw.line(surf, _GOLD, (gx, CROWN_Y - 4), (gx, CROWN_Y + 1), 1)
    for i in range(3):
        bx = HX + 14 + i * 2
        pygame.draw.line(surf, _BLACK, (bx, CROWN_Y - 4), (bx, CROWN_Y + 1), 1)


build = _make_skin(_paint)
