"""Render 5 candidate genie portraits side-by-side for design review.

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_genie_designs [tag]
"""
import os, sys, math, random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_designs")
os.makedirs(OUT_DIR, exist_ok=True)

W, H, SS = 200, 280, 4
PW, PH = W * SS, H * SS
SKY = (110, 175, 220)


# ── Helpers ──────────────────────────────────────────────────────────────────
def _v_torso(surf, cx, neck_y, shoulder_y, waist_y, base_y,
             neck_w, shoulder_w, waist_w, base_w,
             body, body_lo, body_hi, outline_w=2):
    """V-shape torso: narrow neck, wide shoulders, tapered waist,
    optional flared base. Draws shadow polygon + body + flank
    highlight."""
    pts = [
        (cx - neck_w,     neck_y),
        (cx - shoulder_w, shoulder_y),
        (cx - waist_w,    waist_y),
        (cx - base_w,     base_y),
        (cx + base_w,     base_y),
        (cx + waist_w,    waist_y),
        (cx + shoulder_w, shoulder_y),
        (cx + neck_w,     neck_y),
    ]
    pygame.draw.polygon(surf, body_lo,
                        [(x + 2 * SS, y + 2 * SS) for x, y in pts])
    pygame.draw.polygon(surf, body, pts)
    pygame.draw.lines(surf, body_lo, True, pts, max(2, SS // 2))
    # Left flank highlight
    pygame.draw.lines(surf, body_hi, False, [
        (cx - shoulder_w + 6 * SS, shoulder_y + 4 * SS),
        (cx - waist_w + 4 * SS, waist_y),
        (cx - base_w + 4 * SS, base_y - 4 * SS),
    ], max(3, SS))


def _smoke_curl(surf, cx, cy, length, color_lo, color_mid, color_hi,
                t=0.0, side=-1):
    """Smoke trail that curls down and out to one side (side=-1 left,
    +1 right). 6 ellipses with decreasing radius, sway-animated."""
    cols = [color_hi, color_mid, color_mid, color_lo, color_lo, color_lo]
    for i in range(6):
        k = i / 5.0
        sway = math.sin(t * 1.6 + i * 0.4) * 6 * SS
        offset_x = side * (4 + i * 6) * SS + sway
        offset_y = (i * length / 5) * SS
        r = (14 - i * 2) * SS
        pygame.draw.ellipse(surf, (*cols[i], 230),
                            (cx + offset_x - r,
                             cy + offset_y - int(r * 0.6),
                             r * 2, int(r * 1.3)))


def _arm(surf, x0, y0, x1, y1, x2, y2,
         color, color_lo, color_hi, cuff_color, cuff_hi,
         hand_color=None, w=10):
    """Two-segment arm with shadow, bicep bulge, elbow ball, cuff,
    and a fist circle at the wrist."""
    w_px = w * SS
    # Shadow
    pygame.draw.line(surf, color_lo, (x0, y0 + 2), (x1, y1 + 2), w_px + 4)
    pygame.draw.line(surf, color_lo, (x1, y1 + 2), (x2, y2 + 2), w_px + 2)
    # Main
    pygame.draw.line(surf, color, (x0, y0), (x1, y1), w_px + 2)
    pygame.draw.line(surf, color, (x1, y1), (x2, y2), w_px)
    # Bicep bulge
    mx, my = (x0 + x1) // 2, (y0 + y1) // 2
    pygame.draw.circle(surf, color_hi, (mx - 2 * SS, my - 3 * SS),
                       max(5, w_px // 2 + 2))
    # Elbow
    pygame.draw.circle(surf, color, (x1, y1), max(6, w_px // 2 + 1))
    # Cuff
    pygame.draw.circle(surf, cuff_color, (x2, y2), max(8, int(w_px * 0.85)))
    pygame.draw.circle(surf, cuff_hi, (x2 - 3 * SS, y2 - 3 * SS),
                       max(3, int(w_px * 0.4)))
    # Fist
    if hand_color is None:
        hand_color = color
    pygame.draw.circle(surf, color_lo, (x2 + 1, y2 - w_px + 2),
                       max(7, int(w_px * 0.7)))
    pygame.draw.circle(surf, hand_color, (x2, y2 - w_px),
                       max(7, int(w_px * 0.65)))


def _eye(surf, cx, cy, r, iris=(18, 14, 10), white=(250, 250, 245),
         glint=True):
    pygame.draw.ellipse(surf, white,
                        (cx - int(r * 1.5), cy - int(r * 1.1),
                         int(r * 3), int(r * 2.2)))
    pygame.draw.circle(surf, iris, (cx, cy), r)
    if glint:
        pygame.draw.circle(surf, (255, 255, 255),
                           (cx - r // 3, cy - r // 3), max(1, r // 3))


def _star(surf, cx, cy, r, color):
    pygame.draw.line(surf, color, (cx - r * 2, cy), (cx + r * 2, cy),
                     max(1, SS // 2))
    pygame.draw.line(surf, color, (cx, cy - r * 2), (cx, cy + r * 2),
                     max(1, SS // 2))
    pygame.draw.circle(surf, (255, 255, 255), (cx, cy), max(1, r))


def _head(surf, cx, cy, r, skin, skin_lo, skin_hi):
    pygame.draw.circle(surf, skin_lo, (cx + 3 * SS, cy + 3 * SS), r + 2)
    pygame.draw.circle(surf, skin, (cx, cy), r)
    pygame.draw.circle(surf, skin_hi, (cx - r // 3, cy - r // 3), r // 3)


# ────────────────────────────────────────────────────────────────────────────
# Design A — "Hero Genie" (Aladdin tribute, muscular)
def draw_design_a(big, cx, t):
    SKIN     = ( 70, 175, 220)
    SKIN_HI  = (160, 225, 250)
    SKIN_LO  = ( 25, 115, 175)
    GOLD     = (240, 200, 100)
    GOLD_HI  = (255, 240, 175)
    GOLD_LO  = (160, 115,  30)
    BLACK    = ( 18,  14,  10)
    WHITE    = (250, 250, 245)
    HAIR     = ( 28,  20,  18)
    RUBY     = (215,  70,  85)

    # smoke trailing down-left FROM the base of the figure
    _smoke_curl(big, cx - 8 * SS, int(210 * SS), length=60,
                color_lo=SKIN_LO, color_mid=SKIN, color_hi=SKIN_HI,
                t=t, side=-1)

    # ── V-shaped muscular torso ────────────────────────────────────────
    _v_torso(big, cx,
             neck_y=int(105 * SS),
             shoulder_y=int(122 * SS),
             waist_y=int(180 * SS),
             base_y=int(220 * SS),
             neck_w=int(18 * SS),
             shoulder_w=int(62 * SS),
             waist_w=int(30 * SS),
             base_w=int(18 * SS),
             body=SKIN, body_lo=SKIN_LO, body_hi=SKIN_HI)
    # Pec definition
    for sx in (-int(20 * SS), int(20 * SS)):
        pygame.draw.ellipse(big, SKIN_HI,
                            (cx + sx - int(20 * SS), int(125 * SS),
                             int(34 * SS), int(20 * SS)))
        pygame.draw.arc(big, SKIN_LO,
                        (cx + sx - int(20 * SS), int(132 * SS),
                         int(34 * SS), int(16 * SS)),
                        math.radians(0), math.radians(180), max(3, SS))
    # Abs centre line
    pygame.draw.line(big, SKIN_LO,
                     (cx, int(148 * SS)), (cx, int(178 * SS)),
                     max(2, SS - 1))
    # Belly highlight
    pygame.draw.ellipse(big, SKIN_HI,
                        (cx - int(14 * SS), int(155 * SS),
                         int(28 * SS), int(20 * SS)))

    # ── crossed arms ───────────────────────────────────────────────────
    # Arm 1 (right shoulder → mid-chest → left waist)
    _arm(big, cx + int(50 * SS), int(126 * SS),
         cx + int(20 * SS), int(150 * SS),
         cx - int(26 * SS), int(165 * SS),
         SKIN, SKIN_LO, SKIN_HI, GOLD, GOLD_HI, w=9)
    # Arm 2 ON TOP of arm 1 (left shoulder → mid-chest → right waist)
    _arm(big, cx - int(50 * SS), int(126 * SS),
         cx - int(20 * SS), int(145 * SS),
         cx + int(26 * SS), int(160 * SS),
         SKIN, SKIN_LO, SKIN_HI, GOLD, GOLD_HI, w=9)

    # ── sash with ruby buckle (over arms) ─────────────────────────────
    sash_y = int(180 * SS)
    pygame.draw.polygon(big, GOLD_LO,
                        [(cx - int(46 * SS), sash_y - 6 * SS),
                         (cx + int(46 * SS), sash_y - 4 * SS),
                         (cx + int(42 * SS), sash_y + 12 * SS),
                         (cx - int(42 * SS), sash_y + 10 * SS)])
    pygame.draw.polygon(big, GOLD,
                        [(cx - int(44 * SS), sash_y - 3 * SS),
                         (cx + int(44 * SS), sash_y - 1 * SS),
                         (cx + int(40 * SS), sash_y + 9 * SS),
                         (cx - int(40 * SS), sash_y + 7 * SS)])
    pygame.draw.line(big, GOLD_HI,
                     (cx - int(42 * SS), sash_y - 1 * SS),
                     (cx + int(42 * SS), sash_y + 1 * SS),
                     max(2, SS))
    # Buckle
    pygame.draw.circle(big, GOLD_LO, (cx, sash_y + 3 * SS), int(10 * SS))
    pygame.draw.circle(big, GOLD_HI, (cx, sash_y + 3 * SS), int(8 * SS))
    pygame.draw.polygon(big, RUBY,
                        [(cx, sash_y - 2 * SS),
                         (cx + int(6 * SS), sash_y + 3 * SS),
                         (cx, sash_y + 8 * SS),
                         (cx - int(6 * SS), sash_y + 3 * SS)])
    pygame.draw.polygon(big, (255, 200, 220),
                        [(cx - 2 * SS, sash_y + 1 * SS),
                         (cx, sash_y + 3 * SS),
                         (cx - 3 * SS, sash_y + 4 * SS)])

    # ── HEAD ───────────────────────────────────────────────────────────
    head_cy = int(58 * SS)
    head_r = int(32 * SS)
    _head(big, cx, head_cy, head_r, SKIN, SKIN_LO, SKIN_HI)

    # Hair tuft
    pygame.draw.circle(big, HAIR, (cx, head_cy - head_r - int(2 * SS)),
                       int(10 * SS))
    # Gold headband strip
    pygame.draw.rect(big, GOLD_LO,
                     (cx - int(34 * SS), head_cy - int(22 * SS),
                      int(68 * SS), int(8 * SS)))
    pygame.draw.rect(big, GOLD,
                     (cx - int(32 * SS), head_cy - int(20 * SS),
                      int(64 * SS), int(5 * SS)))
    # Gem
    pygame.draw.polygon(big, RUBY,
                        [(cx, head_cy - int(26 * SS)),
                         (cx + int(6 * SS), head_cy - int(18 * SS)),
                         (cx, head_cy - int(10 * SS)),
                         (cx - int(6 * SS), head_cy - int(18 * SS))])
    pygame.draw.polygon(big, (255, 200, 220),
                        [(cx - 2 * SS, head_cy - int(22 * SS)),
                         (cx - int(1 * SS), head_cy - int(18 * SS)),
                         (cx - 3 * SS, head_cy - int(19 * SS))])
    # Brow
    pygame.draw.polygon(big, HAIR,
                        [(cx - int(18 * SS), head_cy - int(6 * SS)),
                         (cx - int(4 * SS),  head_cy - int(8 * SS)),
                         (cx - int(4 * SS),  head_cy - int(4 * SS)),
                         (cx - int(18 * SS), head_cy - int(2 * SS))])
    pygame.draw.polygon(big, HAIR,
                        [(cx + int(18 * SS), head_cy - int(6 * SS)),
                         (cx + int(4 * SS),  head_cy - int(8 * SS)),
                         (cx + int(4 * SS),  head_cy - int(4 * SS)),
                         (cx + int(18 * SS), head_cy - int(2 * SS))])
    # Eyes
    _eye(big, cx - int(11 * SS), head_cy + int(2 * SS), int(5 * SS),
         white=WHITE)
    _eye(big, cx + int(11 * SS), head_cy + int(2 * SS), int(5 * SS),
         white=WHITE)
    # Big confident grin
    mt = head_cy + int(15 * SS)
    pygame.draw.polygon(big, HAIR,
                        [(cx - int(13 * SS), mt),
                         (cx + int(13 * SS), mt),
                         (cx + int(9 * SS), mt + int(11 * SS)),
                         (cx - int(9 * SS), mt + int(11 * SS))])
    pygame.draw.polygon(big, WHITE,
                        [(cx - int(11 * SS), mt + int(2 * SS)),
                         (cx + int(11 * SS), mt + int(2 * SS)),
                         (cx + int(7 * SS), mt + int(8 * SS)),
                         (cx - int(7 * SS), mt + int(8 * SS))])
    pygame.draw.polygon(big, HAIR,
                        [(cx - int(6 * SS), mt + int(11 * SS)),
                         (cx + int(6 * SS), mt + int(11 * SS)),
                         (cx, mt + int(24 * SS))])
    # Curled mustache
    pygame.draw.arc(big, HAIR,
                    (cx - int(18 * SS), head_cy + int(10 * SS),
                     int(18 * SS), int(10 * SS)),
                    math.radians(190), math.radians(360), max(3, SS + 1))
    pygame.draw.arc(big, HAIR,
                    (cx, head_cy + int(10 * SS),
                     int(18 * SS), int(10 * SS)),
                    math.radians(180), math.radians(350), max(3, SS + 1))
    # Earrings
    for sx in (-int(32 * SS), int(32 * SS)):
        pygame.draw.circle(big, GOLD_LO,
                           (cx + sx, head_cy + int(8 * SS)),
                           int(7 * SS), max(3, SS + 1))
        pygame.draw.circle(big, GOLD,
                           (cx + sx, head_cy + int(8 * SS)),
                           int(5 * SS), max(2, SS))


# ────────────────────────────────────────────────────────────────────────────
# Design B — "Mystic Sage" (long-bearded wizard djinn)
def draw_design_b(big, cx, t):
    ROBE_LO  = ( 35,  15,  60)
    ROBE     = ( 80,  40, 130)
    ROBE_HI  = (150, 110, 210)
    GLOW     = (210, 175, 255)
    EYE_GLOW = (220, 240, 255)
    GOLD     = (240, 200, 100)
    GOLD_HI  = (255, 240, 175)
    GOLD_LO  = (155, 110,  30)
    SKIN     = (210, 180, 240)
    SKIN_LO  = (155, 115, 200)
    WHITE    = (250, 245, 255)

    # Stars
    random.seed(3)
    for _ in range(24):
        sx = random.randint(int(10 * SS), int((W - 10) * SS))
        sy = random.randint(int(8 * SS), int(240 * SS))
        sr = random.randint(int(2 * SS), int(5 * SS))
        _star(big, sx, sy, sr, GLOW)

    # ── flowing robe (full body, no legs) ─────────────────────────────
    robe_pts = [
        (cx - int(28 * SS), int(110 * SS)),
        (cx - int(48 * SS), int(140 * SS)),
        (cx - int(70 * SS), int(180 * SS)),
        (cx - int(86 * SS), int(225 * SS)),
        (cx - int(70 * SS), int(252 * SS)),
        (cx + int(70 * SS), int(252 * SS)),
        (cx + int(86 * SS), int(225 * SS)),
        (cx + int(70 * SS), int(180 * SS)),
        (cx + int(48 * SS), int(140 * SS)),
        (cx + int(28 * SS), int(110 * SS)),
    ]
    pygame.draw.polygon(big, ROBE_LO,
                        [(x + 2 * SS, y + 2 * SS) for x, y in robe_pts])
    pygame.draw.polygon(big, ROBE, robe_pts)
    pygame.draw.lines(big, ROBE_LO, True, robe_pts, max(2, SS // 2))
    # Drape folds
    for sx in (-int(40 * SS), -int(12 * SS), int(12 * SS), int(40 * SS)):
        pygame.draw.line(big, ROBE_HI,
                         (cx + sx, int(125 * SS)),
                         (cx + int(sx * 1.4), int(245 * SS)),
                         max(3, SS))
    # Hem ruffle
    hem_y = int(248 * SS)
    hem_pts = []
    for i in range(15):
        x = cx - int(72 * SS) + int(i * (144 * SS / 14))
        y = hem_y + (int(7 * SS) if i % 2 else int(-2 * SS))
        hem_pts.append((x, y))
    pygame.draw.lines(big, GOLD, False, hem_pts, max(2, SS))

    # ── amulet ─────────────────────────────────────────────────────────
    am_cy = int(150 * SS)
    pygame.draw.circle(big, GOLD_HI, (cx, am_cy), int(20 * SS))
    pygame.draw.circle(big, GOLD, (cx, am_cy), int(17 * SS))
    pygame.draw.circle(big, ROBE_LO, (cx, am_cy), int(13 * SS))
    # All-seeing eye
    pygame.draw.ellipse(big, WHITE,
                        (cx - int(11 * SS), am_cy - int(7 * SS),
                         int(22 * SS), int(14 * SS)))
    pygame.draw.circle(big, EYE_GLOW, (cx, am_cy), int(6 * SS))
    pygame.draw.circle(big, (18, 14, 10), (cx, am_cy), int(3 * SS))
    pygame.draw.circle(big, WHITE,
                       (cx - 2 * SS, am_cy - 2 * SS), int(1 * SS))
    # Chain arc
    for ang in range(200, 341, 8):
        ax = cx + int(math.cos(math.radians(ang)) * 28 * SS)
        ay = am_cy + int(math.sin(math.radians(ang)) * 28 * SS)
        pygame.draw.circle(big, GOLD, (ax, ay), max(1, int(1.6 * SS)))

    # ── hands holding orbs ─────────────────────────────────────────────
    for side in (-1, 1):
        # Sleeve drape
        pygame.draw.polygon(big, ROBE,
                            [(cx + side * int(28 * SS), int(155 * SS)),
                             (cx + side * int(62 * SS), int(175 * SS)),
                             (cx + side * int(58 * SS), int(200 * SS)),
                             (cx + side * int(22 * SS), int(185 * SS))])
        # Sleeve gold trim
        pygame.draw.line(big, GOLD,
                         (cx + side * int(58 * SS), int(199 * SS)),
                         (cx + side * int(22 * SS), int(184 * SS)),
                         max(2, SS))
        wx = cx + side * int(50 * SS)
        wy = int(178 * SS)
        # Hand
        pygame.draw.circle(big, SKIN_LO, (wx, wy + 2 * SS), int(11 * SS))
        pygame.draw.circle(big, SKIN, (wx, wy), int(10 * SS))
        # Orb
        s = pygame.Surface((int(40 * SS), int(40 * SS)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*GLOW, 90),
                           (int(20 * SS), int(20 * SS)), int(18 * SS))
        pygame.draw.circle(s, (*GLOW, 150),
                           (int(20 * SS), int(20 * SS)), int(12 * SS))
        pygame.draw.circle(s, (*EYE_GLOW, 220),
                           (int(20 * SS), int(20 * SS)), int(8 * SS))
        pygame.draw.circle(s, (255, 255, 255, 255),
                           (int(20 * SS), int(20 * SS)), int(4 * SS))
        big.blit(s, (wx - int(20 * SS), wy - int(32 * SS)))

    # ── HOOD ──────────────────────────────────────────────────────────
    hood_cy = int(72 * SS)
    hood_w  = int(108 * SS)
    hood_h  = int(96 * SS)
    pygame.draw.ellipse(big, ROBE_LO,
                        (cx - hood_w // 2 - 2 * SS,
                         hood_cy - hood_h // 2 - 2 * SS,
                         hood_w + 4 * SS, hood_h + 4 * SS))
    pygame.draw.ellipse(big, ROBE,
                        (cx - hood_w // 2, hood_cy - hood_h // 2,
                         hood_w, hood_h))
    pygame.draw.arc(big, GOLD,
                    (cx - hood_w // 2, hood_cy - hood_h // 2,
                     hood_w, hood_h),
                    math.radians(190), math.radians(350), max(3, SS + 1))
    # Hood inner shadow
    pygame.draw.ellipse(big, ROBE_LO,
                        (cx - int(32 * SS), hood_cy - int(14 * SS),
                         int(64 * SS), int(54 * SS)))
    # Face inside
    pygame.draw.circle(big, SKIN_LO, (cx + SS, hood_cy + SS + int(6 * SS)),
                       int(22 * SS))
    pygame.draw.circle(big, SKIN, (cx, hood_cy + int(6 * SS)),
                       int(20 * SS))
    # Glowing eyes
    face_cy = hood_cy + int(6 * SS)
    for sx in (-int(8 * SS), int(8 * SS)):
        s = pygame.Surface((int(24 * SS), int(24 * SS)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*GLOW, 90),
                           (int(12 * SS), int(12 * SS)), int(12 * SS))
        pygame.draw.circle(s, (*EYE_GLOW, 220),
                           (int(12 * SS), int(12 * SS)), int(6 * SS))
        pygame.draw.circle(s, (255, 255, 255, 255),
                           (int(12 * SS), int(12 * SS)), int(3 * SS))
        big.blit(s, (cx + sx - int(12 * SS), face_cy - int(12 * SS)))
    # Wispy long beard down chest
    beard_top = face_cy + int(12 * SS)
    beard_bot = int(155 * SS)
    pygame.draw.polygon(big, WHITE,
                        [(cx - int(12 * SS), beard_top),
                         (cx + int(12 * SS), beard_top),
                         (cx + int(20 * SS), beard_top + int(28 * SS)),
                         (cx + int(14 * SS), beard_bot),
                         (cx, beard_bot + int(10 * SS)),
                         (cx - int(14 * SS), beard_bot),
                         (cx - int(20 * SS), beard_top + int(28 * SS))])
    # Beard strands
    for dx in (-int(10 * SS), -int(2 * SS), int(6 * SS), int(14 * SS)):
        pygame.draw.line(big, (215, 210, 230),
                         (cx + dx, beard_top + int(5 * SS)),
                         (cx + int(dx * 0.5), beard_bot),
                         max(2, SS - 1))


# ────────────────────────────────────────────────────────────────────────────
# Design C — "Cosmic Genie" (nebula-bodied transcendent)
def draw_design_c(big, cx, t):
    NEBULA_BG = (40, 30, 80)
    NEBULA_PURPLE = (135, 70, 200)
    NEBULA_PINK   = (235, 95, 175)
    NEBULA_BLUE   = (75, 150, 240)
    GLOW    = (220, 200, 255)
    GOLD    = (240, 200, 100)
    GOLD_HI = (255, 240, 175)
    WHITE   = (250, 250, 255)
    EDGE    = (200, 180, 250)
    SKIN    = (220, 200, 250)
    SKIN_LO = (160, 130, 220)

    # Distant background stars
    random.seed(7)
    for _ in range(35):
        sx = random.randint(int(6 * SS), int((W - 6) * SS))
        sy = random.randint(int(6 * SS), int((H - 6) * SS))
        sr = random.randint(int(1 * SS), int(3 * SS))
        _star(big, sx, sy, sr, GLOW)

    # ── full silhouette ────────────────────────────────────────────────
    silhouette = [
        # Top of head
        (cx - int(28 * SS), int(35 * SS)),
        (cx + int(28 * SS), int(35 * SS)),
        # Down to shoulders
        (cx + int(34 * SS), int(70 * SS)),
        (cx + int(20 * SS), int(85 * SS)),
        # Down arms (both crossed-ish)
        (cx + int(58 * SS), int(105 * SS)),
        (cx + int(62 * SS), int(150 * SS)),
        (cx + int(40 * SS), int(155 * SS)),
        # Down right flank
        (cx + int(48 * SS), int(185 * SS)),
        (cx + int(70 * SS), int(225 * SS)),
        # Bottom of smoke tail
        (cx + int(35 * SS), int(260 * SS)),
        (cx - int(35 * SS), int(260 * SS)),
        # Up left flank
        (cx - int(70 * SS), int(225 * SS)),
        (cx - int(48 * SS), int(185 * SS)),
        (cx - int(40 * SS), int(155 * SS)),
        (cx - int(62 * SS), int(150 * SS)),
        (cx - int(58 * SS), int(105 * SS)),
        (cx - int(20 * SS), int(85 * SS)),
        (cx - int(34 * SS), int(70 * SS)),
    ]
    # Edge glow (drawn first, slightly larger)
    pygame.draw.polygon(big, EDGE,
                        [(x, y) for x, y in silhouette], 0)
    pygame.draw.polygon(big, NEBULA_BG,
                        [(x * 0.97 + cx * 0.03 if x != cx else x,
                          y * 0.97 + int(140 * SS) * 0.03 if y != int(140 * SS) else y)
                         for x, y in silhouette], 0)
    # Fill silhouette with nebula clouds
    random.seed(11)
    for _ in range(40):
        nx = cx + random.randint(-int(55 * SS), int(55 * SS))
        ny = random.randint(int(40 * SS), int(250 * SS))
        nr = random.randint(int(14 * SS), int(28 * SS))
        nc = random.choice([NEBULA_PURPLE, NEBULA_PINK, NEBULA_BLUE])
        s = pygame.Surface((nr * 2 + 4, nr * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*nc, 80), (nr + 2, nr + 2), nr)
        big.blit(s, (nx - nr - 2, ny - nr - 2))
    # Mask with silhouette: re-stroke the silhouette edge in EDGE
    pygame.draw.lines(big, EDGE, True, silhouette, max(3, SS + 1))
    # Outline shadow
    pygame.draw.lines(big, (*GLOW, 80), True, silhouette, max(6, SS * 2))

    # Stars sprinkled across the body
    random.seed(13)
    for _ in range(22):
        sx = cx + random.randint(-int(50 * SS), int(50 * SS))
        sy = random.randint(int(40 * SS), int(250 * SS))
        sr = random.randint(int(1 * SS), int(3 * SS))
        _star(big, sx, sy, sr, WHITE)

    # ── face features (galaxy eyes + smile + crown) ───────────────────
    head_cy = int(58 * SS)
    head_r  = int(28 * SS)
    # Galaxy eyes (spiral pattern)
    for sx in (-int(10 * SS), int(10 * SS)):
        # Eye base ring
        pygame.draw.circle(big, (10, 5, 30), (cx + sx, head_cy), int(7 * SS))
        pygame.draw.circle(big, NEBULA_PURPLE, (cx + sx, head_cy), int(5 * SS))
        pygame.draw.circle(big, NEBULA_PINK, (cx + sx, head_cy), int(3 * SS))
        pygame.draw.circle(big, WHITE, (cx + sx, head_cy), int(1 * SS))
        # Spiral hint
        for i in range(3):
            ang = math.radians(i * 120 + t * 30)
            sx_o = math.cos(ang) * 4 * SS
            sy_o = math.sin(ang) * 4 * SS
            pygame.draw.circle(big, WHITE,
                               (cx + sx + int(sx_o), head_cy + int(sy_o)),
                               max(1, SS // 2))
    # Smile (subtle curve)
    pygame.draw.arc(big, EDGE,
                    (cx - int(12 * SS), head_cy + int(10 * SS),
                     int(24 * SS), int(14 * SS)),
                    math.radians(0), math.radians(180), max(3, SS + 1))

    # Cosmic crown (5 spikes with gem tips)
    for spike_x in (-int(24 * SS), -int(12 * SS), 0, int(12 * SS), int(24 * SS)):
        pygame.draw.polygon(big, GOLD,
                            [(cx + spike_x, int(28 * SS)),
                             (cx + spike_x + int(4 * SS), int(40 * SS)),
                             (cx + spike_x - int(4 * SS), int(40 * SS))])
        pygame.draw.circle(big, NEBULA_BLUE, (cx + spike_x, int(28 * SS)),
                           int(3 * SS))
        pygame.draw.circle(big, WHITE,
                           (cx + spike_x - SS, int(27 * SS)), int(1 * SS))


# ────────────────────────────────────────────────────────────────────────────
# Design D — "Trickster Imp" (mischievous, dynamic)
def draw_design_d(big, cx, t):
    SKIN     = (110, 200, 130)
    SKIN_HI  = (190, 235, 200)
    SKIN_LO  = ( 50, 130,  75)
    FEZ      = (180,  45,  60)
    FEZ_HI   = (225, 100, 115)
    FEZ_LO   = (115,  20,  30)
    BLACK    = ( 18,  14,  10)
    GOLD     = (240, 200, 100)
    GOLD_HI  = (255, 240, 175)
    WHITE    = (250, 250, 245)
    SPARK    = (255, 235, 180)
    SPARK_HI = (255, 255, 230)

    _smoke_curl(big, cx + 4 * SS, int(208 * SS), length=58,
                color_lo=SKIN_LO, color_mid=SKIN, color_hi=SKIN_HI,
                t=t, side=-1)

    # ── slim torso ─────────────────────────────────────────────────────
    _v_torso(big, cx,
             neck_y=int(110 * SS),
             shoulder_y=int(124 * SS),
             waist_y=int(180 * SS),
             base_y=int(220 * SS),
             neck_w=int(14 * SS),
             shoulder_w=int(42 * SS),
             waist_w=int(22 * SS),
             base_w=int(14 * SS),
             body=SKIN, body_lo=SKIN_LO, body_hi=SKIN_HI)
    # Belly highlight
    pygame.draw.ellipse(big, SKIN_HI,
                        (cx - int(12 * SS), int(150 * SS),
                         int(24 * SS), int(22 * SS)))

    # ── snap arm — raised diagonally up-left ──────────────────────────
    sh_x, sh_y = cx - int(34 * SS), int(126 * SS)
    el_x, el_y = sh_x - int(26 * SS), sh_y - int(28 * SS)
    fi_x, fi_y = el_x + int(2 * SS), el_y - int(38 * SS)
    _arm(big, sh_x, sh_y, el_x, el_y, fi_x, fi_y,
         SKIN, SKIN_LO, SKIN_HI, GOLD, GOLD_HI, w=8)
    # Hand at the tip
    pygame.draw.circle(big, SKIN_LO, (fi_x + SS, fi_y + SS), int(8 * SS))
    pygame.draw.circle(big, SKIN, (fi_x, fi_y), int(7 * SS))
    # BIG magic spark burst
    burst_r1 = int(24 * SS)
    burst_r2 = int(14 * SS)
    for ang in range(0, 360, 22):
        ax = math.cos(math.radians(ang))
        ay = math.sin(math.radians(ang))
        pygame.draw.line(big, SPARK,
                         (fi_x + int(ax * burst_r2),
                          fi_y + int(ay * burst_r2)),
                         (fi_x + int(ax * burst_r1),
                          fi_y + int(ay * burst_r1)),
                         max(3, SS + 1))
    s = pygame.Surface((burst_r1 * 2 + 4, burst_r1 * 2 + 4),
                       pygame.SRCALPHA)
    pygame.draw.circle(s, (*SPARK, 130),
                       (burst_r1 + 2, burst_r1 + 2), burst_r1)
    pygame.draw.circle(s, (*SPARK_HI, 220),
                       (burst_r1 + 2, burst_r1 + 2), int(burst_r1 * 0.5))
    pygame.draw.circle(s, (255, 255, 255, 255),
                       (burst_r1 + 2, burst_r1 + 2), int(4 * SS))
    big.blit(s, (fi_x - burst_r1 - 2, fi_y - burst_r1 - 2))

    # ── hip arm ────────────────────────────────────────────────────────
    _arm(big,
         cx + int(34 * SS), int(130 * SS),
         cx + int(28 * SS), int(160 * SS),
         cx + int(14 * SS), int(168 * SS),
         SKIN, SKIN_LO, SKIN_HI, GOLD, GOLD_HI, w=8)

    # ── head ───────────────────────────────────────────────────────────
    head_cy = int(60 * SS)
    head_r = int(32 * SS)
    _head(big, cx, head_cy, head_r, SKIN, SKIN_LO, SKIN_HI)
    # Pointed ears
    for sx in (-int(28 * SS), int(28 * SS)):
        sign = 1 if sx > 0 else -1
        ear_pts = [
            (cx + sx, head_cy - int(2 * SS)),
            (cx + sx + sign * int(12 * SS), head_cy - int(16 * SS)),
            (cx + sx + sign * int(2 * SS), head_cy + int(8 * SS)),
        ]
        pygame.draw.polygon(big, SKIN_LO,
                            [(p[0] + 1 * SS, p[1] + 1 * SS) for p in ear_pts])
        pygame.draw.polygon(big, SKIN, ear_pts)

    # Jaunty tilted fez
    fez_h = int(28 * SS)
    fez_w = int(52 * SS)
    fez_cx = cx + int(6 * SS)
    fez_cy = head_cy - head_r + int(8 * SS)
    fez_surf = pygame.Surface((fez_w + int(20 * SS), fez_h + int(16 * SS)),
                              pygame.SRCALPHA)
    sw, sh = fez_surf.get_size()
    fy0 = (sh - fez_h) // 2
    fx0 = (sw - fez_w) // 2
    pygame.draw.rect(fez_surf, FEZ_LO, (fx0, fy0 + int(2 * SS), fez_w, fez_h))
    pygame.draw.rect(fez_surf, FEZ, (fx0, fy0, fez_w, fez_h))
    pygame.draw.ellipse(fez_surf, FEZ_HI,
                        (fx0, fy0 - int(6 * SS), fez_w, int(12 * SS)))
    pygame.draw.ellipse(fez_surf, FEZ_LO,
                        (fx0, fy0 + fez_h - int(6 * SS), fez_w, int(12 * SS)))
    pygame.draw.line(fez_surf, GOLD,
                     (fx0, fy0 + fez_h - int(3 * SS)),
                     (fx0 + fez_w, fy0 + fez_h - int(3 * SS)),
                     max(2, SS))
    fez_surf = pygame.transform.rotate(fez_surf, 12.0)
    big.blit(fez_surf, (fez_cx - fez_surf.get_width() // 2,
                        fez_cy - fez_surf.get_height() // 2))
    # Tassel
    tx = fez_cx + int(16 * SS)
    ty = fez_cy - int(4 * SS)
    pygame.draw.line(big, BLACK, (tx, ty),
                     (tx + int(22 * SS), ty + int(16 * SS)),
                     max(3, SS + 1))
    pygame.draw.circle(big, BLACK,
                       (tx + int(24 * SS), ty + int(20 * SS)),
                       int(6 * SS))
    pygame.draw.circle(big, GOLD,
                       (tx + int(24 * SS), ty + int(20 * SS)),
                       int(3 * SS))

    # Eyes — half closed
    pygame.draw.arc(big, BLACK,
                    (cx - int(20 * SS), head_cy - int(14 * SS),
                     int(18 * SS), int(14 * SS)),
                    math.radians(180), math.radians(360), max(4, SS + 2))
    pygame.draw.arc(big, BLACK,
                    (cx + int(2 * SS), head_cy - int(14 * SS),
                     int(18 * SS), int(14 * SS)),
                    math.radians(180), math.radians(360), max(4, SS + 2))
    pygame.draw.arc(big, BLACK,
                    (cx - int(16 * SS), head_cy - int(4 * SS),
                     int(14 * SS), int(12 * SS)),
                    math.radians(0), math.radians(180), max(4, SS + 2))
    pygame.draw.arc(big, BLACK,
                    (cx + int(2 * SS), head_cy - int(4 * SS),
                     int(14 * SS), int(12 * SS)),
                    math.radians(0), math.radians(180), max(4, SS + 2))
    pygame.draw.circle(big, BLACK,
                       (cx - int(9 * SS), head_cy + int(2 * SS)), int(4 * SS))
    pygame.draw.circle(big, BLACK,
                       (cx + int(9 * SS), head_cy + int(2 * SS)), int(4 * SS))
    pygame.draw.circle(big, WHITE,
                       (cx - int(10 * SS), head_cy + int(1 * SS)),
                       max(1, SS))
    pygame.draw.circle(big, WHITE,
                       (cx + int(8 * SS), head_cy + int(1 * SS)),
                       max(1, SS))

    # HUGE curled mustache
    for side in (-1, 1):
        mx_in = cx + side * int(4 * SS)
        mx_out = cx + side * int(36 * SS)
        pygame.draw.arc(big, BLACK,
                        (min(mx_in, mx_out), head_cy + int(8 * SS),
                         abs(mx_out - mx_in), int(20 * SS)),
                        math.radians(180), math.radians(360), max(4, SS + 2))
        pygame.draw.circle(big, BLACK,
                           (mx_out, head_cy + int(16 * SS)),
                           int(7 * SS), max(3, SS + 1))
        pygame.draw.circle(big, BLACK,
                           (mx_out, head_cy + int(16 * SS)),
                           int(3 * SS))

    # Sly smile + tooth
    pygame.draw.arc(big, BLACK,
                    (cx - int(8 * SS), head_cy + int(16 * SS),
                     int(20 * SS), int(12 * SS)),
                    math.radians(0), math.radians(180), max(4, SS + 2))
    pygame.draw.polygon(big, WHITE,
                        [(cx + int(2 * SS), head_cy + int(22 * SS)),
                         (cx + int(6 * SS), head_cy + int(22 * SS)),
                         (cx + int(4 * SS), head_cy + int(26 * SS))])


# ────────────────────────────────────────────────────────────────────────────
# Design E — "Storm Genie" (lightning-charged hero)
def draw_design_e(big, cx, t):
    BODY     = ( 75, 110, 165)
    BODY_HI  = (155, 190, 240)
    BODY_LO  = ( 30,  55, 105)
    CAPE     = ( 28,  35,  72)
    CAPE_HI  = ( 75,  95, 155)
    CAPE_LO  = ( 15,  18,  40)
    GOLD     = (240, 200, 100)
    GOLD_HI  = (255, 240, 175)
    BLACK    = ( 18,  14,  10)
    WHITE    = (250, 250, 245)
    CYAN     = (150, 225, 255)
    CYAN_HI  = (235, 250, 255)

    # Storm cloud aura behind
    for cx_d, cy_d, r in (
            (cx - int(60 * SS), int(100 * SS), int(46 * SS)),
            (cx + int(60 * SS), int(100 * SS), int(46 * SS)),
            (cx - int(80 * SS), int(160 * SS), int(40 * SS)),
            (cx + int(80 * SS), int(160 * SS), int(40 * SS))):
        s = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*BODY_LO, 200), (r + 2, r + 2), r)
        big.blit(s, (cx_d - r - 2, cy_d - r - 2))
    # Crackling outer bolts
    for path in (
        [(cx - int(80 * SS), int(60 * SS)),
         (cx - int(58 * SS), int(95 * SS)),
         (cx - int(82 * SS), int(120 * SS)),
         (cx - int(60 * SS), int(150 * SS))],
        [(cx + int(80 * SS), int(60 * SS)),
         (cx + int(58 * SS), int(95 * SS)),
         (cx + int(82 * SS), int(120 * SS)),
         (cx + int(60 * SS), int(150 * SS))]):
        pygame.draw.lines(big, CYAN, False, path, max(4, SS + 2))
        pygame.draw.lines(big, WHITE, False, path, max(2, SS))

    # Cape
    cape_pts = [
        (cx - int(56 * SS), int(110 * SS)),
        (cx - int(94 * SS), int(160 * SS)),
        (cx - int(76 * SS), int(218 * SS)),
        (cx - int(40 * SS), int(248 * SS)),
        (cx + int(40 * SS), int(248 * SS)),
        (cx + int(76 * SS), int(218 * SS)),
        (cx + int(94 * SS), int(160 * SS)),
        (cx + int(56 * SS), int(110 * SS)),
    ]
    pygame.draw.polygon(big, CAPE_LO,
                        [(x + 3 * SS, y + 3 * SS) for x, y in cape_pts])
    pygame.draw.polygon(big, CAPE, cape_pts)
    for sx in (-int(64 * SS), -int(20 * SS), int(20 * SS), int(64 * SS)):
        pygame.draw.line(big, CAPE_HI,
                         (cx + sx, int(118 * SS)),
                         (cx + int(sx * 1.2), int(238 * SS)),
                         max(2, SS))

    # ── chiselled V-torso ──────────────────────────────────────────────
    _v_torso(big, cx,
             neck_y=int(108 * SS),
             shoulder_y=int(126 * SS),
             waist_y=int(182 * SS),
             base_y=int(220 * SS),
             neck_w=int(18 * SS),
             shoulder_w=int(58 * SS),
             waist_w=int(28 * SS),
             base_w=int(16 * SS),
             body=BODY, body_lo=BODY_LO, body_hi=BODY_HI)
    # Pecs
    for sx in (-int(17 * SS), int(17 * SS)):
        pygame.draw.ellipse(big, BODY_HI,
                            (cx + sx - int(20 * SS), int(128 * SS),
                             int(34 * SS), int(22 * SS)))
        pygame.draw.arc(big, BODY_LO,
                        (cx + sx - int(20 * SS), int(136 * SS),
                         int(34 * SS), int(16 * SS)),
                        math.radians(0), math.radians(180), max(3, SS))
    # 6-pack abs
    for ay in (int(152 * SS), int(166 * SS), int(180 * SS)):
        for ax in (-int(9 * SS), int(9 * SS)):
            pygame.draw.ellipse(big, BODY_HI,
                                (cx + ax - int(7 * SS), ay,
                                 int(14 * SS), int(8 * SS)))
            pygame.draw.line(big, BODY_LO,
                             (cx + ax, ay + int(2 * SS)),
                             (cx + ax, ay + int(8 * SS)), max(2, SS - 1))
    pygame.draw.line(big, BODY_LO,
                     (cx, int(148 * SS)), (cx, int(192 * SS)),
                     max(2, SS - 1))

    # ── arms held up + outward, lightning between fists ───────────────
    _arm(big,
         cx + int(48 * SS), int(128 * SS),
         cx + int(72 * SS), int(98 * SS),
         cx + int(54 * SS), int(60 * SS),
         BODY, BODY_LO, BODY_HI, GOLD, GOLD_HI, w=10)
    _arm(big,
         cx - int(48 * SS), int(128 * SS),
         cx - int(72 * SS), int(98 * SS),
         cx - int(54 * SS), int(60 * SS),
         BODY, BODY_LO, BODY_HI, GOLD, GOLD_HI, w=10)

    # Lightning bolt between fists (3-layer)
    bolt_pts = [
        (cx - int(52 * SS), int(60 * SS)),
        (cx - int(32 * SS), int(48 * SS)),
        (cx - int(16 * SS), int(64 * SS)),
        (cx, int(46 * SS)),
        (cx + int(16 * SS), int(64 * SS)),
        (cx + int(32 * SS), int(50 * SS)),
        (cx + int(52 * SS), int(60 * SS)),
    ]
    pygame.draw.lines(big, CYAN, False, bolt_pts, max(10, int(2.8 * SS)))
    pygame.draw.lines(big, CYAN_HI, False, bolt_pts, max(5, SS + 2))
    pygame.draw.lines(big, WHITE, False, bolt_pts, max(2, SS))
    for x, y in bolt_pts:
        s = pygame.Surface((int(20 * SS), int(20 * SS)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*CYAN, 160),
                           (int(10 * SS), int(10 * SS)), int(10 * SS))
        big.blit(s, (x - int(10 * SS), y - int(10 * SS)))
        pygame.draw.circle(big, WHITE, (x, y), max(2, SS))

    # ── head — square jaw + ponytail ──────────────────────────────────
    head_cy = int(86 * SS)
    head_r = int(28 * SS)
    pygame.draw.circle(big, BODY_LO,
                       (cx + 3 * SS, head_cy + 3 * SS), head_r + 2)
    pygame.draw.circle(big, BODY, (cx, head_cy), head_r)
    pygame.draw.polygon(big, BODY,
                        [(cx - int(18 * SS), head_cy + int(8 * SS)),
                         (cx + int(18 * SS), head_cy + int(8 * SS)),
                         (cx + int(14 * SS), head_cy + int(28 * SS)),
                         (cx - int(14 * SS), head_cy + int(28 * SS))])
    pygame.draw.circle(big, BODY_HI,
                       (cx - head_r // 3, head_cy - head_r // 3),
                       head_r // 3)
    # Hair
    pygame.draw.ellipse(big, BLACK,
                        (cx - int(24 * SS), head_cy - int(30 * SS),
                         int(48 * SS), int(22 * SS)))
    # Ponytail
    pt_pts = [
        (cx + int(20 * SS), head_cy - int(18 * SS)),
        (cx + int(42 * SS), head_cy - int(22 * SS)),
        (cx + int(56 * SS), head_cy - int(6 * SS)),
        (cx + int(50 * SS), head_cy + int(14 * SS)),
        (cx + int(34 * SS), head_cy + int(6 * SS)),
    ]
    pygame.draw.polygon(big, BLACK, pt_pts)
    pygame.draw.circle(big, GOLD,
                       (cx + int(22 * SS), head_cy - int(14 * SS)),
                       int(4 * SS))

    pygame.draw.polygon(big, BLACK,
                        [(cx - int(9 * SS), head_cy + int(22 * SS)),
                         (cx + int(9 * SS), head_cy + int(22 * SS)),
                         (cx + int(3 * SS), head_cy + int(34 * SS)),
                         (cx - int(3 * SS), head_cy + int(34 * SS))])

    # Glowing cyan eyes
    for sx in (-int(10 * SS), int(10 * SS)):
        s = pygame.Surface((int(28 * SS), int(28 * SS)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*CYAN, 150),
                           (int(14 * SS), int(14 * SS)), int(14 * SS))
        pygame.draw.circle(s, (*CYAN_HI, 240),
                           (int(14 * SS), int(14 * SS)), int(8 * SS))
        pygame.draw.circle(s, (255, 255, 255, 255),
                           (int(14 * SS), int(14 * SS)), int(4 * SS))
        big.blit(s, (cx + sx - int(14 * SS), head_cy - int(14 * SS)))
    # Scowl
    pygame.draw.polygon(big, BLACK,
                        [(cx - int(20 * SS), head_cy - int(12 * SS)),
                         (cx - int(2 * SS),  head_cy - int(6 * SS)),
                         (cx - int(2 * SS),  head_cy - int(2 * SS)),
                         (cx - int(20 * SS), head_cy - int(6 * SS))])
    pygame.draw.polygon(big, BLACK,
                        [(cx + int(20 * SS), head_cy - int(12 * SS)),
                         (cx + int(2 * SS),  head_cy - int(6 * SS)),
                         (cx + int(2 * SS),  head_cy - int(2 * SS)),
                         (cx + int(20 * SS), head_cy - int(6 * SS))])
    pygame.draw.arc(big, BLACK,
                    (cx - int(12 * SS), head_cy + int(12 * SS),
                     int(24 * SS), int(10 * SS)),
                    math.radians(180), math.radians(360), max(3, SS + 1))


# ────────────────────────────────────────────────────────────────────────────
# Design F — "Champion Genie" (v4 hybrid: Hero body + jovial grin +
# cosmic nebula glow inside body + lightning ambience + visible arms).
# Tries to be THE winning design by combining the strongest elements
# from earlier candidates.
def draw_design_f(big, cx, t):
    SKIN      = ( 65, 175, 220)
    SKIN_HI   = (170, 230, 255)
    SKIN_LO   = ( 20, 110, 170)
    NEB_PINK  = (255, 130, 200)
    NEB_PURPLE= (160,  85, 220)
    GOLD      = (245, 205, 105)
    GOLD_HI   = (255, 240, 175)
    GOLD_LO   = (160, 115,  30)
    BLACK     = ( 18,  14,  10)
    WHITE     = (250, 250, 245)
    HAIR      = ( 28,  20,  18)
    RUBY      = (215,  70,  85)
    CYAN      = (160, 230, 255)

    # Ambient sparkles around the figure
    random.seed(5)
    for _ in range(18):
        sx = random.randint(int(8 * SS), int((W - 8) * SS))
        sy = random.randint(int(8 * SS), int((H - 8) * SS))
        sr = random.randint(int(1 * SS), int(3 * SS))
        _star(big, sx, sy, sr, GOLD_HI)

    # Smoke trail
    _smoke_curl(big, cx - 12 * SS, int(212 * SS), length=58,
                color_lo=SKIN_LO, color_mid=SKIN, color_hi=SKIN_HI,
                t=t, side=-1)
    _smoke_curl(big, cx + 12 * SS, int(212 * SS), length=58,
                color_lo=SKIN_LO, color_mid=SKIN, color_hi=SKIN_HI,
                t=t + 1.2, side=+1)

    # V-torso
    _v_torso(big, cx,
             neck_y=int(108 * SS),
             shoulder_y=int(126 * SS),
             waist_y=int(182 * SS),
             base_y=int(218 * SS),
             neck_w=int(18 * SS),
             shoulder_w=int(66 * SS),
             waist_w=int(32 * SS),
             base_w=int(18 * SS),
             body=SKIN, body_lo=SKIN_LO, body_hi=SKIN_HI)
    # Nebula glow INSIDE body (subtle)
    for col, alpha in ((NEB_PINK, 60), (NEB_PURPLE, 70)):
        s = pygame.Surface((int(80 * SS), int(80 * SS)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*col, alpha),
                           (int(40 * SS), int(40 * SS)), int(34 * SS))
        big.blit(s, (cx - int(40 * SS), int(135 * SS)))
    # Tiny stars on the body
    random.seed(8)
    for _ in range(10):
        sx = cx + random.randint(-int(30 * SS), int(30 * SS))
        sy = random.randint(int(140 * SS), int(195 * SS))
        pygame.draw.circle(big, WHITE, (sx, sy), max(1, SS // 2))

    # Pec definition
    for sx in (-int(22 * SS), int(22 * SS)):
        pygame.draw.ellipse(big, SKIN_HI,
                            (cx + sx - int(22 * SS), int(128 * SS),
                             int(38 * SS), int(22 * SS)))
        pygame.draw.arc(big, SKIN_LO,
                        (cx + sx - int(22 * SS), int(136 * SS),
                         int(38 * SS), int(16 * SS)),
                        math.radians(0), math.radians(180), max(3, SS))
    # Abs centre line
    pygame.draw.line(big, SKIN_LO,
                     (cx, int(150 * SS)), (cx, int(180 * SS)),
                     max(2, SS - 1))
    # Belly highlight
    pygame.draw.ellipse(big, SKIN_HI,
                        (cx - int(14 * SS), int(155 * SS),
                         int(28 * SS), int(22 * SS)))

    # ── arms held wide outward (welcoming gesture) ─────────────────────
    # Right arm: shoulder out and slightly up
    _arm(big,
         cx + int(56 * SS), int(132 * SS),
         cx + int(84 * SS), int(118 * SS),
         cx + int(86 * SS), int(82 * SS),
         SKIN, SKIN_LO, SKIN_HI, GOLD, GOLD_HI, w=10)
    # Left arm: shoulder out and slightly up
    _arm(big,
         cx - int(56 * SS), int(132 * SS),
         cx - int(84 * SS), int(118 * SS),
         cx - int(86 * SS), int(82 * SS),
         SKIN, SKIN_LO, SKIN_HI, GOLD, GOLD_HI, w=10)
    # Magical sparkle clouds at the palms
    for side in (-1, 1):
        px, py = cx + side * int(86 * SS), int(82 * SS) - int(12 * SS)
        s = pygame.Surface((int(40 * SS), int(40 * SS)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*CYAN, 120),
                           (int(20 * SS), int(20 * SS)), int(18 * SS))
        pygame.draw.circle(s, (*GOLD_HI, 200),
                           (int(20 * SS), int(20 * SS)), int(11 * SS))
        pygame.draw.circle(s, (255, 255, 255, 255),
                           (int(20 * SS), int(20 * SS)), int(5 * SS))
        big.blit(s, (px - int(20 * SS), py - int(20 * SS)))

    # ── sash at waist (below arms now) ─────────────────────────────────
    sash_y = int(182 * SS)
    pygame.draw.polygon(big, GOLD_LO,
                        [(cx - int(38 * SS), sash_y - 5 * SS),
                         (cx + int(38 * SS), sash_y - 3 * SS),
                         (cx + int(34 * SS), sash_y + 12 * SS),
                         (cx - int(34 * SS), sash_y + 10 * SS)])
    pygame.draw.polygon(big, GOLD,
                        [(cx - int(36 * SS), sash_y - 2 * SS),
                         (cx + int(36 * SS), sash_y),
                         (cx + int(32 * SS), sash_y + 9 * SS),
                         (cx - int(32 * SS), sash_y + 7 * SS)])
    pygame.draw.line(big, GOLD_HI,
                     (cx - int(34 * SS), sash_y - 1 * SS),
                     (cx + int(34 * SS), sash_y + 1 * SS),
                     max(2, SS))
    # Buckle
    pygame.draw.circle(big, GOLD_LO, (cx, sash_y + 3 * SS), int(11 * SS))
    pygame.draw.circle(big, GOLD_HI, (cx, sash_y + 3 * SS), int(9 * SS))
    pygame.draw.polygon(big, RUBY,
                        [(cx, sash_y - 4 * SS),
                         (cx + int(7 * SS), sash_y + 3 * SS),
                         (cx, sash_y + 10 * SS),
                         (cx - int(7 * SS), sash_y + 3 * SS)])
    pygame.draw.polygon(big, (255, 220, 230),
                        [(cx - 3 * SS, sash_y - 1 * SS),
                         (cx, sash_y + 2 * SS),
                         (cx - 4 * SS, sash_y + 4 * SS)])

    # ── HEAD ───────────────────────────────────────────────────────────
    head_cy = int(58 * SS)
    head_r  = int(34 * SS)
    _head(big, cx, head_cy, head_r, SKIN, SKIN_LO, SKIN_HI)

    # ── ornate gold crown across forehead ──────────────────────────────
    crown_y = head_cy - int(22 * SS)
    # Crown base
    pygame.draw.rect(big, GOLD_LO,
                     (cx - int(40 * SS), crown_y,
                      int(80 * SS), int(12 * SS)))
    pygame.draw.rect(big, GOLD,
                     (cx - int(38 * SS), crown_y + int(1 * SS),
                      int(76 * SS), int(9 * SS)))
    pygame.draw.line(big, GOLD_HI,
                     (cx - int(36 * SS), crown_y + int(3 * SS)),
                     (cx + int(36 * SS), crown_y + int(3 * SS)),
                     max(2, SS))
    # 3 spikes above crown
    for spx in (-int(20 * SS), 0, int(20 * SS)):
        pygame.draw.polygon(big, GOLD_LO,
                            [(cx + spx - int(8 * SS), crown_y),
                             (cx + spx, crown_y - int(20 * SS)),
                             (cx + spx + int(8 * SS), crown_y)])
        pygame.draw.polygon(big, GOLD,
                            [(cx + spx - int(6 * SS), crown_y),
                             (cx + spx, crown_y - int(18 * SS)),
                             (cx + spx + int(6 * SS), crown_y)])
    # Gem in centre spike
    pygame.draw.polygon(big, RUBY,
                        [(cx, crown_y - int(20 * SS)),
                         (cx + int(5 * SS), crown_y - int(13 * SS)),
                         (cx, crown_y - int(6 * SS)),
                         (cx - int(5 * SS), crown_y - int(13 * SS))])
    pygame.draw.polygon(big, (255, 200, 220),
                        [(cx - 2 * SS, crown_y - int(16 * SS)),
                         (cx - 1 * SS, crown_y - int(13 * SS)),
                         (cx - 3 * SS, crown_y - int(14 * SS))])
    # Side gems on outer spikes
    pygame.draw.circle(big, CYAN, (cx - int(20 * SS), crown_y - int(13 * SS)),
                       int(3 * SS))
    pygame.draw.circle(big, CYAN, (cx + int(20 * SS), crown_y - int(13 * SS)),
                       int(3 * SS))

    # Brow
    pygame.draw.polygon(big, HAIR,
                        [(cx - int(18 * SS), head_cy - int(6 * SS)),
                         (cx - int(4 * SS),  head_cy - int(8 * SS)),
                         (cx - int(4 * SS),  head_cy - int(3 * SS)),
                         (cx - int(18 * SS), head_cy - int(1 * SS))])
    pygame.draw.polygon(big, HAIR,
                        [(cx + int(18 * SS), head_cy - int(6 * SS)),
                         (cx + int(4 * SS),  head_cy - int(8 * SS)),
                         (cx + int(4 * SS),  head_cy - int(3 * SS)),
                         (cx + int(18 * SS), head_cy - int(1 * SS))])
    # Bigger sparkly eyes
    _eye(big, cx - int(12 * SS), head_cy + int(3 * SS), int(6 * SS),
         white=WHITE)
    _eye(big, cx + int(12 * SS), head_cy + int(3 * SS), int(6 * SS),
         white=WHITE)
    # JOVIAL grin (open mouth)
    mt = head_cy + int(17 * SS)
    pygame.draw.polygon(big, HAIR,
                        [(cx - int(14 * SS), mt),
                         (cx + int(14 * SS), mt),
                         (cx + int(10 * SS), mt + int(12 * SS)),
                         (cx - int(10 * SS), mt + int(12 * SS))])
    pygame.draw.polygon(big, WHITE,
                        [(cx - int(12 * SS), mt + int(2 * SS)),
                         (cx + int(12 * SS), mt + int(2 * SS)),
                         (cx + int(8 * SS), mt + int(8 * SS)),
                         (cx - int(8 * SS), mt + int(8 * SS))])
    # Tongue hint
    pygame.draw.circle(big, RUBY,
                       (cx, mt + int(9 * SS)), int(3 * SS))
    # Goatee
    pygame.draw.polygon(big, HAIR,
                        [(cx - int(7 * SS), mt + int(12 * SS)),
                         (cx + int(7 * SS), mt + int(12 * SS)),
                         (cx, mt + int(26 * SS))])
    # Curled mustache
    pygame.draw.arc(big, HAIR,
                    (cx - int(20 * SS), head_cy + int(10 * SS),
                     int(20 * SS), int(12 * SS)),
                    math.radians(190), math.radians(360), max(4, SS + 1))
    pygame.draw.arc(big, HAIR,
                    (cx, head_cy + int(10 * SS),
                     int(20 * SS), int(12 * SS)),
                    math.radians(180), math.radians(350), max(4, SS + 1))
    # Earrings — bigger hoops with ruby drops
    for sx in (-int(32 * SS), int(32 * SS)):
        pygame.draw.circle(big, GOLD_LO,
                           (cx + sx, head_cy + int(10 * SS)),
                           int(8 * SS), max(3, SS + 1))
        pygame.draw.circle(big, GOLD,
                           (cx + sx, head_cy + int(10 * SS)),
                           int(6 * SS), max(2, SS))
        pygame.draw.circle(big, RUBY,
                           (cx + sx, head_cy + int(20 * SS)),
                           int(3 * SS))


# ────────────────────────────────────────────────────────────────────────────
# Design G — "Brass Djinn" (NEW: steampunk clockwork genie)
def draw_design_g(big, cx, t):
    BRASS     = (210, 155,  75)
    BRASS_HI  = (255, 220, 140)
    BRASS_LO  = (135,  85,  20)
    COPPER    = (200, 110,  60)
    COPPER_HI = (240, 165, 110)
    DARK      = ( 40,  25,  15)
    BLACK     = ( 18,  14,  10)
    WHITE     = (250, 245, 230)
    GLOW      = (255, 200, 100)
    LAVA      = (255, 130,  40)
    LAVA_HI   = (255, 240, 180)

    # Smoke + steam
    _smoke_curl(big, cx - 4 * SS, int(216 * SS), length=58,
                color_lo=BRASS_LO, color_mid=BRASS, color_hi=BRASS_HI,
                t=t, side=-1)

    # V-torso in brass
    _v_torso(big, cx,
             neck_y=int(110 * SS),
             shoulder_y=int(128 * SS),
             waist_y=int(182 * SS),
             base_y=int(218 * SS),
             neck_w=int(18 * SS),
             shoulder_w=int(62 * SS),
             waist_w=int(32 * SS),
             base_w=int(18 * SS),
             body=BRASS, body_lo=BRASS_LO, body_hi=BRASS_HI)
    # Riveted seams (vertical line + rivets along edges)
    for sx in (-int(50 * SS), int(50 * SS)):
        pygame.draw.line(big, BRASS_LO,
                         (cx + sx, int(132 * SS)),
                         (cx + int(sx * 0.6), int(214 * SS)),
                         max(2, SS - 1))
        for y_step in range(140, 215, 14):
            x = cx + int(sx * (1 - (y_step - 140) / 75 * 0.4))
            pygame.draw.circle(big, BRASS_HI, (x, int(y_step * SS)),
                               max(2, SS))
    # Central glowing molten cracks (3 jagged lines)
    crack1 = [(cx, int(132 * SS)),
              (cx + int(4 * SS), int(150 * SS)),
              (cx - int(2 * SS), int(170 * SS)),
              (cx + int(4 * SS), int(192 * SS))]
    pygame.draw.lines(big, LAVA, False, crack1, max(4, SS + 2))
    pygame.draw.lines(big, LAVA_HI, False, crack1, max(2, SS))
    # Side cracks
    for side in (-1, 1):
        c = [(cx + side * int(14 * SS), int(148 * SS)),
             (cx + side * int(22 * SS), int(168 * SS)),
             (cx + side * int(14 * SS), int(190 * SS))]
        pygame.draw.lines(big, LAVA, False, c, max(3, SS + 1))
        pygame.draw.lines(big, LAVA_HI, False, c, max(1, SS - 1))
    # Central gear in chest
    gear_cy = int(160 * SS)
    pygame.draw.circle(big, BRASS_LO, (cx, gear_cy), int(20 * SS))
    pygame.draw.circle(big, COPPER, (cx, gear_cy), int(17 * SS))
    # Gear teeth (8 spokes)
    for ang in range(0, 360, 45):
        ax = math.cos(math.radians(ang))
        ay = math.sin(math.radians(ang))
        pygame.draw.rect(big, BRASS_LO,
                         (cx + int(ax * 17 * SS) - int(3 * SS),
                          gear_cy + int(ay * 17 * SS) - int(3 * SS),
                          int(6 * SS), int(6 * SS)))
    pygame.draw.circle(big, COPPER_HI, (cx, gear_cy), int(12 * SS))
    pygame.draw.circle(big, GLOW, (cx, gear_cy), int(6 * SS))
    pygame.draw.circle(big, WHITE, (cx - SS, gear_cy - SS), int(2 * SS))

    # ── piston arms (segmented with rivets) ────────────────────────────
    for side in (-1, 1):
        sh_x, sh_y = cx + side * int(56 * SS), int(130 * SS)
        el_x, el_y = sh_x + side * int(24 * SS), sh_y - int(10 * SS)
        wr_x, wr_y = el_x - side * int(6 * SS), el_y - int(40 * SS)
        # Upper piston (rectangle)
        ang_u = math.atan2(el_y - sh_y, el_x - sh_x)
        # Use line for simplicity but with thick brass
        pygame.draw.line(big, BRASS_LO,
                         (sh_x, sh_y + 2), (el_x, el_y + 2),
                         max(12, int(2.6 * SS)))
        pygame.draw.line(big, BRASS,
                         (sh_x, sh_y), (el_x, el_y),
                         max(10, int(2.2 * SS)))
        pygame.draw.line(big, BRASS_HI,
                         (sh_x, sh_y - 2), (el_x, el_y - 2),
                         max(2, SS))
        # Lower piston
        pygame.draw.line(big, BRASS_LO,
                         (el_x, el_y + 2), (wr_x, wr_y + 2),
                         max(11, int(2.4 * SS)))
        pygame.draw.line(big, BRASS,
                         (el_x, el_y), (wr_x, wr_y),
                         max(9, int(2.0 * SS)))
        # Elbow joint (big rivet)
        pygame.draw.circle(big, BRASS_LO, (el_x, el_y), int(10 * SS))
        pygame.draw.circle(big, COPPER, (el_x, el_y), int(7 * SS))
        pygame.draw.circle(big, COPPER_HI, (el_x - 2 * SS, el_y - 2 * SS),
                           int(2 * SS))
        # Fist with glowing core
        pygame.draw.circle(big, BRASS_LO, (wr_x, wr_y), int(11 * SS))
        pygame.draw.circle(big, BRASS, (wr_x, wr_y), int(9 * SS))
        pygame.draw.circle(big, LAVA, (wr_x, wr_y), int(5 * SS))
        pygame.draw.circle(big, LAVA_HI, (wr_x - SS, wr_y - SS), int(2 * SS))

    # ── head — bronze, with crown of brass spikes ─────────────────────
    head_cy = int(62 * SS)
    head_r = int(30 * SS)
    pygame.draw.circle(big, BRASS_LO, (cx + 3 * SS, head_cy + 3 * SS),
                       head_r + 2)
    pygame.draw.circle(big, BRASS, (cx, head_cy), head_r)
    pygame.draw.circle(big, BRASS_HI,
                       (cx - head_r // 3, head_cy - head_r // 3),
                       head_r // 3)
    # Forehead bolts (3 in a row)
    for fx in (-int(14 * SS), 0, int(14 * SS)):
        pygame.draw.circle(big, COPPER, (cx + fx, head_cy - int(18 * SS)),
                           int(4 * SS))
        pygame.draw.circle(big, COPPER_HI,
                           (cx + fx - SS, head_cy - int(20 * SS)),
                           int(2 * SS))
    # Spiky brass crown (5 spikes radiating up)
    for ang in (-60, -30, 0, 30, 60):
        rad = math.radians(ang - 90)
        x0 = cx + int(math.cos(rad) * head_r * 0.8)
        y0 = head_cy + int(math.sin(rad) * head_r * 0.8)
        x1 = cx + int(math.cos(rad) * (head_r + int(20 * SS)))
        y1 = head_cy + int(math.sin(rad) * (head_r + int(20 * SS)))
        pygame.draw.line(big, BRASS_LO, (x0, y0), (x1, y1), max(3, SS + 1))
        pygame.draw.line(big, BRASS, (x0, y0), (x1, y1), max(2, SS))
        pygame.draw.circle(big, COPPER, (x1, y1), int(3 * SS))

    # Glowing slit eyes (no whites — mechanical)
    eye_y = head_cy + int(2 * SS)
    for sx in (-int(11 * SS), int(11 * SS)):
        # Eye socket
        pygame.draw.ellipse(big, DARK,
                            (cx + sx - int(7 * SS), eye_y - int(4 * SS),
                             int(14 * SS), int(8 * SS)))
        # Glowing slit
        s = pygame.Surface((int(16 * SS), int(8 * SS)), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*LAVA_HI, 240),
                            (0, 0, int(16 * SS), int(8 * SS)))
        pygame.draw.ellipse(s, (255, 255, 255),
                            (int(4 * SS), int(2 * SS),
                             int(8 * SS), int(4 * SS)))
        big.blit(s, (cx + sx - int(8 * SS), eye_y - int(4 * SS)))

    # Mechanical mouth (grill of vertical bars)
    mt_y = head_cy + int(14 * SS)
    pygame.draw.rect(big, DARK,
                     (cx - int(14 * SS), mt_y,
                      int(28 * SS), int(8 * SS)))
    for bx in range(-12, 13, 4):
        pygame.draw.line(big, BRASS_LO,
                         (cx + int(bx * SS), mt_y),
                         (cx + int(bx * SS), mt_y + int(8 * SS)),
                         max(1, SS // 2))
    # Glow inside the grill
    s = pygame.Surface((int(28 * SS), int(8 * SS)), pygame.SRCALPHA)
    pygame.draw.rect(s, (*LAVA, 180),
                     (0, 0, int(28 * SS), int(8 * SS)))
    big.blit(s, (cx - int(14 * SS), mt_y))


DESIGNS = [
    ("F — Champion Genie", draw_design_f),
    ("B — Mystic Sage",    draw_design_b),
    ("C — Cosmic Genie",   draw_design_c),
    ("G — Brass Djinn",    draw_design_g),
    ("E — Storm Genie",    draw_design_e),
]


def render_one(draw_fn, t=0.0):
    big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    big.fill(SKY)
    cx = PW // 2
    draw_fn(big, cx, t)
    return pygame.transform.smoothscale(big, (W, H))


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "v1"
    margin = 16
    label_h = 22
    sheet_w = W * len(DESIGNS) + margin * (len(DESIGNS) + 1)
    sheet_h = H + margin * 2 + label_h
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 22, 30))
    font = pygame.font.SysFont("Arial", 14, bold=True)
    for i, (label, draw_fn) in enumerate(DESIGNS):
        portrait = render_one(draw_fn)
        x = margin + i * (W + margin)
        pygame.draw.rect(sheet, (60, 65, 80),
                         (x - 2, margin - 2, W + 4, H + 4), 2)
        sheet.blit(portrait, (x, margin))
        text = font.render(label, True, (240, 240, 240))
        sheet.blit(text, (x + (W - text.get_width()) // 2,
                          margin + H + 4))
    out = os.path.join(OUT_DIR, f"sheet_{tag}.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
