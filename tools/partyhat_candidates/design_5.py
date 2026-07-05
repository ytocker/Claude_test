"""PARTY HAT candidate 5 — BALLOON BOUQUET (SCRATCH ONLY).

A cluster of round party balloons tied with curling strings, bobbing above
the head. No cone — the silhouette is a rounded multi-blob bouquet that
gathers at a knot on the crown and rises above it. The strings curl down to
the gather point; each balloon carries a tied nib and a white specular dot.

Read-down strategy mirrors the original: detail (specular, knot nibs, curls)
is gated off below ~22px head_w so the small in-game render stays a clean
multi-blob silhouette of vivid balloons instead of muddy clutter.
"""
import math

import pygame

from tools.partyhat_candidates._template import make_build, make_icon

# Vivid balloon colourway with a matched darker shade per balloon for the
# rounded shadow flank; one white specular dot reads "glossy latex" at a glance.
_BALLOONS = (
    ((0xE8, 0x45, 0x4A), (0xB8, 0x34, 0x1E)),   # red
    ((0xFF, 0xD2, 0x3F), (0xC9, 0xA2, 0x27)),   # yellow
    ((0x19, 0xC3, 0xC9), (0x0E, 0x8A, 0x90)),   # teal
    ((0x7B, 0x2F, 0xF7), (0x5A, 0x1F, 0xC0)),   # violet
)
_SPEC = (255, 255, 255)
_STRING = (245, 245, 250)
_STRING_LO = (200, 200, 212)
_KNOT = (120, 96, 70)


