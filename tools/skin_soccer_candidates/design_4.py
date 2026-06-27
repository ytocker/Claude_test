"""SOCCER redesign — design_4 THE FLYING DUTCHMAN (exploration only).

The Netherlands '74 total-football kit on Pip: a fully electric-orange
re-plumaged macaw whose signature tell is the TWO bold black stripes that
flow off each shoulder and run down the wing — the '74 jersey's most
recognisable graphic, painted onto the wing shape itself so it reads at
40px in motion rather than as fiddly chest trim. A glossy swept-back black
hair crest replaces a hat, a slim black scoop collar + lion-crest shield
sit at the chest, a "14" hint rides the back, and the kit is finished off
below with a black shorts waistband, black socks and orange cleats with
black studs.

The whole bird is re-plumaged orange through the palette so the body reads
as the jersey itself; black is reserved for the high-contrast kit graphics
that carry the silhouette.

Scratch builder — NOT registered in store_skins.BUILDERS. Production art is
untouched until a winner is picked.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette ──────────────────────────────────────────────────────────────────
_ORANGE     = (255, 106, 0)        # #FF6A00 electric-orange jersey
_ORANGE_HI  = (255, 166, 77)       # #FFA64D highlight
_ORANGE_SH  = (194, 74, 0)         # #C24A00 body shadow
_BLACK      = (17, 17, 17)         # #111111 stripes / crest / boots
_OUTLINE    = (58, 21, 0)          # #3A1500 warm dark outline
_WHITE      = (250, 248, 244)

# Full electric-orange re-plumage so the bird IS the '74 jersey. Every feather
# slot is an orange value; the beak is held a touch darker-orange so a warm
# macaw bill survives without going scarlet. Lenses are dropped — the swept
# hair crest owns the head.
_KIT_PAL = _pal(
    tail=[(194, 74, 0), (224, 90, 6), (255, 106, 0), (255, 140, 50)],
    tail_line=_ORANGE_SH,
    body_shadow=_ORANGE_SH,
    body_main=_ORANGE,
    body_chest=(255, 130, 36),
    body_belly=(255, 150, 60),
    sheen=(255, 255, 255, 70),
    wing_main=(255, 116, 14),
    wing_dark=_ORANGE_SH,
    wing_tip=_ORANGE_HI,
    wing_secondary=None,
    wing_highlight=_ORANGE_HI,
    head_shadow=_ORANGE_SH,
    head_main=_ORANGE,
    head_cheek=(255, 140, 55),
    head_crown=(255, 128, 34),
    lens_frame=(200, 80, 10),
    lens_body=_ORANGE_SH,
    lens_tint=None,
    lens_glint=None,
    beak_main=(214, 92, 14),       # slightly darker orange bill
    beak_dark=(150, 60, 6),
    beak_gloss=(255, 170, 90),
    foot=(214, 92, 14),
)


def _kit_base(angle_deg):
    # Orange-suited bird, no aviators — the swept hair crest owns the head.
    return _build_parrot_with_palette(angle_deg, _KIT_PAL, draw_lenses=False)


def _shoulder_stripes(surf):
    """The '74 signature: two bold parallel black stripes flowing off each
    shoulder down the wing. Painted onto the wing silhouette itself so the
    graphic IS the wing — this is the single element that has to survive the
    40px in-motion read, so each stripe is kept WIDE (3px, 4px apart).
    """
    # LEFT wing — sweeps down toward the lower-left primaries.
    pygame.draw.line(surf, _BLACK, (HX - 12, HY - 5), (HX - 26, HY + 16), 3)
    pygame.draw.line(surf, _BLACK, (HX - 8,  HY - 4), (HX - 22, HY + 18), 3)
    # RIGHT wing — sweeps down toward the trailing wingtip.
    pygame.draw.line(surf, _BLACK, (HX + 2,  HY - 5), (HX + 10, HY + 16), 3)
    pygame.draw.line(surf, _BLACK, (HX + 6,  HY - 4), (HX + 14, HY + 18), 3)


def _hair_crest(surf):
    """Glossy swept-back black hair crest along the crown — no hat. A row of
    angled wedges marching from the back of the head toward the front, each
    leaning the same way so it reads as slicked-back hair, not feathers."""
    base_y = CROWN_Y - 1
    # Back-to-front: rising spikes that lean forward (toward higher x).
    crest = [
        (HX - 9, base_y + 2, 5, 7),
        (HX - 5, base_y - 1, 5, 8),
        (HX - 1, base_y - 2, 5, 8),
        (HX + 3, base_y,     4, 6),
    ]
    for cx, cy, w, h in crest:
        # Forward-leaning wedge: root at the crown, tip swept toward the beak.
        pygame.draw.polygon(surf, _BLACK, [
            (cx - w, cy + h), (cx, cy), (cx + w, cy + h)])
    # Slick base band tying the wedges into one mass along the crown.
    pygame.draw.polygon(surf, _BLACK, [
        (HX - 11, base_y + 6), (HX + 7, base_y + 4),
        (HX + 6, base_y + 9), (HX - 11, base_y + 10)])
    # Single gloss sweep so the hair reads wet-look, not matte.
    pygame.draw.line(surf, (70, 70, 70), (HX - 8, base_y + 5), (HX + 4, base_y + 3), 1)


def _collar_and_crest(surf):
    """Slim black scoop collar at the neck + a tiny lion-crest shield over the
    heart. Both kept as simple dark shapes so they don't smear at thumbnail."""
    # Scoop collar — a shallow dark crescent under the chin.
    collar = pygame.Surface((26, 12), pygame.SRCALPHA)
    pygame.draw.ellipse(collar, _BLACK, (0, -6, 26, 14))
    pygame.draw.ellipse(collar, (0, 0, 0, 0), (3, -3, 20, 12))
    surf.blit(collar, (HX - 16, HY + 2))

    # Lion-crest shield over the heart (left chest) — small dark pentagon.
    sx, sy = HX - 6, HY + 9
    pygame.draw.polygon(surf, _BLACK, [
        (sx, sy), (sx + 6, sy), (sx + 6, sy + 4),
        (sx + 3, sy + 8), (sx, sy + 4)])
    # Faint orange notch so it reads as a crest, not a dark blob.
    pygame.draw.line(surf, _ORANGE_HI, (sx + 3, sy + 1), (sx + 3, sy + 4), 1)


