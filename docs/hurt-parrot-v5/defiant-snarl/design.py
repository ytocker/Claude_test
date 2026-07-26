"""
Hurt-parrot concept: DEFIANT SNARL — Round 2.

Same thesis as Round 1: "hurt, and coming for you anyway." Round 2 tightens
the four levers that Round 1 identified but under-executed:

  * the head mass is rotated ~13° nose-down about the neck pivot as a unit,
    not merely translated — an angle change between two masses reads as a
    hunch at sprite scale; translation alone reads as "tired";
  * brow wedges now physically overprint the top of each lens in a visible
    warm-dark colour, shifting the apparent lens shape so the scowl reads in
    the glasses silhouette itself;
  * the mouth gape is widened to a true snarl by moving the hinge back and
    flattening the upper cutting edge to horizontal;
  * wing flap amplitude restored to full 90° travel so the bird reads alive.
"""
import math
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "offscreen")

import pygame
pygame.init()

from game.draw import (
    BIRD_RED, BIRD_RED_D, BIRD_BELLY, BIRD_BEAK, BIRD_BEAK_D,
)
from game.parrot import (
    SPRITE_W, SPRITE_H, _aaellipse, _build_wing, _add_outline,
    SHADE_FRAME, SHADE_BLACK, SHADE_TINT, SHADE_GLINT,
)

# Full 90° travel with a uniform -5° carry vs stock — each frame is
# exactly stock (50,20,-10,-40) minus 5, so no frame is identical to stock
# and the amplitude that reads as vitality is preserved.
_HURT_ANGLES = (45, 15, -15, -45)

# Body stays at stock Y so the hunch reads as an angle change between
# head and body, not as a global droop.
_HEAD_DX, _HEAD_DY = 2, 3
_BODY_DY = 0

# Neck pivot about which the entire head group (head ellipses + shades
# + brows + beak) is rotated as one rigid piece, nose-down.
_HEAD_PIVOT = (40, 28)
_HEAD_ROT_CW = 13.0  # degrees CW in screen space = nose pitching forward

# Warm dark red: visible over the black lens (luma contrast) and reads
# as an extension of the scarlet plumage rather than a foreign prop.
BROW_DARK = (150, 15, 20)
MOUTH_DARK = (15, 10, 10)
# Warm accent at the back of the cavity so pure black doesn't read as
# a sprite hole punched through the head on a dark background.
THROAT_ACCENT = (182, 80, 80)

# Hinge moved back (lower x) and up (lower y) so the swing arm that
# drives the lower mandible is longer, producing a wider gape arc.
_JAW_HINGE_X = 51
_JAW_HINGE_Y = 25
_JAW_OPEN_DEG = 38.0

_TAIL_PIVOT = (22, 33)
_TAIL_SWEEP_DEG = 10.0
_TAIL_FLATTEN = 0.86


def _rot(p, pivot, deg, flatten=1.0):
    """Rotate about pivot in screen space (y down). Positive deg is CW
    visually, which sweeps the tail rearward and pitches the nose down."""
    x = p[0] - pivot[0]
    y = (p[1] - pivot[1]) * flatten
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (pivot[0] + x * c - y * s, pivot[1] + x * s + y * c)


def _sweep_tail(p):
    return _rot((p[0], p[1] + _BODY_DY), _TAIL_PIVOT, _TAIL_SWEEP_DEG,
                _TAIL_FLATTEN)


