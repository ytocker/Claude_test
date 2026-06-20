"""SHOES category for Pip's coin Store — ~10 stylized procedural homages of
iconic sneakers + sandals, drawn entirely from pygame primitives.

These are HOMAGES in the spirit of the game's KFC theme: each shoe evokes a
silhouette + colorway and a single signature cue (shell toe, side stripe,
air window, high-top collar, checkerboard), never an exact trademarked mark.

Architecture — each shoe is defined ONCE as a side-profile core:

    _draw_<shoe>(surf, x, y, w, h, facing=1)

renders a single sneaker (toe pointing right when facing=1) filling a box at
(x, y, w, h). Everything downstream reuses that one core:

  * ICON   = the core drawn BIG, centred, then run through parrot._add_outline
             for house consistency. Stored in ICONS[id].
  * IN-GAME = a paint_fn that draws the core SMALL at BOTH of Pip's feet,
             wrapped by store_skins._make_skin into the standard
             (frame_idx, tilt) -> Surface getter. Stored in BUILDERS[id].

Foot anchors (COMPOSITE space, store_skins): the base macaw sits at (0,20);
its bare feet are two tiny lines near x≈26–36, y≈65–69. So the in-game shoes
are drawn centred on (29,67) and (35,67), each ~12px wide, covering the bare
foot tucks. In-game Pip is ~40px, so the foot shoes only need to read as
colored footwear — the product-shot ICON is where the recognisable detail goes.

Liftable as `game/shoe_skins.py`: ICONS + BUILDERS keys are the catalog ids.
"""
import math
import pygame

from game import parrot
from game.parrot import _add_outline
from game.store_skins import _make_skin, COMPOSITE_W, COMPOSITE_H


# ── shared sole/draw helpers ──────────────────────────────────────────────────
# The core draws into a box (x, y, w, h). To keep each shoe readable at BOTH
# the 130px hero and the ~12px foot, geometry is expressed as fractions of the
# box so it scales cleanly, and stroke widths are clamped to >=1px.

def _px(w, frac, lo=1):
    """Box-relative pixel width, never thinner than `lo` so detail survives
    the downscale to foot size."""
    return max(lo, int(round(w * frac)))


def _fx(facing, x, cx):
    """Mirror an x about the box centre when facing left, so the same core
    geometry serves both feet / both store orientations."""
    return x if facing >= 0 else (2 * cx - x)


def _scale_pts(pts, x, y, w, h, facing, cx):
    """Map a list of (u, v) unit-box coords [0..1] to device pixels, applying
    the facing mirror in unit space about u=0.5."""
    out = []
    for u, v in pts:
        if facing < 0:
            u = 1.0 - u
        out.append((x + u * w, y + v * h))
    return out


def _poly_u(surf, color, pts, x, y, w, h, facing):
    pygame.draw.polygon(surf, color, _scale_pts(pts, x, y, w, h, facing, None))


def _line_u(surf, color, a, b, x, y, w, h, facing, width):
    pa = _scale_pts([a], x, y, w, h, facing, None)[0]
    pb = _scale_pts([b], x, y, w, h, facing, None)[0]
    pygame.draw.line(surf, color, pa, pb, width)


def _u(u, v, x, y, w, h, facing):
    if facing < 0:
        u = 1.0 - u
    return (int(round(x + u * w)), int(round(y + v * h)))


def _sole(surf, x, y, w, h, facing, sole_col, sole_dark, *, thick=0.20,
          toe_round=True):
    """Generic outsole slab hugging the bottom of the box, with a slightly
    lifted toe spring. The sneakers stack their upper on top of this."""
    top = 1.0 - thick
    pts = [(0.04, top), (0.10, top - 0.05) if toe_round else (0.10, top),
           (0.96, top - 0.02), (0.99, top + 0.04),
           (0.95, 0.99), (0.06, 0.99), (0.02, top + 0.05)]
    _poly_u(surf, sole_dark, pts, x, y, w, h, facing)
    inner = [(0.06, top + 0.02), (0.95, top + 0.02),
             (0.95, 0.95), (0.07, 0.95)]
    _poly_u(surf, sole_col, inner, x, y, w, h, facing)


