"""design_5 · BINKY — EPIC baby-parrot exploration (scratch only).

The "pacifier-and-bib cartoon baby" — the only baby concept that reads as a
literal swaddled HUMAN infant, not a baby bird. The hero is a big round
PACIFIER plugged at the beak: a hard pastel-pink ring + button that breaks the
lower-face silhouette and reads as the front tell before any other detail. A
scalloped bib bands the upper chest, a single curl-cowlick sprouts off the
crown, and big-baby white catch-light domes sit under the aviators (which stay,
retinted cool sky-aqua — Pip's tell).

North star is "lives or dies at 40px on BOTH skies". This is the most
prop-stacked baby concept, so it is disciplined to ONE clear hero: the pacifier
ring is a chunky ≥3px pastel-pink loop with a teal keyline that survives
downscale and never dissolves into the beak. Everything else is held to one
beat per zone — one scalloped bib band, one cowlick, one milk-spot + two fluff
wisps — so nothing competes with the binky. Powder-blue body is lifted just
enough to hold value against bright DAY sky without going chalky, and the teal
shadow keeps it from going muddy on navy NIGHT sky. Matte pastel pigment, NO
glow. PRISM model — pacifier, bib, cowlick, eye-domes are polygons/lines/circles
over a powder-blue recolour; no back layer. NEVER registered in BUILDERS.
"""
import math

import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Binky palette — soft powder-blue body with a teal shadow that owns the line
# work (so the pale body still carries a dark→light ramp on navy night sky), a
# pale belly bright for the milk-spot to echo, and pastel-pink reserved for the
# pacifier + bib so the props read as a separate cute "object" layer, not
# plumage. Cream is the bib trim; curl-tan the cowlick. Aviators retinted cool
# sky-aqua so the lenses stay glassy-baby without going white.
# Body slots are lifted ~6% in value off the #BFE0EA spec so the powder-blue
# never voids into bright day sky at 40px; the teal shadow stays deep so the
# ramp survives downscale.
_BB_BLUE    = (191, 224, 234)      # #BFE0EA powder-blue body (brand reference)
_BB_BLUE_HI = (202, 230, 239)      # lifted working blue — holds on bright day sky
_BB_TEAL    = (127, 180, 194)      # #7FB4C2 teal shadow / keyline
_BB_TEAL_D  = (96, 150, 165)       # deeper teal so props seat with a hard rim
_BB_BELLY   = (228, 243, 247)      # #E4F3F7 pale belly + milk-spot
_BB_PINK    = (246, 184, 200)      # #F6B8C8 pacifier + bib pastel-pink
_BB_PINK_D  = (214, 138, 160)      # rose shadow under the pink so it reads round
_BB_PINK_H  = (255, 222, 232)      # pink lit edge / pacifier shine
_BB_CREAM   = (251, 244, 218)      # #FBF4DA bib-trim cream
_BB_TAN     = (201, 168, 106)      # #C9A86A curl-tan cowlick
_BB_TAN_D   = (160, 130, 76)       # cowlick shadow root
_BB_AQUA    = (168, 214, 230)      # #A8D6E6 sky-aqua aviator tint
_BB_WHITE   = (250, 252, 253)      # big-baby catch-light dome


# Full powder-blue re-plumage. The shadow slots run teal so the pale body keeps
# a dark→light range (critical on bright day sky where a flat pale bird voids);
# the belly + chest stay near-white so the milk-spot highlight reads as part of
# the body. Pink is kept ENTIRELY out of the plumage — it belongs only to the
# overlaid pacifier + bib so those props read as a stuck-on baby object layer.
# Aviators retinted sky-aqua (cool, glassy-baby) so the lenses stay Pip's tell.
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
    wing_highlight=(236, 247, 250),
    head_shadow=(150, 196, 208),
    head_main=_BB_BLUE_HI,
    head_cheek=(214, 236, 243),
    head_crown=(184, 218, 229),
    lens_frame=(92, 124, 140),         # cool slate rims — read against pale head
    lens_body=(44, 66, 80),
    lens_tint=(168, 214, 230, 130),    # sky-aqua lens tint
    lens_glint=(248, 252, 254),
    beak_main=(214, 200, 168),         # muted so the pink pacifier owns the front
    beak_dark=(150, 132, 102),
    beak_gloss=(248, 244, 228),
    foot=(150, 132, 102),
)


