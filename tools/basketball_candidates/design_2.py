"""THE STREETBALLER — the basketball candidate (DESIGN 2 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched.

Concept: dress Pip as a playground legend, an attitude apart from the clean
league pro. There is NO ball — it ships separately as a matching PARCEL item,
so the costume must read as STREETBALL from the KIT alone. The swagger tells
are carried by the gear: a backwards SNAPBACK cap (brim pointing off the back
of the crown — a distinct headgear silhouette no league uniform has), a baggy
red reversible TANK with a loose low neckline, a grey compression arm SLEEVE
running down the near wing, chunky high-tops with bold laces, and — the HERO,
drawn LAST in front of everything — a thick GOLD ROPE CHAIN looping the neck
and dipping onto the chest, rendered as alternating gold + gold-shadow links
so it reads as a chunky chain rather than a smooth ring even at 40px.

At 40px the read, in value order: (1) the gold chain dipping on the chest +
the backwards-cap silhouette breaking the crown's outline backward, (2) the
loud red baggy tank, (3) the grey arm sleeve down the near wing, then the
high-tops. Every kit piece stays INSIDE the base bird footprint — the chain
sits on the chest, the cap hugs the crown, nothing dangles below the feet.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Loud blacktop palette: dark cap/laces ground the loud red tank and let the
# warm gold chain pop hardest as the hero. The red tank is a mid value so the
# white neckline trim + the gold both separate from the scarlet head above.
_BLK     = (22, 24, 30)              # #16181E blacktop black (cap, laces)
_BLK_H   = (52, 56, 66)             # black highlight / brim underside
_RED     = (216, 54, 47)            # #D8362F red tank
_RED_D   = (160, 36, 32)            # tank shadow / armhole
_RED_H   = (240, 96, 88)            # tank highlight
_GOLD    = (232, 178, 58)           # #E8B23A gold chain link
_GOLD_D  = (158, 116, 30)           # gold-shadow link (the every-other tick)
_GOLD_H  = (255, 224, 138)          # gold glint
_SLV     = (90, 94, 107)            # #5A5E6B sleeve grey
_SLV_D   = (60, 64, 76)             # sleeve shadow
_SLV_H   = (140, 144, 158)          # sleeve seam highlight
_WHT     = (244, 244, 248)          # #F4F4F8 white trim / laces glint
_WHT_D   = (196, 198, 208)          # white shadow / sole


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── BACKWARDS SNAPBACK first, behind the chain. The brim points off the
    #    BACK of the crown (toward the tail side, off-x) so the silhouette is a
    #    flat-billed cap worn backwards — a headgear shape no clean league
    #    uniform carries. The dome hugs the crown; an exposed adjuster strap +
    #    button sit where the brim would normally be at the front.
    cy = CROWN_Y + 3
    # Crown dome over the back of the head.
    _poly(surf, _BLK, [(HX - 14, cy + 6), (HX - 12, cy - 2),
                       (HX - 4, cy - 6), (HX + 6, cy - 5),
                       (HX + 9, cy + 2), (HX + 8, cy + 7)])
    # Dome highlight band so the cap reads round, not a flat blob.
    _poly(surf, _BLK_H, [(HX - 11, cy - 1), (HX - 4, cy - 4),
                         (HX + 4, cy - 3), (HX + 2, cy - 1), (HX - 6, cy - 1)])
    # Flat brim jutting BACKWARD off the crown (off-x side) — the backwards tell.
    _poly(surf, _BLK, [(HX - 14, cy + 2), (HX - 22, cy + 4),
                       (HX - 22, cy + 7), (HX - 13, cy + 7)])
    pygame.draw.line(surf, _BLK_H, (HX - 21, cy + 4), (HX - 15, cy + 4), 1)  # brim top edge
    # Snapback adjuster strap + button left exposed at the FRONT (worn-back tell).
    pygame.draw.line(surf, _WHT_D, (HX + 6, cy + 1), (HX + 9, cy + 5), 2)
    pygame.draw.circle(surf, _BLK_H, (HX + 7, cy + 2), 1)

    # ── BAGGY TANK over the torso, drawn before the chain/sleeve. Looser cut +
    #    a low loose neckline (a wide shallow scoop) and a slightly flared baggy
    #    hem so it reads streetwear, not a tailored singlet. Held inside the
    #    footprint (hem ~BCY+14).
    tank = [(BCX - 12, BCY - 5), (BCX + 11, BCY - 5),
            (BCX + 14, BCY + 3), (BCX + 13, BCY + 14),
            (BCX - 12, BCY + 14), (BCX - 15, BCY + 3)]
    _poly(surf, _RED, tank)
    # Off-side shadow panel gives the baggy tank dressed-up form.
    _poly(surf, _RED_D, [(BCX - 15, BCY + 2), (BCX - 11, BCY),
                         (BCX - 10, BCY + 13), (BCX - 13, BCY + 14)])
    # Near-side sheen down the loose drape.
    pygame.draw.line(surf, _RED_H, (BCX + 9, BCY - 2), (BCX + 11, BCY + 11), 2)
    # LOW LOOSE neckline — a wide, shallow scoop with white trim so the baggy
    # low cut is explicit (vs the pro's tight crew).
    pygame.draw.lines(surf, _RED_D, False,
                      [(BCX - 8, BCY - 4), (BCX, BCY + 1), (BCX + 8, BCY - 4)], 3)
    pygame.draw.lines(surf, _WHT, False,
                      [(BCX - 8, BCY - 5), (BCX, BCY), (BCX + 8, BCY - 5)], 1)
    # Deep armhole on the near side so the sleeveless baggy cut reads.
    pygame.draw.arc(surf, _RED_D, (BCX + 4, BCY - 6, 12, 16), -1.1, 1.3, 2)
    # Flared baggy hem with a white trim band.
    pygame.draw.line(surf, _WHT, (BCX - 12, BCY + 13), (BCX + 12, BCY + 13), 1)

    # ── HIGH-TOPS on the feet line. Chunky black-and-white boots with BOLD
    #    cross laces + a grey sole, sitting ON the feet line (~HY+21..27), never
    #    below it, so the bird keeps its true size.
    for fx in (26, 34):
        pygame.draw.rect(surf, _WHT_D, (fx - 4, HY + 22, 9, 6), border_radius=2)
        pygame.draw.rect(surf, _WHT, (fx - 4, HY + 21, 9, 4), border_radius=2)
        # Black ankle collar so the HIGH-top cut reads.
        pygame.draw.rect(surf, _BLK, (fx - 4, HY + 20, 4, 4), border_radius=1)
        # Bold cross laces.
        pygame.draw.line(surf, _BLK, (fx - 2, HY + 21), (fx + 2, HY + 24), 1)
        pygame.draw.line(surf, _BLK, (fx + 2, HY + 21), (fx - 2, HY + 24), 1)
        pygame.draw.line(surf, _WHT_D, (fx - 4, HY + 27), (fx + 5, HY + 27), 2)  # sole
        pygame.draw.line(surf, _GOLD, (fx + 1, HY + 21), (fx + 4, HY + 21), 1)   # gold toe glint

    # ── COMPRESSION ARM SLEEVE down the near wing, drawn over the tank. A clean
    #    grey tube hugging the forearm with a bright seam highlight so it reads
    #    as a fitted sleeve (the streetball forearm tell), not a wristband.
    sx, sy = BCX + 13, BCY + 1
    pygame.draw.line(surf, _SLV_D, (sx - 1, sy - 2), (sx + 4, sy + 13), 8)  # sleeve shadow
    pygame.draw.line(surf, _SLV, (sx - 1, sy - 2), (sx + 3, sy + 12), 6)    # sleeve tube
    pygame.draw.line(surf, _SLV_H, (sx - 2, sy - 1), (sx + 2, sy + 11), 2)  # seam highlight
    pygame.draw.line(surf, _BLK, (sx - 2, sy + 12), (sx + 4, sy + 14), 3)   # ribbed cuff
    pygame.draw.line(surf, _SLV_H, (sx - 1, sy + 12), (sx + 3, sy + 13), 1)

    # ── GOLD ROPE CHAIN — the HERO, drawn LAST over everything. It loops the
    #    neck just under the cap and dips onto the chest to (BCX, BCY+1). Built
    #    as a string of LINKS: a gold base stroke, then alternating gold + dark
    #    gold ticks stepped along it so the eye reads chunky linked beads, not a
    #    smooth wire ring — the texture survives the 40px shrink.
    pts = [(BCX - 9, BCY - 6), (BCX - 7, BCY - 2),
           (BCX - 3, BCY + 1), (BCX + 1, BCY + 2),
           (BCX + 5, BCY + 1), (BCX + 9, BCY - 2),
           (BCX + 11, BCY - 6)]
    pygame.draw.lines(surf, _GOLD_D, False, pts, 5)   # chain underside / depth
    pygame.draw.lines(surf, _GOLD, False, pts, 4)     # chain body
    # Alternating link ticks: walk the polyline and drop gold / dark-gold beads
    # so the chain reads as discrete segments.
    seg = []
    for a, b in zip(pts, pts[1:]):
        steps = 3
        for i in range(steps):
            t = i / steps
            seg.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    for i, (lx, ly) in enumerate(seg):
        c = _GOLD_H if i % 2 == 0 else _GOLD_D
        pygame.draw.circle(surf, c, (int(round(lx)), int(round(ly))), 1)
    # Chunky pendant link where the chain dips lowest on the chest.
    pygame.draw.circle(surf, _GOLD_D, (BCX + 1, BCY + 3), 3)
    pygame.draw.circle(surf, _GOLD, (BCX + 1, BCY + 2), 2)
    pygame.draw.circle(surf, _GOLD_H, (BCX, BCY + 1), 1)


build = store_skins._make_skin(_paint)
