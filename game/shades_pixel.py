"""PIXEL SHADES — blocky 8-bit "deal-with-it" black sunglasses.

Hard right-angle steps, no anti-aliasing feel: every shape is an axis-aligned
filled rect snapped to a pixel grid sized off ``eye_w``. The chunky stepped
silhouette is the read; a single white pixel highlight per lens sells the
meme look without softening it.
"""
import pygame

_BLACK   = (18, 18, 24)
_GLINT   = (235, 240, 250)


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    # Pixel unit — everything snaps to this so it reads as crisp 8-bit blocks.
    px = max(1, int(round(eye_w * 0.085)))

    # Two stacked block rows per lens give the stepped meme silhouette:
    # a wide top row + a narrower lower row offset inward.
    lens_w = px * 4
    sep = px * 2                            # gap/bridge width between lenses
    top_h = px * 2
    bot_h = px

    near_x = cx + f * (sep // 2)            # inner edge toward beak
    far_x  = cx - f * (sep // 2)

    def block(x_inner, sign):
        # x_inner is the lens edge nearest the bridge; sign points outward.
        x0 = x_inner if sign > 0 else x_inner - lens_w
        ty = cy - top_h
        # top wide row
        surf.fill(_BLACK, (x0, ty, lens_w, top_h))
        # lower row, stepped in by one px on the outer side (the classic notch)
        surf.fill(_BLACK, (x0 + px, cy, lens_w - px, bot_h))
        # single bright pixel highlight, upper-inner corner
        gx = x0 + (lens_w - px * 2 if sign > 0 else px)
        surf.fill(_GLINT, (gx, ty, px, px))

    block(near_x, 1)
    block(far_x - 0, -1)

    # Solid bridge bar across the top connecting the lenses.
    bx = min(far_x, near_x)
    surf.fill(_BLACK, (bx, cy - top_h, abs(near_x - far_x), px))

    # Stepped temple arm marching back toward the ear (2 blocks).
    ay = cy - top_h
    ax = far_x - lens_w
    surf.fill(_BLACK, (ax - px * 2, ay, px * 2, px))
    surf.fill(_BLACK, (ax - px * 3, ay - px, px, px))