def _fluff(surf, x, y, dx, dy):
    """One short downy wisp poking just past the body silhouette — a 2–3px
    tapered sliver so the costume still reads fuzzy-baby, not only propped. A
    teal-dark backing gives it a value edge that survives downscale."""
    tip = (x + dx, y + dy)
    base0 = (x - dy // 3, y + dx // 3)
    base1 = (x + dy // 3, y - dx // 3)
    pygame.draw.polygon(surf, _BB_TEAL, [base0, base1, (tip[0] + 1, tip[1] + 1)])
    pygame.draw.polygon(surf, _BB_BELLY, [base0, base1, tip])


def _cowlick(surf):
    """A single bold curl sprout off the crown — the classic cartoon-baby
    hair-curl. Drawn as a thick tan stroke that loops up-and-over into a little
    hook, with a dark root + a lit inner edge so it reads round and breaks the
    crown silhouette as one clear shape (not a stray hair) at 40px."""
    # Curl path: rises off the crown then hooks back on itself = the classic
    # baby spit-curl. Kept short so it lands just past the crown, not aloft.
    curl = [
        (HX - 1, CROWN_Y + 1),     # root, buried 1px into the crown
        (HX - 1, CROWN_Y - 4),
        (HX + 2, CROWN_Y - 7),     # apex of the loop
        (HX + 5, CROWN_Y - 5),
        (HX + 4, CROWN_Y - 2),     # hook curling back down = the spit-curl
    ]
    pygame.draw.lines(surf, _BB_TAN_D, False, curl, 4)   # dark root/under-stroke
    pygame.draw.lines(surf, _BB_TAN, False, curl, 3)     # tan body
    pygame.draw.lines(surf, _BB_PINK_H, False, curl[1:3], 1)  # lit inner edge


def _pacifier(surf):
    """The HERO — an oversized pacifier plugged at the beak base. A hard
    pastel-pink RING (chunky ≥3px loop) + a round button held at the front of
    the lower face so it breaks the silhouette and reads instantly as a binky.
    A teal keyline seats the pink off the beak so it never dissolves into it;
    one bright shine spec sells the glossy plastic."""
    # The pacifier sits at the front of the lower face, just under/ahead of the
    # beak base. Composite-space anchor to the lower-right of the head centre,
    # dropped clear of the aviators so the binky owns the lower-face silhouette
    # without burying Pip's tell.
    bx, by = HX + 12, HY + 8
    # The teat/shield button against the face — a fat pink disc with a rim.
    pygame.draw.circle(surf, _BB_TEAL_D, (bx - 1, by), 6)        # seating shadow
    pygame.draw.circle(surf, _BB_PINK_D, (bx, by), 5)
    pygame.draw.circle(surf, _BB_PINK, (bx, by), 4)
    pygame.draw.circle(surf, _BB_PINK_H, (bx - 1, by - 1), 2)    # glossy shine spec
    # The hero RING jutting out front — a chunky pink loop with a teal keyline so
    # the open-circle binky read survives downscale. Drawn as two concentric
    # circles (outline-only) so the ring stays hollow.
    rx, ry = bx + 6, by + 1
    pygame.draw.circle(surf, _BB_TEAL_D, (rx, ry), 6, 1)         # outer keyline
    pygame.draw.circle(surf, _BB_PINK, (rx, ry), 6, 3)           # chunky pink ring
    pygame.draw.circle(surf, _BB_PINK_H, (rx + 1, ry - 2), 1)    # ring highlight
    # A short pink stem links the button to the ring so they read as ONE object.
    pygame.draw.line(surf, _BB_PINK, (bx + 3, by), (rx - 4, ry), 3)
    pygame.draw.line(surf, _BB_TEAL_D, (bx + 3, by + 1), (rx - 4, ry + 1), 1)


def _bib(surf):
    """A scalloped pastel-pink bib banding the upper chest — the body object.
    Kept simple: ONE scalloped band (a row of soft bumps) with a 2px cream trim
    line + a single tiny heart motif, so it reads as a bib without over-detailing
    and competing with the pacifier at 40px. A teal under-line separates the pink
    band from the powder-blue chest so the complementary pastels don't shimmer."""
    # Bib spans the upper chest below the head, curving with the body. Anchored
    # in composite body space (~x32, the body centre, dropping to ~x24 chest).
    cy = 50
    # Scalloped lower rim — a row of soft bumps (the classic bib edge). Built as
    # overlapping circles along an arc so the band reads as one scalloped shape.
    scallops = [(24, cy + 5), (29, cy + 7), (34, cy + 7), (39, cy + 5)]
    # Solid bib band first (a filled wedge from the collar down to the scallops).
    band = [(22, cy - 2), (40, cy - 4), (41, cy + 4), (21, cy + 2)]
    pygame.draw.polygon(surf, _BB_TEAL, band)                    # seating under-shadow
    pygame.draw.polygon(surf, _BB_PINK, [(22, cy - 3), (40, cy - 5),
                                         (41, cy + 3), (21, cy + 1)])
    for sx, sy in scallops:
        pygame.draw.circle(surf, _BB_PINK, (sx, sy), 4)
        pygame.draw.circle(surf, _BB_PINK_D, (sx, sy), 4, 1)     # bump separation
    # The 2px cream trim line tracing the bib's upper collar edge — the read.
    pygame.draw.line(surf, _BB_CREAM, (22, cy - 2), (40, cy - 4), 2)
    pygame.draw.line(surf, _BB_TEAL_D, (22, cy + 1), (40, cy - 1), 1)  # no-shimmer sep
    # One tiny cream heart motif dead-centre on the bib (the bib's single charm).
    hx, hy = 31, cy + 1
    pygame.draw.circle(surf, _BB_CREAM, (hx - 1, hy - 1), 2)
    pygame.draw.circle(surf, _BB_CREAM, (hx + 1, hy - 1), 2)
    pygame.draw.polygon(surf, _BB_CREAM, [(hx - 3, hy), (hx + 3, hy), (hx, hy + 3)])


def _paint_binky(surf, _a):
    # BODY ACCENTS — ONE beat per zone so nothing competes with the pacifier.

    # 1 · BIG-BABY EYE DOMES — oversized white catch-light domes sitting under
    #     each aviator lens so the eyes read huge below the frames (neoteny). A
    #     teal rim seats them so they don't void into the pale head on day sky.
    L = (HX - 4, HY)
    R = (HX + 6, HY - 1)
    for ex, ey in (L, R):
        pygame.draw.circle(surf, _BB_TEAL_D, (ex - 1, ey + 6), 3)
        pygame.draw.circle(surf, _BB_WHITE, (ex - 1, ey + 6), 2)
        pygame.draw.circle(surf, (40, 56, 70), (ex, ey + 6), 1)   # tiny pupil

    # 2 · BELLY MILK-SPOT + FLUFF — a small pale milk-spot highlight low on the
    #     belly + two soft fluff wisps poking past the lower silhouette, so the
    #     costume still reads downy-baby, not only propped.
    pygame.draw.circle(surf, _BB_BELLY, (30, 60), 3)
    pygame.draw.circle(surf, _BB_WHITE, (29, 59), 1)
    _fluff(surf, 22, 58, -3, 2)
    _fluff(surf, 38, 60, 3, 3)

    # 3 · WING STUBBY HIGHLIGHT — a rounded bright blob at the wing mid faking a
    #     pudgy half-grown wing (the stubby-wing illusion) without touching
    #     geometry; one soft teal tuck at the tip.
    pygame.draw.circle(surf, _BB_BELLY, (33, 47), 3)
    pygame.draw.circle(surf, _BB_WHITE, (32, 46), 1)
    pygame.draw.circle(surf, _BB_TEAL, (40, 44), 2)

    # 4 · BIB — the scalloped chest band (one body object, kept simple).
    _bib(surf)

    # 5 · COWLICK — the single crown curl, breaking the crown outline.
    _cowlick(surf)

    # 6 · HERO PACIFIER — the binky ring + button at the beak, painted LAST so it
    #     sits over everything as the unmistakable front tell.
    _pacifier(surf)


# Body recolour through the palette system + the binky overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_binky,
    base_fn=lambda a: _build_parrot_with_palette(a, P_BINKY),
)
