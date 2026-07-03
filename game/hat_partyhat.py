import math

import pygame


# Vivid party colorway: teal cone with magenta diagonal stripes and a yellow
# pom. Layered flat tones (not a gradient) keep the read crisp at head_w~18 where
# blends muddy; a single lighter rib down the lit side fakes the cone's volume.
_CONE = (38, 196, 196)
_CONE_HI = (120, 230, 226)
_CONE_LO = (22, 150, 156)
_STRIPE = (236, 58, 150)
_STRIPE_LO = (190, 36, 120)
_TRIM = (255, 224, 96)
_TRIM_LO = (214, 176, 56)
_POM = (255, 226, 86)
_POM_HI = (255, 246, 178)
_POM_LO = (220, 178, 48)
_ELASTIC = (60, 52, 90)


def _lerp(a, b, t):
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile PARTY HAT sized for a head of width head_w, centered at cx, base line at base_y."""
    # All geometry scales off head_w so the cone survives big and small.
    r = head_w * 0.5
    f = 1 if facing >= 0 else -1

    # A party hat is TALL — the tip rises ~1.4x head_w above the base. The cone
    # leans slightly forward at facing=1 so it reads as worn, not balanced.
    tip_x = cx + f * r * 0.18
    tip_y = base_y - head_w * 1.42
    base_hw = r * 0.96  # half-width of the cone where it meets the head
    # The base sits a touch above base_y so the scalloped trim and the curved
    # underside can wrap down onto the round head's crown.
    base_cy = base_y - r * 0.22

    left_x = cx - base_hw
    right_x = cx + base_hw

    # Underside curves UP into the cone so it seats on a round head rather than
    # cutting a flat line across the crown.
    seat_dip = r * 0.34

    def underside(n=18):
        out = []
        for i in range(n + 1):
            t = i / n
            x = left_x + (right_x - left_x) * t
            # parabola: lowest (seated) at the edges, lifted under the centre
            lift = seat_dip * (1.0 - 4.0 * (t - 0.5) ** 2)
            out.append((x, base_cy + r * 0.30 - lift))
        return out

    bottom = underside()

    # Solid cone body.
    cone = [(tip_x, tip_y)] + bottom
    pygame.draw.polygon(surf, _CONE, cone)

    # Shade the trailing flank a step darker for cheap roundness.
    shade = [
        (tip_x, tip_y),
        (cx, base_cy + r * 0.30 - seat_dip),
        bottom[0] if f >= 0 else bottom[-1],
    ]
    pygame.draw.polygon(surf, _CONE_LO, shade)

    # Diagonal stripes wrap the cone — gated off below ~22px so the tiny hat
    # stays a clean cone+pom silhouette instead of a muddy band.
    if head_w >= 22:
        _draw_stripes(surf, tip_x, tip_y, left_x, right_x, base_cy, r, seat_dip, f)

    # A bright rib down the lit edge sells the cone's curvature.
    lit_edge = right_x if f >= 0 else left_x
    rib_w = max(1, int(r * 0.10))
    pygame.draw.line(surf, _CONE_HI, (tip_x, tip_y),
                     ((tip_x + lit_edge) * 0.5, base_cy + r * 0.05), rib_w)

    # Scalloped trim ring the base. Bumps scale with head_w; a smooth band stands
    # in below the scallop threshold so small sizes keep a tidy collar.
    _draw_trim(surf, left_x, right_x, base_cy, r, head_w)

    # Hint of chin elastic dropping from the trailing base corner.
    chin_x = (left_x if f >= 0 else right_x)
    elastic_w = max(1, int(r * 0.07))
    pygame.draw.line(surf, _ELASTIC,
                     (chin_x + f * r * 0.04, base_cy + r * 0.22),
                     (chin_x + f * r * 0.10, base_cy + r * 0.62), elastic_w)

    # Fluffy pom-pom on the very tip.
    _draw_pom(surf, tip_x, tip_y, r)


def _draw_stripes(surf, tip_x, tip_y, left_x, right_x, base_cy, r, seat_dip, f):
    # Stripes are quads that fan from near the tip down to the base, clipped to
    # the cone by a polygon mask so they never spill past the silhouette.
    base_y_line = base_cy + r * 0.30
    cone_mask = [
        (tip_x, tip_y),
        (left_x, base_y_line),
        (right_x, base_y_line),
    ]
    mask_rect = pygame.Rect(int(left_x - 2), int(tip_y - 2),
                            int(right_x - left_x + 4), int(base_y_line - tip_y + 4))
    if mask_rect.width <= 0 or mask_rect.height <= 0:
        return
    layer = pygame.Surface(mask_rect.size, pygame.SRCALPHA)
    ox, oy = mask_rect.left, mask_rect.top

    span = right_x - left_x
    n = 5
    sw = span / (n + 1)
    for i in range(-1, n + 2):
        # Slant each band forward so the stripes read as diagonal wraps.
        x0 = left_x + i * sw
        slant = span * 0.42 * f
        quad = [
            (x0 - ox, base_y_line - oy),
            (x0 + sw * 0.6 - ox, base_y_line - oy),
            (x0 + sw * 0.6 + slant - ox, tip_y - oy),
            (x0 + slant - ox, tip_y - oy),
        ]
        col = _STRIPE if (i % 2 == 0) else _STRIPE_LO
        pygame.draw.polygon(layer, col + (255,), quad)

    mask = pygame.Surface(mask_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(p[0] - ox, p[1] - oy) for p in cone_mask])
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(layer, (ox, oy))


def _draw_trim(surf, left_x, right_x, base_cy, r, head_w):
    band_y = base_cy + r * 0.26
    band_h = max(2, int(r * 0.20))
    pygame.draw.rect(surf, _TRIM_LO,
                     (int(left_x), int(band_y), int(right_x - left_x), band_h))
    pygame.draw.rect(surf, _TRIM,
                     (int(left_x), int(band_y), int(right_x - left_x),
                      max(1, band_h - 1)))

    # Scalloped bumps below the band, gated so tiny hats keep a clean collar.
    if head_w >= 20:
        bump_r = max(2, int(r * 0.14))
        step = bump_r * 1.7
        x = left_x + bump_r * 0.4
        bump_cy = band_y + band_h
        while x <= right_x - bump_r * 0.4:
            pygame.draw.circle(surf, _TRIM_LO, (int(x), int(bump_cy)), bump_r)
            pygame.draw.circle(surf, _TRIM, (int(x), int(bump_cy - 1)),
                               max(1, bump_r - 1))
            x += step


def _draw_pom(surf, tip_x, tip_y, r):
    pom_r = max(2, int(r * 0.30))
    cx, cy = tip_x, tip_y
    # Cluster of small blobs reads as fluff better than one flat disc; the back
    # blobs sit darker, a front-top highlight catches the light.
    offs = [
        (-0.6, 0.2, _POM_LO), (0.6, 0.2, _POM_LO), (0.0, 0.55, _POM_LO),
        (-0.35, -0.25, _POM), (0.35, -0.25, _POM), (0.0, 0.05, _POM),
    ]
    for dx, dy, col in offs:
        pygame.draw.circle(surf, col,
                           (int(cx + dx * pom_r), int(cy + dy * pom_r)),
                           max(1, int(pom_r * 0.62)))
    pygame.draw.circle(surf, _POM_HI,
                       (int(cx - pom_r * 0.2), int(cy - pom_r * 0.3)),
                       max(1, int(pom_r * 0.34)))