# ══════════════════════════════════════════════════════════════════════════════
# SHOE CORES — one _draw_<shoe>(surf, x, y, w, h, facing=1) each.
# Toe points RIGHT at facing=1. Box is the product-shot frame (~120×80 / aspect
# ~3:2); the same proportions hold when drawn tiny at a foot.
# ══════════════════════════════════════════════════════════════════════════════

# 1 · AIR FLYER — white chunky low-top, thick sole, subtle curved side accent.
_AF_WHITE  = (245, 245, 242)
_AF_SHADE  = (208, 208, 204)
_AF_SOLE   = (236, 236, 232)
_AF_SOLED  = (188, 188, 184)
_AF_ACCENT = (210, 210, 208)
_AF_LACE   = (224, 224, 220)


def _draw_airflyer(surf, x, y, w, h, facing=1):
    # Thick stacked sole — the AF signature chunk.
    _sole(surf, x, y, w, h, facing, _AF_SOLE, _AF_SOLED, thick=0.26)
    # Mid-sole pinstripe.
    _line_u(surf, _AF_SOLED, (0.06, 0.80), (0.95, 0.80), x, y, w, h, facing,
            _px(h, 0.04))
    # Bulky rounded upper.
    upper = [(0.07, 0.78), (0.07, 0.42), (0.16, 0.30), (0.40, 0.26),
             (0.66, 0.30), (0.86, 0.40), (0.95, 0.55), (0.96, 0.78)]
    _poly_u(surf, _AF_SHADE, upper, x, y, w, h, facing)
    upper2 = [(0.09, 0.76), (0.09, 0.44), (0.17, 0.33), (0.40, 0.29),
              (0.64, 0.33), (0.84, 0.42), (0.93, 0.56), (0.93, 0.76)]
    _poly_u(surf, _AF_WHITE, upper2, x, y, w, h, facing)
    # Subtle curved side accent (the swoosh-evoking arc, kept tonal not a mark).
    arc = [_u(0.30, 0.70, x, y, w, h, facing), _u(0.48, 0.52, x, y, w, h, facing),
           _u(0.74, 0.44, x, y, w, h, facing), _u(0.86, 0.50, x, y, w, h, facing)]
    pygame.draw.lines(surf, _AF_ACCENT, False, arc, _px(w, 0.05))
    # Collar + tongue notch.
    _poly_u(surf, _AF_SHADE, [(0.13, 0.40), (0.30, 0.30), (0.34, 0.40),
                              (0.18, 0.48)], x, y, w, h, facing)
    # Lace bars.
    for lv in (0.40, 0.48, 0.56):
        _line_u(surf, _AF_LACE, (0.34, lv), (0.50, lv - 0.04), x, y, w, h,
                facing, _px(h, 0.05))
    # Toe cap seam.
    _line_u(surf, _AF_SHADE, (0.72, 0.40), (0.90, 0.56), x, y, w, h, facing,
            _px(w, 0.03))


# 2 · RETRO 1 — red/black/white high-top, ankle collar.
_R1_RED    = (196, 40, 46)
_R1_RED_D  = (150, 26, 32)
_R1_BLACK  = (34, 32, 38)
_R1_BLACKH = (70, 66, 74)
_R1_WHITE  = (242, 240, 236)
_R1_SOLE   = (236, 234, 230)
_R1_SOLED  = (180, 178, 174)


