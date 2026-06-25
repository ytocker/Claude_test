"""GOLD-LADEN — the treasure raider candidate for the pirate redraw.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_pirate`` is untouched.

Concept: keep the pirate IDENTITY (slate tricorn + white skull cockade) but
bury the scarlet macaw under PLUNDER. Gold reads beautifully on scarlet, so the
body stays the default red bird and every new object is gold layered across
multiple zones for sheer wealth-mass:

  * head — tricorn whose brim band carries a ROW of tiny coins/gems, plus a red
    gem set into the skull cockade's brow,
  * chest — THREE draped coin-chains arcing across the body, each a beaded line
    of 2px gold dots with a bright highlight pip so the arcs stay distinct and
    don't merge into a blob when the bird shrinks,
  * belt — a bulging leather coin pouch with a couple of coins spilling out,
  * foot — a curved gold hook hint over the near foot.

The 40px read, in order of value: a scarlet bird, the white skull + gold brim
anchoring it as a PIRATE, then a cascade of gold across the chest reading as
wealth. Strokes are ≥2px and each gold mass gets a single bright highlight so
the gold pops on day AND night without muddying.
"""
import math
import pygame

from game import store_skins
from game.store_skins import (
    HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, PARROT_DY, _poly,
)

# Gold owns this build — a deep core, the mid body tone, and a bright highlight
# so each gold mass throws one hot pip that survives the brutal downscale.
_GOLD     = (255, 205, 70)         # #FFCD46 body gold
_GOLD_D   = (200, 146, 42)         # #C8922A deep gold (shadow / under-edge)
_GOLD_H   = (255, 240, 160)        # #FFF0A0 hot highlight pip
_GEM_RED  = (210, 53, 58)          # #D2353A ruby
_GEM_GRN  = (54, 178, 107)         # #36B26B emerald
_LEATHER  = (90, 58, 34)           # #5A3A22 pouch leather
_LEATHER_D = (60, 38, 22)          # pouch shadow / seam

# Tricorn felt — reuse the production pirate's mid-slate so the hat lifts off the
# scarlet head exactly like the original (the identity read we must preserve).
_FELT    = store_skins._PIR_FELT
_FELT_D  = store_skins._PIR_FELT_D
_FELT_H  = store_skins._PIR_FELT_H
_SKULL   = store_skins._PIR_SKULL


def _coin(surf, cx, cy, r):
    """A small struck coin — deep rim, gold face, one hot pip. r>=2 so the rim
    survives downscale; the highlight is offset up-left for a consistent light."""
    pygame.draw.circle(surf, _GOLD_D, (cx, cy), r)
    pygame.draw.circle(surf, _GOLD, (cx, cy), max(1, r - 1))
    pygame.draw.circle(surf, _GOLD_H, (cx - 1, cy - 1), 1)


def _chain(surf, p0, p1, p2, beads):
    """A draped coin-chain: a quadratic-bezier arc of gold beads from p0 through
    control p1 to p2. Each bead is a 2px gold dot over a deep-gold under-dot, so
    the arc reads as a distinct beaded line — not a smear — at 40px. A few beads
    get a bright pip to keep the cascade sparkling."""
    pts = []
    for i in range(beads):
        t = i / (beads - 1)
        mt = 1 - t
        x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
        y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    # Deep-gold shadow line first so the chain reads as one continuous object,
    # then the bright beads on top — the line stops the beads dissolving when
    # the bird shrinks and the gaps close up.
    pygame.draw.lines(surf, _GOLD_D, False, pts, 2)
    for i, (x, y) in enumerate(pts):
        pygame.draw.circle(surf, _GOLD, (int(x), int(y)), 2)
        if i % 2 == 0:
            pygame.draw.circle(surf, _GOLD_H, (int(x - 1), int(y - 1)), 1)


