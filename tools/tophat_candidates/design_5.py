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
# Coat base dropped ~12% in value to #B0AAC6 so the lavender reads as a CRISP
# SHAPE against the bright day biome instead of melting into it; the original
# #C8C2DA is reserved for a single highlight ridge.
_DN_LAV     = (176, 170, 198)     # #B0AAC6 dove-lavender coat (lifted off sky)
_DN_LAV_D   = (138, 132, 162)     # coat shadow / fold
_DN_LAV_H   = (200, 194, 218)     # #C8C2DA single highlight ridge
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
    # The ferrule tip is left ivory (no gold) — gold is reserved for the ONE
    # accent so it doesn't smear. The cane KNOB at the grip is that single
    # strong gold tell: a fat round knob breaking the outline against the sky.
    pygame.draw.circle(surf, _DN_OUTLINE, tip, 3)
    pygame.draw.circle(surf, _DN_IVORY,   tip, 2)
    pygame.draw.circle(surf, _DN_OUTLINE, grip, 5)
    pygame.draw.circle(surf, _DN_GOLD_D,  grip, 4)
    pygame.draw.circle(surf, _DN_GOLD,    grip, 3)
    pygame.draw.circle(surf, _DN_GOLD_H,  (grip[0] - 1, grip[1] - 1), 1)

    # ── 2 · LAVENDER TAILCOAT — painted OVER the scarlet body. Two shoulder
    # panels flare down and out to the waist, opening at the centre to expose the
    # emerald wedge. The RIGHT panel is pushed wider (out to cx+18) so it fully
    # COVERS the bird's native blue/teal wing feather that used to punch through
    # the coat opening; the centre notch is kept narrow so only emerald shows in
    # the gap, never bare wing. A dark outline traces the coat edge so the pale
    # dove-lavender never dissolves into a bright day sky.
    cx = 32
    coat = [(cx - 13, HY + 6), (cx - 17, HY + 31), (cx - 6, HY + 35),
            (cx, HY + 24),                                   # narrow centre notch
            (cx + 6, HY + 35), (cx + 21, HY + 33), (cx + 16, HY + 3)]
    _poly(surf, _DN_OUTLINE, [(x, y + 2) for (x, y) in coat])  # 2px sky-facing edge
    _poly(surf, _DN_LAV, coat)
    # Right shoulder cap — buries the native blue/orange wing crest that peeks
    # above the coat collar on the far side, so no stray feather survives at 40px.
    _poly(surf, _DN_LAV_D, [(cx + 3, HY), (cx + 17, HY - 1),
                            (cx + 19, HY + 13), (cx + 5, HY + 13)])
    # Shoulder/fold shading on each panel + ONE highlight ridge down the near side.
    _poly(surf, _DN_LAV_D, [(cx - 17, HY + 31), (cx - 13, HY + 14),
                            (cx - 9, HY + 16), (cx - 7, HY + 33), (cx - 6, HY + 35)])
    _poly(surf, _DN_LAV_D, [(cx + 21, HY + 33), (cx + 13, HY + 14),
                            (cx + 9, HY + 16), (cx + 7, HY + 33), (cx + 6, HY + 35)])
    pygame.draw.line(surf, _DN_LAV_H, (cx - 9, HY + 9), (cx - 12, HY + 28), 1)
    # Peaked lapels framing the open front — a darker lavender so the V reads.
    _poly(surf, _DN_LAV_D, [(cx - 12, HY + 7), (cx - 3, HY + 9),
                            (cx - 5, HY + 22), (cx - 10, HY + 16)])
    _poly(surf, _DN_LAV_D, [(cx + 14, HY + 7), (cx + 3, HY + 9),
                            (cx + 5, HY + 22), (cx + 11, HY + 16)])

    # ── 3 · EMERALD WAISTCOAT WEDGE — the saturated HERO, now ~40% wider and
    # RAISED so its mass sits centred directly under the ascot: emerald is the
    # second thing the eye catches after the hat. A broad bright V of emerald
    # fills the open coat front, outlined dark, with a lighter ridge. Pushed up
    # to HY+7 so the wide top edge anchors the chest under the throat.
    wedge = [(cx - 9, HY + 7), (cx + 9, HY + 7), (cx + 6, HY + 27),
             (cx, HY + 31), (cx - 6, HY + 27)]
    _poly(surf, _DN_OUTLINE, [(x, y + 1) for (x, y) in wedge])
    _poly(surf, _DN_EMER, wedge)
    _poly(surf, _DN_EMER_D, [(cx + 3, HY + 9), (cx + 9, HY + 7),
                             (cx + 6, HY + 27), (cx + 2, HY + 25)])
    pygame.draw.line(surf, _DN_EMER_H, (cx - 5, HY + 9), (cx - 2, HY + 25), 2)

    # ONE gold accent on the chest: two LARGER waistcoat buttons (the gold tell),
    # plus a single 1px chain hint so the gold doesn't smear into a smudge.
    for by in (HY + 13, HY + 21):
        pygame.draw.circle(surf, _DN_GOLD_D, (cx, by), 2)
        pygame.draw.circle(surf, _DN_GOLD,   (cx, by), 2, 1)
        pygame.draw.circle(surf, _DN_GOLD_H, (cx - 1, by - 1), 1)
    pygame.draw.line(surf, _DN_GOLD, (cx, HY + 13), (cx + 5, HY + 18), 1)  # chain hint

    # ── 4 · ASCOT / CRAVAT — bright emerald-and-gold puff at the throat, sitting
    # just under the head where the wedge meets the collar. A small saturated
    # blob carries the colour up to the face so the wedge isn't an island.
    ax, ay = cx, HY + 5
    _poly(surf, _DN_OUTLINE, [(ax - 6, ay - 2), (ax + 6, ay - 2),
                              (ax + 4, ay + 5), (ax - 4, ay + 5)])
    _poly(surf, _DN_EMER, [(ax - 5, ay - 2), (ax + 5, ay - 2),
                           (ax + 3, ay + 4), (ax - 3, ay + 4)])
    pygame.draw.line(surf, _DN_EMER_H, (ax - 3, ay - 1), (ax - 2, ay + 3), 1)
    # No gold pin at the knot — gold is reserved for the single cane/button tell.

    # ── 5 · ROSE BOUTONNIÈRE — bumped to a solid 3px scarlet dot high on the near
    # lapel (a nod to Pip's native red) so the bloom survives a touch at 40px.
    rx, ry = cx - 9, HY + 10
    pygame.draw.circle(surf, _DN_OUTLINE, (rx, ry), 4)
    pygame.draw.circle(surf, _DN_ROSE,   (rx, ry), 3)
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
    # (two small rings) instead of a monocle, for the jazz-age look. The frames
    # are TORTOISESHELL brown, NOT gold — keeping gold to the single cane/button
    # tell so the chest read stays clean (the specs are hero-only charm anyway).
    _TORT   = (96, 62, 38)
    _TORT_H = (150, 108, 70)
    lx, rx2 = HX + 2, HX + 9
    sy2 = HY
    pygame.draw.circle(surf, _TORT,   (lx, sy2), 3, 1)
    pygame.draw.circle(surf, _TORT,   (rx2, sy2), 3, 1)
    pygame.draw.circle(surf, _TORT_H, (lx, sy2), 2, 1)
    pygame.draw.circle(surf, _TORT_H, (rx2, sy2), 2, 1)
    pygame.draw.line(surf, _TORT, (lx + 2, sy2 - 1), (rx2 - 2, sy2 - 1), 1)     # bridge
    pygame.draw.circle(surf, (255, 255, 255), (lx - 1, sy2 - 1), 1)            # glint
    # Pencil-thin curled moustache under the beak — two strands flicking up.
    mx, my = HX + 7, HY + 7
    pygame.draw.lines(surf, _DN_OUTLINE, False,
                      [(mx - 5, my), (mx - 1, my + 1), (mx - 3, my - 2)], 1)
    pygame.draw.lines(surf, _DN_OUTLINE, False,
                      [(mx + 5, my), (mx + 1, my + 1), (mx + 3, my - 2)], 1)


build = store_skins._make_skin(_paint)
