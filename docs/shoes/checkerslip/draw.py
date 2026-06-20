"""CHECKER SLIP — laceless slip-on with a black/white checkerboard upper.

Drawn entirely from pygame primitives so it survives the full size range:
the SAME function is the ~104×62 product shot AND a ~15×10 sprite on the
bird's feet. Geometry is fractions of the (x, y, w, h) box so it scales
cleanly; the checkerboard cell size is derived from box width (≈6 cells
across the upper) so it still reads as alternating light/dark when tiny.

It is a HOMAGE in the spirit of the game's KFC parody theme — a silhouette +
checkerboard colorway with two stylized cues (padded collar opening, white
foxing stripe), never an exact trademarked mark. No text, no logo.
"""
import pygame


# Stark black/white check on a cream waffle sole; sole edges are darker
# tints of the cream (not black) so the gum/cream outsole stays warm.
_CANVAS_W  = (244, 244, 240)   # white check / collar canvas
_CANVAS_D  = (24, 24, 28)      # black check
_LINING    = (236, 226, 206)   # collar opening / interior cream
_LINING_D  = (208, 196, 172)
_FOXING    = (248, 248, 244)   # white rubber foxing stripe
_FOXING_E  = (206, 206, 200)
_GUM       = (228, 206, 160)   # pale gum/cream outsole
_GUM_E     = (196, 172, 128)   # 1px darker sole edge / waffle line
_SEAM      = (212, 212, 208)   # quiet seam on white canvas


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


# Upper silhouette (toe-right), shared by the fill and the checker clip mask so
# the pattern never spills past the canvas. Low, round slip-on profile.
_UPPER = [(0.05, 0.78), (0.05, 0.50), (0.10, 0.40), (0.22, 0.34),
          (0.40, 0.32), (0.60, 0.33), (0.78, 0.40), (0.91, 0.52),
          (0.95, 0.66), (0.95, 0.78)]


def _checker_upper(surf, x, y, w, h, facing):
    """Tile a black/white checkerboard across the upper, clipped to its shape.

    Cell size scales with box width (~6 cells over the canvas) so the pattern
    survives shrinking to a 16px foot sprite: tiny, it degrades to a couple of
    legible light/dark blocks rather than a muddy grey. A device-space clip mask
    keeps squares inside the upper without per-pixel polygon math."""
    poly = [_u(u, v, x, y, w, h, facing) for u, v in _UPPER]
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    bx0, bx1 = min(xs), max(xs)
    by0, by1 = min(ys), max(ys)
    bw = max(1, bx1 - bx0)
    bh = max(1, by1 - by0)

    # White canvas base first; black squares stamp on top.
    pygame.draw.polygon(surf, _CANVAS_W, poly)

    # ~6 cells across the upper, min 2px so a cell never collapses to nothing.
    cell = max(2, int(round(bw / 6.0)))
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    # The check rides at ~28° so diagonals read like the real diamond-set
    # canvas rather than a flat grid; we approximate with an offset row shift.
    cols = bw // cell + 2
    rows = bh // cell + 2
    for r in range(rows):
        for c in range(cols):
            if (r + c) % 2 == 0:
                continue
            cxp = c * cell - (r % 2) * (cell // 2)
            cyp = r * cell
            pygame.draw.rect(mask, _CANVAS_D, (cxp, cyp, cell, cell))

    # Clip the tiled mask to the upper polygon by punching a stencil.
    stencil = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(stencil, (255, 255, 255, 255),
                        [(px - bx0, py - by0) for px, py in poly])
    mask.blit(stencil, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(mask, (bx0, by0))

    # Quiet seam where the toe-cap canvas meets the vamp, on the white base.
    _line(surf, _SEAM, (0.66, 0.36), (0.90, 0.54), x, y, w, h, facing,
          max(1, w * 0.012))


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile CHECKER SLIP shoe into box (x, y, w, h).

    Toe points RIGHT when facing=1 (mirrored for -1). Laceless slip-on:
    cream waffle outsole + white foxing stripe in the bottom ~22% of h,
    checkerboard canvas above, padded collar opening at the throat. No outer
    outline — the caller adds the house outline.
    """
    # ── cream gum outsole (bottom ~14%) ───────────────────────────────────
    # Pale waffle sole sits flat on the ground line with a soft toe-spring.
    sole = [(0.03, 0.86), (0.09, 0.84), (0.93, 0.85), (0.98, 0.89),
            (0.95, 0.99), (0.05, 0.99), (0.01, 0.92)]
    _poly(surf, _GUM_E, sole, x, y, w, h, facing)
    sole_face = [(0.04, 0.87), (0.93, 0.87), (0.95, 0.93), (0.06, 0.94)]
    _poly(surf, _GUM, sole_face, x, y, w, h, facing)
    # A few vertical waffle ticks — clamp to >=1px so they survive tiny.
    for tu in (0.20, 0.40, 0.60, 0.80):
        _line(surf, _GUM_E, (tu, 0.90), (tu, 0.97), x, y, w, h, facing,
              max(1, w * 0.01))

    # ── CUE 1 · white foxing stripe band along the sole ───────────────────
    # The bumper that wraps the slip-on: a clean white rubber band riding just
    # above the gum, the signature contrast against the cream below.
    foxing = [(0.04, 0.78), (0.95, 0.78), (0.96, 0.87), (0.03, 0.87)]
    _poly(surf, _FOXING_E, foxing, x, y, w, h, facing)
    foxing_face = [(0.05, 0.79), (0.94, 0.79), (0.95, 0.855), (0.045, 0.855)]
    _poly(surf, _FOXING, foxing_face, x, y, w, h, facing)

    # ── checkerboard canvas upper (hero cue) ──────────────────────────────
    _checker_upper(surf, x, y, w, h, facing)

    # ── CUE 2 · padded collar opening (no laces) ──────────────────────────
    # The slip-on tell: an open elasticated collar scooped out of the vamp,
    # lined in cream with a soft padded lip — and crucially NO laces.
    collar = [(0.22, 0.34), (0.40, 0.32), (0.56, 0.34), (0.54, 0.44),
              (0.40, 0.47), (0.27, 0.45)]
    _poly(surf, _LINING_D, collar, x, y, w, h, facing)
    collar_face = [(0.25, 0.355), (0.40, 0.34), (0.53, 0.355), (0.51, 0.43),
                   (0.40, 0.45), (0.29, 0.435)]
    _poly(surf, _LINING, collar_face, x, y, w, h, facing)
    # Padded collar lip — a bright cream rim arcing over the opening.
    _line(surf, _LINING, (0.23, 0.355), (0.40, 0.325), x, y, w, h, facing,
          max(1, h * 0.05))
    _line(surf, _LINING, (0.40, 0.325), (0.55, 0.355), x, y, w, h, facing,
          max(1, h * 0.05))

    # Crisp heel + toe edge tints so the white canvas reads against any sky.
    _line(surf, _SEAM, (0.05, 0.50), (0.05, 0.78), x, y, w, h, facing,
          max(1, w * 0.01))