def _draw_retro1(surf, x, y, w, h, facing=1):
    _sole(surf, x, y, w, h, facing, _R1_SOLE, _R1_SOLED, thick=0.16)
    # Red outsole accent band sitting on the white sole.
    _line_u(surf, _R1_RED, (0.05, 0.83), (0.96, 0.83), x, y, w, h, facing,
            _px(h, 0.06))
    # High-top upper — tall ankle collar is the RETRO 1 tell.
    upper = [(0.08, 0.82), (0.08, 0.30), (0.16, 0.16), (0.30, 0.12),
             (0.40, 0.20), (0.42, 0.40), (0.70, 0.34), (0.90, 0.46),
             (0.95, 0.62), (0.95, 0.82)]
    _poly_u(surf, _R1_WHITE, upper, x, y, w, h, facing)
    # Black toe + black ankle panels (the colour-blocking that reads).
    _poly_u(surf, _R1_BLACK, [(0.62, 0.40), (0.90, 0.48), (0.95, 0.64),
                              (0.95, 0.82), (0.70, 0.82), (0.66, 0.56)],
            x, y, w, h, facing)
    _poly_u(surf, _R1_BLACK, [(0.08, 0.30), (0.30, 0.12), (0.40, 0.20),
                              (0.40, 0.34), (0.20, 0.40), (0.08, 0.44)],
            x, y, w, h, facing)
    # Red mid panel swoosh-evoking sweep.
    _poly_u(surf, _R1_RED, [(0.34, 0.52), (0.58, 0.40), (0.74, 0.50),
                            (0.56, 0.62), (0.38, 0.66)], x, y, w, h, facing)
    _line_u(surf, _R1_RED_D, (0.34, 0.52), (0.74, 0.50), x, y, w, h, facing,
            _px(w, 0.02))
    # Ankle collar opening + tongue.
    _poly_u(surf, _R1_BLACKH, [(0.16, 0.20), (0.34, 0.16), (0.36, 0.30),
                               (0.18, 0.34)], x, y, w, h, facing)
    # Lace eyelets.
    for lv in (0.30, 0.40, 0.50, 0.60):
        pygame.draw.circle(surf, _R1_WHITE,
                           _u(0.30, lv, x, y, w, h, facing), _px(w, 0.02))


# 3 · AIR BUBBLE — runner with a visible translucent air window in the heel.
_AB_GREY   = (96, 102, 116)
_AB_GREYH  = (140, 148, 164)
_AB_WHITE  = (236, 238, 240)
_AB_SOLE   = (224, 226, 230)
_AB_SOLED  = (168, 172, 180)
_AB_ACCENT = (240, 110, 60)


