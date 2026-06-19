"""Round-1 candidate store skins for Pip the macaw.

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
    recoloured body (e.g. metallic robot) instead of the scarlet macaw."""
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


# ─────────────────────────────────────────────────────────────────────────────
# 1 · PIRATE — tricorn hat, eyepatch over the far lens, gold hoop earring.
# ─────────────────────────────────────────────────────────────────────────────
_PIR_FELT   = (38, 30, 28)
_PIR_FELT_D = (20, 16, 16)
_PIR_FELT_H = (70, 58, 54)
_PIR_TRIM   = (210, 180, 90)
_PIR_TRIM_H = (255, 235, 150)
_PIR_GOLD   = (255, 205, 70)


def _paint_pirate(surf, _a):
    # Gold hoop earring under the head, behind the hat layer.
    pygame.draw.circle(surf, _PIR_GOLD, (HX - 8, HY + 9), 3, 1)
    pygame.draw.circle(surf, _PIR_TRIM_H, (HX - 9, HY + 8), 1)

    # Eyepatch over the FAR (left) lens + a strap across the crown.
    pygame.draw.line(surf, _PIR_FELT_D, (HX - 11, CROWN_Y + 2),
                     (HX + 7, HY - 2), 2)
    pygame.draw.ellipse(surf, _PIR_FELT, (HX - 8, HY - 5, 9, 9))
    pygame.draw.ellipse(surf, _PIR_FELT_H, (HX - 7, HY - 4, 4, 3))

    # Tricorn: three upturned felt corners around a low crown.
    cy = CROWN_Y - 1
    brim = [(HX - 16, cy + 4), (HX - 5, cy - 6), (HX + 4, cy - 7),
            (HX + 15, cy + 3), (HX + 6, cy + 8), (HX - 6, cy + 8)]
    pygame.draw.polygon(surf, _PIR_FELT_D, brim)
    inner = [(HX - 13, cy + 3), (HX - 4, cy - 4), (HX + 3, cy - 5),
             (HX + 12, cy + 2), (HX + 5, cy + 6), (HX - 5, cy + 6)]
    pygame.draw.polygon(surf, _PIR_FELT, inner)
    pygame.draw.polygon(surf, _PIR_FELT_H, [(HX - 4, cy - 4), (HX + 3, cy - 5),
                                            (HX + 2, cy - 1), (HX - 3, cy - 1)])
    # Gold rope trim tracing the brim edge.
    pygame.draw.lines(surf, _PIR_TRIM, False,
                      [(HX - 14, cy + 3), (HX - 4, cy - 4), (HX + 3, cy - 5),
                       (HX + 13, cy + 2)], 2)
    pygame.draw.lines(surf, _PIR_TRIM_H, False,
                      [(HX - 13, cy + 2), (HX - 4, cy - 5), (HX + 3, cy - 6)], 1)
    # Skull cockade — tiny pale skull on the front-left corner.
    pygame.draw.circle(surf, (235, 230, 220), (HX - 9, cy + 1), 3)
    pygame.draw.circle(surf, (40, 30, 30), (HX - 10, cy + 1), 1)
    pygame.draw.circle(surf, (40, 30, 30), (HX - 8, cy + 1), 1)


get_pirate_parrot = _make_skin(_paint_pirate)


# ─────────────────────────────────────────────────────────────────────────────
# 2 · NINJA — black wrap hood/mask leaving an eye-slit, headband tails
#             streaming behind the head.
# ─────────────────────────────────────────────────────────────────────────────
_NIN_CLOTH   = (32, 36, 48)
_NIN_CLOTH_D = (16, 18, 28)
_NIN_CLOTH_H = (64, 70, 90)
_NIN_BAND    = (200, 50, 55)
_NIN_BAND_D  = (130, 28, 34)
_NIN_BAND_H  = (255, 120, 110)
_NIN_EYE     = (240, 248, 255)


