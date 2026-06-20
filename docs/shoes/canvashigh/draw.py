"""CANVAS HIGH — black canvas basketball HIGH-TOP homage.

Drawn entirely from pygame primitives so it survives the full size range:
the SAME function is the ~104×62 product shot AND a ~15×10 sprite on the
bird's feet. Geometry is expressed as fractions of the (x, y, w, h) box so it
scales cleanly; stroke widths clamp to >=1px so detail never vanishes tiny.

It is a HOMAGE in the spirit of the game's KFC parody theme — the classic
black-canvas hi-top colorway and silhouette with stylized cues (white rubber
toe cap, white foxing stripe, cream outsole, generic star-in-circle ankle
patch), never an exact trademarked mark. No text, no logo.

The READ is the silhouette: the high-top collar deliberately rises ABOVE the
box top (v < 0), so callers / previews must leave vertical headroom.
"""
import pygame


# Black canvas upper with a near-black shadow tint (not pure black, so the 1px
# edges read against a dark navy field). White rubber + cream outsole are the
# contrast that sells "hi-top sneaker".
_CANVAS    = (28, 28, 32)
_CANVAS_S  = (16, 16, 20)      # canvas shadow / seam
_RUBBER    = (244, 244, 238)   # white toe cap + foxing stripe
_RUBBER_S  = (206, 206, 200)   # 1px rubber edge
_SOLE      = (236, 230, 214)   # cream vulcanized outsole face
_SOLE_EDGE = (198, 192, 176)   # 1px sole edge
_PATCH     = (242, 236, 220)   # cream ankle patch disc
_PATCH_S   = (206, 198, 178)   # patch ring
_STAR      = (150, 60, 60)     # muted red star inside the patch
_LACE      = (224, 224, 218)
_EYELET    = (150, 150, 156)


def _u(u, v, x, y, w, h, facing):
    """Map unit-box (u, v) to device pixels, mirroring about u=0.5 when facing
    left so one core serves both feet / both store orientations. v may be < 0:
    the hi-top collar lives above the box top."""
    if facing < 0:
        u = 1.0 - u
    return (int(round(x + u * w)), int(round(y + v * h)))


def _poly(surf, color, pts, x, y, w, h, facing):
    pygame.draw.polygon(surf, color, [_u(u, v, x, y, w, h, facing)
                                      for u, v in pts])


def _line(surf, color, a, b, x, y, w, h, facing, width):
    pygame.draw.line(surf, color, _u(*a, x, y, w, h, facing),
                     _u(*b, x, y, w, h, facing), max(1, int(round(width))))


