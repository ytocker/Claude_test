import pygame


# Beachy thong sandal: cream foam sole, white midsole edge, bright teal strap.
# Kept deliberately flat + minimal so the silhouette reads as a flip-flop (not a
# sneaker) even at bird-foot size; the only "hero" detail is the Y-thong strap.
_SOLE_TOP = (224, 200, 156)      # warm cream/tan footbed
_SOLE_TOP_DK = (196, 170, 124)   # subtle 1px lip under the footbed
_SOLE_EDGE = (244, 240, 232)     # white midsole stripe
_SOLE_EDGE_DK = (210, 204, 192)  # shadow line at the very bottom
_STRAP = (38, 196, 190)          # bright teal thong
_STRAP_DK = (24, 150, 146)       # strap shading / underside


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile FLIP-FLOP sandal into box (x,y,w,h)."""

    def px(fx, fy):
        # Proportional point; mirror horizontally about the box centre when
        # facing left so the toe always points the requested way.
        nx = fx if facing >= 0 else (1.0 - fx)
        return (x + nx * w, y + fy * h)

    ground = y + h

    # Thin two-layer sole hugging the ground line. The footbed is the coloured
    # top band; the white edge is a slimmer band beneath it. Slight upward
    # curl at toe + heel keeps it from looking like a plain block.
    foot_top = 0.66          # top of the cream footbed
    foot_bot = 0.84          # footbed / white-edge boundary
    edge_bot = 1.0           # ground
    heel_x = 0.06
    toe_x = 0.94

    footbed = [
        px(heel_x, foot_top + 0.04),   # heel: tiny curl up
        px(0.30, foot_top - 0.02),
        px(0.66, foot_top - 0.02),
        px(toe_x, foot_top + 0.05),    # toe: tiny curl up
        px(toe_x, foot_bot),
        px(heel_x, foot_bot),
    ]
    pygame.draw.polygon(surf, _SOLE_TOP, footbed)
    # 1px darker lip along the footbed/edge seam for separation.
    pygame.draw.line(surf, _SOLE_TOP_DK, px(heel_x, foot_bot), px(toe_x, foot_bot),
                     max(1, int(h * 0.03)))

    white_edge = [
        px(heel_x, foot_bot),
        px(toe_x, foot_bot),
        px(toe_x - 0.01, edge_bot),
        px(heel_x + 0.01, edge_bot),
    ]
    pygame.draw.polygon(surf, _SOLE_EDGE, white_edge)
    pygame.draw.line(surf, _SOLE_EDGE_DK, px(heel_x + 0.01, edge_bot - 0.005),
                     px(toe_x - 0.01, edge_bot - 0.005), max(1, int(h * 0.03)))

    # Y-thong strap — the signature cue. A short post rises from the footbed
    # near the toe, then splits: one strap leans forward toward the toe, the
    # other sweeps back toward the arch, both anchored into the sole.
    post_x = 0.70                 # where the thong meets the sole, near the toe
    apex = px(post_x, foot_top - 0.30)   # split point, floating above the sole
    sw = max(1, int(w * 0.045))   # strap thickness scales with size

    # Anchor roots sit just above the footbed surface.
    root_y = foot_top - 0.01
    front_root = px(0.84, root_y)
    back_root = px(0.50, root_y)
    post_root = px(post_x, root_y)

    # Two side straps form the V; the post is the stem of the Y.
    pygame.draw.line(surf, _STRAP, apex, front_root, sw)
    pygame.draw.line(surf, _STRAP, apex, back_root, sw)
    pygame.draw.line(surf, _STRAP_DK, apex, post_root, sw)

    # Rounded caps so the thin straps don't look frayed at any scale, plus a
    # small knob at the apex where the straps meet.
    for pt in (apex, front_root, back_root, post_root):
        pygame.draw.circle(surf, _STRAP, (int(pt[0]), int(pt[1])), max(1, sw // 2 + 1))
    pygame.draw.circle(surf, _STRAP_DK, (int(apex[0]), int(apex[1])),
                       max(1, sw // 2 + 1))
