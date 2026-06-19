"""Round-2 candidate store skins for Pip the macaw.

Preview/exploration only — NOTHING in the game imports this. Each builder
mirrors the production skin contract so a winner is directly liftable into
game/parrot.py later:

  * signature `(frame_idx, tilt_deg) -> pygame.Surface`
  * composes over the 4 base wing frames so the flap animates
  * runs the composite through `parrot._add_outline` for the house silhouette
  * caches flat frames once + a per-(frame, 3°-bucket) rotation cache

Accessories are drawn relative to the same head/body anchors the base
sprite uses (`parrot._build_frame`): head centre ~(47, 21), beak tip ~61,
body centre ~(32, 32). Most builders draw onto a TALLER composite (like
dollar_parrot_hat) so tall headgear isn't clipped before rotation, keeping
the parrot centred so the existing center-blit rotation maths still holds.

ROUND-2 NORTH STAR (art-director): a skin lives or dies at 40px in motion.
Every signature shape is pushed UP and OUTWARD past the crown so it breaks
the bird's outline, given a value floor (no near-black on the navy store
card), made 2px+ minimum, and kept off the dark head where it muddies.
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _build_frame, _add_outline, _aaellipse,
)
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Taller canvas so horned/pointed headgear has headroom above the crown.
# Parrot stays vertically centred (blitted at y=PARROT_DY) so rotation in
# the getters reuses the base center-blit pattern.
COMPOSITE_W = SPRITE_W            # 64
COMPOSITE_H = 100
PARROT_DY   = 20

# Head/beak anchors in COMPOSITE space (base anchors + PARROT_DY on y).
HX = 47                           # head centre x
HY = 21 + PARROT_DY               # head centre y  → 41
CROWN_Y = 11 + PARROT_DY          # top of head crown → 31


# ── generic frame/getters factory ────────────────────────────────────────────

def _compose(wing_angle_deg, paint_fn, *, base_fn=_build_frame):
    """Blit a base parrot frame onto the tall composite, then run paint_fn
    to add the costume. `base_fn(angle)->Surface` lets a skin start from a
    recoloured body (e.g. disco) instead of the scarlet macaw."""
    comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    comp.blit(base_fn(wing_angle_deg), (0, PARROT_DY))
    paint_fn(comp, wing_angle_deg)
    return comp


def _make_skin(paint_fn, *, base_fn=_build_frame):
    """Return a cached `(frame_idx, tilt_deg) -> Surface` getter for a skin
    whose costume is painted by `paint_fn(surf, wing_angle_deg)`. Mirrors the
    lazy-flat-build + per-(frame, angle) rotation-cache shape used across
    parrot.py's getters."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [
                _add_outline(_compose(a, paint_fn, base_fn=base_fn))
                for a in _WING_ANGLES
            ]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


# ── small shared drawing helpers ─────────────────────────────────────────────

def _poly(surf, color, pts):
    pygame.draw.polygon(surf, color, pts)


