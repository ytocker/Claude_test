"""RA — the sun-falcon god (DESIGN 3 of 5), the LEGENDARY pharaoh showpiece.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_pharaoh`` is untouched.

Concept: Ra, the solar-disk falcon — the 700-coin flex. The hero silhouette is a
big glowing GOLD SOLAR DISK crowning the head, ringed by a coiled gold uraeus
cobra and wrapped in a soft ``#FFF6C8`` bloom so it reads as a tiny sun and is
the single brightest thing on screen — instantly on day, dominantly on night.
Below it the bird is re-plumaged a warm GOLD that runs to AMBER toward the belly
(solar sheen), the face wears a sharp gold-and-black Eye-of-Ra liner, and a
WINGED SUN COLLAR fans falcon-wing feathers in gold + sky-blue + falcon-red
bands across the chest — kept strictly inside the body width so the silhouette
never balloons past the fixed hitbox. A gold was-scepter + small ankh are slung
diagonally in the wing, and gold talon-anklets sit at the feet line.

At 40px the read, in order of value: (1) the glowing solar-disk halo (the sun),
(2) a gold bird, (3) the banded winged collar across the chest, (4) the Eye-of-Ra
liner + the slung was/ankh. The disk bloom is drawn as stacked translucent rings
so it survives downscale as a luminous blob rather than a hard ring.

FOOTPRINT LAW: every body element (collar, was, ankh, anklets, recolor) stays
inside the base bird footprint; nothing crosses the feet line (~HY+24..28). ONLY
the solar disk + its bloom rise above CROWN_Y.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# RA palette — concept hexes. Sun gold leads, solar amber deepens the belly so
# the recolor reads as a warm-to-amber solar gradient, falcon red + sky blue are
# the collar's wing bands, and the glow cream is the disk bloom + every glint.
_SUN_GOLD   = (255, 210, 74)       # #FFD24A sun gold
_SUN_GOLD_D = (198, 150, 36)       # gold shadow / line work
_SOLAR_AMB  = (255, 138, 30)       # #FF8A1E solar amber (belly / lower body)
_SOLAR_AMB_D = (190, 96, 18)
_FALCON_RED = (192, 51, 31)        # #C0331F falcon red
_SKY_BLUE   = (46, 111, 176)       # #2E6FB0 sky blue
_SKY_BLUE_D = (28, 72, 122)
_RA_GLOW    = (255, 246, 200)      # #FFF6C8 solar bloom / hero glint
_RA_BLACK   = (28, 22, 16)         # Eye-of-Ra liner / dark separators
_DISK_HOT   = (255, 232, 150)      # disk inner-hot core


# Warm-to-amber GOLD re-plumage of the macaw: head/chest run sun-gold, belly +
# lower wing deepen to solar amber so the whole bird reads as glowing metal in
# motion. Lenses dropped — the Eye-of-Ra liner owns the face; beak kept warm gold
# so nothing cool survives; deepest amber-bronze does the line work.
_RA_BODY = _pal(
    tail=[(190, 96, 18), (214, 122, 24), (236, 156, 40), (255, 196, 70)],
    tail_line=(150, 78, 16),
    body_shadow=(196, 116, 22),
    body_main=_SUN_GOLD,
    body_chest=(255, 226, 120),
    body_belly=_SOLAR_AMB,
    sheen=(255, 252, 220, 120),
    wing_main=(245, 176, 50),
    wing_dark=(176, 96, 22),
    wing_tip=(255, 224, 120),
    wing_secondary=None,
    wing_highlight=_RA_GLOW,
    head_shadow=(204, 132, 28),
    head_main=_SUN_GOLD,
    head_cheek=(255, 226, 120),
    head_crown=(255, 214, 96),
    lens_frame=(204, 132, 28),
    lens_body=(150, 78, 16),
    lens_tint=None,
    lens_glint=None,
    beak_main=(255, 196, 70),
    beak_dark=(176, 110, 26),
    beak_gloss=(255, 240, 180),
    foot=(176, 110, 26),
)


def _ra_base(angle_deg):
    # Gold-and-amber solar bird, no aviators — the Eye-of-Ra liner owns the face.
    return _build_parrot_with_palette(angle_deg, _RA_BODY, draw_lenses=False)


def _disk_bloom(surf, cx, cy, r):
    """Soft solar aura: stacked translucent cream rings (largest, faintest first)
    so the disk reads as a luminous blob at 40px on night sky rather than a hard
    edge that downscale would alias away. Drawn onto its own SRCALPHA layer and
    blitted with additive blend so it brightens whatever sky sits behind it."""
    pad = r + 16
    glow = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    gc = (pad, pad)
    # Opaque-building rings (additive) so the bloom is a SOLID luminous disk that
    # the outline pass traces as a soft cream edge, not a faint fringe that
    # _add_outline would darken into a hard black ring.
    for rad, a in ((r + 15, 60), (r + 12, 90), (r + 9, 130),
                   (r + 6, 180), (r + 3, 230)):
        pygame.draw.circle(glow, (*_RA_GLOW, a), gc, rad)
    surf.blit(glow, (cx - pad, cy - pad), special_flags=pygame.BLEND_RGBA_ADD)


def _paint(surf, _a):
    # ── WINGED SUN COLLAR (drawn first, under the disk/face) — a usekh collar
    #    whose outer rows fan into stylised falcon-wing feathers. Three banded
    #    rows (gold → sky-blue → falcon-red) arc across the upper breast and
    #    sweep into short wing-feather points at each shoulder. Held strictly
    #    inside the body width (x ≈ HX-22 .. HX+2) so the silhouette never grows.
    ccx, ccy = HX - 9, HY + 12          # collar centre, on the upper chest
    # Three concentric banded arcs as filled lens-shaped rows.
    for rw, rh, col in ((19, 12, _SUN_GOLD), (16, 10, _SKY_BLUE),
                        (13, 8, _FALCON_RED)):
        pygame.draw.ellipse(surf, col, (ccx - rw, ccy - rh, rw * 2, rh + 6))
    # Re-open the centre so the rows read as stacked bands, not a solid bib.
    pygame.draw.ellipse(surf, _SUN_GOLD, (ccx - 9, ccy - 5, 18, 8))
    pygame.draw.ellipse(surf, _SUN_GOLD_D, (ccx - 9, ccy - 5, 18, 8), 1)
    # Falcon-wing feather points fanning off each shoulder — short stylised
    # primaries in alternating gold/blue, tucked inside the body silhouette.
    for sgn, ax in ((-1, ccx - 16), (1, ccx + 14)):
        for k, col in enumerate((_SUN_GOLD, _SKY_BLUE, _SUN_GOLD)):
            fx = ax + sgn * k * 3
            fy = ccy - 1 + k * 3
            _poly(surf, col, [(fx, fy - 3), (fx + sgn * 5, fy + 1),
                              (fx, fy + 4)])
        pygame.draw.line(surf, _FALCON_RED, (ax, ccy - 2),
                         (ax + sgn * 9, ccy + 7), 2)

    # ── WAS-SCEPTER + ANKH slung diagonally in the near wing (over the body,
    #    inside the silhouette). A gold forked-base staff with a stylised animal
    #    head at the top; a small gold ankh hangs at the lower end. Kept above the
    #    feet line so nothing dangles past the hitbox.
    wtop = (HX - 4, HY + 4)
    wbot = (HX - 18, HY + 22)
    pygame.draw.line(surf, _SUN_GOLD_D, wtop, wbot, 4)
    pygame.draw.line(surf, _SUN_GOLD, wtop, wbot, 2)
    pygame.draw.line(surf, _RA_GLOW, (wtop[0] - 1, wtop[1] + 1),
                     ((wtop[0] + wbot[0]) // 2 - 1, (wtop[1] + wbot[1]) // 2 + 1), 1)
    # Forked base of the was (the two prongs).
    _poly(surf, _SUN_GOLD, [(wbot[0] - 3, wbot[1] + 3), (wbot[0] + 1, wbot[1]),
                            (wbot[0] + 3, wbot[1] + 4)])
    pygame.draw.line(surf, _SUN_GOLD_D, (wbot[0] - 3, wbot[1] + 3),
                     (wbot[0] - 4, wbot[1] + 6), 2)
    # Stylised seth-head crook at the top.
    pygame.draw.line(surf, _SUN_GOLD, wtop, (wtop[0] + 5, wtop[1] - 3), 3)
    pygame.draw.circle(surf, _RA_GLOW, (wtop[0] + 5, wtop[1] - 3), 1)
    # Small ankh slung at the lower wing.
    akx, aky = HX - 20, HY + 16
    pygame.draw.circle(surf, _SUN_GOLD, (akx, aky - 2), 3, 2)
    pygame.draw.line(surf, _SUN_GOLD, (akx, aky + 1), (akx, aky + 7), 2)
    pygame.draw.line(surf, _SUN_GOLD, (akx - 3, aky + 3), (akx + 3, aky + 3), 2)
    pygame.draw.circle(surf, _RA_GLOW, (akx - 1, aky - 3), 1)

    # ── GOLD TALON-ANKLETS at the feet line — a banded gold cuff on each foot
    #    with a tiny falcon-talon hint. Kept at the feet (~y65), never below.
    for fx, fy in ((28, 65), (34, 65)):
        pygame.draw.line(surf, _SUN_GOLD_D, (fx - 3, fy), (fx + 3, fy), 4)
        pygame.draw.line(surf, _SUN_GOLD, (fx - 3, fy - 1), (fx + 3, fy - 1), 2)
        pygame.draw.line(surf, _RA_GLOW, (fx - 2, fy - 1), (fx + 1, fy - 1), 1)
        # Three short talon ticks just below the cuff (at the feet, not past).
        for tdx in (-2, 0, 2):
            pygame.draw.line(surf, _SUN_GOLD_D, (fx + tdx, fy + 1),
                             (fx + tdx, fy + 3), 1)

    # ── EYE-OF-RA liner — a sharp gold-and-black falcon liner sweeping back from
    #    the near eye, with the wedjat tear-drop hook below. The single graphic
    #    note that turns the face from "gold bird" into "the sun-god".
    ex, ey = HX + 2, HY - 1
    # Upper lid line sweeping back past the eye.
    pygame.draw.line(surf, _RA_BLACK, (ex - 5, ey - 1), (ex + 11, ey - 3), 3)
    pygame.draw.line(surf, _SUN_GOLD, (ex - 5, ey - 2), (ex + 11, ey - 4), 1)
    # Backswept liner flick.
    pygame.draw.line(surf, _RA_BLACK, (ex + 9, ey - 3), (ex + 14, ey - 6), 2)
    pygame.draw.line(surf, _SUN_GOLD, (ex + 10, ey - 4), (ex + 14, ey - 6), 1)
    # The eye itself — gold-rimmed with a dark pupil + a bright catchlight.
    pygame.draw.ellipse(surf, _SUN_GOLD, (ex - 4, ey - 1, 9, 6))
    pygame.draw.circle(surf, _RA_BLACK, (ex, ey + 2), 2)
    pygame.draw.circle(surf, _RA_GLOW, (ex - 1, ey + 1), 1)
    # Wedjat tear-drop hook curling down from the eye.
    pygame.draw.line(surf, _RA_BLACK, (ex - 2, ey + 4), (ex - 1, ey + 8), 2)
    pygame.draw.line(surf, _RA_BLACK, (ex - 1, ey + 8), (ex + 2, ey + 8), 1)

    # ── SOLAR DISK (the hero) crowning the head, above CROWN_Y. Soft cream bloom
    #    first (so the disk sits in a halo), then a coiled gold uraeus cobra
    #    ringing the lower disk, then the disk itself with a hot inner core and a
    #    bright top glint so it reads as a tiny sun — the brightest sprite on
    #    screen at 40px, on day AND night.
    dcx, dcy = HX, CROWN_Y - 8         # disk centre, lifted clear of the crown
    dr = 11
    _disk_bloom(surf, dcx, dcy, dr)

    # Coiled gold uraeus cobra wrapping the base of the disk — a low arc of coil
    # with a reared hood + head at the front, so it reads as a cobra ringing the
    # sun rather than a plain ring.
    pygame.draw.arc(surf, _SUN_GOLD_D,
                    (dcx - dr - 3, dcy - 2, (dr + 3) * 2, dr * 2 + 6),
                    math.radians(200), math.radians(340), 4)
    pygame.draw.arc(surf, _SUN_GOLD,
                    (dcx - dr - 3, dcy - 2, (dr + 3) * 2, dr * 2 + 6),
                    math.radians(200), math.radians(340), 2)
    # Reared cobra head + flared hood at the front of the coil.
    hx0, hy0 = dcx + dr - 2, dcy + dr - 1
    cobra = [(hx0, hy0), (hx0 + 5, hy0 - 2), (hx0 + 4, hy0 + 3)]
    _poly(surf, _SUN_GOLD, cobra)
    pygame.draw.polygon(surf, _SUN_GOLD_D, cobra, 1)
    pygame.draw.circle(surf, _FALCON_RED, (hx0 + 4, hy0), 1)

    # The disk: amber rim → gold body → hot core → cream top glint, so it has the
    # solar value ramp that makes it glow rather than read flat.
    pygame.draw.circle(surf, _SOLAR_AMB, (dcx, dcy), dr)
    pygame.draw.circle(surf, _SUN_GOLD, (dcx, dcy), dr - 1)
    pygame.draw.circle(surf, _DISK_HOT, (dcx, dcy), dr - 4)
    pygame.draw.circle(surf, _RA_GLOW, (dcx - 2, dcy - 3), 3)
    pygame.draw.circle(surf, (255, 255, 255), (dcx - 3, dcy - 4), 1)
    # A faint amber rim-line keeps the disk edge crisp against a bright day sky.
    pygame.draw.circle(surf, _SOLAR_AMB_D, (dcx, dcy), dr, 1)


build = store_skins._make_skin(_paint, base_fn=_ra_base)
