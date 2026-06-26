"""THE ALL-STAR DUNKER — basketball candidate (DESIGN 4 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched.

Concept: the dunk-contest showman. Where the other basketball designs read matte
and athletic, this one is pure SPECTACLE — a shiny metallic GOLD/chrome tank with
a big white STAR behind the number, a glossy full-length shooter ARM SLEEVE down
the near wing (the hero, drawn LAST so it sits in front), a flashy gold headband
with a star, baggy shorts with star side-panels, and gold-and-white high-tops
with a glint. There is NO ball — it ships separately as a PARCEL item, so the kit
alone must scream HOOPS-ALL-STAR at the 40px read.

The "metallic" look is carried by a 3-value gold ramp on every gold surface
(deep gold shadow → gold → near-white chrome glint), so the cloth reads as
reflective rather than flat. Midnight navy is the contrast trim/piping so the
gold pops on both a bright day sky and a dark night sky. At 40px, in order of
value: (1) the gold tank + big white STAR, (2) the long chrome arm sleeve down
the near wing, (3) the gold star headband, then the gold high-tops. Every kit
piece stays INSIDE the base bird footprint — the sleeve hugs the wing, the
headband hugs the crown, nothing drops below the feet line.
"""
import math

import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# 3-value metallic GOLD ramp — the reflective tell. Deep shadow + mid + a
# near-white chrome glint read as a curved metal surface rather than flat cloth.
_GOLD_D = (184, 134, 42)             # #B8862A deep gold shadow
_GOLD   = (232, 178, 58)             # #E8B23A metallic gold
_GOLD_H = (250, 226, 150)            # warm chrome highlight (just shy of white)
_CHROME = (124, 201, 240)            # #7CC9F0 cool chrome glint (specular pop)
# Midnight navy is the trim/piping that frames the gold so it reads on any sky.
_NAVY   = (26, 33, 80)               # #1A2150 midnight navy
_NAVY_H = (54, 66, 130)              # navy sheen
_WHITE  = (244, 244, 248)            # #F4F4F8 white star / number
_WHITE_D = (200, 202, 212)           # white shadow so it survives a light sky
# Sleeve greys/navy so the chrome highlight reads as a smooth reflective tube.
_SLV_D  = (22, 27, 58)               # sleeve deep navy
_SLV    = (40, 50, 96)               # sleeve mid
_SLV_H  = (132, 196, 232)            # sleeve chrome seam