def _draw_snarl_shades(surf, cx, cy):
    """Stock aviator geometry restored: r_outer=6, right lens at cx+6,
    double brow-bar. Brows are drawn AFTER this call and overprint the
    lens top, so the brow real-estate is gained through overprinting
    rather than by shrinking the lenses."""
    r_outer = 6
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)

    pygame.draw.circle(surf, SHADE_FRAME, left,  r_outer + 1)
    pygame.draw.circle(surf, SHADE_FRAME, right, r_outer + 1)
    pygame.draw.circle(surf, SHADE_BLACK, left,  r_outer)
    pygame.draw.circle(surf, SHADE_BLACK, right, r_outer)

    tint = pygame.Surface((r_outer * 2, r_outer), pygame.SRCALPHA)
    pygame.draw.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (left[0]  - r_outer, left[1]  - r_outer + 1))
    surf.blit(tint, (right[0] - r_outer, right[1] - r_outer + 1))

    # Stock glint positions (from _draw_sunglasses in parrot.py)
    pygame.draw.circle(surf, SHADE_GLINT, (left[0]  - 2, left[1]  - 2), 2)
    pygame.draw.circle(surf, SHADE_GLINT, (right[0] - 2, right[1] - 3), 2)
    pygame.draw.circle(surf, (255, 255, 255, 200), (left[0]  + 2, left[1]  + 2), 1)
    pygame.draw.circle(surf, (255, 255, 255, 200), (right[0] + 2, right[1] + 1), 1)

    # Bridge bar
    pygame.draw.line(surf, SHADE_FRAME,
                     (left[0]  + r_outer, left[1]),
                     (right[0] - r_outer, right[1]), 2)
    # Top brow-bar (aviator double-bar — the identity mark of this character)
    pygame.draw.line(surf, SHADE_FRAME,
                     (left[0]  - r_outer + 1, left[1]  - r_outer + 2),
                     (right[0] + r_outer - 1, right[1] - r_outer + 2), 1)

    return left, right


def _ipoly(pts):
    """Integer-round a list of float (x, y) pairs for pygame.draw.polygon."""
    return [(int(round(x)), int(round(y))) for x, y in pts]


def _draw_brows(surf, left_lens, right_lens):
    """Brow wedges drawn AFTER the lens fill so they overprint the upper
    third of each lens — the brow deforms the apparent lens shape, which
    is the read at sprite scale. Angled so the outer/temple end is higher
    than the inner/nose end: the classic angry-V convergence.

    Each wedge is 4 px tall to survive 1× without anti-aliasing away."""
    r = 6
    thick = 4

    lx, ly = left_lens
    # Left brow: temple at the left rim (high), nose at the right rim (low)
    l_t = (lx - r + 1, ly - r + 2)       # temple corner (higher)
    l_n = (lx + r - 1, ly - r + 2 + 3)   # nose corner (lower)
    pygame.draw.polygon(surf, BROW_DARK, _ipoly([
        l_t,
        l_n,
        (l_n[0],   l_n[1]   + thick),
        (l_t[0],   l_t[1]   + thick),
    ]))

    rx, ry = right_lens
    # Right brow: temple at the right rim (high), nose at the left rim (low)
    r_t = (rx + r - 1, ry - r + 2)        # temple corner (higher)
    r_n = (rx - r + 1, ry - r + 2 + 3)   # nose corner (lower)
    pygame.draw.polygon(surf, BROW_DARK, _ipoly([
        r_t,
        r_n,
        (r_n[0],   r_n[1]   + thick),
        (r_t[0],   r_t[1]   + thick),
    ]))


def _draw_snarl_beak(surf, dx, dy):
    """Upper mandible with a flat (horizontal) cutting edge so the opening
    reads as a proper wedge-gape rather than a pinched slit. Lower mandible
    swung off a back-set hinge for maximum arc travel. Cavity polygon built
    from the two jaw edges to guarantee no dark pixel leaks outside the
    beak silhouette."""
    hinge = (int(_JAW_HINGE_X + dx), int(_JAW_HINGE_Y + dy))

    # Upper mandible: tip of hook at ~(63,28), cutting edge flat at y=27+dy
    up_back  = (53 + dx, 27 + dy)
    up_front = (61 + dx, 27 + dy)   # horizontal — gape reads as a shout
    upper = [(52 + dx, 22 + dy), (57 + dx, 21 + dy), (62 + dx, 25 + dy),
             (61 + dx, 30 + dy), up_front, up_back]

    # Lower mandible rest position, then swung open off the hinge
    lower_flat = [
        (53 + dx, 28 + dy),
        (61 + dx, 29 + dy),
        (60 + dx, 34 + dy),
        (52 + dx, 33 + dy),
    ]
    lower = [_rot(p, hinge, _JAW_OPEN_DEG) for p in lower_flat]

    pygame.draw.polygon(surf, BIRD_BEAK,   _ipoly(lower))
    pygame.draw.polygon(surf, BIRD_BEAK_D, _ipoly(lower), 1)
    pygame.draw.polygon(surf, BIRD_BEAK,   _ipoly(upper))
    pygame.draw.polygon(surf, BIRD_BEAK_D, _ipoly(upper), 1)

    # Cavity: polygon defined between upper cutting edge and open lower jaw.
    # Inset from each jaw edge by ~0.5 px so the 1 px jaw outlines don't eat
    # the gap, which at this scale is the difference between snarl and seam.
    inset = 0.6
    cavity = [
        (up_back[0]  + inset,       up_back[1]  + inset),
        (up_front[0] - inset,       up_front[1] + inset),
        (up_front[0] - 1.2,         up_front[1] + 5.8),
        (lower[1][0] - inset,       lower[1][1] - inset),
        (lower[0][0] + inset,       lower[0][1] - inset * 0.5),
    ]
    pygame.draw.polygon(surf, MOUTH_DARK, _ipoly(cavity))

    # Warm throat accent at the hinge end of the cavity
    throat_x = int(lower[0][0] + 1.5)
    throat_y = int(lower[0][1] - 1)
    pygame.draw.circle(surf, THROAT_ACCENT, (throat_x, throat_y), 2)

    # Ridge gloss on upper mandible only — lower is in shadow
    pygame.draw.line(surf, (255, 230, 150),
                     (int(54 + dx), int(23 + dy)), (int(59 + dx), int(25 + dy)), 1)