def _spark(surf, cx, cy, r, color):
    """4-point sparkle (matches the hat module's star idiom)."""
    pygame.draw.polygon(surf, color, [(cx, cy - r), (cx + r // 2, cy),
                                      (cx, cy + r), (cx - r // 2, cy)])
    pygame.draw.polygon(surf, color, [(cx - r, cy), (cx, cy - r // 2),
                                      (cx + r, cy), (cx, cy + r // 2)])


def _star5(surf, cx, cy, r, color, rot=-math.pi / 2):
    """Filled 5-point star — the silhouette-breaking shape the keepers use."""
    pts = []
    for i in range(10):
        rad = r if i % 2 == 0 else r * 0.45
        a = rot + i * math.pi / 5
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    pygame.draw.polygon(surf, color, pts)


# ─────────────────────────────────────────────────────────────────────────────
# 1 · PIRATE — lightened mid-felt tricorn pushed UP off the crown, a big
#     white skull cockade dead-centre-front, a continuous bright gold band,
#     and the eyepatch over the NEAR eye so it reads.
#
# R1 fail: dark tricorn fused with the dark head into a brown lump.
# R2: felt is mid-value blue-grey (separates from the scarlet head), the
#     gold rope is one continuous 2px bright band carrying the read, and a
#     ~4px white skull sits front-and-centre as the hero pop.
# ─────────────────────────────────────────────────────────────────────────────
_PIR_FELT   = (74, 78, 96)        # mid-value slate so it lifts off scarlet
_PIR_FELT_D = (48, 52, 70)
_PIR_FELT_H = (120, 126, 150)
_PIR_TRIM   = (255, 205, 70)
_PIR_TRIM_H = (255, 240, 160)
_PIR_GOLD   = (255, 205, 70)
_PIR_SKULL  = (244, 246, 240)


def _paint_pirate(surf, _a):
    # Gold hoop earring under the head.
    pygame.draw.circle(surf, _PIR_GOLD, (HX - 8, HY + 10), 3, 2)
    pygame.draw.circle(surf, _PIR_TRIM_H, (HX - 9, HY + 9), 1)

    # Eyepatch over the NEAR (right) eye + a strap up over the crown.
    pygame.draw.line(surf, _PIR_FELT_D, (HX + 11, HY - 2),
                     (HX - 6, CROWN_Y), 2)
    pygame.draw.ellipse(surf, _PIR_FELT_D, (HX + 6, HY - 5, 9, 9))
    pygame.draw.ellipse(surf, _PIR_FELT, (HX + 7, HY - 4, 7, 7))

    # Tricorn lifted a row higher so the brim breaks the crown outline.
    cy = CROWN_Y - 3
    brim = [(HX - 17, cy + 5), (HX - 5, cy - 7), (HX + 4, cy - 8),
            (HX + 16, cy + 4), (HX + 6, cy + 9), (HX - 6, cy + 9)]
    pygame.draw.polygon(surf, _PIR_FELT_D, brim)
    inner = [(HX - 14, cy + 4), (HX - 4, cy - 5), (HX + 3, cy - 6),
             (HX + 13, cy + 3), (HX + 5, cy + 7), (HX - 5, cy + 7)]
    pygame.draw.polygon(surf, _PIR_FELT, inner)
    pygame.draw.polygon(surf, _PIR_FELT_H, [(HX - 4, cy - 5), (HX + 3, cy - 6),
                                            (HX + 2, cy - 2), (HX - 3, cy - 2)])
    # One continuous bright gold band tracing the whole brim edge — the read.
    band = [(HX - 15, cy + 4), (HX - 4, cy - 5), (HX + 3, cy - 6),
            (HX + 14, cy + 3)]
    pygame.draw.lines(surf, _PIR_TRIM, False, band, 2)
    pygame.draw.lines(surf, _PIR_TRIM_H, False,
                      [(HX - 13, cy + 3), (HX - 4, cy - 6), (HX + 3, cy - 7)], 1)
    # Big white skull cockade dead-centre-front.
    sx, sy = HX, cy + 1
    pygame.draw.circle(surf, _PIR_SKULL, (sx, sy), 4)
    pygame.draw.polygon(surf, _PIR_SKULL, [(sx - 3, sy + 2), (sx + 3, sy + 2),
                                           (sx + 1, sy + 5), (sx - 1, sy + 5)])
    pygame.draw.circle(surf, (40, 30, 40), (sx - 2, sy - 1), 1)
    pygame.draw.circle(surf, (40, 30, 40), (sx + 2, sy - 1), 1)


get_pirate_parrot = _make_skin(_paint_pirate)


# ─────────────────────────────────────────────────────────────────────────────
# 2 · NINJA — the CRIMSON HEADBAND is the hero: a solid bright band wrapping
#     the full crown, sitting ABOVE a slim dark cowl so it pops. One thick
#     tail only; eye-glints warmed to amber so they don't fight the scarlet.
#
# R1 fail: only the blue eye-slit read, like a random blue blob.
# ─────────────────────────────────────────────────────────────────────────────
_NIN_CLOTH   = (40, 44, 58)
_NIN_CLOTH_D = (24, 27, 38)
_NIN_CLOTH_H = (78, 84, 104)
_NIN_BAND    = (224, 48, 46)
_NIN_BAND_D  = (150, 26, 30)
_NIN_BAND_H  = (255, 120, 96)
_NIN_EYE     = (255, 232, 180)     # warm amber, not cold blue
_NIN_EYE_D   = (210, 150, 70)


def _paint_ninja(surf, _a):
    # Slim dark cowl hugging the head (kept below the band so the band reads).
    pygame.draw.ellipse(surf, _NIN_CLOTH_D, (HX - 12, CROWN_Y - 1, 25, 24))
    pygame.draw.ellipse(surf, _NIN_CLOTH, (HX - 11, CROWN_Y, 23, 22))
    pygame.draw.ellipse(surf, _NIN_CLOTH_H, (HX - 5, CROWN_Y + 1, 8, 3))
    # Wrap fold across the lower face.
    pygame.draw.polygon(surf, _NIN_CLOTH_D,
                        [(HX - 10, HY + 4), (HX + 12, HY + 2),
                         (HX + 11, HY + 9), (HX - 9, HY + 10)])

    # Eye-slit with two warm amber glints (no blue).
    pygame.draw.rect(surf, (12, 13, 18), (HX - 5, HY - 2, 18, 6), border_radius=3)
    pygame.draw.circle(surf, _NIN_EYE, (HX, HY + 1), 2)
    pygame.draw.circle(surf, _NIN_EYE, (HX + 8, HY), 2)
    pygame.draw.circle(surf, _NIN_EYE_D, (HX, HY + 1), 1)
    pygame.draw.circle(surf, _NIN_EYE_D, (HX + 8, HY), 1)

    # HERO: solid crimson headband ABOVE the cowl, breaking the crown outline.
    by = CROWN_Y - 1
    pygame.draw.line(surf, _NIN_BAND_D, (HX - 13, by + 1), (HX + 13, by - 1), 5)
    pygame.draw.line(surf, _NIN_BAND, (HX - 13, by), (HX + 13, by - 2), 4)
    pygame.draw.line(surf, _NIN_BAND_H, (HX - 11, by - 1), (HX + 6, by - 2), 1)
    # One thick streaming tail flicking back off the far side.
    pygame.draw.line(surf, _NIN_BAND_D, (HX - 12, by), (HX - 23, by + 4), 4)
    pygame.draw.line(surf, _NIN_BAND, (HX - 12, by), (HX - 22, by + 3), 3)
    pygame.draw.circle(surf, _NIN_BAND_D, (HX - 12, by), 2)   # knot


get_ninja_parrot = _make_skin(_paint_ninja)


# ─────────────────────────────────────────────────────────────────────────────
# 3 · WIZARD (keeper) — keep the tall starred cone + star-tip beacon, but:
#     beard reduced ~25% + warm under-shadow ties it to the chest so the
#     high-value white stops detaching; cone anchored lower/wider on the
#     crown so a steep dive-tilt can't snap it off the body mass.
# ─────────────────────────────────────────────────────────────────────────────
_WIZ_HAT   = (52, 50, 120)
_WIZ_HAT_D = (30, 28, 78)
_WIZ_HAT_H = (96, 94, 180)
_WIZ_STAR  = (255, 224, 110)
_WIZ_BEARD = (222, 228, 240)
_WIZ_BEARD_D = (168, 178, 196)
_WIZ_BEARD_SH = (150, 60, 60)      # warm under-shadow onto the chest


def _paint_wizard(surf, _a):
    # Warm shadow under the beard knits the white to the red chest.
    pygame.draw.ellipse(surf, _WIZ_BEARD_SH, (HX - 4, HY + 9, 18, 12))
    # Beard: ~25% smaller cloud of off-white hanging under the beak.
    pygame.draw.ellipse(surf, _WIZ_BEARD_D, (HX - 4, HY + 5, 17, 12))
    pygame.draw.ellipse(surf, _WIZ_BEARD, (HX - 3, HY + 4, 15, 10))
    pygame.draw.polygon(surf, _WIZ_BEARD,
                        [(HX - 1, HY + 11), (HX + 10, HY + 11), (HX + 5, HY + 20)])
    pygame.draw.polygon(surf, _WIZ_BEARD_D,
                        [(HX + 3, HY + 14), (HX + 8, HY + 14), (HX + 6, HY + 19)])

    # Cone hat — anchored low & WIDE on the crown so it stays welded to the
    # head mass under steep tilt, leaning slightly back with a curled tip.
    base_y = CROWN_Y + 3
    tip = (HX - 8, base_y - 30)
    bend = (HX - 4, base_y - 22)
    pygame.draw.polygon(surf, _WIZ_HAT_D,
                        [(HX - 14, base_y + 1), (HX + 13, base_y + 1), bend])
    pygame.draw.polygon(surf, _WIZ_HAT,
                        [(HX - 13, base_y), (HX + 12, base_y), bend])
    pygame.draw.line(surf, _WIZ_HAT_D, bend, tip, 6)
    pygame.draw.line(surf, _WIZ_HAT, bend, tip, 4)
    pygame.draw.line(surf, _WIZ_HAT_H, (HX - 12, base_y - 1), bend, 1)
    # Up-turned brim hugging the crown (wide anchor).
    pygame.draw.ellipse(surf, _WIZ_HAT_D, (HX - 16, base_y - 2, 32, 8))
    pygame.draw.ellipse(surf, _WIZ_HAT, (HX - 15, base_y - 2, 30, 5))

    # Star-tip beacon (kept) + scattered stars up the cone.
    _star5(surf, tip[0], tip[1] - 1, 4, _WIZ_STAR)
    pygame.draw.circle(surf, (255, 250, 220), (tip[0] - 1, tip[1] - 2), 1)
    _spark(surf, HX + 2, base_y - 9, 3, _WIZ_STAR)
    _spark(surf, HX - 3, base_y - 17, 2, _WIZ_STAR)
    _spark(surf, HX + 4, base_y - 21, 2, (255, 255, 255))


get_wizard_parrot = _make_skin(_paint_wizard)


# ─────────────────────────────────────────────────────────────────────────────
# 4 · ASTRONAUT — read it as a HARD sphere: opaque crisp bright rim (2px) +
#     one strong specular hot-spot. Visor cooled to blue-steel + a hard dark
#     edge so it never reads as the macaw's gold beak. Antenna committed to a
#     2px bright tip on a 2px stalk.
#
# R1 fail: translucent dome read "out of focus"; gold visor doubled the beak.
# ─────────────────────────────────────────────────────────────────────────────
_AST_RING   = (236, 240, 246)
_AST_RING_D = (170, 178, 190)
_AST_GLASS  = (108, 150, 186)      # opaque cool glass tone
_AST_GLASS_D = (70, 104, 140)
_AST_RIM    = (220, 244, 255)
_AST_VISOR  = (70, 120, 170)       # cool blue-steel, NOT gold
_AST_VISOR_D = (28, 54, 86)
_AST_VISOR_H = (150, 200, 240)


def _paint_astronaut(surf, _a):
    cx, cy = HX + 1, HY - 2
    r = 15
    # White EVA collar ring behind the dome.
    pygame.draw.ellipse(surf, _AST_RING_D, (cx - 12, cy + 8, 26, 10))
    pygame.draw.ellipse(surf, _AST_RING, (cx - 11, cy + 8, 24, 7))

    # OPAQUE glass dome — a hard sphere, not a translucent veil.
    pygame.draw.circle(surf, _AST_GLASS_D, (cx, cy), r)
    pygame.draw.circle(surf, _AST_GLASS, (cx, cy - 1), r - 1)

    # Cool blue-steel visor band across the lower-front, with a hard dark edge.
    visor = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(visor, _AST_VISOR, (4, r - 1, r * 2 - 4, r))
    clip = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(clip, (255, 255, 255, 255), (r + 2, r + 2), r - 2)
    visor.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(visor, (cx - r - 2, cy - r - 2))
    pygame.draw.line(surf, _AST_VISOR_D, (cx - 11, cy + 2), (cx + 9, cy), 2)
    pygame.draw.line(surf, _AST_VISOR_H, (cx - 8, cy + 4), (cx + 5, cy + 3), 1)

    # Crisp opaque bright rim (2px) — reads the sphere at 40px.
    pygame.draw.circle(surf, _AST_RIM, (cx, cy), r, 2)
    # One strong specular hot-spot top-left.
    pygame.draw.circle(surf, (255, 255, 255), (cx - 6, cy - 7), 3)
    pygame.draw.circle(surf, (255, 255, 255), (cx - 4, cy - 9), 1)

    # Antenna: committed 2px stalk + 2px bright tip.
    pygame.draw.line(surf, _AST_RING, (cx + 11, cy - 10), (cx + 16, cy - 17), 2)
    pygame.draw.circle(surf, (255, 90, 80), (cx + 16, cy - 17), 2)
    pygame.draw.circle(surf, (255, 200, 190), (cx + 15, cy - 18), 1)


get_astronaut_parrot = _make_skin(_paint_astronaut)


# ─────────────────────────────────────────────────────────────────────────────
# 5 · PHARAOH (keeper, 2nd-best silhouette) — keep the gold cap; simplify the
#     stripes to 2-3px wider/fewer (kill the 1px noise); enlarge the uraeus
#     cobra so it reads hero-only above the brow.
# ─────────────────────────────────────────────────────────────────────────────
_PH_GOLD   = (245, 200, 70)
_PH_GOLD_D = (190, 145, 35)
_PH_GOLD_H = (255, 240, 160)
_PH_BLUE   = (44, 100, 188)
_PH_BLUE_D = (26, 64, 128)


def _paint_pharaoh(surf, _a):
    cy = CROWN_Y
    # Side lappet — striped cloth falling beside the head, fewer 2px stripes.
    lappet = [(HX - 13, cy + 2), (HX - 5, cy + 2), (HX - 4, HY + 16),
              (HX - 12, HY + 16)]
    pygame.draw.polygon(surf, _PH_GOLD, lappet)
    for i in range(3):
        x = HX - 12 + i * 3
        col = _PH_BLUE if i % 2 == 0 else _PH_GOLD_D
        pygame.draw.line(surf, col, (x, cy + 3), (x + 1, HY + 15), 2)
    pygame.draw.polygon(surf, _PH_GOLD_D, lappet, 1)

    # Domed headcloth cap over the crown.
    pygame.draw.ellipse(surf, _PH_GOLD_D, (HX - 13, cy - 5, 27, 18))
    pygame.draw.ellipse(surf, _PH_GOLD, (HX - 12, cy - 5, 25, 15))
    # Wider, fewer alternating stripes radiating over the cap (2px each).
    for i in range(-3, 4):
        x = HX + i * 3
        col = _PH_BLUE if i % 2 == 0 else _PH_GOLD_D
        pygame.draw.line(surf, col, (x, cy - 4), (x, cy + 6), 2)
    # Front headband.
    pygame.draw.line(surf, _PH_BLUE_D, (HX - 12, cy + 5), (HX + 13, cy + 4), 4)
    pygame.draw.line(surf, _PH_BLUE, (HX - 12, cy + 4), (HX + 13, cy + 3), 2)
    pygame.draw.ellipse(surf, _PH_GOLD_H, (HX - 5, cy - 4, 8, 3))

    # Enlarged uraeus cobra rearing from the brow — the hero accent.
    bx = HX
    pygame.draw.line(surf, _PH_GOLD_D, (bx, cy + 1), (bx - 1, cy - 9), 4)
    pygame.draw.line(surf, _PH_GOLD, (bx, cy + 1), (bx - 1, cy - 9), 2)
    # Flared hood.
    pygame.draw.polygon(surf, _PH_GOLD,
                        [(HX - 5, cy - 8), (HX + 3, cy - 8), (HX - 1, cy - 13)])
    pygame.draw.polygon(surf, _PH_GOLD_H,
                        [(HX - 3, cy - 9), (HX + 1, cy - 9), (HX - 1, cy - 12)])
    pygame.draw.circle(surf, _PH_GOLD_H, (HX - 1, cy - 12), 2)
    pygame.draw.circle(surf, (210, 50, 50), (HX - 1, cy - 12), 1)


get_pharaoh_parrot = _make_skin(_paint_pharaoh)


# ─────────────────────────────────────────────────────────────────────────────
# 6 · VIKING (ship-candidate) — widen horn TIPS 1px so they read at 40px;
#     cool/darken the braided beard so it separates from the scarlet body
#     (let the bright helmet carry the read). Horns anchored to the brow band.
# ─────────────────────────────────────────────────────────────────────────────
_VK_IRON   = (126, 134, 148)
_VK_IRON_D = (74, 80, 92)
_VK_IRON_H = (198, 206, 218)
_VK_HORN   = (240, 230, 206)
_VK_HORN_D = (184, 172, 142)
_VK_BEARD  = (150, 120, 70)        # cooler/darker tan — off the scarlet
_VK_BEARD_D = (104, 80, 44)
_VK_BEAD   = (210, 180, 90)


def _paint_viking(surf, _a):
    cy = CROWN_Y
    # Darker braided beard, kept compact so the helmet dominates.
    pygame.draw.ellipse(surf, _VK_BEARD_D, (HX - 3, HY + 5, 16, 12))
    pygame.draw.ellipse(surf, _VK_BEARD, (HX - 2, HY + 4, 14, 10))
    for bx in (HX + 1, HX + 7):
        for j in range(3):
            yy = HY + 11 + j * 3
            pygame.draw.circle(surf, _VK_BEARD, (bx, yy), 2)
            pygame.draw.circle(surf, _VK_BEARD_D, (bx, yy), 2, 1)
    pygame.draw.circle(surf, _VK_BEAD, (HX + 1, HY + 19), 2)
    pygame.draw.circle(surf, _VK_BEAD, (HX + 7, HY + 19), 2)

    # Two curved horns sweeping up & outward, with WIDER tips, rooted in the
    # brow band so the rotated composite keeps them on the head mass.
    for sgn, hx0 in ((-1, HX - 9), (1, HX + 9)):
        tipx = hx0 + sgn * 6
        tip = (tipx, cy - 16)
        mid = (hx0 + sgn * 5, cy - 6)
        pygame.draw.polygon(surf, _VK_HORN_D,
                            [(hx0 - 4, cy + 2), (hx0 + 4, cy + 2), mid,
                             (tipx + sgn * 2, cy - 16)])
        pygame.draw.polygon(surf, _VK_HORN,
                            [(hx0 - 3, cy + 1), (hx0 + 3, cy + 1),
                             (mid[0], mid[1] + 1),
                             (tipx + sgn * 2, cy - 15)])
        # Bright wide tip cap so the point survives downscale.
        pygame.draw.circle(surf, _VK_HORN, (tipx + sgn, cy - 15), 2)
        pygame.draw.line(surf, _VK_HORN_D, (hx0 - 1, cy - 3),
                         (hx0 + 2, cy - 3), 1)

    # Iron dome cap (bright — carries the read).
    pygame.draw.ellipse(surf, _VK_IRON_D, (HX - 12, cy - 6, 25, 18))
    pygame.draw.ellipse(surf, _VK_IRON, (HX - 11, cy - 6, 23, 15))
    pygame.draw.ellipse(surf, _VK_IRON_H, (HX - 6, cy - 5, 9, 4))
    # Riveted brow band.
    pygame.draw.line(surf, _VK_IRON_D, (HX - 11, cy + 5), (HX + 12, cy + 4), 4)
    pygame.draw.line(surf, _VK_IRON_H, (HX - 11, cy + 4), (HX + 12, cy + 3), 1)
    for rx in (HX - 8, HX - 1, HX + 6):
        pygame.draw.circle(surf, _VK_IRON_H, (rx, cy + 5), 1)
    # Nose-guard.
    pygame.draw.rect(surf, _VK_IRON_D, (HX + 1, cy + 4, 3, 11))
    pygame.draw.rect(surf, _VK_IRON, (HX + 1, cy + 4, 2, 10))


get_viking_parrot = _make_skin(_paint_viking)


# ─────────────────────────────────────────────────────────────────────────────
# 7 · COWBOY (benchmark, ship) — minor only: nudge the kerchief cooler/darker
#     so it separates from the scarlet body.
# ─────────────────────────────────────────────────────────────────────────────
_CB_TAN    = (200, 154, 96)
_CB_TAN_D  = (142, 102, 58)
_CB_TAN_H  = (236, 200, 144)
_CB_BAND   = (80, 56, 36)
_CB_KER    = (170, 60, 80)         # cooler wine-red, off the scarlet chest
_CB_KER_D  = (118, 36, 56)
_CB_KER_H  = (220, 110, 130)


def _paint_cowboy(surf, _a):
    cy = CROWN_Y
    # Bandana knotted under the beak.
    ker = [(HX - 11, HY + 6), (HX + 12, HY + 4), (HX + 4, HY + 16)]
    pygame.draw.polygon(surf, _CB_KER_D, ker)
    pygame.draw.polygon(surf, _CB_KER,
                        [(HX - 10, HY + 6), (HX + 11, HY + 5), (HX + 4, HY + 14)])
    pygame.draw.line(surf, _CB_KER_H, (HX - 8, HY + 7), (HX + 8, HY + 6), 1)
    for px, py in ((HX - 5, HY + 9), (HX + 2, HY + 8), (HX + 6, HY + 10)):
        pygame.draw.circle(surf, (245, 235, 240), (px, py), 1)
    pygame.draw.circle(surf, _CB_KER_D, (HX - 9, HY + 6), 2)   # knot

    # Wide curled-brim stetson.
    pygame.draw.ellipse(surf, _CB_TAN_D, (HX - 19, cy + 1, 38, 9))
    pygame.draw.ellipse(surf, _CB_TAN, (HX - 18, cy, 36, 6))
    pygame.draw.ellipse(surf, _CB_TAN_H, (HX - 18, cy - 1, 8, 4))
    pygame.draw.ellipse(surf, _CB_TAN_H, (HX + 10, cy - 1, 8, 4))
    # Crown with a cattleman crease.
    pygame.draw.ellipse(surf, _CB_TAN_D, (HX - 9, cy - 11, 19, 16))
    pygame.draw.ellipse(surf, _CB_TAN, (HX - 8, cy - 11, 17, 13))
    pygame.draw.line(surf, _CB_TAN_D, (HX, cy - 10), (HX, cy - 2), 2)
    pygame.draw.line(surf, _CB_TAN_H, (HX - 5, cy - 9), (HX - 5, cy - 2), 1)
    # Leather hatband + silver buckle.
    pygame.draw.line(surf, _CB_BAND, (HX - 8, cy - 1), (HX + 9, cy - 1), 3)
    pygame.draw.rect(surf, (224, 228, 234), (HX + 4, cy - 3, 3, 3))


get_cowboy_parrot = _make_skin(_paint_cowboy)


# ─────────────────────────────────────────────────────────────────────────────
# 8 · DISCO (premium, ship) — simplify the star-shaped shades to ONE clean
#     star-lens (drop the per-lens stamping noise); keep wide value contrast
#     for colourblind safety; keep the full-body rainbow recolour + shimmer.
# ─────────────────────────────────────────────────────────────────────────────
P_DISCO = _pal(
    tail=[(255, 60, 90), (255, 150, 40), (255, 230, 60), (120, 230, 110)],
    tail_line=(120, 30, 60),
    body_shadow=(120, 40, 120),
    body_main=(225, 90, 200),
    body_chest=(255, 150, 230),
    body_belly=(255, 210, 245),
    sheen=(255, 255, 255, 170),
    wing_main=(70, 140, 255),
    wing_dark=(40, 60, 170),
    wing_tip=(120, 240, 160),
    wing_secondary=(255, 230, 90),
    wing_highlight=(220, 245, 255),
    head_shadow=(110, 40, 130),
    head_main=(200, 90, 230),
    head_cheek=(255, 160, 235),
    head_crown=(245, 200, 250),
    lens_frame=(255, 230, 120),
    lens_body=(28, 16, 40),
    lens_tint=(180, 120, 255, 140),
    lens_glint=(255, 255, 255),
    beak_main=(255, 205, 70),
    beak_dark=(170, 110, 20),
    beak_gloss=(255, 245, 190),
    foot=(120, 60, 120),
)

_DISCO_SHIMMER = [(255, 80, 120), (255, 200, 60), (120, 240, 140),
                  (90, 180, 255), (200, 110, 255)]


def _disco_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, P_DISCO)


def _paint_disco(surf, _a):
    # Diagonal shimmer streaks clamped to the body silhouette.
    streak = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for i, col in enumerate(_DISCO_SHIMMER):
        x = 14 + i * 5
        pygame.draw.line(streak, (*col, 90), (x, PARROT_DY + 18),
                         (x + 12, PARROT_DY + 40), 2)
    mask = pygame.mask.from_surface(surf, 8).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    streak.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(streak, (0, 0))

    # Mirror-ball twinkles, value-bright for colourblind safety.
    for cx, cy, r in ((HX + 9, HY - 11, 3), (HX - 12, HY - 4, 2),
                      (HX - 16, HY + 12, 2), (HX + 13, HY + 6, 2),
                      (HX - 2, CROWN_Y - 6, 2)):
        _spark(surf, cx, cy, r, (255, 255, 255))
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy), 1)

    # ONE clean gold star-lens over the near eye (replaces the doubled stamping).
    lx, ly = HX + 4, HY - 1
    _star5(surf, lx, ly, 6, (255, 232, 120))
    _star5(surf, lx, ly, 3, (40, 20, 50))
    pygame.draw.circle(surf, (255, 255, 255), (lx - 1, ly - 1), 1)


get_disco_parrot = _make_skin(_paint_disco, base_fn=_disco_base)


# ─────────────────────────────────────────────────────────────────────────────
# 9 · CROWN / KING (Pirate replacement on standby) — a tall bright-gold
#     silhouette-breaker: guaranteed 40px read, never dark-fabric headgear.
#     Five jewelled points rising well above the crown.
# ─────────────────────────────────────────────────────────────────────────────
_CR_GOLD   = (255, 206, 64)
_CR_GOLD_D = (196, 146, 30)
_CR_GOLD_H = (255, 244, 168)
_CR_BAND   = (210, 162, 40)
_CR_JEWEL  = [(230, 60, 70), (70, 150, 230), (90, 210, 120)]


def _paint_crown(surf, _a):
    cy = CROWN_Y - 1
    # Jewelled base band, lifted above the crown so it breaks the outline.
    pygame.draw.rect(surf, _CR_GOLD_D, (HX - 13, cy - 1, 26, 6))
    pygame.draw.rect(surf, _CR_GOLD, (HX - 12, cy - 1, 24, 4))
    pygame.draw.line(surf, _CR_GOLD_H, (HX - 11, cy), (HX + 11, cy), 1)
    # Inset gems along the band.
    for gx, gc in zip((HX - 8, HX, HX + 8), _CR_JEWEL):
        pygame.draw.circle(surf, gc, (gx, cy + 2), 2)
        pygame.draw.circle(surf, (255, 255, 255), (gx - 1, cy + 1), 1)

    # Five tall spikes rising high above the head; each tipped with a bead.
    spikes = [-12, -6, 0, 6, 12]
    top = cy - 12
    for i, sx in enumerate(spikes):
        h = 12 if i % 2 == 0 else 9
        tipy = cy - h
        pygame.draw.polygon(surf, _CR_GOLD_D,
                            [(HX + sx - 3, cy - 1), (HX + sx + 3, cy - 1),
                             (HX + sx, tipy - 1)])
        pygame.draw.polygon(surf, _CR_GOLD,
                            [(HX + sx - 2, cy - 1), (HX + sx + 2, cy - 1),
                             (HX + sx, tipy)])
        pygame.draw.line(surf, _CR_GOLD_H, (HX + sx - 1, cy - 2),
                         (HX + sx, tipy + 1), 1)
        # Bright bead finial.
        pygame.draw.circle(surf, _CR_GOLD_H, (HX + sx, tipy), 2)
        pygame.draw.circle(surf, (255, 255, 255), (HX + sx - 1, tipy - 1), 1)


get_crown_parrot = _make_skin(_paint_crown)


# ─────────────────────────────────────────────────────────────────────────────
# CURRENT-SKIN REDRAWS (approved) — liftable builders that replace the
# weak shipped looks. These start from the base parrot (NOT the buff/death
# sprites the shipped skins recycle).
# ─────────────────────────────────────────────────────────────────────────────

# ── TOP HAT redraw — dapper black-felt topper + bright satin band + monocle.
# R1 fail: shipped skin reuses the Triple-buff gold-$ cylinder (reads as a
# buff prop). R2: black felt with a crisp light top rim so it survives 40px
# on navy, a deep-red satin band as the bright accent, and a near-eye monocle.
_TH_FELT   = (34, 32, 44)
_TH_FELT_D = (18, 16, 26)
_TH_FELT_H = (96, 96, 118)         # crisp light rim so the black survives navy
_TH_BAND   = (200, 44, 56)         # bright satin-red accent
_TH_BAND_H = (255, 110, 110)
_TH_GOLD   = (255, 206, 80)


def _paint_tophat(surf, _a):
    cy = CROWN_Y
    # Brim — wide ellipse with a bright top edge so the silhouette reads.
    pygame.draw.ellipse(surf, _TH_FELT_D, (HX - 17, cy + 1, 34, 8))
    pygame.draw.ellipse(surf, _TH_FELT, (HX - 16, cy, 32, 5))
    pygame.draw.line(surf, _TH_FELT_H, (HX - 13, cy + 1), (HX + 13, cy + 1), 1)

    # Tall cylindrical crown rising well above the head.
    top_y = cy - 17
    pygame.draw.rect(surf, _TH_FELT_D, (HX - 9, top_y, 19, 19))
    pygame.draw.rect(surf, _TH_FELT, (HX - 8, top_y, 16, 18))
    pygame.draw.line(surf, _TH_FELT_H, (HX - 6, top_y + 1), (HX - 6, cy - 2), 2)
    # Crisp light top rim — the hero edge that keeps black off the navy floor.
    pygame.draw.ellipse(surf, _TH_FELT_H, (HX - 9, top_y - 2, 19, 6))
    pygame.draw.ellipse(surf, _TH_FELT, (HX - 8, top_y - 1, 17, 4))

    # Bright satin band wrapping the base of the crown.
    pygame.draw.rect(surf, _TH_BAND, (HX - 9, cy - 3, 19, 4))
    pygame.draw.line(surf, _TH_BAND_H, (HX - 8, cy - 3), (HX + 8, cy - 3), 1)

    # Monocle on the NEAR eye — gold ring + glint + a thin chain.
    mx, my = HX + 6, HY
    pygame.draw.circle(surf, _TH_GOLD, (mx, my), 5, 2)
    pygame.draw.circle(surf, (255, 255, 255), (mx - 2, my - 2), 1)
    pygame.draw.line(surf, _TH_GOLD, (mx + 4, my + 3), (mx + 6, HY + 9), 1)


get_tophat_redraw = _make_skin(_paint_tophat)


# ── SKELETON redraw — warm bone-ivory on deep-navy body, hollow sockets +
# a pinpoint glint. Day-of-the-Dead charm, NOT the X-Ray electrocution sprite.
# Bones are the brightest element and 2px min so they survive downscale.
_SK_BODY   = (38, 40, 64)          # deep-navy "flesh"
_SK_BODY_D = (24, 26, 46)
_SK_BONE   = (245, 240, 220)       # warm ivory — brightest element
_SK_BONE_D = (196, 188, 160)
_SK_SOCK   = (20, 22, 38)


def _skel_wing(angle_deg):
    """Recoloured wing: navy silhouette + bold ivory bone tracing (2px)."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    pts = [(24, 26), (46, 14), (50, 30), (34, 44), (18, 40)]
    pygame.draw.polygon(w, _SK_BODY, pts)
    pygame.draw.polygon(w, _SK_BODY_D, pts, 1)
    pygame.draw.line(w, _SK_BONE, (25, 27), (39, 22), 2)
    pygame.draw.line(w, _SK_BONE, (39, 22), (47, 30), 2)
    pygame.draw.line(w, _SK_BONE_D, (47, 30), (42, 40), 2)
    pygame.draw.circle(w, _SK_BONE, (25, 27), 2)
    pygame.draw.circle(w, _SK_BONE, (39, 22), 2)
    return pygame.transform.rotate(w, angle_deg)


def _build_skeleton_redraw(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    # Tail — navy fan.
    pygame.draw.polygon(surf, _SK_BODY, [(2, 26), (17, 24), (23, 36), (12, 42)])
    pygame.draw.polygon(surf, _SK_BODY_D,
                        [(2, 26), (17, 24), (23, 36), (12, 42)], 1)
    # Body.
    _aaellipse(surf, _SK_BODY_D, (33, 33), 19, 14)
    _aaellipse(surf, _SK_BODY, (32, 32), 18, 13)
    # Wing.
    wing = _skel_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)
    # Head.
    _aaellipse(surf, _SK_BODY_D, (48, 22), 12, 11)
    _aaellipse(surf, _SK_BODY, (47, 21), 11, 10)

    # Ribcage — bold ivory arcs across the chest (2px).
    pygame.draw.line(surf, _SK_BONE, (38, 26), (22, 36), 2)   # spine
    for off_x in (-5, 0, 5):
        pygame.draw.arc(surf, _SK_BONE, (24 + off_x, 24, 13, 16),
                        math.radians(200), math.radians(340), 2)
    # Skull — bright ivory dome with hollow sockets + a pinpoint glint.
    _aaellipse(surf, _SK_BONE, (47, 21), 9, 8)
    _aaellipse(surf, _SK_BONE_D, (47, 25), 6, 3)   # jaw shadow
    pygame.draw.circle(surf, _SK_SOCK, (50, 19), 3)
    pygame.draw.circle(surf, _SK_SOCK, (44, 20), 3)
    pygame.draw.circle(surf, (255, 255, 255), (51, 18), 1)   # pinpoint glint
    # Tiny nose triangle + grin stitches.
    pygame.draw.polygon(surf, _SK_SOCK, [(47, 23), (49, 23), (48, 25)])
    for gx in (44, 47, 50):
        pygame.draw.line(surf, _SK_BONE_D, (gx, 27), (gx, 29), 1)

    # Beak — ivory bone outline over a navy beak.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, _SK_BODY, beak_pts)
    pygame.draw.polygon(surf, _SK_BONE, beak_pts, 2)

    # Leg bones.
    pygame.draw.line(surf, _SK_BONE, (28, 45), (27, 49), 2)
    pygame.draw.line(surf, _SK_BONE, (34, 45), (35, 49), 2)
    return surf


def _make_prebuilt_skin(build_fn):
    """Getter for a skin whose flat frames come from a full build_fn(angle)
    (used by the current-skin redraws that recolour the whole body)."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


get_skeleton_redraw = _make_prebuilt_skin(_build_skeleton_redraw)


# ── ZOMBIE redraw — "undead but happy": healthy-green body, stitched grin,
# one mismatched googly eye, a small wound stitch. NOT the chartreuse KO pose.
_ZB_BODY   = (118, 168, 78)        # friendly zombie green
_ZB_BODY_D = (78, 120, 50)
_ZB_BODY_H = (170, 208, 120)
_ZB_BELLY  = (196, 218, 150)
_ZB_STITCH = (60, 84, 40)
_ZB_WING   = (92, 140, 168)
_ZB_WING_D = (58, 96, 120)


def _zb_wing(angle_deg):
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    pts = [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)]
    pygame.draw.polygon(w, _ZB_WING, pts)
    pygame.draw.polygon(w, _ZB_WING_D, [(24, 24), (32, 42), (18, 36)])
    pygame.draw.line(w, _ZB_WING_D, (26, 25), (42, 18), 2)
    pygame.draw.line(w, (170, 210, 220), (25, 25), (41, 15), 1)
    return pygame.transform.rotate(w, angle_deg)


def _build_zombie_redraw(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    # Tail — green wedges.
    for i, c in enumerate([_ZB_BODY_D, _ZB_BODY, _ZB_BODY_H, _ZB_BELLY]):
        pts = [(2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
               (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2)]
        pygame.draw.polygon(surf, c, pts)
    # Body.
    _aaellipse(surf, _ZB_BODY_D, (34, 35), 19, 14)
    _aaellipse(surf, _ZB_BODY, (32, 32), 19, 14)
    _aaellipse(surf, _ZB_BODY_H, (30, 29), 13, 8)
    _aaellipse(surf, _ZB_BELLY, (28, 38), 12, 6)
    # Belly seam stitch — the jaunty undead detail.
    pygame.draw.line(surf, _ZB_STITCH, (26, 34), (26, 42), 1)
    for sy in range(34, 42, 2):
        pygame.draw.line(surf, _ZB_STITCH, (24, sy), (28, sy), 1)

    # Wing.
    wing = _zb_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Head.
    _aaellipse(surf, _ZB_BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, _ZB_BODY, (47, 21), 12, 11)
    _aaellipse(surf, _ZB_BODY_H, (46, 16), 7, 3)

    # Two mismatched googly eyes (one big, one small) — happy, alive-ish.
    pygame.draw.circle(surf, (245, 245, 235), (50, 19), 4)
    pygame.draw.circle(surf, (20, 20, 26), (51, 20), 2)
    pygame.draw.circle(surf, (245, 245, 235), (44, 21), 3)
    pygame.draw.circle(surf, (20, 20, 26), (43, 22), 1)
    pygame.draw.circle(surf, (255, 255, 255), (51, 18), 1)

    # Beak.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, BIRD_BEAK_FALLBACK, beak_pts)
    pygame.draw.polygon(surf, _ZB_STITCH, beak_pts, 1)
    # Stitched grin under the beak.
    pygame.draw.line(surf, _ZB_STITCH, (52, 30), (59, 29), 1)
    for gx in (53, 55, 57):
        pygame.draw.line(surf, _ZB_STITCH, (gx, 28), (gx, 31), 1)

    # Cheek-scar stitch.
    pygame.draw.line(surf, _ZB_STITCH, (44, 24), (47, 25), 1)
    for sx in (44, 46):
        pygame.draw.line(surf, _ZB_STITCH, (sx, 23), (sx + 1, 26), 1)

    # Feet.
    pygame.draw.line(surf, _ZB_BODY_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, _ZB_BODY_D, (34, 45), (36, 49), 2)
    return surf


# Beak colour for the zombie redraw (warm horn, separate from green body).
BIRD_BEAK_FALLBACK = (232, 176, 70)

get_zombie_redraw = _make_prebuilt_skin(_build_zombie_redraw)


# ─────────────────────────────────────────────────────────────────────────────
# Registry — id, label, getter. Mirrors parrot.SKIN_BUILDERS shape so a
# winner lifts straight into the production dict.
# ─────────────────────────────────────────────────────────────────────────────
CANDIDATES = [
    ("skin_pirate",    "PIRATE",    get_pirate_parrot),
    ("skin_ninja",     "NINJA",     get_ninja_parrot),
    ("skin_wizard",    "WIZARD",    get_wizard_parrot),
    ("skin_astronaut", "ASTRONAUT", get_astronaut_parrot),
    ("skin_pharaoh",   "PHARAOH",   get_pharaoh_parrot),
    ("skin_viking",    "VIKING",    get_viking_parrot),
    ("skin_cowboy",    "COWBOY",    get_cowboy_parrot),
    ("skin_disco",     "DISCO",     get_disco_parrot),
    ("skin_crown",     "CROWN",     get_crown_parrot),
]

# Current-skin redraws (before = shipped getter; after = our redraw).
REDRAWS = [
    ("TOP HAT",  parrot.get_hat_parrot,                       get_tophat_redraw),
    ("SKELETON", parrot.get_skeleton_parrot,                  get_skeleton_redraw),
    ("ZOMBIE",   lambda f, t: parrot.get_dead_parrot(f, t, "B"), get_zombie_redraw),
]