def _paint_ninja(surf, _a):
    # Hood: a cowl wrapping the whole head, leaving a horizontal eye-slit.
    pygame.draw.ellipse(surf, _NIN_CLOTH_D, (HX - 13, CROWN_Y - 4, 27, 26))
    pygame.draw.ellipse(surf, _NIN_CLOTH, (HX - 12, CROWN_Y - 3, 25, 24))
    # Crown sheen.
    pygame.draw.ellipse(surf, _NIN_CLOTH_H, (HX - 6, CROWN_Y - 1, 9, 4))
    # Wrap fold across the lower face / under the beak base.
    pygame.draw.polygon(surf, _NIN_CLOTH_D,
                        [(HX - 11, HY + 4), (HX + 12, HY + 2),
                         (HX + 11, HY + 9), (HX - 10, HY + 10)])

    # Eye-slit band (dark) with two glinting eyes.
    pygame.draw.rect(surf, (8, 9, 14), (HX - 6, HY - 3, 19, 7), border_radius=3)
    pygame.draw.circle(surf, _NIN_EYE, (HX - 1, HY + 1), 2)
    pygame.draw.circle(surf, _NIN_EYE, (HX + 8, HY), 2)
    pygame.draw.circle(surf, (90, 130, 200), (HX - 1, HY + 1), 1)
    pygame.draw.circle(surf, (90, 130, 200), (HX + 8, HY), 1)

    # Crimson headband across the forehead.
    pygame.draw.line(surf, _NIN_BAND_D, (HX - 12, CROWN_Y + 5),
                     (HX + 13, CROWN_Y + 3), 4)
    pygame.draw.line(surf, _NIN_BAND, (HX - 12, CROWN_Y + 4),
                     (HX + 13, CROWN_Y + 2), 3)
    pygame.draw.line(surf, _NIN_BAND_H, (HX - 10, CROWN_Y + 3),
                     (HX + 6, CROWN_Y + 2), 1)
    # Streaming knot tails flowing back off the far side of the head.
    for dx, dy, dx2, dy2 in [(-12, 4, -22, 1), (-12, 7, -21, 11)]:
        pygame.draw.line(surf, _NIN_BAND_D, (HX + dx, CROWN_Y + dy),
                         (HX + dx2, CROWN_Y + dy2), 4)
        pygame.draw.line(surf, _NIN_BAND, (HX + dx, CROWN_Y + dy),
                         (HX + dx2, CROWN_Y + dy2), 2)


get_ninja_parrot = _make_skin(_paint_ninja)


# ─────────────────────────────────────────────────────────────────────────────
# 3 · WIZARD — tall midnight-blue starred cone hat + flowing white beard.
# ─────────────────────────────────────────────────────────────────────────────
_WIZ_HAT   = (52, 50, 120)
_WIZ_HAT_D = (30, 28, 78)
_WIZ_HAT_H = (96, 94, 180)
_WIZ_STAR  = (255, 224, 110)
_WIZ_BEARD = (236, 240, 248)
_WIZ_BEARD_D = (180, 190, 205)


def _paint_wizard(surf, _a):
    # Beard: a soft cloud of white hanging under the beak, drawn first so the
    # head/beak overlap it. Stacked ellipses taper to a point.
    pygame.draw.ellipse(surf, _WIZ_BEARD_D, (HX - 6, HY + 4, 22, 16))
    pygame.draw.ellipse(surf, _WIZ_BEARD, (HX - 5, HY + 3, 20, 14))
    pygame.draw.polygon(surf, _WIZ_BEARD,
                        [(HX - 3, HY + 12), (HX + 11, HY + 12), (HX + 5, HY + 24)])
    pygame.draw.polygon(surf, _WIZ_BEARD_D,
                        [(HX + 3, HY + 16), (HX + 9, HY + 16), (HX + 6, HY + 23)])

    # Cone hat — tall, leaning slightly back, with a curled droopy tip.
    base_y = CROWN_Y + 2
    tip = (HX - 9, base_y - 30)
    bend = (HX - 5, base_y - 22)
    pygame.draw.polygon(surf, _WIZ_HAT_D,
                        [(HX - 13, base_y + 1), (HX + 12, base_y + 1), bend])
    pygame.draw.polygon(surf, _WIZ_HAT,
                        [(HX - 12, base_y), (HX + 11, base_y), bend])
    # Curled tip flopping forward off the bend.
    pygame.draw.line(surf, _WIZ_HAT_D, bend, tip, 6)
    pygame.draw.line(surf, _WIZ_HAT, bend, tip, 4)
    pygame.draw.circle(surf, _WIZ_STAR, tip, 3)
    pygame.draw.circle(surf, (255, 245, 200), (tip[0] - 1, tip[1] - 1), 1)
    # Lit left edge of the cone.
    pygame.draw.line(surf, _WIZ_HAT_H, (HX - 11, base_y - 1), bend, 1)
    # Up-turned brim.
    pygame.draw.ellipse(surf, _WIZ_HAT_D, (HX - 15, base_y - 2, 30, 8))
    pygame.draw.ellipse(surf, _WIZ_HAT, (HX - 14, base_y - 2, 28, 5))

    # Stars + moons scattered up the cone.
    _spark(surf, HX + 2, base_y - 8, 3, _WIZ_STAR)
    _spark(surf, HX - 4, base_y - 16, 2, _WIZ_STAR)
    _spark(surf, HX + 4, base_y - 20, 2, (255, 255, 255))


