"""DESIGN 3 — THE CAPTAIN (Soccer / Football), v3.

Scratch exploration only — NOT registered in store_skins.BUILDERS, so production
art stays untouched.

The critical advance over the earlier soccer kits: a FULL-BODY navy jersey that
wraps most of the visible torso (left edge pulled out to x=20 rather than the old
narrow x=33), so the kit reads as a worn shirt, not a chest patch. The jersey is
two-zoned — a dark navy back and a lighter navy chest — so the rounded torso reads
at 40px. The hero captaincy cues sit on top: a gold captain's ARMBAND isolated on
the near shoulder, a small red/gold CREST patch on the chest, and a white squad
NUMBER "10" below it. Knee-high navy socks with a white hoop, grey shorts, and dark
boots finish the kit. NO headgear of any kind — the crown stays the open macaw head.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
BCX, BCY = 32, 52

# Two-zone navy jersey — a dark back so the lighter chest reads as a lit front.
_CAP_BACK    = (7, 24, 72)         # #071848 dark navy back zone
_CAP_CHEST   = (13, 40, 120)       # #0D2878 lighter navy chest zone
_CAP_FOLD    = (10, 32, 96)        # seam fold line between the zones
_CAP_OUTLINE = (4, 14, 48)         # very dark navy contour outline

# Gold captain's armband — the hero captaincy note, isolated on the near shoulder.
_ARMBAND     = (232, 178, 58)      # #E8B23A gold band
_ARMBAND_H   = (255, 215, 100)     # armband highlight

# Squad number + crest — the on-shirt identity marks.
_NUM_W       = (244, 244, 248)     # white squad number
_CREST_R     = (195, 50, 40)       # crest red field
_CREST_G     = (240, 200, 50)      # crest gold bar

# Kit darks — navy socks with a white hoop, grey shorts, near-black boots.
_SOCK_NAVY   = (15, 26, 100)       # knee-high navy sock
_SOCK_W      = (240, 240, 248)     # white sock hoop
_SHORTS_GREY = (130, 134, 150)     # grey shorts band
_BOOT_D      = (26, 24, 32)        # near-black boot
_BOOT_SOLE   = (200, 200, 210)     # boot sole glint


def _paint(surf, _a):
    # Full-body jersey polygon — left edge pulled out to (BCX-10, HY+7)=(22,48)
    # so the navy wraps the whole visible torso (~36px wide), not a chest patch.
    jersey = [
        (BCX - 10, HY + 7),    # left shoulder  (22, 48)
        (BCX - 12, HY + 17),   # left hip       (20, 58)
        (BCX - 8,  HY + 23),   # left hem       (24, 64)
        (HX + 8,   HY + 23),   # right hem      (55, 64)
        (HX + 11,  HY + 18),   # right hip      (58, 59)
        (HX + 9,   HY + 8),    # right shoulder (56, 49)
    ]
    # Lighter chest zone over the near (right) half so the torso reads as a lit
    # front against the dark back.
    chest_zone = [
        (BCX,      HY + 7),
        (BCX,      HY + 23),
        (HX + 8,   HY + 23),
        (HX + 11,  HY + 18),
        (HX + 9,   HY + 8),
    ]

    # ── 1 · GREY SHORTS — a band between the jersey hem and the socks so there's
    #    a kit break between shirt and legs. Drawn before the legs so the hem and
    #    shorts overlap the sock tops.
    pygame.draw.line(surf, _SHORTS_GREY, (BCX - 8, HY + 24), (HX + 8, HY + 24), 4)

    # ── 2 · FULL JERSEY (two zones) — dark back, lighter chest, a seam fold down
    #    the centre, and a dark contour so the navy holds its edge on night sky.
    _poly(surf, _CAP_BACK, jersey)
    _poly(surf, _CAP_CHEST, chest_zone)
    pygame.draw.line(surf, _CAP_FOLD, (BCX, HY + 7), (BCX, HY + 23), 1)
    pygame.draw.polygon(surf, _CAP_OUTLINE, jersey, 1)

    # ── 3 · GOLD CAPTAIN'S ARMBAND — dropped onto the navy shoulder cloth (well
    #    below the head/eye junction) so the gold can't smear into the sunglasses
    #    and cheek. Thin dark gaps top and bottom isolate it on the navy.
    pygame.draw.line(surf, _CAP_OUTLINE, (HX + 2, HY + 8),  (HX + 10, HY + 8),  1)
    pygame.draw.line(surf, _ARMBAND,     (HX + 2, HY + 9),  (HX + 10, HY + 9),  5)
    pygame.draw.line(surf, _ARMBAND_H,   (HX + 3, HY + 8),  (HX + 9,  HY + 8),  1)
    pygame.draw.line(surf, _CAP_OUTLINE, (HX + 2, HY + 13), (HX + 10, HY + 13), 1)

    # ── 4 · CREST PATCH — a small red shield dropped 2px lower and capped at 4px
    #    tall so crest, armband and number form a spaced triangle, not a pile.
    crest = [(HX - 5, HY + 11), (HX - 1, HY + 11), (HX - 1, HY + 14),
             (HX - 3, HY + 15), (HX - 5, HY + 14)]
    _poly(surf, _CREST_R, crest)
    pygame.draw.line(surf, _CREST_G, (HX - 5, HY + 12), (HX - 1, HY + 12), 1)
    pygame.draw.polygon(surf, _CAP_OUTLINE, crest, 1)

    # ── 5 · SQUAD NUMBER "10" — chest-centre so it anchors the third point of the
    #    triangle. A dark drop-shadow 1px down/right gives it contrast against the
    #    dark navy at night, where plain white was washing out.
    font = pygame.font.SysFont("arial", 7, bold=True)
    num = font.render("10", True, _NUM_W)
    shadow = font.render("10", True, _CAP_OUTLINE)
    surf.blit(shadow, (BCX + 3, HY + 16))
    surf.blit(num, (BCX + 2, HY + 15))

    # ── 6 · NAVY SOCK PILLARS (knee-high) — white hoop near the knee is the
    #    classic cue. Drawn over the hem so they read as legs below the shirt.
    for fx in (HX - 9, HX + 1):
        pygame.draw.line(surf, _SOCK_NAVY, (fx, HY + 13), (fx, HY + 25), 5)
        pygame.draw.line(surf, _SOCK_W, (fx - 1, HY + 15), (fx + 2, HY + 15), 2)

    # ── 7 · BOOTS — dark studded shoes at the feet line with a bright sole edge.
    for fx in (HX - 9, HX + 1):
        pygame.draw.ellipse(surf, _BOOT_D, (fx - 4, HY + 23, 9, 5))
        pygame.draw.line(surf, _BOOT_SOLE, (fx - 3, HY + 25), (fx + 3, HY + 25), 1)


build = store_skins._make_skin(_paint)
