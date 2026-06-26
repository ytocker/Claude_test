"""design_5 · BINKY — EPIC baby-parrot exploration (scratch only).

The "pacifier baby" — the only baby concept that reads as a literal swaddled
HUMAN infant, not a baby bird. After the first pass proved too prop-dense at
40px, this build is a disciplined SUBTRACTION: ONE hero (the pacifier), a LIGHT
baby face, restored eye-domes, and a quiet cream bib. Everything that competed
for the eye is gone.

North star is "lives or dies at 40px on BOTH skies". The whole sprite is now
read as three beats only: a clear pink RING-WITH-HOLE plugged at the beak, a
LIGHT powder-blue baby face with two white eye-domes above it, and a cream bib
crescent below. Nothing else fights.

Discipline notes that drove the redraw:
  * Head value is the priority — the face is lifted to the body powder-blue so it
    is no longer the darkest, least-cute zone; head shadow is held no darker than
    the palette teal so the white eye-domes pop instead of voiding into navy.
  * The pacifier is the ONLY bright pink on the sprite and the ONLY front hero: a
    hollow ring with a hard dark hole punched through its centre so it reads as a
    RING, not a pink dot, plus a 2-value button dome.
  * The bib is demoted to a single CREAM 2-scallop crescent so it stops competing
    for the pink-focal slot; the heart/trim sub-pixel noise is cut.
  * One pink budget: pacifier + a 1px cheek-blush dot, nothing more. Belly fluff
    wisps and milk-spot pink are gone.
  * One tucked foot, one thinned 2px cowlick sprout.

Matte pastel pigment, NO glow. PRISM model — pacifier, bib, cowlick, eye-domes
are polygons/lines/circles over a powder-blue recolour; no back layer. NEVER
registered in BUILDERS.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Binky palette. The body is the brand powder-blue, lifted just enough to hold
# against bright day sky; the head now shares that SAME light value so the baby's
# face is no longer a muddy dark zone. The teal is the deepest the head shadow is
# allowed to go (it owns line-work + seating shadows so props still seat), and a
# darker teal is reserved for hard keylines / the punched ring hole. Pink is held
# ENTIRELY for the pacifier so it stays the single focal; cream carries the bib;
# curl-tan the cowlick. Aviators retinted cool sky-aqua (Pip's tell).
_BB_BLUE    = (191, 224, 234)      # #BFE0EA powder-blue body (brand reference)
_BB_BLUE_HI = (202, 230, 239)      # lifted working blue — holds on bright day sky
_BB_TEAL    = (127, 180, 194)      # #7FB4C2 teal — the FLOOR for head shadow value
_BB_TEAL_D  = (96, 150, 165)       # deeper teal for prop seating rims only
_BB_HOLE    = (42, 53, 64)         # #2A3540 hard dark hole punched through the ring
_BB_BELLY   = (228, 243, 247)      # #E4F3F7 pale belly highlight
_BB_PINK    = (229, 138, 160)      # #E58AA0 pacifier base rose
_BB_PINK_HI = (246, 184, 200)      # #F6B8C8 brighter pink button dome (2-value pop)
_BB_PINK_LT = (255, 222, 232)      # pink shine spec / cheek blush
_BB_PINK_D  = (196, 110, 134)      # rose shadow so the button reads round
_BB_CREAM   = (251, 244, 218)      # #FBF4DA bib cream
_BB_CREAM_D = (224, 214, 178)      # bib under-shadow so the crescent seats
_BB_TAN     = (201, 168, 106)      # #C9A86A curl-tan cowlick
_BB_TAN_D   = (160, 130, 76)       # cowlick shadow root
_BB_WHITE   = (250, 252, 253)      # big-baby catch-light dome
_BB_INK     = (40, 56, 70)         # eye pupil


# Full powder-blue re-plumage with a LIGHT head. The head slots are lifted to the
# body value (and the head shadow held to the palette teal, not darker) so the
# face is the cute light zone the eye-domes can pop against — the single biggest
# fix from the first pass. Pink stays out of the plumage entirely so the pacifier
# owns the only pink on the bird. Aviators retinted sky-aqua (Pip's tell).
P_BINKY = _pal(
    tail=[(118, 168, 182), (150, 196, 208), (178, 214, 226), (206, 232, 240)],
    tail_line=_BB_TEAL_D,
    body_shadow=(150, 196, 208),
    body_main=_BB_BLUE_HI,
    body_chest=(214, 236, 243),
    body_belly=_BB_BELLY,
    sheen=(255, 255, 255, 120),
    wing_main=(176, 212, 224),
    wing_dark=(120, 172, 188),
    wing_tip=(220, 238, 244),
    wing_secondary=None,               # single-hue powder-blue — no contrast feather
    wing_highlight=(236, 247, 250),    # cream-pale wing highlight (kept)
    # Head lifted to body value; the shadow is the palette teal — the floor — so
    # the face never crushes to slate-navy and the eye-domes read against it.
    head_shadow=_BB_TEAL,
    head_main=_BB_BLUE_HI,
    head_cheek=(216, 237, 244),
    head_crown=(196, 226, 235),        # crown only a hair below the face, stays light
    lens_frame=(92, 124, 140),         # cool slate rims — read against pale head
    lens_body=(44, 66, 80),
    lens_tint=(168, 214, 230, 130),    # sky-aqua lens tint
    lens_glint=(248, 252, 254),
    beak_main=(214, 200, 168),         # muted so the pink pacifier owns the front
    beak_dark=(150, 132, 102),
    beak_gloss=(248, 244, 228),
    foot=(150, 132, 102),
)


def _cowlick(surf):
    """A single thin tan sprout off the crown — the cartoon-baby spit-curl, kept
    to a 2px stroke so it stays a distinct little hook and never blobs into the
    light head. A dark root + lit edge keep it round at 40px."""
    curl = [
        (HX - 1, CROWN_Y + 1),     # root, buried 1px into the crown
        (HX, CROWN_Y - 4),
        (HX + 3, CROWN_Y - 6),     # apex of the loop
        (HX + 5, CROWN_Y - 4),
        (HX + 4, CROWN_Y - 1),     # hook curling back = the spit-curl
    ]
    pygame.draw.lines(surf, _BB_TAN_D, False, curl, 3)   # dark under-stroke (root)
    pygame.draw.lines(surf, _BB_TAN, False, curl, 2)     # thin tan body
    pygame.draw.line(surf, _BB_PINK_LT, curl[1], curl[2], 1)  # lit inner edge


def _eye_domes(surf):
    """Two oversized white catch-light domes tucked just under the aviator lenses
    + a 1px ink pupil each — restored now the head is light enough for them to
    pop (neoteny). A teal seat keeps them from melting into the cheek."""
    for ex, ey in ((HX - 4, HY + 6), (HX + 6, HY + 5)):
        pygame.draw.circle(surf, _BB_TEAL, (ex - 1, ey), 3)      # seat rim
        pygame.draw.circle(surf, _BB_WHITE, (ex - 1, ey), 2)     # big white dome
        pygame.draw.circle(surf, _BB_INK, (ex, ey), 1)           # tiny pupil


def _bib(surf):
    """A quiet CREAM bib — one 2-scallop crescent low on the chest. Cream (not
    pink) so it stops competing for the pink-focal slot; no heart, no trim line
    (sub-pixel noise at 40px). A cream-dark under-shadow seats the crescent on the
    powder-blue chest so it still reads as one soft band."""
    cy = 52
    # Two soft scallop bumps = the classic bib edge, nothing more.
    scallops = [(28, cy + 2), (35, cy + 2)]
    for sx, sy in scallops:
        pygame.draw.circle(surf, _BB_CREAM_D, (sx, sy + 1), 4)   # seating shadow
    for sx, sy in scallops:
        pygame.draw.circle(surf, _BB_CREAM, (sx, sy), 4)
    # A short collar band ties the two scallops into one crescent.
    pygame.draw.line(surf, _BB_CREAM, (27, cy - 2), (36, cy - 2), 3)
    pygame.draw.line(surf, _BB_CREAM_D, (27, cy + 1), (36, cy + 1), 1)


def _pacifier(surf):
    """The ONE hero — an oversized pacifier plugged at the beak base, front-centre.
    A hollow pink RING with a hard dark HOLE punched through its centre (so it
    reads as a ring, not a dot) sits ahead of a 2-value pink button dome. This is
    the only bright pink on the sprite; a teal keyline seats it off the beak."""
    # Composite anchor: beak-base front-centre, just under/ahead of the beak so the
    # binky owns the lower-face silhouette without burying the aviators.
    bx, by = HX - 7, HY + 5         # composite ~(40, 46)
    # Button shield against the face — a fat dome with a 2-value pop (bright dome
    # over a rose base) so it reads round and plush.
    pygame.draw.circle(surf, _BB_TEAL_D, (bx, by + 1), 6)        # seating shadow
    pygame.draw.circle(surf, _BB_PINK_D, (bx, by), 5)
    pygame.draw.circle(surf, _BB_PINK, (bx, by), 4)
    pygame.draw.circle(surf, _BB_PINK_HI, (bx - 1, by - 1), 3)   # brighter dome top
    pygame.draw.circle(surf, _BB_PINK_LT, (bx - 1, by - 2), 1)   # glossy shine spec
    # The hero RING jutting out front. Outer Ø ≥7px (r=4 → Ø8) with a ≥3px rim, and
    # a hard dark hole punched dead-centre so the open-ring read survives downscale.
    rx, ry = bx - 7, by
    pygame.draw.circle(surf, _BB_TEAL_D, (rx, ry), 5)            # outer keyline disc
    pygame.draw.circle(surf, _BB_PINK, (rx, ry), 4)             # solid pink disc
    pygame.draw.circle(surf, _BB_PINK_HI, (rx - 1, ry - 1), 1)   # ring rim highlight
    pygame.draw.circle(surf, _BB_HOLE, (rx, ry), 2)             # PUNCHED dark hole
    # A short pink stem ties button + ring into ONE object.
    pygame.draw.line(surf, _BB_PINK, (bx - 4, by), (rx + 3, ry), 3)
    pygame.draw.line(surf, _BB_TEAL_D, (bx - 4, by + 1), (rx + 3, ry + 1), 1)


def _rimlight(surf):
    """A 1px darker-teal rim-light tracing the lower-left silhouette. Cheap
    insurance so the pale powder-blue body never voids into navy night sky — it
    gives the bottom edge a hard separation line on dark backgrounds without
    touching the day read (the rim sits just inside the outline)."""
    pts = [(20, 62), (26, 68), (34, 70), (42, 68)]
    pygame.draw.lines(surf, _BB_TEAL_D, False, pts, 1)


def _paint_binky(surf, _a):
    # SUBTRACTION pass — three beats only: eyes, bib, pacifier (+ cowlick + 1px
    # blush + rim-light insurance). Nothing else competes at 40px.

    # 1 · LOWER-SILHOUETTE RIM-LIGHT — navy-sky separation insurance.
    _rimlight(surf)

    # 2 · BIB — the quiet cream crescent (drawn before the face so the head/eyes
    #     sit cleanly above it).
    _bib(surf)

    # 3 · COWLICK — the single thinned crown curl.
    _cowlick(surf)

    # 4 · EYE-DOMES — the restored big-baby eyes on the now-light face.
    _eye_domes(surf)

    # 5 · CHEEK BLUSH — the single permitted 1px pink dot (the only pink besides
    #     the pacifier), low on the cheek for warmth.
    pygame.draw.circle(surf, _BB_PINK_LT, (HX + 9, HY + 7), 1)

    # 6 · HERO PACIFIER — painted LAST so it sits over everything as the
    #     unmistakable front tell, the one bright pink ring-with-hole.
    _pacifier(surf)


# Body recolour through the palette system + the binky overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_binky,
    base_fn=lambda a: _build_parrot_with_palette(a, P_BINKY),
)
