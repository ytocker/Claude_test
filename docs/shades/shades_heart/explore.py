"""ROUND 1 exploration — HEART SHADES (shades_heart).

Three takes on heart-shaped festival eyewear for side-profile Pip (facing
right). All share one heart-silhouette builder; the hard problem is keeping the
heart readable at eye_w=22, so the lobes are kept fat and round with a crisp
top notch, and the rim is a filled larger heart underneath (no thin strokes that
vanish on downscale). Variants differ only in palette / gloss treatment:

  A — HOT PINK   : opaque bubblegum-magenta, white rim, hard glossy glint.
  B — FESTIVAL RED: classic Lolita red heart, warm gold rim, twin sparkle.
  C — ROSE TINT  : translucent rose lens (eye shows through), gold rim.
"""
import math
import pygame


# ── shared heart geometry ─────────────────────────────────────────────────────

def _heart_points(cx, cy, w, n=14):
    """Return a closed heart polygon whose widest span is ~``w`` and total
    height ~``w``. Centred on (cx, cy). Built from the classic implicit heart
    parametric curve so the two lobes stay round and the notch stays crisp —
    that read is what survives the downscale to 22px."""
    s = w * 0.5 / 17.0  # the parametric curve spans ~±17 in x at scale 1
    pts = []
    for i in range(n + 1):
        t = math.pi - (i / n) * 2 * math.pi      # sweep so top-notch is centred
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t)
              - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * s, cy + y * s * 0.92))
    return pts


def _fill_heart(surf, cx, cy, w, color):
    pygame.draw.polygon(surf, color, _heart_points(cx, cy, w))


# ── variant builders ──────────────────────────────────────────────────────────

# A · HOT PINK -----------------------------------------------------------------
A_RIM   = (255, 252, 254)          # bright white plastic rim
A_RIM_D = (236, 200, 222)
A_LENS  = (255, 64, 150)           # hot bubblegum magenta
A_LENS_H = (255, 150, 200)         # upper-lobe sheen
A_LENS_D = (206, 28, 110)          # point shadow
A_GLINT = (255, 255, 255)