get_wizard_parrot = _make_skin(_paint_wizard)


# ─────────────────────────────────────────────────────────────────────────────
# 4 · ASTRONAUT — clear bubble helmet, gold reflective visor, side antenna,
#                 white EVA collar ring.
# ─────────────────────────────────────────────────────────────────────────────
_AST_RING   = (236, 240, 246)
_AST_RING_D = (170, 178, 190)
_AST_GLASS  = (150, 205, 235)
_AST_VISOR  = (255, 200, 70)
_AST_VISOR_D = (200, 140, 30)
_AST_VISOR_H = (255, 240, 170)


def _paint_astronaut(surf, _a):
    cx, cy = HX + 1, HY - 1
    r = 15
    # White EVA collar ring around the neck, behind the dome.
    pygame.draw.ellipse(surf, _AST_RING_D, (cx - 12, cy + 7, 26, 10))
    pygame.draw.ellipse(surf, _AST_RING, (cx - 11, cy + 7, 24, 7))

    # Glass dome — translucent blue sphere over the whole head.
    glass = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(glass, (*_AST_GLASS, 70), (r + 2, r + 2), r)
    glass.set_alpha(255)
    surf.blit(glass, (cx - r - 2, cy - r - 2))

    # Gold reflective visor — a curved band across the lower-front of the dome.
    visor = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(visor, _AST_VISOR, (4, r - 2, r * 2 - 4, r + 2))
    clip = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(clip, (255, 255, 255, 255), (r + 2, r + 2), r - 1)
    visor.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(visor, (cx - r - 2, cy - r - 2))
    pygame.draw.line(surf, _AST_VISOR_H, (cx - 9, cy + 3), (cx + 6, cy + 1), 1)

    # Crisp glass rim + bright specular highlight (top-left).
    pygame.draw.circle(surf, (235, 248, 255), (cx, cy), r, 1)
    pygame.draw.circle(surf, (255, 255, 255), (cx - 6, cy - 7), 3)
    pygame.draw.circle(surf, (255, 255, 255), (cx - 3, cy - 9), 1)

    # Side antenna with a glowing red tip.
    pygame.draw.line(surf, _AST_RING_D, (cx + 12, cy - 9), (cx + 16, cy - 15), 2)
    pygame.draw.circle(surf, (255, 70, 60), (cx + 16, cy - 15), 2)
    pygame.draw.circle(surf, (255, 180, 170), (cx + 15, cy - 16), 1)


get_astronaut_parrot = _make_skin(_paint_astronaut)


# ─────────────────────────────────────────────────────────────────────────────
# 5 · PHARAOH — gold-and-blue striped nemes headdress + rearing uraeus cobra.
# ─────────────────────────────────────────────────────────────────────────────
_PH_GOLD   = (245, 200, 70)
_PH_GOLD_D = (190, 145, 35)
_PH_GOLD_H = (255, 240, 160)
_PH_BLUE   = (40, 95, 175)
_PH_BLUE_D = (24, 60, 120)


def _paint_pharaoh(surf, _a):
    cy = CROWN_Y
    # Side lappets — the striped cloth falling down beside the head/neck.
    lappet = [(HX - 13, cy + 2), (HX - 6, cy + 2), (HX - 5, HY + 16),
              (HX - 12, HY + 16)]
    pygame.draw.polygon(surf, _PH_GOLD, lappet)
    for i in range(4):
        x = HX - 12 + i * 2
        col = _PH_BLUE if i % 2 == 0 else _PH_GOLD_D
        pygame.draw.line(surf, col, (x, cy + 3), (x + 1, HY + 15), 1)
    pygame.draw.polygon(surf, _PH_GOLD_D, lappet, 1)

    # Domed headcloth cap over the crown.
    pygame.draw.ellipse(surf, _PH_GOLD_D, (HX - 13, cy - 5, 27, 18))
    pygame.draw.ellipse(surf, _PH_GOLD, (HX - 12, cy - 5, 25, 15))
    # Alternating gold/blue stripes radiating over the cap.
    for i in range(-5, 6):
        x = HX + i * 2
        col = _PH_BLUE if i % 2 == 0 else _PH_GOLD_D
        pygame.draw.line(surf, col, (x, cy - 4), (x, cy + 6), 1)
    # Front headband.
    pygame.draw.line(surf, _PH_BLUE_D, (HX - 12, cy + 5), (HX + 13, cy + 4), 4)
    pygame.draw.line(surf, _PH_BLUE, (HX - 12, cy + 4), (HX + 13, cy + 3), 2)
    pygame.draw.ellipse(surf, _PH_GOLD_H, (HX - 5, cy - 4, 8, 3))

    # Uraeus cobra rearing from the brow.
    base = (HX, cy)
    pygame.draw.line(surf, _PH_GOLD_D, base, (HX - 1, cy - 7), 3)
    pygame.draw.line(surf, _PH_GOLD, base, (HX - 1, cy - 7), 2)
    # Flared hood + head.
    pygame.draw.polygon(surf, _PH_GOLD,
                        [(HX - 4, cy - 7), (HX + 2, cy - 7), (HX, cy - 11)])
    pygame.draw.circle(surf, _PH_GOLD_H, (HX - 1, cy - 10), 2)
    pygame.draw.circle(surf, (200, 40, 40), (HX - 1, cy - 10), 1)


