"""BURLAP SACK parcel cosmetic (LOW tier).

A cinched-neck burlap loot sack: a fat onion/teardrop body bulging at the
BOTTOM, pinched HARD to a tied NECK so the silhouette has a visible WAIST
(not a stub on a ball), capped by a small COMPACT rounded knot. The only
soft, organic, non-boxy shape in the low tier. Built at 2x then smoothscaled
so the curved outline + cinch survive the 22px read and the tilt rotation.
"""
import math
import pygame

from game.parrot import _lerp_color

PARCEL_SIZE = 22

# DAY-anchored burlap palette. The body gradient runs tan -> base shadow so
# the bag reads as a weighted, full sack rather than a flat blob.
TAN_TOP   = (201, 163, 107)   # #C9A36B lit upper body
TAN_BASE  = (140, 106,  58)   # #8C6A3A darker base shadow at the bottom bulge
TAN_WEAVE = (162, 126,  72)   # #A27E48 mid value for the horizontal weave break-up
CORD      = ( 84,  62,  32)   # #543E20 dark tie-cord at the neck
KEYLINE   = (232, 201, 138)   # #E8C98A warm rim so brown survives NIGHT sky
OUTLINE   = ( 38,  26,  12)   # dark high-value bake to read on bright day sky


def _onion_points(cx, neck_y, base_y, half_w, neck_half):
    """Teardrop/onion outline with a HARD cinch: the profile pinches sharply
    in toward `neck_half` at the neck (t=0) then swells to a wide rounded
    bottom belly. The sharp pinch is what gives a visible waist so the shape
    is a tied sack, not a coconut. Sampled as a closed mirrored polygon so the
    curve stays smooth after the 2x->1x downscale and stays a bag rotated."""
    pts_r = []
    span = base_y - neck_y
    for i in range(0, 25):
        t = i / 24.0
        y = neck_y + t * span
        # Width profile: pinched at the neck (t=0), bulging low (t~0.62),
        # tucking back to a rounded base (t=1). The high exponent on the early
        # ramp makes the cinch snap in fast so the waist is unmistakable.
        bulge = math.sin(t * math.pi * 0.86 + 0.16)
        # Sharp early ramp gives the cinch a hard waist; the gentler exponent
        # keeps the belly a rounded onion rather than a sharp diamond equator.
        ramp = bulge ** 1.25 if t < 0.32 else bulge ** 0.92
        w = neck_half + (half_w - neck_half) * ramp
        pts_r.append((cx + w, y))
    # Rounded bottom cap, then mirror the right edge back up the left side.
    pts = pts_r + [(p[0] - 2 * (p[0] - cx), p[1]) for p in reversed(pts_r)]
    return pts


