"""WAR PHARAOH — the Khepresh Conqueror (PHARAOH v2_design_4 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
pharaoh skin is untouched. WAR PHARAOH is a paint-over (Pip's face stays under
the crown).

Concept: the ONLY round/soft crown in the batch + the ONLY weapon prop. The
hero silhouette is the smooth deep-blue Khepresh war-dome — a single bulbous
cap that reads as a soft helmet against every conical pharaoh crown — studded
with a SPARSE grid of gold disc bosses and topped by a forward-striking gold
uraeus cobra at the brow. A curved gold khopesh sickle-sword is slung
diagonally across the body, blade tucked inside the silhouette, as the war
tell. Everything below the dome stays inside the base bird footprint: a thin
gold scale-armor pectoral on the upper chest, a faint blue-and-gold royal sash,
and a dark sandal recolor at the feet line.

At 40px the read, in order: (1) a saturated blue ROUND dome (the soft-crown
break), (2) the gold uraeus glinting at the brow, (3) a curved gold blade laid
across the body. The blue dome carries the day read on bright sky; the gold
uraeus + khopesh glint carry the night read against the dark blue.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Khepresh deep royal blue needs two values so the dome reads as a rounded
# helmet (shadow on the underside) rather than a flat disc at 40px.
_WP_BLUE    = (30, 58, 138)        # #1E3A8A khepresh blue
_WP_BLUE_D  = (20, 42, 99)         # #142A63 blue shadow
_WP_BLUE_H  = (54, 92, 184)        # crown top-light so the dome catches the sky
# Gold is the hero accent + the weapon; three values so the curved khopesh keeps
# a bright edge that survives the downscale (a metal curve only reads if it glints).
_WP_GOLD    = (232, 178, 58)       # #E8B23A gold uraeus / khopesh
_WP_GOLD_H  = (244, 214, 122)      # #F4D67A gold highlight (the 40px glint)
_WP_GOLD_D  = (168, 122, 36)       # gold shadow so the blade has a dark edge
_WP_SHEEN   = (159, 180, 232)      # #9FB4E8 disc-boss sheen
_WP_SANDAL  = (58, 40, 26)         # dark leather sandal at the feet line
_WP_SANDAL_H = (96, 70, 46)


def _khopesh_blade(surf, p0, ctrl, p1, color, width):
    """Quadratic-bezier polyline so the khopesh reads as a CURVED sickle, not a
    straight bar. Sampled coarse — the curve survives downscale, extra points
    don't (same idiom as the pirate cutlass)."""
    pts = []
    for i in range(9):
        t = i / 8.0
        mt = 1 - t
        x = mt * mt * p0[0] + 2 * mt * t * ctrl[0] + t * t * p1[0]
        y = mt * mt * p0[1] + 2 * mt * t * ctrl[1] + t * t * p1[1]
        pts.append((x, y))
    pygame.draw.lines(surf, color, False, pts, width)
    return pts


