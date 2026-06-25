"""Equippable Store skins for Pip the macaw.

The expanded cosmetic roster — nine new character skins plus dedicated
redraws of three looks that used to recycle power-up / death sprites. Each
builder follows the production skin contract so it plugs straight into
``parrot.get_skin_frame`` via the ``BUILDERS`` registry at the bottom:

  * signature `(frame_idx, tilt_deg) -> pygame.Surface`
  * composes over the 4 base wing frames so the flap animates
  * runs the composite through `parrot._add_outline` for the house silhouette
  * caches flat frames once + a per-(frame, 3°-bucket) rotation cache

Accessories are drawn relative to the same head/body anchors the base
sprite uses (`parrot._build_frame`): head centre ~(47, 21), beak tip ~61,
body centre ~(32, 32). Most builders draw onto a TALLER composite (like
dollar_parrot_hat) so tall headgear isn't clipped before rotation, keeping
the parrot centred so the existing center-blit rotation maths still holds.

Survived a two-round graphics-designer / art-director design loop; the north
star is "a skin lives or dies at 40px in motion" — every signature shape is
pushed up past the crown to break the bird's outline, kept off near-black on
the navy store card, and held to 2px-minimum so it survives downscale.

The redraws here are the COSMETIC versions only; the power-up sprites they
used to share (parrot.get_hat_parrot / get_skeleton_parrot / get_dead_parrot)
are untouched and still drive their buff / strike / death visuals.
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _build_frame, _add_outline, _aaellipse,
)
from game.draw import blit_glow, lerp_color
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
# 2 · NINJA — a black-shadow shinobi. The whole macaw is re-plumaged near-black
#     through the palette system (like the crimson/disco skins) so the costume
#     accents read as crimson lines ON black instead of red-on-red, and the
#     silhouette reads as one dark moving shadow. At 40px the read is, in order
#     of value: a near-black bird, a bright metal eye-slit looking forward, a
#     steel-tipped ninjato slung corner-to-corner (BOTH tips glinting past the
#     silhouette so it breaks the egg shape no other costume has), then the
#     crimson headband + trailing tails and the obi as the only colour. Every
#     object is mass + ONE accent per object so the stack survives downscale.
# ─────────────────────────────────────────────────────────────────────────────
_NIN_BLACK     = (17, 19, 26)      # shadow body
_NIN_CLOTH_H   = (31, 36, 48)      # cloth highlight — separates stacked black
_NIN_SHADOW    = (42, 47, 60)      # wrap shadow / soft edge
_NIN_CRIMSON   = (200, 16, 46)     # crimson accent (one line per object)
_NIN_CRIMSON_D = (138, 12, 34)
_NIN_CRIMSON_H = (236, 70, 92)
_NIN_METAL     = (232, 234, 240)   # eye-slit + steel glint
_NIN_METAL_D   = (150, 156, 170)

# Near-black re-plumage of the whole macaw. Every slot is shadow-black with a
# slightly lifted cloth-highlight on chest/crown so the dark mass doesn't read
# as a flat void on night sky; tail/wing line work uses the deepest tone. Beak
# and foot are blacked so nothing warm survives; lenses are dropped by the base
# call so the eye-slit owns the face.
P_NINJA = _pal(
    tail=[(13, 15, 21), (15, 17, 23), (19, 21, 28), (24, 27, 35)],
    tail_line=(8, 9, 13),
    body_shadow=(11, 12, 17),
    body_main=_NIN_BLACK,
    body_chest=(24, 27, 35),
    body_belly=(19, 21, 28),
    sheen=(120, 130, 150, 40),
    wing_main=(14, 16, 22),
    wing_dark=(8, 9, 13),
    wing_tip=(28, 31, 40),
    wing_secondary=None,
    wing_highlight=_NIN_CLOTH_H,
    head_shadow=(11, 12, 17),
    head_main=_NIN_BLACK,
    head_cheek=(20, 22, 30),
    head_crown=(24, 27, 35),
    lens_frame=(20, 22, 30),
    lens_body=(8, 9, 13),
    lens_tint=None,
    lens_glint=None,
    beak_main=(20, 22, 30),
    beak_dark=(8, 9, 13),
    beak_gloss=(48, 52, 64),
    foot=(18, 20, 26),
)


def _ninja_base(angle_deg):
    # Black bird with no aviators — the face wrap + eye-slit own the head.
    return _build_parrot_with_palette(angle_deg, P_NINJA, draw_lenses=False)


def _paint_ninja(surf, wing_angle_deg):
    # Headband tails flick with the wing beat so the shadow feels alive; the
    # base wing angles run negative-on-downbeat, so a small share reads as the
    # ribbons trailing the dive.
    flick = int(round(wing_angle_deg * 0.12))

    # Ninjato slung corner-to-corner (drawn FIRST, behind the body/head so only
    # the ends poke out — the hero silhouette-breaker). On a black body the HARD
    # STEEL at BOTH tips is the single highest-value note at 40px, so each end
    # overshoots the silhouette and gets a metal glint.
    lo = (HX - 31, HY + 28)        # scabbard butt, out past the tail
    hi = (HX + 19, CROWN_Y - 18)   # handle tip, up past the crown
    pygame.draw.line(surf, _NIN_SHADOW, lo, hi, 7)
    pygame.draw.line(surf, _NIN_BLACK, lo, hi, 5)
    pygame.draw.line(surf, _NIN_CLOTH_H,
                     (lo[0] + 2, lo[1] - 2), (hi[0] - 2, hi[1] + 2), 1)
    # The crimson sageo cord runs the whole length between two dark edges so it
    # reads as a line, not a wash.
    pygame.draw.line(surf, _NIN_CRIMSON,
                     (lo[0] + 1, lo[1] - 3), (hi[0] - 1, hi[1] + 3), 1)

    dx, dy = hi[0] - lo[0], hi[1] - lo[1]
    blen = math.hypot(dx, dy)
    ux, uy = dx / blen, dy / blen
    px, py = -uy, ux                 # perpendicular, for the square guard

    # Square guard (tsuba) where the handle meets the blade, near the crown.
    gx = hi[0] - ux * 13
    gy = hi[1] - uy * 13
    guard = [
        (gx + px * 5, gy + py * 5), (gx - px * 5, gy - py * 5),
        (gx - px * 5 + ux * 3, gy - py * 5 + uy * 3),
        (gx + px * 5 + ux * 3, gy + py * 5 + uy * 3),
    ]
    _poly(surf, _NIN_BLACK, guard)
    pygame.draw.line(surf, _NIN_METAL_D, (gx + px * 4, gy + py * 4),
                     (gx - px * 4, gy - py * 4), 1)

    # Wrapped handle (tsuka) above the guard, poking past the crown — cord-wrap
    # ticks, then a HARD steel pommel cap glinting at the tip so the top end
    # clearly breaks the crown outline.
    for t in (4, 9):
        hxp = hi[0] - ux * t
        hyp = hi[1] - uy * t
        pygame.draw.line(surf, _NIN_CLOTH_H, (hxp + px * 2, hyp + py * 2),
                         (hxp - px * 2, hyp - py * 2), 1)
    pygame.draw.circle(surf, _NIN_METAL_D, (int(hi[0]), int(hi[1])), 3)
    pygame.draw.circle(surf, _NIN_METAL, (int(hi[0]), int(hi[1])), 2)
    pygame.draw.circle(surf, (255, 255, 255), (int(hi[0] - 1), int(hi[1] - 1)), 1)

    # Steel scabbard-butt cap (kojiri) glinting at the LOW tip past the tail —
    # the second hard metal note, sized to throw an EQUAL-weight steel break at
    # 40px on night, where the low tip is otherwise the softer of the two reads.
    pygame.draw.circle(surf, _NIN_METAL_D, (int(lo[0]), int(lo[1])), 4)
    pygame.draw.circle(surf, _NIN_METAL, (int(lo[0]), int(lo[1])), 3)
    pygame.draw.circle(surf, (255, 255, 255), (int(lo[0] + 1), int(lo[1] - 1)), 1)
    pygame.draw.circle(surf, (255, 255, 255), (int(lo[0]), int(lo[1] - 1)), 1)

    # Headband tails streaming off the BACK of the skull (drawn before the head
    # wrap so the wrap roots them). Two crimson ribbons aimed to trail OFF the
    # silhouette into open sky (up-left, away from the body) so they read as
    # motion, not body lines.
    bx, by = HX - 11, CROWN_Y + 2   # back-of-skull anchor
    for k, spread in ((0, 0), (1, 4)):
        t0 = (bx, by + k * 2)
        t1 = (bx - 13, by - 1 + flick + spread)
        t2 = (bx - 25, by + 2 + flick * 2 + spread)
        pygame.draw.lines(surf, _NIN_CRIMSON_D, False, [t0, t1, t2], 3)
        pygame.draw.lines(surf, _NIN_CRIMSON, False, [t0, t1, t2], 2)
    pygame.draw.line(surf, _NIN_CRIMSON_H, (bx, by), (bx - 11, by - 1 + flick), 1)

    # Full face wrap (fukumen): black cloth over the whole head from the
    # beak-base up past the crown, leaving a horizontal eye-slit.
    pygame.draw.ellipse(surf, _NIN_SHADOW, (HX - 13, CROWN_Y - 1, 26, 25))
    pygame.draw.ellipse(surf, _NIN_BLACK, (HX - 12, CROWN_Y, 24, 23))
    # Crown highlight so the black skull-cap doesn't vanish on night sky.
    pygame.draw.ellipse(surf, _NIN_CLOTH_H, (HX - 6, CROWN_Y + 1, 10, 4))
    # Lower-face wrap fold across the beak base, with a single cloth crease.
    fold = [(HX - 11, HY + 3), (HX + 12, HY + 1),
            (HX + 12, HY + 9), (HX - 10, HY + 11)]
    _poly(surf, _NIN_BLACK, fold)
    pygame.draw.line(surf, _NIN_CLOTH_H, (HX - 9, HY + 6), (HX + 10, HY + 4), 1)

    # Eye-slit: a bright metal band so Pip still reads as looking forward —
    # framed dark so it reads as a slit, not a bar.
    pygame.draw.rect(surf, (8, 9, 13), (HX - 6, HY - 3, 19, 7), border_radius=3)
    pygame.draw.rect(surf, _NIN_METAL, (HX - 4, HY - 1, 15, 3), border_radius=1)
    # Two darker pupils sitting in the slit so it reads as eyes, not a bar.
    pygame.draw.circle(surf, (20, 22, 30), (HX, HY), 1)
    pygame.draw.circle(surf, (20, 22, 30), (HX + 8, HY), 1)

    # Hachimaki band over the wrap (crimson) — the brow accent that ties the
    # trailing tails to the head. Dark cloth on both sides keeps it a line.
    by2 = CROWN_Y + 5
    pygame.draw.line(surf, _NIN_CRIMSON_D, (HX - 12, by2 + 1), (HX + 12, by2 - 1), 4)
    pygame.draw.line(surf, _NIN_CRIMSON, (HX - 12, by2), (HX + 12, by2 - 2), 3)
    pygame.draw.line(surf, _NIN_CRIMSON_H, (HX - 10, by2 - 1), (HX + 6, by2 - 2), 1)
    pygame.draw.circle(surf, _NIN_CRIMSON_D, (bx, by), 2)   # side knot

    # Obi sash wrapped around the belly, knotted at the side with a hanging end.
    bcx, bcy = 31, 53
    sash = [(bcx - 17, bcy - 3), (bcx + 14, bcy - 6),
            (bcx + 15, bcy + 1), (bcx - 16, bcy + 4)]
    _poly(surf, _NIN_SHADOW, sash)
    sash2 = [(bcx - 17, bcy - 2), (bcx + 14, bcy - 5),
             (bcx + 14, bcy - 1), (bcx - 16, bcy + 2)]
    _poly(surf, _NIN_BLACK, sash2)
    pygame.draw.line(surf, _NIN_CLOTH_H, (bcx - 15, bcy - 2), (bcx + 12, bcy - 5), 1)
    # Side knot + short hanging end (crimson accent on the body object).
    kx, ky = bcx - 15, bcy
    pygame.draw.circle(surf, _NIN_CRIMSON_D, (kx, ky), 3)
    pygame.draw.circle(surf, _NIN_CRIMSON, (kx, ky), 2)
    _poly(surf, _NIN_CRIMSON_D, [(kx - 1, ky + 2), (kx + 3, ky + 2),
                                 (kx + 1, ky + 9), (kx - 3, ky + 8)])
    _poly(surf, _NIN_CRIMSON, [(kx, ky + 3), (kx + 2, ky + 3),
                               (kx + 1, ky + 8), (kx - 1, ky + 8)])

    # Lower wing/tail back-edge rim: a single 1px cloth-highlight stroke tracing
    # the underside silhouette that faces open sky, so the dark mass keeps a
    # crisp lower edge against dark night backgrounds. Pure edge rim — held one
    # tone above shadow so the bright-sky day read is untouched.
    pygame.draw.lines(surf, _NIN_CLOTH_H, False,
                      [(15, 40), (22, 44), (28, 47), (38, 47), (45, 43)], 1)

    # Forearm wrap: ONE thicker black band near the wing root with a single
    # crimson tie so the wing reads as a bound shinobi arm, not bare plumage.
    wrx, wry = 40, 47
    pygame.draw.line(surf, _NIN_SHADOW, (wrx - 6, wry + 1), (wrx + 7, wry - 2), 5)
    pygame.draw.line(surf, _NIN_BLACK, (wrx - 6, wry + 1), (wrx + 7, wry - 2), 3)
    pygame.draw.line(surf, _NIN_CRIMSON, (wrx - 5, wry - 1), (wrx + 6, wry - 3), 1)


get_ninja_parrot = _make_skin(_paint_ninja, base_fn=_ninja_base)


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
# 4 · ASTRONAUT — a sleek modern flight-suit with an oval white helmet shell and
#     a hard hexagonal black faceplate (visor DOWN).
#
# The whole macaw is re-plumaged near-WHITE through
# the palette system, so the bird is a bright blob the dark sky never swallows,
# and the HELMET wins the read — the hard black faceplate is the single largest
# dark mass, carried at 40px by one dominant white diagonal glint. The flight-
# pack is GRAY (not black) and sits LOW behind the shoulder, overlapped by the
# body and tied in by a white strap, so it reads "pack on back", not a second
# head. One black shoulder yoke is the only body panel; the lone colour is a
# single cyan status line on the chest, kept off the face.
# ─────────────────────────────────────────────────────────────────────────────
_AST_W     = (244, 246, 250)       # glossy suit white
_AST_SH    = (200, 205, 214)       # suit shadow
_AST_BLACK = (21, 23, 28)          # visor / accent panels
_AST_GRAY  = (90, 97, 112)         # flight-pack / mid shadow
_AST_CYAN  = (43, 198, 224)        # cyan status accent
_AST_HI    = (255, 255, 255)

# Full near-white suit re-plumage. Every slot becomes glossy white with a cool
# shadow doing the line work so the dark sky never eats the silhouette; lenses
# dropped so the angular faceplate owns the face; beak goes dark so no warm gold
# survives the two-tone.
P_ASTRONAUT = _pal(
    tail=[(214, 219, 228), (224, 228, 236), (234, 237, 243), (244, 246, 250)],
    tail_line=_AST_SH,
    body_shadow=(196, 201, 211),
    body_main=_AST_W,
    body_chest=(255, 255, 255),
    body_belly=(232, 236, 242),
    sheen=(255, 255, 255, 150),
    wing_main=(228, 232, 239),
    wing_dark=_AST_SH,
    wing_tip=(248, 250, 253),
    wing_secondary=None,
    wing_highlight=_AST_HI,
    head_shadow=(200, 205, 214),
    head_main=_AST_W,
    head_cheek=(248, 250, 253),
    head_crown=(255, 255, 255),
    lens_frame=(200, 205, 214),
    lens_body=_AST_BLACK,
    lens_tint=None,
    lens_glint=None,
    beak_main=(70, 76, 90),
    beak_dark=_AST_BLACK,
    beak_gloss=(150, 156, 170),
    foot=_AST_BLACK,
)


def _astronaut_base(angle_deg):
    # Glossy-white suited bird, no aviators — the angular faceplate owns the head.
    return _build_parrot_with_palette(angle_deg, P_ASTRONAUT, draw_lenses=False)


def _paint_astronaut(surf, wing_angle_deg):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # Low-profile GRAY flight-pack hugging the shoulder. Drawn first so the body
    # overlaps its inner edge → reads worn ON the back, attached, not a second
    # mass. Gray + low (top below the crown) so the dark faceplate stays the
    # single largest dark shape; the top is canted (never a vertical bar
    # mirroring the helmet) and a white strap ties it to the suit.
    pkx, pky = BCX - 13, BCY + 1
    pack = [(pkx - 5, pky - 6), (pkx + 4, pky - 9), (pkx + 7, pky + 1),
            (pkx + 6, pky + 12), (pkx - 4, pky + 13), (pkx - 6, pky + 3)]
    _poly(surf, _AST_GRAY, pack)
    pygame.draw.line(surf, _AST_SH, (pkx - 4, pky - 5), (pkx + 5, pky + 11), 1)
    _poly(surf, _AST_BLACK, [(pkx - 4, pky + 8), (pkx + 6, pky + 8),
                             (pkx + 5, pky + 12), (pkx - 4, pky + 12)])
    pygame.draw.line(surf, _AST_HI, (pkx + 3, pky - 8), (BCX + 1, BCY - 9), 2)
    pygame.draw.line(surf, _AST_SH, (pkx + 3, pky - 7), (BCX + 1, BCY - 8), 1)

    # ONE bold black shoulder YOKE across the upper chest — the single body panel
    # that survives at 40px; the white body stays clean below it.
    yoke = [(BCX - 14, BCY - 7), (BCX - 4, BCY - 12), (BCX + 9, BCY - 11),
            (BCX + 15, BCY - 5), (BCX + 9, BCY - 5), (BCX - 2, BCY - 7),
            (BCX - 11, BCY - 3)]
    _poly(surf, _AST_BLACK, yoke)
    pygame.draw.line(surf, _AST_GRAY, (BCX - 11, BCY - 6), (BCX + 11, BCY - 8), 1)

    # Minimalist black chest module with one thin CYAN status line + dot — the
    # single colour accent on the whole skin.
    mx, my = BCX + 1, BCY + 1
    pygame.draw.rect(surf, _AST_BLACK, (mx - 6, my - 3, 13, 9), border_radius=2)
    pygame.draw.rect(surf, _AST_GRAY, (mx - 6, my - 3, 13, 9), 1, border_radius=2)
    pygame.draw.line(surf, _AST_CYAN, (mx - 4, my + 1), (mx + 3, my + 1), 1)
    pygame.draw.circle(surf, _AST_CYAN, (mx + 5, my - 1), 1)
    pygame.draw.circle(surf, _AST_HI, (mx - 4, my + 3), 1)

    # Black glove at the near wingtip, black boots, and a thin seam up the wing
    # root → the two-tone reaches every extremity.
    pygame.draw.line(surf, _AST_BLACK, (BCX + 4, BCY - 6), (BCX + 14, BCY - 9), 2)
    pygame.draw.circle(surf, _AST_BLACK, (BCX + 16, BCY - 4), 3)
    pygame.draw.circle(surf, _AST_SH, (BCX + 15, BCY - 5), 1)
    for fx in (BCX - 6, BCX):
        pygame.draw.line(surf, _AST_BLACK, (fx, BCY + 13), (fx - 1, BCY + 17), 3)
        pygame.draw.circle(surf, _AST_BLACK, (fx - 1, BCY + 17), 2)

    # Oval white helmet shell with a crisp gray rim (the outline pass only edges
    # the outer silhouette, so this internal rim separates shell from white body),
    # then a hard hexagonal BLACK faceplate (visor DOWN) with one dominant white
    # diagonal glint and a chin/comms wedge. The flatter oval is the modern read.
    hcx, hcy = HX + 1, HY - 1
    pygame.draw.ellipse(surf, _AST_GRAY, (hcx - 14, hcy - 14, 29, 27))
    pygame.draw.ellipse(surf, _AST_W, (hcx - 13, hcy - 13, 27, 25))
    pygame.draw.ellipse(surf, _AST_GRAY, (hcx - 13, hcy - 13, 27, 25), 1)
    pygame.draw.ellipse(surf, _AST_HI, (hcx - 9, hcy - 12, 11, 4))
    fx, fy = hcx + 1, hcy + 1
    face = [(fx - 11, fy - 4), (fx - 6, fy - 8), (fx + 9, fy - 7),
            (fx + 12, fy - 1), (fx + 8, fy + 7), (fx - 7, fy + 7),
            (fx - 11, fy + 2)]
    _poly(surf, (8, 9, 12), [(x, y + 1) for x, y in face])
    _poly(surf, _AST_BLACK, face)
    pygame.draw.line(surf, _AST_GRAY, (fx - 6, fy - 7), (fx + 8, fy - 6), 1)
    pygame.draw.line(surf, _AST_HI, (fx - 8, fy + 5), (fx + 6, fy - 6), 3)
    _poly(surf, _AST_BLACK, [(fx - 4, fy + 7), (fx + 6, fy + 7),
                             (fx + 3, fy + 12), (fx - 2, fy + 12)])


get_astronaut_parrot = _make_skin(_paint_astronaut, base_fn=_astronaut_base)


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
# 6 · VIKING — a rust-raider macaw: the whole bird is re-plumaged warm auburn
#     through the palette system, then it reads as a NORMAL parrot wearing
#     Viking gear — the bare macaw eye + hooked beak stay in the open under a
#     RAISED horned spangenhelm, a long braided moustache drops to two metal
#     beads over a chin beard, and a twin-bit axe is STOWED diagonally on the
#     back behind the round shield (carried, not wielded). The body must hold a
#     crisp edge on a bright sky, so the silhouette is wrapped in a near-black
#     outline instead of the default 1px line. Axe is drawn BEHIND the body, so
#     this skin uses its own compose rather than _make_skin's body-first order.
# ─────────────────────────────────────────────────────────────────────────────
_VK_RUST       = (154, 51, 34)
_VK_RUST_DK    = (94, 28, 18)
_VK_IRON       = (90, 94, 104)
_VK_IRON_DK    = (52, 56, 63)
_VK_IRON_HI    = (166, 174, 184)
_VK_RING       = (176, 182, 192)
_VK_FUR        = (74, 53, 38)
_VK_FUR_HI     = (122, 90, 64)
_VK_BEARD      = (36, 26, 20)
_VK_BEARD_HI   = (62, 44, 32)
_VK_SHIELD_RED = (110, 20, 16)
_VK_BRASS      = (199, 154, 58)
_VK_BONE       = (214, 198, 168)
_VK_HAFT       = (94, 56, 32)
_VK_HAFT_HI    = (150, 96, 56)
_VK_KEY        = (26, 20, 16)            # opaque face/axe keyline
_VK_OUTLINE    = (26, 20, 16, 235)       # near-black silhouette outline

# Full rusty-auburn re-plumage of the macaw; the deepest RUST_DK owns the line
# work, and lenses are dropped (the helm brow + facial hair own the face — the
# bare eye is painted back on in _viking_face).
_VK_PAL = _pal(
    tail=[(118, 38, 26), (138, 46, 30), (158, 58, 40), (180, 80, 56)],
    tail_line=_VK_RUST_DK, body_shadow=(112, 34, 22), body_main=_VK_RUST,
    body_chest=(182, 84, 58), body_belly=(122, 40, 24), sheen=(255, 220, 200, 90),
    wing_main=(140, 46, 30), wing_dark=(86, 26, 16), wing_tip=(196, 100, 72),
    wing_secondary=None, wing_highlight=(214, 130, 100), head_shadow=(112, 34, 22),
    head_main=_VK_RUST, head_cheek=(182, 84, 58), head_crown=(168, 64, 44),
    lens_frame=(120, 40, 26), lens_body=(40, 22, 16), lens_tint=None,
    lens_glint=None, beak_main=(196, 150, 96), beak_dark=(120, 84, 44),
    beak_gloss=(228, 200, 150), foot=(120, 78, 44),
)


def _viking_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _VK_PAL, draw_lenses=False)


def _viking_back(surf):
    # Round shield on the back: a proud iron rim, deep-red field, plank seams, a
    # single brass stud and a bright boss; then a scalloped fur ruff bridging the
    # neck. The shield is drawn AFTER the axe so it covers the haft's middle.
    sx, sy, sr = HX - 26, HY + 11, 13
    pygame.draw.circle(surf, _VK_IRON_DK, (sx, sy), sr + 2)
    pygame.draw.circle(surf, _VK_SHIELD_RED, (sx, sy), sr - 2)
    for dx in (-6, 0, 6):
        pygame.draw.line(surf, _VK_RUST_DK, (sx + dx, sy - sr + 4), (sx + dx, sy + sr - 4), 1)
    pygame.draw.circle(surf, _VK_BRASS, (sx, sy - sr + 2), 2)
    pygame.draw.circle(surf, (240, 210, 130), (sx, sy - sr + 2), 1)
    pygame.draw.circle(surf, _VK_IRON_DK, (sx, sy), 6)
    pygame.draw.circle(surf, _VK_IRON_HI, (sx, sy), 5)
    pygame.draw.circle(surf, _VK_IRON_DK, (sx, sy), 5, 1)
    pygame.draw.circle(surf, (255, 255, 255), (sx - 1, sy - 1), 1)
    ruff_y = HY + 9
    for i in range(-3, 4):
        fx = HX - 1 + i * 5
        r = 5 if i % 2 == 0 else 4
        pygame.draw.circle(surf, _VK_BEARD, (fx, ruff_y + 1), r)
        pygame.draw.circle(surf, _VK_FUR, (fx, ruff_y), r - 1)
    for i in range(-1, 2):
        pygame.draw.circle(surf, _VK_FUR_HI, (HX - 1 + i * 5, ruff_y - 1), 1)


def _viking_helm(surf):
    # Horned spangenhelm with the dome + brow lifted 4px and a short 2px nasal,
    # so the bare macaw eye (≈(50,40)) and hooked beak sit in the open below the
    # brow. Boot cuffs on the feet.
    cy = CROWN_Y
    for sgn, hx0 in ((-1, HX - 9), (1, HX + 9)):
        tipx = hx0 + sgn * 6
        mid = (hx0 + sgn * 5, cy - 6)
        _poly(surf, _VK_BEARD, [(hx0 - 4, cy + 2), (hx0 + 4, cy + 2), mid, (tipx + sgn * 2, cy - 16)])
        _poly(surf, _VK_FUR_HI, [(hx0 + sgn * 3, cy + 1), (hx0 + sgn * 4, cy + 1),
                                 (mid[0] + sgn, mid[1] + 1), (tipx + sgn * 2, cy - 15)])
        pygame.draw.circle(surf, _VK_FUR_HI, (tipx + sgn, cy - 15), 3)
        pygame.draw.circle(surf, _VK_BONE, (tipx + sgn, cy - 15), 2)
        pygame.draw.circle(surf, (244, 234, 210), (tipx + sgn - 1, cy - 16), 1)
    dy = -4
    pygame.draw.ellipse(surf, _VK_IRON_DK, (HX - 12, cy - 6 + dy, 25, 18))
    pygame.draw.ellipse(surf, _VK_IRON, (HX - 11, cy - 6 + dy, 23, 8))
    pygame.draw.ellipse(surf, _VK_IRON_HI, (HX - 6, cy - 5 + dy, 9, 4))
    pygame.draw.line(surf, _VK_IRON_DK, (HX - 11, cy + 5 + dy), (HX + 12, cy + 4 + dy), 4)
    pygame.draw.line(surf, _VK_IRON_HI, (HX - 11, cy + 4 + dy), (HX + 12, cy + 3 + dy), 1)
    for rx in (HX - 8, HX - 1, HX + 6):
        pygame.draw.circle(surf, _VK_IRON_HI, (rx, cy + 5 + dy), 1)
    nx = HX + 1
    pygame.draw.rect(surf, _VK_IRON_DK, (nx, cy + 4 + dy, 2, 5))
    pygame.draw.line(surf, _VK_IRON, (nx, cy + 4 + dy), (nx, cy + 8 + dy), 1)
    for fx, fy in ((27, 65), (35, 65)):
        pygame.draw.circle(surf, _VK_BEARD, (fx, fy + 1), 3)
        pygame.draw.circle(surf, _VK_FUR_HI, (fx, fy), 2)


def _viking_face(surf):
    # The bare macaw eye, then a dark chin beard, a lighter walrus moustache band
    # dropping two braids to metal beads, the redrawn hooked beak on top, and the
    # beads. A 1px keyline edges every facial-hair mass so it separates from the
    # body. The light-on-dark stack (light moustache over dark chin) is what
    # keeps the 'stache + beads legible at 40px.
    ex, ey = 50, 40
    _aaellipse(surf, (250, 243, 236), (ex, ey), 6, 5)
    pygame.draw.line(surf, (236, 210, 205), (ex - 5, ey - 2), (ex + 5, ey - 2), 1)
    pygame.draw.line(surf, (236, 210, 205), (ex - 5, ey + 2), (ex + 5, ey + 2), 1)
    pygame.draw.circle(surf, (40, 26, 30), (ex + 1, ey), 3)
    pygame.draw.circle(surf, (15, 10, 12), (ex + 1, ey), 3, 1)
    pygame.draw.circle(surf, (255, 255, 255), (ex, ey - 1), 1)

    # Chin beard — a narrow rounded tuft hanging from the chin between the two
    # braids; a doubled keyline strengthens its edge against the body.
    cx0, cy0 = 47, 53
    chin = [(cx0 - 4, cy0), (cx0 - 5, cy0 + 6), (cx0 - 2, cy0 + 11),
            (cx0 + 3, cy0 + 11), (cx0 + 5, cy0 + 6), (cx0 + 4, cy0), (cx0, cy0 - 1)]
    _poly(surf, _VK_KEY, [(x, y + 2) for x, y in chin])
    _poly(surf, _VK_KEY, [(x, y + 1) for x, y in chin])
    _poly(surf, _VK_BEARD, chin)
    _poly(surf, _VK_BEARD_HI, [(cx0 - 4, cy0 + 1), (cx0 - 1, cy0 + 1),
                              (cx0 - 2, cy0 + 8), (cx0 - 5, cy0 + 6)])

    # Walrus moustache — a compact lighter band under the beak over a keyline.
    mx, my = 50, 45
    band = [(mx - 8, my - 1), (mx - 9, my + 3), (mx - 5, my + 4), (mx - 1, my + 2),
            (mx + 4, my + 2), (mx + 8, my + 4), (mx + 9, my + 1), (mx + 7, my - 1), (mx, my - 2)]
    _poly(surf, _VK_KEY, [(x, y + 1) for x, y in band])
    _poly(surf, _VK_BEARD_HI, band)
    pygame.draw.lines(surf, _VK_BONE, False,
                      [(mx - 7, my - 1), (mx - 1, my - 2), (mx + 4, my - 2), (mx + 7, my)], 1)

    # Two braids dropping from the band corners to the beads.
    for sgn, bx0 in ((-1, mx - 8), (1, mx + 8)):
        braid = [(bx0, my + 2), (bx0 + sgn, my + 5), (bx0 + sgn, my + 12),
                 (bx0 - sgn * 2, my + 12), (bx0 - sgn * 2, my + 4)]
        _poly(surf, _VK_KEY, [(x, y + 1) for x, y in braid])
        _poly(surf, _VK_BEARD_HI, braid)
        pygame.draw.line(surf, _VK_BEARD, (bx0, my + 5), (bx0, my + 11), 1)

    # Redraw the hooked beak on top so it always pokes through between the braids.
    beak_pts = [(55, 41), (61, 44), (58, 48), (52, 46)]
    pygame.draw.polygon(surf, (196, 150, 96), beak_pts)
    pygame.draw.polygon(surf, (120, 84, 44), beak_pts, 1)
    pygame.draw.line(surf, (228, 200, 150), (55, 42), (59, 44), 1)
    pygame.draw.line(surf, (120, 84, 44), (52, 44), (58, 45), 1)

    # Metal beads capping each braid tip.
    for bdx, bdy in ((mx - 9, my + 14), (mx + 9, my + 14)):
        pygame.draw.circle(surf, _VK_KEY, (bdx, bdy), 3)
        pygame.draw.circle(surf, _VK_RING, (bdx, bdy), 2)
        pygame.draw.circle(surf, (255, 255, 255), (bdx - 1, bdy - 1), 1)


def _viking_axe(surf):
    # Twin-bit axe slung diagonally across the back (butt low past the tail, head
    # high past the back shoulder into open sky). Each bit is a crescent held off
    # the haft by a slim socket, so a wedge of open sky bites between bit and
    # socket — that negative-space notch, not a painted line, splits the head
    # into a clean "><" twin-crescent. Drawn BEHIND the body.
    blade, blade_dk, blade_hi = _VK_IRON, _VK_IRON_DK, _VK_IRON_HI
    lo = (HX - 30, HY + 30)
    hi = (HX - 3, CROWN_Y - 23)
    dx, dy = hi[0] - lo[0], hi[1] - lo[1]
    blen = math.hypot(dx, dy)
    ux, uy = dx / blen, dy / blen
    px, py = -uy, ux

    hx0, hy0 = lo
    hx1, hy1 = hi[0] - ux * 8, hi[1] - uy * 8
    pygame.draw.line(surf, _VK_KEY, (hx0, hy0), (hx1, hy1), 6)
    pygame.draw.line(surf, _VK_HAFT, (hx0, hy0), (hx1, hy1), 4)
    pygame.draw.line(surf, _VK_HAFT_HI, (hx0 + px, hy0 + py), (hx1 + px, hy1 + py), 1)
    for t in (0.30, 0.55, 0.80):
        wx, wy = hx0 + (hx1 - hx0) * t, hy0 + (hy1 - hy0) * t
        pygame.draw.line(surf, blade_dk, (wx - px * 2, wy - py * 2), (wx + px * 2, wy + py * 2), 1)
    pygame.draw.circle(surf, blade_dk, (int(lo[0]), int(lo[1])), 3)
    pygame.draw.circle(surf, blade_hi, (int(lo[0]), int(lo[1])), 2)

    tx, ty = hi

    def L(a, b):
        return (tx + ux * a + px * b, ty + uy * a + py * b)

    for side in (-1, 1):
        bit = [L(8, side * 4), L(8, side * 8), L(4, side * 12), L(0, side * 13),
               L(-4, side * 12), L(-8, side * 8), L(-8, side * 4), L(-5, side * 7),
               L(0, side * 8), L(5, side * 7)]
        _poly(surf, blade_dk, bit)
        facet = [L(6, side * 6), L(6, side * 9), L(0, side * 11),
                 L(-6, side * 9), L(-6, side * 6), L(0, side * 9)]
        _poly(surf, blade, facet)
        pygame.draw.lines(surf, blade_hi, False, [L(8, side * 8), L(0, side * 13), L(-8, side * 8)], 2)
        pygame.draw.line(surf, (255, 255, 255), L(0, side * 13), L(0, side * 12), 1)
    pygame.draw.line(surf, _VK_KEY, L(8, 0), L(-8, 0), 5)
    pygame.draw.line(surf, blade_dk, L(8, 0), L(-8, 0), 3)
    pygame.draw.line(surf, blade, L(7, 0), L(-7, 0), 1)
    pygame.draw.circle(surf, _VK_RING, (int(tx), int(ty)), 1)


def _viking_getter():
    # The axe must sit BEHIND the body, so the body-first order in _make_skin
    # can't be used: axe -> body -> shield+fur -> raised helm -> face -> outline.
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _viking_axe(comp)
        comp.blit(_viking_base(wing_angle), (0, PARROT_DY))
        _viking_back(comp)
        _viking_helm(comp)
        _viking_face(comp)
        return _add_outline(comp, outline_color=_VK_OUTLINE)

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_flat(a) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


get_viking_parrot = _viking_getter()


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
# PARROT SPECIES — full-body recolours of the macaw via the 24-slot palette
# system (dollar_parrot_ghost._build_parrot_with_palette). These are *designs*,
# not props: the whole bird is re-plumaged. Pip keeps his aviators across the
# family (his signature), so the species read as "Pip's cousins" rather than a
# generic recolour. The crested cockatoo adds a small geometry signature.
# ─────────────────────────────────────────────────────────────────────────────

P_BLUEGOLD = _pal(
    tail=[(30, 90, 170), (40, 110, 190), (60, 140, 210), (90, 170, 230)],
    tail_line=(20, 60, 120),
    body_shadow=(25, 70, 140), body_main=(45, 110, 190),
    body_chest=(235, 200, 70), body_belly=(245, 215, 90),
    sheen=(255, 255, 255, 90),
    wing_main=(35, 95, 175), wing_dark=(20, 55, 120), wing_tip=(70, 150, 220),
    wing_secondary=(235, 200, 70), wing_highlight=(150, 200, 245),
    head_shadow=(25, 70, 140), head_main=(50, 120, 200),
    head_cheek=(240, 235, 235), head_crown=(70, 150, 220),
    lens_frame=(240, 200, 80), lens_body=(20, 25, 45),
    lens_tint=(60, 120, 190, 120), lens_glint=(255, 255, 255),
    beak_main=(40, 40, 48), beak_dark=(15, 15, 20), beak_gloss=(120, 120, 130),
    foot=(60, 55, 55),
)

P_AMAZON = _pal(
    tail=[(40, 120, 50), (60, 150, 60), (90, 180, 80), (150, 200, 90)],
    tail_line=(30, 90, 40),
    body_shadow=(35, 100, 45), body_main=(70, 160, 70),
    body_chest=(110, 190, 90), body_belly=(150, 205, 120),
    sheen=(255, 255, 255, 80),
    wing_main=(55, 140, 60), wing_dark=(30, 90, 40), wing_tip=(210, 70, 60),
    wing_secondary=(240, 200, 70), wing_highlight=(170, 210, 130),
    head_shadow=(40, 110, 50), head_main=(80, 170, 75),
    head_cheek=(235, 210, 70), head_crown=(240, 220, 80),
    lens_frame=(230, 200, 80), lens_body=(20, 30, 20),
    lens_tint=(60, 140, 70, 120), lens_glint=(255, 255, 255),
    beak_main=(190, 180, 170), beak_dark=(120, 110, 100),
    beak_gloss=(235, 230, 220), foot=(120, 110, 90),
)

P_SUNCONURE = _pal(
    tail=[(60, 130, 70), (120, 170, 70), (200, 170, 60), (240, 150, 50)],
    tail_line=(120, 90, 30),
    body_shadow=(210, 120, 30), body_main=(250, 180, 40),
    body_chest=(252, 200, 60), body_belly=(255, 150, 40),
    sheen=(255, 255, 255, 100),
    wing_main=(245, 170, 40), wing_dark=(200, 110, 30), wing_tip=(70, 150, 70),
    wing_secondary=(90, 170, 90), wing_highlight=(255, 225, 120),
    head_shadow=(220, 120, 30), head_main=(252, 175, 45),
    head_cheek=(250, 130, 50), head_crown=(255, 200, 70),
    lens_frame=(60, 60, 60), lens_body=(25, 20, 15),
    lens_tint=(255, 180, 80, 110), lens_glint=(255, 255, 255),
    beak_main=(40, 38, 42), beak_dark=(15, 15, 18), beak_gloss=(110, 110, 115),
    foot=(80, 70, 55),
)

P_HYACINTH = _pal(
    tail=[(30, 40, 120), (35, 50, 140), (45, 65, 165), (60, 85, 190)],
    tail_line=(20, 28, 90),
    body_shadow=(25, 35, 110), body_main=(45, 60, 165),
    body_chest=(60, 80, 185), body_belly=(75, 95, 200),
    sheen=(255, 255, 255, 70),
    wing_main=(38, 52, 150), wing_dark=(22, 30, 100), wing_tip=(70, 90, 195),
    wing_secondary=None, wing_highlight=(120, 140, 220),
    head_shadow=(25, 35, 110), head_main=(48, 64, 170),
    head_cheek=(245, 210, 60), head_crown=(60, 80, 185),
    lens_frame=(245, 210, 60), lens_body=(15, 18, 40),
    lens_tint=(50, 65, 160, 130), lens_glint=(255, 255, 255),
    beak_main=(30, 30, 38), beak_dark=(12, 12, 18), beak_gloss=(90, 90, 100),
    foot=(45, 45, 55),
)

P_COCKATOO = _pal(
    tail=[(235, 235, 240), (240, 240, 245), (245, 245, 250), (250, 250, 252)],
    tail_line=(180, 180, 190),
    body_shadow=(205, 205, 215), body_main=(245, 245, 250),
    body_chest=(252, 252, 255), body_belly=(255, 255, 255),
    sheen=(255, 255, 255, 120),
    wing_main=(238, 238, 245), wing_dark=(200, 200, 212), wing_tip=(250, 220, 90),
    wing_secondary=None, wing_highlight=(255, 255, 255),
    head_shadow=(210, 210, 220), head_main=(248, 248, 252),
    head_cheek=(250, 225, 90), head_crown=(255, 255, 255),
    lens_frame=(80, 80, 90), lens_body=(25, 25, 32),
    lens_tint=(200, 210, 230, 110), lens_glint=(255, 255, 255),
    beak_main=(70, 70, 78), beak_dark=(35, 35, 42), beak_gloss=(140, 140, 150),
    foot=(120, 115, 115),
)

P_LORIKEET = _pal(
    tail=[(40, 120, 50), (70, 150, 60), (120, 180, 60), (180, 200, 60)],
    tail_line=(30, 90, 40),
    body_shadow=(180, 50, 40), body_main=(225, 70, 55),
    body_chest=(245, 120, 50), body_belly=(250, 200, 70),
    sheen=(255, 255, 255, 90),
    wing_main=(55, 150, 65), wing_dark=(30, 100, 45), wing_tip=(240, 200, 70),
    wing_secondary=(70, 170, 80), wing_highlight=(150, 210, 120),
    head_shadow=(30, 60, 140), head_main=(50, 90, 190),
    head_cheek=(70, 110, 210), head_crown=(60, 100, 200),
    lens_frame=(245, 160, 50), lens_body=(20, 25, 45),
    lens_tint=(80, 130, 200, 120), lens_glint=(255, 255, 255),
    beak_main=(245, 130, 40), beak_dark=(180, 80, 20), beak_gloss=(255, 200, 120),
    foot=(90, 80, 70),
)


def _species_getter(P):
    return _make_prebuilt_skin(lambda a, _P=P: _build_parrot_with_palette(a, _P))


get_bluegold_parrot = _species_getter(P_BLUEGOLD)
get_amazon_parrot = _species_getter(P_AMAZON)
get_sunconure_parrot = _species_getter(P_SUNCONURE)
get_hyacinth_parrot = _species_getter(P_HYACINTH)
get_lorikeet_parrot = _species_getter(P_LORIKEET)


# Cockatoo = white palette + a recurved yellow head crest (geometry signature),
# composited via the taller-canvas paint pattern so the plumes clear the crown.
_COCK_CREST = (250, 215, 80)
_COCK_CREST_D = (224, 182, 52)


def _paint_cockatoo_crest(surf, _a):
    base_y = CROWN_Y + 5  # just above the white crown
    for dx, h, lean in ((-3, 16, 4), (0, 21, 6), (3, 17, 9)):
        x = HX + dx
        root = (x, base_y + 2)
        mid = (x + lean // 2, base_y - h // 2)
        tip = (x + lean, base_y - h)
        pygame.draw.line(surf, _COCK_CREST_D, root, mid, 4)
        pygame.draw.line(surf, _COCK_CREST, mid, tip, 3)


get_cockatoo_parrot = _make_skin(
    _paint_cockatoo_crest,
    base_fn=lambda a: _build_parrot_with_palette(a, P_COCKATOO))


# ─────────────────────────────────────────────────────────────────────────────
# PRISM (epic) — the faceted/crystalline parrot: hard cut-crystal geometry
# against the whole tab's soft feathers. Every signature is a flat fill split by
# a hard white edge so it stays sharp and reads as polished geometry, not
# feathers, once downscaled to the 40px store thumbnail — a 3-shard crystal crest
# breaking the crown, two large facet planes carrying the crystalline language
# below the crown, two hard chest/wing facet glints, and a pair of refraction
# diamonds scattering into open sky.
# ─────────────────────────────────────────────────────────────────────────────
# Crystal palette: cool teal mass, amethyst undertone, rose refraction, and a
# pure white facet glint that owns every sharp edge. The deep teal is the
# keyline that holds shards apart from sky and from the body mass.
_PRISM_TEAL   = (94, 215, 208)     # #5ED7D0 crystal teal
_PRISM_AMETH  = (185, 140, 240)    # #B98CF0 amethyst
_PRISM_ROSE   = (255, 154, 208)    # #FF9AD0 rose refraction
_PRISM_GLINT  = (255, 255, 255)    # facet glint
_PRISM_DEEP   = (46, 110, 120)     # #2E6E78 deep teal keyline


# Full crystal-teal re-plumage with an amethyst undertone: the tail/wing line
# work runs the deepest teal so facets read against the body, the chest carries
# the amethyst shift, and aviators are RETAINED (tinted crystal-teal — Pip's
# signature) rather than dropped, since the shard crest owns the silhouette.
P_PRISM = _pal(
    tail=[(36, 92, 102), (52, 132, 134), (78, 178, 176), (118, 210, 204)],
    tail_line=_PRISM_DEEP,
    body_shadow=(40, 100, 110),
    body_main=_PRISM_TEAL,
    body_chest=(150, 196, 224),       # cooled amethyst-leaning chest
    body_belly=(132, 224, 216),
    sheen=(230, 248, 255, 110),
    wing_main=(70, 176, 178),
    wing_dark=_PRISM_DEEP,
    wing_tip=(150, 232, 224),
    wing_secondary=(150, 122, 210),   # amethyst secondary so the wing refracts
    wing_highlight=(214, 250, 246),
    head_shadow=(40, 100, 110),
    head_main=_PRISM_TEAL,
    head_cheek=(132, 224, 216),
    head_crown=(120, 206, 224),
    lens_frame=(150, 122, 210),       # amethyst rims keep the aviators on-theme
    lens_body=(24, 40, 56),
    lens_tint=(120, 220, 220, 130),
    lens_glint=(255, 255, 255),
    beak_main=(120, 210, 210),
    beak_dark=_PRISM_DEEP,
    beak_gloss=(220, 250, 248),
    foot=(70, 140, 150),
)


def _facet(surf, pts, fill, *, edge=_PRISM_GLINT, edge_w=2):
    """A flat crystal facet: a hard single-colour fill with a bright edge so
    it reads as polished geometry, not a feather. The white edge is what keeps
    the shard sharp once the sprite is downscaled to the store thumbnail; ≥2px
    by default so the edge survives the 40px downscale."""
    pygame.draw.polygon(surf, fill, pts)
    pygame.draw.polygon(surf, edge, pts, edge_w)


def _shard(surf, root, tip, half, *, light, dark, sky_edge=False):
    """One angular crystal shard from `root` up to `tip`, split down the spine
    into a lit face and a shadowed face so it reads as a 3-D faceted prism. A
    full-white spine highlight runs root→tip as the hero edge that survives
    40px. When `sky_edge`, a deep-teal keyline traces the outer edges so the
    shard tip holds against bright day sky instead of dropping out."""
    rx, ry = root
    tx, ty = tip
    # Two faces meeting at the spine; the base is `half` wide each side of root.
    left = [(rx - half, ry), (rx, ry - 1), (tx, ty)]
    right = [(rx, ry - 1), (rx + half, ry), (tx, ty)]
    _facet(surf, left, dark, edge_w=1)
    _facet(surf, right, light, edge_w=1)
    if sky_edge:
        # Deep-teal outline on the sky-facing edges so the point doesn't vanish.
        pygame.draw.line(surf, _PRISM_DEEP, (rx - half, ry), (tx, ty), 1)
        pygame.draw.line(surf, _PRISM_DEEP, (rx + half, ry), (tx, ty), 1)
    # Full-white spine — the brightest, sharpest edge, drawn last so it owns the
    # centre of the shard at any size.
    pygame.draw.line(surf, _PRISM_GLINT, (rx, ry - 1), (tx, ty), 2)


def _diamond(surf, cx, cy, r, fill):
    """A floating refraction diamond (rotated square) with a white core glint —
    the aura sparkle that scatters off the back. The white core is ≥2px so it
    holds the 'crystal sparkle' read at thumbnail size."""
    _facet(surf, [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill,
           edge_w=1)
    pygame.draw.circle(surf, _PRISM_GLINT, (cx, cy), 2)


def _paint_prism(surf, _a):
    base_y = CROWN_Y + 4   # roots just above the crystal crown

    # Two LARGE flat planes split the back/wing into a lit teal face and an
    # amethyst shadow face, divided by a single hard white spine — the same
    # faceted grammar as the crest, so the whole bird reads as cut crystal, not a
    # soft body wearing a hat.
    spine = [(20, 39), (31, 45), (43, 47)]   # back ridge, up-right toward wing
    lit = [(20, 39), (31, 45), (43, 47), (40, 53), (28, 52), (18, 46)]
    shadow = [(20, 39), (18, 46), (14, 50), (16, 41)]
    _facet(surf, lit, (110, 224, 216), edge_w=1)         # lit teal plane
    _facet(surf, shadow, (108, 92, 168), edge_w=1)       # amethyst shadow plane
    pygame.draw.lines(surf, _PRISM_GLINT, False, spine, 2)  # the white spine

    # TWO LARGE hard facets — one rose, one amethyst — each a flat triangle with
    # a ≥2px white edge, pointed like the crest shards. Two notes, two hues: the
    # spectrum tell without scattering into mud at 40px.
    _facet(surf, [(28, 49), (35, 54), (27, 58)], _PRISM_ROSE)      # chest rose
    _facet(surf, [(40, 43), (47, 46), (40, 51)], _PRISM_AMETH)     # wing amethyst

    # HERO: 3 angular crystal shards fanning up PAST the crown. The centre shard
    # is tallest and the outer two splay out so the cluster reads as a gem cluster
    # breaking the silhouette. The right-most shard gets the deep-teal sky-edge so
    # its tip holds on day sky. Painted after the body so it sits on top.
    shards = (
        (HX - 7, base_y + 1, HX - 13, base_y - 14, 4, _PRISM_AMETH, _PRISM_DEEP, False),
        (HX - 1, base_y,     HX - 2,  base_y - 24, 5, _PRISM_TEAL,  _PRISM_DEEP, True),
        (HX + 6, base_y + 1, HX + 12, base_y - 16, 4, _PRISM_ROSE,  _PRISM_DEEP, True),
    )
    for rx, ry, tx, ty, half, light, dark, sky_edge in shards:
        _shard(surf, (rx, ry), (tx, ty), half, light=light, dark=dark,
               sky_edge=sky_edge)
    # A small teal facet seats the cluster onto the crown so it reads anchored,
    # leaving a sliver of body between the crown facet and the aviator top rim.
    _facet(surf, [(HX - 9, base_y + 2), (HX + 8, base_y + 2),
                  (HX + 5, base_y - 3), (HX - 6, base_y - 3)], _PRISM_TEAL,
           edge_w=1)

    # A 1px bright top rim across both lenses so Pip's signature glasses catch
    # the light again under the crest — the hard top edge that separates lens
    # from face at a glance.
    pygame.draw.line(surf, (214, 250, 246), (40, 44), (46, 44), 2)
    pygame.draw.line(surf, (214, 250, 246), (49, 44), (54, 44), 2)

    # Two 4-point diamond sparkles drifting off the back into OPEN sky (kept off
    # the near-black card edge), white cores ≥2px so they read as scattered
    # crystal light. Held to two so the bird stays epic, not legendary.
    _diamond(surf, HX - 19, CROWN_Y + 5, 3, _PRISM_ROSE)
    _diamond(surf, HX - 24, CROWN_Y + 15, 2, _PRISM_TEAL)


get_prism_lorikeet = _make_skin(
    _paint_prism,
    base_fn=lambda a: _build_parrot_with_palette(a, P_PRISM))


# ─────────────────────────────────────────────────────────────────────────────
# AURORA (legendary) — night sky given wings: a midnight-galaxy Pip haloed by a
# bright additive teal/blue crescent, crowned with a connected green→magenta
# nebula crest, trailing wide flowing aurora ribbons where the tail-fan was. The
# legendary tell is the luminous halo PLUS the silhouette-breaking ribbon tail —
# a clear tier above the single-zone epics.
#
# Draw order matters: the halo and ribbon tail must paint BEHIND the body, so
# this can't use _make_skin's body-first _compose. Mirroring the viking-axe
# pattern, this is a custom getter — back-aura (halo + ribbons) → recoloured
# galaxy body → front overlay (nebula crest, star flecks, rim light) → house
# outline → per-(frame, 3°-bucket) rotation cache. The aurora is baked into each
# of the 4 frames and sweeps with the wing beat so the flap still reads alive.
# ─────────────────────────────────────────────────────────────────────────────
_AUR_INDIGO   = (28, 27, 58)          # #1C1B3A midnight indigo
_AUR_GREEN    = (63, 224, 166)        # #3FE0A6 aurora green
_AUR_MAGENTA  = (196, 92, 232)        # #C45CE8 aurora magenta
_AUR_STARBLU  = (111, 168, 255)       # #6FA8FF star blue
_AUR_GLINT    = (255, 255, 255)       # #FFFFFF star glint

# Body re-plumage: a deep midnight-indigo galaxy. The core values are lifted so
# the body reads as cosmic, not a flat void; the crown/back cool toward aurora
# teal, the belly toward magenta. Lenses keep Pip's aviators but tint to aurora
# teal so the signature shades read on the night palette; the beak is brightened
# so the macaw face survives.
_AURORA_PAL = _pal(
    tail=[(30, 28, 60), (40, 38, 80), (54, 56, 110), (74, 90, 150)],
    tail_line=(20, 19, 42),
    body_shadow=(26, 24, 54),
    body_main=(40, 38, 82),
    body_chest=(58, 58, 116),
    body_belly=(54, 46, 96),
    sheen=(150, 180, 255, 95),
    wing_main=(44, 44, 92),
    wing_dark=(22, 21, 46),
    wing_tip=(92, 124, 196),
    wing_secondary=None,
    wing_highlight=(128, 184, 250),
    head_shadow=(26, 24, 54),
    head_main=(42, 40, 86),
    head_cheek=(62, 64, 122),
    head_crown=(54, 74, 130),
    lens_frame=(96, 110, 168),
    lens_body=(12, 16, 36),
    lens_tint=(70, 210, 180, 150),
    lens_glint=(235, 255, 250),
    beak_main=(150, 160, 210),
    beak_dark=(52, 56, 100),
    beak_gloss=(225, 238, 255),
    foot=(76, 80, 130),
)


def _aurora_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _AURORA_PAL)


def _aurora_mix(t):
    """Green→star-blue→magenta light band, the aurora's signature ramp."""
    if t < 0.5:
        return lerp_color(_AUR_GREEN, _AUR_STARBLU, t / 0.5)
    return lerp_color(_AUR_STARBLU, _AUR_MAGENTA, (t - 0.5) / 0.5)


