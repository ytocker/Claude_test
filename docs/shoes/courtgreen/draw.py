"""COURT GREEN — clean minimalist white-leather tennis low-top homage.

Drawn entirely from pygame primitives so it survives the full size range:
the SAME function is the ~104×62 product shot AND a ~15×10 sprite on the
bird's feet. Geometry is expressed as fractions of the (x, y, w, h) box so it
scales cleanly; stroke widths clamp to >=1px so detail never vanishes tiny.

It is a HOMAGE in the spirit of the game's KFC parody theme — a silhouette +
colorway with two stylized cues (green heel tab, perforation-dot column where
a side stripe would be), never an exact trademarked mark. No text, no logo.
"""
import pygame


# Crisp all-white leather + understated green accent. Edges are 1px darker
# tints of the base, not black, so the shoe stays premium and clean.
_LEATHER   = (246, 246, 242)
_LEATHER_S = (220, 220, 214)   # leather shadow / soft seam
_SOLE      = (250, 250, 248)   # slim flat white sole face
_SOLE_EDGE = (206, 206, 200)   # 1px darker sole/edge line
_GREEN      = (40, 120, 78)    # heel-tab green
_GREEN_D    = (28, 92, 58)     # heel-tab shadow
_PERF       = (212, 212, 206)  # midfoot perforation dots
_LACE       = (236, 236, 230)


def _u(u, v, x, y, w, h, facing):
    """Map unit-box (u, v) in [0..1] to device pixels, mirroring about u=0.5
    when facing left so one core serves both feet / both store orientations."""
    if facing < 0:
        u = 1.0 - u
    return (int(round(x + u * w)), int(round(y + v * h)))


def _poly(surf, color, pts, x, y, w, h, facing):
    pygame.draw.polygon(surf, color, [_u(u, v, x, y, w, h, facing)
                                      for u, v in pts])


def _line(surf, color, a, b, x, y, w, h, facing, width):
    pygame.draw.line(surf, color, _u(*a, x, y, w, h, facing),
                     _u(*b, x, y, w, h, facing), max(1, int(round(width))))


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile COURT GREEN sneaker into box (x, y, w, h).

    Toe points RIGHT when facing=1 (mirrored for -1). Slim low-profile tennis
    shoe: outsole/midsole is the bottom ~18% of h, upper top near y. No outer
    outline — the caller adds the house outline.
    """
    # ── slim flat sole (bottom ~18%) ──────────────────────────────────────
    # A low, near-flat cupsole with a barely-lifted toe spring — the tennis
    # silhouette, not a chunky runner. Drawn dark-edge first, white face on top.
    sole = [(0.04, 0.86), (0.10, 0.83), (0.92, 0.84), (0.98, 0.88),
            (0.95, 0.99), (0.06, 0.99), (0.02, 0.92)]
    _poly(surf, _SOLE_EDGE, sole, x, y, w, h, facing)
    sole_face = [(0.05, 0.86), (0.92, 0.86), (0.95, 0.92), (0.07, 0.93)]
    _poly(surf, _SOLE, sole_face, x, y, w, h, facing)
    # Foxing seam where leather meets sole.
    _line(surf, _SOLE_EDGE, (0.06, 0.85), (0.93, 0.855), x, y, w, h, facing,
          max(1, h * 0.025))

    # ── white leather upper — low-top, clean swept silhouette ─────────────
    upper = [(0.06, 0.85), (0.06, 0.46), (0.14, 0.34), (0.30, 0.30),
             (0.46, 0.30), (0.66, 0.34), (0.86, 0.46), (0.95, 0.62),
             (0.96, 0.85)]
    _poly(surf, _LEATHER_S, upper, x, y, w, h, facing)
    upper_face = [(0.08, 0.84), (0.08, 0.47), (0.16, 0.36), (0.30, 0.32),
                  (0.46, 0.32), (0.65, 0.36), (0.84, 0.47), (0.93, 0.62),
                  (0.94, 0.84)]
    _poly(surf, _LEATHER, upper_face, x, y, w, h, facing)

    # Soft toe-cap seam — subtle, keeps the all-white read.
    _line(surf, _LEATHER_S, (0.72, 0.42), (0.90, 0.62), x, y, w, h, facing,
          max(1, w * 0.018))

    # ── collar notch + tongue (clean, tonal) ──────────────────────────────
    _poly(surf, _LEATHER_S, [(0.14, 0.44), (0.30, 0.32), (0.36, 0.40),
                             (0.20, 0.52)], x, y, w, h, facing)
    _poly(surf, _LEATHER, [(0.16, 0.45), (0.30, 0.35), (0.34, 0.41),
                           (0.20, 0.51)], x, y, w, h, facing)
    # Lace bars across the throat.
    for lv in (0.44, 0.52, 0.60):
        _line(surf, _LACE, (0.34, lv), (0.50, lv - 0.04), x, y, w, h, facing,
              max(1, h * 0.045))

    # ── CUE 1 · perforation-dot column on the midfoot ─────────────────────
    # Where rivals run a side stripe, this model has only quiet perforations.
    # Drawn as a short vertical arc of dots; radius clamps to >=1px so it still
    # reads as "dotted, not striped" when tiny.
    rad = max(1, int(round(w * 0.012)))
    for i, (du, dv) in enumerate(((0.50, 0.50), (0.54, 0.56), (0.58, 0.62))):
        pygame.draw.circle(surf, _PERF, _u(du, dv, x, y, w, h, facing), rad)

    # ── CUE 2 · green heel tab ────────────────────────────────────────────
    # The signature: a small coloured tab at the back collar. Shadow block
    # first, brighter green on top for a touch of dimension.
    _poly(surf, _GREEN_D, [(0.06, 0.40), (0.115, 0.36), (0.135, 0.46),
                           (0.085, 0.52)], x, y, w, h, facing)
    _poly(surf, _GREEN, [(0.07, 0.41), (0.115, 0.38), (0.125, 0.45),
                         (0.085, 0.50)], x, y, w, h, facing)