def _back_number(surf):
    """A black '14' hint on the back of the jersey (upper-left body), small
    and low-contrast enough to be a tell without competing with the stripes."""
    # '1'
    pygame.draw.line(surf, _BLACK, (HX - 21, HY + 8), (HX - 21, HY + 15), 2)
    # '4'
    pygame.draw.line(surf, _BLACK, (HX - 17, HY + 8), (HX - 17, HY + 12), 2)
    pygame.draw.line(surf, _BLACK, (HX - 17, HY + 12), (HX - 13, HY + 12), 2)
    pygame.draw.line(surf, _BLACK, (HX - 13, HY + 8), (HX - 13, HY + 15), 2)


def _waistband_and_boots(surf):
    """Black shorts waistband at the tail base, black socks, and orange cleats
    with black studs — the kit's footing, forming the bottom of the read."""
    # Shorts waistband — a dark band across the tail base.
    pygame.draw.rect(surf, _BLACK, (HX - 24, 70, 22, 4), border_radius=2)
    pygame.draw.line(surf, (70, 70, 70), (HX - 23, 71), (HX - 4, 71), 1)

    # Two legs: black sock with an orange turnover, shin-guard band, then an
    # orange cleat with black stud dots underneath.
    for lx in (HX - 21, HX - 13):
        # Black sock.
        pygame.draw.rect(surf, _BLACK, (lx - 2, 65, 5, 8), border_radius=2)
        # Orange turnover at the top of the sock.
        pygame.draw.rect(surf, _ORANGE, (lx - 2, 65, 5, 2))
        # Shin-guard band hint.
        pygame.draw.line(surf, _ORANGE_HI, (lx - 2, 68), (lx + 2, 68), 1)
        # Orange cleat.
        pygame.draw.ellipse(surf, _ORANGE, (lx - 4, 72, 9, 5))
        pygame.draw.ellipse(surf, _ORANGE_HI, (lx - 3, 72, 6, 2))
        # Black studs.
        pygame.draw.circle(surf, _BLACK, (lx - 2, 77), 1)
        pygame.draw.circle(surf, _BLACK, (lx + 2, 77), 1)


def _paint(surf, wing_angle_deg):
    # Footing first so the body/tail edges overlap its top.
    _waistband_and_boots(surf)
    # Back number under the wing stripes so the stripes win any overlap.
    _back_number(surf)
    # Chest kit.
    _collar_and_crest(surf)
    # THE signature tell, painted over the wings last so it stays crisp.
    _shoulder_stripes(surf)
    # Head crest last so it sits in front of the crown.
    _hair_crest(surf)


build = store_skins._make_skin(_paint, base_fn=_kit_base)
