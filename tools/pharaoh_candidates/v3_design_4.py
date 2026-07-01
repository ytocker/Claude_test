"""THE SUN-GILDED — divine gold-flesh pharaoh  (pharaoh v3, candidate 4).

Scratch exploration only — NOT registered in store_skins.BUILDERS.

The single RECOLOR variant in the v3 enrich batch. It keeps the classic
pharaoh's identity core UNCHANGED — the gold+lapis striped nemes headdress with
flaring side lappet + the gold uraeus cobra at the brow (rebuilt verbatim from
``_paint_pharaoh``) — but re-plumages the WHOLE BIRD in warm "eternal gold"
god-flesh so it reads as the SAME pharaoh, now divine. Richness comes from the
gilded skin + cool-collar contrast, not added props.

The danger with an all-gold bird is that warm gold can wash out against a bright
day sky and go to mud. The value structure that holds the shape at 40px is
deliberately COOL + DARK against the warm body: the LAPIS nemes stripes, a cool
LAPIS/TURQUOISE usekh collar across the breast, the amber shadow tones baked
into the body palette, and the outline pass. The winged-sun brow emblem is the
divine hero motif. Footprint law: collar + anklets stay inside the base bird
footprint; only the nemes + winged-sun rise above CROWN_Y.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── Gilded god-flesh palette — warm eternal gold with an AMBER shadow so the
# form still reads as a body (not a flat gold blob) and a bright gold highlight
# for the lit upper surfaces. The beak is gold too — the whole bird is gilded.
# Sheen is warmed so the chest catches a divine sun-glint. No lenses: the
# winged-sun + uraeus own the head, and a bare face keeps the gold reading.
_SG_GOLD     = (244, 196, 48)      # #F4C430 main gilded flesh
_SG_GOLD_H   = (255, 233, 168)     # #FFE9A8 lit gold highlight
_SG_GOLD_D   = (154, 107, 30)      # #9A6B1E amber shadow (the form-holding dark)
_SG_LAPIS    = (27, 58, 140)       # #1B3A8C lapis
_SG_LAPIS_D  = (16, 36, 92)        # lapis shadow / line work
_SG_LAPIS_H  = (74, 110, 198)      # lapis sheen
_SG_TURQ     = (47, 184, 166)      # #2FB8A6 turquoise
_SG_TURQ_H   = (140, 230, 216)     # turquoise glint
_SG_RIM      = (40, 26, 10)        # warm-dark amber-black OUTER contour rim

# Whole-bird gold re-plumage. Every plumage slot is a gold value; the amber
# shadow does the line + underside work so the silhouette keeps internal form
# against a bright sky; beak is gilded; lenses dropped (regalia owns the face).
_SG_BODY = _pal(
    # Lower body runs a notch darker than the head — a deep amber tail ramp with a
    # thicker dark tail_line and a lower-value belly — so the bottom third carries
    # its own value anchor (like the collar anchors the chest) instead of going
    # uniform warm gold and blobbing out on a bright day sky. Stays GOLD throughout.
    tail=[(150, 100, 26), (172, 120, 32), (196, 146, 42), (224, 174, 52)],
    tail_line=(120, 82, 22),
    body_shadow=(140, 96, 24),
    body_main=_SG_GOLD,
    body_chest=(255, 220, 120),
    body_belly=(206, 152, 44),
    sheen=(255, 244, 200, 90),
    wing_main=(232, 182, 52),
    wing_dark=(126, 86, 22),
    wing_tip=(255, 226, 130),
    wing_secondary=None,
    wing_highlight=_SG_GOLD_H,
    head_shadow=(158, 110, 30),
    head_main=_SG_GOLD,
    head_cheek=(255, 222, 128),
    head_crown=(252, 214, 96),
    lens_frame=(180, 130, 40),
    lens_body=(60, 42, 12),
    lens_tint=None,
    lens_glint=None,
    beak_main=(238, 188, 56),
    beak_dark=(150, 104, 28),
    beak_gloss=(255, 232, 150),
    foot=(150, 104, 28),
)


def _sg_rim_outer(src, color):
    """Stamp a 1px warm-dark amber rim hugging the source silhouette's OUTER edge
    (same grow-the-mask trick the mummy uses) so the gilded body keeps an unbroken
    dark contour — especially around the tail + lower wing — against a bright day
    sky where warm gold otherwise washes out and the bottom third goes blobby. It
    only touches the outer ring, so the night read and interior regalia are
    untouched."""
    w, h = src.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    ring = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(ring, (dx, dy))
    out.blit(src, (0, 0))
    return out


def _sg_base(angle_deg):
    # The gilded god-flesh bird, no aviators — the regalia owns the face. The
    # outer amber rim is baked here (like the mummy) so the silhouette holds on
    # the bright day sky before any regalia is painted over the interior.
    body = _build_parrot_with_palette(angle_deg, _SG_BODY, draw_lenses=False)
    return _sg_rim_outer(body, _SG_RIM)


def _paint(surf, _a):
    BCX, BCY = 32, 52              # body centre in composite space
    cy = CROWN_Y

    # ── USEKH COLLAR — the COOL accent that owns the breast. Lapis + turquoise
    # bead rows so it pops against the warm gold body and gives the upper body a
    # dark, cool value anchor at 40px (the single most important shape-holder
    # besides the nemes). Drawn FIRST so the nemes lappet overlaps its top edge,
    # and held well inside the body footprint. Three concentric arcs: an outer
    # gold rim, a fat lapis band, an inner turquoise band, tied off with gold.
    col = pygame.Rect(BCX - 13, BCY - 16, 30, 22)
    pygame.draw.arc(surf, _SG_GOLD_D, col.inflate(2, 2), 3.45, 6.10, 4)
    pygame.draw.arc(surf, _SG_GOLD,   col,               3.50, 6.05, 2)   # gold rim
    pygame.draw.arc(surf, _SG_LAPIS_D, col.inflate(-4, -4), 3.52, 6.02, 5)
    pygame.draw.arc(surf, _SG_LAPIS,   col.inflate(-4, -4), 3.55, 5.98, 3)  # lapis band
    pygame.draw.arc(surf, _SG_LAPIS_H, col.inflate(-5, -6), 3.60, 5.92, 1)
    pygame.draw.arc(surf, _SG_TURQ,   col.inflate(-9, -9), 3.58, 5.95, 3)   # turquoise band
    pygame.draw.arc(surf, _SG_TURQ_H, col.inflate(-10, -10), 3.62, 5.90, 1)
    pygame.draw.arc(surf, _SG_GOLD,   col.inflate(-13, -13), 3.60, 5.92, 2)  # inner gold tie
    # Bead drops hanging off the collar's lower lip — alternating lapis/turquoise
    # dots so the collar reads as strung beadwork, not a flat band, at the bottom.
    for i, bx in enumerate(range(BCX - 9, BCX + 11, 4)):
        bc = _SG_LAPIS if i % 2 == 0 else _SG_TURQ
        pygame.draw.circle(surf, bc, (bx, BCY + 5), 2)
        pygame.draw.circle(surf, _SG_GOLD_H, (bx, BCY + 4), 1)

    # ── GOLD ANKLETS — thin gold bands on the feet line, ON the line never below
    # it, so the bird keeps its true size. A lapis pip on each ties them to the
    # collar's cool notes.
    for fx in (27, 35):
        pygame.draw.line(surf, _SG_GOLD_D, (fx - 3, HY + 23), (fx + 3, HY + 23), 3)
        pygame.draw.line(surf, _SG_GOLD,   (fx - 3, HY + 22), (fx + 3, HY + 22), 1)
        pygame.draw.circle(surf, _SG_LAPIS, (fx, HY + 22), 1)

    # ── NEMES (identity core, rebuilt verbatim from _paint_pharaoh) — the gold+
    # lapis striped headcloth. The lapis stripes are the body's strongest value
    # break against the gilded skin, so this is doing double duty as both the
    # identity tell AND the head-region shape-holder at 40px.
    lappet = [(HX - 13, cy + 2), (HX - 5, cy + 2), (HX - 4, HY + 16),
              (HX - 12, HY + 16)]
    pygame.draw.polygon(surf, _SG_GOLD, lappet)
    for i in range(3):
        x = HX - 12 + i * 3
        c = _SG_LAPIS if i % 2 == 0 else _SG_GOLD_D
        pygame.draw.line(surf, c, (x, cy + 3), (x + 1, HY + 15), 2)
    pygame.draw.polygon(surf, _SG_GOLD_D, lappet, 1)

    # Domed headcloth cap over the crown.
    pygame.draw.ellipse(surf, _SG_GOLD_D, (HX - 13, cy - 5, 27, 18))
    pygame.draw.ellipse(surf, _SG_GOLD, (HX - 12, cy - 5, 25, 15))
    # Wider, fewer alternating stripes radiating over the cap (2px each).
    for i in range(-3, 4):
        x = HX + i * 3
        c = _SG_LAPIS if i % 2 == 0 else _SG_GOLD_D
        pygame.draw.line(surf, c, (x, cy - 4), (x, cy + 6), 2)
    # Front headband.
    pygame.draw.line(surf, _SG_LAPIS_D, (HX - 12, cy + 5), (HX + 13, cy + 4), 4)
    pygame.draw.line(surf, _SG_LAPIS, (HX - 12, cy + 4), (HX + 13, cy + 3), 2)
    pygame.draw.ellipse(surf, _SG_GOLD_H, (HX - 5, cy - 4, 8, 3))

    # ── WINGED-SUN brow emblem — the DIVINE hero motif. A small gold sun disk on
    # the front of the headband with two short out-swept wings, the disk ringed in
    # lapis so it separates from the gold cap behind it (warm-on-warm would
    # vanish). Seated just above the headband, below the uraeus' rear, inside the
    # nemes width so it never balloons the headgear.
    sx, sy = HX, cy + 1
    # Wings reduced to two short dark-lapis TICKS flanking the disk — "a dot with
    # two flanks", not a fanned feather smear that fattens the brow and turns to a
    # blue blob at 40px. One straight stroke per side reads as a flank without
    # competing with the disk.
    for sgn in (-1, 1):
        pygame.draw.line(surf, _SG_LAPIS_D, (sx + sgn * 5, sy - 1),
                         (sx + sgn * 11, sy - 2), 2)
    # The sun disk — bumped a notch (core +1px, lapis ring +1px) so it stays a
    # distinct DOT above the headband and separates from the gold cap behind it.
    pygame.draw.circle(surf, _SG_LAPIS, (sx, sy - 1), 5)
    pygame.draw.circle(surf, _SG_GOLD, (sx, sy - 1), 4)
    pygame.draw.circle(surf, _SG_GOLD_H, (sx - 1, sy - 2), 2)

    # ── URAEUS COBRA (identity core, rebuilt verbatim from _paint_pharaoh) — the
    # rearing gold cobra at the brow, the classic pharaoh tell. Sits forward of
    # the winged-sun disk; the red eye-bead is the only warm accent it carries.
    bx = HX
    pygame.draw.line(surf, _SG_GOLD_D, (bx, cy + 1), (bx - 1, cy - 9), 4)
    pygame.draw.line(surf, _SG_GOLD, (bx, cy + 1), (bx - 1, cy - 9), 2)
    # Flared hood.
    pygame.draw.polygon(surf, _SG_GOLD,
                        [(HX - 5, cy - 8), (HX + 3, cy - 8), (HX - 1, cy - 13)])
    pygame.draw.polygon(surf, _SG_GOLD_H,
                        [(HX - 3, cy - 9), (HX + 1, cy - 9), (HX - 1, cy - 12)])
    pygame.draw.circle(surf, _SG_GOLD_H, (HX - 1, cy - 12), 2)
    pygame.draw.circle(surf, (210, 50, 50), (HX - 1, cy - 12), 1)


build = store_skins._make_skin(_paint, base_fn=_sg_base)
