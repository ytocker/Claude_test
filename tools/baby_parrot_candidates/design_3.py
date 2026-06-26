"""design_3 · BIG-EYES baby macaw — EPIC baby-parrot exploration (scratch only).

"Neoteny dialed to 11." Pip's signature aviators become enormous baby eyes:
each lens body lifts to a glassy baby-blue and is filled with one huge glossy
cartoon eye — a fat white catch-light dome, a tiny low pupil, a starry glint —
so the whole face reads as two gigantic shiny eyes behind the shades. The face,
not the fluff, is the tell. A single soft cowlick and a few sparse chest wisps
keep it baby without stealing the read; a 2px open-beak "peep" makes it chirp.

North star is "lives or dies at 40px on BOTH skies". The whole read sits in the
lens interior, so contrast is engineered hard: the lens body is darkened to a
deep glassy teal-blue (a clear value floor), the catch-light dome is pure near-
white at ≥3px (the one spec that survives downscale and refuses to wash out on a
bright DAY sky), the pupil is near-black ink, and the aviator frame is kept as a
hard rim ringing each eye. Mint-cream re-plumage stays clear of every adult and
rarity skin. PRISM model — eyes/cowlick/wisps are circles + polygons over a mint
recolour; no back layer. Exploration only — NEVER registered in store_skins.BUILDERS.
"""
import math

import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# BIG-EYES palette — fresh mint-cream body (a hue no adult/rarity owns: amazon
# green is far darker/saturated, nowhere near moonbloom lilac or hyacinth cobalt)
# with a sage shadow that carries the line work so the body still ramps dark→
# light. The aviators retint glassy-aqua so the lens reads as GLASS, not a black
# disc — the giant eyes are then painted ON TOP in the overlay.
_BE_MINT    = (207, 230, 198)      # #CFE6C6 mint-cream body — one value step down
                                   # from #DDEFD6 so it still seats as a baby
                                   # pastel but throws a cleaner silhouette
                                   # against a bright day sky.
_BE_SAGE    = (159, 199, 154)      # #9FC79A sage shadow / keyline (cowlick+wisps)
_BE_EDGE    = (127, 168, 120)      # #7FA878 deeper sage — the hard silhouette
                                   # keyline (body_shadow crescent) so the day
                                   # edge stops reading mushy.
_BE_BELLY   = (239, 248, 234)      # #EFF8EA pale belly bright — kept bright so
                                   # face+belly stay the focal bright zone.
_BE_LENS_SKY = (191, 227, 242)     # #BFE3F2 glassy baby-blue lens fill
_BE_PUPIL   = (42, 53, 64)         # #2A3540 pupil ink
_BE_BLUSH   = (240, 168, 160)      # #F0A8A0 cheek blush
_BE_AVIAQUA = (159, 212, 232)      # #9FD4E8 glassy-aqua aviator tint

# Eye-interior working tones. The lens body is darkened well BELOW the glassy
# sky fill so the white catch-light dome has a hard value floor to pop against on
# a bright day sky (the make-or-break for this skin); the upper lens stays a
# lighter glass so the eye reads round and wet, not flat.
_BE_LENS_DEEP = (60, 108, 138)     # deep glassy teal — the dark floor of the eye,
                                   # dropped ~25% darker so the white dome has a
                                   # real value drop to pop against on day.
_BE_LENS_GLASS = (208, 236, 248)   # lit upper-glass — kept bright so the top arc
                                   # still reads wet: a STEEP floor→dome ramp, not
                                   # a flat dark disc.
_BE_WHITE   = (250, 253, 255)      # catch-light dome — the surviving spec
_BE_FRAME   = (118, 168, 190)      # aqua aviator rim, a touch deeper than tint
_BE_FRAME_D = (74, 118, 140)       # rim shadow so the frame stays a hard ring


