"""SOCCER redesign — design_4 THE FLYING DUTCHMAN (exploration only).

The Netherlands '74 total-football kit on Pip: a fully electric-orange
re-plumaged macaw whose signature tell is the TWO bold black stripes that run
off the shoulder and down the WING — the '74 jersey's sleeve graphic painted
along the wing's long axis so it reads at 40px in motion rather than as fiddly
chest trim. A small dark hair accent replaces a hat, a slim black scoop collar
sits at the neck, and the kit is finished off below with a black shorts
waistband, black socks and small orange cleats with black studs.

The whole bird is re-plumaged orange through the palette so the body reads as
the jersey itself; black is reserved for the high-contrast kit graphics that
carry the silhouette — chiefly the two wing stripes.

R2 fix-list (each tied to the 40px read):
  * The two shoulder stripes were lifted off the crown and reparented to the
    WING, flowing from the wing-root down the wing's diagonal long axis toward
    the tip — the '74 sleeve graphic, where this kit's identity actually lives.
  * Each stripe is BLACK, 2px wide, with a clean 2px orange gap between them so
    "two stripes" survives downscale as high-contrast black-on-orange.
  * The hair crest was cut ~60% to a small narrow dark accent (~3px tall) so it
    stops merging with the stripes into one dark mass on top of the bird.
  * The sub-pixel lion shield + back number were dropped; the wing stripes are
    the identity and nothing is left to dilute them.
  * Feet simplified to a 2px black sock, a small hard-edged orange cleat and 3
    black stud dots — no sock turnover that wouldn't survive 1x.

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
_BLACK      = (17, 17, 17)         # #111111 stripes / accent / boots
_OUTLINE    = (58, 21, 0)          # #3A1500 warm dark outline
_WHITE      = (250, 248, 244)

# Full electric-orange re-plumage so the bird IS the '74 jersey. Every feather
# slot is an orange value; the beak is held a touch darker-orange so a warm
# macaw bill survives without going scarlet. Lenses are dropped so the head
# stays a clean orange dome that lets the wing stripes own the read.
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
    # Orange-suited bird, no aviators — the head stays a clean dome so the
    # wing stripes are the uncontested signature.
    return _build_parrot_with_palette(angle_deg, _KIT_PAL, draw_lenses=False)


def _wing_stripes(surf):
    """The '74 signature: two bold black stripes running off the shoulder and
    down the WING along its long axis. The wing sits over the back at roughly
    composite x=33..53 / y=36..62, its long axis sweeping from the wing-root
    (near the body, upper area) out toward the wingtip. The two stripes are
    drawn parallel to that diagonal: 2px BLACK each with a 2px orange gap, the
    only thing that reads as "two stripes" at 40px (high-contrast black-on-
    orange). Drawn last so they stay crisp over the feather divider lines.
    """
    # Wing-root anchor (shoulder, near the body) and wingtip anchor, picked to
    # sit ON the painted wing feathers rather than over bare body/sky.
    root_a = (HX - 11, HY + 7)     # upper stripe, at the shoulder
    tip_a  = (HX + 5,  HY + 22)    # upper stripe, toward the tip
    root_b = (HX - 8,  HY + 9)     # lower stripe, 2px offset across the wing
    tip_b  = (HX + 8,  HY + 24)
    pygame.draw.line(surf, _BLACK, root_a, tip_a, 2)
    pygame.draw.line(surf, _BLACK, root_b, tip_b, 2)


def _hair_accent(surf):
    """Small dark hair accent on the crown — a thin swept wedge, NOT a crest.
    Cut ~60% from R1 so it no longer merges with the stripes into one dark mass;
    a single narrow shape (~3px tall) that just hints slicked-back hair."""
    base_y = CROWN_Y + 1
    # One low swept wedge leaning forward, plus a thin slick band tying it down.
    pygame.draw.polygon(surf, _BLACK, [
        (HX - 6, base_y + 3), (HX - 1, base_y),
        (HX + 4, base_y + 3)])
    pygame.draw.line(surf, _BLACK, (HX - 7, base_y + 3), (HX + 5, base_y + 2), 2)
    # Single gloss sweep so the hair reads wet-look, not matte.
    pygame.draw.line(surf, (70, 70, 70), (HX - 5, base_y + 2), (HX + 2, base_y + 1), 1)


def _collar(surf):
    """Slim black scoop collar at the neck — a shallow dark crescent under the
    chin, kept as one simple shape so it doesn't smear at thumbnail."""
    collar = pygame.Surface((26, 12), pygame.SRCALPHA)
    pygame.draw.ellipse(collar, _BLACK, (0, -6, 26, 14))
    pygame.draw.ellipse(collar, (0, 0, 0, 0), (3, -3, 20, 12))
    surf.blit(collar, (HX - 16, HY + 2))


def _waistband_and_boots(surf):
    """Black shorts waistband at the tail base, black socks and small orange
    cleats with black studs — the kit's footing, forming the bottom of the
    read. Simplified: 2px sock, hard-edged cleat, 3 stud dots, no turnover."""
    # Shorts waistband — a dark band across the tail base.
    pygame.draw.rect(surf, _BLACK, (HX - 24, 70, 22, 4), border_radius=2)
    pygame.draw.line(surf, (70, 70, 70), (HX - 23, 71), (HX - 4, 71), 1)

    # Two legs: a short black sock, a small hard-edged orange cleat, 3 studs.
    for lx in (HX - 21, HX - 13):
        # Black sock (2-3px tall band above the foot).
        pygame.draw.rect(surf, _BLACK, (lx - 2, 69, 5, 3))
        # Small orange cleat — hard rectangle so the edges survive 1x.
        pygame.draw.rect(surf, _ORANGE, (lx - 3, 72, 7, 4))
        pygame.draw.line(surf, _ORANGE_HI, (lx - 3, 72), (lx + 3, 72), 1)
        # Three black stud dots underneath.
        pygame.draw.circle(surf, _BLACK, (lx - 2, 76), 1)
        pygame.draw.circle(surf, _BLACK, (lx,     76), 1)
        pygame.draw.circle(surf, _BLACK, (lx + 2, 76), 1)


def _paint(surf, wing_angle_deg):
    # Footing first so the body/tail edges overlap its top.
    _waistband_and_boots(surf)
    # Chest collar.
    _collar(surf)
    # THE signature tell, painted over the wing last so it stays crisp.
    _wing_stripes(surf)
    # Small hair accent last so it sits in front of the crown.
    _hair_accent(surf)


build = store_skins._make_skin(_paint, base_fn=_kit_base)
