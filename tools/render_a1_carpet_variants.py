"""Render 5 magic-carpet variants under the locked A1 lotus genie.

Carpet designs researched from popular references:
  1. Aladdin (Disney) — magenta/burgundy with gold zigzag border, tassels
  2. Persian rug — ornate medallion, geometric border, fringe
  3. Royal velvet — purple + gold trim, stars + crescents
  4. Cosmic nebula — deep blue with constellation pattern + glow
  5. Tribal desert — warm earth tones, tribal chevrons + diamonds

The carpet sits under the lotus genie, replacing the smoke aura
that was there before. Same body + arms + face + shines as the
locked variant 2 v5 / shine #1 design — only the lower atmosphere
changes per variant.

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_a1_carpet_variants [tag]
"""
import os, sys, math, random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from tools.render_a1_refined import (
    W, H, SS, PW, PH, SKY, P, s,
    aa_circle, ell, gem_facet,
    draw_torso, draw_neck, draw_head, draw_face,
    draw_earrings, draw_topknot_and_headband, draw_sash,
)
from tools.render_a1_crossed_legs_variants import (
    draw_crossed_legs_ankle_cross,
)
from tools.render_a1_shine_variants import (
    draw_offering_arms_with_shine,
    shine_1_classic_pixie,
)

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_designs")
os.makedirs(OUT_DIR, exist_ok=True)

DISPLAY_SCALE = 2


# ─────────────────────────────────────────────────────────────────────────────
# Common helpers for carpet drawings
# ─────────────────────────────────────────────────────────────────────────────

def _carpet_perspective_quad(cx, cy_top, half_w_front, half_w_back, height):
    """Trapezoidal quad with the FRONT (bottom) edge wider than the
    BACK (top) edge — gives a faux-3D 'tilted toward viewer' look.
    Returns 4 points in clockwise order: TL, TR, BR, BL."""
    return [
        (cx - half_w_back,  cy_top),
        (cx + half_w_back,  cy_top),
        (cx + half_w_front, cy_top + height),
        (cx - half_w_front, cy_top + height),
    ]


