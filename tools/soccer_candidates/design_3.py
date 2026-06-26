"""DESIGN 3 — THE CAPTAIN (Soccer / Football, v2).

Scratch exploration only — NOT registered in store_skins.BUILDERS, so
production is untouched. Pip the scarlet macaw kitted as the side's captain:
a classic deep-NAVY jersey with a white V-collar at the chest neckline, a
white squad NUMBER on the chest, a small gold team CREST on the upper-left
chest, and — the hero tell — a bright white CAPTAIN'S ARMBAND wrapped around
the near (forward-right) wing. White shorts hem, tall navy socks with a white
hoop, and low dark boots finish the kit. No ball, no headgear — the crown
stays the open macaw so Pip still reads as a parrot, and NOTHING covers the
beak/eye/face.

The jersey reuses the EXACT baseball-jersey polygon anchored on HX,HY (top at
HY+8, hem at HY+23) so the kit sits centred on the torso, never riding up onto
the face or off to the side. The armband is the one cue that must survive the
40px downscale: a 4px bright white band on the dark navy sleeve, the single
brightest mark in the costume, so "captain" reads at hero scale.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, _poly


# Classic deep-navy kit. Three cloth values so the collar, number and crest
# still separate from the jersey field after the 40px downscale.
_CAP_NAVY    = (10, 32, 96)         # #0A2060 jersey deep navy (cloth mid)
_CAP_NAVY_D  = (6, 20, 62)          # cloth shadow / seams / off-side
_CAP_NAVY_H  = (40, 70, 150)        # shoulder / sleeve sheen
_CAP_WHITE   = (244, 247, 255)      # #F4F7FF collar / number / armband / shorts
_CAP_WHITE_D = (200, 210, 232)      # cool white shade so trim reads rounded
_CAP_GREY    = (208, 212, 222)      # light-grey shorts shade
_CAP_GOLD    = (236, 198, 78)       # #ECC64E crest shield rim
_CAP_GOLD_H  = (255, 232, 158)      # crest glint
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

    # --- WHITE V-COLLAR at the chest neckline (on the CHEST, not the face). A
    #     small open V notch at the jersey top, HY+9..13, well below the head, so
    #     it can never be mistaken for sunglasses or cover the beak/eye.
    pygame.draw.line(surf, _CAP_WHITE, (HX - 4, HY + 9), (HX, HY + 13), 2)
    pygame.draw.line(surf, _CAP_WHITE, (HX + 4, HY + 9), (HX, HY + 13), 2)
    pygame.draw.line(surf, _CAP_WHITE_D, (HX - 3, HY + 9), (HX, HY + 12), 1)

    # --- WHITE SQUAD NUMBER on the chest — a bold "10" reads as a captain's
    #     number at hero scale. Sits at HY+12..18, right of centre so the crest
    #     owns the upper-left chest.
    pygame.draw.line(surf, _CAP_WHITE, (HX + 1, HY + 12), (HX + 1, HY + 18), 2)  # "1"
    pygame.draw.ellipse(surf, _CAP_WHITE, (HX + 3, HY + 12, 5, 7))               # "0"
    pygame.draw.ellipse(surf, _CAP_NAVY, (HX + 4, HY + 13, 3, 5))                # "0" hole

    # --- GOLD TEAM CREST on the upper-left chest — a small shield (~8x8) with one
    #     white slash, drawn around (HX-7, HY+10).
    cx, cy = HX - 7, HY + 11
    shield = [(cx - 3, cy - 3), (cx + 3, cy - 3), (cx + 3, cy + 1),
              (cx, cy + 4), (cx - 3, cy + 1)]
    _poly(surf, _CAP_NAVY_D, shield)                  # crest field (dark, so gold pops)
    pygame.draw.polygon(surf, _CAP_GOLD, shield, 1)   # gold shield outline
    pygame.draw.line(surf, _CAP_WHITE, (cx - 2, cy + 1), (cx + 2, cy - 2), 1)   # white slash
    pygame.draw.line(surf, _CAP_GOLD_H, (cx - 3, cy - 3), (cx + 3, cy - 3), 1)  # rim glint

    # --- WHITE SHORTS hem just below the jersey hem — a short light band between
    #     the jersey (HY+23) and the socks so the kit has the shorts read.
    _poly(surf, _CAP_WHITE, [(HX - 11, HY + 22), (HX + 9, HY + 22),
                             (HX + 8, HY + 26), (HX - 10, HY + 26)])
    _poly(surf, _CAP_GREY, [(HX - 1, HY + 22), (HX + 9, HY + 22),
                            (HX + 8, HY + 26), (HX - 1, HY + 26)])  # off-side shade
    pygame.draw.line(surf, _CAP_NAVY_D, (HX - 1, HY + 22), (HX - 1, HY + 26), 1)  # leg split

    # --- TALL NAVY SOCKS with a white hoop near the top + low dark BOOTS. Two
    #     sock pillars on the feet line, one white band over each.
    for fx in (HX - 10, HX):
        pygame.draw.rect(surf, _CAP_NAVY, (fx, HY + 26, 7, 9))
        pygame.draw.line(surf, _CAP_NAVY_H, (fx, HY + 26), (fx, HY + 34), 1)
        pygame.draw.line(surf, _CAP_WHITE, (fx, HY + 27), (fx + 6, HY + 27), 2)  # white hoop
        pygame.draw.rect(surf, _CAP_BOOT, (fx - 1, HY + 33, 9, 4), border_radius=2)
        pygame.draw.line(surf, _CAP_BOOT_H, (fx - 1, HY + 34), (fx + 7, HY + 34), 1)

    # --- CAPTAIN'S ARMBAND (THE hero tell) — drawn LAST so it sits ON TOP of the
    #     navy sleeve. A 4px bright-white band wrapped around the near (forward-
    #     right) wing at HY+18..22. White edges sell it as a band ON the sleeve;
    #     the gold trim is the single brightest mark so "captain" reads at 40px.
    pygame.draw.line(surf, _CAP_WHITE_D, (HX + 7, HY + 19), (HX + 14, HY + 21), 5)
    pygame.draw.line(surf, _CAP_WHITE, (HX + 7, HY + 18), (HX + 14, HY + 20), 4)
    pygame.draw.line(surf, _CAP_GOLD, (HX + 8, HY + 17), (HX + 14, HY + 19), 1)  # gold trim


build = store_skins._make_skin(_paint)
