"""HORUS — the Falcon-God King  (pharaoh v2, RE-ROLL candidate 1).

Scratch exploration only — NOT registered in store_skins.BUILDERS.

The bolder pharaoh re-roll: instead of stacking a hat on Pip, HORUS reshapes
the HEAD ITSELF into a falcon — a long near-black HOOKED beak that breaks the
head's right edge and hooks DOWN below the chin line, so a notch reads against
the sky at 40px. The head sits at mid-slate so the black beak separates from it
as its own value instead of fusing into one dark blob; that hook is the brand.

The whole bird is re-plumaged deep slate-grey falcon (palette recolor, like the
ninja/astronaut skins) with thin gold feather-edge accents — the scarlet/orange
macaw is gone so the GOD wins the focal hierarchy. The only loud notes are the
GOLD regalia, the WHITE Hedjet, and the single RED Deshret accent; everything
else is calm dark plumage. Footprint law: body regalia stays inside the base
bird footprint; only the tall asymmetric Pschent rises above CROWN_Y.

Palette discipline — 3 hero notes (slate / white / gold) + ONE red accent +
neutrals. Turquoise is dropped to a single tiny eye dot.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── Hero palette — slate body+head, white Hedjet, gold regalia, red accent.
# The head is lifted to MID-slate so the near-black beak reads as its own value
# wedge against it; the body is DEEPER slate so the lit head pops as the focal.
_HR_HEAD     = (82, 103, 126)      # #52677E mid-slate falcon head (beak lifts off)
_HR_HEAD_D   = (54, 70, 90)        # head shadow / underside
_HR_HEAD_H   = (132, 152, 174)     # head crown sheen
_HR_WHITE    = (242, 239, 230)     # #F2EFE6 Hedjet white
_HR_WHITE_D  = (198, 196, 184)     # Hedjet shadow side
_HR_WHITE_H  = (255, 254, 248)     # Hedjet specular
_HR_RED      = (188, 52, 40)       # #C0392B Deshret red (the SINGLE accent)
_HR_RED_D    = (138, 36, 28)
_HR_RED_H    = (220, 92, 74)
_HR_GOLD     = (232, 178, 58)      # #E8B23A gold regalia
_HR_GOLD_D   = (168, 122, 34)
_HR_GOLD_H   = (255, 226, 142)
_HR_COLLAR_D = (28, 37, 48)        # collar/upper-body knocked one step darker so
                                   # the lit slate head separates as its own shape
_HR_BEAK     = (22, 24, 28)        # near-black hooked beak (the silhouette)
_HR_BEAK_H   = (96, 106, 120)      # beak ridge glint so the wedge keeps a top edge
_HR_CERE     = (228, 182, 64)      # gold cere band at the beak base
_HR_EYE_DOT  = (34, 150, 144)      # the ONE tiny turquoise survivor (eye dot)

# Deep-slate falcon re-plumage of the whole macaw. Every slot is a slate value,
# the deepest tone does the line work, the beak is blacked (the head-paint
# redraws the hero hooked beak on top), and lenses are dropped so the wedjat +
# falcon eye own the face. Quieting the body is the whole point of the re-roll.
_HR_PAL = _pal(
    tail=[(34, 45, 58), (40, 53, 68), (48, 63, 80), (58, 75, 94)],
    tail_line=(22, 30, 40),
    body_shadow=(32, 42, 54),
    body_main=(46, 60, 76),
    body_chest=(60, 78, 96),
    body_belly=(40, 52, 66),
    sheen=(150, 172, 196, 55),
    wing_main=(42, 55, 70),
    wing_dark=(26, 35, 46),
    wing_tip=(64, 82, 100),
    wing_secondary=None,
    wing_highlight=(96, 116, 138),
    head_shadow=_HR_HEAD_D,
    head_main=_HR_HEAD,
    head_cheek=(98, 118, 140),
    head_crown=_HR_HEAD_H,
    lens_frame=(40, 52, 66),
    lens_body=(22, 30, 40),
    lens_tint=None,
    lens_glint=None,
    beak_main=(30, 33, 40),
    beak_dark=(18, 20, 24),
    beak_gloss=(70, 80, 94),
    foot=(30, 33, 40),
)


def _horus_base(angle_deg):
    # Deep-slate falcon-plumage bird, no aviators — the wedjat owns the face.
    return _build_parrot_with_palette(angle_deg, _HR_PAL, draw_lenses=False)


def _paint(surf, _a):
    BCX, BCY = 32, 52              # body centre in composite space

    # ── Was-scepter — ONE clean gold diagonal that breaks the body silhouette as
    # a thin readable line (top-left → mid-right), drawn first so the collar root
    # overlaps it; kept thin + inside the footprint so it never reads as mass.
    s_top = (BCX - 10, BCY - 11)
    s_bot = (BCX + 9, BCY + 11)
    pygame.draw.line(surf, _HR_GOLD_D, (s_top[0] + 1, s_top[1] + 1),
                     (s_bot[0] + 1, s_bot[1] + 1), 3)
    pygame.draw.line(surf, _HR_GOLD, s_top, s_bot, 2)
    pygame.draw.line(surf, _HR_GOLD_H, s_top, (BCX - 1, BCY - 2), 1)
    # Forked was-foot at the staff base — the scepter's twin prong.
    pygame.draw.line(surf, _HR_GOLD_D, s_bot, (s_bot[0] - 2, s_bot[1] + 3), 2)
    pygame.draw.line(surf, _HR_GOLD_D, s_bot, (s_bot[0] + 2, s_bot[1] + 3), 2)
    # Small angular jackal-head crook at the staff head.
    _poly(surf, _HR_GOLD, [(s_top[0] - 2, s_top[1] + 1), (s_top[0] - 4, s_top[1] - 3),
                           (s_top[0], s_top[1] - 3), (s_top[0] + 1, s_top[1])])

    # ── Gold feather-edge accents on the upper chest — TWO thin gold chevrons,
    # kept few + wide so the quiet slate body gets a warm note without going busy
    # (NO orange flame). Set off-centre toward the front.
    for i, cy in enumerate((BCY - 1, BCY + 5)):
        w = 7 - i * 2
        pygame.draw.lines(surf, _HR_GOLD_D, False,
                          [(BCX - w, cy - 2), (BCX + 1, cy + 2), (BCX + w + 2, cy - 2)], 2)
        pygame.draw.lines(surf, _HR_GOLD, False,
                          [(BCX - w, cy - 3), (BCX + 1, cy + 1), (BCX + w + 2, cy - 3)], 1)

    # ── Broad collar (wesekh) — a slim gold-banded arc hugging the neck under the
    # head. A dark slate fill is laid under the arcs FIRST, one value step below
    # the body, so a clear shadow gap opens between the lit falcon head and the
    # collar and the face stops reading as one fused slate blob.
    col = pygame.Rect(BCX - 11, BCY - 17, 28, 18)
    pygame.draw.arc(surf, _HR_COLLAR_D, col.inflate(2, 2), 3.50, 6.05, 4)
    pygame.draw.arc(surf, _HR_GOLD,   col, 3.55, 6.00, 3)
    pygame.draw.arc(surf, _HR_GOLD_H, col.inflate(-5, -5), 3.60, 5.95, 2)
    pygame.draw.arc(surf, _HR_GOLD,   col.inflate(-9, -9), 3.65, 5.90, 2)

    # ── Dark talon recolor on the feet line — small claw clumps ON the line,
    # never below it, so the bird keeps its true size.
    for fx in (28, 35):
        pygame.draw.ellipse(surf, _HR_BEAK, (fx - 3, HY + 22, 7, 5))
        for tx in (fx - 2, fx, fx + 2):
            pygame.draw.line(surf, _HR_BEAK, (tx, HY + 25), (tx, HY + 27), 1)

    # ── FALCON HEAD MASS — repaint Pip's head as a clean mid-slate falcon skull
    # so the near-black beak below reads as a SEPARATE value wedge (no dark blob).
    # The brow is pulled forward over the eye into a heavy hood and the chin is
    # cut UNDER so a clear gap opens for the down-hook — predatory before the beak
    # is even added. The back of the skull stays high+round (the cere/beak owns
    # the front).
    head = [(HX - 13, HY - 3), (HX - 11, HY - 11), (HX - 3, HY - 14),
            (HX + 7, HY - 13), (HX + 13, HY - 8), (HX + 14, HY - 2),
            (HX + 11, HY + 4), (HX + 4, HY + 9), (HX - 5, HY + 11),
            (HX - 12, HY + 5)]
    _poly(surf, _HR_HEAD_D, [(x, y + 1) for x, y in head])
    _poly(surf, _HR_HEAD, head)
    # Crown sheen — a lifted highlight across the top of the slate skull.
    pygame.draw.ellipse(surf, _HR_HEAD_H, (HX - 8, HY - 12, 15, 6))
    # Light cheek patch (cool slate, NOT a white smear) so the eye + beak read as
    # the brightest marks on the face, not a random pale blaze.
    _poly(surf, (118, 138, 160), [(HX + 5, HY + 1), (HX + 11, HY + 2),
                                  (HX + 8, HY + 8), (HX - 1, HY + 9),
                                  (HX - 1, HY + 4)])
    # Thin dark line under the chin/jaw — the value cut that frees the lit head
    # from the collar so they stop fusing into one slate mass at 40px.
    pygame.draw.lines(surf, _HR_HEAD_D, False,
                      [(HX - 11, HY + 6), (HX - 4, HY + 11),
                       (HX + 5, HY + 10), (HX + 10, HY + 5)], 2)

    # ── HOOKED BEAK — THE HERO SILHOUETTE. Raised ~3px and lengthened so the
    # whole wedge rides ABOVE the cheek/collar mass and the down-hook clears the
    # head's right edge into open sky — the notch between tip and chin sits against
    # BACKGROUND, not body, so "falcon" reads at 40px. Near-black against the
    # mid-slate head so the two never fuse. The bird faces right.
    beak = [(HX + 6, HY - 8), (HX + 22, HY - 7), (HX + 31, HY - 3),
            (HX + 34, HY + 1), (HX + 32, HY + 3), (HX + 21, HY + 1),
            (HX + 11, HY), (HX + 8, HY - 3)]
    _poly(surf, _HR_BEAK, beak)
    # The down-curl: the predator hook dropping off the tip into open sky PAST the
    # head's right edge — the deepest, most separated part of the silhouette, with
    # the notch between it and the chin reading against background. Dropped lower +
    # pushed further right so the talon-notch sits firmly on the sky at 40px.
    _poly(surf, _HR_BEAK, [(HX + 31, HY - 2), (HX + 36, HY),
                           (HX + 35, HY + 14), (HX + 30, HY + 13),
                           (HX + 28, HY + 5), (HX + 30, HY + 1)])
    # Ridge glint along the top of the wedge so it keeps a hard upper edge.
    pygame.draw.line(surf, _HR_BEAK_H, (HX + 8, HY - 7), (HX + 30, HY - 3), 1)
    # Gold cere band at the beak base (the falcon's fleshy nostril band).
    _poly(surf, _HR_CERE, [(HX + 5, HY - 8), (HX + 9, HY - 8),
                           (HX + 9, HY - 2), (HX + 5, HY - 2)])
    pygame.draw.circle(surf, (40, 30, 14), (HX + 7, HY - 5), 1)   # nostril dot

    # ── EYE-OF-HORUS (wedjat) — the single bold face mark: a large gold almond
    # with a dark pupil, a straight gold brow bar, and the signature teardrop tail
    # curling down off the front. Gold so it carries on day AND night, seated high
    # on the slate brow. Turquoise survives ONLY as a 1px iris dot.
    ex, ey = HX, HY - 4
    pygame.draw.line(surf, _HR_GOLD_D, (ex - 8, ey - 4), (ex + 5, ey - 3), 3)   # brow
    pygame.draw.line(surf, _HR_GOLD_H, (ex - 8, ey - 5), (ex + 5, ey - 4), 1)
    _poly(surf, _HR_GOLD, [(ex - 8, ey), (ex - 1, ey - 4), (ex + 6, ey),
                           (ex - 1, ey + 4)])                                   # almond
    _poly(surf, _HR_WHITE_H, [(ex - 5, ey), (ex - 1, ey - 2), (ex + 4, ey),
                              (ex - 1, ey + 2)])                               # eye white
    pygame.draw.circle(surf, (16, 18, 22), (ex - 1, ey), 2)                    # pupil
    pygame.draw.circle(surf, _HR_EYE_DOT, (ex - 1, ey), 2, 1)                  # turq iris
    pygame.draw.circle(surf, _HR_WHITE_H, (ex - 2, ey - 1), 1)                 # catchlight
    # The wedjat teardrop tail curling down off the eye front — bold gold.
    pygame.draw.lines(surf, _HR_GOLD, False,
                      [(ex - 6, ey + 3), (ex - 9, ey + 7), (ex - 4, ey + 9)], 2)
    pygame.draw.line(surf, _HR_GOLD_H, (ex - 6, ey + 3), (ex - 8, ey + 6), 1)

    # ── PSCHENT (the double crown) — the ONLY element above CROWN_Y, rebuilt as a
    # TALL VERTICAL STACK so it can NEVER read as a floppy red cap: a NARROW, TALL
    # red Deshret CUP (~18px wide, ~18px tall) with a tall WHITE Hedjet onion
    # rising WELL ABOVE it — "a tall white onion sitting inside a tall red cup."
    # The asymmetry is a slim back-spike SEPARATED from the cup by a sky notch, not
    # a wide brim. The whole thing is taller than it is wide.
    cx = HX + 1
    base_y = CROWN_Y + 2          # crown seats just above the falcon skull

    # The slim REAR back-spike (red) — drawn FIRST and set behind/left of the cup
    # with a clear notch of sky between it and the bowl, so it reads as a separate
    # directional horn rather than melting into a brim. This is the anti-cap tell.
    spike = [(cx - 13, base_y - 2), (cx - 10, base_y - 4),
             (cx - 13, base_y - 17), (cx - 17, base_y - 14),
             (cx - 16, base_y - 4)]
    _poly(surf, _HR_RED_D, [(x + 1, y) for x, y in spike])
    _poly(surf, _HR_RED, spike)
    pygame.draw.circle(surf, _HR_RED,   (cx - 14, base_y - 15), 2)   # flared tip
    pygame.draw.circle(surf, _HR_RED_H, (cx - 15, base_y - 16), 1)   # tip glint

    # Deshret (red) — a NARROW, TALL cup: ~18px wide at the rim, rising ~18px to
    # nearly straight vertical sides that cradle the Hedjet. Tall + slim is the
    # whole point; the cup must read as a deep red vase, not a wide red band.
    desh = [(cx - 7, base_y + 1), (cx + 8, base_y + 1),
            (cx + 9, base_y - 8), (cx + 7, base_y - 16),
            (cx + 2, base_y - 18), (cx - 4, base_y - 16),
            (cx - 6, base_y - 8)]
    _poly(surf, _HR_RED_D, [(x + 1, y) for x, y in desh])
    _poly(surf, _HR_RED, desh)
    pygame.draw.line(surf, _HR_RED_H, (cx + 7, base_y - 2),
                     (cx + 6, base_y - 14), 2)                       # front rim sheen

    # Hedjet (white) — a TALL onion bulb rising well ABOVE the red cup, narrowing
    # to a slim rounded point. Seated INSIDE the cup so the stack reads as one
    # vertical white-in-red column climbing high over the head.
    hed = [(cx - 5, base_y - 11), (cx + 6, base_y - 11),
           (cx + 6, base_y - 20), (cx + 3, base_y - 28),
           (cx + 1, base_y - 31), (cx - 1, base_y - 28),
           (cx - 4, base_y - 20)]
    _poly(surf, _HR_WHITE_D, [(x + 1, y) for x, y in hed])
    _poly(surf, _HR_WHITE, hed)
    # Slim rounded tip — a small cap, NOT a knob (radius 2, sat right on the point).
    pygame.draw.circle(surf, _HR_WHITE, (cx + 1, base_y - 30), 2)
    pygame.draw.circle(surf, _HR_WHITE_H, (cx, base_y - 30), 1)
    # Hedjet sheen — a tall pale highlight straight up the front face.
    pygame.draw.line(surf, _HR_WHITE_H, (cx - 1, base_y - 13),
                     (cx, base_y - 27), 2)
    pygame.draw.line(surf, _HR_WHITE_D, (cx + 4, base_y - 13),
                     (cx + 4, base_y - 21), 1)

    # Gold uraeus (rearing cobra) at the BROW, thrust FORWARD as a clear front-
    # spike so the crown reads directional/pharaonic (front ≠ back — the falcon
    # faces right, so the cobra strikes forward-right off the brow).
    ux, uy = cx + 6, base_y + 1
    _poly(surf, _HR_GOLD, [(ux - 2, uy + 2), (ux + 4, uy + 2),
                           (ux + 5, uy - 1), (ux - 1, uy - 1)])      # cobra hood
    pygame.draw.line(surf, _HR_GOLD, (ux + 3, uy - 1), (ux + 7, uy - 5), 3)  # rearing neck
    pygame.draw.line(surf, _HR_GOLD_H, (ux + 3, uy - 1), (ux + 6, uy - 4), 1)
    pygame.draw.circle(surf, _HR_GOLD_H, (ux + 7, uy - 5), 2)        # head bead
    pygame.draw.circle(surf, _HR_RED, (ux + 8, uy - 6), 1)           # eye spot


build = store_skins._make_skin(_paint, base_fn=_horus_base)