# Full mint-cream re-plumage. Shadow slots run sage so the head/body still carry
# a dark→light range under the eyes; chest+belly stay pale mint so the face
# reads as the bright focal zone. Lenses are tinted glassy-aqua here, but the
# overlay overpaints the lens INTERIOR entirely, so these lens_* slots only seat
# the frame colour — the eye is drawn from scratch on top.
P_BIGEYES = _pal(
    tail=[(150, 188, 146), (172, 208, 166), (196, 226, 190), (220, 240, 214)],
    tail_line=_BE_SAGE,
    # body_shadow seats the outer crescent under body_main — run it the deeper
    # sage edge tone so the lower-right silhouette reads as a HARD keyline on day
    # without darkening the lit fill.
    body_shadow=_BE_EDGE,
    body_main=_BE_MINT,
    body_chest=(226, 242, 218),
    body_belly=_BE_BELLY,
    sheen=(255, 255, 255, 120),
    wing_main=(186, 220, 180),
    wing_dark=(146, 188, 142),
    wing_tip=(226, 242, 220),
    wing_secondary=None,               # single-hue mint — keep the wing quiet
    wing_highlight=(240, 250, 236),
    head_shadow=_BE_EDGE,
    head_main=_BE_MINT,
    head_cheek=(198, 224, 190),
    head_crown=(195, 222, 188),
    lens_frame=_BE_FRAME,
    lens_body=_BE_LENS_SKY,            # glassy base; overpainted by the overlay
    lens_tint=(159, 212, 232, 120),    # glassy-aqua wash
    lens_glint=None,                   # the giant-eye glint is drawn in overlay
    beak_main=(214, 226, 206),
    beak_dark=(150, 180, 146),
    beak_gloss=(248, 252, 244),
    foot=(170, 156, 120),
)


# Aviator lens centres in COMPOSITE space. The base is blitted at y=PARROT_DY, so
# _draw_lenses' base centre (50,20) lands at (50,40); the near (R) lens is the
# hero, the far (L) lens reads slightly smaller/back. Radius 6 matches the base.
_L = (HX - 1, HY)                      # far lens  → (46, 41)
_R = (HX + 9, HY - 1)                  # near lens → (56, 40)
_LR = 6


def _big_eye(surf, cx, cy, *, near):
    """Paint one giant glossy baby eye filling an aviator lens at (cx,cy).

    The read is engineered for 40px on a bright DAY sky: a dark glassy floor →
    a fat near-white catch-light dome (≥3px) → a tiny low pupil → a 1px starry
    glint. The near eye runs a hair larger so the face has a clear front/back.
    Clipping to the lens circle keeps the eye INSIDE the frame so the rim still
    reads as a hard ring around it."""
    r = _LR
    # Clip everything to the lens disc so the eye never spills past the frame.
    prev = surf.get_clip()
    clip = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)

    # 1 · Dark glassy floor — the value floor the white dome pops against. A
    #     lighter lit-glass arc across the TOP makes the eye read round + wet.
    pygame.draw.circle(surf, _BE_LENS_DEEP, (cx, cy), r)
    top = pygame.Surface((r * 2, r), pygame.SRCALPHA)
    pygame.draw.ellipse(top, _BE_LENS_GLASS, top.get_rect())
    surf.blit(top, (cx - r, cy - r + 1))

    # 2 · The hero catch-light dome — a fat near-white blob high-and-near in the
    #     lens. This is the one spec sized to survive downscale; on a washed-out
    #     day sky it stays the brightest thing in the silhouette. Offset toward
    #     the centre of the face so both domes face inward (a cute cross-eyed
    #     baby read) and never touch the rim.
    dome_r = 4 if near else 3
    dx = -1 if near else 1                 # near dome shifts in toward the bridge
    # A 1px dark keyline ring under the dome — without it the near-white dome
    # blurs straight into the lit upper-glass on a day sky and the dome edge goes
    # soft. Drawing the deep tone one px larger gives the dome a crisp boundary
    # that survives the 40px downscale.
    pygame.draw.circle(surf, _BE_LENS_DEEP, (cx + dx, cy - 2), dome_r + 1)
    pygame.draw.circle(surf, _BE_WHITE, (cx + dx, cy - 2), dome_r)

    # 3 · The pupil — a tiny dark ink dot sitting LOW in the lens (baby eyes look
    #     down), tucked just under the dome so it reads as the eye's centre, not
    #     a smudge. Kept small so the eye stays mostly bright + glossy.
    pygame.draw.circle(surf, _BE_PUPIL, (cx + dx, cy + 2), 2)
    # A 1px starry glint on the pupil edge — the wet-eye sparkle.
    pygame.draw.circle(surf, _BE_WHITE, (cx + dx + 1, cy + 1), 1)

    surf.set_clip(prev)
    del clip


