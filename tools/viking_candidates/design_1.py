"""STORMBEARD — classic raider berserker candidate for the viking redraw.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_viking`` is untouched.

ROUND 2 rebuild. R1 read at 40px as "grey helmet on a brown blob": the horns
curled INWARD and barely cleared the dome, the beard / mantle / belt / boots
were all the same brown so the lower mass merged, the back-shield read as mud,
and the scarlet macaw was buried. The art-director ranked the fixes; this
rebuild follows them in order.

The whole costume now rests on TWO value tiers plus the bird's own scarlet:

  * HORNS are the hero. A creamy pair sweeps outward-then-up in an S-curve,
    tips clearing the dome ~9px each side, 7px-thick roots tapering to 2px,
    each carrying a 1px dark keyline (#2A2118) so the cream survives both
    bright sky AND the grey dome — the horn-pair breaking the top outline is
    ~70% of the Viking read.
  * BEARD is pushed near-black (#241A11) so it reads OFF the scarlet body and
    the warm mid-brown is RESERVED for the fur mantle only — two tiers, no
    brown-on-brown merge. The studded belt + boot cuffs are gone (sub-pixel
    noise that muddied the lower mass).
  * SHIELD is promoted to the back-silhouette hero: enlarged, pushed further
    off the back so a clean disc-arc breaks the rear outline, a bright iron
    rim keyline against the sky, and a bold gold boss on a saturated red field
    (no sub-pixel plank seams).
  * The SCARLET chest stays visible as a confident wedge so it still reads as
    "Pip dressed as a Viking", and the red body is the value foil for the dark
    beard.
  * HELM is one unmistakable tell: a shrunk-down dome so the horns dominate,
    capped by a bold high-contrast brow-band + nasal as a single dark shape.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Two value tiers carry the costume so nothing merges brown-on-brown.
# Tier 1 — near-black beard (reads OFF the scarlet body).
_BEARD   = (36, 26, 17)            # #241A11
_BEARD_D = (22, 16, 10)
_BEARD_H = (74, 56, 36)
# Tier 2 — warm mid-brown, RESERVED for the fur mantle only.
_FUR     = (120, 92, 60)
_FUR_D   = (82, 62, 40)
_FUR_H   = (170, 140, 100)
# Iron helm — bright cool grey so the dome lifts off the scarlet head.
_IRON    = (132, 144, 158)
_IRON_D  = (70, 78, 90)
_IRON_H  = (204, 212, 224)
# Horn — warm cream with a dark keyline so it survives sky AND dome.
_HORN    = (238, 228, 204)
_HORN_H  = (255, 250, 234)
_HORN_KEY = (42, 33, 24)           # #2A2118 — the 1px horn keyline
# Shield — saturated raider red field + gold boss + bright iron rim.
_RED     = (196, 52, 40)
_RED_D   = (138, 34, 28)
_RED_H   = (236, 110, 94)
_GOLD    = (231, 182, 64)
_GOLD_D  = (172, 130, 36)
_GOLD_H  = (255, 234, 152)


def _horn(surf, sgn):
    """One cream horn sweeping outward-then-up in an S-curve from a 7px root to
    a 2px tip, ~9px clear of the dome, with a 1px dark keyline along its whole
    length so the cream reads against both bright sky and the grey dome."""
    rx = HX + sgn * 7                       # root tucks under the dome rim
    ry = CROWN_Y + 4
    # outward-then-up S: out low, swing wide, hook the tip up. The back horn
    # (sgn -1) sweeps a touch wider so it clears the dome instead of hiding
    # behind it as a detached speck after the downscale.
    out = 11 if sgn < 0 else 10
    pts = [
        (rx, ry),
        (rx + sgn * (out - 2), ry - 2),     # sweep OUT past the dome
        (rx + sgn * out, ry - 11),          # widest point, rising
        (rx + sgn * (out - 4), ry - 20),    # tip hooks up (tip ~9px clear)
    ]
    # Dark keyline first (thick), then the cream body inside it — gives every
    # cream stroke a 1px dark edge on both flanks at once.
    pygame.draw.lines(surf, _HORN_KEY, False, pts, 8)
    pygame.draw.lines(surf, _HORN, False, pts, 6)
    pygame.draw.lines(surf, _HORN_H, False, pts[:3], 2)   # lit outer flank
    # Bright wedged tip so the 2px point survives the downscale, keyed dark.
    tip = pts[-1]
    pygame.draw.circle(surf, _HORN_KEY, tip, 3)
    pygame.draw.circle(surf, _HORN, tip, 2)
    pygame.draw.circle(surf, _HORN_H, (tip[0] - sgn, tip[1] - 1), 1)


def _paint(surf, _a):
    cy = CROWN_Y

    # ── round shield slung across the BACK — the back-silhouette hero. Drawn
    #    FIRST so the body sits in front and a clean disc-arc breaks the rear
    #    outline. Bright iron rim keyline + gold boss on a saturated red field.
    scx, scy = HX - 35, HY + 17
    sr = 17
    pygame.draw.circle(surf, _IRON_H, (scx, scy), sr + 1)       # rim keyline (sky)
    pygame.draw.circle(surf, _RED_D, (scx, scy), sr)
    pygame.draw.circle(surf, _RED, (scx, scy), sr - 2)
    pygame.draw.circle(surf, _RED_H, (scx - 5, scy - 6), 5)     # lit quadrant
    pygame.draw.circle(surf, _IRON, (scx, scy), sr, 2)          # bright iron rim
    pygame.draw.circle(surf, _IRON_H, (scx, scy), sr, 1)
    # Gold boss dome dead-centre — the disc's hero pop.
    pygame.draw.circle(surf, _GOLD_D, (scx, scy), 6)
    pygame.draw.circle(surf, _GOLD, (scx, scy), 5)
    pygame.draw.circle(surf, _GOLD_H, (scx - 2, scy - 2), 2)

    # ── fur shoulder-mantle ringing the neck — the ONLY warm mid-brown. Drawn
    #    before the head so the head + beard sit in front; it breaks the upper
    #    body outline on both sides as a soft ruff, value-separated from beard.
    mcx, mcy = HX - 7, HY + 11
    pygame.draw.ellipse(surf, _FUR_D, (mcx - 17, mcy - 4, 32, 16))
    pygame.draw.ellipse(surf, _FUR, (mcx - 16, mcy - 4, 30, 13))
    for i in range(-4, 5):
        tx = mcx + i * 4
        _poly(surf, _FUR, [(tx - 3, mcy + 2), (tx + 3, mcy + 2),
                           (tx, mcy + 8 + (abs(i) % 2) * 2)])
    for i in (-3, 0, 3):
        pygame.draw.line(surf, _FUR_H, (mcx + i * 4, mcy + 1),
                         (mcx + i * 4, mcy + 5), 1)

    # ── near-black braided beard ballooning from the beak-base to the chest.
    #    Pushed near-black so it reads OFF the scarlet body and is the dark
    #    foil the visible red chest plays against.
    pygame.draw.ellipse(surf, _BEARD_D, (HX - 5, HY + 3, 20, 15))
    pygame.draw.ellipse(surf, _BEARD, (HX - 4, HY + 2, 18, 13))
    for bx, blen in ((HX, 6), (HX + 7, 5)):
        for j in range(blen):
            yy = HY + 12 + j * 2
            r = 3 if j < blen - 1 else 2
            pygame.draw.circle(surf, _BEARD if j % 2 else _BEARD_D, (bx, yy), r)
        pygame.draw.line(surf, _BEARD_H, (bx - 1, HY + 12),
                         (bx - 1, HY + 12 + blen), 1)
    # One gold beard-ring — the single warm glint allowed on the dark mass.
    pygame.draw.circle(surf, _GOLD_D, (HX + 7, HY + 21), 3)
    pygame.draw.circle(surf, _GOLD, (HX + 7, HY + 21), 3, 1)
    pygame.draw.circle(surf, _GOLD_H, (HX + 6, HY + 20), 1)

    # ── HORNS — the hero pair, drawn before the dome so their roots tuck under
    #    the helm rim while the tips sweep ~9px clear on each side.
    _horn(surf, -1)
    _horn(surf, 1)

    # ── iron dome — deliberately SMALL so the horns dominate the top. A tight
    #    riveted half-dome capping the crown.
    pygame.draw.ellipse(surf, _IRON_D, (HX - 10, cy - 4, 21, 15))
    pygame.draw.ellipse(surf, _IRON, (HX - 9, cy - 4, 19, 12))
    pygame.draw.ellipse(surf, _IRON_H, (HX - 5, cy - 3, 8, 4))

    # ── bold brow-band + nasal as a single high-contrast DARK shape — the one
    #    unmistakable helmet tell. Dark iron band across the brow with a bright
    #    top rim, dropping into a wide nasal bar between the eyes.
    pygame.draw.line(surf, _IRON_D, (HX - 10, cy + 5), (HX + 11, cy + 4), 5)
    pygame.draw.line(surf, _IRON_H, (HX - 10, cy + 3), (HX + 11, cy + 2), 1)
    pygame.draw.rect(surf, _IRON_D, (HX + 1, cy + 4, 4, 12))
    pygame.draw.rect(surf, _IRON, (HX + 1, cy + 5, 2, 10))
    for rx in (HX - 7, HX + 8):
        pygame.draw.circle(surf, _IRON_H, (rx, cy + 4), 1)


build = store_skins._make_skin(_paint)
