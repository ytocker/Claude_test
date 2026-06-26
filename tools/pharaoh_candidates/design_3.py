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
from game.store_skins import HX, HY, CROWN_Y, _poly, _compose, PARROT_DY
from game.parrot import _add_outline, _WING_ANGLES
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
_RA_GLOW    = (255, 246, 200)      # #FFF6C8 solar bloom inner cream / hero glint
_RA_BLACK   = (28, 22, 16)         # Eye-of-Ra liner / dark separators
_DISK_HOT   = (255, 232, 150)      # disk inner-hot core

# Tiered bloom hue ramp — a warm halo reads as SUNLIGHT; a neutral cream one
# desaturates over bright day sky into "grey smoke". Outer rings are warm amber,
# mid rings sun-gold, the innermost cream, so the falloff is a colour-temperature
# gradient (warm→hot) as well as a value gradient.
_BLOOM_AMBER = (255, 180, 74)      # #FFB44A outer warm-amber corona
_BLOOM_GOLD  = (255, 210, 74)      # #FFD24A mid sun-gold
_BLOOM_CREAM = (255, 246, 200)     # #FFF6C8 inner cream
_RIM_AMBER   = (255, 138, 30)      # #FF8A1E opaque day rim ("sun's edge")


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
    """Soft solar CORONA, applied AFTER the outline pass so nothing traces a dark
    ring around it (the outline mask reading the soft fringe was what made the
    halo look like grey smoke). A warm colour-temperature falloff — amber corona
    → sun-gold → cream — over a smooth 11-ring alpha ramp reads as sunlight, not
    neutral fog. Sized generously so on night sky the disk is unambiguously the
    brightest sprite; additive blend brightens whatever sky sits behind it."""
    rad_out = int(r * 2.6) + 6      # ~30% bigger corona, sized for the night read
    pad = rad_out + 2
    glow = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    gc = (pad, pad)
    # 11 rings, large+faint+amber first → small+bright+cream last. Hue warms and
    # value climbs together so the gradient is one continuous warm glow.
    n = 11
    for i in range(n):
        t = i / (n - 1)                         # 0 outer → 1 inner
        rad = int(rad_out - t * (rad_out - r + 1))
        if t < 0.45:
            col = _BLOOM_AMBER
        elif t < 0.78:
            col = _BLOOM_GOLD
        else:
            col = _BLOOM_CREAM
        # Gentle quadratic ramp: very soft at the corona edge, near-solid at core.
        a = int(34 + (255 - 34) * (t * t))
        pygame.draw.circle(glow, (*col, a), gc, rad)
    surf.blit(glow, (cx - pad, cy - pad), special_flags=pygame.BLEND_RGBA_ADD)


def _paint(surf, _a):
    # ── WINGED SUN COLLAR (drawn first, under the disk/face). Reduced to TWO
    #    clean bands — a gold outer band and one cool sky-blue inner band — split
    #    by a crisp 1px dark separator, so it survives the 40px downscale as a
    #    legible collar rather than collapsing into a band of mud. The blue is the
    #    SOLE cool accent that holds against all the gold. Held strictly inside the
    #    body width (x ≈ HX-22 .. HX+2) so the silhouette never grows.
    ccx, ccy = HX - 9, HY + 12          # collar centre, on the upper chest
    # Gold outer band, then a 1px dark separator, then the sky-blue inner band.
    pygame.draw.ellipse(surf, _SUN_GOLD, (ccx - 19, ccy - 12, 38, 18))
    pygame.draw.ellipse(surf, _RA_BLACK, (ccx - 15, ccy - 9, 30, 15))
    pygame.draw.ellipse(surf, _SKY_BLUE, (ccx - 14, ccy - 8, 28, 14))
    # Re-open the centre so the two rows read as bands, not a solid bib, and the
    # dark chin-line re-establishes value contrast so the collar reads as a collar.
    pygame.draw.ellipse(surf, _RA_BLACK, (ccx - 9, ccy - 5, 18, 9))
    pygame.draw.ellipse(surf, _SUN_GOLD, (ccx - 8, ccy - 4, 16, 8))
    # One short clean gold wing-sweep off each shoulder (replaces the muddy
    # per-feather poly fan) — a single stylised falcon-wing flick per side.
    for sgn, ax in ((-1, ccx - 17), (1, ccx + 15)):
        _poly(surf, _SUN_GOLD,
              [(ax, ccy - 4), (ax + sgn * 8, ccy + 2), (ax + sgn * 2, ccy + 5)])
        pygame.draw.line(surf, _SUN_GOLD_D, (ax, ccy - 4),
                         (ax + sgn * 8, ccy + 2), 1)

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

    # ── SOLAR DISK (the hero) crowning the head, above CROWN_Y. The soft additive
    #    corona is applied LATER (post-outline, in the getter) so no dark ring bites
    #    it; here we draw the solid disk + a coiled gold uraeus cobra + an OPAQUE
    #    warm-amber RIM ring just outside the disk. That rim gives the sun a defined
    #    warm edge against bright blue day sky even before the soft corona, so the
    #    read is "sun with corona", not "disk with dirty fog".
    dcx, dcy = HX, CROWN_Y - 8         # disk centre, lifted clear of the crown
    dr = 11

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
    # solar value ramp that makes it glow rather than read flat. (KEEP — the win.)
    pygame.draw.circle(surf, _SOLAR_AMB, (dcx, dcy), dr)
    pygame.draw.circle(surf, _SUN_GOLD, (dcx, dcy), dr - 1)
    pygame.draw.circle(surf, _DISK_HOT, (dcx, dcy), dr - 4)
    pygame.draw.circle(surf, _RA_GLOW, (dcx - 2, dcy - 3), 3)
    pygame.draw.circle(surf, (255, 255, 255), (dcx - 3, dcy - 4), 1)
    # A faint amber rim-line keeps the disk edge crisp against a bright day sky.
    pygame.draw.circle(surf, _SOLAR_AMB_D, (dcx, dcy), dr, 1)
    # OPAQUE warm-amber rim ring just OUTSIDE the disk — the sun's defined warm
    # edge against bright blue, so day stays legible before the soft corona lands.
    rim = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(rim, (*_RIM_AMBER, 180), (dcx, dcy), dr + 2, 2)
    surf.blit(rim, (0, 0))


# Disk anchor in COMPOSITE space (matches _paint), so the getter can lay the soft
# corona down AFTER the outline pass without re-deriving geometry.
_DISK_CX = HX
_DISK_CY = (CROWN_Y - 8)
_DISK_R  = 11


def build_frame(wing_angle_deg):
    """Compose body + costume, run the house outline, THEN add the soft solar
    corona on top. Keeping the bloom out of the outline mask is what stops the
    dark ring that made the halo read as grey smoke."""
    comp = _add_outline(_compose(wing_angle_deg, _paint, base_fn=_ra_base))
    # _add_outline pads by 2px, so the disk anchor shifts by that pad.
    _disk_bloom(comp, _DISK_CX + 2, _DISK_CY + 2, _DISK_R)
    return comp


def _ra_getter():
    # RA needs the corona applied post-outline, so it can't use the generic
    # body→paint→outline order in _make_skin; this mirrors the viking getter.
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [build_frame(a) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


build = _ra_getter()
