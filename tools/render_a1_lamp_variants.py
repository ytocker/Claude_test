"""Render 5 STRUCTURALLY DISTINCT genie-vessel candidates + the
current original for review. The five candidates are NOT the same
silhouette in different paints — each is a different physical
object that happens to also read as a magical genie-summoning
vessel. Smoke is the unifying "this is magic" cue.

Candidate shapes:
  1. Aladdin teardrop lamp — squat brass body, S-spout, ring handle.
  2. Genie bottle — tall slender glass bottle, cork popping off,
     swirling smoke + star dots VISIBLE INSIDE the glass.
  3. Persian samovar/ewer — tall belly body, domed lid w/ finial
     spike, tall swan-neck spout, C-handle.
  4. Crystal orb on tripod — perfect sphere body with nebula
     INSIDE, gold equator band, 3-leg gold tripod stand.
  5. Domed urn — wide squat cylinder, two side ring handles,
     askew domed lid with smoke leaking from the gap.

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_a1_lamp_variants [tag]
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

# Per-portrait native canvas. Taller than wide so the bottle +
# ewer + tripod variants have vertical room.
W, H, SS = 96, 112, 6
PW, PH = W * SS, H * SS
SKY = (110, 175, 220)
NEAR_BLK = (18, 14, 10)

DISPLAY_BIG   = 4
DISPLAY_SMALL = 1


def s(v):
    return int(v * SS)


def aa_circle(surf, color, cx, cy, r):
    pygame.draw.circle(surf, color, (int(cx), int(cy)), int(r))


def ell(surf, color, cx, cy, w, h):
    pygame.draw.ellipse(surf, color,
                        (int(cx - w / 2), int(cy - h / 2),
                         int(w), int(h)))


def stroked_ell(surf, color, cx, cy, w, h, stroke):
    pygame.draw.ellipse(surf, color,
                        (int(cx - w / 2), int(cy - h / 2),
                         int(w), int(h)), int(stroke))


def filled_poly(surf, color, pts):
    pygame.draw.polygon(surf, color, pts)


def gem_diamond(surf, cx, cy, r, color, hi_color):
    pygame.draw.polygon(surf, NEAR_BLK,
                        [(cx, cy - r - s(1) // 2),
                         (cx + r + s(1) // 2, cy),
                         (cx, cy + r + s(1) // 2),
                         (cx - r - s(1) // 2, cy)])
    pygame.draw.polygon(surf, color,
                        [(cx, cy - r), (cx + r, cy),
                         (cx, cy + r), (cx - r, cy)])
    pygame.draw.polygon(surf, hi_color,
                        [(cx, cy - r),
                         (cx - int(r * 0.55), cy),
                         (cx - int(r * 0.25),
                          cy - int(r * 0.35))])
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - r * 0.3), int(cy - r * 0.5)),
                       max(1, int(r * 0.22)))


def gem_round(surf, cx, cy, r, color, hi_color):
    pygame.draw.circle(surf, NEAR_BLK, (cx, cy), int(r + s(1) // 2))
    pygame.draw.circle(surf, color, (cx, cy), int(r))
    pygame.draw.circle(surf, hi_color,
                       (int(cx - r * 0.32), int(cy - r * 0.32)),
                       max(1, int(r * 0.55)))
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - r * 0.45), int(cy - r * 0.45)),
                       max(1, int(r * 0.22)))


def smoke_ribbon(surf, ox, oy, palette, n_puffs=11, height_n=40,
                 curl=2.0, taper=True):
    for i in range(n_puffs):
        k = i / max(1, n_puffs - 1)
        sway = math.sin(0.6 + i * 0.55) * s(curl) * (0.3 + k)
        x = ox + sway
        y = oy - int(s(height_n) * k)
        if taper:
            rad = max(s(1), int(s(3.5) * (1 - k * 0.6)))
        else:
            rad = max(s(1), int(s(2.5)))
        alpha = int(230 * (1 - k * 0.78))
        col = palette[min(int(k * len(palette)), len(palette) - 1)]
        puff = pygame.Surface((rad * 2 + 4, rad * 2 + 4),
                              pygame.SRCALPHA)
        pygame.draw.circle(puff, (*col, alpha),
                           (rad + 2, rad + 2), rad)
        surf.blit(puff, (int(x - rad - 2), int(y - rad - 2)))


def sparkles_around(surf, cx, cy, n=5, radius_n=38,
                    color=(255, 240, 180), rng_seed=11,
                    ang_lo=-math.pi, ang_hi=0.3):
    rng = random.Random(rng_seed)
    R = s(radius_n)
    for _ in range(n):
        ang = rng.uniform(ang_lo, ang_hi)
        r = rng.uniform(R * 0.7, R)
        sx = cx + math.cos(ang) * r
        sy = cy + math.sin(ang) * r * 0.85 - s(4)
        sr = max(1, rng.randint(s(1) // 2, s(1)))
        cw = max(1, s(1) // 2)
        pygame.draw.line(surf, color,
                         (int(sx - sr * 2), int(sy)),
                         (int(sx + sr * 2), int(sy)), cw)
        pygame.draw.line(surf, color,
                         (int(sx), int(sy - sr * 2)),
                         (int(sx), int(sy + sr * 2)), cw)
        aa_circle(surf, (255, 255, 255), sx, sy, max(1, sr))


# ─────────────────────────────────────────────────────────────────────
# SHAPE 1 — Aladdin teardrop lamp (the canonical squat brass).
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_1_aladdin(big, cx, cy):
    DK    = (110,  60,  10)
    BASE  = (210, 140,  35)
    HI    = (255, 220, 120)
    GLINT = (255, 255, 230)
    GOLD  = (255, 230, 140)
    RUBY  = (220,  55,  75)
    RUBY_HI = (255, 175, 195)
    SMOKE = [(230, 205, 250), (185, 140, 220), (135, 85, 170)]

    # Body — wide squat ellipse (3:1 aspect)
    body_cy = cy + s(8)
    bw = s(52)
    bh = s(22)
    # Drop-shadow body for outline
    ell(big, NEAR_BLK, cx, body_cy + s(1), bw + s(1), bh + s(1))
    ell(big, DK, cx, body_cy, bw, bh)
    ell(big, BASE, cx - s(1), body_cy - s(1), bw - s(5), bh - s(4))
    # Highlight crescent
    pygame.draw.arc(big, HI,
                    (cx - bw // 2 + s(4), body_cy - bh // 2 + s(3),
                     bw - s(8), bh - s(8)),
                    math.radians(195), math.radians(325),
                    max(3, s(1) + 1))
    aa_circle(big, GLINT, cx - s(10), body_cy - s(6), max(1, s(1)))

    # Gold rim along the dome top
    pygame.draw.arc(big, GOLD,
                    (cx - bw // 2 + s(4), body_cy - bh // 2 - s(1),
                     bw - s(8), bh - s(8)),
                    math.radians(195), math.radians(345),
                    max(3, s(1) + 1))

    # Foot stem + flared base
    stem_w, stem_h = s(20), s(3)
    base_w, base_h = s(32), s(5)
    stem_y = body_cy + bh // 2 - s(2)
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - stem_w // 2 - s(1) // 2,
                      stem_y, stem_w + s(1), stem_h + s(1)),
                     border_radius=s(1))
    pygame.draw.rect(big, DK,
                     (cx - stem_w // 2, stem_y, stem_w, stem_h),
                     border_radius=s(1))
    pygame.draw.rect(big, BASE,
                     (cx - stem_w // 2 + s(1) // 2, stem_y,
                      stem_w - s(1), max(1, stem_h - s(1))),
                     border_radius=s(1))
    base_y = stem_y + stem_h
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - base_w // 2 - s(1) // 2,
                      base_y, base_w + s(1), base_h + s(1)),
                     border_radius=s(1))
    pygame.draw.rect(big, DK,
                     (cx - base_w // 2, base_y, base_w, base_h),
                     border_radius=s(1))
    pygame.draw.rect(big, BASE,
                     (cx - base_w // 2 + s(1) // 2, base_y,
                      base_w - s(1), max(1, base_h - s(1))),
                     border_radius=s(1))
    pygame.draw.line(big, HI,
                     (cx - base_w // 2 + s(3), base_y + s(1)),
                     (cx + base_w // 2 - s(3), base_y + s(1)),
                     max(1, s(1) // 2))

    # Spout — swan-neck S-curve, base buried inside body shoulder
    spa_x = cx + bw // 2 - s(8)
    spa_y = body_cy - s(1)
    outer = [
        (spa_x - s(3),  spa_y + s(6)),
        (spa_x + s(5),  spa_y + s(3)),
        (spa_x + s(12), spa_y - s(3)),
        (spa_x + s(18), spa_y - s(11)),
        (spa_x + s(21), spa_y - s(19)),
        (spa_x + s(20), spa_y - s(25)),
        (spa_x + s(17), spa_y - s(30)),
    ]
    inner = [
        (spa_x + s(11), spa_y - s(30)),
        (spa_x + s(13), spa_y - s(25)),
        (spa_x + s(15), spa_y - s(19)),
        (spa_x + s(13), spa_y - s(11)),
        (spa_x + s(8),  spa_y - s(3)),
        (spa_x + s(2),  spa_y + s(2)),
        (spa_x - s(3),  spa_y + s(4)),
    ]
    spout_pts = outer + inner
    sh = [(x + s(1), y + s(1)) for x, y in spout_pts]
    filled_poly(big, NEAR_BLK, sh)
    filled_poly(big, DK, spout_pts)
    # Inner fill (offset toward inner edge)
    in_fill = [(x - s(1), y + s(1)) for x, y in outer] + \
              [(x + s(2), y) for x, y in inner]
    filled_poly(big, BASE, in_fill)
    pygame.draw.lines(big, HI, False,
                      [(spa_x + s(8),  spa_y - s(3)),
                       (spa_x + s(14), spa_y - s(11)),
                       (spa_x + s(18), spa_y - s(20))],
                      max(2, s(1)))
    # Mouth (rim crescent + opening)
    mouth_x = spa_x + s(14)
    mouth_y = spa_y - s(30)
    pygame.draw.lines(big, NEAR_BLK, False,
                      [(spa_x + s(11), spa_y - s(29)),
                       (mouth_x, spa_y - s(28)),
                       (spa_x + s(17), spa_y - s(29))],
                      max(2, s(1)))
    ell(big, NEAR_BLK, mouth_x, mouth_y, s(6), s(2))

    # Handle — torus ring on left
    h_cx = cx - bw // 2 - s(4)
    h_cy = body_cy - s(2)
    h_w, h_h = s(13), s(22)
    HOLE_COLOR = (60, 95, 130)
    pygame.draw.ellipse(big, NEAR_BLK,
                        (h_cx - h_w // 2 - s(1),
                         h_cy - h_h // 2 - s(1),
                         h_w + s(2), h_h + s(2)))
    pygame.draw.ellipse(big, DK,
                        (h_cx - h_w // 2, h_cy - h_h // 2, h_w, h_h))
    pygame.draw.ellipse(big, BASE,
                        (h_cx - h_w // 2 + s(1) // 2,
                         h_cy - h_h // 2 + s(1) // 2,
                         h_w - s(1), h_h - s(1)))
    pygame.draw.ellipse(big, HOLE_COLOR,
                        (h_cx - h_w // 2 + s(3),
                         h_cy - h_h // 2 + s(4),
                         h_w - s(6), h_h - s(8)))
    pygame.draw.arc(big, NEAR_BLK,
                    (h_cx - h_w // 2 + s(3),
                     h_cy - h_h // 2 + s(4),
                     h_w - s(6), h_h - s(8)),
                    math.radians(260), math.radians(80),
                    max(3, s(1) + 1))

    # Ruby gem on body
    gem_diamond(big, cx + s(4), body_cy + s(1), s(4), RUBY, RUBY_HI)

    # Smoke + sparkles
    smoke_ribbon(big, mouth_x, mouth_y, SMOKE,
                 n_puffs=11, height_n=42, curl=1.8)
    sparkles_around(big, cx, cy - s(4), n=5, radius_n=42,
                    color=(255, 235, 170))


# ─────────────────────────────────────────────────────────────────────
# SHAPE 2 — Genie bottle. Tall slender translucent glass with a cork
# popping off, smoke + stars VISIBLE INSIDE the glass.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_2_bottle(big, cx, cy):
    GLASS_DK = ( 35,  20,  85)
    GLASS    = ( 90,  55, 170)
    GLASS_HI = (170, 130, 220)
    HIGHLIGHT = (235, 215, 255)
    GOLD     = (255, 220, 110)
    GOLD_HI  = (255, 245, 175)
    CORK     = (155,  95,  45)
    CORK_HI  = (215, 160,  95)
    STAR_W   = (255, 255, 250)
    SMOKE    = [(245, 220, 255), (190, 160, 230), (140, 100, 200)]

    # Bottle body — tall rounded vase silhouette built as a polygon
    # (curved sides via parametric oval). Body sits from y_top to
    # y_bottom; neck narrows above to y_neck_top.
    y_neck_top    = cy - s(38)
    y_neck_bottom = cy - s(28)
    y_shoulder    = cy - s(22)
    y_body_bottom = cy + s(32)
    y_foot        = cy + s(38)
    neck_half = s(5)
    body_max_half = s(16)
    foot_half = s(13)

    # Bottle silhouette (clockwise: top-left → top-right → ...)
    left_pts = []
    right_pts = []
    # Neck wall (straight)
    for k in range(4):
        t = k / 3.0
        y = y_neck_top + t * (y_neck_bottom - y_neck_top)
        left_pts.append((cx - neck_half, y))
        right_pts.append((cx + neck_half, y))
    # Shoulder (curves outward)
    for k in range(1, 6):
        t = k / 5.0
        y = y_neck_bottom + t * (y_shoulder - y_neck_bottom)
        half = neck_half + t * (body_max_half - neck_half) * 1.05
        # smooth shoulder curve
        if t > 0.7:
            half *= 1.0
        left_pts.append((cx - half, y))
        right_pts.append((cx + half, y))
    # Body bulge — slight arc from shoulder to bottom
    for k in range(1, 14):
        t = k / 13.0
        y = y_shoulder + t * (y_body_bottom - y_shoulder)
        # belly bulges, then narrows to foot
        bulge = math.sin(t * math.pi) * s(2)
        half = body_max_half + bulge - t * (body_max_half - foot_half) * 0.3
        left_pts.append((cx - half, y))
        right_pts.append((cx + half, y))
    # Foot — rounded bottom corner
    for k in range(1, 4):
        t = k / 3.0
        y = y_body_bottom + t * (y_foot - y_body_bottom)
        half = (foot_half +
                (body_max_half - (body_max_half - foot_half) * 0.3 - foot_half) *
                (1 - t))
        left_pts.append((cx - half * (1 - t * 0.05), y))
        right_pts.append((cx + half * (1 - t * 0.05), y))
    silhouette = left_pts + list(reversed(right_pts))

    # Drop-shadow outline
    shadow_pts = [(x + s(1), y + s(1)) for x, y in silhouette]
    filled_poly(big, NEAR_BLK, shadow_pts)
    # Outer glass colour
    filled_poly(big, GLASS_DK, silhouette)
    # Inner glass (slightly inset on both sides)
    inset = []
    for x, y in left_pts:
        inset.append((x + s(2), y))
    for x, y in reversed(right_pts):
        inset.append((x - s(2), y))
    filled_poly(big, GLASS, inset)

    # Build a body-clip mask so internal smoke + stars stay
    # inside the silhouette
    clip = pygame.Surface((PW, PH), pygame.SRCALPHA)
    rng = random.Random(7)
    # Internal swirling smoke — drawn as low-alpha lavender puffs
    for k in range(11):
        # Spiral path from bottom to neck
        t = k / 10.0
        spiral_ang = t * math.tau * 1.4
        radius = s(8) * (1 - t * 0.7)
        sx = cx + math.cos(spiral_ang) * radius
        sy_p = y_body_bottom - t * (y_body_bottom - y_neck_bottom + s(2))
        r = s(3) + int(rng.uniform(-1, 2))
        col = SMOKE[k % len(SMOKE)]
        sub = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(sub, (*col, 150),
                           (r + 2, r + 2), r)
        clip.blit(sub, (sx - r - 2, sy_p - r - 2))
    # Star dots inside the glass
    for _ in range(9):
        sx_p = cx + rng.randint(-body_max_half + s(3),
                                 body_max_half - s(3))
        sy_p = rng.randint(y_shoulder + s(2), y_body_bottom - s(2))
        r = max(1, s(1) // 2 + rng.randint(0, 1))
        pygame.draw.circle(clip, (*STAR_W, 240), (sx_p, sy_p), r)
        # Star cross
        pygame.draw.line(clip, (*STAR_W, 200),
                         (sx_p - r * 2, sy_p),
                         (sx_p + r * 2, sy_p), max(1, s(1) // 3))
        pygame.draw.line(clip, (*STAR_W, 200),
                         (sx_p, sy_p - r * 2),
                         (sx_p, sy_p + r * 2), max(1, s(1) // 3))
    # Apply mask
    mask = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(int(x), int(y)) for x, y in silhouette])
    clip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(clip, (0, 0))

    # Glass highlight stripe — vertical streak on the left curve
    pygame.draw.lines(big, HIGHLIGHT, False,
                      [(cx - body_max_half + s(2), y_shoulder + s(3)),
                       (cx - body_max_half + s(3), cy),
                       (cx - body_max_half + s(2), y_body_bottom - s(4))],
                      max(2, s(1)))

    # Gold band around the neck (collar)
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - neck_half - s(2),
                      y_neck_bottom - s(2),
                      neck_half * 2 + s(4), s(5)))
    pygame.draw.rect(big, GOLD,
                     (cx - neck_half - s(1),
                      y_neck_bottom - s(2),
                      neck_half * 2 + s(2), s(4)))
    pygame.draw.line(big, GOLD_HI,
                     (cx - neck_half, y_neck_bottom - s(1)),
                     (cx + neck_half, y_neck_bottom - s(1)),
                     max(1, s(1) // 2))

    # Foot ring
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - foot_half - s(1),
                      y_foot - s(1),
                      foot_half * 2 + s(2), s(4)))
    pygame.draw.rect(big, GOLD,
                     (cx - foot_half, y_foot, foot_half * 2, s(3)))
    pygame.draw.line(big, GOLD_HI,
                     (cx - foot_half + s(1), y_foot + s(1)),
                     (cx + foot_half - s(1), y_foot + s(1)),
                     max(1, s(1) // 2))

    # Cork — tilted, lifting off the neck mouth, with spark trail
    cork_cx = cx + s(4)
    cork_cy = y_neck_top - s(5)
    cork_w = s(7)
    cork_h = s(8)
    cork_angle_deg = -18
    cork_pts = []
    for vx, vy in ((-cork_w // 2, -cork_h // 2),
                    (cork_w // 2, -cork_h // 2),
                    (cork_w // 2, cork_h // 2),
                    (-cork_w // 2, cork_h // 2)):
        rad = math.radians(cork_angle_deg)
        rx = vx * math.cos(rad) - vy * math.sin(rad)
        ry = vx * math.sin(rad) + vy * math.cos(rad)
        cork_pts.append((cork_cx + rx, cork_cy + ry))
    # shadow
    filled_poly(big, NEAR_BLK,
                [(x + s(1), y + s(1)) for x, y in cork_pts])
    filled_poly(big, CORK, cork_pts)
    # cork highlight
    hi_pts = []
    for vx, vy in ((-cork_w // 2 + s(1), -cork_h // 2 + s(1)),
                    (cork_w // 2 - s(1), -cork_h // 2 + s(1)),
                    (cork_w // 2 - s(1), -cork_h // 4),
                    (-cork_w // 2 + s(1), -cork_h // 4)):
        rad = math.radians(cork_angle_deg)
        rx = vx * math.cos(rad) - vy * math.sin(rad)
        ry = vx * math.sin(rad) + vy * math.cos(rad)
        hi_pts.append((cork_cx + rx, cork_cy + ry))
    filled_poly(big, CORK_HI, hi_pts)

    # Smoke pouring out of the open neck (white burst from the
    # gap where the cork was)
    smoke_ribbon(big, cx, y_neck_top - s(1), SMOKE,
                 n_puffs=10, height_n=32, curl=1.5, taper=True)

    # Sparkles around the cork (the "pop" effect)
    sparkles_around(big, cork_cx, cork_cy, n=6, radius_n=18,
                    color=(255, 245, 200),
                    ang_lo=-math.pi, ang_hi=math.pi,
                    rng_seed=21)


# ─────────────────────────────────────────────────────────────────────
# SHAPE 3 — Persian samovar/ewer. Tall belly body with domed lid +
# finial spike + tall swan-neck spout + C-handle.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_3_samovar(big, cx, cy):
    DK    = ( 70,  45,  20)
    BASE  = (175, 135,  65)
    HI    = (235, 215, 150)
    GLINT = (255, 250, 220)
    GOLD  = (255, 220, 110)
    GOLD_HI = (255, 245, 175)
    SAPP  = ( 70, 100, 220)
    SAPP_HI = (175, 200, 255)
    SMOKE = [(215, 215, 240), (170, 165, 215), (110, 100, 160)]

    # Body — tall belly: top narrow neck, wide belly, narrow base.
    # Dimensions tuned for samovar look: taller than wide.
    y_neck   = cy - s(16)
    y_belly  = cy - s(2)
    y_bottom = cy + s(22)
    neck_half  = s(8)
    belly_half = s(14)
    bottom_half = s(9)

    # Body polygon (clockwise from upper-left)
    body_pts = []
    # left side, top→bottom
    n = 10
    for k in range(n + 1):
        t = k / n
        # interpolate y
        if t < 0.4:
            tt = t / 0.4
            y = y_neck + tt * (y_belly - y_neck)
            half = neck_half + tt * (belly_half - neck_half)
        else:
            tt = (t - 0.4) / 0.6
            y = y_belly + tt * (y_bottom - y_belly)
            half = belly_half - tt * (belly_half - bottom_half)
        body_pts.append((cx - half, y))
    # right side, bottom→top
    for k in range(n + 1):
        t = (n - k) / n
        if t < 0.4:
            tt = t / 0.4
            y = y_neck + tt * (y_belly - y_neck)
            half = neck_half + tt * (belly_half - neck_half)
        else:
            tt = (t - 0.4) / 0.6
            y = y_belly + tt * (y_bottom - y_belly)
            half = belly_half - tt * (belly_half - bottom_half)
        body_pts.append((cx + half, y))

    # Drop shadow + body fill
    filled_poly(big, NEAR_BLK,
                [(x + s(1), y + s(1)) for x, y in body_pts])
    filled_poly(big, DK, body_pts)
    inset = []
    for x, y in body_pts:
        dx = (x - cx) * 0.86
        inset.append((cx + dx, y))
    filled_poly(big, BASE, inset)

    # Highlight crescent on belly (left side)
    pygame.draw.lines(big, HI, False,
                      [(cx - belly_half + s(3), y_belly - s(3)),
                       (cx - belly_half + s(2), y_belly + s(2)),
                       (cx - belly_half + s(4), y_belly + s(7))],
                      max(3, s(1) + 1))
    aa_circle(big, GLINT, cx - belly_half + s(4),
              y_belly - s(1), max(1, s(1)))

    # Engraved gold bands across body (3 bands)
    for band_y in (y_belly - s(6), y_belly, y_belly + s(8)):
        # find local body width at this y
        t_band = (band_y - y_neck) / (y_bottom - y_neck)
        if t_band < 0.4:
            half_band = neck_half + (t_band / 0.4) * (belly_half - neck_half)
        else:
            tt = (t_band - 0.4) / 0.6
            half_band = belly_half - tt * (belly_half - bottom_half)
        pygame.draw.arc(big, GOLD,
                        (cx - int(half_band) + s(2),
                         band_y - s(2),
                         int(half_band) * 2 - s(4), s(4)),
                        math.radians(200), math.radians(340),
                        max(2, s(1)))
    # Sapphire in the centre band
    gem_round(big, cx, y_belly, s(3), SAPP, SAPP_HI)

    # Stem + flared base
    stem_y = y_bottom
    stem_w, stem_h = s(14), s(3)
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - stem_w // 2 - s(1) // 2, stem_y,
                      stem_w + s(1), stem_h + s(1)),
                     border_radius=s(1))
    pygame.draw.rect(big, DK,
                     (cx - stem_w // 2, stem_y, stem_w, stem_h),
                     border_radius=s(1))
    base_w, base_h = s(26), s(5)
    base_y = stem_y + stem_h
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - base_w // 2 - s(1) // 2, base_y,
                      base_w + s(1), base_h + s(1)),
                     border_radius=s(1))
    pygame.draw.rect(big, DK,
                     (cx - base_w // 2, base_y, base_w, base_h),
                     border_radius=s(1))
    pygame.draw.rect(big, BASE,
                     (cx - base_w // 2 + s(1) // 2, base_y,
                      base_w - s(1), max(1, base_h - s(1))),
                     border_radius=s(1))
    pygame.draw.line(big, HI,
                     (cx - base_w // 2 + s(3), base_y + s(1)),
                     (cx + base_w // 2 - s(3), base_y + s(1)),
                     max(1, s(1) // 2))

    # Neck collar (gold band)
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - neck_half - s(2), y_neck - s(3),
                      neck_half * 2 + s(4), s(5)))
    pygame.draw.rect(big, GOLD,
                     (cx - neck_half - s(1), y_neck - s(3),
                      neck_half * 2 + s(2), s(4)))

    # Domed lid
    lid_h = s(8)
    lid_w = neck_half * 2 + s(2)
    lid_top_y = y_neck - s(3) - lid_h
    pygame.draw.ellipse(big, NEAR_BLK,
                        (cx - lid_w // 2 - s(1) // 2,
                         lid_top_y - s(1) // 2,
                         lid_w + s(1), lid_h + s(1)))
    pygame.draw.ellipse(big, DK,
                        (cx - lid_w // 2, lid_top_y,
                         lid_w, lid_h))
    pygame.draw.ellipse(big, BASE,
                        (cx - lid_w // 2 + s(1) // 2,
                         lid_top_y + s(1) // 2,
                         lid_w - s(1), lid_h - s(1)))
    pygame.draw.arc(big, HI,
                    (cx - lid_w // 2 + s(2),
                     lid_top_y + s(1),
                     lid_w - s(4), lid_h - s(2)),
                    math.radians(195), math.radians(345),
                    max(2, s(1)))
    # Lid gold rim
    pygame.draw.line(big, GOLD,
                     (cx - lid_w // 2 + s(1), lid_top_y + lid_h - s(1)),
                     (cx + lid_w // 2 - s(1), lid_top_y + lid_h - s(1)),
                     max(2, s(1)))

    # Finial spike + small ball on top of lid
    fin_tip_y = lid_top_y - s(6)
    fin_base_y = lid_top_y + s(1)
    pygame.draw.polygon(big, NEAR_BLK,
                        [(cx - s(2), fin_base_y),
                         (cx + s(2) + s(1) // 2, fin_base_y),
                         (cx + s(1) // 2, fin_tip_y)])
    pygame.draw.polygon(big, GOLD,
                        [(cx - s(2), fin_base_y),
                         (cx + s(2), fin_base_y),
                         (cx, fin_tip_y)])
    pygame.draw.line(big, GOLD_HI,
                     (cx - s(1), fin_base_y - s(1)),
                     (cx, fin_tip_y + s(1)),
                     max(1, s(1) // 2))
    aa_circle(big, GOLD, cx, fin_base_y, s(2))
    aa_circle(big, GOLD_HI, cx - s(1), fin_base_y - s(1),
              max(1, s(1) // 2))

    # Tall swan-neck spout on the RIGHT, attached to belly
    sp_x = cx + belly_half - s(2)
    sp_y = y_belly - s(3)
    outer = [
        (sp_x - s(3),  sp_y + s(8)),
        (sp_x + s(5),  sp_y + s(2)),
        (sp_x + s(13), sp_y - s(6)),
        (sp_x + s(20), sp_y - s(16)),
        (sp_x + s(23), sp_y - s(24)),
        (sp_x + s(22), sp_y - s(30)),
        (sp_x + s(19), sp_y - s(34)),
    ]
    inner = [
        (sp_x + s(13), sp_y - s(34)),
        (sp_x + s(15), sp_y - s(28)),
        (sp_x + s(17), sp_y - s(22)),
        (sp_x + s(14), sp_y - s(14)),
        (sp_x + s(8),  sp_y - s(6)),
        (sp_x + s(2),  sp_y + s(2)),
        (sp_x - s(3),  sp_y + s(5)),
    ]
    spout = outer + inner
    filled_poly(big, NEAR_BLK, [(x + s(1), y + s(1)) for x, y in spout])
    filled_poly(big, DK, spout)
    # inner fill
    in_fill = [(x - s(1), y + s(1)) for x, y in outer] + \
              [(x + s(2), y) for x, y in inner]
    filled_poly(big, BASE, in_fill)
    pygame.draw.lines(big, HI, False,
                      [(sp_x + s(9),  sp_y - s(4)),
                       (sp_x + s(16), sp_y - s(14)),
                       (sp_x + s(20), sp_y - s(24))],
                      max(2, s(1)))
    mouth_x = sp_x + s(16)
    mouth_y = sp_y - s(34)
    pygame.draw.lines(big, NEAR_BLK, False,
                      [(sp_x + s(13), sp_y - s(33)),
                       (mouth_x, sp_y - s(32)),
                       (sp_x + s(19), sp_y - s(33))],
                      max(2, s(1)))
    ell(big, NEAR_BLK, mouth_x, mouth_y, s(6), s(2))

    # C-handle on the LEFT — proper full C with visible thickness,
    # attached at upper-belly and lower-belly via short stubs.
    h_top_y    = y_belly - s(6)
    h_bot_y    = y_belly + s(8)
    h_attach_x = cx - belly_half + s(2)
    h_outer_x  = h_attach_x - s(13)
    # Outer arc rectangle (the C's outside curve)
    arc_rect = (h_outer_x, h_top_y,
                h_attach_x - h_outer_x, h_bot_y - h_top_y)
    # outer outline (thick)
    pygame.draw.arc(big, NEAR_BLK,
                    (arc_rect[0] - s(1), arc_rect[1] - s(1),
                     arc_rect[2] + s(2), arc_rect[3] + s(2)),
                    math.radians(60), math.radians(300),
                    max(8, s(2) + s(1)))
    # mid tone
    pygame.draw.arc(big, DK, arc_rect,
                    math.radians(60), math.radians(300),
                    max(7, s(2)))
    # base colour
    pygame.draw.arc(big, BASE,
                    (arc_rect[0] + s(1), arc_rect[1] + s(1),
                     arc_rect[2] - s(2), arc_rect[3] - s(2)),
                    math.radians(70), math.radians(290),
                    max(4, s(1) + 1))
    # highlight on the back-left of the handle
    pygame.draw.arc(big, HI,
                    (arc_rect[0] + s(2), arc_rect[1] + s(2),
                     arc_rect[2] - s(4), arc_rect[3] - s(4)),
                    math.radians(140), math.radians(220),
                    max(2, s(1)))
    # Short stubs where the handle joins the body
    pygame.draw.rect(big, DK,
                     (h_attach_x - s(2), h_top_y - s(1),
                      s(5), s(3)))
    pygame.draw.rect(big, DK,
                     (h_attach_x - s(2), h_bot_y - s(2),
                      s(5), s(3)))

    # Smoke + sparkles
    smoke_ribbon(big, mouth_x, mouth_y, SMOKE,
                 n_puffs=11, height_n=36, curl=1.6)
    sparkles_around(big, cx, cy - s(8), n=4, radius_n=42,
                    color=GOLD_HI, rng_seed=31)


# ─────────────────────────────────────────────────────────────────────
# SHAPE 4 — Crystal orb on a gold tripod. Sphere body with nebula
# INSIDE, gold equator, 3-leg gold stand, brass cap with smoke.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_4_orb(big, cx, cy):
    NIGHT = ( 16,  14,  46)
    DEEP  = ( 28,  22,  78)
    NEBULA = [(130,  60, 200), (210,  90, 180), ( 70, 130, 230)]
    GOLD  = (255, 220, 110)
    GOLD_HI = (255, 245, 175)
    GOLD_DK = (165, 120,  40)
    CYAN  = (175, 230, 255)
    WHITE = (250, 250, 250)
    SMOKE = [WHITE, CYAN, (130, 110, 210), ( 80,  60, 180)]

    # Orb — perfect sphere
    orb_r = s(22)
    orb_cy = cy + s(4)
    # Outer glow halo (subtle)
    for r_n, a in ((s(30), 30), (s(26), 60)):
        ho = pygame.Surface((r_n * 2 + 4, r_n * 2 + 4),
                            pygame.SRCALPHA)
        pygame.draw.circle(ho, (*CYAN, a),
                           (r_n + 2, r_n + 2), r_n)
        big.blit(ho, (cx - r_n - 2, orb_cy - r_n - 2))
    # Black ring (outline)
    aa_circle(big, NEAR_BLK, cx, orb_cy, orb_r + s(1) // 2)
    # Sphere body (deep navy)
    aa_circle(big, NIGHT, cx, orb_cy, orb_r)
    # Inner gradient (slightly brighter centre band)
    ell(big, DEEP, cx, orb_cy, orb_r * 2 - s(2), int(orb_r * 1.7))

    # Internal nebula + stars — clip to circular mask
    clip = pygame.Surface((PW, PH), pygame.SRCALPHA)
    rng = random.Random(11)
    for _ in range(9):
        nx = cx + rng.randint(-orb_r + s(3), orb_r - s(3))
        ny = orb_cy + rng.randint(-orb_r + s(3), orb_r - s(3))
        nr = rng.randint(s(3), s(6))
        col = rng.choice(NEBULA)
        sub = pygame.Surface((nr * 2 + 4, nr * 2 + 4),
                             pygame.SRCALPHA)
        pygame.draw.circle(sub, (*col, 130),
                           (nr + 2, nr + 2), nr)
        clip.blit(sub, (nx - nr - 2, ny - nr - 2))
    # Stars
    for k in range(13):
        sx_p = cx + rng.randint(-orb_r + s(3), orb_r - s(3))
        sy_p = orb_cy + rng.randint(-orb_r + s(3), orb_r - s(3))
        if k < 4:
            pygame.draw.line(clip, (*WHITE, 220),
                             (sx_p - s(1), sy_p),
                             (sx_p + s(1), sy_p),
                             max(1, s(1) // 2))
            pygame.draw.line(clip, (*WHITE, 220),
                             (sx_p, sy_p - s(1)),
                             (sx_p, sy_p + s(1)),
                             max(1, s(1) // 2))
        pygame.draw.circle(clip, (*WHITE, 230),
                           (sx_p, sy_p), max(1, s(1) // 2))
    # Mask
    mask = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255),
                       (cx, orb_cy), orb_r - s(1))
    clip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(clip, (0, 0))

    # Glossy orb highlight (crescent on upper-left)
    pygame.draw.arc(big, (255, 255, 255, 80) and (220, 230, 255),
                    (cx - orb_r + s(2), orb_cy - orb_r + s(2),
                     orb_r * 2 - s(4), orb_r * 2 - s(4)),
                    math.radians(200), math.radians(290),
                    max(2, s(1)))
    aa_circle(big, (255, 255, 255), cx - s(8), orb_cy - s(9),
              max(2, s(1) + s(1) // 2))

    # Gold equator band wrapping the sphere
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - orb_r, orb_cy + s(1) - s(2) // 2,
                      orb_r * 2, s(4)))
    pygame.draw.rect(big, GOLD,
                     (cx - orb_r, orb_cy + s(1) - s(2) // 2,
                      orb_r * 2, s(3)))
    pygame.draw.line(big, GOLD_HI,
                     (cx - orb_r + s(2), orb_cy + s(1)),
                     (cx + orb_r - s(2), orb_cy + s(1)),
                     max(1, s(1) // 2))
    # Equator decorative bolts (3 dots on each side)
    for k in range(-3, 4):
        if k == 0: continue
        aa_circle(big, GOLD_DK, cx + k * s(5),
                  orb_cy + s(2), max(1, s(1) // 2))

    # Brass cap on top of orb — small dome with a tiny mouth opening
    cap_cy = orb_cy - orb_r + s(1)
    cap_w = s(14)
    cap_h = s(6)
    pygame.draw.ellipse(big, NEAR_BLK,
                        (cx - cap_w // 2 - s(1) // 2,
                         cap_cy - cap_h // 2 - s(1) // 2,
                         cap_w + s(1), cap_h + s(1)))
    pygame.draw.ellipse(big, GOLD_DK,
                        (cx - cap_w // 2, cap_cy - cap_h // 2,
                         cap_w, cap_h))
    pygame.draw.ellipse(big, GOLD,
                        (cx - cap_w // 2 + s(1) // 2,
                         cap_cy - cap_h // 2 + s(1) // 2,
                         cap_w - s(1), cap_h - s(1)))
    pygame.draw.arc(big, GOLD_HI,
                    (cx - cap_w // 2 + s(1),
                     cap_cy - cap_h // 2 + s(1),
                     cap_w - s(2), cap_h - s(2)),
                    math.radians(200), math.radians(340),
                    max(1, s(1) // 2))
    # Smoke mouth (tiny dark oval)
    mouth_x = cx
    mouth_y = cap_cy - s(2)
    ell(big, NEAR_BLK, mouth_x, mouth_y, s(4), s(2))

    # Tripod — 3 splayed legs (centre leg behind, two front splayed)
    leg_top = (cx, orb_cy + orb_r - s(2))
    leg_feet = [(cx - s(18), orb_cy + orb_r + s(20)),
                (cx,         orb_cy + orb_r + s(22)),
                (cx + s(18), orb_cy + orb_r + s(20))]
    # Centre back leg first (lower z)
    for foot in (leg_feet[1],):
        pygame.draw.line(big, NEAR_BLK,
                         (leg_top[0] + s(1) // 3,
                          leg_top[1] + s(1) // 3),
                         (foot[0] + s(1) // 3,
                          foot[1] + s(1) // 3),
                         max(4, s(1) + 2))
        pygame.draw.line(big, GOLD_DK, leg_top, foot,
                         max(3, s(1) + 1))
        pygame.draw.line(big, GOLD,
                         (leg_top[0] - s(1) // 2, leg_top[1]),
                         (foot[0] - s(1) // 2, foot[1]),
                         max(1, s(1) // 2))
        # ball foot
        aa_circle(big, NEAR_BLK, foot[0] + s(1) // 2,
                  foot[1] + s(1) // 2, s(3))
        aa_circle(big, GOLD, foot[0], foot[1], s(3))
        aa_circle(big, GOLD_HI, foot[0] - s(1),
                  foot[1] - s(1), max(1, s(1)))
    # Front two legs (higher z, drawn after orb-bottom shadow)
    for foot in (leg_feet[0], leg_feet[2]):
        pygame.draw.line(big, NEAR_BLK,
                         (leg_top[0] + s(1) // 3,
                          leg_top[1] + s(1) // 3),
                         (foot[0] + s(1) // 3,
                          foot[1] + s(1) // 3),
                         max(4, s(1) + 2))
        pygame.draw.line(big, GOLD_DK, leg_top, foot,
                         max(3, s(1) + 1))
        pygame.draw.line(big, GOLD,
                         (leg_top[0] - s(1) // 2, leg_top[1]),
                         (foot[0] - s(1) // 2, foot[1]),
                         max(1, s(1) // 2))
        # ball foot
        aa_circle(big, NEAR_BLK, foot[0] + s(1) // 2,
                  foot[1] + s(1) // 2, s(3))
        aa_circle(big, GOLD, foot[0], foot[1], s(3))
        aa_circle(big, GOLD_HI, foot[0] - s(1),
                  foot[1] - s(1), max(1, s(1)))
    # Tripod top collar (where legs meet)
    aa_circle(big, NEAR_BLK, leg_top[0],
              leg_top[1] + s(1) // 2, s(4))
    aa_circle(big, GOLD, leg_top[0], leg_top[1], s(3))

    # Smoke + sparkles
    smoke_ribbon(big, mouth_x, mouth_y, SMOKE,
                 n_puffs=13, height_n=44, curl=2.4)
    sparkles_around(big, cx, orb_cy, n=7, radius_n=38,
                    color=CYAN, rng_seed=11)
    sparkles_around(big, cx, orb_cy, n=4, radius_n=30,
                    color=GOLD_HI, rng_seed=17)


# ─────────────────────────────────────────────────────────────────────
# SHAPE 5 — Domed urn. Wide squat cylindrical body with two side
# ring handles, askew domed lid with smoke leaking from the gap.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_5_urn(big, cx, cy):
    DK    = ( 80,  35,  35)
    BASE  = (165,  85,  75)
    HI    = (220, 150, 130)
    GLINT = (255, 230, 215)
    GOLD  = (255, 220, 110)
    GOLD_HI = (255, 245, 175)
    GOLD_DK = (175, 130,  40)
    EMERALD = ( 70, 175, 110)
    EMERALD_HI = (180, 240, 200)
    SMOKE = [(245, 220, 255), (190, 160, 230), (140, 100, 200)]

    # Body — vase/amphora silhouette. Narrow shoulders, bulging
    # belly, narrow foot. Taller than wide so it reads as an urn,
    # not a chest.
    y_top    = cy - s(8)
    y_bottom = cy + s(28)
    body_half_top = s(18)
    body_half_eq  = s(24)
    body_half_bot = s(15)

    body_pts = []
    # Left side top→bottom
    for k in range(10):
        t = k / 9.0
        y = y_top + t * (y_bottom - y_top)
        # interpolate the side
        if t < 0.5:
            tt = t / 0.5
            half = body_half_top + tt * (body_half_eq - body_half_top)
        else:
            tt = (t - 0.5) / 0.5
            half = body_half_eq - tt * (body_half_eq - body_half_bot)
        body_pts.append((cx - half, y))
    # Right side bottom→top
    for k in range(9, -1, -1):
        t = k / 9.0
        y = y_top + t * (y_bottom - y_top)
        if t < 0.5:
            tt = t / 0.5
            half = body_half_top + tt * (body_half_eq - body_half_top)
        else:
            tt = (t - 0.5) / 0.5
            half = body_half_eq - tt * (body_half_eq - body_half_bot)
        body_pts.append((cx + half, y))

    # Drop shadow + body fill
    filled_poly(big, NEAR_BLK,
                [(x + s(1), y + s(1)) for x, y in body_pts])
    filled_poly(big, DK, body_pts)
    inset = []
    for x, y in body_pts:
        dx = (x - cx) * 0.88
        inset.append((cx + dx, y))
    filled_poly(big, BASE, inset)

    # Highlight band on upper-left
    pygame.draw.lines(big, HI, False,
                      [(cx - body_half_top + s(4), y_top + s(2)),
                       (cx - body_half_eq + s(4), cy + s(4)),
                       (cx - body_half_bot + s(5), y_bottom - s(5))],
                      max(3, s(1) + 1))
    aa_circle(big, GLINT, cx - body_half_eq + s(5),
              cy - s(2), max(1, s(1) + 1))

    # Single gold rim band where the lid sits (no lower band — the
    # body sweeps cleanly from belly to foot so it reads as a vase,
    # not a panelled chest).
    for band_y in (y_top + s(3),):
        # local body width
        t_band = (band_y - y_top) / (y_bottom - y_top)
        if t_band < 0.5:
            half_band = body_half_top + (t_band / 0.5) * (body_half_eq - body_half_top)
        else:
            tt = (t_band - 0.5) / 0.5
            half_band = body_half_eq - tt * (body_half_eq - body_half_bot)
        pygame.draw.rect(big, NEAR_BLK,
                         (cx - int(half_band) + s(1),
                          band_y - s(1),
                          int(half_band) * 2 - s(2), s(3)))
        pygame.draw.rect(big, GOLD,
                         (cx - int(half_band) + s(1),
                          band_y - s(1),
                          int(half_band) * 2 - s(2), s(2)))
        pygame.draw.line(big, GOLD_HI,
                         (cx - int(half_band) + s(3), band_y),
                         (cx + int(half_band) - s(3), band_y),
                         max(1, s(1) // 2))

    # Hieroglyph-style dot band in the middle (between the two gold trim)
    for k in range(-5, 6):
        if k == 0:
            # central emerald gem
            gem_diamond(big, cx, cy + s(3), s(3),
                        EMERALD, EMERALD_HI)
        else:
            aa_circle(big, GOLD_DK, cx + k * s(4), cy + s(3),
                      max(1, s(1) // 2 + 1))

    # Two side ring handles (one each side at body equator).
    # Big enough to read at small scale: wider than tall (so they
    # look like sturdy ring handles, not buttons).
    for sign in (-1, 1):
        h_cx = cx + sign * (body_half_eq + s(5))
        h_cy = cy + s(4)
        h_w  = s(13)
        h_h  = s(11)
        HOLE = (60, 95, 130)
        # Outer dark ring
        pygame.draw.ellipse(big, NEAR_BLK,
                            (h_cx - h_w // 2 - s(1),
                             h_cy - h_h // 2 - s(1),
                             h_w + s(2), h_h + s(2)))
        pygame.draw.ellipse(big, GOLD_DK,
                            (h_cx - h_w // 2, h_cy - h_h // 2,
                             h_w, h_h))
        # Inner gold body of the ring
        pygame.draw.ellipse(big, GOLD,
                            (h_cx - h_w // 2 + s(1) // 2,
                             h_cy - h_h // 2 + s(1) // 2,
                             h_w - s(1), h_h - s(1)))
        # Hole through the ring (so it reads as a torus, not a disc)
        pygame.draw.ellipse(big, HOLE,
                            (h_cx - h_w // 2 + s(3),
                             h_cy - h_h // 2 + s(3),
                             h_w - s(6), h_h - s(6)))
        pygame.draw.arc(big, NEAR_BLK,
                        (h_cx - h_w // 2 + s(3),
                         h_cy - h_h // 2 + s(3),
                         h_w - s(6), h_h - s(6)),
                        math.radians(260 if sign > 0 else 100),
                        math.radians(80 if sign > 0 else 260),
                        max(3, s(1) + 1))
        # Catch-light
        pygame.draw.line(big, GOLD_HI,
                         (h_cx - s(2) * sign, h_cy - h_h // 2 + s(2)),
                         (h_cx + s(2) * sign, h_cy - h_h // 2 + s(2)),
                         max(1, s(1) // 2))
        # Stub attaching to body
        pygame.draw.rect(big, DK,
                         (h_cx + sign * (h_w // 2 - s(1)) - s(2),
                          h_cy - s(2), s(4), s(4)))

    # Foot stripe (flared base supports the narrow bottom)
    foot_w = s(28)
    foot_h = s(4)
    foot_y = y_bottom - s(1)
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - foot_w // 2 - s(1) // 2,
                      foot_y, foot_w + s(1), foot_h + s(1)),
                     border_radius=s(1))
    pygame.draw.rect(big, DK,
                     (cx - foot_w // 2, foot_y, foot_w, foot_h),
                     border_radius=s(1))
    pygame.draw.rect(big, BASE,
                     (cx - foot_w // 2 + s(1) // 2, foot_y,
                      foot_w - s(1), max(1, foot_h - s(1))),
                     border_radius=s(1))

    # Domed lid — slightly askew, smoke leaking from the gap.
    # Subtler tilt so it doesn't look like a flying-saucer hovering.
    lid_angle = math.radians(-7)
    lid_cx = cx - s(2)
    lid_cy = y_top - s(2)
    lid_w = body_half_top * 2 + s(4)
    lid_h = s(10)
    # Lid as a polygon (semi-ellipse top + flat bottom) rotated
    n_lid = 14
    lid_pts = []
    for k in range(n_lid + 1):
        t = k / n_lid
        ang = math.pi + t * math.pi  # bottom→top→bottom of dome
        # ellipse local coords
        lx = math.cos(ang) * lid_w / 2
        ly = math.sin(ang) * lid_h / 2
        # If we're in the upper half, ly is negative → dome shape.
        # Rotate
        rx = lx * math.cos(lid_angle) - ly * math.sin(lid_angle)
        ry = lx * math.sin(lid_angle) + ly * math.cos(lid_angle)
        lid_pts.append((lid_cx + rx, lid_cy + ry))
    # Close the polygon along the bottom edge (left endpoint back to right)
    # The semi-ellipse above gives us a closed dome already.

    # Drop shadow
    filled_poly(big, NEAR_BLK,
                [(x + s(1), y + s(1)) for x, y in lid_pts])
    filled_poly(big, DK, lid_pts)
    # Inset highlight
    inset_lid = []
    for x, y in lid_pts:
        dx = (x - lid_cx) * 0.86
        dy = (y - lid_cy) * 0.78
        inset_lid.append((lid_cx + dx, lid_cy + dy))
    filled_poly(big, BASE, inset_lid)
    # Highlight arc on the dome
    pygame.draw.arc(big, HI,
                    (lid_cx - lid_w // 2 + s(2),
                     lid_cy - lid_h // 2 + s(1),
                     lid_w - s(4), lid_h - s(2)),
                    math.radians(195 - 12), math.radians(345 - 12),
                    max(2, s(1)))
    # Gold rim on lid bottom
    rim_w = lid_w
    # tilted line for the rim
    rim_left = (lid_cx - rim_w // 2 * math.cos(lid_angle),
                lid_cy - rim_w // 2 * math.sin(lid_angle))
    rim_right = (lid_cx + rim_w // 2 * math.cos(lid_angle),
                 lid_cy + rim_w // 2 * math.sin(lid_angle))
    pygame.draw.line(big, GOLD, rim_left, rim_right, max(3, s(1) + 1))
    pygame.draw.line(big, GOLD_HI,
                     (rim_left[0] + s(2) * math.cos(lid_angle),
                      rim_left[1] + s(2) * math.sin(lid_angle)),
                     (rim_right[0] - s(2) * math.cos(lid_angle),
                      rim_right[1] - s(2) * math.sin(lid_angle)),
                     max(1, s(1) // 2))
    # Small finial knob on top of the lid
    knob_top_x = lid_cx - lid_h * math.sin(lid_angle)
    knob_top_y = lid_cy - lid_h * math.cos(lid_angle)
    aa_circle(big, NEAR_BLK,
              knob_top_x + s(1) // 2,
              knob_top_y + s(1) // 2, s(3))
    aa_circle(big, GOLD, knob_top_x, knob_top_y, s(3))
    aa_circle(big, GOLD_HI, knob_top_x - s(1),
              knob_top_y - s(1), max(1, s(1)))

    # Smoke leaks from the lid-gap (the askew tilt opens a wedge
    # on the right side between the lid rim and the body rim)
    smoke_origin_x = cx + s(8)
    smoke_origin_y = y_top - s(1)
    smoke_ribbon(big, smoke_origin_x, smoke_origin_y, SMOKE,
                 n_puffs=12, height_n=40, curl=2.2)
    # Faint secondary smoke on the left (lighter, smaller)
    smoke_ribbon(big, cx - s(12), y_top - s(2),
                 [(220, 200, 240), (170, 145, 210)],
                 n_puffs=6, height_n=22, curl=1.4)

    sparkles_around(big, cx, cy - s(8), n=5, radius_n=42,
                    color=GOLD_HI, rng_seed=29)


# ─────────────────────────────────────────────────────────────────────
# Original — re-renders the current in-game `_draw_genie_icon` so it
# sits next to the candidates at the same canvas size.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_original(big, cx, cy):
    BRASS_DK = ( 95,  60,  18)
    BRASS    = (185, 130,  45)
    BRASS_HI = (250, 215, 130)
    SMOKE_DK = ( 95,  60, 110)
    SMOKE    = (170, 130, 195)
    SMOKE_HI = (220, 200, 240)

    body_cx = cx
    body_cy = cy + s(8)
    body_w  = s(50)
    body_h  = s(24)
    body_rect = pygame.Rect(0, 0, body_w, body_h)
    body_rect.center = (body_cx, body_cy)
    pygame.draw.ellipse(big, NEAR_BLK, body_rect.inflate(SS, SS))
    pygame.draw.ellipse(big, BRASS_DK, body_rect)
    inner = body_rect.inflate(-int(SS * 1.5), -int(SS * 1.5))
    pygame.draw.ellipse(big, BRASS, inner)
    hi = pygame.Rect(0, 0, int(body_w * 0.55), int(body_h * 0.30))
    hi.center = (body_cx - int(body_w * 0.06),
                 body_cy - int(body_h * 0.22))
    pygame.draw.ellipse(big, BRASS_HI, hi)

    base = pygame.Rect(0, 0, int(body_w * 0.55), int(SS * 1.6))
    base.midtop = (body_cx, body_cy + body_h // 2 - SS)
    pygame.draw.rect(big, BRASS_DK, base, border_radius=SS // 2)

    spout_pts_outer = [
        (body_cx + int(body_w * 0.42), body_cy - int(body_h * 0.15)),
        (body_cx + int(body_w * 0.70), body_cy - int(body_h * 0.55)),
        (body_cx + int(body_w * 0.88), body_cy - int(body_h * 0.95)),
        (body_cx + int(body_w * 0.80), body_cy - int(body_h * 1.10)),
        (body_cx + int(body_w * 0.62), body_cy - int(body_h * 0.78)),
        (body_cx + int(body_w * 0.42), body_cy - int(body_h * 0.45)),
    ]
    pygame.draw.polygon(big, NEAR_BLK, spout_pts_outer)
    inset_pts = [
        (body_cx + int(body_w * 0.45), body_cy - int(body_h * 0.20)),
        (body_cx + int(body_w * 0.68), body_cy - int(body_h * 0.55)),
        (body_cx + int(body_w * 0.83), body_cy - int(body_h * 0.92)),
        (body_cx + int(body_w * 0.78), body_cy - int(body_h * 1.03)),
        (body_cx + int(body_w * 0.62), body_cy - int(body_h * 0.75)),
        (body_cx + int(body_w * 0.45), body_cy - int(body_h * 0.45)),
    ]
    pygame.draw.polygon(big, BRASS, inset_pts)
    pygame.draw.line(big, BRASS_HI,
                     (body_cx + int(body_w * 0.50), body_cy - int(body_h * 0.30)),
                     (body_cx + int(body_w * 0.78), body_cy - int(body_h * 0.90)),
                     max(1, SS // 2))

    handle_cx = body_cx - int(body_w * 0.55)
    handle_cy = body_cy - int(body_h * 0.15)
    handle_w = int(body_w * 0.30)
    handle_h = int(body_h * 0.85)
    handle_outer = pygame.Rect(0, 0, handle_w, handle_h)
    handle_outer.center = (handle_cx, handle_cy)
    pygame.draw.ellipse(big, NEAR_BLK, handle_outer)
    pygame.draw.ellipse(big, BRASS, handle_outer.inflate(-int(SS * 1.2),
                                                          -int(SS * 1.2)))
    cutout = handle_outer.inflate(-int(SS * 3.5), -int(SS * 3.5))
    pygame.draw.ellipse(big, SKY, cutout)
    pygame.draw.ellipse(big, BRASS_DK, cutout, max(1, SS // 2))

    plume_origin_x = body_cx + int(body_w * 0.80)
    plume_origin_y = body_cy - int(body_h * 1.10)
    smoke_ribbon(big, plume_origin_x, plume_origin_y,
                 [SMOKE_HI, SMOKE, SMOKE_DK],
                 n_puffs=10, height_n=30, curl=1.5)
    aa_circle(big, BRASS_HI, body_cx + int(body_w * 0.95),
              body_cy - int(body_h * 0.50), max(2, SS // 2) + SS // 3)
    aa_circle(big, (255, 255, 230), body_cx + int(body_w * 0.95),
              body_cy - int(body_h * 0.50), max(2, SS // 2))


# ─────────────────────────────────────────────────────────────────────
LAMPS = [
    ("Original (current)",        draw_lamp_original),
    ("1: Aladdin lamp",           draw_lamp_1_aladdin),
    ("2: Genie bottle",           draw_lamp_2_bottle),
    ("3: Persian samovar",        draw_lamp_3_samovar),
    ("4: Crystal orb on tripod",  draw_lamp_4_orb),
    ("5: Domed urn (canopic)",    draw_lamp_5_urn),
]


def render_one(fn, display_scale):
    big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    big.fill(SKY)
    cx = PW // 2
    cy = PH // 2
    fn(big, cx, cy)
    out_w = W * display_scale
    out_h = H * display_scale
    return pygame.transform.smoothscale(big, (out_w, out_h))


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "v1"
    DW = W * DISPLAY_BIG
    DH = H * DISPLAY_BIG
    SW = W * DISPLAY_SMALL
    SH = H * DISPLAY_SMALL
    cols, rows = 3, 2
    margin = 16
    label_h = 26
    small_band_h = SH + 8
    cell_h = DH + label_h + small_band_h + 8
    sheet_w = DW * cols + margin * (cols + 1)
    sheet_h = cell_h * rows + margin * (rows + 1)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 24, 32))
    font_big = pygame.font.SysFont("Arial", 18, bold=True)
    font_small = pygame.font.SysFont("Arial", 11)
    small_caption = font_small.render("in-game scale", True, (170, 180, 200))
    for i, (label, fn) in enumerate(LAMPS):
        col, row = i % cols, i // cols
        portrait = render_one(fn, DISPLAY_BIG)
        small = render_one(fn, DISPLAY_SMALL)
        x = margin + col * (DW + margin)
        y = margin + row * (cell_h + margin)
        pygame.draw.rect(sheet, (60, 65, 80),
                         (x - 2, y - 2, DW + 4, DH + 4), 2)
        sheet.blit(portrait, (x, y))
        text = font_big.render(label, True, (240, 240, 240))
        sheet.blit(text, (x + (DW - text.get_width()) // 2,
                          y + DH + 2))
        sb_y = y + DH + label_h + 6
        for k in range(3):
            sx = x + 10 + k * (SW + 12) + ((DW - 3 * SW - 24) // 2)
            sheet.blit(small, (sx, sb_y))
            pygame.draw.rect(sheet, (50, 55, 70),
                             (sx - 1, sb_y - 1, SW + 2, SH + 2), 1)
        sheet.blit(small_caption,
                   (x + DW - small_caption.get_width() - 8,
                    sb_y + SH - 2))
        if i == 0:
            ind_path = os.path.join(OUT_DIR, f"lamp_original_{tag}.png")
        else:
            ind_path = os.path.join(OUT_DIR, f"lamp_{i}_{tag}.png")
        pygame.image.save(portrait, ind_path)
    out = os.path.join(OUT_DIR, f"lamp_sheet_{tag}.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
