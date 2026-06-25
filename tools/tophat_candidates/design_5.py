"""DESIGN 5 — THE DANDY (jazz-age bon vivant) · scratch tophat candidate.

A FULL gentleman outfit for the ``skin_tophat`` store costume: black topper
with a lavender grosgrain band, dove-lavender tailcoat opening to a vivid
emerald waistcoat wedge, an emerald-and-gold ascot, a scarlet rose
boutonnière, tortoiseshell spectacles + curled moustache, an ivory dress
cane, and two-tone spectator spats.

Exploration only — wrapped by ``store_skins._make_skin`` and NOT registered
in ``store_skins.BUILDERS``. The charm of this look is mid-value pastels, so
the read at 40px is protected by a saturated EMERALD wedge + the dark hat as
the value anchors, with a clean dark outline holding the pale coat off a
bright day sky. Layer order mirrors the pirate: behind (cane) → lavender coat
→ emerald wedge → ascot → rose → head/hat → face.
"""
from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly
import pygame


# ── concept palette (per the spec) + derived shadow/highlight steps ──────────
_DN_LAV     = (200, 194, 218)     # #C8C2DA dove-lavender coat
_DN_LAV_D   = (150, 144, 172)     # coat shadow / fold
_DN_LAV_H   = (228, 224, 240)     # coat highlight ridge
_DN_HAT     = (21, 23, 28)        # #15171C near-black topper
_DN_HAT_D   = (10, 11, 15)
_DN_HAT_H   = (66, 70, 82)        # cool silk sheen on the crown
_DN_EMER    = (31, 122, 77)       # #1F7A4D emerald waistcoat / ascot (the hero)
_DN_EMER_D  = (18, 80, 50)
_DN_EMER_H  = (70, 176, 120)
_DN_GOLD    = (229, 190, 72)      # #E5BE48 buttons / watch-chain / cane
_DN_GOLD_D  = (160, 126, 40)
_DN_GOLD_H  = (255, 232, 150)
_DN_ROSE    = (194, 27, 30)       # #C21B1E scarlet boutonnière (Pip's native red)
_DN_ROSE_D  = (132, 16, 20)
_DN_ROSE_H  = (236, 92, 86)
_DN_IVORY   = (236, 228, 206)     # cane shaft / spat cream
_DN_IVORY_D = (190, 180, 156)
_DN_TAN     = (176, 138, 92)      # spat tan toe
_DN_TAN_D   = (132, 100, 62)
_DN_OUTLINE = (32, 28, 40)        # clean dark edge against a bright sky