def _star(surf, color, cx, cy, r, *, rot=-math.pi / 2, inner=0.42):
    """A clean 5-point star — the all-star motif. `inner` is the valley radius
    as a fraction of `r`; the default reads as a crisp pointed star at 40px."""
    pts = []
    for i in range(10):
        ang = rot + i * math.pi / 5
        rad = r if i % 2 == 0 else r * inner
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    _poly(surf, color, pts)


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── BAGGY SHORTS first, behind the tank hem, with metallic STAR side-panels.
    #    Painted before the tank so the singlet overlaps the waistband cleanly.
    _poly(surf, _NAVY, [(BCX - 11, BCY + 9), (BCX + 12, BCY + 9),
                        (BCX + 12, BCY + 17), (BCX - 11, BCY + 17)])
    _poly(surf, _NAVY_H, [(BCX - 11, BCY + 9), (BCX + 12, BCY + 9),
                          (BCX + 12, BCY + 11), (BCX - 11, BCY + 11)])  # waist sheen
    # Gold star side-panels down each thigh — the flash even on the shorts.
    for sx in (BCX - 10, BCX + 8):
        _poly(surf, _GOLD_D, [(sx, BCY + 11), (sx + 3, BCY + 11),
                              (sx + 3, BCY + 17), (sx, BCY + 17)])
        _star(surf, _GOLD_H, sx + 1, BCY + 14, 2)

    # ── SLEEVELESS METALLIC TANK over the torso. Cut unmistakably sleeveless
    #    (bare-shoulder scoops + thin straps) so it still reads HOOPS, but every
    #    surface uses the 3-value gold ramp so it looks like reflective metal,
    #    not a flat jersey. Hem held ~BCY+10 inside the footprint.
    jersey = [(BCX - 11, BCY - 6), (BCX + 10, BCY - 6),
              (BCX + 13, BCY + 2), (BCX + 12, BCY + 10),
              (BCX - 11, BCY + 10), (BCX - 13, BCY + 2)]
    _poly(surf, _GOLD, jersey)
    # Deep-gold shadow down the off side + along the hem = curved metal volume.
    _poly(surf, _GOLD_D, [(BCX - 13, BCY + 1), (BCX - 9, BCY - 1),
                          (BCX - 8, BCY + 9), (BCX - 11, BCY + 10)])
    pygame.draw.line(surf, _GOLD_D, (BCX - 10, BCY + 9), (BCX + 11, BCY + 9), 2)
    # Bright chrome glint band catching the light down the near side = reflective.
    pygame.draw.line(surf, _GOLD_H, (BCX + 7, BCY - 4), (BCX + 9, BCY + 7), 2)
    pygame.draw.line(surf, _CHROME, (BCX + 8, BCY - 3), (BCX + 9, BCY + 4), 1)

    # Thin shoulder STRAPS at the wing roots — bare scarlet shoulder reads outside
    # each (the sleeveless tell), trimmed in navy so the gold edges stay crisp.
    _poly(surf, _GOLD, [(BCX - 11, BCY - 6), (BCX - 6, BCY - 9),
                        (BCX - 4, BCY - 5), (BCX - 8, BCY - 2)])      # off strap
    _poly(surf, _GOLD, [(BCX + 10, BCY - 6), (BCX + 5, BCY - 9),
                        (BCX + 3, BCY - 5), (BCX + 7, BCY - 2)])      # near strap
    # Metallic NAVY trim piping along the neckline + hem — the dressed-up frame.
    pygame.draw.lines(surf, _NAVY, False,
                      [(BCX - 5, BCY - 3), (BCX, BCY - 1), (BCX + 5, BCY - 3)], 2)
    pygame.draw.line(surf, _NAVY, (BCX - 11, BCY + 10), (BCX + 12, BCY + 10), 2)
    # Deep armhole scoops so the bare-shoulder, sleeveless cut is explicit at 40px.
    pygame.draw.arc(surf, _GOLD_D, (BCX + 3, BCY - 7, 11, 14), -1.0, 1.4, 2)
    pygame.draw.arc(surf, _GOLD_D, (BCX - 14, BCY - 7, 11, 14), 1.7, 4.2, 2)

    # ── BIG WHITE STAR behind the number — the all-star headline tell. Drawn on
    #    the chest, shadowed down-left so it survives a light day sky, with the
    #    bold white number "1" sitting in front (the showman's #1).
    sx, sy = BCX, BCY + 1
    _star(surf, _WHITE_D, sx, sy + 1, 8)                  # star shadow
    _star(surf, _WHITE, sx, sy, 8)                        # white star
    _star(surf, _GOLD, sx, sy, 3.4)                       # gold star eye
    # Bold "1" overlaid on the star centre — navy so it reads on the white star.
    pygame.draw.line(surf, _NAVY, (sx, sy - 5), (sx, sy + 5), 2)
    pygame.draw.line(surf, _NAVY, (sx - 2, sy - 3), (sx, sy - 5), 2)

    # ── GOLD-AND-WHITE HIGH-TOPS on the feet line. Chunky metallic boots with a
    #    navy accent stripe, a white midsole, and a chrome toe glint — sitting ON
    #    the feet line (~HY+21..27), never below it, so the bird stays true size.
    for fx in (26, 34):
        pygame.draw.rect(surf, _GOLD_D, (fx - 4, HY + 22, 9, 6), border_radius=2)
        pygame.draw.rect(surf, _GOLD, (fx - 4, HY + 21, 9, 4), border_radius=2)
        pygame.draw.line(surf, _NAVY, (fx - 3, HY + 23), (fx + 4, HY + 23), 1)
        pygame.draw.line(surf, _WHITE, (fx - 4, HY + 27), (fx + 5, HY + 27), 2)  # midsole
        pygame.draw.line(surf, _CHROME, (fx - 3, HY + 21), (fx, HY + 21), 1)     # toe glint

    # ── GOLD STAR HEADBAND across the brow — bold metallic band hugging the crown
    #    with a 3-value gold sheen + a tiny white STAR badge at centre. Leaves
    #    Pip's eye + beak in the open below it.
    by = CROWN_Y + 5
    pygame.draw.line(surf, _GOLD_D, (HX - 12, by + 1), (HX + 13, by), 7)    # band shadow
    pygame.draw.line(surf, _GOLD, (HX - 12, by), (HX + 13, by - 1), 5)
    pygame.draw.line(surf, _GOLD_H, (HX - 10, by - 2), (HX + 6, by - 2), 1)  # chrome glint
    _star(surf, _WHITE, HX + 1, by, 3)                                       # star badge
    # Tiny navy knot + tail tied at the off-temple — the "worn band" tell.
    pygame.draw.circle(surf, _NAVY, (HX - 12, by), 3)
    pygame.draw.line(surf, _NAVY_H, (HX - 13, by + 2), (HX - 16, by + 5), 2)

    # ── FULL-LENGTH SHOOTER ARM SLEEVE down the near wing — THE HERO, drawn LAST
    #    so it sits in front of everything. A smooth tapered TUBE with a long
    #    bright chrome highlight seam running its length so it reads glossy/metal.
    #    Spans BCX+12, BCY-4..+13, hugging the wing inside the footprint.
    sleeve = [(BCX + 9, BCY - 4), (BCX + 16, BCY - 3),
              (BCX + 17, BCY + 13), (BCX + 12, BCY + 14)]
    _poly(surf, _SLV, sleeve)
    # Deep-navy shadow down the outer edge gives the tube its round cross-section.
    _poly(surf, _SLV_D, [(BCX + 15, BCY - 3), (BCX + 17, BCY + 1),
                         (BCX + 17, BCY + 13), (BCX + 14, BCY + 13)])
    # Long bright chrome highlight seam down the inner face = the glossy read.
    pygame.draw.line(surf, _SLV_H, (BCX + 11, BCY - 2), (BCX + 13, BCY + 12), 2)
    pygame.draw.line(surf, _WHITE, (BCX + 11, BCY - 1), (BCX + 12, BCY + 5), 1)
    # Gold cuff bands top + bottom tie the sleeve back into the gold kit.
    pygame.draw.line(surf, _GOLD, (BCX + 9, BCY - 3), (BCX + 16, BCY - 2), 2)
    pygame.draw.line(surf, _GOLD, (BCX + 12, BCY + 13), (BCX + 17, BCY + 12), 2)
    pygame.draw.line(surf, _GOLD_H, (BCX + 10, BCY - 3), (BCX + 13, BCY - 3), 1)


build = store_skins._make_skin(_paint)