def _paint(surf, _a):
    BCX, BCY = 32, 52                 # body centre in composite space

    # ── KHOPESH slung diagonally across the body (painted first so the body
    #    covers the grip root and the blade tucks INSIDE the silhouette like the
    #    pirate cutlass — only its glint reads against the body). Hilt low-front
    #    at the waist; the sickle hooks up-and-back, the curved cutting edge held
    #    just shy of the back outline so it never balloons the footprint.
    hilt = (HX - 4, HY + 22)          # grip, near the waist / near wing
    ktip = (HX - 21, HY + 2)          # hook tip, tucked inside the back outline
    kctrl = (HX - 20, HY + 18)        # control pulls the sickle belly outward
    # Dark gold underlay (widest) so the bright blade has an edge against the body.
    _khopesh_blade(surf, hilt, kctrl, ktip, _WP_GOLD_D, 6)
    _khopesh_blade(surf, hilt, kctrl, ktip, _WP_GOLD, 4)
    # Bright back-edge glint — the single highest-value line that makes the gold
    # curve read as a blade at 40px. Offset along the spine of the curve.
    _khopesh_blade(surf, (hilt[0] - 1, hilt[1] - 2),
                   (kctrl[0] - 2, kctrl[1] - 2), (ktip[0] + 1, ktip[1] - 1),
                   _WP_GOLD_H, 2)
    # Hooked sickle point so the blade tip reads as the khopesh's signature hook.
    _poly(surf, _WP_GOLD_H, [(ktip[0] - 1, ktip[1] - 3), (ktip[0] + 4, ktip[1]),
                             (ktip[0] - 1, ktip[1] + 2)])
    # Short dark grip stub + a gold pommel bead so the low end reads as the handle.
    pygame.draw.line(surf, _WP_BLUE_D, (hilt[0] + 2, hilt[1] + 1),
                     (hilt[0] + 6, hilt[1] + 6), 4)
    pygame.draw.circle(surf, _WP_GOLD, (hilt[0] + 7, hilt[1] + 7), 2)

    # ── ROYAL SASH — a faint blue-and-gold diagonal across the body echoing the
    #    crown, kept thin and INSIDE the footprint so it never adds body mass.
    s0 = (HX + 6, HY + 7)             # near shoulder
    s1 = (HX - 16, HY + 23)           # off hip
    pygame.draw.line(surf, _WP_BLUE_D, s0, s1, 6)
    pygame.draw.line(surf, _WP_BLUE, (s0[0] - 1, s0[1] + 1), (s1[0] - 1, s1[1] + 1), 4)
    pygame.draw.line(surf, _WP_GOLD, (s0[0] - 2, s0[1] + 2), (s1[0] - 2, s1[1] + 2), 1)

    # ── GOLDEN SCALE-ARMOR PECTORAL — an arc of small gold scale-flecks across
    #    the upper chest, thin and few so it reads as armor at 40px without
    #    bulking the body. Two short staggered rows following the chest curve.
    row1 = [(BCX - 9, BCY - 6), (BCX - 4, BCY - 7), (BCX + 1, BCY - 7),
            (BCX + 6, BCY - 6)]
    row2 = [(BCX - 7, BCY - 2), (BCX - 2, BCY - 3), (BCX + 3, BCY - 3),
            (BCX + 8, BCY - 2)]
    for (fx, fy) in row1 + row2:
        pygame.draw.circle(surf, _WP_GOLD_D, (fx, fy + 1), 2)   # scale shadow
        pygame.draw.circle(surf, _WP_GOLD, (fx, fy), 2)
        pygame.draw.circle(surf, _WP_GOLD_H, (fx, fy - 1), 1)   # scale glint

    # ── SANDAL RECOLOR at the feet line (~HY+24) — dark leather straps sitting ON
    #    the feet, never below them, so the bird keeps its true size.
    for fx in (28, 34):
        pygame.draw.ellipse(surf, _WP_SANDAL, (fx - 3, HY + 23, 7, 4))
        pygame.draw.line(surf, _WP_SANDAL_H, (fx - 2, HY + 23), (fx + 2, HY + 23), 1)
        pygame.draw.line(surf, _WP_SANDAL, (fx, HY + 21), (fx, HY + 24), 1)  # ankle strap

    # ── THIN GOLD BROW-BAND where the dome meets the head (drawn before the dome
    #    so the dome's lower edge overlaps it cleanly), a hard horizontal gold
    #    line that anchors the face under the crown at 40px.
    pygame.draw.line(surf, _WP_GOLD, (HX - 12, CROWN_Y + 9), (HX + 12, CROWN_Y + 9), 3)
    pygame.draw.line(surf, _WP_GOLD_H, (HX - 9, CROWN_Y + 8), (HX + 4, CROWN_Y + 8), 1)

    # ── KHEPRESH WAR-DOME (above CROWN_Y) — the hero. A single smooth deep-blue
    #    rounded cap (the only round/soft crown in the batch), tall enough to
    #    dome over the crown but bulbous, NOT a cone. A shadow ellipse underlay
    #    gives the dome volume; a top-light arc catches the sky.
    dome = pygame.Rect(HX - 15, CROWN_Y - 11, 30, 26)         # bulbous cap
    pygame.draw.ellipse(surf, _WP_BLUE_D, dome)
    inner = pygame.Rect(HX - 14, CROWN_Y - 11, 28, 23)        # body sits high
    pygame.draw.ellipse(surf, _WP_BLUE, inner)
    pygame.draw.ellipse(surf, _WP_BLUE_H, (HX - 9, CROWN_Y - 10, 16, 8))  # top-light
    # Flatten the dome's bottom into the brow-band so it reads as a seated helmet,
    # not a floating ball.
    _poly(surf, _WP_BLUE_D, [(HX - 14, CROWN_Y + 7), (HX + 14, CROWN_Y + 7),
                             (HX + 13, CROWN_Y + 10), (HX - 13, CROWN_Y + 10)])

    # Sparse grid of gold disc bosses for the scaled shimmer — kept FEW (so it
    # never muddies) and given a cool sheen dot so the studs read on the blue.
    bosses = [(HX - 7, CROWN_Y - 6), (HX + 2, CROWN_Y - 7), (HX + 9, CROWN_Y - 2),
              (HX - 10, CROWN_Y), (HX - 1, CROWN_Y - 1), (HX + 6, CROWN_Y + 4),
              (HX - 6, CROWN_Y + 5)]
    for (bx, by) in bosses:
        pygame.draw.circle(surf, _WP_GOLD_D, (bx, by + 1), 2)
        pygame.draw.circle(surf, _WP_GOLD, (bx, by), 1)
        pygame.draw.circle(surf, _WP_SHEEN, (bx - 1, by - 1), 1)

    # ── GOLD URAEUS cobra striking forward at the brow — the hero accent. A
    #    reared S-body rising from the brow-band into a flared hood + head that
    #    juts forward over the beak, drawn LARGE and bright so it carries the
    #    night read. Painted last so it sits proud of the dome.
    ux, uy = HX + 2, CROWN_Y + 7      # cobra root at the brow-band centre-front
    body = [(ux, uy), (ux - 1, uy - 4), (ux + 2, uy - 7), (ux + 1, uy - 11)]
    pygame.draw.lines(surf, _WP_GOLD_D, False,
                      [(x + 1, y + 1) for x, y in body], 4)   # cobra shadow
    pygame.draw.lines(surf, _WP_GOLD, False, body, 3)         # reared S-body
    # Flared hood + forward-striking head jutting over the beak.
    hood = [(ux - 3, uy - 11), (ux + 1, uy - 14), (ux + 6, uy - 12),
            (ux + 4, uy - 9), (ux, uy - 9)]
    _poly(surf, _WP_GOLD_D, [(x + 1, y + 1) for x, y in hood])
    _poly(surf, _WP_GOLD, hood)
    pygame.draw.circle(surf, _WP_GOLD_H, (ux + 4, uy - 12), 2)   # bright cobra head
    pygame.draw.circle(surf, (40, 24, 12), (ux + 5, uy - 13), 1)  # eye dot
    pygame.draw.line(surf, _WP_GOLD_H, (ux, uy - 5), (ux + 1, uy - 9), 1)  # body glint


build = store_skins._make_skin(_paint)
