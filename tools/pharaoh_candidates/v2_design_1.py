"""HORUS — the Falcon-God King  (pharaoh v2, RE-ROLL candidate 1).

Scratch exploration only — NOT registered in store_skins.BUILDERS.

The bolder pharaoh re-roll: instead of stacking a hat on Pip, HORUS reshapes
the HEAD ITSELF into a slate falcon — a hooked black beak replaces the parrot
beak and the head mass goes grey — so it reads as a falcon-headed god, totally
unlike a parrot, at 40px. The tall white+red Pschent double crown is the only
element allowed above CROWN_Y; everything body-worn (broad collar, was-scepter,
chest chevrons) stays strictly inside the base bird footprint because the
collision hitbox is a fixed ~10px circle and a visually bigger body would
mislead the player.

Paint-over: Pip keeps his scarlet body + flapping wings (so he still feels like
Pip in costume); a few grey falcon chest chevrons make the head and body agree.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Palette — five hero notes from the concept spec, each split into a few values
# so the shape survives the 40px downscale instead of flattening to one tone.
_HR_SLATE    = (58, 74, 92)        # #3A4A5C slate falcon head mass
_HR_SLATE_D  = (38, 50, 64)        # falcon head shadow / underside
_HR_SLATE_H  = (96, 116, 138)      # falcon head highlight (crown sheen)
_HR_WHITE    = (242, 239, 230)     # #F2EFE6 Hedjet white
_HR_WHITE_D  = (206, 202, 188)     # Hedjet shadow
_HR_WHITE_H  = (255, 254, 248)     # Hedjet specular
_HR_RED      = (192, 57, 43)       # #C0392B Deshret red
_HR_RED_D    = (140, 38, 30)       # Deshret shadow
_HR_RED_H    = (224, 96, 80)       # Deshret highlight
_HR_GOLD     = (232, 178, 58)      # #E8B23A gold
_HR_GOLD_D   = (176, 128, 36)
_HR_GOLD_H   = (255, 224, 140)
_HR_TURQ     = (31, 163, 154)      # #1FA39A wedjat turquoise
_HR_TURQ_D   = (20, 112, 106)
_HR_BEAK     = (24, 26, 30)        # near-black hooked beak
_HR_BEAK_H   = (70, 76, 86)        # beak ridge glint
_HR_CERE     = (236, 190, 70)      # yellow cere dot
_HR_TALON    = (28, 30, 36)        # dark talon recolor


def _paint(surf, _a):
    BCX, BCY = 32, 52              # body centre in composite space

    # ── Was-scepter, slung diagonally across the body (drawn FIRST so the body
    # and collar overlap its root; only the inner shaft reads). A slim gold rod
    # angled top-left → mid-right, kept thin + entirely inside the footprint so
    # it never balloons the body or reads as mass.
    s_top = (BCX - 8, BCY - 9)
    s_bot = (BCX + 8, BCY + 9)
    pygame.draw.line(surf, _HR_GOLD_D, (s_top[0] + 1, s_top[1] + 1),
                     (s_bot[0] + 1, s_bot[1] + 1), 3)
    pygame.draw.line(surf, _HR_GOLD, s_top, s_bot, 2)
    pygame.draw.line(surf, _HR_GOLD_H, s_top, (BCX, BCY), 1)
    # Jackal-head crook at the staff head — a small angular gold hook.
    _poly(surf, _HR_GOLD, [(s_top[0] - 2, s_top[1] + 1), (s_top[0] - 4, s_top[1] - 3),
                           (s_top[0], s_top[1] - 3), (s_top[0] + 1, s_top[1])])
    # Forked foot at the staff base — the was-scepter's twin prong.
    pygame.draw.line(surf, _HR_GOLD_D, s_bot, (s_bot[0] - 2, s_bot[1] + 3), 2)
    pygame.draw.line(surf, _HR_GOLD_D, s_bot, (s_bot[0] + 2, s_bot[1] + 3), 2)

    # ── Grey falcon chest-feather chevrons — so the recolored head and scarlet
    # body agree. Few + thin so they never read as added body mass; a stacked V
    # of slate strokes down the upper chest, set off-centre toward the front.
    for i, cy in enumerate((BCY - 4, BCY + 1, BCY + 6)):
        w = 8 - i * 2
        pygame.draw.lines(surf, _HR_SLATE_D, False,
                          [(BCX - w, cy - 2), (BCX + 1, cy + 2), (BCX + w + 2, cy - 2)], 2)

    # ── Broad collar (wesekh) — a slim turquoise+gold arc of thin banded rings
    # hugging the neck just under the head. Drawn as concentric thin arcs so it
    # reads as a collar, never as body bulk.
    col = pygame.Rect(BCX - 11, BCY - 17, 28, 18)
    pygame.draw.arc(surf, _HR_GOLD,  col, 3.55, 6.00, 3)
    pygame.draw.arc(surf, _HR_TURQ,  col.inflate(-5, -5), 3.60, 5.95, 2)
    pygame.draw.arc(surf, _HR_GOLD,  col.inflate(-9, -9), 3.65, 5.90, 2)

    # ── Dark talon recolor at the feet line (~HY+24). Two small dark claw clumps
    # ON the feet line, never below it, so the bird keeps its true size.
    for fx in (28, 35):
        pygame.draw.ellipse(surf, _HR_TALON, (fx - 3, HY + 22, 7, 5))
        for tx in (fx - 2, fx, fx + 2):
            pygame.draw.line(surf, _HR_TALON, (tx, HY + 25), (tx, HY + 27), 1)

    # ── FALCON HEAD MASS — recolor Pip's whole head to slate-grey. A clean round
    # skull that tapers to a strong brow over the beak so the profile already
    # reads predatory. Drawn large + bold so the dark head is the dominant value
    # block under the crown (the day read) and a solid mass at night.
    head = [(HX - 13, HY - 2), (HX - 11, HY - 10), (HX - 3, HY - 14),
            (HX + 7, HY - 13), (HX + 14, HY - 6), (HX + 16, HY + 1),
            (HX + 15, HY + 7), (HX + 8, HY + 12), (HX - 4, HY + 12),
            (HX - 12, HY + 6)]
    _poly(surf, _HR_SLATE_D, [(x, y + 1) for x, y in head])
    _poly(surf, _HR_SLATE, head)
    # Crown sheen — a lifted highlight across the top of the falcon skull.
    pygame.draw.ellipse(surf, _HR_SLATE_H, (HX - 8, HY - 11, 15, 7))

    # ── HOOKED BEAK — the hero re-shape. A bold black beak springing FORWARD off
    # the brow and hooking sharply DOWN past the right silhouette edge (the bird
    # faces right), so the profile reads falcon, not parrot, the instant it's
    # seen. Solid wedge → downturned talon point, with a ridge glint.
    beak = [(HX + 9, HY - 4), (HX + 23, HY - 2), (HX + 26, HY + 3),
            (HX + 22, HY + 4), (HX + 13, HY + 3), (HX + 10, HY + 1)]
    _poly(surf, _HR_BEAK, beak)
    # Downturned hook dropping off the tip — the predator curl.
    _poly(surf, _HR_BEAK, [(HX + 23, HY + 1), (HX + 27, HY + 3),
                           (HX + 24, HY + 9), (HX + 20, HY + 5)])
    pygame.draw.line(surf, _HR_BEAK_H, (HX + 10, HY - 3), (HX + 22, HY - 1), 1)
    # Yellow cere patch at the beak base (the falcon's fleshy nostril band).
    _poly(surf, _HR_CERE, [(HX + 8, HY - 4), (HX + 12, HY - 4),
                           (HX + 12, HY + 1), (HX + 8, HY + 1)])
    pygame.draw.circle(surf, (40, 30, 14), (HX + 10, HY - 2), 1)   # nostril dot

    # White cheek blaze — a clean pale wedge sweeping back/down behind the beak,
    # the falcon's signature malar mark; one bold shape that brightens the lower
    # face so the dark beak + eye read against it.
    _poly(surf, _HR_WHITE, [(HX + 8, HY + 2), (HX + 14, HY + 4),
                            (HX + 11, HY + 11), (HX - 1, HY + 11),
                            (HX - 1, HY + 5)])
    pygame.draw.line(surf, _HR_WHITE_D, (HX - 1, HY + 10), (HX + 11, HY + 10), 1)

    # ── EYE-OF-HORUS (wedjat) — ONE bold stroke as the face's hero mark: a large
    # almond eye with a dark pupil, a straight brow bar above, and the signature
    # teardrop tail curling down off the front. Drawn LARGE in turquoise so it
    # carries the face on day AND night; seated high on the slate brow.
    ex, ey = HX, HY - 4
    pygame.draw.line(surf, _HR_TURQ, (ex - 8, ey - 4), (ex + 6, ey - 3), 3)   # brow
    pygame.draw.line(surf, _HR_TURQ_D, (ex - 8, ey - 3), (ex + 6, ey - 2), 1)
    _poly(surf, _HR_WHITE_H, [(ex - 7, ey), (ex - 1, ey - 3), (ex + 6, ey),
                              (ex - 1, ey + 3)])                              # eye white
    pygame.draw.circle(surf, (16, 18, 22), (ex - 1, ey), 3)                   # pupil
    pygame.draw.circle(surf, _HR_TURQ, (ex - 1, ey), 3, 1)
    pygame.draw.circle(surf, _HR_WHITE_H, (ex - 2, ey - 1), 1)               # catchlight
    # The wedjat teardrop tail — the long marking curling down off the eye front.
    pygame.draw.lines(surf, _HR_TURQ, False,
                      [(ex - 6, ey + 2), (ex - 9, ey + 6), (ex - 5, ey + 8)], 2)

    # ── PSCHENT (the double crown) — the ONLY element allowed above CROWN_Y.
    # Built as a flared RED Deshret basket with a bulbous WHITE Hedjet cone
    # nested inside, a front curl wire, and a gold uraeus bump at the brow.
    cx = HX + 1
    base_y = CROWN_Y + 2          # crown seats just above the falcon skull

    # Deshret (red) basket — a flared trapezoid cup, widest at the brow.
    desh = [(cx - 13, base_y), (cx + 13, base_y), (cx + 11, base_y - 11),
            (cx - 11, base_y - 11)]
    _poly(surf, _HR_RED_D, [(x, y + 1) for x, y in desh])
    _poly(surf, _HR_RED, desh)
    # Deshret front rim + a left-side highlight band.
    pygame.draw.line(surf, _HR_RED_H, (cx - 11, base_y - 10),
                     (cx - 9, base_y - 1), 2)
    pygame.draw.line(surf, _HR_RED_D, (cx - 13, base_y), (cx + 13, base_y), 2)

    # Hedjet (white) cone nested inside, rising tall — the night-carrying value.
    hed = [(cx - 8, base_y - 9), (cx + 8, base_y - 9),
           (cx + 5, base_y - 22), (cx + 1, base_y - 27),
           (cx - 3, base_y - 22)]
    _poly(surf, _HR_WHITE_D, [(x + 1, y) for x, y in hed])
    _poly(surf, _HR_WHITE, hed)
    # Bulbous white knob at the cone tip (the Hedjet's rounded crown).
    pygame.draw.circle(surf, _HR_WHITE, (cx + 1, base_y - 27), 3)
    pygame.draw.circle(surf, _HR_WHITE_H, (cx, base_y - 28), 2)
    # Hedjet sheen — a tall pale highlight up the front face.
    pygame.draw.line(surf, _HR_WHITE_H, (cx - 3, base_y - 11),
                     (cx, base_y - 24), 2)

    # Front curl wire — the Deshret's signature spiral springing forward off the
    # basket front, a thin gold question-mark curl.
    pygame.draw.lines(surf, _HR_GOLD, False,
                      [(cx + 12, base_y - 4), (cx + 17, base_y - 5),
                       (cx + 18, base_y - 9), (cx + 15, base_y - 10)], 2)
    pygame.draw.circle(surf, _HR_GOLD_H, (cx + 15, base_y - 10), 1)

    # Gold uraeus (rearing cobra) bump at the brow — a tiny gold S over a hood,
    # the royal serpent, dead-centre-front where crown meets head.
    ux, uy = cx, base_y + 1
    _poly(surf, _HR_GOLD, [(ux - 3, uy + 2), (ux + 3, uy + 2),
                           (ux + 2, uy - 2), (ux - 2, uy - 2)])   # cobra hood
    pygame.draw.line(surf, _HR_GOLD, (ux, uy - 2), (ux + 1, uy - 5), 2)  # rearing neck
    pygame.draw.circle(surf, _HR_GOLD_H, (ux + 1, uy - 5), 1)             # head bead
    pygame.draw.circle(surf, _HR_RED, (ux + 1, uy - 5), 1)               # eye spot


build = store_skins._make_skin(_paint)
