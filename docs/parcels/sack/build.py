"""BURLAP SACK parcel cosmetic (LOW tier).

A cinched-neck burlap loot sack: a fat onion/teardrop body bulging at the
BOTTOM, pinched to a tied NECK with a chunky knot nub at the top — the only
soft, organic, non-boxy silhouette in the low tier. Built at 2× then
smoothscaled so the curved outline survives the 22px read and the tilt
rotation.
"""
import math
import pygame

from game.parrot import _lerp_color

PARCEL_SIZE = 22

# DAY-anchored burlap palette. The body gradient runs tan -> base shadow so
# the bag reads as a weighted, full sack rather than a flat blob.
TAN_TOP   = (201, 163, 107)   # #C9A36B lit upper body
TAN_BASE  = (140, 106,  58)   # #8C6A3A darker base shadow at the bottom bulge
CORD      = ( 90,  68,  36)   # #5A4424 dark tie-cord at the neck
KEYLINE   = (232, 201, 138)   # #E8C98A warm rim so brown survives NIGHT sky
OUTLINE   = ( 38,  26,  12)   # dark high-value bake to read on bright day sky


def _onion_points(cx, neck_y, base_y, half_w, neck_half):
    """Teardrop/onion outline: narrow pinched neck swelling to a wide rounded
    bottom belly. Sampled as a closed polygon (mirrored L/R) so the curve is
    smooth after the 2x->1x downscale and stays a bag under rotation."""
    pts_r = []
    span = base_y - neck_y
    for i in range(0, 21):
        t = i / 20.0
        y = neck_y + t * span
        # Width profile: pinched at the neck (t=0), bulging low (t~0.72),
        # tucking back in to a rounded base (t=1).
        bulge = math.sin(t * math.pi * 0.92 + 0.18)
        w = neck_half + (half_w - neck_half) * (bulge ** 0.85)
        pts_r.append((cx + w, y))
    # Rounded bottom cap, then mirror the right edge back up the left side.
    pts = pts_r + [(p[0] - 2 * (p[0] - cx), p[1]) for p in reversed(pts_r)]
    return pts


def build(mode: str = "normal") -> pygame.Surface:
    # `mode` is ignored — the cosmetic keeps one look across all power-ups.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    neck_y = 11
    base_y = 39
    half_w = 16
    neck_half = 4

    body = _onion_points(cx, neck_y, base_y, half_w, neck_half)

    # Soft contact shadow under the heavy bottom bulge.
    sh = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 5, 2, 120), pygame.Rect(cx - 16, base_y - 5, 32, 11))
    surf.blit(sh, (0, 0))

    # Outline bake: draw the body polygon fattened in OUTLINE first, then the
    # fill on top. A single bold dark edge is what carries the 22px read.
    out_pts = []
    for x, y in body:
        dx, dy = x - cx, y - (neck_y + base_y) / 2
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
    surf.blit(grad, (0, 0))

    # Warm keyline along the lit upper-left belly so the brown body separates
    # from a dark NIGHT sky. Drawn just inside the outline on the left arc.
    left_arc = [(cx - (p[0] - cx) - 0, p[1]) for p in
                [body[i] for i in range(2, 9)]]
    if len(left_arc) >= 2:
        pygame.draw.lines(surf, KEYLINE, False,
                          [(int(x + 1.5), int(y + 1)) for x, y in left_arc], 2)

    # A couple of burlap pucker folds gathering from the neck into the body —
    # cheap texture that still reads as cloth, not stitching, when tiny.
    pygame.draw.line(surf, (TAN_BASE), (cx - 5, 17), (cx - 8, 30), 1)
    pygame.draw.line(surf, (TAN_BASE), (cx + 5, 17), (cx + 8, 30), 1)
    pygame.draw.line(surf, KEYLINE, (cx - 1, 18), (cx - 2, 31), 1)

    # Cinched neck: dark tie-cord band wrapping the pinch, then the chunky
    # knot nub above it. The nub is deliberately fat so it survives 22px and
    # keeps reading as "tied sack" at every bank angle.
    pygame.draw.rect(surf, OUTLINE, pygame.Rect(cx - 7, neck_y - 4, 14, 7),
                     border_radius=3)
    pygame.draw.rect(surf, CORD, pygame.Rect(cx - 6, neck_y - 3, 12, 5),
                     border_radius=2)
    pygame.draw.line(surf, KEYLINE, (cx - 5, neck_y - 2), (cx + 5, neck_y - 2), 1)

    # Knot nub + the gathered cloth fan above the cord (the bag's "open top"
    # cinched shut). Outline first, then fill, for the same bold-edge read.
    nub = [(cx - 6, neck_y - 4), (cx - 3, neck_y - 10), (cx, neck_y - 7),
           (cx + 3, neck_y - 10), (cx + 6, neck_y - 4)]
    nub_out = [(cx - 7, neck_y - 3), (cx - 4, neck_y - 12), (cx, neck_y - 8),
               (cx + 4, neck_y - 12), (cx + 7, neck_y - 3)]
    pygame.draw.polygon(surf, OUTLINE, nub_out)
    pygame.draw.polygon(surf, TAN_TOP, nub)
    pygame.draw.line(surf, KEYLINE, (cx - 2, neck_y - 9), (cx - 1, neck_y - 5), 1)
    pygame.draw.circle(surf, OUTLINE, (cx, neck_y - 5), 2)
    pygame.draw.circle(surf, CORD, (cx, neck_y - 5), 1)

    return pygame.transform.smoothscale(surf, (PARCEL_SIZE, PARCEL_SIZE))