def _rotate_blit_head(head_layer, dst):
    """Rotate head_layer CW by _HEAD_ROT_CW about _HEAD_PIVOT and blit onto
    dst so that the neck pivot lands at the same position in dst. Body stays
    fixed; only the head mass rotates, producing the nose-down lunge."""
    # pygame.transform.rotate uses positive = CCW; negate for CW
    rotated = pygame.transform.rotate(head_layer, -_HEAD_ROT_CW)
    old_w, old_h = head_layer.get_size()
    new_w, new_h = rotated.get_size()

    # Where the pivot was in the source surface, relative to its centre
    old_cx, old_cy = old_w / 2.0, old_h / 2.0
    px = _HEAD_PIVOT[0] - old_cx
    py = _HEAD_PIVOT[1] - old_cy

    # Where that pivot lands in the rotated surface (CW rotation formula,
    # consistent with the _rot() helper above)
    c = math.cos(math.radians(_HEAD_ROT_CW))
    s = math.sin(math.radians(_HEAD_ROT_CW))
    new_px = px * c - py * s
    new_py = px * s + py * c
    pivot_abs_x = new_w / 2.0 + new_px
    pivot_abs_y = new_h / 2.0 + new_py

    # Blit so pivot_abs in the rotated image maps back to _HEAD_PIVOT in dst
    blit_x = int(_HEAD_PIVOT[0] - pivot_abs_x)
    blit_y = int(_HEAD_PIVOT[1] - pivot_abs_y)
    dst.blit(rotated, (blit_x, blit_y))


def build_defiant_snarl_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail swept rearward — silhouette cue for "bracing against impact"
    tail_colors = [
        (200, 30, 40),
        (240, 95, 40),
        (255, 160, 55),
        (255, 220, 80),
    ]
    for i, c in enumerate(tail_colors):
        pts = [
            (2 + i * 3, 26 + i * 2),
            (14 + i, 24 + i),
            (20 + i, 30 + i * 2),
            (6 + i * 3, 36 + i * 2),
        ]
        pygame.draw.polygon(surf, c, [_sweep_tail(p) for p in pts])
    pygame.draw.line(surf, BIRD_RED_D,
                     _sweep_tail((4, 27)), _sweep_tail((18, 31)), 1)
    pygame.draw.line(surf, BIRD_RED_D,
                     _sweep_tail((6, 33)), _sweep_tail((20, 35)), 1)

    # Body at stock Y — hunch is expressed by head angle, not body translation
    b = _BODY_DY
    _aaellipse(surf, (120, 20, 25), (34, 35 + b), 19, 14)
    _aaellipse(surf, BIRD_RED,      (32, 32 + b), 19, 14)
    _aaellipse(surf, (255, 100, 100), (30, 29 + b), 13, 8)
    _aaellipse(surf, BIRD_BELLY,    (28, 38 + b), 12, 6)
    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 230, 230, 160), sheen.get_rect())
    surf.blit(sheen, (22, 21 + b))

    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28 + b)).topleft)

    # Build the entire head group on a separate layer at stock-size so the
    # whole group can be rotated as one rigid piece about the neck pivot.
    head_layer = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    dx, dy = _HEAD_DX, _HEAD_DY
    hx, hy = 47 + dx, 21 + dy

    _aaellipse(head_layer, (150, 15, 20),   (hx + 1, hy + 2), 12, 11)
    _aaellipse(head_layer, BIRD_RED,         (hx, hy),          12, 11)
    _aaellipse(head_layer, (255, 130, 130),  (hx - 3, hy + 3),   4,  3)
    _aaellipse(head_layer, (255, 170, 170),  (hx - 1, hy - 5),   7,  3)

    # Shades drawn first; brows drawn after to overprint the lens top
    left_lens, right_lens = _draw_snarl_shades(head_layer, 50 + dx, 20 + dy)
    _draw_brows(head_layer, left_lens, right_lens)
    _draw_snarl_beak(head_layer, dx, dy)

    # Rotate head group as a unit, keeping the neck pivot fixed in dst
    _rotate_blit_head(head_layer, surf)

    # Feet at stock position (body is at stock, so tucked feet stay put)
    pygame.draw.line(surf, BIRD_BEAK_D, (28, 45 + b), (26, 49 + b), 2)
    pygame.draw.line(surf, BIRD_BEAK_D, (34, 45 + b), (36, 49 + b), 2)

    return surf


