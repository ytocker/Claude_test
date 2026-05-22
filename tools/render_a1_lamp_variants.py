"""Render genie-lamp icon candidates + the current original side by
side for review. Each candidate is shown at 4x display scale (large)
AND at in-game scale (small) so we can compare both the
detail-reading AND the on-screen reading.

Iteration rounds:
    v1 — first pass, rejected: silhouettes wrong, smoke disconnected,
         halos competed with body, steampunk didn't read as magic.
    v2 — shared proper silhouette helper, smoke anchored to spout
         mouth, halos dropped (game adds its own ambient glow),
         steampunk replaced with Royal Velvet (matches genie carpet).
    v3 — sharper spout curl, deeper torus handle, gradient body
         shading.

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

# Per-portrait native canvas: 96x88, ×6 supersample. Wider than tall
# so the spout + handle have room.
W, H, SS = 96, 88, 6
PW, PH = W * SS, H * SS
SKY = (110, 175, 220)
NEAR_BLK = (18, 14, 10)

DISPLAY_BIG   = 4    # large preview multiplier
DISPLAY_SMALL = 1    # in-game-ish scale (icon is ~32-40px in game)


def s(v):
    return int(v * SS)


def aa_circle(surf, color, cx, cy, r):
    pygame.draw.circle(surf, color, (int(cx), int(cy)), int(r))


def ell(surf, color, cx, cy, w, h):
    pygame.draw.ellipse(surf, color,
                        (int(cx - w / 2), int(cy - h / 2),
                         int(w), int(h)))


def filled_poly(surf, color, pts):
    pygame.draw.polygon(surf, color, pts)


def stroke_poly(surf, color, pts, w=1):
    pygame.draw.polygon(surf, color, pts, int(w))


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


# ─────────────────────────────────────────────────────────────────────
# Shared lamp silhouette — proper magic-lamp profile.
#
# A real magic lamp is SQUAT (body ~3:1 wide:tall), has a defined
# foot stem + flared base, a curving S-spout that starts at the
# upper-right shoulder of the body and arcs UP then back so the
# mouth opens upward, and a looped torus handle on the opposite side
# attached via a short collar. The helper returns the spout-mouth
# coordinates so each variant can anchor smoke there.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_silhouette(big, cx, cy, palette,
                         draw_outline=True,
                         shoulder_lip_color=None):
    """Paint the lamp body + foot + spout + handle. Returns
    (mouth_x, mouth_y, gem_x, gem_y, body_cy, body_w, body_h)."""
    DK = palette["dk"]
    BASE = palette["base"]
    HI = palette["hi"]
    OUT = palette.get("outline", NEAR_BLK)

    # Body — wide squat polygon traced via a parametric ellipse
    # that's flatter on the bottom (so the foot can sit on it)
    # and gently rounded on top. 20 vertices = no visible flat
    # edges at this scale.
    body_cy = cy + s(8)
    bw = s(50)
    bh = s(22)
    body_pts = []
    n_vert = 24
    for k in range(n_vert):
        t = (k / n_vert) * math.tau - math.pi / 2  # start at top
        # Slightly flatter bottom (squash factor for lower half)
        cos_t = math.cos(t)
        sin_t = math.sin(t)
        # Asymmetric squash: top fuller, bottom flatter for foot
        if sin_t > 0:
            yk = sin_t * 0.88
        else:
            yk = sin_t * 1.0
        x = cx + cos_t * (bw / 2)
        y = body_cy + yk * (bh / 2)
        body_pts.append((int(x), int(y)))
    # outline drop-shadow underneath
    if draw_outline:
        shadow_pts = [(x, y + s(1)) for x, y in body_pts]
        filled_poly(big, OUT, shadow_pts)
    # mid tone
    filled_poly(big, DK, body_pts)
    # main fill (slightly inset)
    inset_pts = []
    for x, y in body_pts:
        dx = (x - cx) * 0.86
        dy = (y - body_cy) * 0.84
        inset_pts.append((int(cx + dx), int(body_cy + dy)))
    filled_poly(big, BASE, inset_pts)

    # Highlight crescent — thin tapered streak along upper-left
    # curve. Drawn as a 2-stroke arc so it's a smooth crescent
    # rather than a fried-egg yolk.
    hi_rect_pad = s(3)
    hi_rect = (cx - bw // 2 + hi_rect_pad,
               body_cy - bh // 2 + hi_rect_pad,
               bw - 2 * hi_rect_pad, bh - 2 * hi_rect_pad)
    pygame.draw.arc(big, HI, hi_rect,
                    math.radians(195), math.radians(330),
                    max(3, s(1) + 1))
    # Inner brighter arc (sub-highlight ridge)
    pygame.draw.arc(big, palette.get("glint", (255, 255, 255)),
                    (hi_rect[0] + s(1), hi_rect[1] + s(1),
                     hi_rect[2] - s(2), hi_rect[3] - s(2)),
                    math.radians(210), math.radians(285),
                    max(1, s(1) // 2))
    # Tiny pinpoint glint (the "rubbed-shiny spot")
    aa_circle(big, palette.get("glint", (255, 255, 255)),
              cx - s(8), body_cy - s(7), max(1, s(1)))

    # Shoulder lip — thin band where the spout joins, gives the
    # silhouette some "metal collar" depth at the shoulder.
    if shoulder_lip_color is not None:
        pygame.draw.arc(big, shoulder_lip_color,
                        (cx - bw // 2 + s(3), body_cy - bh // 2 + s(2),
                         bw - s(6), bh - s(8)),
                        math.radians(200), math.radians(340),
                        max(2, s(1)))

    # Foot stem + flared base — two stacked rects with rounded
    # corners. The stem is narrower than the base; together they
    # look like a proper goblet foot.
    stem_w = s(18)
    stem_h = s(3)
    stem_y = body_cy + bh // 2 - s(1)
    base_w = s(30)
    base_h = s(5)
    base_y = stem_y + stem_h
    if draw_outline:
        pygame.draw.rect(big, OUT,
                         (cx - stem_w // 2 - s(1) // 2, stem_y,
                          stem_w + s(1), stem_h + s(1)),
                         border_radius=s(1))
        pygame.draw.rect(big, OUT,
                         (cx - base_w // 2 - s(1) // 2, base_y,
                          base_w + s(1), base_h + s(1)),
                         border_radius=s(1))
    pygame.draw.rect(big, DK,
                     (cx - stem_w // 2, stem_y, stem_w, stem_h),
                     border_radius=s(1))
    pygame.draw.rect(big, DK,
                     (cx - base_w // 2, base_y, base_w, base_h),
                     border_radius=s(1))
    pygame.draw.rect(big, BASE,
                     (cx - stem_w // 2 + s(1) // 2, stem_y,
                      stem_w - s(1), max(1, stem_h - s(1))),
                     border_radius=s(1))
    pygame.draw.rect(big, BASE,
                     (cx - base_w // 2 + s(1) // 2, base_y,
                      base_w - s(1), max(1, base_h - s(1))),
                     border_radius=s(1))
    # Foot highlight stripe
    pygame.draw.line(big, HI,
                     (cx - base_w // 2 + s(3), base_y + s(1)),
                     (cx + base_w // 2 - s(3), base_y + s(1)),
                     max(1, s(1) // 2))

    # ─── SPOUT (right side) ─────────────────────────────────────
    # Swan-neck S-curve. BASE points are buried INSIDE the body's
    # right shoulder so the silhouette flows out of the body
    # without a visible seam. The neck sweeps OUT and UP, reaching
    # a peak above and to the right of the body. The mouth opens
    # UPWARD at the top — no question-mark curl-back.
    sp_anchor_x = cx + bw // 2 - s(8)
    sp_anchor_y = body_cy - s(1)
    # Outer (right) edge, base → tip
    outer_pts = [
        (sp_anchor_x - s(3),  sp_anchor_y + s(6)),   # buried base
        (sp_anchor_x + s(5),  sp_anchor_y + s(3)),   # shoulder exit
        (sp_anchor_x + s(12), sp_anchor_y - s(3)),   # lower outer
        (sp_anchor_x + s(18), sp_anchor_y - s(11)),  # mid outer
        (sp_anchor_x + s(21), sp_anchor_y - s(19)),  # upper outer
        (sp_anchor_x + s(20), sp_anchor_y - s(25)),  # near tip outer
        (sp_anchor_x + s(17), sp_anchor_y - s(30)),  # mouth outer rim
    ]
    # Inner (left) edge, mouth → base
    inner_pts = [
        (sp_anchor_x + s(11), sp_anchor_y - s(30)),  # mouth inner rim
        (sp_anchor_x + s(13), sp_anchor_y - s(25)),  # upper inner
        (sp_anchor_x + s(15), sp_anchor_y - s(19)),  # mid inner (back)
        (sp_anchor_x + s(13), sp_anchor_y - s(11)),  # mid inner
        (sp_anchor_x + s(8),  sp_anchor_y - s(3)),   # lower inner
        (sp_anchor_x + s(2),  sp_anchor_y + s(2)),   # shoulder return
        (sp_anchor_x - s(3),  sp_anchor_y + s(4)),   # buried return
    ]
    spout_pts = outer_pts + inner_pts

    # Mouth coords — centre of the opening at the top of the swan neck
    mouth_x = sp_anchor_x + s(14)
    mouth_y = sp_anchor_y - s(30)

    if draw_outline:
        sh_pts = [(x + s(1), y + s(1)) for x, y in spout_pts]
        filled_poly(big, OUT, sh_pts)
    filled_poly(big, DK, spout_pts)
    # Inner fill (slightly inset toward the outer edge) — gives a
    # light-side / shadow-side split.
    inset_pts = []
    for x, y in outer_pts:
        # shift inward (toward inner edge)
        dx = -s(1)
        inset_pts.append((x + dx, y + s(1)))
    for x, y in inner_pts:
        dx = s(2)
        inset_pts.append((x + dx, y))
    filled_poly(big, BASE, inset_pts)
    # Highlight stripe along the outer (right) curve of the spout
    pygame.draw.lines(big, HI, False,
                      [(sp_anchor_x + s(8),  sp_anchor_y - s(3)),
                       (sp_anchor_x + s(14), sp_anchor_y - s(11)),
                       (sp_anchor_x + s(18), sp_anchor_y - s(20))],
                      max(2, s(1)))
    # Mouth rim — dark crescent BELOW the opening so it reads as
    # a hole opening upward.
    mouth_rim_pts = [
        (sp_anchor_x + s(11), sp_anchor_y - s(29)),
        (sp_anchor_x + s(14), sp_anchor_y - s(28)),
        (sp_anchor_x + s(17), sp_anchor_y - s(29)),
    ]
    pygame.draw.lines(big, OUT, False, mouth_rim_pts, max(2, s(1)))
    # Mouth opening — small dark oval at the very top
    ell(big, OUT, mouth_x, mouth_y, s(6), s(2))

    # ─── HANDLE (left side, torus look) ────────────────────────
    # Outer ring → middle fill → DARK inner hole (slightly darker
    # than SKY so the torus reads as a ring, not a flat band) →
    # heavy inner shadow on the right + bottom of the hole.
    h_cx = cx - bw // 2 - s(4)
    h_cy = body_cy - s(2)
    h_w  = s(13)
    h_h  = s(22)
    HOLE_COLOR = (60, 95, 130)   # darker than SKY (110,175,220)
    if draw_outline:
        pygame.draw.ellipse(big, OUT,
                            (h_cx - h_w // 2 - s(1),
                             h_cy - h_h // 2 - s(1),
                             h_w + s(2), h_h + s(2)))
    pygame.draw.ellipse(big, DK,
                        (h_cx - h_w // 2, h_cy - h_h // 2, h_w, h_h))
    pygame.draw.ellipse(big, BASE,
                        (h_cx - h_w // 2 + s(1) // 2,
                         h_cy - h_h // 2 + s(1) // 2,
                         h_w - s(1), h_h - s(1)))
    # Inner hole — distinct dark colour so it doesn't blend with sky
    pygame.draw.ellipse(big, HOLE_COLOR,
                        (h_cx - h_w // 2 + s(3),
                         h_cy - h_h // 2 + s(4),
                         h_w - s(6), h_h - s(8)))
    # Inner shadow — thick arc on the right + bottom of the hole
    pygame.draw.arc(big, OUT,
                    (h_cx - h_w // 2 + s(3),
                     h_cy - h_h // 2 + s(4),
                     h_w - s(6), h_h - s(8)),
                    math.radians(260), math.radians(80),
                    max(3, s(1) + 1))
    # Top + bottom highlight ticks on the ring (catch-light)
    pygame.draw.line(big, HI,
                     (h_cx - s(1), h_cy - h_h // 2 + s(1)),
                     (h_cx + s(3), h_cy - h_h // 2 + s(1)),
                     max(2, s(1)))
    pygame.draw.line(big, HI,
                     (h_cx + h_w // 2 - s(1), h_cy + s(2)),
                     (h_cx + h_w // 2 - s(1), h_cy + s(5)),
                     max(2, s(1)))
    # Connector stubs — small rects where the handle joins the body
    pygame.draw.rect(big, DK,
                     (h_cx + h_w // 2 - s(1), h_cy - s(8),
                      s(4), s(3)))
    pygame.draw.rect(big, DK,
                     (h_cx + h_w // 2 - s(1), h_cy + s(5),
                      s(4), s(3)))

    # Convenient anchor points for variant decoration
    gem_x = cx + s(2)
    gem_y = body_cy + s(1)
    return mouth_x, mouth_y, gem_x, gem_y, body_cy, bw, bh


# ─────────────────────────────────────────────────────────────────────
# Smoke ribbon — properly anchored. Origin is the SPOUT MOUTH.
# Puffs rise vertically with a gentle sway, taper as they climb.
# ─────────────────────────────────────────────────────────────────────

def smoke_ribbon(surf, ox, oy, palette, n_puffs=11, height_n=42, curl=2.0):
    for i in range(n_puffs):
        k = i / max(1, n_puffs - 1)
        sway = math.sin(0.6 + i * 0.5) * s(curl) * (0.3 + k)
        x = ox + sway
        y = oy - int(s(height_n) * k)
        rad = max(s(1), int(s(3.5) * (1 - k * 0.55)))
        alpha = int(225 * (1 - k * 0.78))
        col = palette[min(int(k * len(palette)), len(palette) - 1)]
        puff = pygame.Surface((rad * 2 + 4, rad * 2 + 4),
                              pygame.SRCALPHA)
        pygame.draw.circle(puff, (*col, alpha),
                           (rad + 2, rad + 2), rad)
        surf.blit(puff, (int(x - rad - 2), int(y - rad - 2)))


def sparkles_around(surf, cx, cy, n=5, radius_n=38, color=(255, 240, 180),
                    rng_seed=11):
    rng = random.Random(rng_seed)
    R = s(radius_n)
    for _ in range(n):
        ang = rng.uniform(-math.pi * 0.9, math.pi * 0.2)
        r = rng.uniform(R * 0.7, R)
        sx = cx + math.cos(ang) * r
        sy = cy + math.sin(ang) * r * 0.85 - s(4)
        sr = max(1, rng.randint(s(1) // 2, s(1)))
        cross_w = max(1, s(1) // 2)
        pygame.draw.line(surf, color,
                         (int(sx - sr * 2), int(sy)),
                         (int(sx + sr * 2), int(sy)), cross_w)
        pygame.draw.line(surf, color,
                         (int(sx), int(sy - sr * 2)),
                         (int(sx), int(sy + sr * 2)), cross_w)
        aa_circle(surf, (255, 255, 255), sx, sy, max(1, sr))


# ─────────────────────────────────────────────────────────────────────
# Variant 1 — Disney-Aladdin classic. Warm amber + ruby + gold trim.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_1_aladdin(big, cx, cy):
    pal = {
        "dk":    (110,  60,  10),
        "base":  (210, 140,  35),
        "hi":    (255, 220, 120),
        "glint": (255, 255, 230),
    }
    GOLD = (255, 230, 140)
    RUBY = (220,  55,  75)
    RUBY_HI = (255, 175, 195)
    SMOKE = [(230, 205, 250), (185, 140, 220), (135,  85, 170)]

    mx, my, gx, gy, body_cy, bw, bh = draw_lamp_silhouette(
        big, cx, cy, pal, shoulder_lip_color=GOLD)

    # Gold rim band across the top of the dome
    pygame.draw.arc(big, GOLD,
                    (cx - bw // 2 + s(4), body_cy - bh // 2 - s(1),
                     bw - s(8), bh - s(8)),
                    math.radians(195), math.radians(345), max(3, s(1) + 1))
    # Ruby gem at the dome centre-top
    gem_diamond(big, gx, gy - s(2), s(4), RUBY, RUBY_HI)

    # Smoke from spout mouth
    smoke_ribbon(big, mx, my, SMOKE, n_puffs=11, height_n=44, curl=1.8)

    # Warm sparkles up-left of the lamp
    sparkles_around(big, cx, cy - s(4), n=5, radius_n=42,
                    color=(255, 235, 170))


# ─────────────────────────────────────────────────────────────────────
# Variant 2 — Persian ornate. Cool brass + engraved bands + sapphire +
# gold tassel from the handle.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_2_persian(big, cx, cy):
    pal = {
        "dk":    ( 75,  50,  20),
        "base":  (175, 140,  70),
        "hi":    (235, 215, 155),
        "glint": (255, 250, 220),
    }
    GOLD = (255, 230, 150)
    SAPPHIRE = ( 70, 100, 220)
    SAPPHIRE_HI = (175, 200, 255)
    SMOKE = [(215, 215, 240), (170, 165, 215), (110, 100, 160)]

    mx, my, gx, gy, body_cy, bw, bh = draw_lamp_silhouette(
        big, cx, cy, pal, shoulder_lip_color=GOLD)

    # Engraved bands — two concentric dotted arcs sweeping across
    # the belly. Equal spacing along each arc so they read as
    # deliberate engraving rather than random freckles.
    for band_y_off, ry_n, n_dots in (
            (-s(5), s(7), 13),
            ( s(3), s(7), 13)):
        for j in range(n_dots):
            t = j / (n_dots - 1)
            ang = math.radians(205 + 130 * t)
            x = cx + math.cos(ang) * (bw * 0.42)
            y = body_cy + band_y_off + math.sin(ang) * ry_n
            aa_circle(big, NEAR_BLK,
                      int(x + s(1) // 3), int(y + s(1) // 3),
                      max(1, s(1) // 2))
            aa_circle(big, GOLD, int(x), int(y), max(1, s(1) // 2))

    # Centre arabesque rosette — 4-petal flower
    rose_x = gx
    rose_y = gy + s(1)
    for dx, dy in ((-s(3), 0), (s(3), 0), (0, -s(3)), (0, s(3))):
        aa_circle(big, GOLD, rose_x + dx, rose_y + dy,
                  max(1, s(1) // 2 + 1))
    aa_circle(big, NEAR_BLK, rose_x, rose_y, max(1, s(1)))
    aa_circle(big, GOLD, rose_x, rose_y, max(1, s(1) // 2 + 1))

    # Sapphire on the spout base
    gem_round(big, cx + s(20), body_cy - s(4), s(3),
              SAPPHIRE, SAPPHIRE_HI)

    # Gold silk tassel hanging from the handle. Structure:
    # rope (visible length) → wrap collar → tassel bell → 5 threads.
    # Positioned BELOW + LEFT of the handle so the rope reads as a
    # proper drop.
    rope_start = (cx - s(33), body_cy + s(9))
    tcx = cx - s(38)
    tcy = body_cy + s(20)
    # Rope — clearly visible diagonal stroke
    pygame.draw.line(big, NEAR_BLK,
                     (rope_start[0] + s(1) // 3,
                      rope_start[1] + s(1) // 3),
                     (tcx + s(1) // 3, tcy - s(3) + s(1) // 3),
                     max(3, s(1) + 1))
    pygame.draw.line(big, GOLD,
                     rope_start, (tcx, tcy - s(3)),
                     max(2, s(1)))
    # Wrap collar — small dark rectangle binding the threads
    pygame.draw.rect(big, NEAR_BLK,
                     (tcx - s(2) - s(1) // 2,
                      tcy - s(3) - s(1) // 2,
                      s(4) + s(1), s(3) + s(1)))
    pygame.draw.rect(big, GOLD,
                     (tcx - s(2), tcy - s(3), s(4), s(3)))
    # Tassel bell (gold bulge below the collar)
    pygame.draw.polygon(big, NEAR_BLK,
                        [(tcx - s(3) - s(1) // 2, tcy),
                         (tcx + s(3) + s(1) // 2, tcy),
                         (tcx + s(2) + s(1) // 2, tcy + s(5)),
                         (tcx - s(2) - s(1) // 2, tcy + s(5))])
    pygame.draw.polygon(big, GOLD,
                        [(tcx - s(3), tcy),
                         (tcx + s(3), tcy),
                         (tcx + s(2), tcy + s(5)),
                         (tcx - s(2), tcy + s(5))])
    # Hanging threads (5 thin strokes from the bell bottom)
    for j, dx in enumerate((-s(2), -s(1), 0, s(1), s(2))):
        pygame.draw.line(big, GOLD,
                         (tcx + dx, tcy + s(5)),
                         (tcx + dx - dx // 4, tcy + s(11)),
                         max(1, s(1) // 2))

    smoke_ribbon(big, mx, my, SMOKE, n_puffs=10, height_n=38, curl=1.4)
    sparkles_around(big, cx, cy - s(2), n=4, radius_n=38,
                    color=(235, 220, 170), rng_seed=21)


# ─────────────────────────────────────────────────────────────────────
# Variant 3 — Royal Velvet. Deep purple body + gold + ruby. Designed
# to match the genie character's velvet magic carpet so the
# pickup-icon and the cinematic share a palette.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_3_royal_velvet(big, cx, cy):
    pal = {
        "dk":    ( 50,  20,  75),
        "base":  (105,  55, 155),
        "hi":    (175, 130, 215),
        "glint": (235, 215, 255),
    }
    GOLD = (255, 220, 110)
    GOLD_HI = (255, 245, 175)
    RUBY = (220,  55,  75)
    RUBY_HI = (255, 175, 195)
    SMOKE = [(245, 220, 255), (200, 165, 230), (145, 100, 200)]

    mx, my, gx, gy, body_cy, bw, bh = draw_lamp_silhouette(
        big, cx, cy, pal, shoulder_lip_color=GOLD)

    # Gold trim along the equator of the body — adds the "royal"
    # banded look. Drawn as a thin arc.
    pygame.draw.arc(big, GOLD,
                    (cx - bw // 2 + s(3), body_cy - s(1),
                     bw - s(6), s(6)),
                    math.radians(195), math.radians(345),
                    max(3, s(1) + 1))
    pygame.draw.arc(big, GOLD_HI,
                    (cx - bw // 2 + s(3), body_cy,
                     bw - s(6), s(4)),
                    math.radians(210), math.radians(330),
                    max(1, s(1) // 2))

    # Gold rim at the dome
    pygame.draw.arc(big, GOLD,
                    (cx - bw // 2 + s(4), body_cy - bh // 2 - s(1),
                     bw - s(8), bh - s(8)),
                    math.radians(195), math.radians(345), max(3, s(1) + 1))

    # Ruby centre gem
    gem_diamond(big, gx, gy - s(2), s(4), RUBY, RUBY_HI)

    # Small gold pip dots above and below the equator band
    for dx in (-s(14), -s(7), s(7), s(14)):
        aa_circle(big, GOLD, cx + dx, body_cy - s(5), max(1, s(1) // 2))
        aa_circle(big, GOLD, cx + dx, body_cy + s(6), max(1, s(1) // 2))

    smoke_ribbon(big, mx, my, SMOKE, n_puffs=12, height_n=44, curl=2.0)
    sparkles_around(big, cx, cy - s(4), n=6, radius_n=42,
                    color=GOLD_HI, rng_seed=31)


# ─────────────────────────────────────────────────────────────────────
# Variant 4 — Cosmic crystal. Translucent navy body with nebula
# clouds + star dots INSIDE the silhouette. Gold rim so the outline
# stays crisp. Cyan magical smoke.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_4_cosmic(big, cx, cy):
    pal = {
        "dk":    ( 12,  10,  35),
        "base":  ( 26,  20,  62),
        "hi":    ( 75,  60, 140),
        "glint": (240, 230, 255),
        "outline": (250, 230, 130),  # crisp gold outline
    }
    NEBULA = [(130,  60, 200), (210,  90, 180), ( 70, 130, 230)]
    GOLD = (255, 230, 150)
    GOLD_HI = (255, 245, 195)
    CYAN = (175, 230, 255)
    WHITE = (250, 250, 250)
    SMOKE = [WHITE, CYAN, (130, 110, 210), ( 80,  60, 180)]

    mx, my, gx, gy, body_cy, bw, bh = draw_lamp_silhouette(
        big, cx, cy, pal, shoulder_lip_color=GOLD)

    # Build a body-shaped clip mask from a parametric oval that
    # matches the silhouette helper's body shape.
    clip = pygame.Surface((PW, PH), pygame.SRCALPHA)
    body_mask_pts = []
    for k in range(24):
        t = (k / 24) * math.tau - math.pi / 2
        cos_t = math.cos(t)
        sin_t = math.sin(t)
        if sin_t > 0:
            yk = sin_t * 0.86
        else:
            yk = sin_t * 0.98
        body_mask_pts.append((cx + cos_t * (bw / 2 - s(2)),
                              body_cy + yk * (bh / 2 - s(1))))
    # Nebula — fewer puffs, bigger, lower alpha so the body
    # silhouette stays crisp.
    rng = random.Random(7)
    for _ in range(8):
        nx = cx + rng.randint(-int(bw // 2) + s(5),
                              int(bw // 2) - s(5))
        ny = body_cy + rng.randint(-int(bh // 2) + s(3),
                                    int(bh // 2) - s(3))
        nr = rng.randint(s(3), s(6))
        col = rng.choice(NEBULA)
        srf = pygame.Surface((nr * 2 + 4, nr * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(srf, (*col, 100), (nr + 2, nr + 2), nr)
        clip.blit(srf, (nx - nr - 2, ny - nr - 2))
    # Stars — brighter + crisp + a 4-point cross on a couple
    rng2 = random.Random(13)
    for k in range(11):
        sx_p = cx + rng2.randint(-int(bw // 2) + s(5),
                                 int(bw // 2) - s(5))
        sy_p = body_cy + rng2.randint(-int(bh // 2) + s(3),
                                       int(bh // 2) - s(3))
        if k < 3:
            sr = max(1, s(1) // 2)
            pygame.draw.line(clip, (*WHITE, 240),
                             (sx_p - s(1), sy_p), (sx_p + s(1), sy_p),
                             max(1, s(1) // 2))
            pygame.draw.line(clip, (*WHITE, 240),
                             (sx_p, sy_p - s(1)), (sx_p, sy_p + s(1)),
                             max(1, s(1) // 2))
        pygame.draw.circle(clip, (*WHITE, 240),
                           (sx_p, sy_p), max(1, s(1) // 2))
    # Mask via the body polygon
    mask = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(int(x), int(y)) for x, y in body_mask_pts])
    clip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(clip, (0, 0))

    # Crisp gold rim across dome — gives the silhouette its lift
    pygame.draw.arc(big, GOLD,
                    (cx - bw // 2 + s(4), body_cy - bh // 2 - s(1),
                     bw - s(8), bh - s(8)),
                    math.radians(195), math.radians(345), max(3, s(1) + 1))
    # Tiny gold equator line
    pygame.draw.line(big, GOLD_HI,
                     (cx - bw // 2 + s(6), body_cy + s(1)),
                     (cx + bw // 2 - s(6), body_cy + s(1)),
                     max(1, s(1) // 2))

    # Big diamond gem — cyan/pearl instead of ruby
    gem_diamond(big, gx, gy - s(2), s(4), CYAN, WHITE)

    smoke_ribbon(big, mx, my, SMOKE, n_puffs=14, height_n=46, curl=2.3)
    sparkles_around(big, cx, cy - s(4), n=8, radius_n=44, color=CYAN)
    sparkles_around(big, cx, cy - s(4), n=4, radius_n=36,
                    color=GOLD_HI, rng_seed=17)


# ─────────────────────────────────────────────────────────────────────
# Variant 5 — Comic-book pop. Thick black outlines, flat colour
# blocks, halftone shadow, soft 6-ray sunburst behind (does NOT
# overlap the lamp).
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_5_comic(big, cx, cy):
    pal = {
        "dk":    (180, 130,  20),
        "base":  (255, 200,  60),
        "hi":    (255, 240, 140),
        "glint": (255, 255, 240),
        "outline": (15, 10, 5),
    }
    OUT = (15, 10, 5)
    GOLD = (255, 200, 60)
    GOLD_HI = (255, 240, 140)
    RUBY = (220, 60, 80)
    WHITE = (255, 255, 245)
    SMOKE_COMIC = (215, 220, 240)

    # Radial sunburst BEHIND the lamp — upper hemisphere only so
    # the rays don't blast through the lamp's foot. Rays converge
    # toward the lamp body; inner radius keeps them clear of the
    # body silhouette.
    burst_cx = cx
    burst_cy = cy + s(8)
    r_inner = s(34)
    r_outer = s(46)
    n_rays = 9
    for k in range(n_rays):
        # Sweep across upper hemisphere, with two extra side rays
        ang = math.radians(-160 + 140 * (k / (n_rays - 1)))
        for col, half_w_deg in ((NEAR_BLK, 7),
                                 (GOLD_HI, 5)):
            w_rad = math.radians(half_w_deg)
            tip_x = burst_cx + math.cos(ang) * r_outer
            tip_y = burst_cy + math.sin(ang) * r_outer * 0.85
            l_x = burst_cx + math.cos(ang - w_rad) * r_inner
            l_y = burst_cy + math.sin(ang - w_rad) * r_inner * 0.85
            r_x = burst_cx + math.cos(ang + w_rad) * r_inner
            r_y = burst_cy + math.sin(ang + w_rad) * r_inner * 0.85
            pygame.draw.polygon(big, col,
                                [(int(tip_x), int(tip_y)),
                                 (int(l_x), int(l_y)),
                                 (int(r_x), int(r_y))])

    mx, my, gx, gy, body_cy, bw, bh = draw_lamp_silhouette(
        big, cx, cy, pal)

    # Halftone dots — only on the RIGHT (shadow) half of the body,
    # clipped to the body ellipse via a per-dot inside-test. Spacing
    # is regular so it reads as comic shading, not noise.
    spacing = s(2) + 1
    for dx in range(s(2), bw // 2 - s(3), spacing):
        for dy in range(-bh // 2 + s(3), bh // 2 - s(2), spacing):
            # Inside-ellipse test (slightly shrunken so dots don't
            # clip the outline)
            nx = dx / (bw / 2 - s(2))
            ny = dy / (bh / 2 - s(2))
            if nx * nx + ny * ny <= 1.0:
                aa_circle(big, OUT, cx + dx + s(1), body_cy + dy,
                          max(1, s(1) // 2))

    # Equator gold line for that comic flat-tone read
    pygame.draw.line(big, OUT,
                     (cx - bw // 2 + s(5), body_cy + s(1)),
                     (cx + bw // 2 - s(5), body_cy + s(1)),
                     max(2, s(1) // 2))

    # Big ruby gem (rotated square style) with black thick outline
    gem_diamond(big, gx, gy - s(2), s(5), RUBY, (255, 175, 195))

    # Smoke — cumulus puff chain (comic style). 3 puffs, tight
    # vertical spacing so they all fit on the canvas. Each puff is
    # a 3-bump cluster so it has a cumulus feel rather than a
    # perfect circle.
    for r, dx, dy in [(s(6),  s(0),  -s(7)),
                      (s(5),  s(4),  -s(14)),
                      (s(4), -s(3),  -s(21))]:
        cx_p = mx + dx
        cy_p = my + dy
        # outline (drawn behind the fill)
        for ox, oy in ((-r // 2, 0), (r // 2, -r // 3), (0, 0)):
            aa_circle(big, OUT, cx_p + ox, cy_p + oy,
                      r + max(2, s(1) // 2))
        # fill (puff cluster)
        for ox, oy in ((-r // 2, 0), (r // 2, -r // 3), (0, 0)):
            aa_circle(big, SMOKE_COMIC, cx_p + ox, cy_p + oy, r)


# ─────────────────────────────────────────────────────────────────────
# Original — re-renders the current in-game `_draw_genie_icon` recipe
# at the same canvas so the side-by-side scale matches.
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
    ("Original (current)",   draw_lamp_original),
    ("1: Aladdin classic",   draw_lamp_1_aladdin),
    ("2: Persian ornate",    draw_lamp_2_persian),
    ("3: Royal velvet",      draw_lamp_3_royal_velvet),
    ("4: Cosmic crystal",    draw_lamp_4_cosmic),
    ("5: Comic-book pop",    draw_lamp_5_comic),
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
    label_h = 24
    # Layout: per cell — big portrait on top, label, then a row
    # of 3 small in-game-scale previews for readability check.
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
        # Small previews — 3 copies in a row so we can see how
        # much the icon stands out on its own (since in-game it'll
        # be mid-scrolling and small).
        sb_y = y + DH + label_h + 6
        for k in range(3):
            sx = x + 10 + k * (SW + 12) + ((DW - 3 * SW - 24) // 2)
            sheet.blit(small, (sx, sb_y))
            pygame.draw.rect(sheet, (50, 55, 70),
                             (sx - 1, sb_y - 1, SW + 2, SH + 2), 1)
        sheet.blit(small_caption,
                   (x + DW - small_caption.get_width() - 8,
                    sb_y + SH - 2))
        # Save individual portrait
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
