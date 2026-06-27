# Soccer v4 — DESIGN 2: THE GOALKEEPER.
# WHY this exists: earlier soccer takes read as "a parrot tinted in team
# colours" rather than a parrot *wearing* a shirt. This GK build forces the
# jersey to register as actual clothing via four explicit garment cues — a
# dark crew-neck collar, sleeve cuffs, a white garment outline, and a chest
# seam — all in high contrast against the bright HV-green kit. The yellow
# keeper gloves are the hero prop and paint last so they sit above everything.
import pygame
from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# WHY a fixed body centre: the jersey/limb anchors are tuned off the macaw's
# torso, independent of the head anchors, so they stay put across wing frames.
BCX, BCY = 32, 52

_GK_BACK   = (19, 160, 101)   # HV green back zone
_GK_CHEST  = (34, 212, 136)   # lighter HV green chest zone
_GK_OUT    = (240, 245, 240)  # white garment outline
_GK_HI     = (50, 230, 160)   # highlight seam
_SLEEVE    = (8, 52, 32)      # dark green collar + sleeve cuffs
_GLOVE_Y   = (255, 184, 0)    # yellow glove
_GLOVE_H   = (255, 220, 80)   # glove highlight
_GLOVE_D   = (180, 120, 0)    # glove shadow
_GLOVE_W   = (240, 240, 245)  # knuckle bar
_SOCK_W    = (240, 240, 248)  # white socks
_BOOT_D    = (26, 24, 32)
_BOOT_SOLE = (200, 200, 210)
_SHORTS_D  = (20, 24, 30)

# WHY a single source-of-truth polygon: the body fill, white outline and chest
# zone all key off this so the garment edges line up exactly.
_JERSEY = [
    (BCX - 10, HY + 7),
    (BCX - 12, HY + 17),
    (BCX - 8,  HY + 23),
    (HX + 8,   HY + 23),
    (HX + 11,  HY + 18),
    (HX + 9,   HY + 8),
]


def _glove(surf, gx, gy):
    """Keeper glove block — knuckle bar + finger lines sell it as a glove,
    not a mitten. Drawn after the body so it reads as a held-up hand."""
    pygame.draw.rect(surf, _GLOVE_D, (gx - 5, gy - 6, 9, 11))   # shadow
    pygame.draw.rect(surf, _GLOVE_Y, (gx - 4, gy - 6, 8, 10))   # main
    for fy in (gy - 4, gy - 2, gy):
        pygame.draw.line(surf, _GLOVE_D, (gx - 3, fy), (gx + 3, fy), 1)
    pygame.draw.line(surf, _GLOVE_W, (gx - 3, gy - 6), (gx + 3, gy - 6), 2)
    pygame.draw.line(surf, _GLOVE_H, (gx - 3, gy - 5), (gx + 2, gy - 5), 1)


def _paint(surf, _a):
    # 1 — SOCKS (knee-high white with a dark hoop).
    for fx in (HX - 9, HX + 1):
        pygame.draw.line(surf, (160, 165, 180), (fx + 1, HY + 13), (fx + 1, HY + 25), 6)
        pygame.draw.line(surf, _SOCK_W,         (fx,     HY + 13), (fx,     HY + 25), 5)
        pygame.draw.line(surf, _SHORTS_D,       (fx - 1, HY + 15), (fx + 2, HY + 15), 2)

    # 2 — BOOTS.
    for fx in (HX - 9, HX + 1):
        pygame.draw.ellipse(surf, _BOOT_D, (fx - 4, HY + 23, 9, 5))
        pygame.draw.line(surf, _BOOT_SOLE, (fx - 3, HY + 25), (fx + 3, HY + 25), 1)

    # 3 — DARK SHORTS hem.
    pygame.draw.line(surf, _SHORTS_D, (BCX - 8, HY + 24), (HX + 8, HY + 24), 4)

    # 4 — JERSEY BODY (two-zone: darker back, lighter chest).
    _poly(surf, _GK_BACK, _JERSEY)
    chest = [(BCX, HY + 7), (BCX, HY + 23), (HX + 8, HY + 23),
             (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, _GK_CHEST, chest)

    # 5 — ELEMENT 3: white garment outline.
    pygame.draw.polygon(surf, _GK_OUT, _JERSEY, 1)

    # 6 — ELEMENT 4: chest seam line.
    pygame.draw.line(surf, _GK_HI, (HX - 1, HY + 11), (HX, HY + 21), 1)

    # 7 — ELEMENT 2: sleeve cuffs.
    pygame.draw.line(surf, _SLEEVE, (BCX - 10, HY + 12), (BCX - 3, HY + 12), 2)
    pygame.draw.line(surf, _SLEEVE, (HX + 4,   HY + 12), (HX + 10, HY + 12), 2)

    # 8 — ELEMENT 1: dark crew-neck collar ring.
    collar_rect = pygame.Rect(HX - 7, HY + 4, 15, 9)
    pygame.draw.ellipse(surf, _SLEEVE,     collar_rect, 3)
    pygame.draw.ellipse(surf, (4, 30, 18), collar_rect, 1)

    # 9 — HERO PROP: keeper gloves last, above the whole kit.
    _glove(surf, HX - 10, HY + 12)   # far glove, raised catch pose
    _glove(surf, HX + 5,  HY + 17)   # near glove, lower / relaxed


build = _make_skin(_paint)