def _shadow_oval(big, cx, cy, w, h, alpha=120):
    """Soft elliptical shadow blot below the carpet to sell that it
    floats above the ground."""
    sh = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (10, 12, 30, alpha), (2, 2, w, h))
    big.blit(sh, (cx - w // 2, cy - h // 2))


def _tassel(big, x, y, color_a, color_b, color_tip, length=s(14)):
    """A dangling tassel with a knot ball + 5 hanging threads."""
    aa_circle(big, color_b, x + s(1), y + s(1), s(4))
    aa_circle(big, color_a, x, y, s(3))
    aa_circle(big, color_tip, x - s(1), y - s(1), s(1))
    for dx in (-s(3), -s(1), s(1), s(3), s(5)):
        pygame.draw.line(big, color_a,
                         (x + dx, y + s(2)),
                         (x + dx - s(1), y + length),
                         max(2, s(1)))


# ─────────────────────────────────────────────────────────────────────────────
# Design 1 — Aladdin / Disney style
# ─────────────────────────────────────────────────────────────────────────────

def draw_carpet_aladdin(big, cx):
    """Magenta/burgundy carpet with gold zigzag border, big tassels,
    front edge curling up. Disney Aladdin reference."""
    BURG    = (165,  35,  75)
    BURG_HI = (215,  70, 115)
    BURG_LO = ( 95,  15,  45)
    GOLD    = (245, 205, 105)
    GOLD_HI = (255, 240, 175)
    GOLD_LO = (160, 115,  30)
    BLACK   = ( 18,  14,  10)

    # Soft shadow below
    _shadow_oval(big, cx, s(338), s(220), s(24), alpha=120)

    # Main carpet body (trapezoid, wider at front)
    cy_top  = s(286)
    body = _carpet_perspective_quad(cx, cy_top,
                                    half_w_front=s(140),
                                    half_w_back=s(110),
                                    height=s(42))
    pygame.draw.polygon(big, BURG_LO,
                        [(x + s(2), y + s(2)) for x, y in body])
    pygame.draw.polygon(big, BURG, body)
    # Front-edge curl: a thin dark stripe at the bottom suggesting
    # the carpet folds under itself
    pygame.draw.polygon(big, BURG_LO,
                        [(body[3][0], body[3][1] - s(2)),
                         (body[2][0], body[2][1] - s(2)),
                         (body[2][0] - s(4), body[2][1] + s(6)),
                         (body[3][0] + s(4), body[3][1] + s(6))])
    # Highlight stripe across the top — suggests sheen
    pygame.draw.line(big, BURG_HI,
                     (body[0][0] + s(8), body[0][1] + s(3)),
                     (body[1][0] - s(8), body[1][1] + s(3)),
                     max(2, s(1)))

    # Gold zigzag border around all four sides
    zigzag_step = s(8)
    # Top edge
    pts = []
    for i in range(0, body[1][0] - body[0][0], zigzag_step):
        x = body[0][0] + i
        y = body[0][1] + (s(2) if (i // zigzag_step) % 2 == 0 else s(6))
        pts.append((x, y))
    if len(pts) >= 2:
        pygame.draw.lines(big, GOLD, False, pts, max(2, s(1)))
    # Bottom edge (wider, more zigzags)
    pts = []
    for i in range(0, body[2][0] - body[3][0], zigzag_step):
        x = body[3][0] + i
        y = body[3][1] - (s(2) if (i // zigzag_step) % 2 == 0 else s(6))
        pts.append((x, y))
    if len(pts) >= 2:
        pygame.draw.lines(big, GOLD, False, pts, max(2, s(1)))
    # Side edges — diagonal gold stripes
    for a, b in ((body[0], body[3]), (body[1], body[2])):
        pygame.draw.line(big, GOLD, a, b, max(2, s(1)))

    # Central star/diamond motif
    cs_y = cy_top + s(20)
    pygame.draw.polygon(big, GOLD_LO,
                        [(cx, cs_y - s(10)), (cx + s(10), cs_y),
                         (cx, cs_y + s(10)), (cx - s(10), cs_y)])
    pygame.draw.polygon(big, GOLD,
                        [(cx, cs_y - s(8)), (cx + s(8), cs_y),
                         (cx, cs_y + s(8)), (cx - s(8), cs_y)])
    aa_circle(big, GOLD_HI, cx, cs_y, s(3))

    # 4 corner tassels (gold knot + crimson threads)
    for corner in body:
        _tassel(big, corner[0], corner[1] + s(2),
                color_a=BURG, color_b=BURG_LO, color_tip=GOLD)


# ─────────────────────────────────────────────────────────────────────────────
# Design 2 — Persian rug (ornate medallion + geometric border)
# ─────────────────────────────────────────────────────────────────────────────

def draw_carpet_persian(big, cx):
    """Classic Persian carpet: deep red base, ornate central
    medallion, geometric border pattern, fringe on the short edges."""
    RED      = (140,  35,  40)
    RED_HI   = (190,  55,  65)
    RED_LO   = ( 90,  20,  25)
    DEEP     = ( 50,  18,  20)
    GOLD     = (235, 195, 100)
    GOLD_HI  = (255, 240, 175)
    CREAM    = (240, 220, 170)
    NAVY     = ( 40,  50,  90)
    EMERALD  = ( 65, 160,  85)

    _shadow_oval(big, cx, s(336), s(210), s(20), alpha=110)

    cy_top = s(288)
    body = _carpet_perspective_quad(cx, cy_top,
                                    half_w_front=s(135),
                                    half_w_back=s(110),
                                    height=s(38))
    pygame.draw.polygon(big, RED_LO,
                        [(x + s(2), y + s(2)) for x, y in body])
    pygame.draw.polygon(big, RED, body)

    # Inner navy border (1-unit inset from edge)
    inset = s(6)
    inner = [
        (body[0][0] + inset, body[0][1] + inset),
        (body[1][0] - inset, body[1][1] + inset),
        (body[2][0] - inset, body[2][1] - inset),
        (body[3][0] + inset, body[3][1] - inset),
    ]
    pygame.draw.polygon(big, NAVY, inner)

    # Border-pattern: alternating gold/cream small diamonds along
    # the navy frame
    n = 14
    for i in range(n):
        t = (i + 0.5) / n
        # Top edge
        x = inner[0][0] + (inner[1][0] - inner[0][0]) * t
        y = inner[0][1] + (inner[1][1] - inner[0][1]) * t
        color = GOLD if i % 2 == 0 else CREAM
        pygame.draw.polygon(big, color,
                            [(int(x), int(y)),
                             (int(x) + s(2), int(y) + s(2)),
                             (int(x), int(y) + s(4)),
                             (int(x) - s(2), int(y) + s(2))])
        # Bottom edge
        x = inner[3][0] + (inner[2][0] - inner[3][0]) * t
        y = inner[3][1] + (inner[2][1] - inner[3][1]) * t
        pygame.draw.polygon(big, color,
                            [(int(x), int(y) - s(4)),
                             (int(x) + s(2), int(y) - s(2)),
                             (int(x), int(y)),
                             (int(x) - s(2), int(y) - s(2))])

    # Inner field — deep red
    field_inset = s(11)
    field = [
        (inner[0][0] + field_inset, inner[0][1] + field_inset),
        (inner[1][0] - field_inset, inner[1][1] + field_inset),
        (inner[2][0] - field_inset, inner[2][1] - field_inset),
        (inner[3][0] + field_inset, inner[3][1] - field_inset),
    ]
    pygame.draw.polygon(big, RED, field)

    # Central medallion — ornate gold + navy + emerald
    med_cy = cy_top + s(19)
    # Outer ring (gold)
    pygame.draw.circle(big, GOLD_HI, (cx, med_cy), s(13))
    pygame.draw.circle(big, GOLD,    (cx, med_cy), s(11))
    pygame.draw.circle(big, NAVY,    (cx, med_cy), s(9))
    pygame.draw.circle(big, CREAM,   (cx, med_cy), s(6))
    pygame.draw.circle(big, EMERALD, (cx, med_cy), s(3))
    # 8 radial petals
    for k in range(8):
        ang = math.radians(k * 45)
        tx = cx + math.cos(ang) * s(15)
        ty = med_cy + math.sin(ang) * s(15)
        pygame.draw.line(big, GOLD,
                         (cx + int(math.cos(ang) * s(11)),
                          med_cy + int(math.sin(ang) * s(11))),
                         (int(tx), int(ty)), max(2, s(1)))

    # Fringe on top and bottom edges (short white threads)
    for fx_step in range(int(body[0][0]) - s(2),
                         int(body[1][0]),
                         s(3)):
        pygame.draw.line(big, CREAM,
                         (fx_step, body[0][1] - s(4)),
                         (fx_step, body[0][1] + s(1)),
                         max(1, s(1) // 2))
    for fx_step in range(int(body[3][0]) - s(2),
                         int(body[2][0]),
                         s(3)):
        pygame.draw.line(big, CREAM,
                         (fx_step, body[3][1] - s(1)),
                         (fx_step, body[3][1] + s(4)),
                         max(1, s(1) // 2))


# ─────────────────────────────────────────────────────────────────────────────
# Design 3 — Royal velvet (purple + gold + stars + crescents)
# ─────────────────────────────────────────────────────────────────────────────

def draw_carpet_royal(big, cx):
    """High-end royal velvet carpet — purple base with multiple layers
    of gold trim, an ornate central medallion, scattered stars +
    crescents arranged in a structured pattern, gem inlay corners,
    and detailed pom-pom + thread tassels. NO ground shadow."""
    PURPLE    = ( 80,  35, 130)
    PURPLE_HI = (140,  85, 200)
    PURPLE_MID= (110,  55, 165)
    PURPLE_LO = ( 45,  18,  85)
    PURPLE_DK = ( 25,  10,  50)
    GOLD      = (245, 205, 105)
    GOLD_HI   = (255, 240, 175)
    GOLD_MID  = (220, 175,  70)
    GOLD_LO   = (160, 115,  30)
    GOLD_DK   = (110,  75,  15)
    WHITE     = (250, 245, 230)
    RUBY      = (220,  60,  80)
    RUBY_HI   = (255, 175, 195)
    EMERALD   = ( 65, 180,  95)
    SAPPHIRE  = ( 70, 130, 220)

    cy_top = s(286)
    body = _carpet_perspective_quad(cx, cy_top,
                                    half_w_front=s(140),
                                    half_w_back=s(110),
                                    height=s(42))
    # ── Base velvet body (multi-tone for depth) ─────────────────
    pygame.draw.polygon(big, PURPLE_DK,
                        [(x + s(2), y + s(2)) for x, y in body])
    pygame.draw.polygon(big, PURPLE_LO, body)
    # Mid-tone inset for the velvet's volume
    inset_pad = s(2)
    body_in = [
        (body[0][0] + inset_pad, body[0][1] + inset_pad),
        (body[1][0] - inset_pad, body[1][1] + inset_pad),
        (body[2][0] - inset_pad, body[2][1] - inset_pad),
        (body[3][0] + inset_pad, body[3][1] - inset_pad),
    ]
    pygame.draw.polygon(big, PURPLE, body_in)
    # Velvet sheen — soft alpha highlight bands
    for off_y, alpha_v in ((s(2), 140), (s(8), 90)):
        sheen = pygame.Surface((body[1][0] - body[0][0], s(10)),
                               pygame.SRCALPHA)
        pygame.draw.ellipse(sheen, (*PURPLE_HI, alpha_v),
                            (0, 0, sheen.get_width(), s(10)))
        big.blit(sheen, (body[0][0], body[0][1] + off_y))

    # ── Multi-layer gold border (outer thick + inner thin) ──────
    # Outer thick gold rim
    for a, b in ((body[0], body[1]),
                 (body[1], body[2]),
                 (body[2], body[3]),
                 (body[3], body[0])):
        pygame.draw.line(big, GOLD_DK, a, b, max(5, s(1) + 3))
    for a, b in ((body[0], body[1]),
                 (body[1], body[2]),
                 (body[2], body[3]),
                 (body[3], body[0])):
        pygame.draw.line(big, GOLD, a, b, max(3, s(1) + 1))
    for a, b in ((body[0], body[1]),
                 (body[1], body[2]),
                 (body[2], body[3]),
                 (body[3], body[0])):
        pygame.draw.line(big, GOLD_HI, a, b, max(1, s(1) // 2))
    # Inner thin gold frame (1 unit inset)
    inset1 = s(5)
    inner1 = [
        (body[0][0] + inset1, body[0][1] + inset1),
        (body[1][0] - inset1, body[1][1] + inset1),
        (body[2][0] - inset1 + s(1), body[2][1] - inset1),
        (body[3][0] + inset1 - s(1), body[3][1] - inset1),
    ]
    pygame.draw.lines(big, GOLD_MID, True, inner1, max(2, s(1)))
    # Decorative dot row along the inner frame (small gold beads)
    for j in range(20):
        t = (j + 0.5) / 20
        # Top edge
        bx = int(inner1[0][0] + (inner1[1][0] - inner1[0][0]) * t)
        by = int(inner1[0][1] + (inner1[1][1] - inner1[0][1]) * t)
        aa_circle(big, GOLD_HI, bx, by, max(1, s(1) // 2))
        # Bottom edge
        bx = int(inner1[3][0] + (inner1[2][0] - inner1[3][0]) * t)
        by = int(inner1[3][1] + (inner1[2][1] - inner1[3][1]) * t)
        aa_circle(big, GOLD_HI, bx, by, max(1, s(1) // 2))

    # ── Symmetric motif rows: stars + crescents in pattern ──────
    # Top row of small stars
    for fx in (-s(60), -s(36), s(36), s(60)):
        sx_p = cx + fx
        sy_p = cy_top + s(10)
        r = s(2)
        for dx_p, dy_p in ((r * 2, 0), (-r * 2, 0), (0, r * 2), (0, -r * 2)):
            pygame.draw.line(big, GOLD,
                             (sx_p, sy_p), (sx_p + dx_p, sy_p + dy_p),
                             max(1, s(1)))
        aa_circle(big, WHITE, sx_p, sy_p, max(1, s(1) // 2))
    # Mid row of crescent moons flanking the medallion
    for fx in (-s(38), s(38)):
        mx_p = cx + fx
        my_p = cy_top + s(22)
        pygame.draw.circle(big, GOLD, (mx_p, my_p), s(4))
        pygame.draw.circle(big, PURPLE, (mx_p + s(2), my_p), s(4))
        # Star inside crescent's "open" side
        pygame.draw.circle(big, GOLD_HI, (mx_p + s(5), my_p), max(1, s(1)))
    # Bottom row of paired tiny stars
    for fx in (-s(70), -s(46), -s(22), s(22), s(46), s(70)):
        sx_p = cx + fx
        sy_p = cy_top + s(34)
        aa_circle(big, GOLD, sx_p, sy_p, max(1, s(1)))
        aa_circle(big, WHITE, sx_p - s(1), sy_p - s(1),
                  max(1, s(1) // 2))

    # ── Decorative gold curlicue flourishes along the border ───
    # Small swirls at the corners (between border and motifs)
    for corner_index, corner in enumerate(body):
        cx_f, cy_f = corner
        # Pick swirl direction so curl points inward + downward
        sign_x = -1 if corner[0] > cx else 1
        sign_y = -1 if corner[1] > cy_top + s(20) else 1
        # Drawing a small spiral-ish flourish with 2 arcs
        pygame.draw.arc(big, GOLD,
                        (cx_f + sign_x * s(5) - s(4),
                         cy_f + sign_y * s(5) - s(4),
                         s(8), s(8)),
                        math.radians(0), math.radians(270),
                        max(2, s(1)))
        pygame.draw.arc(big, GOLD_HI,
                        (cx_f + sign_x * s(7) - s(3),
                         cy_f + sign_y * s(7) - s(3),
                         s(6), s(6)),
                        math.radians(0), math.radians(270),
                        max(1, s(1) // 2))

    # ── Corner gem inlays (small gold settings with tiny gems) ─
    for corner, gem_col in zip(
            [body[0], body[1], body[2], body[3]],
            [SAPPHIRE, SAPPHIRE, EMERALD, EMERALD]):
        # Move slightly inward from corner
        gx_p = corner[0] + (s(8) if corner[0] < cx else -s(8))
        gy_p = corner[1] + (s(8) if corner[1] < cy_top + s(20) else -s(8))
        pygame.draw.circle(big, GOLD_DK, (gx_p + s(1), gy_p + s(1)), s(4))
        pygame.draw.circle(big, GOLD, (gx_p, gy_p), s(3))
        gem_facet(big, gx_p, gy_p, s(2), gem_col,
                  RUBY_HI if gem_col == EMERALD else (170, 215, 255),
                  (15, 60, 80))

    # ── Detailed pom-pom + tassel at each corner ───────────────
    for corner in body:
        cxc, cyc = corner
        # Multi-layer pom-pom
        aa_circle(big, GOLD_DK, cxc + s(1), cyc + s(2), s(7))
        aa_circle(big, GOLD_LO, cxc,         cyc + s(1), s(6))
        aa_circle(big, GOLD,    cxc,         cyc,         s(5))
        aa_circle(big, GOLD_HI, cxc - s(2),  cyc - s(2),  s(2))
        # Ruby gem set in the pom-pom
        pygame.draw.circle(big, RUBY, (cxc, cyc + s(1)), s(2))
        pygame.draw.circle(big, RUBY_HI, (cxc - s(1), cyc), s(1))
        # Dangling thread bundle below
        for dx in (-s(4), -s(2), 0, s(2), s(4)):
            pygame.draw.line(big, RUBY,
                             (cxc + dx, cyc + s(6)),
                             (cxc + dx - s(1), cyc + s(18)),
                             max(2, s(1)))
        # Gold thread tips at the bottom of each strand
        for dx in (-s(4), -s(2), 0, s(2), s(4)):
            aa_circle(big, GOLD,
                      cxc + dx - s(1), cyc + s(18),
                      max(1, s(1)))


# ─────────────────────────────────────────────────────────────────────────────
# Design 4 — Cosmic / nebula carpet
# ─────────────────────────────────────────────────────────────────────────────

def draw_carpet_cosmic(big, cx):
    """Deep blue-purple cosmic carpet with a constellation pattern,
    glowing cyan edges, and tiny stars trailing behind / below.
    Looks like a piece of starry sky."""
    NIGHT    = ( 22,  18,  60)
    NIGHT_HI = ( 60,  45, 130)
    NEBULA_PINK   = (200,  70, 160)
    NEBULA_BLUE   = ( 75, 150, 240)
    NEBULA_PURPLE = (135,  70, 200)
    CYAN     = (160, 230, 255)
    WHITE    = (250, 245, 255)
    GOLD     = (255, 220, 130)

    # Soft glow halo beneath (cyan)
    for r_n, alpha in ((s(130), 60), (s(100), 90), (s(75), 110)):
        glow = pygame.Surface((r_n * 2 + 4, r_n + 4), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*CYAN, alpha),
                            (2, 2, r_n * 2, r_n))
        big.blit(glow, (cx - r_n, s(334)))

    cy_top = s(286)
    body = _carpet_perspective_quad(cx, cy_top,
                                    half_w_front=s(138),
                                    half_w_back=s(110),
                                    height=s(42))
    # Dark base
    pygame.draw.polygon(big, (5, 5, 25),
                        [(x + s(2), y + s(2)) for x, y in body])
    pygame.draw.polygon(big, NIGHT, body)

    # Nebula clouds inside
    random.seed(17)
    mask = pygame.Surface((PW, PH), pygame.SRCALPHA)
    for _ in range(28):
        nx = cx + random.randint(-s(72), s(72))
        ny = cy_top + random.randint(s(4), s(38))
        nr = random.randint(s(8), s(18))
        nc = random.choice([NEBULA_PINK, NEBULA_PURPLE, NEBULA_BLUE])
        srf = pygame.Surface((nr * 2 + 4, nr * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(srf, (*nc, 60),
                           (nr + 2, nr + 2), nr)
        mask.blit(srf, (nx - nr - 2, ny - nr - 2))
    # Clip the mask roughly to the carpet polygon by re-drawing
    # the carpet outline OVER the mask afterwards. Simpler: just
    # blit then re-stroke edges.
    big.blit(mask, (0, 0))

    # Star dots scattered across the carpet
    random.seed(23)
    for _ in range(36):
        sx = cx + random.randint(-s(78), s(78))
        sy = cy_top + random.randint(s(4), s(38))
        sr = random.randint(1, max(1, s(1)))
        pygame.draw.circle(big, WHITE, (sx, sy), sr)
    # A few bigger sparkle stars
    for _ in range(6):
        sx = cx + random.randint(-s(70), s(70))
        sy = cy_top + random.randint(s(6), s(36))
        r = s(2)
        pygame.draw.line(big, CYAN, (sx - r * 2, sy),
                         (sx + r * 2, sy), max(1, s(1)))
        pygame.draw.line(big, CYAN, (sx, sy - r * 2),
                         (sx, sy + r * 2), max(1, s(1)))
        aa_circle(big, WHITE, sx, sy, max(1, s(1) // 2))

    # Glowing cyan edge stroke
    pygame.draw.lines(big, CYAN, True, body, max(2, s(1)))
    pygame.draw.lines(big, WHITE, True, body, max(1, s(1) // 2))

    # 4 corner sparkle stars (instead of tassels)
    for corner in body:
        r = s(3)
        cxc, cyc = corner[0], corner[1] + s(2)
        pygame.draw.line(big, GOLD, (cxc - r * 2, cyc),
                         (cxc + r * 2, cyc), max(2, s(1)))
        pygame.draw.line(big, GOLD, (cxc, cyc - r * 2),
                         (cxc, cyc + r * 2), max(2, s(1)))
        aa_circle(big, WHITE, cxc, cyc, max(1, s(1)))


# ─────────────────────────────────────────────────────────────────────────────
# Design 5 — Tribal / desert carpet (Bedouin style)
# ─────────────────────────────────────────────────────────────────────────────

def draw_carpet_tribal(big, cx):
    """Warm earth-tone carpet with chevron + diamond tribal pattern,
    leather-look tassels. Rugged / practical look."""
    OCHRE    = (185, 110,  55)
    OCHRE_HI = (220, 155,  85)
    OCHRE_LO = (125,  65,  25)
    BROWN    = ( 95,  55,  30)
    DEEP     = ( 50,  25,  10)
    CREAM    = (235, 215, 175)
    TEAL     = ( 65, 130, 130)
    RUST     = (180,  75,  45)

    _shadow_oval(big, cx, s(338), s(210), s(22), alpha=120)

    cy_top = s(288)
    body = _carpet_perspective_quad(cx, cy_top,
                                    half_w_front=s(135),
                                    half_w_back=s(108),
                                    height=s(40))
    pygame.draw.polygon(big, OCHRE_LO,
                        [(x + s(2), y + s(2)) for x, y in body])
    pygame.draw.polygon(big, OCHRE, body)

    # Chevron pattern across the centre
    chevron_y_top = cy_top + s(6)
    chevron_y_bot = cy_top + s(28)
    n_chevrons = 5
    for i in range(n_chevrons):
        t = (i + 0.5) / n_chevrons
        x_left = body[0][0] + (body[1][0] - body[0][0]) * t - s(8)
        x_right = body[0][0] + (body[1][0] - body[0][0]) * t + s(8)
        x_mid = (x_left + x_right) // 2
        color = RUST if i % 2 == 0 else TEAL
        # V chevron
        pygame.draw.lines(big, color, False,
                          [(int(x_left), chevron_y_top),
                           (int(x_mid), chevron_y_bot),
                           (int(x_right), chevron_y_top)],
                          max(2, s(1)))

    # Diamond pattern between chevrons (small accent)
    for i in range(n_chevrons - 1):
        t = (i + 1) / n_chevrons
        x = body[0][0] + (body[1][0] - body[0][0]) * t
        y = (chevron_y_top + chevron_y_bot) // 2
        pygame.draw.polygon(big, CREAM,
                            [(int(x), int(y - s(3))),
                             (int(x + s(3)), int(y)),
                             (int(x), int(y + s(3))),
                             (int(x - s(3)), int(y))])

    # Cream border lines along top + bottom
    pygame.draw.line(big, CREAM,
                     (body[0][0] + s(4), body[0][1] + s(3)),
                     (body[1][0] - s(4), body[1][1] + s(3)),
                     max(2, s(1)))
    pygame.draw.line(big, CREAM,
                     (body[3][0] + s(4), body[3][1] - s(3)),
                     (body[2][0] - s(4), body[2][1] - s(3)),
                     max(2, s(1)))

    # Leather-tipped tassels at corners
    for corner in body:
        pygame.draw.rect(big, BROWN,
                         (corner[0] - s(2), corner[1] + s(2),
                          s(4), s(4)))
        for dx in (-s(2), 0, s(2)):
            pygame.draw.line(big, OCHRE_LO,
                             (corner[0] + dx, corner[1] + s(6)),
                             (corner[0] + dx - s(1), corner[1] + s(14)),
                             max(2, s(1)))


# ─────────────────────────────────────────────────────────────────────────────
# Composer + sheet
# ─────────────────────────────────────────────────────────────────────────────

def render_figure(carpet_fn):
    big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    big.fill(SKY)
    cx = PW // 2
    # Carpet first (below the figure)
    carpet_fn(big, cx)
    # Then the locked v4 lotus genie body + offering arms + shine #1
    draw_crossed_legs_ankle_cross(big, cx)
    draw_torso(big, cx)
    draw_neck(big, cx)
    head_cy = s(60)
    head_r = s(40)
    draw_head(big, cx, head_cy, head_r)
    draw_face(big, cx, head_cy)
    draw_earrings(big, cx, head_cy, head_r)
    draw_topknot_and_headband(big, cx, head_cy, head_r)
    draw_sash(big, cx)
    draw_offering_arms_with_shine(big, cx, shine_1_classic_pixie)
    return pygame.transform.smoothscale(big, (W, H))


CARPETS = [
    ("1 — Aladdin (Disney)",   draw_carpet_aladdin),
    ("2 — Persian rug",        draw_carpet_persian),
    ("3 — Royal velvet",       draw_carpet_royal),
    ("4 — Cosmic nebula",      draw_carpet_cosmic),
    ("5 — Tribal desert",      draw_carpet_tribal),
]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "v1"
    DW = W * DISPLAY_SCALE
    DH = H * DISPLAY_SCALE
    margin = 14
    label_h = 28
    sheet_w = DW * len(CARPETS) + margin * (len(CARPETS) + 1)
    sheet_h = DH + margin * 2 + label_h
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 22, 30))
    font = pygame.font.SysFont("Arial", 18, bold=True)
    for i, (label, fn) in enumerate(CARPETS):
        portrait = render_figure(fn)
        disp = pygame.transform.smoothscale(portrait, (DW, DH))
        x = margin + i * (DW + margin)
        pygame.draw.rect(sheet, (60, 65, 80),
                         (x - 2, margin - 2, DW + 4, DH + 4), 2)
        sheet.blit(disp, (x, margin))
        text = font.render(label, True, (240, 240, 240))
        sheet.blit(text, (x + (DW - text.get_width()) // 2,
                          margin + DH + 6))
        pygame.image.save(disp,
                          os.path.join(OUT_DIR,
                                       f"a1_carpet_{i+1}_{tag}.png"))
    out = os.path.join(OUT_DIR, f"a1_carpets_{tag}.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