def _paint(surf, _a):
    # ── THREE draped coin-chains across the chest (drawn FIRST so the pouch,
    #    belt and any hat detail can overlap them). Body centre ~(32, 52); the
    #    arcs sag low across the breast and stagger in depth so the cascade
    #    reads as layered loot, not one band. This is the hero density.
    bcx, bcy = 31, 52
    _chain(surf, (bcx - 16, bcy - 6), (bcx, bcy + 4),  (bcx + 16, bcy - 4), 9)
    _chain(surf, (bcx - 15, bcy - 1), (bcx, bcy + 10), (bcx + 16, bcy + 1), 10)
    _chain(surf, (bcx - 13, bcy + 4), (bcx, bcy + 14), (bcx + 15, bcy + 6), 9)

    # A single fat medallion hanging off the lowest chain so the eye lands on a
    # hero gold spot at chest centre.
    _coin(surf, bcx + 1, bcy + 14, 3)
    pygame.draw.circle(surf, _GEM_RED, (bcx + 1, bcy + 14), 1)

    # ── bulging coin pouch on the belt (near/right of the waist) with a couple
    #    of coins spilling out the cinched top. Leather mass + seam, gold spill.
    px, py = bcx + 14, bcy + 9
    pygame.draw.ellipse(surf, _LEATHER_D, (px - 6, py - 4, 13, 14))
    pygame.draw.ellipse(surf, _LEATHER, (px - 5, py - 3, 11, 12))
    # Cinched neck of the pouch.
    pygame.draw.line(surf, _LEATHER_D, (px - 4, py - 3), (px + 5, py - 3), 2)
    pygame.draw.line(surf, _GOLD_D, (px - 4, py - 4), (px + 5, py - 4), 1)
    # Coins spilling over the lip.
    _coin(surf, px - 2, py - 5, 2)
    _coin(surf, px + 3, py - 4, 2)
    _coin(surf, px + 1, py + 9, 2)   # one tumbling out the bottom

    # ── curved gold hook over the NEAR (right) foot, below the body. Feet sit
    #    below body centre; a short gold shank into a C-curve so it reads as a
    #    pirate hook, not a claw.
    fx, fy = bcx + 6, bcy + 22
    pygame.draw.line(surf, _GOLD_D, (fx, fy - 6), (fx, fy), 3)
    pygame.draw.line(surf, _GOLD, (fx, fy - 6), (fx, fy), 2)
    hook = [(fx, fy), (fx + 3, fy + 2), (fx + 4, fy + 5),
            (fx + 2, fy + 7), (fx - 1, fy + 6)]
    pygame.draw.lines(surf, _GOLD_D, False, hook, 3)
    pygame.draw.lines(surf, _GOLD, False, hook, 2)
    pygame.draw.circle(surf, _GOLD_H, (fx - 1, fy - 4), 1)

    # ── gold hoop earring under the head (kept from the identity).
    pygame.draw.circle(surf, _GOLD, (HX - 8, HY + 10), 3, 2)
    pygame.draw.circle(surf, _GOLD_H, (HX - 9, HY + 9), 1)

    # ── tricorn lifted off the crown (same geometry as production so it still
    #    reads PIRATE), but the brim band is now a ROW OF COINS/GEMS, not a plain
    #    rope — the head's share of the wealth read.
    cy = CROWN_Y - 3
    brim = [(HX - 17, cy + 5), (HX - 5, cy - 7), (HX + 4, cy - 8),
            (HX + 16, cy + 4), (HX + 6, cy + 9), (HX - 6, cy + 9)]
    _poly(surf, _FELT_D, brim)
    inner = [(HX - 14, cy + 4), (HX - 4, cy - 5), (HX + 3, cy - 6),
             (HX + 13, cy + 3), (HX + 5, cy + 7), (HX - 5, cy + 7)]
    _poly(surf, _FELT, inner)
    _poly(surf, _FELT_H, [(HX - 4, cy - 5), (HX + 3, cy - 6),
                          (HX + 2, cy - 2), (HX - 3, cy - 2)])

    # Coin/gem-studded brim band tracing the front edge. A deep-gold base line
    # carries the band; small coins + two gems sit on it so the head sparkles.
    band = [(HX - 15, cy + 4), (HX - 4, cy - 5), (HX + 3, cy - 6),
            (HX + 14, cy + 3)]
    pygame.draw.lines(surf, _GOLD_D, False, band, 3)
    pygame.draw.lines(surf, _GOLD, False, band, 2)
    studs = [(HX - 12, cy + 1), (HX - 6, cy - 3), (HX + 1, cy - 5),
             (HX + 8, cy - 2), (HX + 12, cy + 1)]
    for i, (gx, gy) in enumerate(studs):
        if i == 1:
            pygame.draw.circle(surf, _GEM_RED, (gx, gy), 2)
            pygame.draw.circle(surf, (255, 200, 200), (gx - 1, gy - 1), 1)
        elif i == 3:
            pygame.draw.circle(surf, _GEM_GRN, (gx, gy), 2)
            pygame.draw.circle(surf, (200, 255, 220), (gx - 1, gy - 1), 1)
        else:
            _coin(surf, gx, gy, 2)

    # ── white skull cockade dead-centre-front with a RED GEM set in its brow —
    #    the kept identity anchor, now jewelled.
    sx, sy = HX, cy + 2
    pygame.draw.circle(surf, _SKULL, (sx, sy), 4)
    _poly(surf, _SKULL, [(sx - 3, sy + 2), (sx + 3, sy + 2),
                         (sx + 1, sy + 5), (sx - 1, sy + 5)])
    pygame.draw.circle(surf, (40, 30, 40), (sx - 2, sy), 1)
    pygame.draw.circle(surf, (40, 30, 40), (sx + 2, sy), 1)
    # Red brow gem set above the skull's eyes.
    pygame.draw.circle(surf, _GOLD_D, (sx, sy - 3), 2)
    pygame.draw.circle(surf, _GEM_RED, (sx, sy - 3), 1)


build = store_skins._make_skin(_paint)
