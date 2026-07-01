# Soccer v4 — DESIGN 2: THE FREE-KICK WALL.
# WHY this exists: the other soccer takes lean on a garment to say "footballer".
# This one is POSE-driven instead — Pip frozen in a defensive wall stance with
# both wings crossed tight into a hard NAVY X over the chest, so the read is a
# body language, not a jersey tint. Keeping the scarlet macaw fully visible under
# a bold crossed-arms silhouette is the differentiator from the kitted designs;
# navy wristbands, white shin tape, a low brow head guard and dark boots are the
# only accessories, each a single bold mark that survives the 40px downscale.
import pygame
from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# WHY a fixed body centre: the crossed-wing X and wristbands key off the macaw's
# torso, independent of the head anchors, so they hold across wing frames.
BCX, BCY = 32, 52

_NAVY    = (15, 45, 100)    # deep navy for the crossed arms (the hero X)
_NAVY_LT = (27, 58, 107)    # lighter navy wristbands
_TAPE    = (240, 240, 240)  # shin tape white
_ACCENT  = (232, 160, 32)   # warm gold accent stripe on each wristband
_BOOT_D  = (20, 20, 30)     # dark boot


def _wristband(surf, cx, cy):
    """A small navy cuff at a wingtip: a lighter-navy block ringed dark, with a
    white highlight stripe and a warm gold accent tick so it reads as a padded
    band, not a stray dark dot, at 40px."""
    pygame.draw.rect(surf, _NAVY, (cx - 3, cy - 4, 8, 9), border_radius=2)      # dark ring
    pygame.draw.rect(surf, _NAVY_LT, (cx - 2, cy - 3, 6, 7), border_radius=2)   # band body
    pygame.draw.line(surf, _TAPE, (cx - 2, cy - 2), (cx + 3, cy - 2), 1)        # white stripe
    pygame.draw.line(surf, _ACCENT, (cx - 2, cy + 1), (cx + 3, cy + 1), 1)      # gold accent


def _paint(surf, _a):
    # 1 — SHIN TAPE: white wraps on each leg, a thin navy stripe across the
    # centre so the tape reads as wrapped athletic strapping, not a plain block.
    for lx in (HX - 14, HX - 2):
        pygame.draw.rect(surf, _TAPE, (lx, HY + 18, 6, 4))
        pygame.draw.line(surf, _NAVY, (lx, HY + 20), (lx + 5, HY + 20), 1)

    # 2 — DARK BOOTS: small near-black ellipses at the feet so the legs terminate
    # in booted studs under the shin tape.
    for lx in (HX - 11, HX + 1):
        pygame.draw.ellipse(surf, _BOOT_D, (lx - 2, HY + 23, 9, 5))

    # 3 — CROSSED-WING X (the hero read): two thick navy diagonals forming a bold
    # X across the chest, crossing at centre — the wings pulled tight over the
    # body in the wall pose. Drawn OVER the scarlet body so the red still shows;
    # a shadow underlay + a lighter top edge keep each arm reading round at 40px.
    lp0, lp1 = (BCX - 12, BCY - 8), (HX + 4, BCY + 4)   # left arm: upper-left → lower-right
    rp0, rp1 = (HX + 4, BCY - 8), (BCX - 12, BCY + 4)   # right arm: upper-right → lower-left
    pygame.draw.line(surf, (9, 28, 66), (lp0[0], lp0[1] + 1), (lp1[0], lp1[1] + 1), 6)
    pygame.draw.line(surf, (9, 28, 66), (rp0[0], rp0[1] + 1), (rp1[0], rp1[1] + 1), 6)
    pygame.draw.line(surf, _NAVY, lp0, lp1, 5)
    pygame.draw.line(surf, _NAVY, rp0, rp1, 5)
    pygame.draw.line(surf, _NAVY_LT, (lp0[0], lp0[1] - 1), (lp1[0], lp1[1] - 1), 1)
    pygame.draw.line(surf, _NAVY_LT, (rp0[0], rp0[1] - 1), (rp1[0], rp1[1] - 1), 1)

    # 4 — WRISTBANDS at the four ends of the crossed arms (where the wingtips
    # sit), so the X terminates in padded cuffs instead of blunt line ends.
    for tip in (lp0, lp1, rp0, rp1):
        _wristband(surf, tip[0], tip[1])

    # 5 — LOW HEADGUARD: a thin dark-navy protective band across the brow ridge —
    # narrow so it reads as a head guard, not a sweatband.
    pygame.draw.line(surf, _NAVY, (HX - 10, HY - 4), (HX + 10, HY - 4), 2)
    pygame.draw.line(surf, _NAVY_LT, (HX - 8, HY - 5), (HX + 6, HY - 5), 1)


build = _make_skin(_paint)
