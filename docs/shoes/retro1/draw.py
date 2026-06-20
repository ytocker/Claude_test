import pygame


# RETRO 1 — high-top basketball sneaker. The read is the colour-blocked AJ1
# silhouette: red toe box, black midfoot/lace panel, red heel counter, a chunky
# white midsole, and a padded ankle collar rising above the box. All geometry is
# proportional so the same call works at product-shot size and at bird-foot size.

_RED     = (206,  34,  40)
_RED_D   = (150,  20,  26)
_BLACK   = ( 28,  26,  32)
_BLACK_D = ( 12,  11,  16)
_WHITE   = (240, 238, 232)
_WHITE_D = (188, 184, 178)
_GREY    = (120, 118, 120)


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile RETRO 1 sneaker into box (x,y,w,h)."""
    # Work in facing=1 (toe right) space, then mirror coordinates if needed so
    # one body of geometry serves both directions.
    def px(t):
        return x + (t * w if facing == 1 else (1.0 - t) * w)

    def py(t):
        return y + t * h

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [(px(a), py(b)) for a, b in pts])

    # Sole band lives in the bottom ~22% of the box; collar rises above the top.
    sole_top = 0.80
    mid_top  = 0.66

    # ── outsole (dark tread) + white midsole stack ─────────────────────────────
    poly(_BLACK_D, [
        (0.02, 1.00), (0.96, 1.00), (0.99, 0.93),
        (0.92, 0.90), (0.05, 0.90), (0.02, 0.95),
    ])
    # Chunky white midsole — the bright base that grounds the colour block.
    poly(_WHITE, [
        (0.03, 0.94), (0.06, sole_top), (0.92, sole_top),
        (0.97, 0.90), (0.97, 0.945), (0.93, 0.97),
        (0.06, 0.97),
    ])
    poly(_WHITE_D, [
        (0.03, 0.94), (0.06, 0.965), (0.06, sole_top), (0.045, sole_top),
    ])

    # ── upper: black foxing/midfoot panel as the base layer ────────────────────
    poly(_BLACK, [
        (0.07, sole_top), (0.07, 0.40), (0.30, 0.34),
        (0.62, 0.36), (0.80, 0.42), (0.92, sole_top),
    ])

    # ── red toe box (front overlay) ────────────────────────────────────────────
    poly(_RED, [
        (0.60, mid_top), (0.66, 0.40), (0.82, 0.46),
        (0.93, 0.62), (0.94, sole_top), (0.78, sole_top),
        (0.66, sole_top),
    ])
    poly(_RED_D, [
        (0.90, 0.66), (0.94, 0.62), (0.94, sole_top), (0.90, sole_top),
    ])

    # ── red heel counter (rear overlay) ────────────────────────────────────────
    poly(_RED, [
        (0.07, sole_top), (0.07, 0.40), (0.18, 0.33),
        (0.26, 0.36), (0.24, sole_top),
    ])
    poly(_RED_D, [
        (0.07, sole_top), (0.07, 0.40), (0.10, 0.40), (0.10, sole_top),
    ])

    # ── padded ankle collar rising above the box top (high-top read) ───────────
    # Black collar pad with a red leather ankle band wrapping its base.
    poly(_RED, [
        (0.13, 0.42), (0.13, 0.18), (0.34, 0.16),
        (0.38, 0.34), (0.26, 0.36),
    ])
    poly(_BLACK, [
        (0.11, 0.30), (0.12, 0.10), (0.22, 0.04),
        (0.34, 0.06), (0.34, 0.20), (0.20, 0.24),
    ])
    # Soft top edge of the collar cuff.
    poly(_BLACK_D, [
        (0.12, 0.10), (0.22, 0.04), (0.34, 0.06), (0.32, 0.10), (0.22, 0.085),
    ])

    # ── lace panel: a few stylized eyelet bars on the black midfoot ────────────
    # Drawn as short white bars so they survive when the shoe is tiny.
    bar_w = 0.05
    for i, ty in enumerate((0.30, 0.40, 0.50, 0.60)):
        lx = 0.36 + i * 0.055
        poly(_WHITE_D, [
            (lx, ty), (lx + bar_w, ty - 0.015),
            (lx + bar_w, ty + 0.035), (lx, ty + 0.05),
        ])

    # ── stylized wing accent near the ankle (generic, not a logo) ──────────────
    # Two swept feather strokes reading as a small wing badge.
    poly(_WHITE, [
        (0.18, 0.20), (0.30, 0.17), (0.27, 0.22), (0.19, 0.24),
    ])
    poly(_WHITE, [
        (0.19, 0.25), (0.29, 0.23), (0.26, 0.27), (0.20, 0.28),
    ])
    poly(_RED, [
        (0.235, 0.165), (0.255, 0.155), (0.25, 0.205), (0.23, 0.215),
    ])
