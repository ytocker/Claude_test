"""THE GRIDIRON — the American-football candidate (DESIGN 3 of the SPORTS set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so no live
skin is touched.

Concept: dress Pip as a helmeted gridiron player. The HERO is the football
HELMET — a rounded navy shell over the head + a CAGE FACEMASK wrapping the FRONT
of the face over the beak — the strongest, most armoured head silhouette of the
whole sports collection. A hint of Pip's eye shows above the cage so the bird
stays a parrot, not a mascot.

No football: the ball ships separately as a matching PARCEL item, so the costume
must read "American football" from the HELMET + kit alone. That works because
the cage facemask over the beak is the instant gridiron tell at any size.

The body is a bulky PADDED JERSEY: navy with a big white number, and the
shoulder pads are SUGGESTED by a raised, shaded shoulder SHAPE painted over the
existing silhouette — never extra width (the collision footprint is fixed).

At 40px the read, in order of value: (1) the rounded navy helmet shell with its
white crown stripe, (2) the dark cage facemask wrapping the beak (the instant
"American football" tell), (3) the navy padded jersey with a bold white number.
Helmet may rise above CROWN_Y; everything else stays inside the base footprint.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Team navy carries three values so the rounded shell still reads as a curved
# helmet (not a flat blob) after the 40px downscale; the jersey reuses the same
# family so helmet + jersey read as one kit.
_GR_NAVY    = (27, 42, 107)        # #1B2A6B team navy — helmet shell / jersey
_GR_NAVY_D  = (16, 26, 72)         # shadow / shell underside
_GR_NAVY_H  = (58, 80, 168)        # lit top of the shell + raised shoulder
_GR_MASK    = (236, 240, 248)      # bright facemask bars — highest-value face note
_GR_FRAME   = (10, 12, 22)         # near-black cage frame so the bars sit in dark gaps
_GR_WHITE   = (242, 242, 242)      # #F2F2F2 jersey number / stripe
_GR_BLACK   = (24, 24, 28)         # eye-black smudge


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── PADDED JERSEY over the torso. The SHOULDER PADS are SUGGESTED by a raised,
    #    lit navy shoulder yoke painted over the existing body — it adds value/shape,
    #    NOT width, so the collision footprint is untouched (footprint law). A darker
    #    underside seam below the yoke sells the pad bulk overhanging the chest.
    # Yoke spans the upper torso WITHIN the silhouette; the lit top edge reads as
    # the rounded pad cap catching light.
    yoke = [(BCX - 14, BCY - 6), (BCX - 7, BCY - 11), (BCX + 7, BCY - 11),
            (BCX + 15, BCY - 5), (BCX + 14, BCY + 1), (BCX - 13, BCY + 1)]
    _poly(surf, _GR_NAVY, yoke)
    # Lit cap along the top of each shoulder so the pads read as raised volume.
    pygame.draw.line(surf, _GR_NAVY_H, (BCX - 13, BCY - 5), (BCX - 7, BCY - 9), 2)
    pygame.draw.line(surf, _GR_NAVY_H, (BCX + 6, BCY - 9), (BCX + 14, BCY - 4), 2)
    # Dark seam under the pad line — the overhang shadow that gives the bulk depth.
    pygame.draw.line(surf, _GR_NAVY_D, (BCX - 12, BCY), (BCX + 13, BCY), 2)

    # Lower jersey body below the pads (navy) so the whole torso is one kit colour.
    jersey = [(BCX - 13, BCY + 1), (BCX + 14, BCY + 1), (BCX + 12, BCY + 12),
              (BCX - 11, BCY + 12)]
    _poly(surf, _GR_NAVY, jersey)
    pygame.draw.line(surf, _GR_NAVY_D, (BCX - 11, BCY + 11), (BCX + 12, BCY + 11), 1)
    # No white shoulder stripe: at 40px a bright bar on the shoulder reads as part of
    # the facemask. Keep the cage the ONLY high-value note up top so it wins the read.

    # ── BIG WHITE NUMBER on the chest. One CRISP "8" as two stacked loops drawn in
    #    bold 2px stroke with NO shadow ring, so at 40px it stays a single clean shape
    #    instead of a fuzzy doubled blob. Centred inside the lower jersey panel.
    nx, ny = BCX + 1, BCY + 6
    pygame.draw.circle(surf, _GR_WHITE, (nx, ny - 2), 3, 2)         # upper loop
    pygame.draw.circle(surf, _GR_WHITE, (nx, ny + 4), 4, 2)         # lower loop

    # ── HELMET — the HERO. A rounded navy SHELL domes over the head (rising above
    #    CROWN_Y, the only element allowed to), three-valued so the curve reads as a
    #    hard shell. Crucially the shell BROW stops ABOVE the beak and the jaw sweeps
    #    BACK to the throat — leaving a FACE OPENING where the beak pokes out, exactly
    #    where a real helmet frames the face. The cage then clamps over that open beak.
    hcx, hcy = HX + 1, HY - 2
    # Shell mass: domed top, a brow that ends above the beak (hcx+13, hcy+2), then the
    # jaw curves DOWN-AND-BACK to the throat so the beak/lower-face stays uncovered.
    shell = [(hcx - 12, hcy + 8), (hcx - 13, hcy - 3), (hcx - 8, hcy - 12),
             (hcx + 4, hcy - 14), (hcx + 13, hcy - 9), (hcx + 14, hcy - 4),
             (hcx + 13, hcy + 2), (hcx + 7, hcy + 6), (hcx, hcy + 10),
             (hcx - 4, hcy + 12)]
    _poly(surf, _GR_NAVY_D, [(x, y + 1) for x, y in shell])
    _poly(surf, _GR_NAVY, shell)
    # Lit dome across the top so the shell reads as a curved hard surface.
    pygame.draw.line(surf, _GR_NAVY_H, (hcx - 8, hcy - 9), (hcx + 4, hcy - 11), 3)
    pygame.draw.line(surf, _GR_NAVY_H, (hcx + 4, hcy - 11), (hcx + 12, hcy - 6), 2)
    # White center stripe over the dome — the helmet's hero trim, crown to brow.
    pygame.draw.line(surf, _GR_WHITE, (hcx - 1, hcy - 14), (hcx, hcy - 2), 2)
    # Ear-hole — a navy/black dot where a real shell vents, so it reads as a helmet.
    pygame.draw.circle(surf, _GR_NAVY_D, (hcx - 6, hcy + 3), 3)
    pygame.draw.circle(surf, _GR_BLACK, (hcx - 6, hcy + 3), 1)

    # ── FACE in the helmet opening: redraw the BEAK so it clearly pokes out of the
    #    shell brow (the base beak may be partly painted over), plus the eye just under
    #    the brow. The beak is what the cage clamps over, so it must read first.
    # Beak (composite of base beak_pts shifted +PARROT_DY): a small hooked horn poking
    # right out of the face opening.
    beak = [(hcx + 7, hcy + 1), (hcx + 13, hcy + 4), (hcx + 10, hcy + 8),
            (hcx + 4, hcy + 6)]
    _poly(surf, (236, 168, 58), beak)                 # warm beak so it reads as face
    pygame.draw.polygon(surf, (150, 96, 24), beak, 1)
    # Eye just under the brow, above the beak — the hint of Pip.
    ex, ey = hcx + 5, hcy - 1
    pygame.draw.circle(surf, _GR_WHITE, (ex, ey), 2)
    pygame.draw.circle(surf, (30, 26, 34), (ex + 1, ey), 1)
    # EYE-BLACK smudge just under the eye — the athlete tell.
    pygame.draw.line(surf, _GR_BLACK, (ex - 1, ey + 2), (ex + 2, ey + 2), 1)

    # ── FACEMASK — a SMALL CAGE clamped over the BEAK, the hero gridiron tell. It is
    #    sized to the beak so the beak reads THROUGH the bars (cage on the face), never
    #    a box beside the head. Mostly DARK FRAME: a thin near-black ring with SHORT
    #    thin grey bars; the bright fill is killed so the dark gaps read as the cage.
    #    Bars angle down-and-forward to follow the front of the face over the beak.
    bx0, bx1 = hcx + 5, hcx + 13        # tight to the beak, x≈53..61
    by0, by1 = hcy + 1, hcy + 8         # over the beak body, y≈40..47
    # Thin near-black perimeter ring tight to the beak (NOT a filled block) so the beak
    # reads through the open interior.
    pygame.draw.lines(surf, _GR_FRAME, True,
                      [(bx0, by0), (bx1, by0 + 1), (bx1 - 1, by1),
                       (bx0 - 1, by1 - 1)], 1)
    # TWO short grey bars across the beak, angled down-and-forward, with a clear dark
    # gap between — the cage read. Thin (1px) light accents in a dark frame.
    pygame.draw.line(surf, _GR_MASK, (bx0, by0 + 2), (bx1 - 1, by0 + 3), 1)
    pygame.draw.line(surf, _GR_MASK, (bx0, by1 - 2), (bx1 - 1, by1 - 1), 1)
    # ONE short vertical post near the beak tip tying the bars; dark gaps either side.
    pygame.draw.line(surf, _GR_MASK, (bx1 - 2, by0 + 2), (bx1 - 2, by1 - 1), 1)


build = store_skins._make_skin(_paint)
