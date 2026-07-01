# Soccer v4 — DESIGN 2: THE GOALKEEPER.
# WHY this exists: earlier soccer takes read as "a parrot tinted in team
# colours" rather than a parrot *wearing* a shirt. This GK build forces the
# jersey to register as actual clothing via explicit garment cues — a visible
# crew-neck collar ring (hollow centre showing the scarlet neck through the
# neckhole), bright sleeve cuffs, a white garment outline, and contrast socks —
# all against a bright HV-green kit. The hero prop is a pair of big CYAN-TEAL
# keeper MITTS shoved OUTBOARD past the jersey edge so they cantilever into the
# sky, break the jersey silhouette, and never fuse with Pip's yellow beak (a
# lime glove read as orange-yellow and blended into the beak); they paint last
# so they sit above the whole kit.
import pygame
from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# WHY a fixed body centre: the jersey/limb anchors are tuned off the macaw's
# torso, independent of the head anchors, so they stay put across wing frames.
BCX, BCY = 32, 52

_GK_BACK   = (19, 160, 101)   # HV green back zone
_GK_CHEST  = (34, 212, 136)   # lighter HV green chest zone
_GK_OUT    = (240, 245, 240)  # white garment outline
_GK_HI     = (50, 230, 160)   # highlight seam
_COLLAR_W  = (240, 245, 240)  # bright white crew-neck ring
_NECK_SCAR = (196, 34, 44)    # scarlet neck fill showing through the neckhole
_CUFF_W    = (230, 255, 230)  # bright white sleeve cuff
# Keeper mitts in CYAN-TEAL — a deliberately un-beak-like hue so the gloves
# never fuse with Pip's yellow beak at 40px (lime read as orange-yellow and
# blended in); a darker teal border rings each one so the mitt holds its own
# edge over the bright green jersey.
_GLOVE_G   = (40, 200, 235)   # cyan-teal mitt body
_GLOVE_GH  = (150, 235, 250)  # mitt highlight (catch-side)
_GLOVE_GD  = (18, 108, 140)   # mitt border / shadow
_GLOVE_W   = (235, 250, 255)  # knuckle bar
_SOCK_W    = (240, 240, 248)  # white socks
_SOCK_HOOP = (240, 240, 248)
_BOOT_D    = (26, 24, 32)
_BOOT_SOLE = (210, 210, 222)
_SHORTS_D  = (20, 24, 30)

# WHY a single source-of-truth polygon: the body fill, white outline and chest
# zone all key off this so the garment edges line up exactly.
_JERSEY = [
    (BCX - 10, HY + 8),
    (BCX - 12, HY + 17),
    (BCX - 8,  HY + 23),
    (HX + 8,   HY + 23),
    (HX + 11,  HY + 18),
    (HX + 9,   HY + 8),
]


def _mitt(surf, rect):
    """A big bright keeper MITT: rounded rect body + dark lime border + a
    bright catch-side highlight and a white knuckle bar so it reads as a padded
    glove, not a coloured patch. Sized/positioned to BREAK the jersey
    silhouette at the wing opening."""
    pygame.draw.rect(surf, _GLOVE_GD, rect.inflate(2, 2), border_radius=5)   # border
    pygame.draw.rect(surf, _GLOVE_G, rect, border_radius=4)                  # body
    # Catch-side highlight down the outer half so the mitt reads padded/round.
    pygame.draw.rect(surf, _GLOVE_GH,
                     pygame.Rect(rect.x + 1, rect.y + 1, rect.w - 4, 4),
                     border_radius=2)
    # White knuckle bar across the top + two short finger seams.
    pygame.draw.line(surf, _GLOVE_W, (rect.x + 1, rect.y + 5),
                     (rect.right - 2, rect.y + 5), 2)
    for fx in (rect.x + 3, rect.x + 7):
        pygame.draw.line(surf, _GLOVE_GD, (fx, rect.y + 7),
                         (fx, rect.bottom - 2), 1)


def _paint(surf, _a):
    # 1 — SOCKS (knee-high white with a dark hoop + a bright white sock hoop).
    for fx in (HX - 9, HX + 1):
        pygame.draw.line(surf, (160, 165, 180), (fx + 1, HY + 13), (fx + 1, HY + 25), 6)
        pygame.draw.line(surf, _SOCK_W,         (fx,     HY + 13), (fx,     HY + 25), 5)
        pygame.draw.line(surf, _SHORTS_D,       (fx - 1, HY + 17), (fx + 2, HY + 17), 2)
        pygame.draw.line(surf, _SOCK_HOOP,      (fx - 1, HY + 20), (fx + 2, HY + 20), 1)

    # 2 — BOOTS (dark ellipse at the sock hem with a lighter sole stripe for
    # contrast) so each foot reads as a booted studded shoe under the white sock.
    for fx in (HX - 9, HX + 1):
        pygame.draw.ellipse(surf, _BOOT_D, (fx - 4, HY + 26, 10, 5))
        pygame.draw.line(surf, _BOOT_SOLE, (fx - 3, HY + 29), (fx + 4, HY + 29), 1)

    # 3 — DARK SHORTS hem.
    pygame.draw.line(surf, _SHORTS_D, (BCX - 8, HY + 24), (HX + 8, HY + 24), 4)

    # 4 — JERSEY BODY (two-zone: darker back, lighter chest).
    _poly(surf, _GK_BACK, _JERSEY)
    chest = [(BCX, HY + 8), (BCX, HY + 23), (HX + 8, HY + 23),
             (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, _GK_CHEST, chest)

    # 5 — white garment outline (the jersey reads as cloth, not a body tint).
    pygame.draw.polygon(surf, _GK_OUT, _JERSEY, 1)

    # 6 — chest seam line.
    pygame.draw.line(surf, _GK_HI, (HX - 1, HY + 12), (HX, HY + 21), 1)

    # 7 — BRIGHT WHITE SLEEVE CUFFS at each wing opening.
    pygame.draw.line(surf, _CUFF_W, (BCX - 10, HY + 12), (BCX - 3, HY + 12), 2)
    pygame.draw.line(surf, _CUFF_W, (HX + 4,   HY + 12), (HX + 11, HY + 12), 2)

    # 8 — CREW-NECK COLLAR RING. A hollow bright-WHITE ellipse ring reads as a
    # neckhole against the green kit at 40px (a dark arc on HV-green was too low
    # contrast to see); the scarlet neck fill inside the ring shows the neckhole,
    # selling it as a real garment opening rather than a body tint.
    collar_rect = pygame.Rect(HX - 8, HY + 2, 15, 9)
    pygame.draw.ellipse(surf, _COLLAR_W, collar_rect)               # bright ring
    pygame.draw.ellipse(surf, _NECK_SCAR, collar_rect.inflate(-4, -4))  # neckhole

    # 9 — HERO PROP: keeper MITTS last, OUTBOARD past the jersey edge so they
    # cantilever into the sky, break the silhouette, and never fuse with the
    # yellow beak. Both rectangles extend beyond the jersey polygon.
    _mitt(surf, pygame.Rect(BCX - 18, HY + 13, 12, 15))   # far mitt (further left)
    _mitt(surf, pygame.Rect(HX + 14, HY + 14, 12, 15))    # near mitt (clear of jersey right edge)


build = _make_skin(_paint)
