"""DESIGN 3 — THE CAPTAIN (Soccer / Football, v2).

Scratch exploration only — NOT registered in store_skins.BUILDERS, so
production is untouched. Pip the scarlet macaw kitted as the side's captain:
a classic deep-NAVY jersey, a white squad NUMBER on the chest, a small gold
team CREST left of it, and — the hero tell — a bright GOLD CAPTAIN'S ARMBAND
high on the near (forward) shoulder. Mid-grey shorts with a white hem, tall
navy socks with a white hoop, and low dark boots finish the kit. No ball, no
headgear — the crown stays the open macaw so Pip still reads as a parrot, and
NOTHING covers the beak/eye/face.

The jersey reuses the EXACT baseball-jersey polygon anchored on HX,HY (top at
HY+8, hem at HY+23) so the kit sits centred on the torso, never riding up onto
the face or off to the side. The armband is the one cue that must survive the
40px downscale: a 4px GOLD band isolated by dark-navy gap pixels high on the
shoulder, the single brightest, loudest mark in the costume, so "captain"
reads at hero scale. Pure white is reserved for the number + shorts hem so the
gold band always wins the eye; a bright navy rim-light keeps the kit from
dissolving into the night sky.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, _poly


# Classic deep-navy kit. Three cloth values so the collar, number and crest
# still separate from the jersey field after the 40px downscale.
_CAP_NAVY    = (10, 32, 96)         # #0A2060 jersey deep navy (cloth mid)
_CAP_NAVY_D  = (6, 20, 62)          # cloth shadow / seams / off-side / band-gap
_CAP_NAVY_H  = (40, 70, 150)        # shoulder / sleeve sheen
_CAP_NAVY_RIM= (70, 110, 200)       # bright rim-light so the kit survives night
_CAP_WHITE   = (244, 247, 255)      # #F4F7FF number / shorts hem (reserved white)
_CAP_WHITE_D = (200, 210, 232)      # cool white shade so trim reads rounded
_CAP_GREY    = (160, 164, 180)      # #A0A4B4 mid-grey shorts main fill
_CAP_GOLD    = (232, 178, 58)       # #E8B23A captain's armband band colour
_CAP_GOLD_H  = (255, 232, 158)      # gold glint / armband sheen
_CAP_BOOT    = (32, 34, 44)         # #20222C low dark boot
_CAP_BOOT_H  = (84, 90, 108)        # boot upper highlight


def _paint(surf, _a):
    # --- NAVY JERSEY over the torso (the team read) -----------------------------
    # Exact baseball-jersey polygon on the HX,HY anchor: top y=HY+8, hem y=HY+23.
    # Nothing rises above y=HY+8 so the kit can never climb onto the face.
    jersey = [(HX - 13, HY + 8), (HX - 14, HY + 18), (HX - 10, HY + 23),
              (HX + 8, HY + 23), (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, _CAP_NAVY, jersey)
    # Off-side shade so the jersey reads as a rounded torso, not a flat panel.
    _poly(surf, _CAP_NAVY_D, [(HX + 4, HY + 9), (HX + 11, HY + 18),
                              (HX + 8, HY + 23), (HX + 5, HY + 22)])
    # Shoulder sheen on the near side so the cloth catches light.
    _poly(surf, _CAP_NAVY_H, [(HX - 12, HY + 9), (HX - 6, HY + 9),
                              (HX - 8, HY + 13), (HX - 13, HY + 13)])
    # Bright rim-light down the near/forward jersey edge so the navy torso never
    # dissolves into a dark night sky — a 1px lit seam reads the silhouette.
    pygame.draw.line(surf, _CAP_NAVY_RIM, (HX + 9, HY + 8), (HX + 11, HY + 18), 1)
    pygame.draw.line(surf, _CAP_NAVY_RIM, (HX + 11, HY + 18), (HX + 8, HY + 23), 1)

    # --- WHITE SQUAD NUMBER on the chest — a bold "10" reads as a captain's
    #     number at hero scale. Nudged RIGHT so a clear navy gap (>=2px) sits
    #     between it and the crest; pure white is reserved for it + the hem.
    pygame.draw.line(surf, _CAP_WHITE, (HX + 2, HY + 12), (HX + 2, HY + 18), 2)  # "1"
    pygame.draw.ellipse(surf, _CAP_WHITE, (HX + 4, HY + 12, 5, 7))               # "0"
    pygame.draw.ellipse(surf, _CAP_NAVY, (HX + 5, HY + 13, 3, 5))                # "0" hole

    # --- GOLD TEAM CREST left of the number — ONE small shield blob (~7x7) with a
    #     navy field so the gold rim pops, nudged LEFT to clear the number. No
    #     V-collar: the chest carries exactly one crest + one number, nothing else.
    cx, cy = HX - 8, HY + 12
    shield = [(cx - 3, cy - 3), (cx + 3, cy - 3), (cx + 3, cy + 1),
              (cx, cy + 4), (cx - 3, cy + 1)]
    _poly(surf, _CAP_NAVY_D, shield)                  # crest field (dark, so gold pops)
    pygame.draw.polygon(surf, _CAP_GOLD, shield, 1)   # gold shield outline
    pygame.draw.line(surf, _CAP_GOLD_H, (cx - 3, cy - 3), (cx + 3, cy - 3), 1)  # rim glint

    # --- MID-GREY SHORTS hem just below the jersey hem — grey main fill so the
    #     shorts recede and never pull focus from the armband; one 1px white hem
    #     highlight is the only white down here.
    _poly(surf, _CAP_GREY, [(HX - 11, HY + 22), (HX + 9, HY + 22),
                            (HX + 8, HY + 26), (HX - 10, HY + 26)])
    pygame.draw.line(surf, _CAP_WHITE, (HX - 10, HY + 26), (HX + 8, HY + 26), 1)  # white hem
    pygame.draw.line(surf, _CAP_NAVY_D, (HX - 1, HY + 22), (HX - 1, HY + 26), 1)  # leg split

    # --- TALL NAVY SOCKS with a white hoop near the top + low dark BOOTS. Two
    #     sock pillars on the feet line; a bright rim down the near sock edge keeps
    #     the legs visible at night, one white band over each.
    for fx in (HX - 10, HX):
        pygame.draw.rect(surf, _CAP_NAVY, (fx, HY + 26, 7, 9))
        pygame.draw.line(surf, _CAP_NAVY_RIM, (fx + 6, HY + 26), (fx + 6, HY + 34), 1)  # rim
        pygame.draw.line(surf, _CAP_WHITE, (fx, HY + 27), (fx + 6, HY + 27), 2)  # white hoop
        pygame.draw.rect(surf, _CAP_BOOT, (fx - 1, HY + 33, 9, 4), border_radius=2)
        pygame.draw.line(surf, _CAP_BOOT_H, (fx - 1, HY + 34), (fx + 7, HY + 34), 1)

    # --- CAPTAIN'S ARMBAND (THE hero tell) — drawn LAST, high on the near/forward
    #     SHOULDER at HY+13..15 so it sits alone, well above the number/shorts
    #     cluster. A 4px GOLD band is the brightest, most isolated mark; dark-navy
    #     gap pixels above and below cut it off the jersey so it never smears into
    #     the kit, and a white sheen pixel gives it shine.
    pygame.draw.line(surf, _CAP_NAVY_D, (HX + 7, HY + 12), (HX + 14, HY + 13), 1)  # top gap
    pygame.draw.line(surf, _CAP_GOLD,   (HX + 7, HY + 14), (HX + 14, HY + 15), 4)  # gold band
    pygame.draw.line(surf, _CAP_GOLD_H, (HX + 7, HY + 13), (HX + 13, HY + 14), 1)  # sheen
    pygame.draw.line(surf, _CAP_NAVY_D, (HX + 7, HY + 17), (HX + 14, HY + 18), 1)  # bottom gap


build = store_skins._make_skin(_paint)
