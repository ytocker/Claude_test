"""STAR SHADES — round-1 exploration set (3 variants).

Three genuinely different takes on novelty rockstar 5-point STAR lenses worn
by side-profile Pip facing right. All share one star geometry tuned with FAT
points (inner/outer ~0.5) so the five points survive the 22px in-game read;
they diverge on lens treatment:

  v1 GOLD MIRROR    — glossy graduated gold (the rockstar benchmark)
  v2 RAINBOW PRISM  — gold rim, prismatic disco-tint lens
  v3 STARS & STRIPES— Americana red lens with a white star-in-a-star core

Each is a standalone ``draw_shades(surf, cx, cy, eye_w, facing=1)`` matching
the production contract so the render harness can drop any of them onto Pip or
a product canvas unchanged. The chosen variant is copied verbatim into
``docs/shades/shades_star/draw.py``.
"""
import math
import pygame

# ── shared star geometry ─────────────────────────────────────────────────────
# A point straight up reads most clearly as "a star" at tiny sizes, so rot puts
# vertex 0 at the top. inner=0.5 keeps the points FAT (a spindly 0.38-inner star
# loses its arms to the 1px floor at eye_w=22); 0.5 still scans unmistakably as
# a 5-point star while covering the eye cleanly.
_INNER = 0.50
_ROT   = -math.pi / 2


def _star_pts(cx, cy, r, inner=_INNER, rot=_ROT):
    pts = []
    for i in range(10):
        rad = r if i % 2 == 0 else r * inner
        a = rot + i * math.pi / 5
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return pts


def _star(surf, cx, cy, r, color, inner=_INNER, rot=_ROT, width=0):
    pygame.draw.polygon(surf, color, _star_pts(cx, cy, r, inner, rot), width)


def _star_clip_fill(surf, cx, cy, r, top_col, bot_col, inner=_INNER, rot=_ROT):
    """Fill a star with a vertical top→bottom gradient by masking a gradient
    rectangle to the star polygon. A glassy lens needs a value sweep — bright
    at the top, deeper toward the lower points — or it reads as a flat sticker.
    Done on a local SRCALPHA surface so it composites onto Pip without a halo.
    """
    box = int(math.ceil(r * 2)) + 2
    g = pygame.Surface((box, box), pygame.SRCALPHA)
    for y in range(box):
        t = y / max(1, box - 1)
        col = (
            int(top_col[0] + (bot_col[0] - top_col[0]) * t),
            int(top_col[1] + (bot_col[1] - top_col[1]) * t),
            int(top_col[2] + (bot_col[2] - top_col[2]) * t),
            255,
        )
        g.fill(col, (0, y, box, 1))
    mask = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        _star_pts(box / 2, box / 2, r, inner, rot))
    g.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(g, (int(cx - box / 2), int(cy - box / 2)))


def _arm(surf, far, r, f, col, w):
    """Temple arm hinging off the FAR (ear-side) lens, angled up to the ear."""
    hinge = (far[0] - f * int(r * 0.7), far[1] - int(r * 0.15))
    elbow = (hinge[0] - f * int(r * 0.55), hinge[1] - int(r * 0.45))
    tip   = (elbow[0] - f * int(r * 0.85), elbow[1] - int(r * 0.30))
    pygame.draw.lines(surf, col, False, [hinge, elbow, tip], w)


def _bridge_and_arm(surf, near, far, r, f, frame, frame_hi, w):
    """Shared metal furniture: a bridge spanning the two star lenses plus the
    temple arm. Kept thin (rockstar wire frames) but >=1px so it survives 22px.
    """
    # Bridge — slight dip in the middle like real wire frames.
    bx0 = far[0] + f * int(r * 0.55)
    bx1 = near[0] - f * int(r * 0.55)
    midx = (bx0 + bx1) // 2
    pygame.draw.lines(surf, frame, False,
                      [(bx0, far[1]), (midx, far[1] + max(1, int(r * 0.12))),
                       (bx1, near[1])], w)
    pygame.draw.line(surf, frame_hi, (bx0, far[1] - 1), (bx1, near[1] - 1),
                     max(1, w - 1))
    _arm(surf, far, r, f, frame, w)


# ── geometry constants shared by all three variants ──────────────────────────