def build(mode: str = "normal") -> pygame.Surface:
    # `mode` is ignored — the cosmetic keeps one look across all power-ups.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # The neck sits LOW relative to the body so the cinch carves a waist into
    # the silhouette rather than perching on top of a sphere; the knot above is
    # kept short + compact so high tilt never elongates it into a gourd stem.
    neck_y = 14
    base_y = 40
    half_w = 16
    neck_half = 3

    body = _onion_points(cx, neck_y, base_y, half_w, neck_half)

    # Soft contact shadow under the heavy bottom bulge.
    sh = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 5, 2, 120), pygame.Rect(cx - 16, base_y - 5, 32, 11))
    surf.blit(sh, (0, 0))

    # Outline bake: draw the body polygon fattened in OUTLINE first, then the
    # fill on top. A single bold dark edge is what carries the 22px read.
    body_cy = (neck_y + base_y) / 2
    out_pts = []
    for x, y in body:
        dx, dy = x - cx, y - body_cy
        d = math.hypot(dx, dy) or 1
        out_pts.append((x + dx / d * 1.8, y + dy / d * 1.8))
    pygame.draw.polygon(surf, OUTLINE, out_pts)

    # Body fill via a vertical tan->base gradient, masked to the onion shape.
    grad = pygame.Surface((S, S), pygame.SRCALPHA)
    for y in range(neck_y - 2, base_y + 3):
        t = (y - neck_y) / max(1, base_y - neck_y)
        col = _lerp_color(TAN_TOP, TAN_BASE, max(0.0, min(1.0, t))) + (255,)
        grad.fill(col, pygame.Rect(0, y, S, 1))
    mask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), body)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Burlap break-up: one faint horizontal weave band across the mid-belly so
    # the body isn't a smooth ceramic/coconut sphere. Two thin value lines
    # (one darker, one lighter) suggest woven cloth without any fine stitching.
    weave_y = int(neck_y + (base_y - neck_y) * 0.5)
    grad.fill(TAN_WEAVE + (150,), pygame.Rect(0, weave_y, S, 1),
              special_flags=pygame.BLEND_RGBA_MIN)
    grad.fill(TAN_WEAVE + (110,), pygame.Rect(0, weave_y + 3, S, 1),
              special_flags=pygame.BLEND_RGBA_MIN)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, (0, 0))

    # Soft cloth bulge highlight: a diffuse OFFSET blob on the upper-left belly
    # instead of a centred vertical stripe (which read as a seam/zipper). Built
    # as a faded ellipse so it reads as light catching a soft sack, not a seam.
    hi = pygame.Surface((S, S), pygame.SRCALPHA)
    for rr, aa in ((6, 60), (4, 70), (2, 80)):
        pygame.draw.ellipse(hi, (*KEYLINE, aa),
                            pygame.Rect(cx - 8 - rr, 22 - rr, rr * 2 + 4, rr * 2))
    hi.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hi, (0, 0))

    # Warm keyline along the lit upper-left belly so the brown body separates
    # from a dark NIGHT sky. Drawn just inside the outline on the left arc.
    left_arc = [(cx - (p[0] - cx), p[1]) for p in
                [body[i] for i in range(3, 11)]]
    if len(left_arc) >= 2:
        pygame.draw.lines(surf, KEYLINE, False,
                          [(int(x + 1.5), int(y + 1)) for x, y in left_arc], 2)

    # Cinched neck: a WIDE dark NOTCH band wrapping the pinch. Drawn fat +
    # darker than the body so the waist reads as a hard horizontal groove at
    # 22px — the single feature that separates "sack" from "coconut/ball".
    band = pygame.Rect(cx - neck_half - 4, neck_y - 3, (neck_half + 4) * 2, 8)
    pygame.draw.rect(surf, OUTLINE, band, border_radius=3)
    inner = band.inflate(-2, -3)
    pygame.draw.rect(surf, CORD, inner, border_radius=2)
    # Two cord wraps catch a sliver of light so the notch reads as a tie, not a
    # painted line, while staying inside the band footprint.
    pygame.draw.line(surf, KEYLINE, (band.left + 2, neck_y - 1),
                     (band.right - 3, neck_y - 1), 1)
    pygame.draw.line(surf, (*CORD, 255), (band.left + 2, neck_y + 2),
                     (band.right - 3, neck_y + 2), 1)

    # Compact rounded knot: a short fat bump sitting ON the band, kept low and
    # round (never a tall stem) so a 60/90 tilt can't elongate it into a gourd.
    # Outline ring -> fill -> tiny highlight reads as "tied" even at day scale.
    knot_y = neck_y - 6
    pygame.draw.circle(surf, OUTLINE, (cx, knot_y), 5)
    pygame.draw.circle(surf, TAN_BASE, (cx, knot_y), 4)
    pygame.draw.circle(surf, TAN_TOP, (cx - 1, knot_y - 1), 2)
    # A short shadow groove down the middle of the knot — the bump+shadow that
    # hints "gathered cloth tied off" without adding height.
    pygame.draw.line(surf, OUTLINE, (cx, knot_y - 2), (cx, knot_y + 3), 1)
    pygame.draw.circle(surf, KEYLINE, (cx - 2, knot_y - 2), 1)

    return pygame.transform.smoothscale(surf, (PARCEL_SIZE, PARCEL_SIZE))
