"""GOLD-LADEN — the treasure raider candidate for the pirate redraw.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_pirate`` is untouched.

Concept: keep the pirate IDENTITY (slate tricorn + white skull cockade) but
drape the scarlet macaw in PLUNDER. The body stays scarlet and reads scarlet
FIRST — gold is the second beat, hung in a tight HIERARCHY so it never eats the
bird at 40px:

  * head — original continuous gold brim band (the proven identity read) plus a
    single red brow gem on the skull cockade; no studs (they speckle at scale),
  * chest — ONE bright HERO coin-chain high on the breast, with clean SCARLET
    owning the whole belly below it so the gold reads as draped on a red bird,
    not a gold blob,
  * chest centre — ONE hero medallion as the single hot focal (beats nine pips),
  * belt — a bulging leather coin pouch (the best non-gold beat) with one bright
    spill-coin at its lip as a secondary focal,
  * foot — a curved gold hook outlined in dark gold so it survives night sky.

The 40px read, in value order: a SCARLET bird, the white skull + gold brim
anchoring it as a PIRATE, then ONE bright chain + medallion reading as wealth.
Target balance ~60/40 scarlet/gold so the bird never disappears under loot.
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


def _chain(surf, p0, p1, p2, beads, hero):
    """A draped coin-chain: a quadratic-bezier arc of gold beads from p0 through
    control p1 to p2. ``hero=True`` draws the single bright strand — 3px gold
    beads over a deep-gold line, ONE shared light read with no per-bead highlight
    pips (those are the primary speckle-noise source at 40px)."""
    pts = []
    for i in range(beads):
        t = i / (beads - 1)
        mt = 1 - t
        x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
        y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    if hero:
        pygame.draw.lines(surf, _GOLD_D, False, pts, 3)
        for x, y in pts:
            pygame.draw.circle(surf, _GOLD, (int(x), int(y)), 3)
    else:
        # Recessed strand: dark line + dark beads only — deliberately dim.
        pygame.draw.lines(surf, _GOLD_D, False, pts, 2)
        for x, y in pts:
            pygame.draw.circle(surf, _GOLD_D, (int(x), int(y)), 2)


def _paint(surf, _a):
    # ── ONE draped coin-chain across the chest (drawn FIRST so the pouch can
    #    overlap). Body centre ~(31, 52). Endpoints pulled INWARD (bcx ± 12) so
    #    the chain doesn't reach the wing edge — the scarlet wing reads as a clean
    #    red shape framing the gold, and the empty scarlet belly below it is what
    #    makes the gold read as DRAPED ON A RED BIRD, not a gold blob.
    bcx, bcy = 31, 52
    # ONE hero strand only — bright, high on the breast. The low recessed strand
    # is dropped: at 40px it didn't read as a 2nd chain, it just filled the red
    # gap. Clean scarlet now owns the whole belly below this single chain, which
    # is what sells "gold draped on a red bird".
    _chain(surf, (bcx - 12, bcy - 4), (bcx, bcy + 4),  (bcx + 12, bcy - 2), 8, True)

    # ── HERO MEDALLION at chest centre: the single hot focal of the whole build.
    #    One bright disc with a ruby boss beats nine scattered highlight pips.
    mx, my = bcx + 1, bcy + 4
    pygame.draw.circle(surf, _GOLD_D, (mx, my), 4)
    pygame.draw.circle(surf, _GOLD, (mx, my), 3)
    pygame.draw.circle(surf, _GEM_RED, (mx, my), 1)
    pygame.draw.circle(surf, _GOLD_H, (mx - 1, my - 2), 1)

    # ── bulging coin pouch on the belt (near/right of the waist) — the best
    #    non-gold beat. Bumped +1px and given ONE bright spill-coin at the lip as
    #    a secondary focal. Spilled-coin count kept low so gold stays second.
    px, py = bcx + 14, bcy + 9
    pygame.draw.ellipse(surf, _LEATHER_D, (px - 7, py - 4, 15, 16))
    pygame.draw.ellipse(surf, _LEATHER, (px - 6, py - 3, 13, 14))
    # Cinched neck of the pouch.
    pygame.draw.line(surf, _LEATHER_D, (px - 5, py - 3), (px + 6, py - 3), 2)
    pygame.draw.line(surf, _GOLD_D, (px - 5, py - 4), (px + 6, py - 4), 1)
    # One bright coin perched at the lip — the pouch's secondary focal.
    _coin(surf, px, py - 5, 2)

    # ── curved gold hook over the NEAR (right) foot, below the body. A short gold
    #    shank into a C-curve so it reads as a pirate hook, not a claw. A 1px dark
    #    outline behind the whole curve anchors it on near-black NIGHT sky.
    fx, fy = bcx + 6, bcy + 22
    hook = [(fx, fy), (fx + 3, fy + 2), (fx + 4, fy + 5),
            (fx + 2, fy + 7), (fx - 1, fy + 6)]
    # Dark anchor pass (shank + curve), then DEEP gold only — no bright pip — so
    # the hook stays dim and the value fight is won by scarlet. The only full
    # bright _GOLD masses left on the bird are the hat rope, the one hero chain,
    # the medallion and the single spill-coin.
    pygame.draw.line(surf, _LEATHER_D, (fx, fy - 6), (fx, fy), 4)
    pygame.draw.lines(surf, _LEATHER_D, False, hook, 4)
    pygame.draw.line(surf, _GOLD_D, (fx, fy - 6), (fx, fy), 2)
    pygame.draw.lines(surf, _GOLD_D, False, hook, 2)

    # ── gold hoop earring under the head (kept from the identity).
    pygame.draw.circle(surf, _GOLD, (HX - 8, HY + 10), 3, 2)
    pygame.draw.circle(surf, _GOLD_H, (HX - 9, HY + 9), 1)

    # ── tricorn lifted off the crown (same geometry as production so it still
    #    reads PIRATE). The brim band reverts to the ORIGINAL single continuous
    #    gold rope — the cleanest, proven identity read. Studs are gone: at 40px
    #    a coin/gem row on the band just speckled.
    cy = CROWN_Y - 3
    brim = [(HX - 17, cy + 5), (HX - 5, cy - 7), (HX + 4, cy - 8),
            (HX + 16, cy + 4), (HX + 6, cy + 9), (HX - 6, cy + 9)]
    _poly(surf, _FELT_D, brim)
    inner = [(HX - 14, cy + 4), (HX - 4, cy - 5), (HX + 3, cy - 6),
             (HX + 13, cy + 3), (HX + 5, cy + 7), (HX - 5, cy + 7)]
    _poly(surf, _FELT, inner)
    _poly(surf, _FELT_H, [(HX - 4, cy - 5), (HX + 3, cy - 6),
                          (HX + 2, cy - 2), (HX - 3, cy - 2)])

    # Thin gold rope on the FRONT brim edge only — matched to production's 2px
    # bright over 1px highlight so slate felt out-masses gold ~3:1. Clipped to the
    # front edge (HX-15 → HX+14): no gold wrapping the head or bleeding down the
    # right felt, which is what made the hat read as a gold helmet.
    band = [(HX - 15, cy + 4), (HX - 4, cy - 5), (HX + 3, cy - 6),
            (HX + 14, cy + 3)]
    pygame.draw.lines(surf, _GOLD_D, False, band, 2)
    pygame.draw.lines(surf, _GOLD_H, False,
                      [(HX - 13, cy + 3), (HX - 4, cy - 6), (HX + 3, cy - 7)], 1)

    # ── white skull cockade dead-centre-front with a RED BROW GEM — the kept
    #    identity anchor, jewelled with the head's ONE wealth accent (no studs).
    sx, sy = HX, cy + 2
    pygame.draw.circle(surf, _SKULL, (sx, sy), 4)
    _poly(surf, _SKULL, [(sx - 3, sy + 2), (sx + 3, sy + 2),
                         (sx + 1, sy + 5), (sx - 1, sy + 5)])
    pygame.draw.circle(surf, (40, 30, 40), (sx - 2, sy), 1)
    pygame.draw.circle(surf, (40, 30, 40), (sx + 2, sy), 1)
    # Red brow gem set above the skull's eyes — 2px ruby with a hot pink pip.
    pygame.draw.circle(surf, _GEM_RED, (sx, sy - 3), 2)
    pygame.draw.circle(surf, (255, 200, 200), (sx - 1, sy - 4), 1)


build = store_skins._make_skin(_paint)
