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
(deep gold shadow → gold → near-white chrome glint), plus ONE broad confident
specular swipe across the upper-near quadrant of the tank — a single streak
sells "shiny" far better than four thin glints that mush to flat gold at 40px.
Midnight navy is the contrast trim/piping so the gold pops on both a bright day
sky and a dark night sky.

The chest is deliberately spare: a big white STAR breathing on a clean gold
field with the bold "1" in front — two elements, nothing else competing. The
HERO is the full-length shooter ARM SLEEVE down the near wing: a wide reflective
tube whose CONTINUOUS bright chrome seam runs the full length, raised to a
lighter steel mid-value so it separates hard from the navy trim and reads as the
second-loudest element after the gold tank. At 40px, in order of value: (1) the
gold tank + big white STAR, (2) the long chrome arm sleeve, (3) the gold star
headband, then the gold high-tops. Every kit piece stays INSIDE the base bird
footprint — the sleeve hugs the wing, the headband hugs the crown, nothing drops
below the feet line.
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
# Sleeve = the HERO. A cool STEEL ramp (not navy) so its mid-value lifts well
# clear of the navy trim/piping and the continuous chrome seam screams glossy
# metal — this is meant to be the second-loudest element after the gold tank.
_SLV_D  = (44, 58, 104)              # sleeve shadow (lifted off true navy)
_SLV    = (96, 122, 176)             # sleeve mid — bright steel, separates from navy
_SLV_H  = (196, 230, 250)            # sleeve chrome seam — near-white, very loud


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
    # ONE confident broad specular SWIPE across the upper-near quadrant — a single
    # 3px diagonal streak reads as a reflective highlight at 40px where four thin
    # glints just average back to flat gold. Cool chrome core inside it = the
    # metallic tell that survives the shrink.
    pygame.draw.line(surf, _GOLD_H, (BCX + 2, BCY - 5), (BCX + 11, BCY + 3), 3)
    pygame.draw.line(surf, _CHROME, (BCX + 4, BCY - 4), (BCX + 10, BCY + 1), 1)

    # Thin shoulder STRAPS at the wing roots — bare scarlet shoulder reads outside
    # each (the sleeveless tell), trimmed in navy so the gold edges stay crisp.
    _poly(surf, _GOLD, [(BCX - 11, BCY - 6), (BCX - 6, BCY - 9),
                        (BCX - 4, BCY - 5), (BCX - 8, BCY - 2)])      # off strap
    _poly(surf, _GOLD, [(BCX + 10, BCY - 6), (BCX + 5, BCY - 9),
                        (BCX + 3, BCY - 5), (BCX + 7, BCY - 2)])      # near strap
    # A single thin NAVY hem line frames the gold; the neckline piping is dropped
    # so the big white star has a clean uncluttered gold field to breathe on.
    pygame.draw.line(surf, _NAVY, (BCX - 11, BCY + 10), (BCX + 12, BCY + 10), 2)
    # Deep armhole scoops so the bare-shoulder, sleeveless cut is explicit at 40px.
    pygame.draw.arc(surf, _GOLD_D, (BCX + 3, BCY - 7, 11, 14), -1.0, 1.4, 2)
    pygame.draw.arc(surf, _GOLD_D, (BCX - 14, BCY - 7, 11, 14), 1.7, 4.2, 2)

    # ── BIG WHITE STAR behind the number — the all-star headline tell. Drawn on
    #    the chest, shadowed down-left so it survives a light day sky, with the
    #    bold white number "1" sitting in front (the showman's #1).
    sx, sy = BCX, BCY + 1
    _star(surf, _WHITE_D, sx, sy + 1, 8)                  # star shadow
    _star(surf, _WHITE, sx, sy, 8)                        # white star — kept solid
    # No gold star-eye: the centre stays clean white so the bold navy "1" is the
    # only thing reading on the star, and the star itself stays a crisp silhouette.
    # Bold "1" overlaid on the star centre — navy so it reads on the white star.
    pygame.draw.line(surf, _NAVY, (sx, sy - 5), (sx, sy + 5), 2)
    pygame.draw.line(surf, _NAVY, (sx - 2, sy - 3), (sx, sy - 5), 2)

    # ── GOLD-AND-WHITE HIGH-TOPS on the feet line. Chunky metallic boots reduced
    #    to the two reads that survive 40px: a gold boot with a navy lace stripe
    #    and ONE clean white sole line. The per-shoe toe glint is dropped — it was
    #    just noise at size. Sits ON the feet line (~HY+21..27), never below it.
    for fx in (26, 34):
        pygame.draw.rect(surf, _GOLD_D, (fx - 4, HY + 22, 9, 6), border_radius=2)
        pygame.draw.rect(surf, _GOLD, (fx - 4, HY + 21, 9, 4), border_radius=2)
        pygame.draw.line(surf, _NAVY, (fx - 3, HY + 23), (fx + 4, HY + 23), 1)
        pygame.draw.line(surf, _WHITE, (fx - 4, HY + 27), (fx + 5, HY + 27), 2)  # sole

    # ── GOLD STAR HEADBAND across the brow — bold metallic band hugging the crown
    #    with a 3-value gold sheen + a tiny white STAR badge at centre. Leaves
    #    Pip's eye + beak in the open below it.
    by = CROWN_Y + 5
    pygame.draw.line(surf, _GOLD_D, (HX - 12, by + 1), (HX + 13, by), 7)    # band shadow
    pygame.draw.line(surf, _GOLD, (HX - 12, by), (HX + 13, by - 1), 5)
    pygame.draw.line(surf, _GOLD_H, (HX - 10, by - 2), (HX + 6, by - 2), 1)  # chrome glint
    # Enlarged white STAR badge (r=4) reads as the head's hero detail; the navy
    # knot + tail are dropped — they merged with the face and added clutter, so
    # the gold band + star badge are now the head's only two elements.
    _star(surf, _WHITE_D, HX + 1, by + 1, 4)                                # badge shadow
    _star(surf, _WHITE, HX + 1, by, 4)                                      # star badge

    # ── FULL-LENGTH SHOOTER ARM SLEEVE down the near wing — THE HERO, drawn LAST
    #    so it sits in front of everything. A smooth tapered TUBE with a long
    #    bright chrome highlight seam running its length so it reads glossy/metal.
    #    Widened ~2px so the tube has real mass; spans BCX+8..18, BCY-4..+14,
    #    hugging the wing inside the footprint.
    sleeve = [(BCX + 8, BCY - 4), (BCX + 18, BCY - 3),
              (BCX + 19, BCY + 13), (BCX + 12, BCY + 14)]
    _poly(surf, _SLV, sleeve)
    # Steel shadow down the outer edge gives the wider tube its round cross-section.
    _poly(surf, _SLV_D, [(BCX + 16, BCY - 3), (BCX + 19, BCY + 1),
                         (BCX + 19, BCY + 13), (BCX + 15, BCY + 13)])
    # CONTINUOUS bright chrome seam running the FULL length of the inner face —
    # one unbroken 3px near-white stripe is the glossy hero read, with a 1px white
    # core to push the specular brightness past everything but the gold tank.
    pygame.draw.line(surf, _SLV_H, (BCX + 11, BCY - 3), (BCX + 13, BCY + 13), 3)
    pygame.draw.line(surf, _WHITE, (BCX + 11, BCY - 3), (BCX + 13, BCY + 13), 1)
    # Gold cuff bands top + bottom tie the sleeve back into the gold kit.
    pygame.draw.line(surf, _GOLD, (BCX + 8, BCY - 3), (BCX + 18, BCY - 2), 2)
    pygame.draw.line(surf, _GOLD, (BCX + 12, BCY + 13), (BCX + 19, BCY + 12), 2)
    pygame.draw.line(surf, _GOLD_H, (BCX + 9, BCY - 3), (BCX + 13, BCY - 3), 1)


build = store_skins._make_skin(_paint)
