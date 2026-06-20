import pygame

# Side-profile BOOST KNIT runner. Every coordinate is derived from the box
# (x,y,w,h) so the same code reads as a 104x62 product shot AND as a 15x10
# bird-foot sprite — no fixed-pixel detail that survives only at one scale.

# Sand/tan knit upper, creamy speckled boost midsole.
_UPPER       = (208, 184, 148)
_UPPER_DK    = (176, 152, 118)   # subtle 1px seam/shadow on the knit
_UPPER_HI    = (226, 206, 174)   # collar/top highlight
_SOLE        = (244, 240, 230)   # creamy boost foam
_SOLE_DK     = (212, 206, 192)   # speckle ticks + bottom shadow
_OUTSOLE     = (190, 182, 168)   # rubber rim under the foam
_LOOP        = (150, 120, 86)    # heel pull-loop


def _fx(x, w, fx, facing):
    """Flip a 0..1 horizontal fraction when the shoe faces left."""
    return x + (fx if facing == 1 else 1.0 - fx) * w


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile BOOST KNIT sneaker into box (x,y,w,h)."""
    gx = y + h  # ground line

    # Chunky ribbed boost midsole — ~28% of the box height, the hero mass.
    sole_top = y + h * 0.72
    # Foam slab: thick at the heel, sweeping up under the toe spring.
    foam = [
        (_fx(x, w, 0.04, facing), sole_top),
        (_fx(x, w, 0.04, facing), gx - h * 0.07),
        (_fx(x, w, 0.10, facing), gx),
        (_fx(x, w, 0.90, facing), gx),
        (_fx(x, w, 0.98, facing), gx - h * 0.12),
        (_fx(x, w, 0.96, facing), sole_top - h * 0.04),
        (_fx(x, w, 0.62, facing), sole_top - h * 0.02),
        (_fx(x, w, 0.30, facing), sole_top),
    ]
    pygame.draw.polygon(surf, _SOLE, foam)

    # Thin rubber outsole rim grounding the foam.
    pygame.draw.polygon(surf, _OUTSOLE, [
        (_fx(x, w, 0.10, facing), gx),
        (_fx(x, w, 0.90, facing), gx),
        (_fx(x, w, 0.98, facing), gx - h * 0.12),
        (_fx(x, w, 0.94, facing), gx - h * 0.05),
        (_fx(x, w, 0.10, facing), gx - h * 0.05),
        (_fx(x, w, 0.07, facing), gx - h * 0.02),
    ])

    # Speckled-foam cue: close vertical tick marks across the midsole. Count
    # scales with width so big shots get dense ribbing and tiny ones stay clean.
    n = max(3, int(w / 7))
    for i in range(n):
        f = 0.12 + (0.74 * i / (n - 1))
        tx = _fx(x, w, f, facing)
        ty0 = sole_top + h * 0.02
        ty1 = gx - h * 0.05
        pygame.draw.line(surf, _SOLE_DK, (tx, ty0), (tx, ty1), 1)

    # Seamless sock-like knit upper — a single soft mound, low collar at heel.
    upper = [
        (_fx(x, w, 0.07, facing), sole_top - h * 0.02),       # heel base
        (_fx(x, w, 0.10, facing), y + h * 0.30),              # heel collar
        (_fx(x, w, 0.20, facing), y + h * 0.16),              # collar dip
        (_fx(x, w, 0.40, facing), y + h * 0.06),              # instep crown
        (_fx(x, w, 0.66, facing), y + h * 0.12),
        (_fx(x, w, 0.86, facing), y + h * 0.34),              # toe taper
        (_fx(x, w, 0.95, facing), y + h * 0.58),
        (_fx(x, w, 0.92, facing), sole_top - h * 0.02),
        (_fx(x, w, 0.30, facing), sole_top),
    ]
    pygame.draw.polygon(surf, _UPPER, upper)

    # Low collar highlight along the ankle opening.
    pygame.draw.line(surf, _UPPER_HI,
                     (_fx(x, w, 0.13, facing), y + h * 0.26),
                     (_fx(x, w, 0.42, facing), y + h * 0.08), 1)

    # Subtle horizontal knit lines — the woven Primeknit texture.
    rows = max(2, int(h / 9))
    for i in range(rows):
        ry = y + h * (0.22 + 0.40 * i / max(1, rows - 1))
        x0 = _fx(x, w, 0.16, facing)
        x1 = _fx(x, w, 0.84 - 0.04 * i, facing)
        pygame.draw.line(surf, _UPPER_DK, (x0, ry), (x1, ry), 1)

    # Heel pull-loop — small premium cue at the back collar.
    lx = _fx(x, w, 0.06, facing)
    pygame.draw.line(surf, _LOOP,
                     (lx, y + h * 0.20), (lx, y + h * 0.40),
                     max(1, int(w / 40)))

    # 1px darker edge where the upper meets the foam, without an outer outline.
    pygame.draw.line(surf, _UPPER_DK,
                     (_fx(x, w, 0.10, facing), sole_top - h * 0.01),
                     (_fx(x, w, 0.90, facing), sole_top - h * 0.01), 1)
    # Bottom shadow seating the outsole on the ground.
    pygame.draw.line(surf, _SOLE_DK,
                     (_fx(x, w, 0.10, facing), gx - 1),
                     (_fx(x, w, 0.90, facing), gx - 1), 1)