def _layout(cx, cy, eye_w, f):
    r   = max(3, int(eye_w * 0.40))      # star outer radius — fat enough to cover the eye
    sep = max(5, int(eye_w * 0.52))      # centre-to-centre spread of the two stars
    near = (cx + f * (sep // 2), cy)
    far  = (cx - f * (sep // 2), cy)
    return r, near, far


# ═════════════════════════════════════════════════════════════════════════════
# v1 · GOLD MIRROR — the rockstar benchmark.
#   Graduated gold glass (hot ivory-gold top → deep amber lower points), one
#   thin ivory rim, a bright diagonal sheen streak across each lens, and a
#   single hero sparkle on the near lens. This is the "obvious" star shade.
# ═════════════════════════════════════════════════════════════════════════════
_G_RIM    = (255, 244, 200)
_G_TOP    = (255, 232, 130)
_G_BOT    = (214, 150, 36)
_G_SHEEN  = (255, 252, 235)
_G_FRAME  = (236, 196, 70)
_G_FR_HI  = (255, 240, 170)
_G_GLINT  = (255, 255, 255)


def draw_shades_gold(surf, cx, cy, eye_w, facing=1):
    f = facing
    r, near, far = _layout(cx, cy, eye_w, f)
    rim = max(1, int(eye_w * 0.07))

    for (lx, ly) in (far, near):
        _star(surf, lx, ly, r + rim, _G_RIM)               # ivory rim
        _star_clip_fill(surf, lx, ly, r, _G_TOP, _G_BOT)   # graduated gold glass
        # Diagonal mirror sheen across the upper-left of the lens.
        sheen_w = max(1, int(r * 0.20))
        pygame.draw.line(surf, _G_SHEEN,
                         (lx - int(r * 0.45), ly - int(r * 0.10)),
                         (lx + int(r * 0.05), ly - int(r * 0.60)), sheen_w)

    _bridge_and_arm(surf, near, far, r, f, _G_FRAME, _G_FR_HI, rim + 1)

    # Hero sparkle on the near lens — a 4-point twinkle + core dot.
    gx, gy = near[0] - f * int(r * 0.30), near[1] - int(r * 0.32)
    gr = max(2, int(r * 0.34))
    pygame.draw.polygon(surf, _G_GLINT,
                        [(gx, gy - gr), (gx + max(1, gr // 3), gy),
                         (gx, gy + gr), (gx - max(1, gr // 3), gy)])
    pygame.draw.polygon(surf, _G_GLINT,
                        [(gx - gr, gy), (gx, gy - max(1, gr // 3)),
                         (gx + gr, gy), (gx, gy + max(1, gr // 3))])
    pygame.draw.circle(surf, _G_GLINT, (gx, gy), max(1, int(r * 0.12)))


# ═════════════════════════════════════════════════════════════════════════════
# v2 · RAINBOW PRISM — disco-funk rockstar.
#   Gold wire frame, but each star lens carries a prismatic rainbow sweep
#   (the mirrored-lens spectrum). Tints are kept value-bright so the star still
#   reads as glass, not a painted blob; a white spark sits top-front.
# ═════════════════════════════════════════════════════════════════════════════
_P_RIM    = (255, 246, 210)
_P_FRAME  = (240, 200, 76)
_P_FR_HI  = (255, 240, 170)
_P_GLINT  = (255, 255, 255)
# Spectrum stops sweep top→bottom through the lens; saturated but light enough
# that each band still reads as "shiny glass" at tiny size.
_P_BANDS  = [
    (255, 120, 150),   # rose
    (255, 180, 90),    # amber
    (255, 240, 110),   # gold
    (140, 230, 150),   # mint
    (130, 195, 255),   # sky
    (190, 150, 255),   # violet
]


def _prism_fill(surf, cx, cy, r, inner=_INNER, rot=_ROT):
    box = int(math.ceil(r * 2)) + 2
    g = pygame.Surface((box, box), pygame.SRCALPHA)
    n = len(_P_BANDS)
    for y in range(box):
        t = y / max(1, box - 1) * (n - 1)
        i0 = int(t)
        i1 = min(n - 1, i0 + 1)
        frac = t - i0
        a, b = _P_BANDS[i0], _P_BANDS[i1]
        col = (int(a[0] + (b[0] - a[0]) * frac),
               int(a[1] + (b[1] - a[1]) * frac),
               int(a[2] + (b[2] - a[2]) * frac), 255)
        g.fill(col, (0, y, box, 1))
    mask = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        _star_pts(box / 2, box / 2, r, inner, rot))
    g.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(g, (int(cx - box / 2), int(cy - box / 2)))


def draw_shades_rainbow(surf, cx, cy, eye_w, facing=1):
    f = facing
    r, near, far = _layout(cx, cy, eye_w, f)
    rim = max(1, int(eye_w * 0.07))

    for (lx, ly) in (far, near):
        _star(surf, lx, ly, r + rim, _P_RIM)
        _prism_fill(surf, lx, ly, r)
        # A bright horizontal mirror band keeps the "spectrum on glass" read.
        pygame.draw.line(surf, (255, 255, 255),
                         (lx - int(r * 0.5), ly - int(r * 0.05)),
                         (lx + int(r * 0.5), ly - int(r * 0.05)),
                         max(1, int(r * 0.14)))
        # Thin gold inner rim so the spectrum doesn't bleed into the ivory rim.
        _star(surf, lx, ly, r, _P_FRAME, width=max(1, int(eye_w * 0.04)))

    _bridge_and_arm(surf, near, far, r, f, _P_FRAME, _P_FR_HI, rim + 1)

    sx, sy = near[0] - f * int(r * 0.28), near[1] - int(r * 0.42)
    sr = max(2, int(r * 0.30))
    pygame.draw.polygon(surf, _P_GLINT,
                        [(sx, sy - sr), (sx + max(1, sr // 3), sy),
                         (sx, sy + sr), (sx - max(1, sr // 3), sy)])
    pygame.draw.polygon(surf, _P_GLINT,
                        [(sx - sr, sy), (sx, sy - max(1, sr // 3)),
                         (sx + sr, sy), (sx, sy + max(1, sr // 3))])


# ═════════════════════════════════════════════════════════════════════════════
# v3 · STARS & STRIPES — Americana rockstar.
#   Deep glossy crimson star lens with a small WHITE star nested at its core
#   (star-in-a-star), wrapped in a bright gold rim. A blue-white spark replaces
#   the usual glint. Bold, instantly "star-spangled" novelty read.
# ═════════════════════════════════════════════════════════════════════════════
_S_RIM    = (255, 244, 190)
_S_TOP    = (236, 72, 78)
_S_BOT    = (158, 26, 40)
_S_WHITE  = (252, 250, 248)
_S_WH_SH  = (210, 214, 230)
_S_FRAME  = (244, 200, 74)
_S_FR_HI  = (255, 240, 170)
_S_SPARK  = (235, 244, 255)


def draw_shades_stripes(surf, cx, cy, eye_w, facing=1):
    f = facing
    r, near, far = _layout(cx, cy, eye_w, f)
    rim = max(1, int(eye_w * 0.07))

    for (lx, ly) in (far, near):
        _star(surf, lx, ly, r + rim, _S_RIM)                  # gold-ivory rim
        _star_clip_fill(surf, lx, ly, r, _S_TOP, _S_BOT)      # crimson glass
        # Nested white core star — the patriotic star-in-a-star signature.
        core = max(2, int(r * 0.50))
        _star(surf, lx, ly + max(1, int(r * 0.04)), core, _S_WH_SH)
        _star(surf, lx, ly, max(2, int(r * 0.46)), _S_WHITE)
        # Tiny crimson pip at the very centre so the white star reads as a ring
        # of points, not a solid blob, when it shrinks.
        if r >= 7:
            _star(surf, lx, ly, max(1, int(r * 0.16)), _S_TOP)

    _bridge_and_arm(surf, near, far, r, f, _S_FRAME, _S_FR_HI, rim + 1)

    # Blue-white spark on the near upper point.
    sx, sy = near[0] - f * int(r * 0.18), near[1] - int(r * 0.55)
    sr = max(2, int(r * 0.26))
    pygame.draw.polygon(surf, _S_SPARK,
                        [(sx, sy - sr), (sx + max(1, sr // 3), sy),
                         (sx, sy + sr), (sx - max(1, sr // 3), sy)])
    pygame.draw.circle(surf, _S_SPARK, (sx, sy), max(1, int(r * 0.10)))


# Convenience registry for the harness.
VARIANTS = [
    ("v1 GOLD MIRROR",     draw_shades_gold),
    ("v2 RAINBOW PRISM",   draw_shades_rainbow),
    ("v3 STARS & STRIPES", draw_shades_stripes),
]
