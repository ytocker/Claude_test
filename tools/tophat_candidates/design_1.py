"""THE TYCOON — gilded-age magnate (Monopoly-man) top-hat candidate (DESIGN 1 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_tophat`` is untouched.

Concept: keep the TOP HAT as the identity anchor and build a full gentleman
costume under it — a tall glossy black silk topper, a fat white walrus
moustache, a gold-rimmed monocle, a tight white wing-collar + bow tie, a black
morning-coat painted OVER the scarlet body (red survives only as a thin lapel
edge) open to a buff waistcoat with a draped gold pocket-watch chain, a black
"$"-capped cane slung in the wing, and white spats over the feet.

At 40px the read, in order of value: (1) a tall black block (the hat) over a
crisp WHITE wedge (collar + moustache) — the hero contrast that survives both
skies; (2) the gold "$" cane disc glinting low-front; (3) the buff waistcoat
with its gold chain swag across the belly. The white chest + black hat is the
hero value pair, so every other mark is kept subordinate to protect it.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Near-black silk so the hat/coat read as one block, but with a light rim/stripe
# value so the black survives the night sky (same trick the production _paint_tophat
# uses) and a soft satin band for the hat.
_TYC_BLACK   = (17, 17, 20)        # #111114 hat / morning-coat body
_TYC_BLACK_D = (8, 8, 11)          # coat/hat shadow underlay
_TYC_BLACK_H = (78, 80, 92)        # crisp silk highlight rim so black ≠ sky
_TYC_BAND    = (40, 40, 50)        # satin hat band, one value up from the felt
_TYC_BAND_H  = (110, 112, 128)

# The WHITE chest is the hero — collar, moustache and spats all share it so the
# bright wedge reads as one shape under the black hat.
_TYC_WHITE   = (244, 239, 226)     # #F4EFE2 collar / shirt / spats / moustache
_TYC_WHITE_D = (196, 190, 174)     # white shadow so the wedge has form
_TYC_WHITE_H = (255, 255, 252)     # brightest glint

# Gold is the wealth flourish — chain swag + the "$" cane disc; needs a glow
# halo + a bright core so the tiny disc still glints at 40px.
_TYC_GOLD    = (232, 194, 74)      # #E8C24A chain / $ disc
_TYC_GOLD_D  = (158, 126, 40)
_TYC_GOLD_H  = (255, 236, 158)
# Dim bronze for the monocle rim + watch-chain so only the belly "$" disc keeps a
# bright gold value — two competing golds was the smear the cane got lost in.
_TYC_BRONZE  = (104, 84, 38)

_TYC_BUFF    = (217, 201, 160)     # #D9C9A0 waistcoat
_TYC_BUFF_D  = (172, 156, 118)
_TYC_BUFF_H  = (240, 228, 196)

_TYC_SCARLET = (124, 14, 18)       # #7C0E12 lapel-edge accent (the surviving red)


def _paint(surf, _a):
    # ── BLACK "$"-CANE dropped to the LOW-FRONT-CENTRE BELLY, painted FIRST so the
    #    coat block buries the upper shaft and only the lower stick + the gold "$"
    #    grip overshoot the belly silhouette into clear sky. Pulled OFF the face
    #    (where it smeared into the monocle/moustache gold + wing rainbow) so the
    #    gold coin now sits ALONE against the black coat with clear air around it —
    #    the one surviving gold focal point. The ferrule drops below the body line
    #    to break the lower outline the way the pirate's peg leg does.
    grip = (HX - 10, HY + 34)           # $-disc grip, low-front-centre belly
    foot = (HX - 14, HY + 50)           # ferrule tip, below the body line
    pygame.draw.line(surf, _TYC_BLACK_D, (grip[0] + 1, grip[1] + 1),
                     (foot[0] + 1, foot[1] + 1), 4)        # shadow underlay
    pygame.draw.line(surf, _TYC_BLACK, grip, foot, 3)      # ebony shaft
    pygame.draw.line(surf, _TYC_BLACK_H, grip,
                     ((grip[0] + foot[0]) // 2, (grip[1] + foot[1]) // 2), 1)  # glint
    pygame.draw.circle(surf, _TYC_BLACK, foot, 2)          # rubber ferrule tip

    # Glowing gold "$" disc at the grip — the legendary flourish, now the SOLE gold
    # focal point. Bumped to r6 with a FULL bright rim RING (not a 1px arc) so the
    # coin still reads as money at 40px against the surrounding black coat.
    gx, gy = grip
    pygame.draw.circle(surf, _TYC_GOLD_D, (gx, gy), 7)     # soft halo / shadow ring
    pygame.draw.circle(surf, _TYC_GOLD, (gx, gy), 6)       # gold disc body
    pygame.draw.circle(surf, _TYC_GOLD_H, (gx, gy), 6, 2)  # full bright rim ring
    # The "$" glyph — a short vertical bar with a tiny serif kick so it reads as
    # currency, not a blank coin.
    pygame.draw.line(surf, _TYC_BLACK_D, (gx, gy - 4), (gx, gy + 4), 1)
    pygame.draw.line(surf, _TYC_BLACK_D, (gx - 3, gy - 2), (gx + 3, gy - 3), 1)
    pygame.draw.line(surf, _TYC_BLACK_D, (gx - 3, gy + 3), (gx + 3, gy + 2), 1)
    pygame.draw.circle(surf, _TYC_GOLD_H, (gx - 2, gy - 2), 1)  # top-left glint

    # ── BLACK MORNING-COAT painted OVER the scarlet body. Body centre ~(32, 52).
    #    A near-black coat block covers the torso; a thin SCARLET lapel edge is left
    #    along the open V so the macaw's red survives as an accent, and a buff
    #    waistcoat wedge shows through the open front.
    # Coat body — one broad rounded block that reaches UP-and-BACK over the wing so
    # the macaw's loud rainbow feathers are buried under near-black; the open
    # feathers were the chaos that read as noise at 40px, so the coat must cover
    # them for the black-vs-white value pair to hold. Raised the top + widened the
    # back so the near-black mass swallows the upper-right green/blue/magenta
    # feather cluster that was poking out as confetti; chest now reads pure
    # black-coat → white-wedge → red-edge and nothing else.
    pygame.draw.ellipse(surf, _TYC_BLACK_D, (HX - 39, HY - 7, 46, 44))
    pygame.draw.ellipse(surf, _TYC_BLACK, (HX - 38, HY - 7, 44, 42))
    # A small near-black collar cap tucked under the hat-brim's back-left edge to
    # bury the last green/blue/magenta head-feather pixels that peeked between the
    # brim and the coat top and read as confetti at 40px. The narrow patch at the
    # band/brim seam (HX-8..HX-6, just below CROWN_Y) seals the exact 2px window the
    # macaw's blue head-feathers poked through.
    pygame.draw.ellipse(surf, _TYC_BLACK_D, (HX - 20, CROWN_Y - 1, 22, 14))
    pygame.draw.ellipse(surf, _TYC_BLACK, (HX - 19, CROWN_Y - 1, 20, 12))
    pygame.draw.rect(surf, _TYC_BLACK, (HX - 10, CROWN_Y - 4, 8, 6))
    # Coat tail sweeping down-back so the formalwear reads below the body line.
    _poly(surf, _TYC_BLACK_D, [(HX - 32, HY + 28), (HX - 20, HY + 24),
                               (HX - 22, HY + 44), (HX - 34, HY + 40)])
    _poly(surf, _TYC_BLACK, [(HX - 31, HY + 28), (HX - 21, HY + 25),
                             (HX - 23, HY + 42), (HX - 33, HY + 39)])

    # Buff WAISTCOAT wedge showing through the open coat front (centre belly).
    waist = [(HX - 6, HY + 8), (HX - 16, HY + 12), (HX - 14, HY + 30),
             (HX - 4, HY + 30), (HX - 2, HY + 12)]
    _poly(surf, _TYC_BUFF_D, [(p[0] - 1, p[1] + 1) for p in waist])
    _poly(surf, _TYC_BUFF, waist)
    pygame.draw.line(surf, _TYC_BUFF_H, (HX - 5, HY + 10), (HX - 13, HY + 13), 1)

    # Three dot buttons down the waistcoat.
    for i, by in enumerate((HY + 15, HY + 21, HY + 27)):
        pygame.draw.circle(surf, _TYC_BLACK_D, (HX - 8, by), 2)
        pygame.draw.circle(surf, _TYC_BUFF_H, (HX - 9, by - 1), 1)

    # Draped pocket-watch chain swag across the belly — kept to the DIM gold-shadow
    # value (no bright core, no glint) so it stays quiet and subordinate and the
    # belly "$" coin is the only bright gold focal point at 40px.
    chain = [(HX - 4, HY + 18), (HX - 9, HY + 24), (HX - 15, HY + 21)]
    pygame.draw.lines(surf, _TYC_BRONZE, False, chain, 1)
    pygame.draw.circle(surf, _TYC_BRONZE, (HX - 16, HY + 21), 1)  # watch fob

    # Thin SCARLET lapel edge framing the open coat V — the surviving macaw red,
    # the one warm accent that keeps Pip's identity under all the black-and-white.
    lapel_l = [(HX - 4, HY + 6), (HX - 15, HY + 11), (HX - 14, HY + 26)]
    lapel_r = [(HX, HY + 6), (HX + 1, HY + 12), (HX - 2, HY + 24)]
    pygame.draw.lines(surf, _TYC_SCARLET, False, lapel_l, 2)
    pygame.draw.lines(surf, _TYC_SCARLET, False, lapel_r, 2)
    # Black lapel facing just inside the scarlet edge so the V reads sharply.
    pygame.draw.lines(surf, _TYC_BLACK_H, False,
                      [(HX - 5, HY + 8), (HX - 13, HY + 12)], 1)

    # ── WHITE SPATS over both feet (~(28,65)/(34,65)) with two side buttons each.
    for fx in (28, 34):
        pygame.draw.rect(surf, _TYC_WHITE_D, (fx - 4, 60, 8, 9), border_radius=2)
        pygame.draw.rect(surf, _TYC_WHITE, (fx - 4, 59, 8, 8), border_radius=2)
        pygame.draw.line(surf, _TYC_WHITE_H, (fx - 3, 60), (fx + 2, 60), 1)
        pygame.draw.circle(surf, _TYC_BLACK_D, (fx + 3, 62), 1)   # side buttons
        pygame.draw.circle(surf, _TYC_BLACK_D, (fx + 3, 65), 1)

    # ── WING-COLLAR + BOW TIE — a tall bright WHITE triangle pinned high at the
    #    throat (just under the beak) so it joins the moustache into one crisp
    #    white wedge — the hero value shape that has to survive 40px on both skies.
    collar = [(HX + 4, HY + 2), (HX - 9, HY + 4), (HX - 2, HY + 16)]
    _poly(surf, _TYC_WHITE_D, [(p[0], p[1] + 1) for p in collar])
    _poly(surf, _TYC_WHITE, collar)
    pygame.draw.line(surf, _TYC_WHITE_H, (HX + 3, HY + 3), (HX - 7, HY + 5), 1)
    # Black BOW TIE sitting at the collar point — pushed to pure shadow-black and
    # 1px wider so it cuts a clean dark NOTCH across the white wedge, splitting it
    # into collar-above / shirt-below instead of one undifferentiated blob.
    bx, by = HX - 3, HY + 8
    _poly(surf, _TYC_BLACK_D, [(bx - 5, by - 3), (bx - 1, by), (bx - 5, by + 3)])
    _poly(surf, _TYC_BLACK_D, [(bx + 4, by - 3), (bx, by), (bx + 4, by + 3)])
    pygame.draw.circle(surf, _TYC_BLACK_D, (bx, by), 2)           # centre knot

    # ── TALL BLACK SILK TOP HAT rising well above CROWN_Y — the identity anchor.
    cy = CROWN_Y
    # Curled brim — wide ellipse with a bright top edge so the silhouette reads.
    pygame.draw.ellipse(surf, _TYC_BLACK_D, (HX - 18, cy + 1, 36, 9))
    pygame.draw.ellipse(surf, _TYC_BLACK, (HX - 17, cy, 34, 6))
    pygame.draw.line(surf, _TYC_BLACK_H, (HX - 14, cy + 1), (HX + 14, cy + 1), 1)

    # Tall cylindrical crown — taller than the production redraw so the topper
    # reads as a magnate's silk hat, not a bowler.
    top_y = cy - 22
    pygame.draw.rect(surf, _TYC_BLACK_D, (HX - 9, top_y, 19, 24))
    pygame.draw.rect(surf, _TYC_BLACK, (HX - 8, top_y, 16, 23))
    # Soft top highlight STRIPE down the silk so the black survives the night sky.
    pygame.draw.line(surf, _TYC_BLACK_H, (HX - 6, top_y + 2), (HX - 6, cy - 4), 2)
    # Crisp light top rim (the hat's flat silk top catching light).
    pygame.draw.ellipse(surf, _TYC_BLACK_H, (HX - 9, top_y - 2, 19, 6))
    pygame.draw.ellipse(surf, _TYC_BLACK, (HX - 8, top_y - 1, 17, 4))

    # Narrow satin BAND wrapping the base of the crown.
    pygame.draw.rect(surf, _TYC_BAND, (HX - 9, cy - 4, 19, 4))
    pygame.draw.line(surf, _TYC_BAND_H, (HX - 8, cy - 4), (HX + 8, cy - 4), 1)

    # ── FACE — the comedy tell. Big bushy WHITE walrus moustache splayed under the
    #    beak + a round gold-rimmed monocle on the near eye.
    # Walrus moustache — a fat WHITE bar splayed under the beak with two drooping
    # curl tips. Sits forward toward the beak (beak tip ~61) and is drawn big +
    # bright because it is THE comedy tell that survives the 40px downscale; a
    # shadow underlay first gives the white fur form against the scarlet face.
    mx, my = HX + 4, HY + 6
    # Raised + extended the RIGHT wing up over the upper lip so the white fur buries
    # the macaw's bright yellow BEAK base — that beak gold was the second bright
    # gold competing with the belly "$" coin; with it covered the "$" is the lone
    # gold focal point.
    _poly(surf, _TYC_WHITE_D, [(mx + 14, my - 4), (mx - 10, my + 1),
                              (mx - 8, my + 8), (mx + 2, my + 6)])
    _poly(surf, _TYC_WHITE, [(mx + 14, my - 5), (mx - 10, my),
                            (mx - 7, my + 7), (mx + 2, my + 5)])
    # Two drooping curl tips so it reads as a walrus, not a smear.
    _poly(surf, _TYC_WHITE, [(mx - 10, my), (mx - 8, my + 7), (mx - 12, my + 5)])
    # Right shoulder raised square over the beak so the bright macaw beak no longer
    # peeks above the fur and steals gold from the belly "$".
    _poly(surf, _TYC_WHITE, [(mx + 5, my - 5), (mx + 18, my - 5),
                            (mx + 16, my + 2), (mx + 5, my + 1)])
    _poly(surf, _TYC_WHITE_D, [(mx + 16, my - 4), (mx + 18, my + 1), (mx + 12, my + 2)])
    pygame.draw.line(surf, _TYC_WHITE_H, (mx + 12, my - 3), (mx - 8, my + 1), 1)
    # One row of white-SHADOW under the lower droop edge so the moustache catches a
    # hard bottom contour — the curl-tips read as a walrus droop, not a paint spill.
    pygame.draw.line(surf, _TYC_WHITE_D, (mx - 11, my + 6), (mx - 8, my + 8), 1)
    pygame.draw.line(surf, _TYC_WHITE_D, (mx - 8, my + 8), (mx + 2, my + 7), 1)
    pygame.draw.line(surf, _TYC_WHITE_D, (mx + 2, my + 7), (mx + 8, my + 5), 1)

    # Round MONOCLE on the near eye + a 1px white glint + a thin cord down to the
    # waistcoat. Its rim is DIMMED to the low gold-shadow value (no bright core) so
    # only the belly "$" coin survives as the single gold focal point at 40px — two
    # competing golds was the smear the cane got lost in.
    ex, ey = HX + 6, HY - 2
    pygame.draw.circle(surf, _TYC_BRONZE, (ex, ey), 5, 1)
    pygame.draw.circle(surf, _TYC_BRONZE, (ex, ey), 4, 1)
    pygame.draw.circle(surf, _TYC_WHITE_H, (ex - 2, ey - 2), 1)   # glint
    pygame.draw.line(surf, _TYC_BRONZE, (ex + 1, ey + 4), (ex + 1, HY + 6), 1)


build = store_skins._make_skin(_paint)
