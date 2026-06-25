"""ASTRONAUT redesign — design_7 TRAILBLAZER (exploration only).

The rugged field-worn sibling to design_1 MOONWALKER: an Apollo A7L lunar-
SURFACE explorer, tool-laden and dust-stained instead of the clean orbital
spacewalker. Same white-suit re-plumage + gold-visor + PLSS idiom, but pushed
toward a planet-surface walker — a single thin ANTENNA whip off the pack is
the unique top tell, the visor runs a warmer/more orange amber so it reads as
a sibling not a clone, and the lower legs/boots carry a DUSTY TAN regolith
stain so the bird looks like it has been walking the ground.

Distinct tells held to survive the 40px read (day + night):
  * ANTENNA whip with a tip-bead curving up off the backpack, breaking the
    crown line at the back corner (wobbles a touch with the flap).
  * DUSTY TAN lower legs + boots — the unique grounding cue MOONWALKER lacks.
  * Warm amber GOLD visor (one clean diagonal glint), oversized round surface
    PLSS pack, a single readable chest harness beat (strap + amber RCU block).

Lessons baked in so they aren't re-flagged: the whole white silhouette is
wrapped in ONE continuous dark (#3A2E22) keyline so it doesn't wash out on the
bright day sky; chest detail is held to one-two beats (no confetti); the gold
visor is a clean convex shape with a single glint, never a second beak.

Scratch builder — NOT registered in store_skins.BUILDERS. Production art is
untouched until a winner is picked.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, PARROT_DY
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.parrot import _aaellipse


# ── palette ──────────────────────────────────────────────────────────────────
_SUIT       = (239, 241, 246)      # #EFF1F6 suit white
_SUIT_SH    = (199, 205, 216)      # suit shadow / seam
_SUIT_SH_D  = (168, 175, 190)      # deeper crease so the white holds shape
_GOLD       = (231, 154, 31)       # #E79A1F warm/orange gold visor (sibling tell)
_GOLD_D     = (170, 104, 18)
_GOLD_H     = (255, 222, 150)
_TAN        = (201, 165, 107)      # #C9A56B lunar-dust regolith stain
_TAN_BOOT   = (211, 176, 117)      # boot mass pushed ~1 value brighter/warmer
                                   # so TAN — not the sole — is the 40px grounding cue
_TAN_D      = (158, 124, 74)       # darker scuff line on the boots
_AMBER      = (242, 193, 78)       # #F2C14E amber RCU display
_DARK       = (58, 46, 34)         # #3A2E22 strap / continuous keyline brown-black
_WHITE      = (255, 255, 255)

# Full white-EVA re-plumage. Every slot is a suit-white value so the body reads
# as a pressurised suit, not bare scarlet; the deepest seam-shadow owns the
# line work and lenses are dropped (the helmet dome owns the face). The beak is
# suit-toned so no warm macaw orange survives to fight the amber visor.
_AST_PAL = _pal(
    tail=[(199, 205, 216), (212, 217, 226), (224, 228, 236), (234, 237, 243)],
    tail_line=_SUIT_SH_D,
    body_shadow=(190, 196, 208),
    body_main=_SUIT,
    body_chest=(251, 252, 255),
    body_belly=(230, 234, 241),
    sheen=(255, 255, 255, 90),
    wing_main=(225, 229, 237),
    wing_dark=_SUIT_SH,
    wing_tip=(247, 249, 252),
    wing_secondary=None,
    wing_highlight=_WHITE,
    head_shadow=(190, 196, 208),
    head_main=_SUIT,
    head_cheek=(249, 250, 254),
    head_crown=(234, 237, 243),
    lens_frame=(210, 215, 224),
    lens_body=(190, 196, 208),
    lens_tint=None,
    lens_glint=None,
    beak_main=(219, 224, 232),
    beak_dark=_SUIT_SH,
    beak_gloss=(249, 250, 254),
    foot=_TAN,                      # feet read dusty-tan even before the boot mass
)


def _white_base(angle_deg):
    # White-suited bird, no aviators — the bubble helmet owns the head.
    return _build_parrot_with_palette(angle_deg, _AST_PAL, draw_lenses=False)


def _plss(surf):
    # OVERSIZED round surface PLSS pack — taller and rounder than MOONWALKER's
    # brick so the sibling reads as the bulkier field unit. Drawn first so the
    # body/helmet sit in front of it; its own dark border is the same #3A2E22
    # keyline weight the whole suit gets, so it stays a distinct mass.
    bx, by, bw, bh = HX - 33, CROWN_Y - 8, 25, 52
    pygame.draw.rect(surf, _DARK, (bx - 2, by - 2, bw + 4, bh + 4), border_radius=11)
    pygame.draw.rect(surf, _SUIT_SH, (bx, by, bw, bh), border_radius=10)
    pygame.draw.rect(surf, _SUIT, (bx + 2, by + 1, bw - 4, bh - 5), border_radius=9)
    # Rounded top dome cap so the pack reads taller/rounder, not boxy.
    _aaellipse(surf, _SUIT, (bx + bw // 2, by + 4), bw / 2 - 1, 6)
    # Two life-support cans split by a soft seam.
    pygame.draw.line(surf, _SUIT_SH_D, (bx + bw // 2, by + 9),
                     (bx + bw // 2, by + bh - 6), 2)
    # A couple of horizontal banding ridges for the field-unit bulk.
    pygame.draw.line(surf, _SUIT_SH, (bx + 3, by + bh - 14),
                     (bx + bw - 3, by + bh - 14), 1)
    pygame.draw.line(surf, _SUIT_SH, (bx + 3, by + bh - 8),
                     (bx + bw - 3, by + bh - 8), 1)
    return bx, by, bw, bh


def _antenna(surf, pack, wing_angle_deg):
    # The unique TOP tell: a single thin ANTENNA whip curving up off the back
    # corner of the pack with a tiny tip-bead, breaking the crown line. It
    # wobbles a touch with the flap so it feels like a real whip antenna, but
    # the base/tip stay well clear of the helmet so it never reads as clutter.
    bx, by, bw, bh = pack
    # Base sits ~2px inboard (toward pack centre) so the whip reads as a clean
    # thin line off the pack, not a lump welded to the shoulder corner.
    base = (bx + bw - 7, by + 1)
    wobble = math.sin(math.radians(wing_angle_deg) * 1.6) * 3.0
    mid = (base[0] + 1 - wobble * 0.4, base[1] - 9)
    tip = (base[0] - 5 + wobble, base[1] - 18)
    pygame.draw.lines(surf, _DARK, False, [base, mid, tip], 2)
    # Tip-bead is light-grey/white, NOT amber, so the only chest-level amber is
    # the RCU and the only big amber is the visor — one warm read per zone.
    pygame.draw.circle(surf, _SUIT_SH, (int(tip[0]), int(tip[1])), 2)
    pygame.draw.circle(surf, _WHITE, (int(tip[0]) - 1, int(tip[1]) - 1), 1)


def _hose_loop(surf, pack):
    # Side hose loop curving from the pack round to the chest — a soft field
    # detail that fills the gap between back unit and torso harness.
    bx, by, bw, bh = pack
    p0 = (bx + bw - 1, by + bh - 18)
    p1 = (bx + bw + 6, by + bh - 8)
    p2 = (HX - 9, HY + 13)
    pygame.draw.lines(surf, _DARK, False, [p0, p1, p2], 3)
    pygame.draw.lines(surf, _SUIT_SH, False, [p0, p1, p2], 1)


def _dusty_legs(surf):
    # The grounding cue MOONWALKER lacks: lower legs + boots shaded DUSTY TAN
    # (regolith staining) with a darker scuff line, forming the literal bottom
    # of the silhouette. One chunky hard-edged surface-boot mass.
    bootx, booty, bootw, booth = 21, 61, 23, 10
    pygame.draw.rect(surf, _TAN_D, (bootx - 1, booty - 1, bootw + 2, booth + 2),
                     border_radius=4)
    pygame.draw.rect(surf, _TAN_BOOT, (bootx, booty, bootw, booth), border_radius=4)
    # Dusty stain creeping up the shins above the boot line.
    _aaellipse(surf, _TAN_BOOT, (bootx + 6, booty - 2), 5, 4)
    _aaellipse(surf, _TAN_BOOT, (bootx + bootw - 6, booty - 2), 5, 4)
    # Split the two boots + a hard scuffed sole keyline thinned to 2px so the
    # bright TAN mass — not the black sole — grounds the silhouette at 40px.
    pygame.draw.line(surf, _TAN_D, (bootx + bootw // 2, booty + 1),
                     (bootx + bootw // 2, booty + booth - 2), 2)
    pygame.draw.rect(surf, _DARK, (bootx, booty + booth - 2, bootw, 2),
                     border_radius=1)
    # One scuff streak so the tan reads as field-worn, not a clean tan boot.
    pygame.draw.line(surf, _TAN_D, (bootx + 3, booty + 4),
                     (bootx + 9, booty + 3), 1)


def _chest_harness(surf):
    # ONE readable chest beat held to a single idea: a dark utility strap +
    # the amber RCU block. The two pouch/tool nubs are CUT — at 40px they were
    # sub-pixel noise stealing the band the gold visor should own, so the strap
    # + RCU now carry the whole chest read.
    # Diagonal strap line.
    pygame.draw.line(surf, _DARK, (HX - 12, HY + 8), (HX + 4, HY + 20), 3)
    pygame.draw.line(surf, _SUIT_SH, (HX - 12, HY + 8), (HX + 4, HY + 20), 1)
    # Amber RCU control/display block riding the strap — the warm chest accent.
    rcu = pygame.Rect(HX - 13, HY + 14, 8, 7)
    pygame.draw.rect(surf, _DARK, rcu.inflate(2, 2), border_radius=2)
    pygame.draw.rect(surf, _AMBER, rcu, border_radius=2)
    pygame.draw.line(surf, _WHITE, (rcu.x + 1, rcu.y + 1),
                     (rcu.right - 2, rcu.y + 1), 1)


def _glove(surf):
    # Thick rounded white surface-glove mitt — kept as a silhouette tell, with
    # a tan dust smudge so the gloves match the field-worn legs.
    pygame.draw.circle(surf, _SUIT_SH, (49, 43), 5)
    pygame.draw.circle(surf, _SUIT, (49, 42), 4)
    pygame.draw.circle(surf, _TAN, (50, 44), 2)        # dusty fingertips
    pygame.draw.circle(surf, _DARK, (45, 44), 1)       # cuff seam dot


def _helmet(surf):
    # Round bubble helmet with the warm-amber GOLD visor DOWN. One clean convex
    # gold shape clipped to the sphere (a crescent, never a blob/second beak)
    # with a single diagonal glint.
    cx, cyh = HX + 1, HY - 1
    r = 15
    # White EVA neck-rim ring behind the dome ties helmet to the suit collar.
    pygame.draw.ellipse(surf, _DARK, (cx - 13, cyh + 8, 28, 11))
    pygame.draw.ellipse(surf, _SUIT, (cx - 12, cyh + 8, 26, 8))

    # Clear dome — a hard bright sphere (opaque so it never reads out of focus).
    pygame.draw.circle(surf, _DARK, (cx, cyh), r + 1)
    pygame.draw.circle(surf, (214, 224, 234), (cx, cyh), r)
    pygame.draw.circle(surf, (236, 242, 248), (cx, cyh - 1), r - 2)

    # Warm-amber GOLD reflective visor filling the lower-front of the dome —
    # clipped to the sphere so it stays a clean convex crescent.
    visor = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(visor, _GOLD_D, (3, r - 3, r * 2 - 2, r + 2))
    pygame.draw.ellipse(visor, _GOLD, (4, r - 2, r * 2 - 4, r))
    clip = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(clip, (255, 255, 255, 255), (r + 2, r + 2), r - 2)
    visor.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(visor, (cx - r - 2, cyh - r - 2))

    # ONE soft diagonal glint sweeping across the warm gold (best element).
    pygame.draw.line(surf, _GOLD_H, (cx - 9, cyh + 7), (cx + 2, cyh - 1), 2)
    pygame.draw.line(surf, _WHITE, (cx - 7, cyh + 6), (cx - 2, cyh + 2), 1)
    # Hard dark visor brow so the gold doesn't bleed into the clear dome.
    pygame.draw.line(surf, _GOLD_D, (cx - 12, cyh + 1), (cx + 11, cyh - 1), 2)

    # Thin white helmet rim ring + a bright specular hot-spot on the dome.
    pygame.draw.circle(surf, _WHITE, (cx, cyh), r, 2)
    pygame.draw.circle(surf, _WHITE, (cx - 7, cyh - 8), 3)
    pygame.draw.circle(surf, _WHITE, (cx - 5, cyh - 10), 1)


def _suit_keyline(surf):
    """Underlay ONE continuous #3A2E22 keyline around the whole painted bird.

    White-on-pale-day-sky dissolves at the soft lower-left wing/tail edge — the
    helmet and pack carry a visible dark contour but the suit does not.
    Dilating a dark silhouette of everything drawn so far and stamping it
    BEHIND the art gives the entire body the same contour weight, so the read
    survives the 40px day wash-out. (The engine's own 1px outline is near-black
    and too thin to hold the white at thumbnail size.)
    """
    mask = pygame.mask.from_surface(surf, threshold=12)
    line = mask.to_surface(setcolor=_DARK, unsetcolor=(0, 0, 0, 0))
    key = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1),
                   (-2, 0), (2, 0), (0, 2)):
        key.blit(line, (dx, dy))
    key.blit(surf, (0, 0))
    surf.blit(key, (0, 0))


def _paint(surf, wing_angle_deg):
    # Back unit first so the body overlaps its front edge.
    pack = _plss(surf)
    _hose_loop(surf, pack)

    # Dusty-tan surface boots — the literal bottom + grounding cue.
    _dusty_legs(surf)

    # Glove mitt tell.
    _glove(surf)

    # Helmet + warm gold visor own the head/central band.
    _helmet(surf)

    # ONE chest harness beat over the suit (drawn after helmet so the strap
    # tucks under the collar rim cleanly).
    _chest_harness(surf)

    # Antenna whip last among the elements so it sits above the pack/crown.
    _antenna(surf, pack, wing_angle_deg)

    # Final pass: ONE continuous dark keyline behind everything.
    _suit_keyline(surf)


build = store_skins._make_skin(_paint, base_fn=_white_base)