def _flap_phase(angle_deg):
    """0 on the down-stroke (wing 50°) → 1 on the up-stroke (-40°). The ribbons
    stream long/loose on the up-beat and bunch tight on the down-beat so the
    baked aurora still feels alive across the 4 frames."""
    return 1.0 - (angle_deg + 40) / 90.0


def _smooth_curve(p0, p1, p2, steps=10):
    """Quadratic-Bezier sample list so wisps/ribbons render as smooth curves
    rather than the 3-point polylines that read as straight rods at 40px."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def _crescent_arc(cx, cy, r, a0, a1, steps=14):
    """Point list along a circular arc (radians a0→a1) — the spine of the
    legendary halo crescent, sampled fine enough to draw as a thick smooth band
    that survives the 40px downscale."""
    pts = []
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * (i / steps)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def _aurora_back(surf, angle_deg):
    """Every glowing element lives here, BEHIND the outlined bird, so the house
    outline (grown from the bird's alpha mask) never boxes a bloom into its own
    dark-rimmed island. Two passes, both un-outlined: an additive under-glow
    buffer that shines on dark night skies, then an opaque bright-detail buffer
    (halo crescent, crest cores, ribbon spines as solid bright pixels with a thin
    indigo backing) so they also survive a bright day/dusk sky where additive
    washes out. Contents: the halo crescent arcing behind+above the head, the
    nebula crest wisp-mass past the crown, and the aurora ribbon tail."""
    phase = _flap_phase(angle_deg)
    cbx, cby = HX - 1, CROWN_Y + 1                  # crest root, set into the crown
    sway = (phase - 0.5) * 3

    # Five overlapping tapered wisps that all spring from ONE shared crown base
    # and curve OUTWARD, the cluster WIDER than it is tall so it reads as a cosmic
    # crest fanning over the skull. Each entry: tip offset + outward control bow +
    # green→magenta ramp position (matching the tail's sweep) + relative height.
    crest = (
        (-13, -15, -10, 0.05),   # far left, low, bows hard left
        (-7,  -20, -6,  0.28),   # left, mid
        (-1,  -23, -1,  0.50),   # centre, tallest — still WIDER cluster overall
        (6,   -19, 6,   0.72),   # right, mid
        (12,  -14, 10,  0.95),   # far right, low, bows hard right
    )

    def wisp_path(dx, dy, bow):
        tip = (cbx + dx + sway, cby + dy)
        ctrl = (cbx + dx * 0.55 + bow + sway * 0.5, cby + dy * 0.5)
        root = (cbx + dx * 0.10, cby + 1)           # all roots converge on the crown
        return _smooth_curve(root, ctrl, tip)

    # Three overlapping S-curve ribbon curtains sweeping down-back into open sky,
    # built wide (a tapering band, not a sliver) with a green→magenta gradient.
    def ribbon_path(k):
        reach = 22 + int(phase * 7)
        droop = (1.0 - phase) * 4                    # tail dips on the down-beat
        bx, by = 14, HY + 7 + k * 4
        c1 = (bx - reach * 0.42, by + 1 + k * 2 - 3)        # bow up first
        c2 = (bx - reach * 0.82, by + 9 + k * 5 + droop)    # then down → S
        tip = (bx - reach, by + 16 + k * 7 + droop)
        return _smooth_curve((bx, by), c1, c2, steps=6) + \
            _smooth_curve(c2, ((c2[0] + tip[0]) / 2, tip[1] - 1), tip, steps=5)

    # Halo crescent: a WIDE arc wrapping the head from the left flank, over the
    # top, down the right flank, sized larger than the skull (r=22) so the bright
    # band clears OUTSIDE the silhouette on the sides — the part that actually
    # reads as a halo separating bird from sky, since the crest occupies the top.
    hcx2, hcy2 = HX - 2, HY - 1
    halo_r = 22
    halo_spine = _crescent_arc(hcx2, hcy2, halo_r, math.radians(195), math.radians(345))

    # ── pass 1: additive under-glow (night) ──────────────────────────────────
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for i, (gx, gy) in enumerate(halo_spine):
        col = _AUR_STARBLU if i % 2 else _AUR_GREEN
        blit_glow(glow, int(gx), int(gy), 8, col, alpha=130)
    # Connected crest haze — a single soft bloom over the WHOLE wisp mass so the
    # gaps fill with light and the cluster reads as ONE crest, not separate stalks.
    for dx, dy, bow, t in crest:
        path = wisp_path(dx, dy, bow)
        for p in (path[1], path[len(path) // 2], path[-1]):
            blit_glow(glow, int(p[0]), int(p[1]), 6, _aurora_mix(t), alpha=95)
    blit_glow(glow, cbx, cby - 3, 13, _AUR_GREEN, alpha=70)
    blit_glow(glow, cbx, cby - 5, 10, _AUR_MAGENTA, alpha=55)
    for k in range(3):
        path = ribbon_path(k)
        blit_glow(glow, int(path[len(path) // 2][0]), int(path[len(path) // 2][1]),
                  5, _aurora_mix(k / 2.0), alpha=110)
        blit_glow(glow, int(path[-1][0]), int(path[-1][1]), 4, _aurora_mix(k / 2.0), alpha=100)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── pass 2: opaque bright detail (day + night) ───────────────────────────
    det = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _INK = (18, 16, 36)                             # thin dark backing for bright sky

    # Halo CRESCENT — the legendary tell: a 5px teal→star-blue band over a 7px
    # dark backing, a green inner edge, a magenta accent on the lower flanks, and
    # white glints near both flank ends so it survives 40px on BOTH skies.
    pygame.draw.lines(det, _INK, False, halo_spine, 7)
    pygame.draw.lines(det, _AUR_STARBLU, False, halo_spine, 5)
    inner = _crescent_arc(hcx2, hcy2, halo_r - 2, math.radians(200), math.radians(340))
    pygame.draw.lines(det, _AUR_GREEN, False, inner, 2)
    lflank = _crescent_arc(hcx2, hcy2, halo_r + 1, math.radians(196), math.radians(240))
    rflank = _crescent_arc(hcx2, hcy2, halo_r + 1, math.radians(300), math.radians(344))
    pygame.draw.lines(det, _AUR_MAGENTA, False, lflank, 2)
    pygame.draw.lines(det, _AUR_MAGENTA, False, rflank, 2)
    for fp in (halo_spine[1], halo_spine[-2]):       # bright caps at each flank
        pygame.draw.circle(det, _AUR_GLINT, (int(fp[0]), int(fp[1])), 2)

    # Nebula CREST — a connecting indigo-haze plinth under the wisp roots, then
    # the wisps as smooth tapering curves over it (longest-first so the centre
    # tucks behind the leans). Each: a 4px dark backing, a 3px green→magenta core,
    # thinning to a 1px tip. Their roots overlap so the mass reads as ONE crest.
    base_pts = [(cbx - 13, cby + 1), (cbx, cby - 3), (cbx + 12, cby + 1)]
    pygame.draw.polygon(det, (40, 36, 86, 200),
                        base_pts + [(cbx + 12, cby + 4), (cbx - 13, cby + 4)])
    for dx, dy, bow, t in sorted(crest, key=lambda p: p[1]):
        path = wisp_path(dx, dy, bow)
        col = _aurora_mix(t)
        base = _aurora_mix(max(0.0, t - 0.18))      # warmer/greener at the hot base
        pygame.draw.lines(det, _INK, False, path, 4)
        pygame.draw.lines(det, base, False, path[:len(path) // 2], 3)
        pygame.draw.lines(det, col, False, path[len(path) // 2 - 1:], 2)
        pygame.draw.circle(det, base, (int(path[0][0]), int(path[0][1])), 2)

    # Aurora RIBBON tail — wide green→magenta curtains: a soft translucent band
    # filling between the spine and an offset edge, a 4px ink backing and a 3px
    # bright spine, ending in a glint. The S-curve + width make it read as flowing
    # aurora, the lower silhouette break that sells the legendary.
    for k in range(3):
        path = ribbon_path(k)
        col = _aurora_mix(k / 2.0)
        edge = [(x, y + 4 + k) for x, y in path]    # widen into a band
        pygame.draw.polygon(det, (*col, 120), path + edge[::-1])
        pygame.draw.lines(det, _INK, False, path, 5)
        pygame.draw.lines(det, col, False, path, 3)
        pygame.draw.circle(det, _AUR_GLINT, (int(path[-1][0]), int(path[-1][1])), 2)

    surf.blit(det, (0, 0))


def _aurora_front(surf, angle_deg):
    """Painted OVER the body and INSIDE the masked layer, so only crisp opaque
    detail belongs here (soft glow lives in _aurora_back to dodge the outline):
    a ≥2px aurora rim-light wrapping the full back+belly edge, the crown-band
    blended into the crest's hot base, a re-asserted face, and star flecks
    crowded onto the LIT edge. These survive the downscale as hard pixels."""
    # Aurora rim-light wrapping the WHOLE silhouette — a ≥2px teal/blue band over
    # the back+crown and a green band under the belly, so the lifted indigo body
    # is framed by light rather than reading as a flat void on either sky.
    pygame.draw.lines(surf, _AUR_STARBLU, False,
                      [(HX - 12, CROWN_Y + 3), (HX - 5, CROWN_Y - 1),
                       (HX + 4, CROWN_Y), (HX + 12, HY - 3)], 2)
    pygame.draw.lines(surf, _AUR_STARBLU, False,
                      [(16, 46), (15, 52), (18, 40)], 2)            # back-of-body edge
    # Lit belly rim — a MONOTONIC descending diagonal, never a U, so it can't
    # close into a mouth. Broken into a bright fore-segment + a faint aft-segment
    # so the eye reads two rim glints, not a smile line, at 40px.
    pygame.draw.lines(surf, _AUR_GREEN, False,
                      [(46, 56), (43, 60), (39, 63)], 2)            # bright fore rim, descending
    pygame.draw.lines(surf, _AUR_GREEN, False,
                      [(34, 65), (28, 67), (22, 67)], 1)            # faint aft rim, still dropping

    # Crown-band ↔ crest blend: a short green→magenta wash where the crown meets
    # the plume root, so the headband stripe dissolves into the crest's cosmic
    # base instead of reading as a separate stripe.
    for i in range(5):
        t = i / 4.0
        cx = HX - 6 + i * 3
        pygame.draw.circle(surf, _aurora_mix(0.15 + t * 0.6), (cx, CROWN_Y + 3), 2)

    # Re-assert Pip's face at 40px: a bright specular glint on the near lens and
    # a sharpened beak edge so the macaw identity survives the downscale.
    pygame.draw.circle(surf, _AUR_GLINT, (HX + 6, HY - 3), 2)
    pygame.draw.line(surf, _AUR_GLINT, (HX + 8, HY + 1), (HX + 13, HY + 4), 2)  # beak top edge

    # Star flecks CROWDED on the lit back/upper edge (where they catch the rim
    # light) — a fixed scatter (NOT random, so frames are stable) of small
    # white/blue twinkles. Off the face/shadow so the eyes stay clean.
    stars = (
        (24, 42, 1, _AUR_GLINT),
        (20, 40, 1, _AUR_STARBLU),
        (28, 38, 1, _AUR_GLINT),
        (34, 40, 1, _AUR_STARBLU),
        (18, 45, 1, _AUR_GLINT),
        (30, 44, 1, _AUR_STARBLU),
        (39, 43, 1, _AUR_GLINT),
    )
    for sx, sy, r, col in stars:
        pygame.draw.circle(surf, col, (sx, sy), r)
        if col is _AUR_GLINT:              # only the brightest get a twinkle cross
            pygame.draw.line(surf, (*col, 160), (sx - 2, sy), (sx + 2, sy), 1)
            pygame.draw.line(surf, (*col, 160), (sx, sy - 2), (sx, sy + 2), 1)


def _aurora_getter():
    """back aura (halo + ribbons) → galaxy body → front nebula/stars/rim →
    house outline, then the per-(frame, 3°-bucket) rotation cache shared by every
    store skin. The faint additive halo + ribbons must NOT be part of the masked
    layer (else the dark outline would wrap the glow and kill it), so the OPAQUE
    bird (body + front overlay) is outlined alone and the soft back-aura is laid
    UNDER it, padded to match the outline's 2px grow so the bird stays centred."""
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        bird = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        bird.blit(_aurora_base(wing_angle), (0, PARROT_DY))
        _aurora_front(bird, wing_angle)
        bird = _add_outline(bird)

        aura = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
        pad = (bird.get_width() - COMPOSITE_W) // 2
        back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _aurora_back(back, wing_angle)
        aura.blit(back, (pad, pad))
        aura.blit(bird, (0, 0))
        return aura

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_flat(a) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


get_aurora_macaw = _aurora_getter()


# ─────────────────────────────────────────────────────────────────────────────
# THORNCREST MACAW (epic) — botanical parrot: rose-red body, briar-vine crest
# with ivory thorns and a bloomed heraldic rose past the crown. Matte pigment,
# no glow — warmth from saturated local colour only, never emission.
# ─────────────────────────────────────────────────────────────────────────────
_TC_ROSE    = (181, 41, 74)
_TC_ROSE_HI = (205, 52, 88)
_TC_WINE    = (122, 23, 48)
_TC_BLUSH   = (242, 182, 196)
_TC_GREEN   = (47, 107, 58)
_TC_GREEN_D = (30, 72, 40)
_TC_GREEN_H = (104, 168, 96)
_TC_IVORY   = (239, 231, 210)
_TC_CRIMSON = (200, 38, 66)

P_THORNCREST = _pal(
    tail=[(96, 20, 42), (140, 30, 58), (176, 46, 76), (206, 96, 118)],
    tail_line=_TC_WINE,
    body_shadow=(132, 30, 56),
    body_main=_TC_ROSE_HI,
    body_chest=(222, 122, 144),
    body_belly=_TC_BLUSH,
    sheen=(255, 224, 230, 130),
    wing_main=(188, 46, 82),
    wing_dark=(110, 24, 46),
    wing_tip=(228, 156, 174),
    wing_secondary=None,
    wing_highlight=(238, 188, 200),
    head_shadow=(132, 30, 56),
    head_main=_TC_ROSE_HI,
    head_cheek=(220, 130, 150),
    head_crown=(206, 80, 108),
    lens_frame=(214, 132, 110),
    lens_body=(58, 24, 30),
    lens_tint=(232, 150, 120, 130),
    lens_glint=(255, 244, 230),
    beak_main=(228, 160, 150),
    beak_dark=(150, 70, 60),
    beak_gloss=(255, 244, 232),
    foot=(150, 70, 64),
)


def _tc_thorn(surf, bx, by, dx, dy):
    if abs(dx) >= abs(dy):
        b0, b1 = (bx, by - 3), (bx, by + 3)
    else:
        b0, b1 = (bx - 3, by), (bx + 3, by)
    tip = (bx + dx, by + dy)
    sx = 1 if dx >= 0 else -1
    sy = 1 if dy >= 0 else -1
    pygame.draw.polygon(surf, _TC_GREEN_D,
                        [(b0[0] + sx, b0[1] + sy), (b1[0] + sx, b1[1] + sy),
                         (tip[0] + sx, tip[1] + sy)])
    pygame.draw.polygon(surf, _TC_IVORY, [b0, b1, tip])
    pygame.draw.line(surf, _TC_WINE, b0, tip, 1)


def _tc_leaf(surf, cx, cy, dx, dy):
    tip = (cx + dx, cy + dy)
    base = (cx - dx // 2, cy - dy // 2)
    side = (cx + dy // 2, cy - dx // 2)
    side2 = (cx - dy // 2, cy + dx // 2)
    pygame.draw.polygon(surf, _TC_GREEN, [base, side, tip, side2])
    pygame.draw.line(surf, _TC_GREEN_H, base, side, 1)
    pygame.draw.line(surf, _TC_GREEN_D, base, tip, 1)


def _tc_bloom(surf, cx, cy):
    petals = (
        (cx, cy - 6, 4), (cx + 6, cy - 2, 4), (cx + 4, cy + 5, 4),
        (cx - 4, cy + 5, 4), (cx - 6, cy - 2, 4),
    )
    for px, py, r in petals:
        pygame.draw.circle(surf, _TC_CRIMSON, (px, py), r)
        pygame.draw.circle(surf, _TC_WINE, (px, py), r, 1)
    pygame.draw.circle(surf, _TC_BLUSH, (cx - 4, cy - 4), 3)
    pygame.draw.circle(surf, _TC_WINE, (cx - 4, cy - 4), 3, 1)
    pygame.draw.circle(surf, _TC_WINE, (cx, cy), 3)
    pygame.draw.circle(surf, _TC_CRIMSON, (cx, cy), 2)
    pygame.draw.circle(surf, _TC_IVORY, (cx - 1, cy - 1), 1)


def _paint_thorncrest(surf, _a):
    wrap = [(38, 43), (33, 46)]
    pygame.draw.lines(surf, _TC_WINE, False, wrap, 5)
    pygame.draw.lines(surf, _TC_GREEN_D, False, wrap, 4)
    pygame.draw.lines(surf, _TC_GREEN, False, wrap, 2)
    _tc_leaf(surf, 36, 44, 3, -4)
    _tc_leaf(surf, 35, 47, -2, 4)
    edge = [(44, 40), (40, 37), (35, 35)]
    pygame.draw.lines(surf, _TC_WINE, False, edge, 3)
    pygame.draw.lines(surf, _TC_GREEN, False, edge, 2)
    for tx, ty in edge:
        pygame.draw.line(surf, _TC_IVORY, (tx, ty), (tx - 2, ty - 2), 1)
    _tc_leaf(surf, 52, 39, 2, -3)
    # briar-cane crest: root emerges from back of skull, arches up-back, rose caps
    cane = [
        (HX - 6, CROWN_Y + 4), (HX - 9, CROWN_Y - 1),
        (HX - 12, CROWN_Y - 6), (HX - 14, CROWN_Y - 9),
    ]
    bloom_c = (HX - 16, CROWN_Y - 13)
    pygame.draw.lines(surf, _TC_WINE, False, cane, 6)
    pygame.draw.lines(surf, _TC_GREEN_D, False, cane, 5)
    pygame.draw.lines(surf, _TC_GREEN, False, cane, 3)
    pygame.draw.lines(surf, _TC_GREEN_H, False, cane[:2], 1)
    _tc_thorn(surf, HX - 10, CROWN_Y - 2, -5, -3)
    _tc_thorn(surf, HX - 13, CROWN_Y - 7, -5, -1)
    _tc_bloom(surf, *bloom_c)


get_thorncrest_macaw = _make_skin(
    _paint_thorncrest,
    base_fn=lambda a: _build_parrot_with_palette(a, P_THORNCREST))


# ─────────────────────────────────────────────────────────────────────────────
# MOONBLOOM MACAW (legendary) — night-flora: pearl-white/lilac body, opened
# moonflower crest, pale-gold moon-disc halo behind the head, petal-streamer
# tail with pollen-motes. AURORA pattern: back halo/tail → body → front crest
# → outline → rotation cache. Hard opaque detail carries the day read; additive
# glow carries night.
# ─────────────────────────────────────────────────────────────────────────────
_MB_PEARL     = (243, 238, 248)
_MB_PEARL_HL  = (252, 250, 254)
_MB_LILAC     = (185, 168, 214)
_MB_LILAC_DK  = (122, 104, 166)
_MB_MINT      = (224, 240, 232)
_MB_MOONGOLD  = (246, 230, 168)
_MB_DEEPLILAC = (130, 112, 174)
_MB_VIOLET    = (198, 184, 224)
_MB_GLINT     = (255, 255, 255)
_MB_OUTLINE   = (56, 42, 80, 235)
_MB_PETAL_HI  = (250, 247, 252)
_MB_PETAL_LO  = (188, 170, 214)
_MB_POLLEN_HI = (255, 247, 200)

P_MOONBLOOM = _pal(
    tail=[(176, 158, 204), (196, 180, 220), (218, 206, 234), (240, 234, 248)],
    tail_line=_MB_DEEPLILAC,
    body_shadow=_MB_LILAC_DK,
    body_main=_MB_PEARL,
    body_chest=(252, 250, 254),
    body_belly=(200, 184, 222),
    sheen=(228, 240, 234, 110),
    wing_main=(214, 202, 230),
    wing_dark=_MB_LILAC_DK,
    wing_tip=(248, 244, 252),
    wing_secondary=None,
    wing_highlight=_MB_PEARL_HL,
    head_shadow=_MB_LILAC,
    head_main=_MB_PEARL,
    head_cheek=(250, 246, 252),
    head_crown=_MB_PEARL_HL,
    lens_frame=(140, 124, 180),
    lens_body=(70, 58, 100),
    lens_tint=(198, 184, 224, 150),
    lens_glint=(250, 248, 254),
    beak_main=(238, 220, 168),
    beak_dark=(170, 144, 92),
    beak_gloss=(252, 242, 206),
    foot=(170, 152, 196),
)


def _mb_flap_phase(angle_deg):
    return 1.0 - (angle_deg + 40) / 90.0


def _mb_smooth_curve(p0, p1, p2, steps=10):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def _mb_petal_poly(tip, root, width, curve=0.0, blunt=0.0):
    import math as _math
    dx, dy = tip[0] - root[0], tip[1] - root[1]
    length = _math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    mid = (root[0] + dx * 0.5 + px * curve, root[1] + dy * 0.5 + py * curve)
    spine = _mb_smooth_curve(root, mid, tip, steps=8)
    left, right = [], []
    n = len(spine) - 1
    for i, (sx, sy) in enumerate(spine):
        t = i / n
        if t < 0.30:
            w = width * (t / 0.30) ** 0.7
        else:
            tt = (t - 0.30) / 0.70
            point = _math.sin((1 - tt) * _math.pi / 2)
            blunt_w = 1.0 - tt * tt * 0.35
            w = width * (point * (1 - blunt) + blunt_w * blunt)
        left.append((sx + px * w, sy + py * w))
        right.append((sx - px * w, sy - py * w))
    if blunt > 0.4:
        cap = []
        tipw = width * (1.0 - 0.35) * blunt
        for k in range(5):
            a = _math.pi * (k / 4)
            cap.append((tip[0] + px * _math.cos(a) * tipw - ux * _math.sin(a) * tipw,
                        tip[1] + py * _math.cos(a) * tipw - uy * _math.sin(a) * tipw))
        return left + cap + right[::-1], spine
    return left + right[::-1], spine


def _mb_streamer_geo(angle_deg):
    phase = _mb_flap_phase(angle_deg)
    droop = (1.0 - phase) * 3
    reach = 1.0 + phase * 0.12
    troot = (17, HY + 8)
    spec = ((-40, 27, -5), (-26, 32, 1), (-13, 26, 6))
    out = []
    import math as _math
    for ang_deg, length, bow in spec:
        a = _math.radians(150 + ang_deg)
        tip = (troot[0] + _math.cos(a) * length * reach,
               troot[1] + _math.sin(a) * length * reach + droop)
        poly, spine = _mb_petal_poly(tip, troot, 4.2, curve=bow)
        out.append((poly, spine, tip))
    return out


def _mb_pollen_motes(angle_deg):
    phase = _mb_flap_phase(angle_deg)
    drift = phase * 4
    base = ((-6, HY + 26, 2), (-12, HY + 20, 2), (-16, HY + 33, 1), (-3, HY + 36, 1))
    return [(x - drift, y + drift * 0.4, r) for x, y, r in base]


def _mb_petal_mix(t):
    return lerp_color(_MB_PETAL_HI, _MB_PETAL_LO, t)


def _moonbloom_back(surf, angle_deg):
    import math as _math
    streamers = _mb_streamer_geo(angle_deg)
    motes = _mb_pollen_motes(angle_deg)
    hcx, hcy = HX - 1, HY - 2
    moon_r = 20
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    blit_glow(glow, hcx, hcy, 18, _MB_MOONGOLD, alpha=70)
    blit_glow(glow, hcx, hcy, 12, (255, 248, 220), alpha=60)
    for i in range(12):
        a = _math.radians(i * 30)
        blit_glow(glow, int(hcx + _math.cos(a) * moon_r),
                  int(hcy + _math.sin(a) * moon_r), 6, _MB_MOONGOLD, alpha=70)
    for poly, spine, tip in streamers:
        for sp in (spine[len(spine) // 2], spine[-1]):
            blit_glow(glow, int(sp[0]), int(sp[1]), 6, (236, 226, 248), alpha=85)
        blit_glow(glow, int(tip[0]), int(tip[1]), 5, _MB_MINT, alpha=80)
    for mx, my, r in motes:
        blit_glow(glow, int(mx), int(my), 4 + r, _MB_MOONGOLD, alpha=110)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)
    det = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for poly, spine, tip in streamers:
        pygame.draw.polygon(det, _MB_DEEPLILAC, poly)
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        field = [(cx + (x - cx) * 0.74, cy + (y - cy) * 0.80) for x, y in poly]
        pygame.draw.polygon(det, _MB_PETAL_LO, field)
        pygame.draw.lines(det, _MB_PETAL_HI, False, spine, 2)
        pygame.draw.circle(det, _MB_MINT, (int(tip[0]), int(tip[1])), 2)
        pygame.draw.circle(det, _MB_GLINT, (int(tip[0]), int(tip[1])), 1)
    pygame.draw.circle(det, (250, 240, 200, 90), (hcx, hcy), moon_r - 2)
    pygame.draw.circle(det, (255, 248, 214, 200), (hcx, hcy), moon_r + 1, 3)
    pygame.draw.circle(det, _MB_MOONGOLD, (hcx, hcy), moon_r, 2)
    for fa in (_math.radians(196), _math.radians(212),
               _math.radians(328), _math.radians(344)):
        bx = int(hcx + _math.cos(fa) * moon_r)
        by = int(hcy + _math.sin(fa) * moon_r)
        pygame.draw.circle(det, (255, 250, 224), (bx, by), 2)
        pygame.draw.circle(det, _MB_GLINT, (bx, by), 1)
    for mx, my, r in motes:
        pygame.draw.circle(det, _MB_MOONGOLD, (int(mx), int(my)), r + 1)
        pygame.draw.circle(det, _MB_POLLEN_HI, (int(mx), int(my)), r)
    surf.blit(det, (0, 0))


def _moonbloom_front(surf, angle_deg):
    import math as _math
    base_y = CROWN_Y + 2
    cbx = HX - 1
    petals = (
        (-9, -19, -5, 0.10), (-4, -25, -2, 0.32), (0, -29, 0, 0.50),
        (4, -25, 2, 0.68), (9, -19, 5, 0.90),
    )
    drawn = []
    for dx, dy, bow, t in petals:
        tip = (cbx + dx, base_y + dy)
        root = (cbx + dx * 0.22, base_y + 1)
        poly, spine = _mb_petal_poly(tip, root, 5.2, curve=bow, blunt=0.85)
        drawn.append((poly, spine, tip, t))
    for poly, spine, tip, t in sorted(drawn, key=lambda p: p[2][1], reverse=True):
        pygame.draw.polygon(surf, _MB_DEEPLILAC, poly)
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        field = [(cx + (x - cx) * 0.80, cy + (y - cy) * 0.84) for x, y in poly]
        pygame.draw.polygon(surf, _mb_petal_mix(t * 0.5), field)
        rim = spine[len(spine) // 2:]
        pygame.draw.lines(surf, _MB_MOONGOLD, False, rim, 2)
        pygame.draw.circle(surf, _MB_MOONGOLD, (int(tip[0]), int(tip[1])), 2)
        pygame.draw.circle(surf, _MB_PETAL_HI, (int(tip[0]), int(tip[1])), 1)
    px, py = cbx, base_y - 2
    pygame.draw.circle(surf, _MB_MOONGOLD, (px, py), 4)
    pygame.draw.circle(surf, _MB_POLLEN_HI, (px, py), 3)
    pygame.draw.circle(surf, _MB_GLINT, (px - 1, py - 1), 1)
    for a in range(0, 360, 60):
        r = _math.radians(a)
        pygame.draw.circle(surf, (255, 240, 180),
                           (int(px + _math.cos(r) * 4), int(py + _math.sin(r) * 4)), 1)
    pygame.draw.lines(surf, _MB_MINT, False,
                      [(HX - 12, CROWN_Y + 4), (HX - 5, CROWN_Y),
                       (HX + 4, CROWN_Y + 1), (HX + 12, HY - 3)], 2)
    pygame.draw.lines(surf, _MB_MINT, False, [(16, 46), (15, 52), (18, 40)], 2)
    pygame.draw.lines(surf, _MB_LILAC, False, [(46, 56), (43, 60), (39, 63)], 2)
    pygame.draw.lines(surf, _MB_LILAC, False, [(34, 65), (28, 67), (22, 67)], 1)
    veins = (
        ((23, 41), (28, 38)), ((27, 44), (33, 41)), ((31, 47), (38, 44)),
        ((20, 44), (24, 42)), ((35, 45), (41, 43)),
    )
    for a, b in veins:
        pygame.draw.line(surf, (*_MB_DEEPLILAC, 150), a, b, 1)
    for sx, sy in ((26, 40), (32, 43), (38, 42)):
        pygame.draw.circle(surf, (236, 230, 246), (sx, sy), 1)
    ex, ey = HX + 6, HY - 2
    pygame.draw.line(surf, _MB_VIOLET, (ex - 6, ey - 4), (ex + 5, ey - 5), 2)
    pygame.draw.line(surf, (120, 104, 158), (ex - 5, ey + 4), (ex + 4, ey + 4), 1)
    pygame.draw.circle(surf, _MB_GLINT, (ex, ey - 1), 2)
    pygame.draw.circle(surf, _MB_VIOLET, (ex - 3, ey + 1), 1)
    pygame.draw.line(surf, _MB_PETAL_HI, (HX + 8, HY + 1), (HX + 13, HY + 4), 2)


def _moonbloom_getter():
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        bird = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        bird.blit(_build_parrot_with_palette(wing_angle, P_MOONBLOOM), (0, PARROT_DY))
        _moonbloom_front(bird, wing_angle)
        bird = _add_outline(bird, outline_color=_MB_OUTLINE)
        aura = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
        pad = (bird.get_width() - COMPOSITE_W) // 2
        back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _moonbloom_back(back, wing_angle)
        aura.blit(back, (pad, pad))
        aura.blit(bird, (0, 0))
        return aura

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_flat(a) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


get_moonbloom_macaw = _moonbloom_getter()


# ─────────────────────────────────────────────────────────────────────────────
# CHROME MACAW (secret) — mirror-polished Pip: no local hue, every "colour"
# is a hard specular reflection ramp (dark steel → mid chrome → white hotspot).
# Oil-slick holo ring behind the head, swept chrome fin-crest, bladed tail-
# vanes, travelling wing hotspot, mirror-chrome aviators. AURORA pattern:
# back holo/vanes → chrome body → front spec/panels/crest/lenses → outline
# → rotation cache.
# ─────────────────────────────────────────────────────────────────────────────
_CR_STEEL  = (58, 66, 80)
_CR_MID    = (143, 166, 190)
_CR_HOT    = (232, 242, 250)
_CR_SPEC   = (255, 255, 255)
_CR_IRID_C = (124, 240, 224)
_CR_IRID_M = (255, 138, 216)
_CR_INK    = (26, 30, 40)
_CR_RIM    = (214, 230, 245)

P_CHROME = _pal(
    tail=[(72, 82, 98), (96, 110, 130), (136, 158, 182), (188, 208, 226)],
    tail_line=(50, 56, 70),
    body_shadow=(76, 86, 102),
    body_main=(106, 122, 144),
    body_chest=(178, 200, 222),
    body_belly=(96, 110, 130),
    sheen=(150, 200, 245, 180),
    wing_main=(98, 112, 134),
    wing_dark=(70, 80, 96),
    wing_tip=(206, 224, 240),
    wing_secondary=None,
    wing_highlight=(244, 250, 255),
    head_shadow=(74, 84, 100),
    head_main=(114, 132, 156),
    head_cheek=(172, 194, 216),
    head_crown=(212, 230, 244),
    lens_frame=(150, 168, 190),
    lens_body=(30, 36, 48),
    lens_tint=None,
    lens_glint=None,
    beak_main=(154, 174, 196),
    beak_dark=(72, 82, 98),
    beak_gloss=(244, 250, 255),
    foot=(130, 148, 170),
)


def _cr_oil_mix(t):
    s = 1.0 - abs(2.0 * t - 1.0)
    return lerp_color(_CR_IRID_M, _CR_IRID_C, s)


def _cr_flap_phase(angle_deg):
    return 1.0 - (angle_deg + 40) / 90.0


def _cr_arc(cx, cy, r, a0, a1, steps=20):
    import math as _math
    return [(cx + _math.cos(a0 + (a1 - a0) * i / steps) * r,
             cy + _math.sin(a0 + (a1 - a0) * i / steps) * r)
            for i in range(steps + 1)]


def _chrome_back(surf, angle_deg):
    import math as _math
    phase = _cr_flap_phase(angle_deg)
    sway = (phase - 0.5) * 3
    hcx, hcy = HX - 2, HY - 4
    ring_rx, ring_ry = 21, 13
    ring = [(hcx + _math.cos(a) * ring_rx, hcy + _math.sin(a) * ring_ry)
            for a in [_math.radians(d) for d in range(0, 361, 12)]]
    vroot = (15, HY + 9)
    vanes = (
        (-22, 23, 4, 0.10, True), (-27, 14, 5, 0.32, True),
        (-28, 5,  5, 0.55, False), (-24, -3, 4, 0.78, False),
        (-17, -9, 3, 1.00, False),
    )

    def vane_poly(dx, dy, hw):
        tip = (vroot[0] + dx, vroot[1] + dy + sway)
        return [
            (vroot[0] + 2, vroot[1] - hw), (tip[0], tip[1] - 1),
            (tip[0] - 1, tip[1] + 1), (vroot[0], vroot[1] + hw),
        ], tip

    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for i, (gx, gy) in enumerate(ring):
        blit_glow(glow, int(gx), int(gy), 5, _cr_oil_mix((i % 12) / 12.0), alpha=90)
    for dx, dy, hw, t, hard in vanes:
        _, tip = vane_poly(dx, dy, hw)
        blit_glow(glow, int(tip[0]), int(tip[1]), 5, _cr_oil_mix(t), alpha=85)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)
    det = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for dx, dy, hw, t, hard in sorted(vanes, key=lambda v: -abs(v[1])):
        poly, tip = vane_poly(dx, dy, hw)
        _poly(det, _CR_INK, [(x - 1, y + 1) for x, y in poly])
        if hard:
            _poly(det, _CR_STEEL, poly)
            _poly(det, _CR_MID, [poly[0], poly[1], tip])
        else:
            _poly(det, _CR_MID, poly)
        pygame.draw.line(det, _CR_SPEC, (vroot[0] + 2, vroot[1] - hw + 1),
                         (tip[0], tip[1] - 1), 2)
        pygame.draw.circle(det, _cr_oil_mix(t), (int(tip[0]), int(tip[1])), 1)
    pygame.draw.lines(det, _CR_INK, True, ring, 4)
    for i in range(len(ring) - 1):
        seg = _cr_oil_mix((i % 12) / 12.0)
        pygame.draw.line(det, seg, ring[i], ring[i + 1], 2)
    pygame.draw.circle(det, _CR_SPEC, (int(ring[8][0]), int(ring[8][1])), 2)
    pygame.draw.circle(det, _CR_SPEC, (int(ring[24][0]), int(ring[24][1])), 1)
    surf.blit(det, (0, 0))


def _chrome_front(surf, angle_deg):
    import math as _math
    phase = _cr_flap_phase(angle_deg)
    sway = int(round((phase - 0.5) * 3))
    blades = (
        (HX + 4, CROWN_Y + 1, HX - 9 + sway, CROWN_Y - 21),
        (HX + 7, CROWN_Y + 2, HX - 3 + sway, CROWN_Y - 16),
        (HX + 9, CROWN_Y + 4, HX + 3 + sway, CROWN_Y - 10),
    )
    for rx, ry, tx, ty in blades:
        body = [(rx - 3, ry), (rx + 3, ry), (tx + 1, ty + 1), (tx, ty)]
        _poly(surf, _CR_INK, [(x - 1, y) for x, y in body])
        _poly(surf, _CR_STEEL, body)
        _poly(surf, _CR_MID, [(rx - 2, ry), (rx + 1, ry), (tx, ty)])
        pygame.draw.line(surf, _CR_SPEC, (rx - 2, ry - 1), (tx - 1, ty + 1), 2)
        pygame.draw.circle(surf, _CR_SPEC, (int(tx), int(ty)), 1)
    pygame.draw.line(surf, _CR_SPEC, (HX - 6, HY - 9), (HX + 6, HY - 11), 2)
    pygame.draw.line(surf, _CR_STEEL, (HX - 6, HY - 6), (HX + 7, HY - 8), 2)
    pygame.draw.line(surf, _CR_SPEC, (24, 46), (38, 43), 3)
    pygame.draw.line(surf, _CR_STEEL, (24, 51), (40, 49), 2)
    hx0 = 28 + int(round(phase * 10))
    pygame.draw.line(surf, _CR_SPEC, (hx0, 38), (hx0 + 12, 35), 2)
    pygame.draw.line(surf, _CR_HOT, (hx0 - 1, 41), (hx0 + 11, 38), 1)
    pygame.draw.line(surf, _CR_STEEL, (hx0 - 1, 43), (hx0 + 11, 40), 1)
    seams = (
        [(40, 44), (33, 48), (24, 50)],
        [(20, 44), (18, 50), (22, 56)],
        [(34, 56), (28, 58), (22, 57)],
    )
    for s in seams:
        pygame.draw.lines(surf, _CR_INK, False, s, 2)
        pygame.draw.lines(surf, (188, 206, 226), False, s, 1)
    for rx, ry in ((39, 45), (35, 47), (22, 47)):
        pygame.draw.circle(surf, _CR_STEEL, (rx, ry), 2)
        pygame.draw.circle(surf, _CR_SPEC, (rx - 1, ry - 1), 1)
    if phase > 0.66:
        pygame.draw.circle(surf, _CR_SPEC, (38, 44), 2)
        pygame.draw.circle(surf, _CR_IRID_C, (38, 44), 1)
    pygame.draw.lines(surf, _CR_RIM, False,
                      [(16, 53), (21, 58), (29, 61), (38, 61), (45, 57)], 2)
    cx, cy = 50, HY - 1
    L = (cx - 4, cy)
    R = (cx + 6, cy - 1)
    r = 6
    for c in (L, R):
        pygame.draw.circle(surf, _CR_MID, c, r + 1)
        pygame.draw.circle(surf, _CR_STEEL, c, r)
        pygame.draw.arc(surf, (110, 170, 220), (c[0] - r, c[1] - r, 2 * r, 2 * r),
                        _math.radians(20), _math.radians(160), 3)
        pygame.draw.circle(surf, _CR_SPEC, (c[0] - 2, c[1] - 2), 2)
        pygame.draw.line(surf, _CR_IRID_C, (c[0] - 3, c[1] + 2), (c[0] + 1, c[1] + 3), 1)
        pygame.draw.line(surf, _CR_IRID_M, (c[0] + 1, c[1] + 3), (c[0] + 3, c[1] + 2), 1)
    pygame.draw.line(surf, _CR_MID, (L[0] + r, L[1]), (R[0] - r, R[1]), 2)
    pygame.draw.line(surf, _CR_HOT,
                     (L[0] - r + 1, L[1] - r + 2), (R[0] + r - 1, R[1] - r + 2), 1)
    pygame.draw.line(surf, _CR_SPEC, (55, 41), (59, 43), 1)


def _chrome_getter():
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        bird = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        bird.blit(_build_parrot_with_palette(wing_angle, P_CHROME, draw_lenses=False),
                  (0, PARROT_DY))
        _chrome_front(bird, wing_angle)
        bird = _add_outline(bird)
        out = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
        pad = (bird.get_width() - COMPOSITE_W) // 2
        back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _chrome_back(back, wing_angle)
        out.blit(back, (pad, pad))
        out.blit(bird, (0, 0))
        return out

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_flat(a) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


get_chrome_macaw = _chrome_getter()


# ─────────────────────────────────────────────────────────────────────────────
# Production registry: catalog id -> getter. Consulted by
# parrot.get_skin_frame (which checks this first, so the three redraws here
# override the power-up-sprite mappings the base parrot keeps for buff use).
# Keys must mirror the "skin"-kind ids in game.store_catalog.
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "skin_pirate":    get_pirate_parrot,
    "skin_ninja":     get_ninja_parrot,
    "skin_wizard":    get_wizard_parrot,
    "skin_astronaut": get_astronaut_parrot,
    "skin_pharaoh":   get_pharaoh_parrot,
    "skin_viking":    get_viking_parrot,
    "skin_cowboy":    get_cowboy_parrot,
    "skin_disco":     get_disco_parrot,
    "skin_crown":     get_crown_parrot,
    # Dedicated cosmetic redraws (override the recycled power-up sprites).
    "skin_tophat":    get_tophat_redraw,
    "skin_zombie":    get_zombie_redraw,
    # Parrot species (full-body recolours + cockatoo crest).
    "skin_bluegold":  get_bluegold_parrot,
    "skin_amazon":    get_amazon_parrot,
    "skin_sunconure": get_sunconure_parrot,
    "skin_hyacinth":  get_hyacinth_parrot,
    "skin_cockatoo":  get_cockatoo_parrot,
    "skin_lorikeet":  get_lorikeet_parrot,
    # Rarity-tier parrots (epic crystal, legendary aurora).
    "skin_prism":     get_prism_lorikeet,
    "skin_aurora":    get_aurora_macaw,
    # Wave 2 rarity parrots (epic botanical, legendary night-flora, secret chrome).
    "skin_thorncrest": get_thorncrest_macaw,
    "skin_moonbloom":  get_moonbloom_macaw,
    "skin_chrome":     get_chrome_macaw,
}