def _paint(surf, _a):
    # ── 1 · DRESS CANE — slung diagonally BEHIND the body (painted first so the
    # coat covers all but the parts that overshoot the silhouette). Ivory shaft
    # from the slung wing down past the feet, gold ferrule + a gold knob grip
    # that breaks the outline against the sky. Dark underlay first so the pale
    # ivory stick keeps an edge wherever it crosses the bright coat or sky.
    grip = (HX - 16, HY + 8)
    tip  = (HX - 28, HY + 38)
    pygame.draw.line(surf, _DN_OUTLINE, grip, tip, 5)
    pygame.draw.line(surf, _DN_IVORY,   grip, tip, 3)
    pygame.draw.line(surf, _DN_IVORY_D, (grip[0] - 1, grip[1] + 1),
                     (tip[0] - 1, tip[1] + 1), 1)
    # Gold ferrule tip + a round gold knob at the grip — the bright cane tells.
    pygame.draw.circle(surf, _DN_OUTLINE, tip, 3)
    pygame.draw.circle(surf, _DN_GOLD_D, tip, 2)
    pygame.draw.circle(surf, _DN_GOLD,   (tip[0], tip[1] - 1), 1)
    pygame.draw.circle(surf, _DN_OUTLINE, grip, 4)
    pygame.draw.circle(surf, _DN_GOLD_D,  grip, 3)
    pygame.draw.circle(surf, _DN_GOLD,    grip, 2)
    pygame.draw.circle(surf, _DN_GOLD_H,  (grip[0] - 1, grip[1] - 1), 1)

    # ── 2 · LAVENDER TAILCOAT — painted OVER the scarlet body. Two shoulder
    # panels flare down and out to the waist, opening at the centre to expose the
    # emerald wedge. A dark outline traces the coat edge so the pale dove-lavender
    # never dissolves into a bright day sky.
    cx = 32
    coat = [(cx - 12, HY + 6), (cx - 16, HY + 30), (cx - 6, HY + 34),
            (cx, HY + 22),                                   # centre notch (open)
            (cx + 6, HY + 34), (cx + 16, HY + 30), (cx + 12, HY + 6)]
    _poly(surf, _DN_OUTLINE, [(x, y + 1) for (x, y) in coat])  # drop edge
    _poly(surf, _DN_LAV, coat)
    # Shoulder/fold shading on each panel + a highlight ridge down the near side.
    _poly(surf, _DN_LAV_D, [(cx - 16, HY + 30), (cx - 13, HY + 14),
                            (cx - 9, HY + 16), (cx - 7, HY + 32), (cx - 6, HY + 34)])
    _poly(surf, _DN_LAV_D, [(cx + 16, HY + 30), (cx + 13, HY + 14),
                            (cx + 9, HY + 16), (cx + 7, HY + 32), (cx + 6, HY + 34)])
    pygame.draw.line(surf, _DN_LAV_H, (cx - 8, HY + 9), (cx - 11, HY + 27), 1)
    pygame.draw.line(surf, _DN_LAV_H, (cx + 8, HY + 9), (cx + 11, HY + 27), 1)
    # Peaked lapels framing the open front — a darker lavender so the V reads.
    _poly(surf, _DN_LAV_D, [(cx - 11, HY + 7), (cx - 2, HY + 9),
                            (cx - 5, HY + 22), (cx - 9, HY + 16)])
    _poly(surf, _DN_LAV_D, [(cx + 11, HY + 7), (cx + 2, HY + 9),
                            (cx + 5, HY + 22), (cx + 9, HY + 16)])

    # ── 3 · EMERALD WAISTCOAT WEDGE — the saturated HERO, bold and central so the
    # pastel coat has a high-chroma anchor that holds day AND night. A bright V
    # of emerald filling the open coat front, outlined dark, with a lighter ridge.
    wedge = [(cx - 6, HY + 9), (cx + 6, HY + 9), (cx + 4, HY + 26),
             (cx, HY + 30), (cx - 4, HY + 26)]
    _poly(surf, _DN_OUTLINE, [(x, y + 1) for (x, y) in wedge])
    _poly(surf, _DN_EMER, wedge)
    _poly(surf, _DN_EMER_D, [(cx + 2, HY + 11), (cx + 6, HY + 9),
                             (cx + 4, HY + 26), (cx + 1, HY + 24)])
    pygame.draw.line(surf, _DN_EMER_H, (cx - 3, HY + 11), (cx - 1, HY + 24), 1)

    # Three gold waistcoat buttons down the centre of the wedge.
    for by in (HY + 13, HY + 18, HY + 23):
        pygame.draw.circle(surf, _DN_GOLD_D, (cx, by), 2)
        pygame.draw.circle(surf, _DN_GOLD,   (cx, by), 1)
    # Slim gold watch-chain swagging across the belly from a button to the pocket.
    pygame.draw.lines(surf, _DN_GOLD_D, False,
                      [(cx, HY + 18), (cx + 3, HY + 24), (cx + 7, HY + 22)], 2)
    pygame.draw.lines(surf, _DN_GOLD, False,
                      [(cx, HY + 18), (cx + 3, HY + 23), (cx + 7, HY + 21)], 1)

    # ── 4 · ASCOT / CRAVAT — bright emerald-and-gold puff at the throat, sitting
    # just under the head where the wedge meets the collar. A small saturated
    # blob carries the colour up to the face so the wedge isn't an island.
    ax, ay = cx, HY + 6
    _poly(surf, _DN_OUTLINE, [(ax - 5, ay - 2), (ax + 5, ay - 2),
                              (ax + 4, ay + 5), (ax - 4, ay + 5)])
    _poly(surf, _DN_EMER, [(ax - 4, ay - 2), (ax + 4, ay - 2),
                           (ax + 3, ay + 4), (ax - 3, ay + 4)])
    pygame.draw.line(surf, _DN_EMER_H, (ax - 2, ay - 1), (ax - 1, ay + 3), 1)
    # Gold ascot pin glinting at the knot.
    pygame.draw.circle(surf, _DN_GOLD,   (ax, ay + 1), 1)
    pygame.draw.circle(surf, _DN_GOLD_H, (ax - 1, ay), 1)

    # ── 5 · ROSE BOUTONNIÈRE — scarlet bloom on the near lapel (a nod to Pip's
    # native red), a small layered red flower with a green leaf flick.
    rx, ry = cx - 8, HY + 11
    pygame.draw.circle(surf, _DN_OUTLINE, (rx, ry), 4)
    pygame.draw.circle(surf, _DN_ROSE_D, (rx, ry), 3)
    pygame.draw.circle(surf, _DN_ROSE,   (rx, ry), 2)
    pygame.draw.circle(surf, _DN_ROSE_H, (rx - 1, ry - 1), 1)
    pygame.draw.line(surf, _DN_EMER_D, (rx - 2, ry + 3), (rx - 4, ry + 6), 2)  # leaf

    # ── 6 · TWO-TONE SPECTATOR SPATS over the feet — cream vamp + tan toe cap, so
    # the dandy is dressed head to toe. Drawn before the hat so headgear can blit
    # last, but they sit at the feet and don't overlap.
    for fx in (28, 36):
        pygame.draw.ellipse(surf, _DN_OUTLINE, (fx - 4, 62, 9, 7))
        pygame.draw.ellipse(surf, _DN_IVORY,   (fx - 3, 62, 7, 5))
        pygame.draw.ellipse(surf, _DN_TAN_D,   (fx - 1, 63, 5, 4))
        pygame.draw.ellipse(surf, _DN_TAN,     (fx, 63, 3, 3))
        pygame.draw.line(surf, _DN_IVORY_D, (fx - 2, 65), (fx + 2, 65), 1)  # spat seam

    # ── 7 · TOP HAT — black topper rising above the crown with a wide LAVENDER
    # grosgrain band (the colourful twist on the hat itself). Dark silk so it
    # anchors the value structure on any sky.
    cy = CROWN_Y
    # Brim — wide ellipse with a bright top edge so the silhouette reads.
    pygame.draw.ellipse(surf, _DN_HAT_D, (HX - 17, cy + 1, 34, 8))
    pygame.draw.ellipse(surf, _DN_HAT,   (HX - 16, cy, 32, 5))
    pygame.draw.line(surf, _DN_HAT_H, (HX - 13, cy + 1), (HX + 13, cy + 1), 1)
    # Tall cylindrical crown rising well above the head.
    top_y = cy - 17
    pygame.draw.rect(surf, _DN_HAT_D, (HX - 9, top_y, 19, 19))
    pygame.draw.rect(surf, _DN_HAT,   (HX - 8, top_y, 16, 18))
    pygame.draw.line(surf, _DN_HAT_H, (HX - 6, top_y + 1), (HX - 6, cy - 4), 2)
    # Crisp light top rim — keeps the black off a dark night sky.
    pygame.draw.ellipse(surf, _DN_HAT_H, (HX - 9, top_y - 2, 19, 6))
    pygame.draw.ellipse(surf, _DN_HAT,   (HX - 8, top_y - 1, 17, 4))
    # Wide LAVENDER grosgrain band at the base of the crown — the hat's colour.
    pygame.draw.rect(surf, _DN_LAV_D, (HX - 9, cy - 5, 19, 6))
    pygame.draw.rect(surf, _DN_LAV,   (HX - 8, cy - 5, 17, 5))
    pygame.draw.line(surf, _DN_LAV_H, (HX - 7, cy - 5), (HX + 7, cy - 5), 1)

    # ── 8 · FACE — pencil-thin curled moustache + round tortoiseshell SPECTACLES
    # (two small rings) instead of a monocle, for the jazz-age look.
    # Spectacles: two gold-brown rings over both eyes + a bridge.
    lx, rx2 = HX + 2, HX + 9
    sy2 = HY
    pygame.draw.circle(surf, _DN_GOLD_D, (lx, sy2), 3, 1)
    pygame.draw.circle(surf, _DN_GOLD_D, (rx2, sy2), 3, 1)
    pygame.draw.circle(surf, _DN_GOLD,   (lx, sy2), 2, 1)
    pygame.draw.circle(surf, _DN_GOLD,   (rx2, sy2), 2, 1)
    pygame.draw.line(surf, _DN_GOLD, (lx + 2, sy2 - 1), (rx2 - 2, sy2 - 1), 1)  # bridge
    pygame.draw.circle(surf, (255, 255, 255), (lx - 1, sy2 - 1), 1)            # glint
    # Pencil-thin curled moustache under the beak — two strands flicking up.
    mx, my = HX + 7, HY + 7
    pygame.draw.lines(surf, _DN_OUTLINE, False,
                      [(mx - 5, my), (mx - 1, my + 1), (mx - 3, my - 2)], 1)
    pygame.draw.lines(surf, _DN_OUTLINE, False,
                      [(mx + 5, my), (mx + 1, my + 1), (mx + 3, my - 2)], 1)


build = store_skins._make_skin(_paint)