get_pharaoh_parrot = _make_skin(_paint_pharaoh)


# ─────────────────────────────────────────────────────────────────────────────
# 6 · VIKING — horned iron helmet with a nose-guard + braided golden beard.
# ─────────────────────────────────────────────────────────────────────────────
_VK_IRON   = (120, 128, 140)
_VK_IRON_D = (70, 76, 88)
_VK_IRON_H = (190, 198, 210)
_VK_HORN   = (236, 226, 200)
_VK_HORN_D = (180, 168, 138)
_VK_BEARD  = (210, 160, 70)
_VK_BEARD_D = (150, 108, 40)


def _paint_viking(surf, _a):
    cy = CROWN_Y
    # Braided beard hanging under the beak, two plaited tails.
    pygame.draw.ellipse(surf, _VK_BEARD_D, (HX - 4, HY + 5, 18, 13))
    pygame.draw.ellipse(surf, _VK_BEARD, (HX - 3, HY + 4, 16, 11))
    for bx in (HX + 1, HX + 8):
        for j in range(3):
            yy = HY + 12 + j * 3
            pygame.draw.circle(surf, _VK_BEARD, (bx, yy), 2)
            pygame.draw.circle(surf, _VK_BEARD_D, (bx, yy), 2, 1)
    pygame.draw.circle(surf, (210, 180, 90), (HX + 1, HY + 21), 2)   # beard bead
    pygame.draw.circle(surf, (210, 180, 90), (HX + 8, HY + 21), 2)

    # Two curved horns sweeping up and outward.
    for sgn, hx0 in ((-1, HX - 9), (1, HX + 9)):
        tip = (hx0 + sgn * 6, cy - 16)
        mid = (hx0 + sgn * 6, cy - 6)
        pygame.draw.polygon(surf, _VK_HORN_D,
                            [(hx0 - 3, cy + 1), (hx0 + 3, cy + 1), mid, tip])
        pygame.draw.polygon(surf, _VK_HORN,
                            [(hx0 - 2, cy), (hx0 + 2, cy),
                             (mid[0], mid[1] + 1), (tip[0], tip[1] + 1)])
        # Growth-ring grooves.
        pygame.draw.line(surf, _VK_HORN_D, (hx0 - 1, cy - 3),
                         (hx0 + 2, cy - 3), 1)
        pygame.draw.line(surf, _VK_HORN_D, (mid[0] - 1, mid[1] - 3),
                         (mid[0] + 2, mid[1] - 3), 1)

    # Iron dome cap.
    pygame.draw.ellipse(surf, _VK_IRON_D, (HX - 12, cy - 6, 25, 18))
    pygame.draw.ellipse(surf, _VK_IRON, (HX - 11, cy - 6, 23, 15))
    pygame.draw.ellipse(surf, _VK_IRON_H, (HX - 6, cy - 5, 8, 4))
    # Riveted brow band.
    pygame.draw.line(surf, _VK_IRON_D, (HX - 11, cy + 5), (HX + 12, cy + 4), 4)
    pygame.draw.line(surf, _VK_IRON_H, (HX - 11, cy + 4), (HX + 12, cy + 3), 1)
    for rx in (HX - 8, HX - 1, HX + 6):
        pygame.draw.circle(surf, _VK_IRON_H, (rx, cy + 5), 1)
    # Nose-guard down the brow between the lenses.
    pygame.draw.rect(surf, _VK_IRON_D, (HX + 1, cy + 4, 3, 11))
    pygame.draw.rect(surf, _VK_IRON, (HX + 1, cy + 4, 2, 10))


get_viking_parrot = _make_skin(_paint_viking)