def _draw_A(surf, cx, cy, eye_w, facing=1):
    f = facing
    w = max(7, int(eye_w * 0.62))
    sep = max(4, int(eye_w * 0.46))
    rim = max(2, int(eye_w * 0.085))

    near = (cx + f * (sep // 2), cy - max(1, int(eye_w * 0.02)))
    far  = (cx - f * (sep // 2), cy - max(1, int(eye_w * 0.02)))

    # Bridge first so it tucks behind the lenses.
    by = cy - max(2, int(w * 0.22))
    pygame.draw.line(surf, A_RIM, (far[0], by), (near[0], by), rim + 1)
    pygame.draw.line(surf, A_RIM_D, (far[0], by + 1), (near[0], by + 1), 1)

    # Temple arm sweeping back toward the ear, with a slight droop.
    ax = far[0] - f * max(2, int(eye_w * 0.34))
    pygame.draw.line(surf, A_RIM_D, (far[0], cy), (ax, cy - max(1, int(eye_w * 0.06))), rim + 2)
    pygame.draw.line(surf, A_RIM, (far[0], cy - 1), (ax, cy - max(1, int(eye_w * 0.06)) - 1), rim)

    for (lx, ly) in (far, near):
        _fill_heart(surf, lx, ly, w + rim * 2, A_RIM)   # white rim underlay
        _fill_heart(surf, lx, ly, w, A_LENS)
        # Upper-lobe sheen blob between the two lobes.
        pygame.draw.circle(surf, A_LENS_H,
                           (lx - max(1, int(w * 0.16)), ly - max(1, int(w * 0.10))),
                           max(1, int(w * 0.20)))
        # Deepen the point for glossy candy volume.
        pts = _heart_points(lx, ly + max(1, int(w * 0.14)), w * 0.55)
        pygame.draw.polygon(surf, A_LENS_D, pts[len(pts) // 3: 2 * len(pts) // 3 + 1]
                            + [(lx, ly + max(2, int(w * 0.48)))])

    # Hard glossy glint on the near lens.
    g = max(1, int(eye_w * 0.07))
    pygame.draw.circle(surf, A_GLINT,
                       (near[0] + max(1, int(w * 0.16)), near[1] - max(2, int(w * 0.18))), g)
    pygame.draw.circle(surf, A_GLINT,
                       (near[0] - max(1, int(w * 0.20)), near[1] + max(1, int(w * 0.06))),
                       max(1, g // 2))


# B · FESTIVAL RED -------------------------------------------------------------
B_RIM   = (255, 214, 92)           # warm gold rim
B_RIM_H = (255, 244, 180)
B_RIM_D = (196, 146, 36)
B_LENS  = (230, 38, 56)            # classic Lolita red
B_LENS_H = (255, 120, 110)
B_LENS_D = (160, 20, 38)
B_GLINT = (255, 255, 255)


def _draw_B(surf, cx, cy, eye_w, facing=1):
    f = facing
    w = max(7, int(eye_w * 0.62))
    sep = max(4, int(eye_w * 0.46))
    rim = max(2, int(eye_w * 0.085))

    near = (cx + f * (sep // 2), cy - max(1, int(eye_w * 0.02)))
    far  = (cx - f * (sep // 2), cy - max(1, int(eye_w * 0.02)))

    by = cy - max(2, int(w * 0.22))
    pygame.draw.line(surf, B_RIM_D, (far[0], by + 1), (near[0], by + 1), rim + 1)
    pygame.draw.line(surf, B_RIM, (far[0], by), (near[0], by), rim)
    pygame.draw.line(surf, B_RIM_H, (far[0], by - 1), (near[0], by - 1), 1)

    ax = far[0] - f * max(2, int(eye_w * 0.34))
    pygame.draw.line(surf, B_RIM_D, (far[0], cy + 1), (ax, cy - max(1, int(eye_w * 0.06)) + 1), rim + 2)
    pygame.draw.line(surf, B_RIM, (far[0], cy), (ax, cy - max(1, int(eye_w * 0.06))), rim)

    for (lx, ly) in (far, near):
        _fill_heart(surf, lx, ly, w + rim * 2, B_RIM_D)
        _fill_heart(surf, lx, ly, w + rim, B_RIM)
        _fill_heart(surf, lx, ly, w, B_LENS)
        pygame.draw.circle(surf, B_LENS_H,
                           (lx - max(1, int(w * 0.16)), ly - max(1, int(w * 0.10))),
                           max(1, int(w * 0.18)))
        pts = _heart_points(lx, ly + max(1, int(w * 0.14)), w * 0.55)
        pygame.draw.polygon(surf, B_LENS_D, pts[len(pts) // 3: 2 * len(pts) // 3 + 1]
                            + [(lx, ly + max(2, int(w * 0.48)))])
        # Gold rim top-edge highlight ties to the festival look.
        pygame.draw.circle(surf, B_RIM_H, (lx + max(1, int(w * 0.20)), ly - max(1, int(w * 0.18))),
                           max(1, int(eye_w * 0.03)))

    g = max(1, int(eye_w * 0.06))
    pygame.draw.circle(surf, B_GLINT,
                       (near[0] + max(1, int(w * 0.16)), near[1] - max(2, int(w * 0.18))), g)
    # Twin sparkle for the playful festival energy.
    pygame.draw.circle(surf, B_GLINT,
                       (near[0] - max(1, int(w * 0.22)), near[1] + max(1, int(w * 0.04))),
                       max(1, g - 1))


# C · ROSE TINT ----------------------------------------------------------------
C_RIM   = (255, 220, 110)          # slim gold rim
C_RIM_H = (255, 248, 190)
C_RIM_D = (200, 150, 40)
C_TINT  = (255, 120, 175, 130)     # translucent rose — eye shows through
C_TINT_D = (220, 70, 140, 160)
C_TINT_H = (255, 200, 225, 150)
C_GLINT = (255, 255, 255)


def _draw_C(surf, cx, cy, eye_w, facing=1):
    f = facing
    w = max(7, int(eye_w * 0.62))
    sep = max(4, int(eye_w * 0.46))
    rim = max(2, int(eye_w * 0.085))

    near = (cx + f * (sep // 2), cy - max(1, int(eye_w * 0.02)))
    far  = (cx - f * (sep // 2), cy - max(1, int(eye_w * 0.02)))

    by = cy - max(2, int(w * 0.22))
    pygame.draw.line(surf, C_RIM_D, (far[0], by + 1), (near[0], by + 1), rim)
    pygame.draw.line(surf, C_RIM, (far[0], by), (near[0], by), max(1, rim - 1))
    pygame.draw.line(surf, C_RIM_H, (far[0], by - 1), (near[0], by - 1), 1)

    ax = far[0] - f * max(2, int(eye_w * 0.34))
    pygame.draw.line(surf, C_RIM_D, (far[0], cy + 1), (ax, cy - max(1, int(eye_w * 0.06)) + 1), rim + 1)
    pygame.draw.line(surf, C_RIM, (far[0], cy), (ax, cy - max(1, int(eye_w * 0.06))), max(1, rim - 1))

    for (lx, ly) in (far, near):
        # Gold rim ring drawn as filled heart band.
        _fill_heart(surf, lx, ly, w + rim * 2, C_RIM_D)
        _fill_heart(surf, lx, ly, w + rim, C_RIM)
        # Translucent rose lens onto a scratch surface so alpha composites once
        # (avoids stacked-alpha darkening where the heart self-overlaps).
        scratch = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        _fill_heart(scratch, lx, ly, w, C_TINT)
        pts = _heart_points(lx, ly + max(1, int(w * 0.14)), w * 0.55)
        pygame.draw.polygon(scratch, C_TINT_D, pts[len(pts) // 3: 2 * len(pts) // 3 + 1]
                            + [(lx, ly + max(2, int(w * 0.48)))])
        pygame.draw.circle(scratch, C_TINT_H,
                           (lx - max(1, int(w * 0.16)), ly - max(1, int(w * 0.10))),
                           max(1, int(w * 0.18)))
        surf.blit(scratch, (0, 0))
        pygame.draw.circle(surf, C_RIM_H, (lx + max(1, int(w * 0.20)), ly - max(1, int(w * 0.18))),
                           max(1, int(eye_w * 0.03)))

    g = max(1, int(eye_w * 0.07))
    pygame.draw.circle(surf, C_GLINT,
                       (near[0] + max(1, int(w * 0.16)), near[1] - max(2, int(w * 0.18))), g)


VARIANTS = [
    ("A  HOT PINK", _draw_A),
    ("B  FESTIVAL RED", _draw_B),
    ("C  ROSE TINT", _draw_C),
]