def _star(surf, color, cu, cv, ru, rv, x, y, w, h, facing):
    """A generic 5-point star (NOT a trademark) inscribed in an ellipse of
    radius (ru, rv) about (cu, cv). Points up; alternates outer/inner radii."""
    import math
    inner = 0.42  # inner-to-outer radius ratio of a classic 5-point star
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = 1.0 if i % 2 == 0 else inner
        pts.append((cu + math.cos(ang) * ru * rr,
                    cv + math.sin(ang) * rv * rr))
    # Mirror handling is done per-point by _u, so build in unit space directly.
    dev = [_u(pu, pv, x, y, w, h, facing) for pu, pv in pts]
    pygame.draw.polygon(surf, color, dev)


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile CANVAS HIGH sneaker into box (x, y, w, h).

    Toe points RIGHT when facing=1 (mirrored for -1). High-top: the ankle
    collar rises above y; the cream vulcanized outsole is the bottom ~22% of h
    with a white foxing stripe along its top. No outer outline — the caller
    adds the house outline.
    """
    # ── cream vulcanized outsole (bottom ~22%) ────────────────────────────
    # A flat-bottomed vulcanized cupsole with a softly upturned toe — the
    # basketball-hi-top read, not a chunky runner. Edge first, cream face on top.
    sole = [(0.05, 0.80), (0.92, 0.80), (0.99, 0.86), (0.97, 0.99),
            (0.06, 0.99), (0.02, 0.90)]
    _poly(surf, _SOLE_EDGE, sole, x, y, w, h, facing)
    sole_face = [(0.06, 0.82), (0.92, 0.82), (0.97, 0.88), (0.95, 0.97),
                 (0.07, 0.97), (0.04, 0.90)]
    _poly(surf, _SOLE, sole_face, x, y, w, h, facing)

    # ── CUE · white foxing stripe along the top of the sole ───────────────
    # The rubber bumper band that wraps the whole shoe just above the outsole.
    # A thick line clamps to >=1px so the white band survives the foot-sprite.
    _line(surf, _RUBBER_S, (0.04, 0.80), (0.97, 0.81), x, y, w, h, facing,
          max(2, h * 0.10))
    _line(surf, _RUBBER, (0.05, 0.785), (0.95, 0.795), x, y, w, h, facing,
          max(1, h * 0.07))

    # ── black canvas upper — HIGH-TOP, collar rises above the box ─────────
    # Heel at left, ankle cuff sweeping up and out of the box (v down to ~-0.30),
    # vamp dropping to the toe. The tall back collar IS the silhouette read.
    upper = [(0.07, 0.80), (0.05, 0.30), (0.06, -0.18), (0.10, -0.28),
             (0.26, -0.30), (0.34, -0.22), (0.34, 0.06), (0.46, 0.16),
             (0.70, 0.24), (0.88, 0.40), (0.93, 0.62), (0.92, 0.80)]
    _poly(surf, _CANVAS_S, upper, x, y, w, h, facing)
    upper_face = [(0.09, 0.79), (0.075, 0.30), (0.085, -0.16), (0.115, -0.255),
                  (0.255, -0.275), (0.315, -0.205), (0.315, 0.07),
                  (0.46, 0.18), (0.695, 0.255), (0.865, 0.41), (0.915, 0.62),
                  (0.905, 0.79)]
    _poly(surf, _CANVAS, upper_face, x, y, w, h, facing)

    # Collar opening notch — the ankle cuff's inner curve, a tonal shadow that
    # gives the hi-top its open-cuff depth.
    _poly(surf, _CANVAS_S, [(0.135, -0.20), (0.30, -0.22), (0.315, 0.02),
                            (0.26, 0.08), (0.18, 0.00)], x, y, w, h, facing)

    # ── CUE · white rounded rubber toe cap ────────────────────────────────
    # The bulbous capped toe — a filled wedge with a rounded leading edge.
    # Edge poly first, white face inset, then an ellipse to round the tip.
    toe = [(0.72, 0.80), (0.76, 0.40), (0.86, 0.41), (0.95, 0.58),
           (0.97, 0.74), (0.93, 0.80)]
    _poly(surf, _RUBBER_S, toe, x, y, w, h, facing)
    toe_face = [(0.74, 0.79), (0.775, 0.43), (0.85, 0.44), (0.925, 0.59),
                (0.945, 0.74), (0.91, 0.79)]
    _poly(surf, _RUBBER, toe_face, x, y, w, h, facing)
    # Rounded toe tip so the cap never reads as a hard corner, even tiny.
    tip = _u(0.90, 0.63, x, y, w, h, facing)
    pygame.draw.circle(surf, _RUBBER, tip, max(1, int(round(w * 0.055))))
    # Toe-cap stitch seam where the rubber meets canvas.
    _line(surf, _RUBBER_S, (0.755, 0.42), (0.745, 0.78), x, y, w, h, facing,
          max(1, w * 0.012))

    # ── lace throat — eyelet column up the high tongue ────────────────────
    # Short cross-bars + dot eyelets climbing the tall throat; both clamp to
    # >=1px so the "laced hi-top" cue survives shrink.
    bar_w = max(1, h * 0.05)
    for i, lv in enumerate((0.10, -0.02, -0.14)):
        _line(surf, _LACE, (0.36, lv), (0.50, lv - 0.05), x, y, w, h, facing,
              bar_w)
    erad = max(1, int(round(w * 0.013)))
    for ev in (0.12, 0.00, -0.12):
        pygame.draw.circle(surf, _EYELET, _u(0.345, ev, x, y, w, h, facing),
                           erad)

    # ── CUE · round cream ankle patch with a generic star ─────────────────
    # The signature medallion on the ankle. Ring + cream disc + muted star.
    # All radii clamp to >=1px; the star collapses to a dot when very small,
    # which still reads as "a patch is there".
    pcu, pcv = 0.20, 0.06
    pr = w * 0.085
    pygame.draw.circle(surf, _PATCH_S, _u(pcu, pcv, x, y, w, h, facing),
                       max(2, int(round(pr * 1.10))))
    pygame.draw.circle(surf, _PATCH, _u(pcu, pcv, x, y, w, h, facing),
                       max(1, int(round(pr))))
    if pr >= 3:
        # ru/rv are unit-box fractions; equalise device radius (ru*w == rv*h)
        # so the star stays visually round regardless of box aspect.
        sr_dev = pr * 0.62
        _star(surf, _STAR, pcu, pcv, sr_dev / w, sr_dev / h,
              x, y, w, h, facing)
    else:
        pygame.draw.circle(surf, _STAR, _u(pcu, pcv, x, y, w, h, facing),
                           max(1, int(round(pr * 0.4))))