def _balloon(surf, cx, cy, rw, rh, base, shade, detail):
    """One latex balloon: shaded body + bright face + a tied nib at the bottom."""
    # Trailing flank a step darker for cheap roundness — draw the shaded disc
    # first, then the lit face inset toward the top-left light.
    pygame.draw.ellipse(surf, shade,
                        (int(cx - rw), int(cy - rh), int(rw * 2), int(rh * 2)))
    face_off = max(1, int(rw * 0.16))
    pygame.draw.ellipse(surf, base,
                        (int(cx - rw + face_off), int(cy - rh + face_off * 0.5),
                         int(rw * 2 - face_off), int(rh * 2 - face_off)))

    # The little pinched knot at the base — a tiny triangle nib.
    nib = max(1, int(rw * 0.28))
    ny = cy + rh
    pygame.draw.polygon(surf, shade, [
        (cx - nib, ny), (cx + nib, ny), (cx, ny + nib * 1.3)])

    if detail:
        # Soft specular highlight, biased up-left toward the light source.
        sr = max(1, int(rw * 0.30))
        pygame.draw.ellipse(surf, _SPEC,
                            (int(cx - rw * 0.42), int(cy - rh * 0.55),
                             int(sr * 1.4), int(sr * 1.8)))


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a BALLOON BOUQUET sized for a head of width head_w, centered at cx.

    base_y is the gather point on the crown where the knot ties and the strings
    converge; the balloon cluster rises ABOVE it so the bouquet reads as worn
    on top of the head, never draped over the face. facing only nudges the
    bouquet's lean so it reads as carried, not balanced.
    """
    r = head_w * 0.5
    f = 1 if facing >= 0 else -1
    detail = head_w >= 22
    # Curling strings + ornate ribbon knot are the product-shot flourish. At the
    # in-game head size they pile white string/nib/loop pixels into a tangle over
    # Pip's face, so they're gated to icon scale; on-bird the bouquet reads as a
    # clean cluster of balloons with just a tiny anchor knot at the crown.
    full = head_w >= 44

    # Gather knot sits right on the crown so the whole cluster lifts above the
    # head instead of hugging it; the lowest balloon's bottom edge then lands
    # at/just above base_y rather than crossing down into the face.
    gather_x = cx + f * r * 0.06
    gather_y = base_y

    # Balloon radius dropped so a taller four-stack clears the 64x100 icon top
    # and so sky opens between adjacent lobes (four countable balloons, not one
    # merged blob); only the lower-pair bottoms touch the crown.
    br = r * 0.43
    # Cluster layout in balloon-radius units, relative to the gather point.
    # Lower pair = YELLOW + RED (largest, most legible) spread wide so each
    # holds its own circle at 40px; upper pair = TEAL + VIOLET, higher and
    # tighter, kept apart so teal never shares an edge with violet. Bottoms of
    # the lower pair sit ~1 br above the gather (top balloons ~2.2 br) so the
    # whole bouquet rises ~head_w*1.3 above base_y, matching the original cone.
    lean = f * 0.08
    layout = [
        (-1.10 + lean, -1.45, 1.08, _BALLOONS[1]),   # lower-left  yellow
        (1.10 + lean, -1.50, 1.08, _BALLOONS[0]),    # lower-right red
        (-0.46 + lean, -2.85, 0.96, _BALLOONS[2]),   # upper-left  teal
        (0.46 + lean, -2.90, 0.96, _BALLOONS[3]),    # upper-right violet
    ]

    # Curling strings first so balloons overlap their tops cleanly. Each string
    # runs from the gather knot up to a balloon's nib with a gentle S-curl. Only
    # at icon scale — on-bird they crowd the face.
    if full:
        string_w = max(1, int(r * 0.07))
        for dx, dy, scale, _ in layout:
            bx = gather_x + dx * br
            by = gather_y + dy * br
            _curl_string(surf, gather_x, gather_y, bx, by + br * scale,
                         br, string_w, detail)

    # Balloons painted back-to-front: lower pair first so the upper crown
    # overlaps them, reinforcing the rounded bouquet stack.
    order = [2, 3, 0, 1] if False else [0, 1, 2, 3]
    for dx, dy, scale, (base, shade) in [layout[i] for i in order]:
        bx = gather_x + dx * br
        by = gather_y + dy * br
        rw = br * scale
        rh = br * scale * 1.16  # latex balloons are taller than wide
        _balloon(surf, bx, by, rw, rh, base, shade, detail)

    # The gather knot: a small ribbon bow / tie where all strings meet, drawn
    # right at base_y (the crown line) so it anchors the bouquet to the head.
    # Ornate ribbon loops only at icon scale.
    _knot(surf, gather_x, base_y, r, full)


def _curl_string(surf, x0, y0, x1, y1, br, w, detail):
    """A gently curling string from the gather (x0,y0) to a balloon nib."""
    if not detail:
        pygame.draw.line(surf, _STRING_LO, (int(x0), int(y0)), (int(x1), int(y1)), w)
        return
    # Sine-bowed polyline gives the curl; a darker under-stroke fakes depth.
    pts = []
    n = 10
    bow = br * 0.32 * (1 if x1 >= x0 else -1)
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t + math.sin(t * math.pi * 2.2) * bow * (1 - t)
        y = y0 + (y1 - y0) * t
        pts.append((int(x), int(y)))
    pygame.draw.lines(surf, _STRING_LO, False,
                      [(px + 1, py) for px, py in pts], w)
    pygame.draw.lines(surf, _STRING, False, pts, max(1, w))


def _knot(surf, cx, cy, r, detail):
    # Even tiny (below the 22px detail gate) keep a 1-2px dark nub at the crown
    # so the cluster reads as TIED to the head, not floating above it.
    kr = max(1, int(r * 0.12))
    pygame.draw.circle(surf, _KNOT, (int(cx), int(cy)), kr)
    if detail:
        # Two tiny ribbon loops flaring out from the knot.
        loop = max(2, int(r * 0.14))
        for s in (-1, 1):
            pygame.draw.ellipse(surf, _KNOT,
                                (int(cx + s * loop * 0.6 - loop * 0.5),
                                 int(cy - loop * 0.3),
                                 loop, int(loop * 0.7)))


build = make_build(draw_hat, seat={"hw": 32, "dx": 4, "dy": -1})
icon = make_icon(draw_hat)
