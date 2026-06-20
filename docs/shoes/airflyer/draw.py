import pygame


# AIR FLYER — an all-white chunky low-top basketball sneaker. The read is a
# tall clean off-white midsole stack capped by a slim grey outsole edge, with a
# single smooth curved side swoop in light grey sweeping heel→toe as the hero
# cue. Flat laces, a small heel tab and a faintly perforated toe finish it. All
# geometry is proportional so the same call serves the product shot and the
# tiny bird-foot size; the swoop survives because it is one bold filled stroke.

_CREAM   = (244, 242, 235)   # off-white upper
_CREAM_D = (210, 207, 198)   # upper shadow / 1px edges
_MID     = (250, 249, 244)   # midsole, a touch brighter than the upper
_MID_D   = (222, 219, 210)
_GREY    = (176, 178, 184)   # the side swoop + grey accents
_GREY_D  = (138, 140, 148)
_OUT     = (118, 120, 128)   # slim outsole edge
_PERF    = (208, 205, 197)   # toe perforation dots


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile AIR FLYER sneaker into box (x,y,w,h)."""
    # Work in facing=1 (toe right) space, then mirror coordinates so one body
    # of geometry serves both directions.
    def px(t):
        return x + (t * w if facing == 1 else (1.0 - t) * w)

    def py(t):
        return y + t * h

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [(px(a), py(b)) for a, b in pts])

    # Bottom ~22% of the box is the sole stack; the low-top upper stays inside.
    mid_top = 0.78   # top of the chunky midsole
    up_top  = 0.30   # crown of the rounded low-top upper

    # ── slim grey outsole edge (thin tread band on the ground line) ────────────
    poly(_OUT, [
        (0.03, 1.00), (0.97, 1.00), (0.99, 0.94),
        (0.95, 0.92), (0.05, 0.92), (0.02, 0.96),
    ])

    # ── chunky off-white midsole stack — the bright base that grounds the shoe ─
    poly(_MID, [
        (0.02, 0.95), (0.045, mid_top), (0.18, 0.74),
        (0.82, 0.74), (0.95, mid_top), (0.985, 0.95),
        (0.95, 0.925), (0.05, 0.925),
    ])
    # Soft heel-side shadow on the midsole for a touch of volume.
    poly(_MID_D, [
        (0.02, 0.95), (0.045, mid_top), (0.075, mid_top),
        (0.055, 0.95),
    ])
    # A single subtle midsole crease line, drawn as a thin shadow wedge.
    poly(_MID_D, [
        (0.20, 0.865), (0.80, 0.865), (0.80, 0.885), (0.20, 0.885),
    ])

    # ── upper: one rounded cream low-top body sitting on the midsole ───────────
    poly(_CREAM, [
        (0.07, mid_top), (0.07, 0.52), (0.12, 0.40),
        (0.24, 0.33), (0.40, 0.31), (0.55, 0.33),
        (0.70, 0.40), (0.84, 0.52), (0.92, 0.66),
        (0.94, mid_top),
    ])
    # Toe cap front edge + heel back edge get a 1px darker seam for definition.
    poly(_CREAM_D, [
        (0.90, 0.66), (0.94, mid_top), (0.905, mid_top), (0.875, 0.68),
    ])
    poly(_CREAM_D, [
        (0.07, mid_top), (0.07, 0.52), (0.095, 0.52), (0.095, mid_top),
    ])

    # ── the hero cue: a single smooth grey side swoop sweeping heel→toe ────────
    # Drawn as one bold filled crescent (outer curve minus inner curve) so it
    # stays a clean stroke even at bird-foot size.
    poly(_GREY, [
        (0.18, 0.70), (0.30, 0.62), (0.48, 0.56),
        (0.66, 0.54), (0.82, 0.56), (0.86, 0.62),
        (0.80, 0.61), (0.64, 0.595), (0.46, 0.61),
        (0.30, 0.665), (0.22, 0.72),
    ])
    # Thin lower shadow on the swoop's trailing edge for a 1px darker lip.
    poly(_GREY_D, [
        (0.18, 0.70), (0.22, 0.72), (0.30, 0.665), (0.28, 0.685),
    ])

    # ── flat laces: short cream bars on a faint grey lace gap ──────────────────
    # A narrow throat shadow first, then bright bars that read when tiny.
    poly(_GREY, [
        (0.36, 0.40), (0.54, 0.385), (0.55, 0.46), (0.38, 0.50),
    ])
    bar_w = 0.045
    for i, (lx, ty) in enumerate(((0.385, 0.41), (0.435, 0.405), (0.485, 0.41))):
        poly(_CREAM, [
            (lx, ty), (lx + bar_w, ty - 0.01),
            (lx + bar_w, ty + 0.045), (lx, ty + 0.055),
        ])

    # ── small heel tab poking up at the back collar ────────────────────────────
    poly(_CREAM, [
        (0.10, 0.40), (0.10, 0.30), (0.17, 0.295),
        (0.18, 0.36), (0.135, 0.40),
    ])
    poly(_CREAM_D, [
        (0.10, 0.40), (0.10, 0.30), (0.125, 0.30), (0.125, 0.40),
    ])

    # ── subtly perforated toe: a few faint dots near the toe box ───────────────
    # Skip when the box is too small to resolve them cleanly.
    if w >= 36:
        for dx, dy in ((0.74, 0.50), (0.78, 0.54), (0.74, 0.58),
                       (0.80, 0.49), (0.80, 0.59)):
            cx, cy = px(dx), py(dy)
            r = max(1, int(w * 0.008))
            pygame.draw.circle(surf, _PERF, (int(cx), int(cy)), r)
