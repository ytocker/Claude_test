"""Round-1 explorations for the WHITE RETRO Skybit SHADES (`shades_white`).

Three takes on 80s/90s white-plastic-framed shades over a side-profile macaw:
  A · SQUARE        — bold rectangular frame, the boxy 80s mall-shade read.
  B · ROUNDED-RECT  — softened-corner frame, the friendly 90s look (PICKED).
  C · CAT-EYE       — slight upswept outer corner, fashion-forward retro.

Each is a self-contained `draw_shades(surf, cx, cy, eye_w, facing=1)` so the
sheet can swap them in. The chosen one is copied verbatim to draw.py.

All geometry is proportional to `eye_w` via `_u()` so the same code reads at
product scale (eye_w~96) and in-game (eye_w=22, where 1px decides legibility).
A side profile only really shows ONE lens edge-on; we draw the near (front)
lens as the hero and let the far lens read as a thin sliver across the bridge,
which is how real shades look from the side. The temple arm sweeps back toward
the ear (-facing).
"""
import pygame


# ── White-retro palette ──────────────────────────────────────────────────────
# Glossy white plastic needs a value spread to read as a 3D rim, not a flat
# blob: a bright top highlight, a mid body, and a grey underside so the frame
# turns. Smoke lens is near-black with a cool tint + a hard specular streak.
FRAME_HI    = (255, 255, 255)     # top edge catching the sun
FRAME_BODY  = (238, 236, 230)     # warm-white plastic body
FRAME_SHADE = (188, 186, 182)     # underside / turn of the bevel
FRAME_LINE  = (120, 120, 124)     # thin seam separating frame from lens
LENS_SMOKE  = (28, 30, 40)        # dark smoke
LENS_SMOKE_H= (58, 64, 84)        # upper-lens cool reflection
LENS_TINT   = (44, 70, 96)        # faint sky reflection low in the lens
GLINT       = (255, 255, 255)     # specular streak
# Optional coloured-mirror tint (used as the C·cat-eye flavour to show range).
MIRROR_TOP  = (255, 120, 170)     # hot-pink → tangerine mirror gradient
MIRROR_BOT  = (255, 180, 90)


def _u(eye_w, k):
    """Proportional unit: never collapses a feature below 1px at small sizes."""
    return max(1, int(round(eye_w * k)))