def _draw_airbubble(surf, x, y, w, h, facing=1):
    # Sole, but leave the heel for the air window.
    _line_u(surf, _AB_SOLED, (0.30, 0.97), (0.96, 0.93), x, y, w, h, facing,
            _px(h, 0.10))
    _line_u(surf, _AB_SOLE, (0.30, 0.95), (0.96, 0.91), x, y, w, h, facing,
            _px(h, 0.06))
    # Heel block housing the bubble.
    _poly_u(surf, _AB_SOLED, [(0.02, 0.76), (0.30, 0.78), (0.30, 0.99),
                              (0.04, 0.99)], x, y, w, h, facing)
    # Translucent air window — a ring + soft fill is the hero cue.
    win = pygame.Surface((w, h), pygame.SRCALPHA)
    cx_w, cy_w = _u(0.15, 0.86, 0, 0, w, h, facing)
    rr = _px(w, 0.07, 3)
    pygame.draw.circle(win, (190, 220, 240, 150), (cx_w, cy_w), rr)
    pygame.draw.circle(win, (255, 255, 255, 220), (cx_w, cy_w), rr, _px(w, 0.02))
    pygame.draw.circle(win, (255, 255, 255, 230),
                       (cx_w - rr // 2, cy_w - rr // 2), _px(w, 0.015, 1))
    surf.blit(win, (x, y))
    # Runner upper — sleek, swept-back.
    upper = [(0.06, 0.78), (0.10, 0.46), (0.26, 0.34), (0.52, 0.30),
             (0.78, 0.36), (0.93, 0.50), (0.95, 0.74), (0.30, 0.76)]
    _poly_u(surf, _AB_GREY, upper, x, y, w, h, facing)
    upper2 = [(0.12, 0.72), (0.16, 0.46), (0.30, 0.37), (0.52, 0.34),
              (0.74, 0.40), (0.88, 0.52), (0.90, 0.70)]
    _poly_u(surf, _AB_GREYH, upper2, x, y, w, h, facing)
    # Bright accent swoosh-sweep toward the heel bubble.
    acc = [_u(0.86, 0.48, x, y, w, h, facing), _u(0.55, 0.60, x, y, w, h, facing),
           _u(0.30, 0.70, x, y, w, h, facing)]
    pygame.draw.lines(surf, _AB_ACCENT, False, acc, _px(w, 0.045))
    # Collar + laces.
    _poly_u(surf, _AB_WHITE, [(0.16, 0.44), (0.34, 0.36), (0.38, 0.46),
                              (0.20, 0.52)], x, y, w, h, facing)
    for lv in (0.44, 0.52, 0.60):
        _line_u(surf, _AB_WHITE, (0.36, lv), (0.52, lv - 0.04), x, y, w, h,
                facing, _px(h, 0.04))


# 4 · SHELL TOE — white low-top, rubber shell toe cap + 3 dark side stripes.
_ST_WHITE  = (244, 244, 240)
_ST_SHADE  = (212, 212, 208)
_ST_SHELL  = (250, 250, 248)
_ST_STRIPE = (38, 36, 42)
_ST_SOLE   = (232, 230, 226)
_ST_SOLED  = (176, 174, 170)


def _draw_shelltoe(surf, x, y, w, h, facing=1):
    _sole(surf, x, y, w, h, facing, _ST_SOLE, _ST_SOLED, thick=0.16)
    # Upper.
    upper = [(0.08, 0.80), (0.08, 0.42), (0.18, 0.32), (0.42, 0.28),
             (0.66, 0.32), (0.84, 0.42), (0.92, 0.56), (0.93, 0.80)]
    _poly_u(surf, _ST_SHADE, upper, x, y, w, h, facing)
    upper2 = [(0.10, 0.78), (0.10, 0.44), (0.19, 0.35), (0.42, 0.31),
              (0.64, 0.35), (0.82, 0.44), (0.90, 0.57), (0.90, 0.78)]
    _poly_u(surf, _ST_WHITE, upper2, x, y, w, h, facing)
    # THE SHELL TOE — rubber cap with the signature scalloped perforation row.
    shell = [(0.66, 0.40), (0.84, 0.46), (0.93, 0.62), (0.93, 0.82),
             (0.66, 0.82), (0.64, 0.58)]
    _poly_u(surf, _ST_SHELL, shell, x, y, w, h, facing)
    _line_u(surf, _ST_SOLED, (0.66, 0.42), (0.66, 0.82), x, y, w, h, facing,
            _px(w, 0.02))
    # Punched dots along the shell ridge.
    for du in (0.72, 0.80, 0.88):
        pygame.draw.circle(surf, _ST_SOLED,
                           _u(du, 0.50 + (du - 0.72) * 0.5, x, y, w, h, facing),
                           _px(w, 0.012, 1))
    # THREE dark side stripes (stylised, slanted — the adidas tell).
    for i, su in enumerate((0.30, 0.40, 0.50)):
        _line_u(surf, _ST_STRIPE, (su, 0.36), (su - 0.06, 0.74),
                x, y, w, h, facing, _px(w, 0.045))
    # Heel tab.
    _poly_u(surf, _ST_STRIPE, [(0.08, 0.40), (0.16, 0.36), (0.16, 0.46),
                               (0.08, 0.48)], x, y, w, h, facing)


# 5 · COURT GREEN — white tennis low-top with a green heel tab.
_CG_WHITE  = (244, 244, 240)
_CG_SHADE  = (214, 214, 210)
_CG_GREEN  = (40, 120, 72)
_CG_GREEND = (28, 90, 54)
_CG_SOLE   = (236, 234, 230)
_CG_SOLED  = (182, 180, 176)
_CG_PERF   = (200, 200, 196)


def _draw_courtgreen(surf, x, y, w, h, facing=1):
    _sole(surf, x, y, w, h, facing, _CG_SOLE, _CG_SOLED, thick=0.14)
    # Clean minimal tennis upper.
    upper = [(0.08, 0.82), (0.08, 0.40), (0.18, 0.30), (0.44, 0.26),
             (0.70, 0.30), (0.88, 0.42), (0.94, 0.58), (0.94, 0.82)]
    _poly_u(surf, _CG_SHADE, upper, x, y, w, h, facing)
    upper2 = [(0.10, 0.80), (0.10, 0.42), (0.19, 0.33), (0.44, 0.29),
              (0.68, 0.33), (0.85, 0.44), (0.91, 0.59), (0.91, 0.80)]
    _poly_u(surf, _CG_WHITE, upper2, x, y, w, h, facing)
    # GREEN HEEL TAB — the Stan-Smith tell, at the back.
    _poly_u(surf, _CG_GREEN, [(0.08, 0.40), (0.18, 0.36), (0.18, 0.62),
                              (0.08, 0.64)], x, y, w, h, facing)
    _line_u(surf, _CG_GREEND, (0.08, 0.40), (0.18, 0.36), x, y, w, h, facing,
            _px(w, 0.015))
    # Signature perforation cluster (three columns of dots) where the stripes
    # would be — keeps it a tennis shoe, not a stripe shoe.
    for cu in (0.34, 0.42, 0.50):
        for dv in (0.42, 0.52, 0.62):
            pygame.draw.circle(surf, _CG_PERF,
                               _u(cu, dv, x, y, w, h, facing), _px(w, 0.012, 1))
    # Laces.
    for lv in (0.38, 0.46, 0.54):
        _line_u(surf, _CG_SHADE, (0.30, lv), (0.46, lv - 0.04), x, y, w, h,
                facing, _px(h, 0.04))
    # Green outsole edge hint at the toe.
    _line_u(surf, _CG_GREEN, (0.74, 0.80), (0.92, 0.74), x, y, w, h, facing,
            _px(h, 0.03))


# 6 · BOOST KNIT — sand/beige knit runner, chunky ribbed boost sole.
_BK_SAND   = (214, 196, 168)
_BK_SANDD  = (176, 156, 128)
_BK_SANDH  = (236, 222, 198)
_BK_SOLE   = (244, 240, 232)
_BK_SOLED  = (206, 200, 188)
_BK_STRIPE = (180, 160, 134)


def _draw_boostknit(surf, x, y, w, h, facing=1):
    # CHUNKY RIBBED BOOST SOLE — tall, with vertical rib ticks (the tell).
    sole_top = 0.66
    _poly_u(surf, _BK_SOLED, [(0.02, sole_top), (0.97, sole_top - 0.02),
                              (0.99, 0.99), (0.02, 0.99)], x, y, w, h, facing)
    _poly_u(surf, _BK_SOLE, [(0.04, sole_top + 0.03), (0.95, sole_top + 0.01),
                             (0.96, 0.95), (0.04, 0.95)], x, y, w, h, facing)
    for ru in [0.08 + i * 0.072 for i in range(12)]:
        _line_u(surf, _BK_SOLED, (ru, sole_top + 0.04), (ru, 0.95),
                x, y, w, h, facing, _px(w, 0.012, 1))
    # Sock-like knit upper, low collar, no stiff panels.
    upper = [(0.08, sole_top), (0.10, 0.42), (0.24, 0.30), (0.36, 0.26),
             (0.46, 0.30), (0.50, 0.40), (0.78, 0.36), (0.92, 0.48),
             (0.94, sole_top)]
    _poly_u(surf, _BK_SANDD, upper, x, y, w, h, facing)
    upper2 = [(0.11, sole_top - 0.02), (0.13, 0.44), (0.26, 0.33),
              (0.46, 0.32), (0.50, 0.42), (0.76, 0.40), (0.89, 0.50),
              (0.90, sole_top - 0.02)]
    _poly_u(surf, _BK_SAND, upper2, x, y, w, h, facing)
    # Knit weave texture — diagonal hatch ticks across the upper.
    for hu in [0.16 + i * 0.07 for i in range(9)]:
        _line_u(surf, _BK_STRIPE, (hu, 0.62), (hu + 0.05, 0.40),
                x, y, w, h, facing, 1)
    # Heel cage stripe (the supportive side cage).
    _line_u(surf, _BK_SANDH, (0.10, 0.46), (0.20, 0.62), x, y, w, h, facing,
            _px(w, 0.03))
    # Sock collar opening.
    _poly_u(surf, _BK_SANDH, [(0.22, 0.34), (0.40, 0.28), (0.44, 0.38),
                              (0.26, 0.44)], x, y, w, h, facing)


# 7 · CANVAS HIGH — black/white canvas high-top, white toe cap + rubber foxing.
_CH_BLACK  = (40, 38, 44)
_CH_BLACKH = (78, 74, 82)
_CH_WHITE  = (240, 238, 232)
_CH_CREAM  = (222, 218, 208)
_CH_SOLED  = (190, 186, 178)


def _draw_canvashigh(surf, x, y, w, h, facing=1):
    # Cream rubber foxing strip wraps the whole base (the Chuck tell).
    _poly_u(surf, _CH_SOLED, [(0.04, 0.74), (0.96, 0.70), (0.99, 0.99),
                              (0.04, 0.99)], x, y, w, h, facing)
    _poly_u(surf, _CH_CREAM, [(0.06, 0.72), (0.95, 0.69), (0.96, 0.88),
                              (0.06, 0.90)], x, y, w, h, facing)
    # WHITE TOE CAP — rounded rubber bumper.
    _poly_u(surf, _CH_WHITE, [(0.74, 0.58), (0.88, 0.62), (0.95, 0.72),
                              (0.90, 0.88), (0.72, 0.86), (0.70, 0.70)],
            x, y, w, h, facing)
    _line_u(surf, _CH_SOLED, (0.70, 0.70), (0.74, 0.58), x, y, w, h, facing,
            _px(w, 0.02))
    # Tall black canvas high-top upper.
    upper = [(0.08, 0.74), (0.08, 0.28), (0.16, 0.14), (0.30, 0.10),
             (0.40, 0.18), (0.42, 0.40), (0.70, 0.58), (0.74, 0.72)]
    _poly_u(surf, _CH_BLACK, upper, x, y, w, h, facing)
    # Ankle patch (round badge) — stylised, no mark, just a disc + star.
    bx, by = _u(0.22, 0.32, x, y, w, h, facing)
    pygame.draw.circle(surf, _CH_CREAM, (bx, by), _px(w, 0.08, 3))
    pygame.draw.circle(surf, _CH_BLACK, (bx, by), _px(w, 0.08, 3), _px(w, 0.015))
    pygame.draw.circle(surf, _CH_BLACK, (bx, by), _px(w, 0.025, 1))
    # White collar binding around the ankle opening.
    _poly_u(surf, _CH_WHITE, [(0.14, 0.18), (0.34, 0.12), (0.38, 0.20),
                              (0.18, 0.26)], x, y, w, h, facing)
    # Lace eyelets up the front.
    for lv in (0.26, 0.36, 0.46, 0.56):
        pygame.draw.circle(surf, _CH_WHITE,
                           _u(0.30, lv, x, y, w, h, facing), _px(w, 0.018, 1))


# 8 · CHECKER SLIP — black/white checkerboard slip-on, no laces.
_CS_WHITE  = (240, 238, 232)
_CS_BLACK  = (38, 36, 42)
_CS_SOLE   = (236, 234, 228)
_CS_SOLED  = (184, 182, 176)
_CS_FOX    = (224, 220, 212)


def _draw_checkerslip(surf, x, y, w, h, facing=1):
    _sole(surf, x, y, w, h, facing, _CS_SOLE, _CS_SOLED, thick=0.14)
    # Waffle foxing tick row along the sole edge.
    for fu in [0.10 + i * 0.08 for i in range(11)]:
        _line_u(surf, _CS_SOLED, (fu, 0.84), (fu, 0.92), x, y, w, h, facing, 1)
    # Low slip-on upper, no laces — clean elastic gore at the collar.
    upper = [(0.08, 0.82), (0.08, 0.42), (0.20, 0.32), (0.48, 0.28),
             (0.74, 0.32), (0.90, 0.44), (0.94, 0.60), (0.94, 0.82)]
    _poly_u(surf, _CS_WHITE, upper, x, y, w, h, facing)
    # CHECKERBOARD fill clipped to the upper — the unmistakable tell.
    board = pygame.Surface((w, h), pygame.SRCALPHA)
    n = max(4, int(round(w * 0.11)))  # cell size scales with box
    cols = int(w // n) + 1
    rows = int(h // n) + 1
    for r in range(rows):
        for c in range(cols):
            if (r + c) % 2 == 0:
                pygame.draw.rect(board, _CS_BLACK, (c * n, r * n, n, n))
    # Clip to the upper polygon.
    clip = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(clip, (255, 255, 255, 255),
                        _scale_pts([(0.12, 0.78), (0.12, 0.44), (0.22, 0.35),
                                    (0.48, 0.31), (0.72, 0.35), (0.86, 0.46),
                                    (0.90, 0.60), (0.90, 0.78)],
                                   0, 0, w, h, facing, None))
    board.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(board, (x, y))
    # Elastic gore + collar binding so it reads as a slip-on.
    _poly_u(surf, _CS_FOX, [(0.20, 0.34), (0.44, 0.30), (0.46, 0.40),
                            (0.24, 0.44)], x, y, w, h, facing)
    _line_u(surf, _CS_BLACK, (0.20, 0.34), (0.46, 0.32), x, y, w, h, facing,
            _px(w, 0.02))


# 9 · POOL SLIDES — single-band pool slide with 3 stripes.
_PS_NAVY   = (44, 52, 96)
_PS_NAVYD  = (28, 34, 68)
_PS_NAVYH  = (78, 88, 140)
_PS_WHITE  = (238, 238, 240)
_PS_SOLE   = (60, 68, 110)


def _draw_poolslides(surf, x, y, w, h, facing=1):
    # Thick footbed sole.
    _poly_u(surf, _PS_NAVYD, [(0.06, 0.66), (0.94, 0.62), (0.96, 0.84),
                              (0.90, 0.92), (0.10, 0.92), (0.05, 0.80)],
            x, y, w, h, facing)
    _poly_u(surf, _PS_SOLE, [(0.08, 0.66), (0.92, 0.63), (0.92, 0.80),
                             (0.10, 0.82)], x, y, w, h, facing)
    # Contoured footbed lip.
    _line_u(surf, _PS_NAVYH, (0.10, 0.67), (0.90, 0.64), x, y, w, h, facing,
            _px(h, 0.03))
    # The single wide band arcing over the foot — the slide signature.
    band = [(0.20, 0.66), (0.26, 0.40), (0.42, 0.30), (0.62, 0.30),
            (0.76, 0.42), (0.80, 0.66)]
    _poly_u(surf, _PS_NAVYD, band, x, y, w, h, facing)
    band2 = [(0.24, 0.64), (0.30, 0.42), (0.44, 0.34), (0.60, 0.34),
             (0.72, 0.44), (0.76, 0.64)]
    _poly_u(surf, _PS_NAVY, band2, x, y, w, h, facing)
    # THREE diagonal stripes across the band (the adidas-slide tell).
    for su in (0.40, 0.50, 0.60):
        _line_u(surf, _PS_WHITE, (su, 0.34), (su - 0.06, 0.62),
                x, y, w, h, facing, _px(w, 0.045))


# 10 · FLIP-FLOPS — simple thong sandal.
_FF_RUBBER = (60, 64, 72)
_FF_RUBBERD = (40, 42, 50)
_FF_FOAM   = (210, 80, 70)
_FF_FOAMD  = (168, 56, 50)
_FF_STRAP  = (235, 235, 235)


def _draw_flipflops(surf, x, y, w, h, facing=1):
    # Flat foam footbed.
    _poly_u(surf, _FF_FOAMD, [(0.06, 0.74), (0.94, 0.70), (0.97, 0.84),
                              (0.90, 0.90), (0.10, 0.90), (0.04, 0.82)],
            x, y, w, h, facing)
    _poly_u(surf, _FF_FOAM, [(0.08, 0.74), (0.92, 0.71), (0.92, 0.82),
                             (0.10, 0.84)], x, y, w, h, facing)
    # Dark rubber sole edge.
    _line_u(surf, _FF_RUBBER, (0.06, 0.86), (0.94, 0.82), x, y, w, h, facing,
            _px(h, 0.04))
    # Y-thong strap — two arms to the toe-post (the flip-flop tell).
    post = _u(0.62, 0.74, x, y, w, h, facing)
    a = _u(0.34, 0.48, x, y, w, h, facing)
    b = _u(0.80, 0.50, x, y, w, h, facing)
    pygame.draw.line(surf, _FF_STRAP, a, post, _px(w, 0.05))
    pygame.draw.line(surf, _FF_STRAP, b, post, _px(w, 0.05))
    # Toe-post nub.
    pygame.draw.circle(surf, _FF_STRAP, post, _px(w, 0.03, 1))
    # Strap anchor highlights.
    pygame.draw.circle(surf, _FF_RUBBERD, a, _px(w, 0.02, 1))
    pygame.draw.circle(surf, _FF_RUBBERD, b, _px(w, 0.02, 1))


# Registry of cores so the icon-builder + foot-painter share one source.
_CORES = {
    "skin_shoe_airflyer":   _draw_airflyer,
    "skin_shoe_retro1":     _draw_retro1,
    "skin_shoe_airbubble":  _draw_airbubble,
    "skin_shoe_shelltoe":   _draw_shelltoe,
    "skin_shoe_courtgreen": _draw_courtgreen,
    "skin_shoe_boostknit":  _draw_boostknit,
    "skin_shoe_canvashigh": _draw_canvashigh,
    "skin_shoe_checkerslip": _draw_checkerslip,
    "skin_shoe_poolslides": _draw_poolslides,
    "skin_shoe_flipflops":  _draw_flipflops,
}

NAMES = {
    "skin_shoe_airflyer":   "AIR FLYER",
    "skin_shoe_retro1":     "RETRO 1",
    "skin_shoe_airbubble":  "AIR BUBBLE",
    "skin_shoe_shelltoe":   "SHELL TOE",
    "skin_shoe_courtgreen": "COURT GREEN",
    "skin_shoe_boostknit":  "BOOST KNIT",
    "skin_shoe_canvashigh": "CANVAS HIGH",
    "skin_shoe_checkerslip": "CHECKER SLIP",
    "skin_shoe_poolslides": "POOL SLIDES",
    "skin_shoe_flipflops":  "FLIP-FLOPS",
}


# ── ICON builder (the store thumbnail / Prize-Machine hero) ──────────────────
ICON_W, ICON_H = 128, 96     # generous frame; product box is centred inside

def _build_icon(core):
    """Draw the shoe BIG and centred in a clean frame, then add the house
    1px outline so it matches the rest of the store catalogue."""
    surf = pygame.Surface((ICON_W, ICON_H), pygame.SRCALPHA)
    bw, bh = 116, 76
    bx = (ICON_W - bw) // 2
    by = (ICON_H - bh) // 2 + 2
    # Soft contact shadow grounds the product shot.
    sh = pygame.Surface((bw, 16), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (10, 8, 16, 90), sh.get_rect())
    surf.blit(sh, (bx, by + bh - 14))
    core(surf, bx, by, bw, bh, 1)
    return _add_outline(surf)


# ── IN-GAME foot painter ─────────────────────────────────────────────────────
# Two small shoes covering Pip's bare foot tucks. Left foot points slightly
# back-left, right foot forward — both use facing=1 so the toe reads forward.
_FOOT_W, _FOOT_H = 14, 11


def _make_foot_painter(core):
    def paint(surf, _wing_angle_deg):
        # Right (front) foot — centred ~ (35, 67).
        core(surf, 35 - _FOOT_W // 2, 67 - _FOOT_H + 2, _FOOT_W, _FOOT_H, 1)
        # Left (back) foot — centred ~ (28, 67), drawn first-ish so the front
        # foot overlaps it slightly for depth.
        core(surf, 28 - _FOOT_W // 2, 68 - _FOOT_H + 2, _FOOT_W, _FOOT_H, 1)
    return paint


# ── public registries ────────────────────────────────────────────────────────
ICONS = {sid: _build_icon(core) for sid, core in _CORES.items()}

BUILDERS = {
    sid: _make_skin(_make_foot_painter(core)) for sid, core in _CORES.items()
}
