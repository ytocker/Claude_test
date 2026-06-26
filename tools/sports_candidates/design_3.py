"""THE GRIDIRON — the American-football candidate (DESIGN 3 of the SPORTS set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so no live
skin is touched.

Concept: dress Pip as a helmeted gridiron player. The HERO is the football
HELMET — a rounded navy shell over the head + a grey 2-bar FACEMASK cage over
the beak + a chin strap — the strongest, most armoured head silhouette of the
whole sports collection. A hint of Pip's eye shows behind the mask so the bird
stays a parrot, not a mascot.

The body is a bulky PADDED JERSEY: navy with a big white number, and the
shoulder pads are SUGGESTED by a raised, shaded shoulder SHAPE painted over the
existing silhouette — never extra width (the collision footprint is fixed). A
brown FOOTBALL with white laces is tucked at the near wing, and an eye-black
smudge sits under the showing eye.

At 40px the read, in order of value: (1) the rounded navy helmet shell, (2) the
grey horizontal facemask bars over the beak (the instant "American football"
tell), (3) the navy padded jersey with a bold white number on the chest, and
(4) the brown football at the wing. Helmet may rise above CROWN_Y; everything
else stays inside the base footprint and above the feet line.
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
_GR_MASK    = (184, 190, 200)      # #B8BEC8 grey facemask cage
_GR_MASK_D  = (120, 126, 138)      # facemask shadow bar (depth on the cage)
_GR_MASK_H  = (224, 228, 236)      # facemask glint
_GR_WHITE   = (242, 242, 242)      # #F2F2F2 jersey number / laces / stripe
_GR_WHITE_D = (196, 198, 204)      # number shadow so it isn't a flat decal
_GR_BALL    = (110, 67, 38)        # #6E4326 football brown
_GR_BALL_D  = (74, 44, 24)         # football shadow / seam
_GR_BALL_H  = (150, 96, 58)        # football top highlight
_GR_BLACK   = (24, 24, 28)         # eye-black smudge / strap shadow
_GR_STRAP   = (208, 198, 176)      # tan chin-strap


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── FOOTBALL tucked at the near wing (drawn FIRST so the wing/jersey overlap
    #    its inner edge → reads CARRIED against the body, not floating). A pointed
    #    brown oval with white laces; kept inside the footprint and above the feet
    #    line. The pointed ends + laces are what make it read "football" and not a
    #    generic ball at 40px.
    fcx, fcy = BCX + 13, BCY + 5
    ball = [(fcx - 9, fcy), (fcx - 4, fcy - 6), (fcx + 4, fcy - 6),
            (fcx + 9, fcy), (fcx + 4, fcy + 6), (fcx - 4, fcy + 6)]
    _poly(surf, _GR_BALL_D, [(x, y + 1) for x, y in ball])
    _poly(surf, _GR_BALL, ball)
    # Pointed tip caps so the oval reads as a prolate spheroid, not a circle.
    _poly(surf, _GR_BALL, [(fcx - 9, fcy), (fcx - 12, fcy - 2), (fcx - 12, fcy + 2)])
    _poly(surf, _GR_BALL, [(fcx + 9, fcy), (fcx + 12, fcy - 2), (fcx + 12, fcy + 2)])
    pygame.draw.line(surf, _GR_BALL_H, (fcx - 6, fcy - 4), (fcx + 5, fcy - 4), 1)
    # White lace band — a short center stripe + cross-ticks, the football tell.
    pygame.draw.line(surf, _GR_WHITE, (fcx - 3, fcy), (fcx + 4, fcy), 2)
    for lx in (fcx - 2, fcx, fcx + 2, fcx + 4):
        pygame.draw.line(surf, _GR_WHITE, (lx, fcy - 2), (lx, fcy + 2), 1)

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
    # A single white shoulder stripe on the near pad — the classic jersey trim that
    # adds a high-value note up top without crowding the number.
    pygame.draw.line(surf, _GR_WHITE, (BCX + 6, BCY - 8), (BCX + 13, BCY - 3), 2)
    pygame.draw.line(surf, _GR_NAVY_D, (BCX + 6, BCY - 6), (BCX + 12, BCY - 1), 1)

    # ── BIG WHITE NUMBER on the chest (a bold "8" reads cleanly at 40px as two
    #    stacked loops). Drawn as two ring outlines with a shadow offset so it reads
    #    as a stitched-on numeral catching light, not a flat sticker. Kept centred
    #    and large but inside the lower jersey panel.
    nx, ny = BCX + 1, BCY + 6
    pygame.draw.circle(surf, _GR_WHITE_D, (nx + 1, ny - 2), 3, 2)   # upper loop shadow
    pygame.draw.circle(surf, _GR_WHITE_D, (nx + 1, ny + 4), 4, 2)   # lower loop shadow
    pygame.draw.circle(surf, _GR_WHITE, (nx, ny - 2), 3, 2)         # upper loop
    pygame.draw.circle(surf, _GR_WHITE, (nx, ny + 4), 4, 2)         # lower loop

    # ── HELMET — the HERO. A rounded navy SHELL domes over the head (rising above
    #    CROWN_Y, the only element allowed to), three-valued so the curve reads as a
    #    hard shell. The jaw flares down past the cheek to read as a full helmet, an
    #    ear-hole sits where a real shell has one, and a small chin strap loops under.
    hcx, hcy = HX + 1, HY - 2
    # Shell mass: domed top + jaw flare. Shadow underlay first for a hard lower edge.
    shell = [(hcx - 12, hcy + 8), (hcx - 13, hcy - 3), (hcx - 8, hcy - 12),
             (hcx + 4, hcy - 14), (hcx + 13, hcy - 9), (hcx + 16, hcy - 1),
             (hcx + 15, hcy + 7), (hcx + 9, hcy + 12), (hcx - 4, hcy + 12)]
    _poly(surf, _GR_NAVY_D, [(x, y + 1) for x, y in shell])
    _poly(surf, _GR_NAVY, shell)
    # Lit dome across the top so the shell reads as a curved hard surface.
    pygame.draw.line(surf, _GR_NAVY_H, (hcx - 8, hcy - 9), (hcx + 4, hcy - 11), 3)
    pygame.draw.line(surf, _GR_NAVY_H, (hcx + 4, hcy - 11), (hcx + 12, hcy - 6), 2)
    # White center stripe over the dome — the helmet's hero trim, crown to brow.
    pygame.draw.line(surf, _GR_WHITE, (hcx - 1, hcy - 14), (hcx, hcy - 2), 2)
    # Ear-hole + a navy jaw shadow so the shell reads as a 3D helmet, not a cap.
    pygame.draw.circle(surf, _GR_NAVY_D, (hcx - 6, hcy + 3), 3)
    pygame.draw.circle(surf, _GR_BLACK, (hcx - 6, hcy + 3), 1)

    # Chin strap looping from the jaw under the beak — tan so it reads against navy.
    pygame.draw.line(surf, _GR_STRAP, (hcx - 9, hcy + 8), (hcx + 4, hcy + 13), 2)
    pygame.draw.line(surf, _GR_NAVY_D, (hcx - 9, hcy + 10), (hcx + 4, hcy + 14), 1)

    # ── FACEMASK — a grey horizontal cage over the beak: a vertical center post +
    #    TWO horizontal bars, with a dark shadow bar behind for cage depth. This is
    #    the instant "American football" read, so the bars are bold (2px) and bright.
    #    A hint of Pip's eye is kept visible ABOVE the top bar, behind the cage.
    mfx = hcx + 8                       # cage sits forward, over the beak
    top_y, bot_y = hcy - 1, hcy + 7
    # Shadow cage first (offset down/right) so the bright bars read as a raised cage.
    pygame.draw.line(surf, _GR_MASK_D, (mfx - 1, top_y + 1), (mfx + 9, top_y + 2), 3)
    pygame.draw.line(surf, _GR_MASK_D, (mfx - 1, bot_y + 1), (mfx + 8, bot_y + 1), 3)
    # The two bright horizontal bars + vertical post tying them — the cage read.
    pygame.draw.line(surf, _GR_MASK, (mfx - 1, top_y), (mfx + 9, top_y + 1), 2)
    pygame.draw.line(surf, _GR_MASK, (mfx - 1, bot_y), (mfx + 8, bot_y), 2)
    pygame.draw.line(surf, _GR_MASK, (mfx + 8, top_y), (mfx + 7, bot_y), 2)
    pygame.draw.line(surf, _GR_MASK, (mfx, top_y), (mfx - 1, bot_y), 1)
    pygame.draw.line(surf, _GR_MASK_H, (mfx, top_y - 1), (mfx + 8, top_y), 1)

    # ── A hint of Pip behind the mask: the near eye showing above the top cage bar
    #    + an EYE-BLACK smudge under it, so the parrot stays legible and the player
    #    reads "athlete," not "robot." Eye sits between the shell brow and top bar.
    ex, ey = hcx + 6, hcy - 4
    pygame.draw.circle(surf, _GR_WHITE, (ex, ey), 2)
    pygame.draw.circle(surf, (30, 26, 34), (ex + 1, ey), 1)
    # Eye-black: two short smudge ticks under the eye (the gridiron face-paint tell).
    pygame.draw.line(surf, _GR_BLACK, (ex - 1, ey + 3), (ex + 3, ey + 3), 2)


build = store_skins._make_skin(_paint)