def build_frames():
    return [_add_outline(build_defiant_snarl_frame(a)) for a in _HURT_ANGLES]


# ── Review strip ─────────────────────────────────────────────────────────────

CELL_W, CELL_H = 68, 64
BG = (8, 8, 20)


def _luma(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b


def _verify(frame_idx, sprite):
    """Print-only legibility probes: brow pixel count and gape width are
    the two reads that must survive 1×."""
    w, h = sprite.get_size()
    brow_n = 0
    gape_n = 0
    brow_high_contrast = 0  # brow pixels adjacent to pixels with Δluma > 80

    brow_l = _luma(*BROW_DARK)

    for y in range(h):
        for x in range(w):
            r, g, bl, a = sprite.get_at((x, y))
            if a < 16:
                continue
            is_brow = (abs(r - BROW_DARK[0]) <= 25
                       and abs(g - BROW_DARK[1]) <= 25
                       and abs(bl - BROW_DARK[2]) <= 25)
            if is_brow:
                brow_n += 1
                # Check contrast against at least one orthogonal neighbour
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < w and 0 <= ny < h:
                        nr, ng, nbl, na = sprite.get_at((nx, ny))
                        if na < 16:
                            continue
                        # Skip neighbour if it's also a brow pixel
                        if (abs(nr - BROW_DARK[0]) <= 25
                                and abs(ng - BROW_DARK[1]) <= 25
                                and abs(nbl - BROW_DARK[2]) <= 25):
                            continue
                        if abs(brow_l - _luma(nr, ng, nbl)) > 80:
                            brow_high_contrast += 1
                            break

            if (abs(r - MOUTH_DARK[0]) <= 10
                    and abs(g - MOUTH_DARK[1]) <= 10
                    and abs(bl - MOUTH_DARK[2]) <= 10
                    and x > 48):   # 48 = beak start in 68-wide outlined sprite
                gape_n += 1

    # Gape height check at x=56-62 (beak mid-section in outlined coords)
    gape_4px_cols = 0
    for cx in range(56, 63):
        col_count = 0
        for cy in range(h):
            r, g, bl, a = sprite.get_at((cx, cy))
            if a < 16:
                continue
            if (abs(r - MOUTH_DARK[0]) <= 10
                    and abs(g - MOUTH_DARK[1]) <= 10
                    and abs(bl - MOUTH_DARK[2]) <= 10):
                col_count += 1
        if col_count >= 4:
            gape_4px_cols += 1

    print(f"frame {frame_idx}: "
          f"brow={brow_n:4d} (gate≥120) | "
          f"brow_hi_contrast={brow_high_contrast:3d} (gate≥60) | "
          f"gape_px={gape_n:3d} (gate≥45) | "
          f"gape_4px_cols={gape_4px_cols}/7 (gate all≥4)")


def main():
    frames = build_frames()
    strip = pygame.Surface((CELL_W * len(frames), CELL_H))
    strip.fill(BG)
    for i, f in enumerate(frames):
        strip.blit(f, (i * CELL_W + (CELL_W - f.get_width()) // 2,
                       (CELL_H - f.get_height()) // 2))
        _verify(i, f)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(strip, out)
    print("wrote", out, strip.get_size())


if __name__ == "__main__":
    main()