def _frame_ring(surf, cx, cy):
    """Re-draw the aviator rim as a HARD ring over the eye so the frame stays a
    crisp boundary at 40px (a dark inner keyline + the aqua rim). Without this
    the painted eye would bleed to the lens edge and lose the 'behind shades'
    read."""
    r = _LR
    pygame.draw.circle(surf, _BE_FRAME_D, (cx, cy), r + 1, 1)
    pygame.draw.circle(surf, _BE_FRAME, (cx, cy), r, 1)


def _cowlick(surf):
    """A single soft down-curl off the crown — understated, so the crown still
    breaks but the eyes own the read. Drawn as a tapered curl (dark sage spine +
    a lit mint over-stroke) so it reads as SOFT down, not a stiff feather."""
    curl = [
        (HX - 2, CROWN_Y + 1),
        (HX - 3, CROWN_Y - 3),
        (HX - 6, CROWN_Y - 5),
        (HX - 5, CROWN_Y - 8),     # the little hook of the curl
    ]
    pygame.draw.lines(surf, _BE_SAGE, False, curl, 3)
    pygame.draw.lines(surf, _BE_MINT, False, curl, 1)
    pygame.draw.circle(surf, _BE_MINT, (HX - 5, CROWN_Y - 8), 1)


def _wisp(surf, x, y, dx, dy):
    """One short down wisp poking just past the chest silhouette — a 2–3px
    tapered line so the costume still feels baby-fuzzy without competing with the
    face. Sage spine + mint tip = a value break that survives downscale."""
    pygame.draw.line(surf, _BE_SAGE, (x, y), (x + dx, y + dy), 2)
    pygame.draw.line(surf, _BE_MINT, (x, y), (x + dx // 2, y + dy // 2), 1)


def _paint_bigeyes(surf, _a):
    # 1 · CROWN — one soft cowlick, the secondary tell (kept understated).
    _cowlick(surf)

    # 2 · CHEST — a few sparse down wisps poking past the lower-near silhouette,
    #     enough to read baby-fuzzy without pulling the eye off the face.
    _wisp(surf, 30, HY + 16, -3, 2)
    _wisp(surf, 36, HY + 19, -2, 3)
    _wisp(surf, 42, HY + 18, 2, 3)

    # 3 · CHEEK-BLUSH — a soft rosy dab under the near lens. Drawn semi-trans so
    #     it reads as a blush on the mint cheek, not a sticker.
    blush = pygame.Surface((7, 5), pygame.SRCALPHA)
    pygame.draw.ellipse(blush, (*_BE_BLUSH, 170), blush.get_rect())
    surf.blit(blush, (_R[0] - 2, _R[1] + 5))

    # 4 · FACE (HERO) — the giant baby eyes painted INSIDE each aviator lens, far
    #     lens first so the near eye overlaps it. The frame ring is re-stamped
    #     over each so the aviators stay a hard rim around the eyes.
    _big_eye(surf, *_L, near=False)
    _frame_ring(surf, *_L)
    _big_eye(surf, *_R, near=True)
    _frame_ring(surf, *_R)

    # 5 · MOUTH — a tiny 2px open-beak "peep" highlight so it reads as a chirping
    #     baby, not a stern adult beak. A bright inner-mouth wedge at the beak
    #     base, just below the near eye.
    pygame.draw.polygon(surf, (255, 248, 240),
                        [(HX + 14, HY + 2), (HX + 18, HY + 3), (HX + 15, HY + 5)])
    pygame.draw.line(surf, _BE_SAGE, (HX + 14, HY + 2), (HX + 18, HY + 3), 1)


# Body recolour through the palette system + the big-eyes overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_bigeyes,
    base_fn=lambda a: _build_parrot_with_palette(a, P_BIGEYES),
)