# ─────────────────────────────────────────────────────────────────────────────
# 7 · COWBOY — tan stetson with a curled brim + red kerchief bandana.
# ─────────────────────────────────────────────────────────────────────────────
_CB_TAN    = (196, 150, 92)
_CB_TAN_D  = (140, 100, 56)
_CB_TAN_H  = (232, 196, 140)
_CB_BAND   = (80, 56, 36)
_CB_KER    = (205, 60, 55)
_CB_KER_D  = (150, 36, 36)
_CB_KER_H  = (255, 120, 105)


def _paint_cowboy(surf, _a):
    cy = CROWN_Y
    # Bandana knotted around the neck under the beak.
    ker = [(HX - 11, HY + 6), (HX + 12, HY + 4), (HX + 4, HY + 16)]
    pygame.draw.polygon(surf, _CB_KER_D, ker)
    pygame.draw.polygon(surf, _CB_KER,
                        [(HX - 10, HY + 6), (HX + 11, HY + 5), (HX + 4, HY + 14)])
    pygame.draw.line(surf, _CB_KER_H, (HX - 8, HY + 7), (HX + 8, HY + 6), 1)
    for px, py in ((HX - 5, HY + 9), (HX + 2, HY + 8), (HX + 6, HY + 10)):
        pygame.draw.circle(surf, (255, 255, 255), (px, py), 1)
    pygame.draw.circle(surf, _CB_KER_D, (HX - 9, HY + 6), 2)   # knot

    # Wide curled-brim stetson.
    pygame.draw.ellipse(surf, _CB_TAN_D, (HX - 19, cy + 1, 38, 9))
    pygame.draw.ellipse(surf, _CB_TAN, (HX - 18, cy, 36, 6))
    # Upturned brim edges.
    pygame.draw.ellipse(surf, _CB_TAN_H, (HX - 18, cy - 1, 8, 4))
    pygame.draw.ellipse(surf, _CB_TAN_H, (HX + 10, cy - 1, 8, 4))
    # Crown with a pinched cattleman crease.
    pygame.draw.ellipse(surf, _CB_TAN_D, (HX - 9, cy - 11, 19, 16))
    pygame.draw.ellipse(surf, _CB_TAN, (HX - 8, cy - 11, 17, 13))
    pygame.draw.line(surf, _CB_TAN_D, (HX, cy - 10), (HX, cy - 2), 2)
    pygame.draw.line(surf, _CB_TAN_H, (HX - 5, cy - 9), (HX - 5, cy - 2), 1)
    # Leather hatband + a small silver buckle.
    pygame.draw.line(surf, _CB_BAND, (HX - 8, cy - 1), (HX + 9, cy - 1), 3)
    pygame.draw.rect(surf, (220, 224, 230), (HX + 4, cy - 3, 3, 3))


get_cowboy_parrot = _make_skin(_paint_cowboy)


# ─────────────────────────────────────────────────────────────────────────────
# 8 · DISCO — rainbow shimmer body (recoloured base) + mirror-ball sparkles
#             and a small star-shaped pair of party shades.
# ─────────────────────────────────────────────────────────────────────────────
# Rainbow palette plugged into the from-scratch parrot builder so the whole
# bird shimmers, not just an overlay. Wing keeps a cool→hot sweep; body warms.
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
    # Diagonal shimmer streaks sweeping across the body for a sheen of light.
    streak = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for i, col in enumerate(_DISCO_SHIMMER):
        x = 14 + i * 5
        pygame.draw.line(streak, (*col, 90), (x, PARROT_DY + 18),
                         (x + 12, PARROT_DY + 40), 2)
    # Clamp the streaks to the body silhouette so light doesn't leak outside.
    mask = pygame.mask.from_surface(surf, 8).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    streak.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(streak, (0, 0))

    # Mirror-ball twinkles around the head + over the body.
    for cx, cy, r in ((HX + 9, HY - 11, 3), (HX - 12, HY - 4, 2),
                      (HX - 16, HY + 12, 2), (HX + 13, HY + 6, 2),
                      (HX - 2, CROWN_Y - 6, 2)):
        _spark(surf, cx, cy, r, (255, 255, 255))
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy), 1)

    # Star-shaped party shades stamped over the existing lenses for flair.
    for lx, ly in ((HX - 4, HY), (HX + 6, HY - 1)):
        _spark(surf, lx, ly, 4, (255, 230, 120))
        pygame.draw.circle(surf, (40, 20, 50), (lx, ly), 2)
        pygame.draw.circle(surf, (255, 255, 255), (lx - 1, ly - 1), 1)


get_disco_parrot = _make_skin(_paint_disco, base_fn=_disco_base)


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
]