# ─────────────────────────────────────────────────────────────────────────────
# Shared lens fill: a vertical smoke gradient + cool top reflection + a low
# sky tint + a diagonal specular streak. `corner` controls how rounded the
# lens rectangle is. Drawn into its own surface and clipped to the rounded
# rect so the gradient never bleeds past the frame.
# ─────────────────────────────────────────────────────────────────────────────
def _smoke_lens(w, h, corner, mirror=False):
    lens = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1)
        if mirror:
            col = _lerp(MIRROR_TOP, MIRROR_BOT, t)
        else:
            # smoke: cool reflection at top easing into dark, with a faint
            # warm-sky tint reappearing low so the lens doesn't read as a hole.
            if t < 0.45:
                col = _lerp(LENS_SMOKE_H, LENS_SMOKE, t / 0.45)
            else:
                col = _lerp(LENS_SMOKE, LENS_TINT, (t - 0.45) / 0.55 * 0.5)
        pygame.draw.line(lens, col, (0, y), (w, y))
    # Clip the gradient to the rounded-rect lens shape.
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=corner)
    lens.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return lens


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _specular(surf, x, y, w, h, eye_w):
    """A single bright diagonal streak across the upper lens — the one cue
    that sells 'glass' even at 22px."""
    gw = _u(eye_w, 0.05)
    pygame.draw.line(surf, GLINT,
                     (x + w * 0.18, y + h * 0.62),
                     (x + w * 0.55, y + h * 0.14), gw)
    # tiny secondary sparkle dot
    pygame.draw.circle(surf, GLINT,
                       (int(x + w * 0.30), int(y + h * 0.30)),
                       max(1, gw // 2))


# ─────────────────────────────────────────────────────────────────────────────
# Common temple arm + bridge: arm sweeps from the back-top corner of the near
# lens toward the ear (-facing); bridge is a short white bar over the beak side
# (+facing) hinting at the far lens.
# ─────────────────────────────────────────────────────────────────────────────
def _temple_and_bridge(surf, cx, cy, eye_w, facing, lens_top, lens_w, lens_h,
                       hinge_dx):
    arm_w = _u(eye_w, 0.085)
    # Hinge stud at the back-top outer corner of the near lens.
    hx = cx - facing * hinge_dx
    hy = lens_top + _u(eye_w, 0.10)
    # Arm sweeps back and slightly up toward the ear, with a soft elbow.
    elbow = (hx - facing * _u(eye_w, 0.22), hy - _u(eye_w, 0.06))
    ear = (hx - facing * _u(eye_w, 0.46), hy - _u(eye_w, 0.02))
    pygame.draw.line(surf, FRAME_SHADE, (hx, hy + 1), elbow, arm_w)
    pygame.draw.lines(surf, FRAME_BODY, False, [(hx, hy), elbow, ear], arm_w)
    pygame.draw.line(surf, FRAME_HI, (hx, hy - 1),
                     (elbow[0], elbow[1] - 1), max(1, arm_w - 2))
    # Bright hinge rivet.
    pygame.draw.circle(surf, FRAME_HI, (hx, hy), max(1, arm_w // 2))

    # Bridge: short raised bar toward the beak hinting the bridge-of-nose +
    # far lens sliver.
    by = cy - _u(eye_w, 0.10)
    bx0 = cx + facing * hinge_dx
    bx1 = cx + facing * (hinge_dx + _u(eye_w, 0.16))
    pygame.draw.line(surf, FRAME_SHADE, (bx0, by + 1), (bx1, by + 1),
                     _u(eye_w, 0.10))
    pygame.draw.line(surf, FRAME_BODY, (bx0, by), (bx1, by), _u(eye_w, 0.09))
    pygame.draw.line(surf, FRAME_HI, (bx0, by - 1), (bx1, by - 1),
                     max(1, _u(eye_w, 0.04)))
    # Far-lens sliver edge-on past the bridge: a thin dark vertical with a
    # white outer rim, the side-profile read of the second lens.
    fx = bx1 + facing * _u(eye_w, 0.03)
    pygame.draw.line(surf, FRAME_BODY, (fx, by - _u(eye_w, 0.02)),
                     (fx, by + lens_h - _u(eye_w, 0.04)), _u(eye_w, 0.06))
    pygame.draw.line(surf, LENS_SMOKE_H,
                     (fx + facing * _u(eye_w, 0.04), by + _u(eye_w, 0.04)),
                     (fx + facing * _u(eye_w, 0.04),
                      by + lens_h - _u(eye_w, 0.06)), _u(eye_w, 0.05))


# ─────────────────────────────────────────────────────────────────────────────
# A · SQUARE — boxy rectangular 80s mall shade. Thick straight white rim,
# minimal corner rounding, smoke lens. The most "retro plastic" silhouette.
# ─────────────────────────────────────────────────────────────────────────────
def draw_shades_square(surf, cx, cy, eye_w, facing=1):
    lens_w = _u(eye_w, 0.62)
    lens_h = _u(eye_w, 0.58)
    rim = _u(eye_w, 0.12)
    corner = _u(eye_w, 0.06)
    # Centre the near lens slightly toward the beak so it covers the eye.
    lx = cx - lens_w // 2 + facing * _u(eye_w, 0.06)
    ly = cy - lens_h // 2
    hinge_dx = lens_w // 2 - rim // 2

    _temple_and_bridge(surf, cx, cy, eye_w, facing, ly, lens_w, lens_h,
                       hinge_dx)

    outer = pygame.Rect(lx - rim, ly - rim, lens_w + rim * 2, lens_h + rim * 2)
    # White plastic rim: shaded base, body, then a bright top-left bevel.
    pygame.draw.rect(surf, FRAME_SHADE, outer, border_radius=corner + rim // 2)
    pygame.draw.rect(surf, FRAME_BODY, outer.inflate(-2, -2),
                     border_radius=corner + rim // 2)
    pygame.draw.line(surf, FRAME_HI, (outer.x + corner, outer.y + 1),
                     (outer.right - corner, outer.y + 1), max(1, rim // 3))
    pygame.draw.line(surf, FRAME_HI, (outer.x + 1, outer.y + corner),
                     (outer.x + 1, outer.bottom - corner), max(1, rim // 3))
    # Lens well.
    pygame.draw.rect(surf, FRAME_LINE, (lx - 1, ly - 1, lens_w + 2, lens_h + 2),
                     border_radius=corner)
    lens = _smoke_lens(lens_w, lens_h, corner)
    surf.blit(lens, (lx, ly))
    _specular(surf, lx, ly, lens_w, lens_h, eye_w)


# ─────────────────────────────────────────────────────────────────────────────
# B · ROUNDED-RECT (PICKED) — friendly 90s shade: thick white rim with softly
# rounded corners, smoke lens. Rounder corners ease against the round head and
# keep a clean read at 22px while still saying "chunky retro plastic".
# ─────────────────────────────────────────────────────────────────────────────
def draw_shades_rounded(surf, cx, cy, eye_w, facing=1):
    lens_w = _u(eye_w, 0.64)
    lens_h = _u(eye_w, 0.60)
    rim = _u(eye_w, 0.13)
    corner = _u(eye_w, 0.22)
    lx = cx - lens_w // 2 + facing * _u(eye_w, 0.06)
    ly = cy - lens_h // 2
    hinge_dx = lens_w // 2 - rim // 3

    _temple_and_bridge(surf, cx, cy, eye_w, facing, ly, lens_w, lens_h,
                       hinge_dx)

    outer = pygame.Rect(lx - rim, ly - rim, lens_w + rim * 2, lens_h + rim * 2)
    out_corner = corner + rim
    pygame.draw.rect(surf, FRAME_SHADE, outer, border_radius=out_corner)
    pygame.draw.rect(surf, FRAME_BODY, outer.inflate(-2, -2),
                     border_radius=out_corner)
    # Glossy top-left highlight arc — the plastic catching light.
    pygame.draw.line(surf, FRAME_HI,
                     (outer.x + out_corner - 1, outer.y + 1),
                     (outer.right - out_corner + 1, outer.y + 1),
                     max(1, rim // 3))
    pygame.draw.line(surf, FRAME_HI, (outer.x + 1, outer.y + out_corner),
                     (outer.x + 1, outer.bottom - out_corner),
                     max(1, rim // 3))
    # Lens well + smoke fill.
    pygame.draw.rect(surf, FRAME_LINE, (lx - 1, ly - 1, lens_w + 2, lens_h + 2),
                     border_radius=corner)
    lens = _smoke_lens(lens_w, lens_h, corner)
    surf.blit(lens, (lx, ly))
    _specular(surf, lx, ly, lens_w, lens_h, eye_w)


# ─────────────────────────────────────────────────────────────────────────────
# C · CAT-EYE (coloured mirror flavour) — slight upswept outer-top corner +
# a hot-pink→tangerine MIRROR lens, showing the tint-variant range. The sweep
# is a small triangular flick at the back-top corner so it reads as cat-eye
# even at 22px without a separate shape pass.
# ─────────────────────────────────────────────────────────────────────────────
def draw_shades_cateye(surf, cx, cy, eye_w, facing=1):
    lens_w = _u(eye_w, 0.62)
    lens_h = _u(eye_w, 0.56)
    rim = _u(eye_w, 0.12)
    corner = _u(eye_w, 0.16)
    lx = cx - lens_w // 2 + facing * _u(eye_w, 0.06)
    ly = cy - lens_h // 2
    hinge_dx = lens_w // 2 - rim // 3

    _temple_and_bridge(surf, cx, cy, eye_w, facing, ly, lens_w, lens_h,
                       hinge_dx)

    outer = pygame.Rect(lx - rim, ly - rim, lens_w + rim * 2, lens_h + rim * 2)
    pygame.draw.rect(surf, FRAME_SHADE, outer, border_radius=corner + rim // 2)
    pygame.draw.rect(surf, FRAME_BODY, outer.inflate(-2, -2),
                     border_radius=corner + rim // 2)
    # Cat-eye flick: a white triangle lifting the BACK-top outer corner
    # (toward the ear, -facing) above the rim line.
    flick_x = outer.x if facing == 1 else outer.right
    flick = [
        (flick_x, outer.y + _u(eye_w, 0.04)),
        (flick_x - facing * _u(eye_w, 0.20), outer.y - _u(eye_w, 0.16)),
        (flick_x - facing * _u(eye_w, 0.02), outer.y + _u(eye_w, 0.14)),
    ]
    pygame.draw.polygon(surf, FRAME_SHADE, flick)
    pygame.draw.polygon(surf, FRAME_BODY,
                        [(flick[0][0], flick[0][1] + 1),
                         (flick[1][0], flick[1][1] + 1),
                         (flick[2][0] - facing, flick[2][1])])
    pygame.draw.line(surf, FRAME_HI, flick[1],
                     (flick[1][0] + facing * _u(eye_w, 0.06),
                      flick[1][1] + _u(eye_w, 0.04)), max(1, rim // 3))
    # Top bevel highlight.
    pygame.draw.line(surf, FRAME_HI, (outer.x + corner, outer.y + 1),
                     (outer.right - corner, outer.y + 1), max(1, rim // 3))
    # Mirror lens.
    pygame.draw.rect(surf, FRAME_LINE, (lx - 1, ly - 1, lens_w + 2, lens_h + 2),
                     border_radius=corner)
    lens = _smoke_lens(lens_w, lens_h, corner, mirror=True)
    surf.blit(lens, (lx, ly))
    _specular(surf, lx, ly, lens_w, lens_h, eye_w)


VARIANTS = [
    ("A · SQUARE", draw_shades_square),
    ("B · ROUNDED-RECT", draw_shades_rounded),
    ("C · CAT-EYE / MIRROR", draw_shades_cateye),
]
PICKED = "B · ROUNDED-RECT"
