import pygame


# Palette kept off pure white so the upper still reads as a body against a
# white HUD/product backdrop, and so the shell cap separates from the laced
# upper at thumbnail size where edge lines vanish.
_UPPER = (245, 245, 240)
_UPPER_EDGE = (208, 208, 200)
_SHELL = (236, 234, 226)
_SHELL_EDGE = (198, 196, 188)
_RIB = (210, 208, 200)
_SOLE = (250, 250, 248)
_SOLE_EDGE = (60, 60, 66)
_STRIPE = (28, 28, 34)
_LACE = (250, 250, 248)
_LACE_EDGE = (200, 200, 196)
_COLLAR = (224, 224, 218)


def _mirror(px, x, w, facing):
    # Mirror about the box centre so toe-right geometry serves facing=-1 too.
    return x + w - (px - x) if facing < 0 else px


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile SHELL TOE sneaker into box (x,y,w,h)."""
    # Everything is authored toe-right then point-mirrored, so the silhouette
    # stays identical when the bird's left/right foot flips.
    def fx(px):
        return _mirror(px, x, w, facing)

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [(fx(px), py) for px, py in pts])

    def line(color, a, b, width=1):
        pygame.draw.line(surf, color, (fx(a[0]), a[1]), (fx(b[0]), b[1]), width)

    ground = y + h
    sole_top = y + h - h * 0.22  # cupsole owns the bottom ~22% per the set spec
    # A thin midsole/sidewall sliver reads as the dark cupsole edge line.
    sidewall = sole_top + h * 0.10

    toe_x = x + w * 0.96
    heel_x = x + w * 0.05
    upper_top = y + h * 0.12

    # --- white rubber cupsole: flat slab, slightly toe-tapered, dark thin edge
    poly(_SOLE, [
        (heel_x - w * 0.01, sole_top),
        (toe_x + w * 0.01, sole_top - h * 0.03),
        (toe_x + w * 0.01, ground - h * 0.02),
        (heel_x - w * 0.01, ground - h * 0.01),
    ])
    # Dark contrast line where the cupsole meets the upper — the signature
    # crisp Superstar sole/upper break.
    line(_SOLE_EDGE, (heel_x - w * 0.01, sole_top), (toe_x + w * 0.01, sole_top - h * 0.03),
         max(1, int(h * 0.04)))
    # Outsole bottom edge.
    line(_SOLE_EDGE, (heel_x - w * 0.01, ground - h * 0.01), (toe_x + w * 0.01, ground - h * 0.02),
         max(1, int(h * 0.03)))

    # --- main white upper body (heel quarter through vamp, sitting on sidewall)
    poly(_UPPER, [
        (heel_x, sidewall),
        (heel_x + w * 0.02, upper_top + h * 0.06),
        (x + w * 0.30, upper_top),
        (x + w * 0.55, upper_top + h * 0.02),
        (x + w * 0.74, upper_top + h * 0.14),
        (toe_x - w * 0.02, sidewall - h * 0.02),
        (toe_x - w * 0.02, sole_top),
        (heel_x, sole_top),
    ])

    # --- ribbed rubber SHELL TOE cap wrapping the front
    # A rounded cap occupying the toe ~26% of the width; vertical ribs read as
    # the hero cue. Built as an ellipse front + filler so it wraps the toe.
    cap_left = x + w * 0.70
    cap_w = (toe_x + w * 0.015) - cap_left
    cap_top = upper_top + h * 0.14
    cap_h = sidewall - cap_top
    # Filler so the cap meets the upper with a flat back instead of a hard arc.
    poly(_SHELL, [
        (cap_left, cap_top + cap_h * 0.18),
        (cap_left + cap_w * 0.5, cap_top),
        (toe_x - cap_w * 0.04, cap_top + cap_h * 0.22),
        (toe_x + w * 0.015, sidewall - h * 0.02),
        (cap_left, sidewall),
    ])
    cap_rect = pygame.Rect(int(fx(cap_left) if facing > 0 else fx(cap_left + cap_w)),
                           int(cap_top), int(cap_w), int(cap_h))
    cap_rect.normalize()
    pygame.draw.ellipse(surf, _SHELL, cap_rect)
    # Off-white shell separates from the upper with a soft darker seam.
    line(_SHELL_EDGE, (cap_left, cap_top + cap_h * 0.18), (cap_left, sidewall),
         max(1, int(h * 0.02)))

    # Vertical rib ticks across the shell — the defining shell-toe texture.
    n_ribs = 5
    rib_w = max(1, int(w * 0.012))
    for i in range(1, n_ribs + 1):
        t = i / (n_ribs + 1)
        rx = cap_left + cap_w * (0.18 + 0.74 * t)
        # Ribs shorten toward the rounded toe so they hug the cap curvature.
        curve = 1.0 - (t - 0.5) * (t - 0.5) * 1.4
        r_top = cap_top + cap_h * (0.18 + 0.30 * (1.0 - curve))
        r_bot = sidewall - h * 0.015
        line(_RIB, (rx, r_top), (rx, r_bot), rib_w)

    # --- THREE bold dark side stripes across the midfoot, angled toward laces
    # Stripes run from the sole up toward the throat, the classic 3-stripe rake.
    band_x0 = x + w * 0.40
    s_gap = w * 0.075
    s_w = max(2, int(w * 0.045))
    for i in range(3):
        bx = band_x0 + i * s_gap
        # Forward rake: top sits ahead of the base.
        poly(_STRIPE, [
            (bx, sole_top - h * 0.02),
            (bx + s_w, sole_top - h * 0.02),
            (bx + s_w + w * 0.03, upper_top + h * 0.10),
            (bx + w * 0.03, upper_top + h * 0.10),
        ])

    # --- collar dip and heel quarter shading for low-top read
    poly(_COLLAR, [
        (heel_x + w * 0.01, upper_top + h * 0.06),
        (x + w * 0.16, upper_top - h * 0.01),
        (x + w * 0.30, upper_top + h * 0.04),
        (x + w * 0.24, upper_top + h * 0.20),
        (heel_x + w * 0.03, upper_top + h * 0.18),
    ])
    # Heel tab nub — small Superstar cue at the back.
    poly(_SHELL, [
        (heel_x - w * 0.005, upper_top + h * 0.04),
        (heel_x + w * 0.05, upper_top + h * 0.01),
        (heel_x + w * 0.05, upper_top + h * 0.16),
        (heel_x - w * 0.005, upper_top + h * 0.17),
    ])

    # --- fat flat laces over the throat/tongue
    lace_x0 = x + w * 0.26
    lace_x1 = x + w * 0.50
    n_laces = 3
    lace_h = max(2, int(h * 0.07))
    for i in range(n_laces):
        ly = upper_top + h * 0.04 + i * (h * 0.11)
        lx0 = lace_x0 + i * w * 0.015
        lx1 = lace_x1 - i * w * 0.01
        rect = pygame.Rect(int(min(fx(lx0), fx(lx1))), int(ly),
                           int(abs(fx(lx1) - fx(lx0))), lace_h)
        pygame.draw.rect(surf, _LACE, rect, border_radius=max(1, lace_h // 2))
        pygame.draw.rect(surf, _LACE_EDGE, rect, width=1,
                         border_radius=max(1, lace_h // 2))

    # Subtle upper top seam to break the large white field on the big shot.
    line(_UPPER_EDGE, (x + w * 0.30, upper_top + h * 0.01),
         (x + w * 0.70, upper_top + h * 0.14), 1)
