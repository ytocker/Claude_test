"""Render 10 candidate genie portraits for design review.

The v5 round explores variations on A (Aladdin Tribute) and F (Champion
Genie), with both loyal-to-source and artistically free interpretations.

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

# Higher resolution than v1–v4 (200×280 ×4 → 240×340 ×5).
W, H, SS = 240, 340, 5
PW, PH = W * SS, H * SS
SKY = (110, 175, 220)


# ─────────────────────────────────────────────────────────────────────────────
# Shared geometry helpers
# ─────────────────────────────────────────────────────────────────────────────

def _v_torso(surf, cx, neck_y, shoulder_y, waist_y, base_y,
             neck_w, shoulder_w, waist_w, base_w,
             body, body_lo, body_hi, mid_alpha_layer=True):
    """V-shape torso with shadow + body + flank highlight. When
    mid_alpha_layer is True, also stamps a soft mid-tone band across
    the chest for extra dimension."""
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
    if mid_alpha_layer:
        # Soft mid-tone band across the upper chest for dimension.
        chest_y = (shoulder_y + waist_y) // 2
        bw = (shoulder_w + waist_w) // 2 + 4 * SS
        s = pygame.Surface((bw * 2, int(18 * SS)), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*body_hi, 90), (0, 0, bw * 2, int(18 * SS)))
        surf.blit(s, (cx - bw, chest_y - int(9 * SS)))
    # Left flank highlight ridge
    pygame.draw.lines(surf, body_hi, False, [
        (cx - shoulder_w + 6 * SS, shoulder_y + 4 * SS),
        (cx - waist_w + 4 * SS, waist_y),
        (cx - base_w + 4 * SS, base_y - 4 * SS),
    ], max(3, SS))


def _smoke_curl(surf, cx, cy, length, color_lo, color_mid, color_hi,
                t=0.0, side=-1, segments=6):
    """Smoke trail that curls out to one side."""
    cols = [color_hi, color_mid, color_mid, color_lo, color_lo, color_lo]
    while len(cols) < segments:
        cols.append(color_lo)
    for i in range(segments):
        sway = math.sin(t * 1.6 + i * 0.4) * 6 * SS
        offset_x = side * (4 + i * 6) * SS + sway
        offset_y = (i * length / max(1, segments - 1)) * SS
        r = (14 - i * 2) * SS
        if r <= 0:
            continue
        pygame.draw.ellipse(surf, (*cols[i], 230),
                            (cx + offset_x - r,
                             cy + offset_y - int(r * 0.6),
                             r * 2, int(r * 1.3)))


def _arm(surf, x0, y0, x1, y1, x2, y2,
         color, color_lo, color_hi, cuff_color, cuff_hi,
         hand_color=None, w=10):
    """Two-segment arm: shoulder → elbow → wrist+cuff+fist."""
    w_px = w * SS
    pygame.draw.line(surf, color_lo, (x0, y0 + 2), (x1, y1 + 2), w_px + 4)
    pygame.draw.line(surf, color_lo, (x1, y1 + 2), (x2, y2 + 2), w_px + 2)
    pygame.draw.line(surf, color, (x0, y0), (x1, y1), w_px + 2)
    pygame.draw.line(surf, color, (x1, y1), (x2, y2), w_px)
    mx, my = (x0 + x1) // 2, (y0 + y1) // 2
    pygame.draw.circle(surf, color_hi, (mx - 2 * SS, my - 3 * SS),
                       max(5, w_px // 2 + 2))
    pygame.draw.circle(surf, color, (x1, y1), max(6, w_px // 2 + 1))
    pygame.draw.circle(surf, cuff_color, (x2, y2), max(8, int(w_px * 0.85)))
    pygame.draw.circle(surf, cuff_hi, (x2 - 3 * SS, y2 - 3 * SS),
                       max(3, int(w_px * 0.4)))
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
        pygame.draw.circle(surf, (255, 255, 255),
                           (cx + r // 2, cy + r // 4), max(1, r // 4))


def _head(surf, cx, cy, r, skin, skin_lo, skin_hi):
    pygame.draw.circle(surf, skin_lo, (cx + 3 * SS, cy + 3 * SS), r + 2)
    pygame.draw.circle(surf, skin, (cx, cy), r)
    pygame.draw.circle(surf, skin_hi, (cx - r // 3, cy - r // 3), r // 3)


def _star(surf, cx, cy, r, color):
    pygame.draw.line(surf, color, (cx - r * 2, cy), (cx + r * 2, cy),
                     max(1, SS // 2))
    pygame.draw.line(surf, color, (cx, cy - r * 2), (cx, cy + r * 2),
                     max(1, SS // 2))
    pygame.draw.circle(surf, (255, 255, 255), (cx, cy), max(1, r))


def _gem_diamond(surf, cx, cy, r, color, hi_color=(255, 230, 240)):
    """Diamond-shaped gem with sparkle."""
    pygame.draw.polygon(surf, color,
                        [(cx, cy - r), (cx + r, cy),
                         (cx, cy + r), (cx - r, cy)])
    pygame.draw.polygon(surf, hi_color,
                        [(cx - r // 3, cy - r // 3),
                         (cx, cy - r // 3),
                         (cx - 2 * r // 3, cy)])


def _gold_band(surf, x0, y0, x1, y1, h, gold, gold_hi, gold_lo,
               engrave=False):
    """Horizontal-ish gold band/strip from (x0,y0) to (x1,y1) with
    thickness h (in SS pixels). Used for headbands, sashes, cuffs."""
    pygame.draw.polygon(surf, gold_lo,
                        [(x0, y0 - h - 2), (x1, y1 - h - 2),
                         (x1 + 2, y1 + h + 2), (x0 - 2, y0 + h + 2)])
    pygame.draw.polygon(surf, gold,
                        [(x0, y0 - h), (x1, y1 - h),
                         (x1, y1 + h), (x0, y0 + h)])
    pygame.draw.line(surf, gold_hi, (x0 + 2, y0 - h // 2),
                     (x1 - 2, y1 - h // 2), max(2, SS - 1))
    if engrave:
        # Tiny decorative dots along the band
        for f in (0.25, 0.5, 0.75):
            mx = int(x0 + (x1 - x0) * f)
            my = int(y0 + (y1 - y0) * f)
            pygame.draw.circle(surf, gold_lo, (mx, my), max(1, SS // 2))


# ─────────────────────────────────────────────────────────────────────────────
# New helpers for the artistic-free variants
# ─────────────────────────────────────────────────────────────────────────────

def _nebula_fill(surf, polygon, palette, seed=11, density=70):
    """Stamp soft alpha cloud-circles inside a region defined by the
    polygon's bounding box. Stars and clouds blend together for a
    cosmic look. Caller masks with the silhouette by drawing the
    silhouette stroke afterwards."""
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    cx = (x_min + x_max) // 2
    cy = (y_min + y_max) // 2
    r = max((x_max - x_min), (y_max - y_min)) // 2
    rng = random.Random(seed)
    for _ in range(density):
        # Pick a point biased toward the centre.
        ang = rng.uniform(0, math.tau)
        dist = rng.uniform(0, r * 0.9)
        nx = cx + int(math.cos(ang) * dist)
        ny = cy + int(math.sin(ang) * dist)
        nr = rng.randint(int(14 * SS), int(34 * SS))
        nc = rng.choice(palette)
        s = pygame.Surface((nr * 2 + 4, nr * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*nc, 80), (nr + 2, nr + 2), nr)
        surf.blit(s, (nx - nr - 2, ny - nr - 2))
    # Star dots
    for _ in range(density // 2):
        ang = rng.uniform(0, math.tau)
        dist = rng.uniform(0, r * 0.8)
        sx = cx + int(math.cos(ang) * dist)
        sy = cy + int(math.sin(ang) * dist)
        pygame.draw.circle(surf, (255, 255, 255),
                           (sx, sy), max(1, SS // 2))


def _halftone(surf, region_rect, color, dot_r=None, spacing=None):
    """Fill a rect with a halftone-dot pattern in the given colour.
    Used for pop-comic shadow shading."""
    x, y, w, h = region_rect
    if dot_r is None:
        dot_r = max(1, int(SS * 0.6))
    if spacing is None:
        spacing = int(SS * 2.4)
    rng = random.Random((x * 31 + y) & 0xFFFF)
    for j in range(0, h, spacing):
        for i in range(0, w, spacing):
            jitter = rng.randint(-SS // 2, SS // 2)
            pygame.draw.circle(surf, color,
                               (x + i + jitter, y + j + jitter), dot_r)


def _lightning(surf, points, colors=None, widths=None):
    """3-layer polyline lightning bolt: wide glow → mid → white core."""
    if colors is None:
        colors = ((150, 225, 255), (220, 240, 255), (255, 255, 255))
    if widths is None:
        widths = (max(8, int(2.4 * SS)), max(4, SS + 2), max(2, SS))
    for col, w in zip(colors, widths):
        pygame.draw.lines(surf, col, False, points, w)


def _thick_outline(surf, polygon, color=(15, 12, 8), w=None):
    """Bold black outline for pop-comic style."""
    if w is None:
        w = max(3, int(SS * 0.9))
    pygame.draw.lines(surf, color, True, polygon, w)


# ─────────────────────────────────────────────────────────────────────────────
# Shared Aladdin face + crown helpers (used by A1, A2, H1, H2, H3 variants)
# ─────────────────────────────────────────────────────────────────────────────

def _aladdin_face(big, cx, head_cy, head_r,
                  hair, white, ruby,
                  goatee=True, mustache=True, smile_wide=True,
                  eye_iris=(18, 14, 10)):
    """Brow + eyes + mouth + goatee + mustache common to the A-family."""
    # Brow
    pygame.draw.polygon(big, hair,
                        [(cx - int(18 * SS), head_cy - int(6 * SS)),
                         (cx - int(4 * SS),  head_cy - int(8 * SS)),
                         (cx - int(4 * SS),  head_cy - int(3 * SS)),
                         (cx - int(18 * SS), head_cy - int(1 * SS))])
    pygame.draw.polygon(big, hair,
                        [(cx + int(18 * SS), head_cy - int(6 * SS)),
                         (cx + int(4 * SS),  head_cy - int(8 * SS)),
                         (cx + int(4 * SS),  head_cy - int(3 * SS)),
                         (cx + int(18 * SS), head_cy - int(1 * SS))])
    _eye(big, cx - int(12 * SS), head_cy + int(2 * SS), int(5 * SS),
         iris=eye_iris, white=white)
    _eye(big, cx + int(12 * SS), head_cy + int(2 * SS), int(5 * SS),
         iris=eye_iris, white=white)
    # Mouth
    mt = head_cy + int(15 * SS)
    if smile_wide:
        pygame.draw.polygon(big, hair,
                            [(cx - int(13 * SS), mt),
                             (cx + int(13 * SS), mt),
                             (cx + int(9 * SS), mt + int(11 * SS)),
                             (cx - int(9 * SS), mt + int(11 * SS))])
        pygame.draw.polygon(big, white,
                            [(cx - int(11 * SS), mt + int(2 * SS)),
                             (cx + int(11 * SS), mt + int(2 * SS)),
                             (cx + int(7 * SS), mt + int(8 * SS)),
                             (cx - int(7 * SS), mt + int(8 * SS))])
        # Tongue hint
        pygame.draw.circle(big, ruby, (cx, mt + int(9 * SS)),
                           max(2, int(2 * SS)))
    else:
        pygame.draw.arc(big, hair,
                        (cx - int(10 * SS), mt - int(4 * SS),
                         int(20 * SS), int(14 * SS)),
                        math.radians(0), math.radians(180), max(3, SS + 1))
    if goatee:
        pygame.draw.polygon(big, hair,
                            [(cx - int(6 * SS), mt + int(11 * SS)),
                             (cx + int(6 * SS), mt + int(11 * SS)),
                             (cx, mt + int(24 * SS))])
    if mustache:
        pygame.draw.arc(big, hair,
                        (cx - int(18 * SS), head_cy + int(10 * SS),
                         int(18 * SS), int(10 * SS)),
                        math.radians(190), math.radians(360), max(3, SS + 1))
        pygame.draw.arc(big, hair,
                        (cx, head_cy + int(10 * SS),
                         int(18 * SS), int(10 * SS)),
                        math.radians(180), math.radians(350), max(3, SS + 1))


def _aladdin_topknot_band(big, cx, head_cy, head_r,
                          hair, gold, gold_hi, gold_lo, ruby):
    """Topknot ball + gold headband with central ruby + small flank gems."""
    # Topknot
    pygame.draw.circle(big, hair, (cx, head_cy - head_r - int(2 * SS)),
                       int(10 * SS))
    # Headband
    pygame.draw.rect(big, gold_lo,
                     (cx - int(34 * SS), head_cy - int(22 * SS),
                      int(68 * SS), int(8 * SS)))
    pygame.draw.rect(big, gold,
                     (cx - int(32 * SS), head_cy - int(20 * SS),
                      int(64 * SS), int(5 * SS)))
    # Ruby gem in centre
    _gem_diamond(big, cx, head_cy - int(18 * SS), int(6 * SS), ruby)


def _aladdin_earrings(big, cx, head_cy, gold, gold_lo, ruby=None):
    for sx in (-int(32 * SS), int(32 * SS)):
        pygame.draw.circle(big, gold_lo,
                           (cx + sx, head_cy + int(8 * SS)),
                           int(7 * SS), max(3, SS + 1))
        pygame.draw.circle(big, gold,
                           (cx + sx, head_cy + int(8 * SS)),
                           int(5 * SS), max(2, SS))
        if ruby:
            pygame.draw.circle(big, ruby,
                               (cx + sx, head_cy + int(18 * SS)),
                               int(3 * SS))


def _aladdin_sash(big, cx, sash_y, sash_w, gold, gold_hi, gold_lo,
                  gems=None):
    """Gold sash with central buckle. `gems` is a list of (color)
    tuples — if 3, places them as left/centre/right; if 1, just centre."""
    pygame.draw.polygon(big, gold_lo,
                        [(cx - sash_w, sash_y - 6 * SS),
                         (cx + sash_w, sash_y - 4 * SS),
                         (cx + sash_w - 4 * SS, sash_y + 12 * SS),
                         (cx - sash_w + 4 * SS, sash_y + 10 * SS)])
    pygame.draw.polygon(big, gold,
                        [(cx - sash_w + 2 * SS, sash_y - 3 * SS),
                         (cx + sash_w - 2 * SS, sash_y - 1 * SS),
                         (cx + sash_w - 6 * SS, sash_y + 9 * SS),
                         (cx - sash_w + 6 * SS, sash_y + 7 * SS)])
    pygame.draw.line(big, gold_hi,
                     (cx - sash_w + 4 * SS, sash_y - 1 * SS),
                     (cx + sash_w - 4 * SS, sash_y + 1 * SS),
                     max(2, SS))
    if gems:
        if len(gems) == 1:
            positions = [(cx, sash_y + 3 * SS, int(6 * SS))]
            colors = gems
        else:
            positions = [
                (cx - int(sash_w * 0.55), sash_y + 3 * SS, int(4 * SS)),
                (cx, sash_y + 3 * SS, int(6 * SS)),
                (cx + int(sash_w * 0.55), sash_y + 3 * SS, int(4 * SS)),
            ]
            colors = gems[:3]
        for (gx, gy, gr), col in zip(positions, colors):
            pygame.draw.circle(big, gold_lo, (gx, gy), gr + 2 * SS)
            pygame.draw.circle(big, gold_hi, (gx, gy), gr + SS)
            _gem_diamond(big, gx, gy, gr, col)


def _crossed_arms(big, cx, shoulder_y, waist_y, skin, skin_lo, skin_hi,
                  gold, gold_hi, arm_w=9):
    """Aladdin-style crossed arms: two arms meeting at the centre,
    each from shoulder to opposite waist, with gold cuffs."""
    _arm(big,
         cx + int(50 * SS), shoulder_y + int(4 * SS),
         cx + int(20 * SS), int(150 * SS),
         cx - int(26 * SS), int(165 * SS),
         skin, skin_lo, skin_hi, gold, gold_hi, w=arm_w)
    _arm(big,
         cx - int(50 * SS), shoulder_y + int(4 * SS),
         cx - int(20 * SS), int(145 * SS),
         cx + int(26 * SS), int(160 * SS),
         skin, skin_lo, skin_hi, gold, gold_hi, w=arm_w)


# ─────────────────────────────────────────────────────────────────────────────
# Champion crown + arms (shared by F1, F2, H4)
# ─────────────────────────────────────────────────────────────────────────────

def _champion_crown(big, cx, crown_y, spikes=3,
                    gold=(245, 205, 105), gold_hi=(255, 240, 175),
                    gold_lo=(160, 115, 30),
                    ruby=(215, 70, 85), cyan=(160, 230, 255)):
    """Gem-spike crown across the forehead. spikes=3 for F1 (ruby
    centre + cyan flanks), spikes=5 for F2 (richer)."""
    crown_w = int(W * 0.20 * SS)
    crown_h = int(W * 0.040 * SS)
    pygame.draw.rect(big, gold_lo,
                     (cx - crown_w, crown_y, crown_w * 2, crown_h))
    pygame.draw.rect(big, gold,
                     (cx - crown_w + SS, crown_y + SS,
                      crown_w * 2 - 2 * SS, crown_h - 2 * SS))
    pygame.draw.line(big, gold_hi,
                     (cx - crown_w + 3 * SS, crown_y + int(crown_h * 0.4)),
                     (cx + crown_w - 3 * SS, crown_y + int(crown_h * 0.4)),
                     max(2, SS))
    # Spikes
    if spikes == 3:
        spike_xs = (-int(W * 0.06 * SS), 0, int(W * 0.06 * SS))
    else:
        # 5 spikes
        spike_xs = tuple(int(i * W * 0.045 * SS) for i in range(-2, 3))
    for spx in spike_xs:
        is_centre = (spx == 0)
        spike_h = int(W * 0.075 * SS) if is_centre else int(W * 0.055 * SS)
        pygame.draw.polygon(big, gold_lo,
                            [(cx + spx - int(W * 0.022 * SS), crown_y),
                             (cx + spx, crown_y - spike_h),
                             (cx + spx + int(W * 0.022 * SS), crown_y)])
        pygame.draw.polygon(big, gold,
                            [(cx + spx - int(W * 0.018 * SS), crown_y),
                             (cx + spx, crown_y - spike_h + SS),
                             (cx + spx + int(W * 0.018 * SS), crown_y)])
        # Gem at tip
        gem_y = crown_y - int(spike_h * 0.65)
        if is_centre:
            _gem_diamond(big, cx + spx, gem_y, int(W * 0.018 * SS), ruby)
        elif abs(spx) <= int(W * 0.05 * SS):
            pygame.draw.circle(big, cyan, (cx + spx, gem_y),
                               max(2, int(W * 0.011 * SS)))
            pygame.draw.circle(big, (255, 255, 255),
                               (cx + spx - SS, gem_y - SS),
                               max(1, int(W * 0.005 * SS)))
        else:
            pygame.draw.circle(big, (65, 180, 90), (cx + spx, gem_y),
                               max(2, int(W * 0.011 * SS)))


def _champion_arms(big, cx, shoulder_y, skin, skin_lo, skin_hi,
                   gold, gold_hi, orb_color=(160, 230, 255),
                   orb_radius_mul=1.0, arm_w=10):
    """Both arms outstretched, raised, with magic orbs at the palms."""
    for side in (-1, +1):
        sh_x = cx + side * int(W * 0.20 * SS)
        sh_y = shoulder_y
        wr_x = sh_x + side * int(W * 0.18 * SS)
        wr_y = sh_y - int(H * 0.10 * SS)
        el_x = (sh_x + wr_x) // 2 + side * int(W * 0.025 * SS)
        el_y = (sh_y + wr_y) // 2 + int(H * 0.012 * SS)
        _arm(big, sh_x, sh_y, el_x, el_y, wr_x, wr_y,
             skin, skin_lo, skin_hi, gold, gold_hi, w=arm_w)
        # Orb at palm
        palm_x = wr_x + side * int(W * 0.015 * SS)
        palm_y = wr_y - int(H * 0.025 * SS)
        orb_r = int(W * 0.05 * SS * orb_radius_mul)
        s = pygame.Surface((orb_r * 3, orb_r * 3), pygame.SRCALPHA)
        pygame.draw.circle(s, (*orb_color, 110),
                           (orb_r * 3 // 2, orb_r * 3 // 2),
                           int(orb_r * 1.3))
        pygame.draw.circle(s, (*orb_color, 200),
                           (orb_r * 3 // 2, orb_r * 3 // 2), orb_r)
        pygame.draw.circle(s, (*gold_hi, 230),
                           (orb_r * 3 // 2, orb_r * 3 // 2), int(orb_r * 0.55))
        pygame.draw.circle(s, (255, 255, 255, 255),
                           (orb_r * 3 // 2, orb_r * 3 // 2), int(orb_r * 0.25))
        big.blit(s, (palm_x - orb_r * 3 // 2, palm_y - orb_r * 3 // 2))


# ─────────────────────────────────────────────────────────────────────────────
# Common Aladdin / Champion palettes
# ─────────────────────────────────────────────────────────────────────────────

ALADDIN = dict(
    SKIN     = (70, 175, 220),
    SKIN_HI  = (170, 230, 255),
    SKIN_LO  = (25, 115, 175),
    GOLD     = (245, 205, 105),
    GOLD_HI  = (255, 240, 175),
    GOLD_LO  = (160, 115, 30),
    BLACK    = (18, 14, 10),
    WHITE    = (250, 250, 245),
    HAIR     = (28, 20, 18),
    RUBY     = (215, 70, 85),
    EMERALD  = (65, 180, 90),
    SAPPHIRE = (70, 130, 220),
    CYAN     = (160, 230, 255),
)


# ─────────────────────────────────────────────────────────────────────────────
# Common Aladdin body shell (used by A1, A2, H1, H2, H3)
# ─────────────────────────────────────────────────────────────────────────────

def _aladdin_body_shell(big, cx, t, P, smoke_segments=6, mid_layer=True):
    """Smoke trail + V-torso + pec definition + abs line + belly
    highlight. Returns (head_cy, head_r) for downstream face drawing."""
    _smoke_curl(big, cx - 10 * SS, int(225 * SS), length=70,
                color_lo=P["SKIN_LO"], color_mid=P["SKIN"],
                color_hi=P["SKIN_HI"], t=t, side=-1,
                segments=smoke_segments)
    _v_torso(big, cx,
             neck_y=int(115 * SS),
             shoulder_y=int(134 * SS),
             waist_y=int(195 * SS),
             base_y=int(238 * SS),
             neck_w=int(20 * SS),
             shoulder_w=int(66 * SS),
             waist_w=int(33 * SS),
             base_w=int(20 * SS),
             body=P["SKIN"], body_lo=P["SKIN_LO"], body_hi=P["SKIN_HI"],
             mid_alpha_layer=mid_layer)
    # Pec definition
    for sx in (-int(22 * SS), int(22 * SS)):
        pygame.draw.ellipse(big, P["SKIN_HI"],
                            (cx + sx - int(22 * SS), int(138 * SS),
                             int(38 * SS), int(22 * SS)))
        pygame.draw.arc(big, P["SKIN_LO"],
                        (cx + sx - int(22 * SS), int(146 * SS),
                         int(38 * SS), int(16 * SS)),
                        math.radians(0), math.radians(180), max(3, SS))
    # Abs line + belly highlight
    pygame.draw.line(big, P["SKIN_LO"],
                     (cx, int(162 * SS)), (cx, int(192 * SS)),
                     max(2, SS - 1))
    pygame.draw.ellipse(big, P["SKIN_HI"],
                        (cx - int(14 * SS), int(168 * SS),
                         int(28 * SS), int(22 * SS)))
    return int(64 * SS), int(36 * SS)


# ═════════════════════════════════════════════════════════════════════════════
# Variant 1: A1 — Classic Aladdin
# ═════════════════════════════════════════════════════════════════════════════
def draw_a1(big, cx, t):
    P = ALADDIN
    head_cy, head_r = _aladdin_body_shell(big, cx, t, P)
    _crossed_arms(big, cx, int(132 * SS), int(180 * SS),
                  P["SKIN"], P["SKIN_LO"], P["SKIN_HI"],
                  P["GOLD"], P["GOLD_HI"])
    _aladdin_sash(big, cx, int(195 * SS), int(46 * SS),
                  P["GOLD"], P["GOLD_HI"], P["GOLD_LO"], gems=[P["RUBY"]])
    _head(big, cx, head_cy, head_r, P["SKIN"], P["SKIN_LO"], P["SKIN_HI"])
    _aladdin_topknot_band(big, cx, head_cy, head_r,
                          P["HAIR"], P["GOLD"], P["GOLD_HI"], P["GOLD_LO"],
                          P["RUBY"])
    _aladdin_face(big, cx, head_cy, head_r,
                  P["HAIR"], P["WHITE"], P["RUBY"])
    _aladdin_earrings(big, cx, head_cy, P["GOLD"], P["GOLD_LO"])


# ═════════════════════════════════════════════════════════════════════════════
# Variant 2: A2 — Aladdin Reborn (enhanced)
# ═════════════════════════════════════════════════════════════════════════════
def draw_a2(big, cx, t):
    P = ALADDIN
    # Thicker double smoke trail
    _smoke_curl(big, cx - 14 * SS, int(228 * SS), length=80,
                color_lo=P["SKIN_LO"], color_mid=P["SKIN"],
                color_hi=P["SKIN_HI"], t=t, side=-1, segments=7)
    _smoke_curl(big, cx + 14 * SS, int(228 * SS), length=60,
                color_lo=P["SKIN_LO"], color_mid=P["SKIN"],
                color_hi=P["SKIN_HI"], t=t + 0.7, side=+1, segments=5)
    _v_torso(big, cx,
             neck_y=int(112 * SS),
             shoulder_y=int(130 * SS),
             waist_y=int(196 * SS),
             base_y=int(240 * SS),
             neck_w=int(20 * SS),
             shoulder_w=int(70 * SS),
             waist_w=int(33 * SS),
             base_w=int(20 * SS),
             body=P["SKIN"], body_lo=P["SKIN_LO"], body_hi=P["SKIN_HI"])
    # Extra flank highlight bands
    for sx in (-int(24 * SS), int(24 * SS)):
        pygame.draw.ellipse(big, P["SKIN_HI"],
                            (cx + sx - int(24 * SS), int(135 * SS),
                             int(42 * SS), int(24 * SS)))
        pygame.draw.arc(big, P["SKIN_LO"],
                        (cx + sx - int(24 * SS), int(144 * SS),
                         int(42 * SS), int(16 * SS)),
                        math.radians(0), math.radians(180), max(3, SS))
    pygame.draw.line(big, P["SKIN_LO"],
                     (cx, int(160 * SS)), (cx, int(194 * SS)),
                     max(2, SS - 1))
    # ── crossed arms with twin gold armbands ───────────────────────────
    _crossed_arms(big, cx, int(130 * SS), int(182 * SS),
                  P["SKIN"], P["SKIN_LO"], P["SKIN_HI"],
                  P["GOLD"], P["GOLD_HI"])
    # Extra gold armbands above the wrist cuffs
    for arm_x, arm_y in ((cx - int(22 * SS), int(155 * SS)),
                         (cx + int(22 * SS), int(155 * SS))):
        pygame.draw.ellipse(big, P["GOLD"],
                            (arm_x - int(7 * SS), arm_y - int(2 * SS),
                             int(14 * SS), int(5 * SS)))
        pygame.draw.line(big, P["GOLD_HI"],
                         (arm_x - int(6 * SS), arm_y),
                         (arm_x + int(6 * SS), arm_y),
                         max(1, SS - 1))
    # Triple-gem sash
    _aladdin_sash(big, cx, int(198 * SS), int(50 * SS),
                  P["GOLD"], P["GOLD_HI"], P["GOLD_LO"],
                  gems=[P["RUBY"], P["EMERALD"], P["SAPPHIRE"]])
    # Head
    head_cy, head_r = int(60 * SS), int(38 * SS)
    _head(big, cx, head_cy, head_r,
          P["SKIN"], P["SKIN_LO"], P["SKIN_HI"])
    _aladdin_topknot_band(big, cx, head_cy, head_r,
                          P["HAIR"], P["GOLD"], P["GOLD_HI"], P["GOLD_LO"],
                          P["RUBY"])
    _aladdin_face(big, cx, head_cy, head_r,
                  P["HAIR"], P["WHITE"], P["RUBY"])
    _aladdin_earrings(big, cx, head_cy, P["GOLD"], P["GOLD_LO"],
                      ruby=P["RUBY"])


# ═════════════════════════════════════════════════════════════════════════════
# Variant 3: F1 — Classic Champion
# ═════════════════════════════════════════════════════════════════════════════
def draw_f1(big, cx, t):
    P = ALADDIN
    # Ambient sparkles
    random.seed(5)
    for _ in range(18):
        sx = random.randint(int(8 * SS), int((W - 8) * SS))
        sy = random.randint(int(8 * SS), int((H - 8) * SS))
        sr = random.randint(int(1 * SS), int(3 * SS))
        _star(big, sx, sy, sr, P["GOLD_HI"])
    # Twin smoke trails
    _smoke_curl(big, cx - 14 * SS, int(228 * SS), length=60,
                color_lo=P["SKIN_LO"], color_mid=P["SKIN"],
                color_hi=P["SKIN_HI"], t=t, side=-1)
    _smoke_curl(big, cx + 14 * SS, int(228 * SS), length=60,
                color_lo=P["SKIN_LO"], color_mid=P["SKIN"],
                color_hi=P["SKIN_HI"], t=t + 1.2, side=+1)
    _v_torso(big, cx,
             neck_y=int(120 * SS),
             shoulder_y=int(138 * SS),
             waist_y=int(196 * SS),
             base_y=int(236 * SS),
             neck_w=int(20 * SS),
             shoulder_w=int(70 * SS),
             waist_w=int(34 * SS),
             base_w=int(20 * SS),
             body=P["SKIN"], body_lo=P["SKIN_LO"], body_hi=P["SKIN_HI"])
    # Pec definition + abs line
    for sx in (-int(24 * SS), int(24 * SS)):
        pygame.draw.ellipse(big, P["SKIN_HI"],
                            (cx + sx - int(24 * SS), int(140 * SS),
                             int(42 * SS), int(24 * SS)))
        pygame.draw.arc(big, P["SKIN_LO"],
                        (cx + sx - int(24 * SS), int(148 * SS),
                         int(42 * SS), int(16 * SS)),
                        math.radians(0), math.radians(180), max(3, SS))
    pygame.draw.line(big, P["SKIN_LO"],
                     (cx, int(163 * SS)), (cx, int(194 * SS)),
                     max(2, SS - 1))
    # Outstretched champion arms with orbs
    _champion_arms(big, cx, int(140 * SS),
                   P["SKIN"], P["SKIN_LO"], P["SKIN_HI"],
                   P["GOLD"], P["GOLD_HI"], orb_color=P["CYAN"])
    # Sash at the waist
    _aladdin_sash(big, cx, int(196 * SS), int(40 * SS),
                  P["GOLD"], P["GOLD_HI"], P["GOLD_LO"], gems=[P["RUBY"]])
    # Head + crown
    head_cy, head_r = int(60 * SS), int(40 * SS)
    _head(big, cx, head_cy, head_r,
          P["SKIN"], P["SKIN_LO"], P["SKIN_HI"])
    _champion_crown(big, cx, head_cy - int(24 * SS), spikes=3,
                    gold=P["GOLD"], gold_hi=P["GOLD_HI"],
                    gold_lo=P["GOLD_LO"], ruby=P["RUBY"], cyan=P["CYAN"])
    _aladdin_face(big, cx, head_cy, head_r,
                  P["HAIR"], P["WHITE"], P["RUBY"], smile_wide=True)
    _aladdin_earrings(big, cx, head_cy, P["GOLD"], P["GOLD_LO"])


# ═════════════════════════════════════════════════════════════════════════════
# Variant 4: F2 — Heroic Champion (amplified)
# ═════════════════════════════════════════════════════════════════════════════
def draw_f2(big, cx, t):
    P = ALADDIN
    # Soft halo behind the head
    head_cy = int(58 * SS)
    halo_r = int(60 * SS)
    s = pygame.Surface((halo_r * 2 + 4, halo_r * 2 + 4), pygame.SRCALPHA)
    for r_step, alpha in ((halo_r, 60),
                          (int(halo_r * 0.75), 90),
                          (int(halo_r * 0.5), 120)):
        pygame.draw.circle(s, (*P["GOLD_HI"], alpha),
                           (halo_r + 2, halo_r + 2), r_step)
    big.blit(s, (cx - halo_r - 2, head_cy - halo_r - 2))
    # Denser ambient sparkles
    random.seed(9)
    for _ in range(24):
        sx = random.randint(int(8 * SS), int((W - 8) * SS))
        sy = random.randint(int(8 * SS), int((H - 8) * SS))
        sr = random.randint(int(1 * SS), int(4 * SS))
        _star(big, sx, sy, sr, P["GOLD_HI"])
    # Thicker twin smoke trails
    _smoke_curl(big, cx - 16 * SS, int(232 * SS), length=78,
                color_lo=P["SKIN_LO"], color_mid=P["SKIN"],
                color_hi=P["SKIN_HI"], t=t, side=-1, segments=7)
    _smoke_curl(big, cx + 16 * SS, int(232 * SS), length=70,
                color_lo=P["SKIN_LO"], color_mid=P["SKIN"],
                color_hi=P["SKIN_HI"], t=t + 0.9, side=+1, segments=6)
    # Bigger torso
    _v_torso(big, cx,
             neck_y=int(115 * SS),
             shoulder_y=int(134 * SS),
             waist_y=int(200 * SS),
             base_y=int(244 * SS),
             neck_w=int(20 * SS),
             shoulder_w=int(78 * SS),
             waist_w=int(36 * SS),
             base_w=int(22 * SS),
             body=P["SKIN"], body_lo=P["SKIN_LO"], body_hi=P["SKIN_HI"])
    # Bigger pecs + 6-pack
    for sx in (-int(26 * SS), int(26 * SS)):
        pygame.draw.ellipse(big, P["SKIN_HI"],
                            (cx + sx - int(26 * SS), int(138 * SS),
                             int(46 * SS), int(26 * SS)))
        pygame.draw.arc(big, P["SKIN_LO"],
                        (cx + sx - int(26 * SS), int(146 * SS),
                         int(46 * SS), int(18 * SS)),
                        math.radians(0), math.radians(180), max(3, SS))
    for ay in (int(166 * SS), int(178 * SS), int(190 * SS)):
        for ax in (-int(9 * SS), int(9 * SS)):
            pygame.draw.ellipse(big, P["SKIN_HI"],
                                (cx + ax - int(7 * SS), ay,
                                 int(14 * SS), int(8 * SS)))
    pygame.draw.line(big, P["SKIN_LO"],
                     (cx, int(160 * SS)), (cx, int(200 * SS)),
                     max(2, SS - 1))
    # Thicker outstretched arms with larger orbs
    _champion_arms(big, cx, int(138 * SS),
                   P["SKIN"], P["SKIN_LO"], P["SKIN_HI"],
                   P["GOLD"], P["GOLD_HI"], orb_color=P["CYAN"],
                   orb_radius_mul=1.3, arm_w=12)
    # Engraved sash
    _aladdin_sash(big, cx, int(200 * SS), int(48 * SS),
                  P["GOLD"], P["GOLD_HI"], P["GOLD_LO"],
                  gems=[P["RUBY"], P["EMERALD"], P["SAPPHIRE"]])
    # Head + 5-spike crown
    head_r = int(42 * SS)
    _head(big, cx, head_cy, head_r,
          P["SKIN"], P["SKIN_LO"], P["SKIN_HI"])
    _champion_crown(big, cx, head_cy - int(26 * SS), spikes=5,
                    gold=P["GOLD"], gold_hi=P["GOLD_HI"],
                    gold_lo=P["GOLD_LO"], ruby=P["RUBY"], cyan=P["CYAN"])
    _aladdin_face(big, cx, head_cy, head_r,
                  P["HAIR"], P["WHITE"], P["RUBY"], smile_wide=True)
    _aladdin_earrings(big, cx, head_cy, P["GOLD"], P["GOLD_LO"],
                      ruby=P["RUBY"])


# ═════════════════════════════════════════════════════════════════════════════
# Variant 5: H1 — Cosmic Aladdin (nebula body)
# ═════════════════════════════════════════════════════════════════════════════
def draw_h1(big, cx, t):
    P = ALADDIN
    NEB_PURPLE = (135, 70, 200)
    NEB_PINK   = (235, 95, 175)
    NEB_BLUE   = (75, 150, 240)

    # Backdrop stars
    random.seed(14)
    for _ in range(25):
        sx = random.randint(int(6 * SS), int((W - 6) * SS))
        sy = random.randint(int(6 * SS), int((H - 6) * SS))
        sr = random.randint(int(1 * SS), int(3 * SS))
        _star(big, sx, sy, sr, (220, 200, 255))

    # Outline silhouette polygon for masking nebula fill
    silhouette = [
        (cx - int(20 * SS), int(115 * SS)),
        (cx - int(66 * SS), int(134 * SS)),
        (cx - int(33 * SS), int(195 * SS)),
        (cx - int(20 * SS), int(238 * SS)),
        (cx + int(20 * SS), int(238 * SS)),
        (cx + int(33 * SS), int(195 * SS)),
        (cx + int(66 * SS), int(134 * SS)),
        (cx + int(20 * SS), int(115 * SS)),
    ]
    # Dark fill first
    pygame.draw.polygon(big, (30, 20, 60), silhouette)
    # Nebula clouds (will spill outside but we re-stroke the edge)
    mask = pygame.Surface((PW, PH), pygame.SRCALPHA)
    _nebula_fill(mask, silhouette,
                 palette=[NEB_PURPLE, NEB_PINK, NEB_BLUE], density=60)
    # Apply mask through polygon: easiest path is alpha-blit then
    # re-stroke the silhouette edge to clean up any bleed.
    big.blit(mask, (0, 0))
    pygame.draw.polygon(big, (220, 200, 255), silhouette, max(3, SS + 1))
    # Stars on body
    random.seed(17)
    for _ in range(20):
        sx = cx + random.randint(-int(50 * SS), int(50 * SS))
        sy = random.randint(int(120 * SS), int(230 * SS))
        pygame.draw.circle(big, (255, 255, 255), (sx, sy),
                           max(1, SS // 2))

    # Smoke trail (cosmic-tinted)
    _smoke_curl(big, cx - 10 * SS, int(232 * SS), length=70,
                color_lo=(60, 30, 100), color_mid=NEB_PURPLE,
                color_hi=(210, 180, 255), t=t, side=-1)
    # Aladdin arms drawn on top (skin-colored)
    _crossed_arms(big, cx, int(134 * SS), int(180 * SS),
                  P["SKIN"], P["SKIN_LO"], P["SKIN_HI"],
                  P["GOLD"], P["GOLD_HI"])
    # Sash
    _aladdin_sash(big, cx, int(196 * SS), int(46 * SS),
                  P["GOLD"], P["GOLD_HI"], P["GOLD_LO"], gems=[P["RUBY"]])
    # Head (Aladdin) - face stays normal but eyes are galaxy
    head_cy, head_r = int(64 * SS), int(38 * SS)
    _head(big, cx, head_cy, head_r,
          P["SKIN"], P["SKIN_LO"], P["SKIN_HI"])
    _aladdin_topknot_band(big, cx, head_cy, head_r,
                          P["HAIR"], P["GOLD"], P["GOLD_HI"], P["GOLD_LO"],
                          P["RUBY"])
    # Galaxy eyes — purple irises with bright dot
    for sx in (-int(12 * SS), int(12 * SS)):
        pygame.draw.ellipse(big, P["WHITE"],
                            (cx + sx - int(8 * SS),
                             head_cy + int(2 * SS) - int(6 * SS),
                             int(16 * SS), int(11 * SS)))
        pygame.draw.circle(big, NEB_PURPLE,
                           (cx + sx, head_cy + int(2 * SS)), int(5 * SS))
        pygame.draw.circle(big, NEB_PINK,
                           (cx + sx, head_cy + int(2 * SS)), int(3 * SS))
        pygame.draw.circle(big, (255, 255, 255),
                           (cx + sx - SS, head_cy + int(1 * SS)),
                           max(1, SS))
    # Reuse face mouth/mustache without eyes
    mt = head_cy + int(15 * SS)
    pygame.draw.polygon(big, P["HAIR"],
                        [(cx - int(13 * SS), mt),
                         (cx + int(13 * SS), mt),
                         (cx + int(9 * SS), mt + int(11 * SS)),
                         (cx - int(9 * SS), mt + int(11 * SS))])
    pygame.draw.polygon(big, P["WHITE"],
                        [(cx - int(11 * SS), mt + int(2 * SS)),
                         (cx + int(11 * SS), mt + int(2 * SS)),
                         (cx + int(7 * SS), mt + int(8 * SS)),
                         (cx - int(7 * SS), mt + int(8 * SS))])
    pygame.draw.polygon(big, P["HAIR"],
                        [(cx - int(6 * SS), mt + int(11 * SS)),
                         (cx + int(6 * SS), mt + int(11 * SS)),
                         (cx, mt + int(24 * SS))])
    # Mustache
    pygame.draw.arc(big, P["HAIR"],
                    (cx - int(18 * SS), head_cy + int(10 * SS),
                     int(18 * SS), int(10 * SS)),
                    math.radians(190), math.radians(360), max(3, SS + 1))
    pygame.draw.arc(big, P["HAIR"],
                    (cx, head_cy + int(10 * SS),
                     int(18 * SS), int(10 * SS)),
                    math.radians(180), math.radians(350), max(3, SS + 1))
    _aladdin_earrings(big, cx, head_cy, P["GOLD"], P["GOLD_LO"])


# ═════════════════════════════════════════════════════════════════════════════
# Variant 6: H2 — Storm Aladdin (lightning-charged)
# ═════════════════════════════════════════════════════════════════════════════
def draw_h2(big, cx, t):
    P = ALADDIN
    # Storm-cloud aura around the body
    for cx_d, cy_d, r in ((cx - int(56 * SS), int(140 * SS), int(40 * SS)),
                          (cx + int(56 * SS), int(140 * SS), int(40 * SS)),
                          (cx - int(70 * SS), int(200 * SS), int(34 * SS)),
                          (cx + int(70 * SS), int(200 * SS), int(34 * SS))):
        s = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (50, 90, 140, 200),
                           (r + 2, r + 2), r)
        big.blit(s, (cx_d - r - 2, cy_d - r - 2))
    # Body
    _aladdin_body_shell(big, cx, t, P, mid_layer=False)
    # Crackling lightning across the chest
    _lightning(big,
               [(cx - int(34 * SS), int(155 * SS)),
                (cx - int(14 * SS), int(170 * SS)),
                (cx + int(4 * SS), int(150 * SS)),
                (cx + int(20 * SS), int(170 * SS)),
                (cx + int(36 * SS), int(155 * SS))],
               colors=(P["CYAN"], (220, 240, 255), (255, 255, 255)),
               widths=(max(8, int(2.4 * SS)), max(4, SS + 2), max(2, SS)))
    # Crossed arms
    _crossed_arms(big, cx, int(132 * SS), int(180 * SS),
                  P["SKIN"], P["SKIN_LO"], P["SKIN_HI"],
                  P["GOLD"], P["GOLD_HI"])
    # Outer flank bolts
    for path in (
            [(cx - int(78 * SS), int(90 * SS)),
             (cx - int(56 * SS), int(112 * SS)),
             (cx - int(80 * SS), int(135 * SS)),
             (cx - int(60 * SS), int(160 * SS))],
            [(cx + int(78 * SS), int(90 * SS)),
             (cx + int(56 * SS), int(112 * SS)),
             (cx + int(80 * SS), int(135 * SS)),
             (cx + int(60 * SS), int(160 * SS))]):
        _lightning(big, path,
                   colors=(P["CYAN"], (255, 255, 255)),
                   widths=(max(4, SS + 2), max(2, SS)))
    # Sash
    _aladdin_sash(big, cx, int(195 * SS), int(46 * SS),
                  P["GOLD"], P["GOLD_HI"], P["GOLD_LO"], gems=[P["CYAN"]])
    # Head
    head_cy, head_r = int(64 * SS), int(36 * SS)
    _head(big, cx, head_cy, head_r,
          P["SKIN"], P["SKIN_LO"], P["SKIN_HI"])
    # Lightning-shaped tiara (forked) instead of normal headband
    tiara_y = head_cy - int(22 * SS)
    pygame.draw.lines(big, P["GOLD_LO"], False,
                      [(cx - int(34 * SS), tiara_y + int(6 * SS)),
                       (cx - int(22 * SS), tiara_y - int(6 * SS)),
                       (cx - int(8 * SS),  tiara_y + int(6 * SS)),
                       (cx + int(2 * SS),  tiara_y - int(8 * SS)),
                       (cx + int(14 * SS), tiara_y + int(6 * SS)),
                       (cx + int(28 * SS), tiara_y - int(6 * SS)),
                       (cx + int(36 * SS), tiara_y + int(6 * SS))],
                      max(4, SS + 2))
    pygame.draw.lines(big, P["GOLD"], False,
                      [(cx - int(34 * SS), tiara_y + int(6 * SS)),
                       (cx - int(22 * SS), tiara_y - int(6 * SS)),
                       (cx - int(8 * SS),  tiara_y + int(6 * SS)),
                       (cx + int(2 * SS),  tiara_y - int(8 * SS)),
                       (cx + int(14 * SS), tiara_y + int(6 * SS)),
                       (cx + int(28 * SS), tiara_y - int(6 * SS)),
                       (cx + int(36 * SS), tiara_y + int(6 * SS))],
                      max(3, SS + 1))
    # Cyan gem at the centre point
    _gem_diamond(big, cx + int(2 * SS), tiara_y - int(8 * SS),
                 int(5 * SS), P["CYAN"])
    # Topknot
    pygame.draw.circle(big, P["HAIR"],
                       (cx, head_cy - head_r - int(2 * SS)), int(10 * SS))
    # Face with cyan eyes
    _aladdin_face(big, cx, head_cy, head_r,
                  P["HAIR"], P["WHITE"], P["RUBY"],
                  eye_iris=(20, 60, 110))
    # Eye cyan glow overlay
    for sx in (-int(12 * SS), int(12 * SS)):
        s = pygame.Surface((int(20 * SS), int(20 * SS)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*P["CYAN"], 130),
                           (int(10 * SS), int(10 * SS)), int(8 * SS))
        big.blit(s, (cx + sx - int(10 * SS),
                     head_cy + int(2 * SS) - int(10 * SS)))
    _aladdin_earrings(big, cx, head_cy, P["GOLD"], P["GOLD_LO"])


# ═════════════════════════════════════════════════════════════════════════════
# Variant 7: H3 — Vizier Aladdin (ornate turban + bushy beard)
# ═════════════════════════════════════════════════════════════════════════════
def draw_h3(big, cx, t):
    P = ALADDIN
    PURPLE    = (88, 35, 110)
    PURPLE_HI = (170, 105, 195)
    PURPLE_LO = (50, 18, 68)
    EMERALD   = P["EMERALD"]
    # Smoke (purple-tinted)
    _smoke_curl(big, cx - 10 * SS, int(228 * SS), length=70,
                color_lo=PURPLE_LO, color_mid=PURPLE, color_hi=PURPLE_HI,
                t=t, side=-1)
    # Body
    _v_torso(big, cx,
             neck_y=int(118 * SS),
             shoulder_y=int(136 * SS),
             waist_y=int(196 * SS),
             base_y=int(240 * SS),
             neck_w=int(20 * SS),
             shoulder_w=int(68 * SS),
             waist_w=int(35 * SS),
             base_w=int(20 * SS),
             body=P["SKIN"], body_lo=P["SKIN_LO"], body_hi=P["SKIN_HI"])
    # X gold chain across torso
    for s, e in (((cx - int(42 * SS), int(140 * SS)),
                  (cx + int(42 * SS), int(190 * SS))),
                 ((cx + int(42 * SS), int(140 * SS)),
                  (cx - int(42 * SS), int(190 * SS)))):
        pygame.draw.line(big, P["GOLD_LO"], s, e, max(5, SS + 2))
        pygame.draw.line(big, P["GOLD"],    s, e, max(3, SS + 1))
    # Centre emerald gem on the chain X
    pygame.draw.circle(big, P["GOLD_LO"], (cx, int(165 * SS)), int(11 * SS))
    pygame.draw.circle(big, P["GOLD"],    (cx, int(165 * SS)), int(9 * SS))
    _gem_diamond(big, cx, int(165 * SS), int(6 * SS), EMERALD)
    # Sleeved crossed arms (purple sleeves with gold trim)
    # Draw sleeves as wider polygons UNDER the arm lines
    for side in (-1, 1):
        sleeve_pts = [
            (cx + side * int(58 * SS), int(140 * SS)),
            (cx + side * int(34 * SS), int(160 * SS)),
            (cx + side * int(8 * SS),  int(166 * SS)),
            (cx + side * int(14 * SS), int(176 * SS)),
            (cx + side * int(40 * SS), int(172 * SS)),
        ]
        pygame.draw.polygon(big, PURPLE, sleeve_pts)
        pygame.draw.lines(big, P["GOLD"], False, sleeve_pts[:3], max(2, SS))
    _crossed_arms(big, cx, int(135 * SS), int(180 * SS),
                  P["SKIN"], P["SKIN_LO"], P["SKIN_HI"],
                  P["GOLD"], P["GOLD_HI"])
    # Sash
    _aladdin_sash(big, cx, int(198 * SS), int(48 * SS),
                  P["GOLD"], P["GOLD_HI"], P["GOLD_LO"],
                  gems=[P["RUBY"], EMERALD, P["SAPPHIRE"]])
    # Head
    head_cy, head_r = int(62 * SS), int(34 * SS)
    _head(big, cx, head_cy, head_r,
          P["SKIN"], P["SKIN_LO"], P["SKIN_HI"])
    # ── HUGE ornate turban with twin feathers ──
    dome_w = int(94 * SS)
    dome_h = int(60 * SS)
    pygame.draw.ellipse(big, PURPLE_LO,
                        (cx - dome_w // 2 - 2 * SS,
                         head_cy - int(50 * SS) - 2 * SS,
                         dome_w + 4 * SS, dome_h + 4 * SS))
    pygame.draw.ellipse(big, PURPLE,
                        (cx - dome_w // 2, head_cy - int(50 * SS),
                         dome_w, dome_h))
    # Wrapping bands
    for dy in (int(-40 * SS), int(-30 * SS), int(-20 * SS)):
        pygame.draw.ellipse(big, PURPLE_HI,
                            (cx - dome_w // 2 + int(4 * SS),
                             head_cy + dy,
                             dome_w - int(8 * SS), int(7 * SS)))
    # Gold band at base
    band_y = head_cy - int(16 * SS)
    pygame.draw.ellipse(big, P["GOLD_LO"],
                        (cx - int(44 * SS), band_y - 2 * SS,
                         int(88 * SS), int(22 * SS) + 4 * SS))
    pygame.draw.ellipse(big, P["GOLD"],
                        (cx - int(42 * SS), band_y,
                         int(84 * SS), int(20 * SS)))
    pygame.draw.ellipse(big, P["GOLD_HI"],
                        (cx - int(38 * SS), band_y + int(2 * SS),
                         int(76 * SS), int(5 * SS)))
    # Centre ruby in gold cradle
    cgy = band_y + int(11 * SS)
    pygame.draw.circle(big, P["GOLD_LO"], (cx, cgy), int(14 * SS))
    pygame.draw.circle(big, P["GOLD"], (cx, cgy), int(12 * SS))
    _gem_diamond(big, cx, cgy, int(8 * SS), P["RUBY"])
    # Twin feathers
    for side in (-1, 1):
        fx0, fy0 = cx + side * int(22 * SS), head_cy - int(48 * SS)
        fx1, fy1 = cx + side * int(50 * SS), head_cy - int(90 * SS)
        pygame.draw.line(big, PURPLE_HI, (fx0, fy0), (fx1, fy1),
                         max(3, SS + 1))
        pygame.draw.circle(big, PURPLE, (fx1, fy1), int(10 * SS))
        pygame.draw.circle(big, EMERALD, (fx1, fy1), int(7 * SS))
        pygame.draw.circle(big, P["SAPPHIRE"], (fx1, fy1), int(4 * SS))
        pygame.draw.circle(big, (255, 255, 255), (fx1 - SS, fy1 - SS),
                           int(1 * SS))
    # Big bushy beard
    beard_top = head_cy + int(14 * SS)
    pygame.draw.polygon(big, P["HAIR"],
                        [(cx - int(22 * SS), beard_top),
                         (cx + int(22 * SS), beard_top),
                         (cx + int(28 * SS), beard_top + int(20 * SS)),
                         (cx + int(20 * SS), beard_top + int(40 * SS)),
                         (cx + int(10 * SS), beard_top + int(52 * SS)),
                         (cx - int(10 * SS), beard_top + int(52 * SS)),
                         (cx - int(20 * SS), beard_top + int(40 * SS)),
                         (cx - int(28 * SS), beard_top + int(20 * SS))])
    for dx in (-int(18 * SS), -int(10 * SS), -int(2 * SS),
               int(6 * SS),  int(14 * SS),  int(22 * SS)):
        pygame.draw.line(big, (60, 35, 25),
                         (cx + dx, beard_top + int(2 * SS)),
                         (cx + int(dx * 0.6), beard_top + int(45 * SS)),
                         max(1, SS // 2))
    # Eyes (narrowed) + curled mustache
    _eye(big, cx - int(11 * SS), head_cy + int(2 * SS), int(4 * SS),
         white=P["WHITE"])
    _eye(big, cx + int(11 * SS), head_cy + int(2 * SS), int(4 * SS),
         white=P["WHITE"])
    for side in (-1, 1):
        mx_in = cx + side * int(4 * SS)
        mx_out = cx + side * int(30 * SS)
        pygame.draw.arc(big, P["HAIR"],
                        (min(mx_in, mx_out), beard_top - int(10 * SS),
                         abs(mx_out - mx_in), int(14 * SS)),
                        math.radians(180), math.radians(360), max(3, SS + 1))
        pygame.draw.circle(big, P["HAIR"],
                           (mx_out, beard_top - int(2 * SS)),
                           int(4 * SS), max(2, SS))


# ═════════════════════════════════════════════════════════════════════════════
# Variant 8: H4 — Mystic Champion (F pose + white wizard beard)
# ═════════════════════════════════════════════════════════════════════════════
def draw_h4(big, cx, t):
    P = ALADDIN
    # Ambient sparkles + faint glow halo
    random.seed(21)
    for _ in range(22):
        sx = random.randint(int(8 * SS), int((W - 8) * SS))
        sy = random.randint(int(8 * SS), int((H - 8) * SS))
        sr = random.randint(int(1 * SS), int(3 * SS))
        _star(big, sx, sy, sr, (210, 230, 255))
    # Twin smoke trails
    _smoke_curl(big, cx - 14 * SS, int(230 * SS), length=60,
                color_lo=P["SKIN_LO"], color_mid=P["SKIN"],
                color_hi=P["SKIN_HI"], t=t, side=-1)
    _smoke_curl(big, cx + 14 * SS, int(230 * SS), length=60,
                color_lo=P["SKIN_LO"], color_mid=P["SKIN"],
                color_hi=P["SKIN_HI"], t=t + 1.2, side=+1)
    # Body
    _v_torso(big, cx,
             neck_y=int(120 * SS),
             shoulder_y=int(138 * SS),
             waist_y=int(198 * SS),
             base_y=int(238 * SS),
             neck_w=int(20 * SS),
             shoulder_w=int(70 * SS),
             waist_w=int(34 * SS),
             base_w=int(20 * SS),
             body=P["SKIN"], body_lo=P["SKIN_LO"], body_hi=P["SKIN_HI"])
    # Outstretched arms with orbs
    _champion_arms(big, cx, int(140 * SS),
                   P["SKIN"], P["SKIN_LO"], P["SKIN_HI"],
                   P["GOLD"], P["GOLD_HI"], orb_color=(210, 230, 255))
    # Sash
    _aladdin_sash(big, cx, int(198 * SS), int(42 * SS),
                  P["GOLD"], P["GOLD_HI"], P["GOLD_LO"], gems=[P["SAPPHIRE"]])
    # Head + crown
    head_cy, head_r = int(60 * SS), int(38 * SS)
    _head(big, cx, head_cy, head_r,
          P["SKIN"], P["SKIN_LO"], P["SKIN_HI"])
    _champion_crown(big, cx, head_cy - int(24 * SS), spikes=3,
                    gold=P["GOLD"], gold_hi=P["GOLD_HI"],
                    gold_lo=P["GOLD_LO"], ruby=P["SAPPHIRE"], cyan=P["CYAN"])
    # Brow + eyes (wise narrowed)
    pygame.draw.polygon(big, (220, 220, 230),
                        [(cx - int(18 * SS), head_cy - int(6 * SS)),
                         (cx - int(4 * SS),  head_cy - int(8 * SS)),
                         (cx - int(4 * SS),  head_cy - int(3 * SS)),
                         (cx - int(18 * SS), head_cy - int(1 * SS))])
    pygame.draw.polygon(big, (220, 220, 230),
                        [(cx + int(18 * SS), head_cy - int(6 * SS)),
                         (cx + int(4 * SS),  head_cy - int(8 * SS)),
                         (cx + int(4 * SS),  head_cy - int(3 * SS)),
                         (cx + int(18 * SS), head_cy - int(1 * SS))])
    _eye(big, cx - int(12 * SS), head_cy + int(2 * SS), int(4 * SS),
         white=P["WHITE"])
    _eye(big, cx + int(12 * SS), head_cy + int(2 * SS), int(4 * SS),
         white=P["WHITE"])
    # LONG flowing white wizard beard reaching the sash
    beard_top = head_cy + int(10 * SS)
    beard_bot = int(178 * SS)
    pygame.draw.polygon(big, (245, 240, 245),
                        [(cx - int(14 * SS), beard_top),
                         (cx + int(14 * SS), beard_top),
                         (cx + int(24 * SS), beard_top + int(26 * SS)),
                         (cx + int(20 * SS), beard_bot - int(20 * SS)),
                         (cx + int(8 * SS),  beard_bot),
                         (cx, beard_bot + int(8 * SS)),
                         (cx - int(8 * SS),  beard_bot),
                         (cx - int(20 * SS), beard_bot - int(20 * SS)),
                         (cx - int(24 * SS), beard_top + int(26 * SS))])
    for dx in (-int(12 * SS), -int(4 * SS), int(4 * SS), int(12 * SS)):
        pygame.draw.line(big, (220, 215, 225),
                         (cx + dx, beard_top + int(4 * SS)),
                         (cx + int(dx * 0.4), beard_bot),
                         max(2, SS - 1))


# ═════════════════════════════════════════════════════════════════════════════
# Variant 9: H5 — Pop Comic Genie (thick black outlines, halftone)
# ═════════════════════════════════════════════════════════════════════════════
def draw_h5(big, cx, t):
    # Comic palette — bright + flat
    SKIN_FLAT = (90, 195, 230)
    SKIN_SHADOW = (40, 130, 180)
    GOLD_FLAT = (255, 215, 95)
    GOLD_SHADOW = (175, 130, 35)
    BLACK_OUT = (15, 12, 8)
    WHITE_FLAT = (255, 255, 250)
    RED_FLAT = (235, 70, 80)
    OUT_W = max(4, int(SS * 1.0))

    # Background bursts/sparkles
    random.seed(33)
    for _ in range(8):
        sx = random.randint(int(8 * SS), int((W - 8) * SS))
        sy = random.randint(int(8 * SS), int((H - 8) * SS))
        sr = random.randint(int(2 * SS), int(5 * SS))
        # Star-burst
        for ang in range(0, 360, 45):
            ax = math.cos(math.radians(ang))
            ay = math.sin(math.radians(ang))
            pygame.draw.line(big, GOLD_FLAT,
                             (sx, sy),
                             (sx + int(ax * sr * 2), sy + int(ay * sr * 2)),
                             max(2, SS - 1))
            pygame.draw.line(big, BLACK_OUT,
                             (sx, sy),
                             (sx + int(ax * sr * 2.2), sy + int(ay * sr * 2.2)),
                             max(1, SS // 2))

    # Smoke (flat with outline)
    for i, (dy, dx, r) in enumerate(((8, -4, 18), (20, -16, 14),
                                     (32, -28, 10))):
        sway = math.sin(t * 1.4 + i * 0.5) * 6 * SS
        tx = cx + dx * SS + sway
        ty = int(225 * SS) + dy * SS
        pygame.draw.ellipse(big, SKIN_FLAT,
                            (tx - r * SS, ty - r * SS // 2 - SS,
                             r * 2 * SS, r * SS + 2 * SS))
        pygame.draw.ellipse(big, BLACK_OUT,
                            (tx - r * SS, ty - r * SS // 2 - SS,
                             r * 2 * SS, r * SS + 2 * SS), OUT_W)

    # Body silhouette
    body_pts = [
        (cx - int(22 * SS), int(115 * SS)),
        (cx - int(68 * SS), int(134 * SS)),
        (cx - int(34 * SS), int(196 * SS)),
        (cx - int(20 * SS), int(238 * SS)),
        (cx + int(20 * SS), int(238 * SS)),
        (cx + int(34 * SS), int(196 * SS)),
        (cx + int(68 * SS), int(134 * SS)),
        (cx + int(22 * SS), int(115 * SS)),
    ]
    pygame.draw.polygon(big, SKIN_FLAT, body_pts)
    # Shadow side with halftone
    shadow_pts = [
        (cx + int(2 * SS), int(115 * SS)),
        (cx + int(22 * SS), int(115 * SS)),
        (cx + int(68 * SS), int(134 * SS)),
        (cx + int(34 * SS), int(196 * SS)),
        (cx + int(20 * SS), int(238 * SS)),
        (cx + int(2 * SS), int(238 * SS)),
    ]
    s = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.polygon(s, SKIN_SHADOW, shadow_pts)
    big.blit(s, (0, 0))
    # Halftone dots in shadow region
    _halftone(big, (cx + int(8 * SS), int(140 * SS),
                    int(60 * SS), int(80 * SS)),
              BLACK_OUT, dot_r=max(2, SS), spacing=int(SS * 3))
    # Thick body outline
    _thick_outline(big, body_pts, BLACK_OUT, OUT_W + SS)

    # Crossed arms (simplified flat)
    for arm in (
            [(cx + int(54 * SS), int(140 * SS)),
             (cx + int(22 * SS), int(165 * SS)),
             (cx - int(30 * SS), int(175 * SS))],
            [(cx - int(54 * SS), int(140 * SS)),
             (cx - int(22 * SS), int(160 * SS)),
             (cx + int(30 * SS), int(170 * SS))]):
        # Outline first (slightly thicker)
        pygame.draw.lines(big, BLACK_OUT, False, arm, max(14, SS * 3))
        # Flat fill
        pygame.draw.lines(big, SKIN_FLAT, False, arm, max(10, int(2.2 * SS)))
    # Big yellow cuffs at wrists
    for wx, wy in ((cx - int(30 * SS), int(175 * SS)),
                   (cx + int(30 * SS), int(170 * SS))):
        pygame.draw.circle(big, BLACK_OUT, (wx, wy), max(10, int(2.4 * SS)))
        pygame.draw.circle(big, GOLD_FLAT, (wx, wy), max(8, int(2.0 * SS)))

    # Sash
    pygame.draw.polygon(big, GOLD_FLAT,
                        [(cx - int(44 * SS), int(190 * SS)),
                         (cx + int(44 * SS), int(192 * SS)),
                         (cx + int(40 * SS), int(208 * SS)),
                         (cx - int(40 * SS), int(206 * SS))])
    pygame.draw.polygon(big, BLACK_OUT,
                        [(cx - int(44 * SS), int(190 * SS)),
                         (cx + int(44 * SS), int(192 * SS)),
                         (cx + int(40 * SS), int(208 * SS)),
                         (cx - int(40 * SS), int(206 * SS))], OUT_W)
    pygame.draw.circle(big, RED_FLAT, (cx, int(199 * SS)), int(8 * SS))
    pygame.draw.circle(big, BLACK_OUT, (cx, int(199 * SS)),
                       int(8 * SS), OUT_W)

    # Head — bigger, exaggerated (1/3 of body)
    head_cy = int(64 * SS)
    head_r = int(44 * SS)
    pygame.draw.circle(big, SKIN_FLAT, (cx, head_cy), head_r)
    pygame.draw.circle(big, BLACK_OUT, (cx, head_cy), head_r, OUT_W + SS)
    # Halftone shadow on right side of face
    s = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.circle(s, SKIN_SHADOW, (cx + int(6 * SS), head_cy), head_r)
    # Use clipping by drawing only over the right half
    pygame.draw.circle(s, (0, 0, 0, 0), (cx - int(40 * SS), head_cy),
                       int(80 * SS))
    big.blit(s, (0, 0))
    _halftone(big, (cx + int(8 * SS), head_cy - int(20 * SS),
                    int(36 * SS), int(40 * SS)),
              BLACK_OUT, dot_r=max(2, SS), spacing=int(SS * 3))

    # Topknot
    pygame.draw.circle(big, BLACK_OUT,
                       (cx, head_cy - head_r - int(2 * SS)), int(13 * SS))
    # Yellow headband
    pygame.draw.rect(big, GOLD_FLAT,
                     (cx - int(40 * SS), head_cy - int(26 * SS),
                      int(80 * SS), int(10 * SS)))
    pygame.draw.rect(big, BLACK_OUT,
                     (cx - int(40 * SS), head_cy - int(26 * SS),
                      int(80 * SS), int(10 * SS)), OUT_W)
    pygame.draw.polygon(big, RED_FLAT,
                        [(cx, head_cy - int(32 * SS)),
                         (cx + int(8 * SS), head_cy - int(22 * SS)),
                         (cx, head_cy - int(12 * SS)),
                         (cx - int(8 * SS), head_cy - int(22 * SS))])
    pygame.draw.polygon(big, BLACK_OUT,
                        [(cx, head_cy - int(32 * SS)),
                         (cx + int(8 * SS), head_cy - int(22 * SS)),
                         (cx, head_cy - int(12 * SS)),
                         (cx - int(8 * SS), head_cy - int(22 * SS))], OUT_W)
    # Big cartoon eyes (just whites + big black pupils)
    for sx in (-int(15 * SS), int(15 * SS)):
        pygame.draw.ellipse(big, WHITE_FLAT,
                            (cx + sx - int(10 * SS), head_cy - int(4 * SS),
                             int(20 * SS), int(15 * SS)))
        pygame.draw.ellipse(big, BLACK_OUT,
                            (cx + sx - int(10 * SS), head_cy - int(4 * SS),
                             int(20 * SS), int(15 * SS)), OUT_W)
        pygame.draw.circle(big, BLACK_OUT,
                           (cx + sx, head_cy + int(3 * SS)), int(5 * SS))
        pygame.draw.circle(big, WHITE_FLAT,
                           (cx + sx - SS, head_cy + int(1 * SS)), int(2 * SS))
    # Mustache & big toothy grin
    pygame.draw.arc(big, BLACK_OUT,
                    (cx - int(22 * SS), head_cy + int(14 * SS),
                     int(22 * SS), int(14 * SS)),
                    math.radians(190), math.radians(360), max(5, int(1.3 * SS)))
    pygame.draw.arc(big, BLACK_OUT,
                    (cx, head_cy + int(14 * SS),
                     int(22 * SS), int(14 * SS)),
                    math.radians(180), math.radians(350), max(5, int(1.3 * SS)))
    # POW! grin
    grin_pts = [(cx - int(18 * SS), head_cy + int(22 * SS)),
                (cx + int(18 * SS), head_cy + int(22 * SS)),
                (cx + int(12 * SS), head_cy + int(36 * SS)),
                (cx - int(12 * SS), head_cy + int(36 * SS))]
    pygame.draw.polygon(big, BLACK_OUT, grin_pts)
    pygame.draw.polygon(big, WHITE_FLAT,
                        [(p[0] * 0.85 + cx * 0.15, p[1])
                         for p in grin_pts])
    # Vertical tooth lines
    for tx in (-int(8 * SS), 0, int(8 * SS)):
        pygame.draw.line(big, BLACK_OUT,
                         (cx + tx, head_cy + int(24 * SS)),
                         (cx + tx, head_cy + int(34 * SS)),
                         max(2, SS - 1))


# ═════════════════════════════════════════════════════════════════════════════
# Variant 10: H6 — Anime Genie (slim, big head, big eyes, dynamic pose)
# ═════════════════════════════════════════════════════════════════════════════
def draw_h6(big, cx, t):
    P = ALADDIN
    # Speed lines trailing
    for i in range(7):
        y = int((110 + i * 18) * SS)
        x0 = int((W - 18 - i * 4) * SS)
        x1 = int((W - 4) * SS)
        pygame.draw.line(big, (200, 220, 240),
                         (x0, y), (x1, y), max(2, SS - 1))
    # Smoke trail (lighter, faster-looking)
    _smoke_curl(big, cx - 10 * SS, int(230 * SS), length=70,
                color_lo=P["SKIN_LO"], color_mid=P["SKIN"],
                color_hi=P["SKIN_HI"], t=t, side=-1, segments=5)
    # Slim torso (slimmer + slightly twisted)
    torso_pts = [
        (cx - int(14 * SS), int(124 * SS)),
        (cx - int(46 * SS), int(140 * SS)),
        (cx - int(26 * SS), int(192 * SS)),
        (cx - int(14 * SS), int(228 * SS)),
        (cx + int(18 * SS), int(228 * SS)),
        (cx + int(30 * SS), int(192 * SS)),
        (cx + int(50 * SS), int(140 * SS)),
        (cx + int(18 * SS), int(124 * SS)),
    ]
    pygame.draw.polygon(big, P["SKIN_LO"],
                        [(x + 2 * SS, y + 2 * SS) for x, y in torso_pts])
    pygame.draw.polygon(big, P["SKIN"], torso_pts)
    # Subtle pec hint (lighter, slimmer)
    for sx in (-int(14 * SS), int(18 * SS)):
        pygame.draw.ellipse(big, P["SKIN_HI"],
                            (cx + sx - int(14 * SS), int(140 * SS),
                             int(26 * SS), int(16 * SS)))
    # Dynamic arms: one forward, one back
    # Forward arm (right, toward viewer)
    _arm(big,
         cx + int(40 * SS), int(140 * SS),
         cx + int(46 * SS), int(170 * SS),
         cx + int(20 * SS), int(196 * SS),
         P["SKIN"], P["SKIN_LO"], P["SKIN_HI"],
         P["GOLD"], P["GOLD_HI"], w=8)
    # Back arm (left, trailing back)
    _arm(big,
         cx - int(34 * SS), int(140 * SS),
         cx - int(60 * SS), int(120 * SS),
         cx - int(54 * SS), int(86 * SS),
         P["SKIN"], P["SKIN_LO"], P["SKIN_HI"],
         P["GOLD"], P["GOLD_HI"], w=8)
    # Sash slim
    pygame.draw.polygon(big, P["GOLD"],
                        [(cx - int(28 * SS), int(196 * SS)),
                         (cx + int(32 * SS), int(196 * SS)),
                         (cx + int(28 * SS), int(208 * SS)),
                         (cx - int(24 * SS), int(208 * SS))])
    # Big anime head
    head_cy = int(56 * SS)
    head_r = int(48 * SS)
    _head(big, cx, head_cy, head_r,
          P["SKIN"], P["SKIN_LO"], P["SKIN_HI"])
    # Spiky hair (5-7 spikes radiating from top)
    HAIR_BLACK = (28, 22, 18)
    HAIR_HI = (70, 60, 60)
    for ang_deg in (-90, -75, -60, -45, -30, -15, 0):
        ang = math.radians(ang_deg - 90)
        tip_x = cx + int(math.cos(ang) * head_r * 1.6)
        tip_y = head_cy + int(math.sin(ang) * head_r * 1.6)
        base_x1 = cx + int(math.cos(ang + 0.2) * head_r * 0.95)
        base_y1 = head_cy + int(math.sin(ang + 0.2) * head_r * 0.95)
        base_x2 = cx + int(math.cos(ang - 0.2) * head_r * 0.95)
        base_y2 = head_cy + int(math.sin(ang - 0.2) * head_r * 0.95)
        pygame.draw.polygon(big, HAIR_BLACK,
                            [(tip_x, tip_y), (base_x1, base_y1),
                             (base_x2, base_y2)])
        pygame.draw.line(big, HAIR_HI,
                         (tip_x, tip_y),
                         ((base_x1 + base_x2) // 2, (base_y1 + base_y2) // 2),
                         max(2, SS - 1))
    # HUGE anime eyes
    eye_y = head_cy + int(6 * SS)
    for sx in (-int(14 * SS), int(14 * SS)):
        # Whites
        pygame.draw.ellipse(big, P["WHITE"],
                            (cx + sx - int(12 * SS), eye_y - int(14 * SS),
                             int(24 * SS), int(28 * SS)))
        pygame.draw.ellipse(big, (18, 14, 10),
                            (cx + sx - int(12 * SS), eye_y - int(14 * SS),
                             int(24 * SS), int(28 * SS)), max(2, SS))
        # Iris (large coloured)
        pygame.draw.ellipse(big, P["SAPPHIRE"],
                            (cx + sx - int(8 * SS), eye_y - int(10 * SS),
                             int(16 * SS), int(22 * SS)))
        pygame.draw.ellipse(big, (35, 80, 160),
                            (cx + sx - int(8 * SS), eye_y - int(8 * SS),
                             int(16 * SS), int(14 * SS)))
        # Pupil
        pygame.draw.ellipse(big, (18, 14, 10),
                            (cx + sx - int(3 * SS), eye_y - int(4 * SS),
                             int(6 * SS), int(14 * SS)))
        # Two big glints
        pygame.draw.circle(big, (255, 255, 255),
                           (cx + sx - int(4 * SS), eye_y - int(6 * SS)),
                           int(3 * SS))
        pygame.draw.circle(big, (255, 255, 255),
                           (cx + sx + int(3 * SS), eye_y + int(4 * SS)),
                           int(2 * SS))
    # Small expressive mouth (slight smirk)
    pygame.draw.arc(big, (18, 14, 10),
                    (cx - int(6 * SS), head_cy + int(28 * SS),
                     int(14 * SS), int(10 * SS)),
                    math.radians(10), math.radians(170), max(3, SS + 1))
    # Headband
    pygame.draw.rect(big, P["GOLD"],
                     (cx - int(34 * SS), head_cy - int(20 * SS),
                      int(68 * SS), int(6 * SS)))
    pygame.draw.line(big, P["GOLD_HI"],
                     (cx - int(32 * SS), head_cy - int(18 * SS)),
                     (cx + int(32 * SS), head_cy - int(18 * SS)),
                     max(2, SS - 1))
    _gem_diamond(big, cx, head_cy - int(17 * SS), int(4 * SS), P["RUBY"])


# ─────────────────────────────────────────────────────────────────────────────
# Sheet layout (2 rows × 5 columns)
# ─────────────────────────────────────────────────────────────────────────────

DESIGNS = [
    ("A1 — Classic Aladdin",   draw_a1),
    ("A2 — Aladdin Reborn",    draw_a2),
    ("F1 — Classic Champion",  draw_f1),
    ("F2 — Heroic Champion",   draw_f2),
    ("H1 — Cosmic Aladdin",    draw_h1),
    ("H2 — Storm Aladdin",     draw_h2),
    ("H3 — Vizier Aladdin",    draw_h3),
    ("H4 — Mystic Champion",   draw_h4),
    ("H5 — Pop Comic Genie",   draw_h5),
    ("H6 — Anime Genie",       draw_h6),
]


def render_one(draw_fn, t=0.0):
    big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    big.fill(SKY)
    cx = PW // 2
    draw_fn(big, cx, t)
    return pygame.transform.smoothscale(big, (W, H))


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "v5"
    cols, rows = 5, 2
    margin = 14
    label_h = 22
    sheet_w = W * cols + margin * (cols + 1)
    sheet_h = (H + margin + label_h) * rows + margin
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 22, 30))
    font = pygame.font.SysFont("Arial", 14, bold=True)
    for i, (label, draw_fn) in enumerate(DESIGNS):
        col, row = i % cols, i // cols
        portrait = render_one(draw_fn)
        x = margin + col * (W + margin)
        y = margin + row * (H + margin + label_h)
        pygame.draw.rect(sheet, (60, 65, 80),
                         (x - 2, y - 2, W + 4, H + 4), 2)
        sheet.blit(portrait, (x, y))
        text = font.render(label, True, (240, 240, 240))
        sheet.blit(text, (x + (W - text.get_width()) // 2, y + H + 4))
        # Save individual portrait
        letter = label.split(" — ")[0].lower()
        pygame.image.save(portrait, os.path.join(OUT_DIR,
                                                 f"{tag}_{letter}.png"))
    out = os.path.join(OUT_DIR, f"sheet_{tag}.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
