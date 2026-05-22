"""Render 5 GENIE-BOTTLE variants at higher resolution + more
decoration. All five share the same tall translucent-glass bottle
silhouette so they read as the same artefact family; what varies is
the decorative treatment, palette, and stopper style.

Variants:
  1. Royal Sapphire — sapphire glass, gold filigree scrollwork,
     crown-shaped stopper, royal cartouche medallion on the belly.
  2. Arabesque Imperial — imperial purple glass, intricate gold
     arabesque pattern wrapping the body, twin gold tassel cords
     around the neck, jeweled finial stopper.
  3. Apothecary Antique — aged emerald-green glass, parchment
     label with calligraphy + red wax seal, brass chain, cork.
  4. Faceted Crystal — pale-cyan cut-glass with diamond facets
     across the body, multi-gem stopper, heavy sparkle ring.
  5. Celestial Nebula — deep cosmic navy glass, constellation
     lines etched on the surface, comet-trail stopper, bright
     golden core star inside.

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

# Higher resolution: SS=8 (was 6), bigger native canvas. The bottle
# is tall so the canvas is portrait.
W, H, SS = 96, 152, 8
PW, PH = W * SS, H * SS
SKY = (110, 175, 220)
NEAR_BLK = (16, 12, 8)

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


def filled_poly(surf, color, pts):
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])


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


def smoke_ribbon(surf, ox, oy, palette, n_puffs=14, height_n=42,
                 curl=2.0, taper=True, start_radius=4):
    for i in range(n_puffs):
        k = i / max(1, n_puffs - 1)
        sway = math.sin(0.6 + i * 0.55) * s(curl) * (0.3 + k)
        x = ox + sway
        y = oy - int(s(height_n) * k)
        if taper:
            rad = max(s(1), int(s(start_radius) * (1 - k * 0.65)))
        else:
            rad = max(s(1), int(s(start_radius * 0.7)))
        alpha = int(235 * (1 - k * 0.78))
        col = palette[min(int(k * len(palette)), len(palette) - 1)]
        puff = pygame.Surface((rad * 2 + 4, rad * 2 + 4),
                              pygame.SRCALPHA)
        pygame.draw.circle(puff, (*col, alpha),
                           (rad + 2, rad + 2), rad)
        surf.blit(puff, (int(x - rad - 2), int(y - rad - 2)))


def sparkles_around(surf, cx, cy, n=6, radius_n=42,
                    color=(255, 240, 180), rng_seed=11,
                    ang_lo=-math.pi, ang_hi=math.pi):
    rng = random.Random(rng_seed)
    R = s(radius_n)
    for _ in range(n):
        ang = rng.uniform(ang_lo, ang_hi)
        r = rng.uniform(R * 0.7, R)
        sx = cx + math.cos(ang) * r
        sy = cy + math.sin(ang) * r * 0.95
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
# Shared bottle silhouette. Returns the polygon + key anchor points
# so each variant can decorate from a consistent starting point.
# Designed to be smooth: 80+ vertices via parametric curves.
# ─────────────────────────────────────────────────────────────────────

def bottle_silhouette(cx, cy):
    """Return (silhouette_pts, anchors). Anchors:
       neck_mouth_y, neck_bottom_y, shoulder_y,
       belly_y, foot_top_y, foot_bot_y, neck_half, belly_half, foot_half."""
    y_mouth     = cy - s(56)
    y_neck_bot  = cy - s(40)
    y_shoulder  = cy - s(32)
    y_belly     = cy + s(8)
    y_body_bot  = cy + s(38)
    y_foot      = cy + s(46)
    neck_half   = s(8)
    belly_half  = s(20)
    body_bot_half = s(15)
    foot_half   = s(17)

    # Build silhouette by parametric profile: y → half-width.
    def half_at(y):
        if y < y_neck_bot:
            # Straight neck, slight taper toward mouth
            t = (y - y_mouth) / (y_neck_bot - y_mouth)
            return neck_half * (0.92 + 0.08 * t)
        if y < y_shoulder:
            # Shoulder curve — quick widening neck → belly transition
            t = (y - y_neck_bot) / (y_shoulder - y_neck_bot)
            # Smooth ease (cosine)
            ee = 0.5 - 0.5 * math.cos(t * math.pi)
            return neck_half + ee * (belly_half * 0.92 - neck_half)
        if y < y_belly:
            # Upper body — slight continued widening to belly
            t = (y - y_shoulder) / (y_belly - y_shoulder)
            return belly_half * (0.92 + 0.08 * (1 - (1 - t) ** 2))
        if y < y_body_bot:
            # Lower body — narrow gently
            t = (y - y_belly) / (y_body_bot - y_belly)
            return belly_half + (body_bot_half - belly_half) * (
                0.5 - 0.5 * math.cos(t * math.pi))
        # Foot transition
        t = (y - y_body_bot) / (y_foot - y_body_bot)
        return body_bot_half + (foot_half - body_bot_half) * (
            1 - (1 - t) ** 2)

    n_samples = 64
    left = []
    right = []
    for k in range(n_samples + 1):
        t = k / n_samples
        y = y_mouth + t * (y_foot - y_mouth)
        half = half_at(y)
        left.append((cx - half, y))
        right.append((cx + half, y))
    silhouette = left + list(reversed(right))

    anchors = {
        "y_mouth": y_mouth,
        "y_neck_bot": y_neck_bot,
        "y_shoulder": y_shoulder,
        "y_belly": y_belly,
        "y_body_bot": y_body_bot,
        "y_foot": y_foot,
        "neck_half": neck_half,
        "belly_half": belly_half,
        "body_bot_half": body_bot_half,
        "foot_half": foot_half,
        "half_at": half_at,
    }
    return silhouette, anchors


def paint_glass_body(big, silhouette, anchors, palette):
    """Paint the bottle's glass body — drop shadow + dark base +
    inset mid-tone + vertical highlight stripe on the left curve."""
    DK    = palette["dk"]
    BASE  = palette["base"]
    HI    = palette["hi"]
    SHEEN = palette.get("sheen", (255, 255, 255))
    # Drop shadow
    shadow = [(x + s(1), y + s(1)) for x, y in silhouette]
    filled_poly(big, NEAR_BLK, shadow)
    # Outer (darker rim)
    filled_poly(big, DK, silhouette)
    # Inset mid-tone — pull the silhouette inward by ~2 native
    cx = (min(x for x, _ in silhouette) + max(x for x, _ in silhouette)) // 2
    inner = []
    for x, y in silhouette:
        dx = (x - cx) * 0.86
        inner.append((cx + dx, y))
    filled_poly(big, BASE, inner)
    # Bright vertical highlight stripe on the left curve
    half_at = anchors["half_at"]
    stripe_pts = []
    n_pts = 24
    for k in range(n_pts + 1):
        t = k / n_pts
        y = anchors["y_shoulder"] + t * (
            anchors["y_body_bot"] - anchors["y_shoulder"])
        half = half_at(y)
        stripe_pts.append((cx - half * 0.78, y))
    if len(stripe_pts) >= 2:
        pygame.draw.lines(big, HI, False, stripe_pts, max(3, s(1) + 1))
    # Crisper sub-stripe (very thin near-white)
    sub_stripe = stripe_pts[2:-2] if len(stripe_pts) > 6 else stripe_pts
    if len(sub_stripe) >= 2:
        pygame.draw.lines(big, SHEEN, False, sub_stripe, max(1, s(1) // 2))


def clip_to_body(surf, silhouette):
    """Apply a body-shaped alpha mask to `surf` so any inner-glass
    drawing stays within the bottle's silhouette."""
    mask = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(int(x), int(y)) for x, y in silhouette])
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


def paint_internal_swirl(big, silhouette, anchors,
                         smoke_palette, star_color=(255, 255, 250),
                         spiral_intensity=1.0,
                         star_count=14,
                         core_star=None):
    """Draw swirling smoke + star dots INSIDE the bottle. Clipped
    to the silhouette so nothing leaks out. Higher resolution =
    more puffs + more star detail."""
    clip = pygame.Surface((PW, PH), pygame.SRCALPHA)
    rng = random.Random(7)
    # Spiral smoke from foot to neck — more puffs at higher SS
    n_swirl = 16
    for k in range(n_swirl):
        t = k / (n_swirl - 1)
        spiral_ang = t * math.tau * 1.6 * spiral_intensity
        radius = s(11) * (1 - t * 0.55)
        cx_local = (min(x for x, _ in silhouette) + max(x for x, _ in silhouette)) // 2
        sx = cx_local + math.cos(spiral_ang) * radius
        sy = anchors["y_body_bot"] - t * (
            anchors["y_body_bot"] - anchors["y_neck_bot"] + s(2))
        r = s(3) + rng.randint(-1, 2)
        col = smoke_palette[k % len(smoke_palette)]
        alpha = 160 if k < n_swirl - 3 else 210
        sub = pygame.Surface((r * 2 + 4, r * 2 + 4),
                             pygame.SRCALPHA)
        pygame.draw.circle(sub, (*col, alpha),
                           (r + 2, r + 2), r)
        clip.blit(sub, (sx - r - 2, sy - r - 2))
    # Star dots
    for j in range(star_count):
        cx_local = (min(x for x, _ in silhouette) + max(x for x, _ in silhouette)) // 2
        # Generate within bounding box of body
        sx_p = cx_local + rng.randint(-s(16), s(16))
        sy_p = rng.randint(anchors["y_shoulder"] + s(2),
                            anchors["y_body_bot"] - s(2))
        sr = max(1, s(1) // 2 + rng.randint(0, 1))
        if j % 3 == 0:
            cw = max(1, s(1) // 3)
            pygame.draw.line(clip, (*star_color, 200),
                             (sx_p - sr * 3, sy_p),
                             (sx_p + sr * 3, sy_p), cw)
            pygame.draw.line(clip, (*star_color, 200),
                             (sx_p, sy_p - sr * 3),
                             (sx_p, sy_p + sr * 3), cw)
        pygame.draw.circle(clip, (*star_color, 235), (sx_p, sy_p), sr)
    # Optional core star — bright halo + cross
    if core_star is not None:
        ccx, ccy, ccol = core_star
        for r_n, a in ((s(8), 90), (s(5), 160), (s(3), 230)):
            sub = pygame.Surface((r_n * 2 + 4, r_n * 2 + 4),
                                 pygame.SRCALPHA)
            pygame.draw.circle(sub, (*ccol, a),
                               (r_n + 2, r_n + 2), r_n)
            clip.blit(sub, (ccx - r_n - 2, ccy - r_n - 2))
        # 4-point cross
        for dx, dy in ((s(8), 0), (-s(8), 0), (0, s(8)), (0, -s(8))):
            pygame.draw.line(clip, (*ccol, 200),
                             (ccx, ccy), (ccx + dx, ccy + dy),
                             max(2, s(1)))
    clip_to_body(clip, silhouette)
    big.blit(clip, (0, 0))


# ─────────────────────────────────────────────────────────────────────
# Variant 1 — Royal Sapphire. Deep sapphire blue glass, gold filigree
# scrollwork on the body, crown-shaped stopper, royal cartouche
# medallion on the belly with a ruby.
# ─────────────────────────────────────────────────────────────────────

def draw_bottle_1_royal_sapphire(big, cx, cy):
    pal = {
        "dk":    ( 18,  30,  90),
        "base":  ( 45,  75, 175),
        "hi":    (140, 175, 235),
        "sheen": (235, 245, 255),
    }
    GOLD     = (255, 220, 110)
    GOLD_HI  = (255, 245, 175)
    GOLD_DK  = (180, 130,  40)
    RUBY     = (220,  55,  75)
    RUBY_HI  = (255, 175, 195)
    SMOKE    = [(245, 230, 255), (180, 200, 245), (110, 140, 220),
                ( 70,  95, 185)]

    silhouette, anc = bottle_silhouette(cx, cy)
    paint_glass_body(big, silhouette, anc, pal)
    paint_internal_swirl(big, silhouette, anc, SMOKE,
                         star_color=(225, 235, 255), star_count=14)

    # Gold filigree scrollwork — 4 elegant S-curves wrapping the
    # body corners. Each scroll is drawn as a smooth polyline with
    # a darker shadow underlay.
    half_at = anc["half_at"]
    def scroll(start_y, end_y, side, anchor_outset_n, curl_dir):
        """side: -1 (left) or +1 (right). curl_dir: +1 or -1 for inward/outward."""
        pts = []
        for k in range(14):
            t = k / 13.0
            y = start_y + t * (end_y - start_y)
            half = half_at(y)
            # base offset
            base_x = cx + side * (half - s(2))
            # curl outward then inward (S-curve)
            curl = math.sin(t * math.pi * 1.5) * s(3) * curl_dir
            x = base_x + side * (anchor_outset_n + curl)
            pts.append((x, y))
        # Shadow
        pygame.draw.lines(big, NEAR_BLK, False,
                          [(p[0] + s(1) // 3, p[1] + s(1) // 3) for p in pts],
                          max(4, s(1) + 1))
        pygame.draw.lines(big, GOLD_DK, False, pts, max(3, s(1)))
        pygame.draw.lines(big, GOLD, False, pts, max(2, s(1) - 1))
        # tip — small curl ball
        aa_circle(big, GOLD_DK, pts[0][0], pts[0][1], max(2, s(1)))
        aa_circle(big, GOLD_HI, pts[0][0] - s(1) // 2,
                  pts[0][1] - s(1) // 2, max(1, s(1) // 2))
        aa_circle(big, GOLD_DK, pts[-1][0], pts[-1][1], max(2, s(1)))
        aa_circle(big, GOLD_HI, pts[-1][0] - s(1) // 2,
                  pts[-1][1] - s(1) // 2, max(1, s(1) // 2))

    scroll(anc["y_shoulder"] + s(2), anc["y_belly"] - s(2), -1, s(1), -1)
    scroll(anc["y_shoulder"] + s(2), anc["y_belly"] - s(2),  1, s(1),  1)
    scroll(anc["y_belly"] + s(4), anc["y_body_bot"] - s(2), -1, s(1),  1)
    scroll(anc["y_belly"] + s(4), anc["y_body_bot"] - s(2),  1, s(1), -1)

    # Royal cartouche medallion at the belly centre — oval shield
    med_cx, med_cy = cx, anc["y_belly"]
    med_w, med_h = s(15), s(10)
    pygame.draw.ellipse(big, NEAR_BLK,
                        (med_cx - med_w // 2 - s(1) // 2,
                         med_cy - med_h // 2 - s(1) // 2,
                         med_w + s(1), med_h + s(1)))
    pygame.draw.ellipse(big, GOLD_DK,
                        (med_cx - med_w // 2, med_cy - med_h // 2,
                         med_w, med_h))
    pygame.draw.ellipse(big, GOLD,
                        (med_cx - med_w // 2 + s(1) // 2,
                         med_cy - med_h // 2 + s(1) // 2,
                         med_w - s(1), med_h - s(1)))
    # tiny inner panel
    pygame.draw.ellipse(big, GOLD_DK,
                        (med_cx - med_w // 2 + s(2),
                         med_cy - med_h // 2 + s(2),
                         med_w - s(4), med_h - s(4)))
    # crown silhouette on top of the medallion
    cr_y = med_cy - med_h // 2 - s(1)
    pygame.draw.polygon(big, GOLD,
                        [(med_cx - s(5), cr_y),
                         (med_cx - s(3), cr_y - s(3)),
                         (med_cx - s(1), cr_y - s(1)),
                         (med_cx, cr_y - s(4)),
                         (med_cx + s(1), cr_y - s(1)),
                         (med_cx + s(3), cr_y - s(3)),
                         (med_cx + s(5), cr_y)])
    pygame.draw.polygon(big, NEAR_BLK,
                        [(med_cx - s(5), cr_y),
                         (med_cx - s(3), cr_y - s(3)),
                         (med_cx - s(1), cr_y - s(1)),
                         (med_cx, cr_y - s(4)),
                         (med_cx + s(1), cr_y - s(1)),
                         (med_cx + s(3), cr_y - s(3)),
                         (med_cx + s(5), cr_y)], max(1, s(1) // 2))
    # ruby in the medallion centre
    gem_diamond(big, med_cx, med_cy + s(1), s(2) + s(1) // 2,
                RUBY, RUBY_HI)
    # tiny dots flanking the ruby
    aa_circle(big, GOLD_HI, med_cx - s(5), med_cy, max(1, s(1) // 2))
    aa_circle(big, GOLD_HI, med_cx + s(5), med_cy, max(1, s(1) // 2))

    # Gold neck collar — wider + more layered than r3
    n_top = anc["y_neck_bot"] - s(1)
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - anc["neck_half"] - s(3), n_top - s(3),
                      anc["neck_half"] * 2 + s(6), s(8)))
    pygame.draw.rect(big, GOLD_DK,
                     (cx - anc["neck_half"] - s(2), n_top - s(3),
                      anc["neck_half"] * 2 + s(4), s(7)))
    pygame.draw.rect(big, GOLD,
                     (cx - anc["neck_half"] - s(2), n_top - s(2),
                      anc["neck_half"] * 2 + s(4), s(5)))
    pygame.draw.line(big, GOLD_HI,
                     (cx - anc["neck_half"] - s(1), n_top - s(1)),
                     (cx + anc["neck_half"] + s(1), n_top - s(1)),
                     max(1, s(1) // 2))
    # tiny rivet dots on the collar
    for dx in (-anc["neck_half"], 0, anc["neck_half"]):
        aa_circle(big, GOLD_DK, cx + dx, n_top + s(1),
                  max(1, s(1) // 2))

    # Foot ring — gold band, ornate
    f_y = anc["y_foot"]
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - anc["foot_half"] - s(2), f_y - s(1),
                      anc["foot_half"] * 2 + s(4), s(6)))
    pygame.draw.rect(big, GOLD_DK,
                     (cx - anc["foot_half"] - s(1), f_y - s(1),
                      anc["foot_half"] * 2 + s(2), s(5)))
    pygame.draw.rect(big, GOLD,
                     (cx - anc["foot_half"] - s(1), f_y,
                      anc["foot_half"] * 2 + s(2), s(3)))
    pygame.draw.line(big, GOLD_HI,
                     (cx - anc["foot_half"] + s(1), f_y + s(1)),
                     (cx + anc["foot_half"] - s(1), f_y + s(1)),
                     max(1, s(1) // 2))

    # Crown-shaped stopper — 5-spike crown, slightly tilted off the
    # neck mouth so smoke can escape from beneath
    stop_cx = cx + s(2)
    stop_base_y = anc["y_mouth"] - s(2)
    stop_w = s(14)
    # Base band
    pygame.draw.rect(big, NEAR_BLK,
                     (stop_cx - stop_w // 2 - s(1),
                      stop_base_y - s(1),
                      stop_w + s(2), s(5)))
    pygame.draw.rect(big, GOLD_DK,
                     (stop_cx - stop_w // 2, stop_base_y,
                      stop_w, s(4)))
    pygame.draw.rect(big, GOLD,
                     (stop_cx - stop_w // 2 + s(1) // 2,
                      stop_base_y + s(1) // 2,
                      stop_w - s(1), s(3)))
    # 5 spikes — middle taller, with a tiny gem on top of the middle
    spike_y_top = stop_base_y - s(8)
    mid_x = stop_cx
    spikes_x = [stop_cx - s(5), stop_cx - s(2), stop_cx,
                stop_cx + s(2), stop_cx + s(5)]
    spike_heights = [s(4), s(5), s(7), s(5), s(4)]
    crown_pts = []
    crown_pts.append((stop_cx - stop_w // 2 + s(1), stop_base_y))
    for sx_, sh_ in zip(spikes_x, spike_heights):
        crown_pts.append((sx_ - s(1), stop_base_y - sh_ + s(1)))
        crown_pts.append((sx_, stop_base_y - sh_))
        crown_pts.append((sx_ + s(1), stop_base_y - sh_ + s(1)))
    crown_pts.append((stop_cx + stop_w // 2 - s(1), stop_base_y))
    # Shadow + fill
    filled_poly(big, NEAR_BLK,
                [(x + s(1) // 3, y + s(1) // 3) for x, y in crown_pts])
    filled_poly(big, GOLD_DK, crown_pts)
    # bright fill on top
    bright_pts = [(x, y + s(1)) for x, y in crown_pts]
    filled_poly(big, GOLD, bright_pts)
    # tiny ruby on the middle spike
    aa_circle(big, NEAR_BLK, mid_x, stop_base_y - s(7) + s(1) // 2,
              max(1, s(1)))
    aa_circle(big, RUBY, mid_x, stop_base_y - s(7), max(1, s(1)))
    aa_circle(big, RUBY_HI, mid_x - s(1) // 2,
              stop_base_y - s(7) - s(1) // 2, max(1, s(1) // 2))

    # Smoke escaping from the gap beneath the lifted crown
    smoke_origin_x = cx - s(3)
    smoke_origin_y = anc["y_mouth"] - s(1)
    smoke_ribbon(big, smoke_origin_x, smoke_origin_y, SMOKE,
                 n_puffs=14, height_n=44, curl=1.8, start_radius=4)

    # Sparkles around the crown
    sparkles_around(big, stop_cx, stop_base_y - s(4), n=8, radius_n=20,
                    color=(255, 245, 200), rng_seed=21)
    sparkles_around(big, cx, cy - s(8), n=5, radius_n=42,
                    color=(220, 230, 255), rng_seed=31)


# ─────────────────────────────────────────────────────────────────────
# Variant 2 — Arabesque Imperial. Imperial purple glass, intricate
# gold arabesque pattern wrapping the body, twin gold tassel cords
# tied around the neck, jeweled finial stopper.
# ─────────────────────────────────────────────────────────────────────

def draw_bottle_2_arabesque(big, cx, cy):
    pal = {
        "dk":    ( 50,  18,  90),
        "base":  (100,  50, 170),
        "hi":    (175, 135, 220),
        "sheen": (245, 230, 255),
    }
    GOLD     = (255, 220, 110)
    GOLD_HI  = (255, 245, 175)
    GOLD_DK  = (180, 130,  40)
    EMERALD  = ( 70, 175, 110)
    EMERALD_HI = (180, 240, 200)
    SMOKE    = [(245, 225, 255), (200, 165, 240), (135,  85, 200),
                ( 80,  45, 165)]

    silhouette, anc = bottle_silhouette(cx, cy)
    paint_glass_body(big, silhouette, anc, pal)
    paint_internal_swirl(big, silhouette, anc, SMOKE,
                         star_color=(255, 235, 200), star_count=12)

    half_at = anc["half_at"]

    # Arabesque pattern — a row of interlocking diamond/eye motifs
    # across the upper and lower body. Each motif is a small gold
    # diamond outline with a centre dot.
    def draw_arabesque_row(band_y, n_motifs):
        half = half_at(band_y)
        span = half * 2 - s(6)
        for j in range(n_motifs):
            t = (j + 0.5) / n_motifs
            x = cx - half + s(3) + span * t
            # diamond
            dr = s(2)
            pygame.draw.polygon(big, GOLD_DK,
                                [(x, band_y - dr),
                                 (x + dr, band_y),
                                 (x, band_y + dr),
                                 (x - dr, band_y)], max(2, s(1)))
            pygame.draw.polygon(big, GOLD,
                                [(x, band_y - dr + 1),
                                 (x + dr - 1, band_y),
                                 (x, band_y + dr - 1),
                                 (x - dr + 1, band_y)], max(1, s(1) // 2))
            # centre dot
            aa_circle(big, GOLD_HI, x, band_y, max(1, s(1) // 2))
            # connecting curve to next motif (sine ripple)
            if j < n_motifs - 1:
                t2 = (j + 1.5) / n_motifs
                x2 = cx - half + s(3) + span * t2
                # curve points between
                cn = 8
                curve_pts = []
                for ck in range(cn + 1):
                    ct = ck / cn
                    cxp = x + (x2 - x) * ct
                    cyp = band_y + math.sin(ct * math.pi) * s(2)
                    curve_pts.append((cxp, cyp))
                pygame.draw.lines(big, GOLD_DK, False, curve_pts,
                                  max(2, s(1)))
                pygame.draw.lines(big, GOLD, False, curve_pts,
                                  max(1, s(1) // 2))

    draw_arabesque_row(anc["y_shoulder"] + s(4), 5)
    draw_arabesque_row(anc["y_belly"], 6)
    draw_arabesque_row(anc["y_body_bot"] - s(3), 5)

    # Vertical gold pin-stripes connecting the rows on left + right
    for sign in (-1, 1):
        pts = []
        for ky in range(20):
            t = ky / 19.0
            y = anc["y_shoulder"] + s(4) + t * (
                anc["y_body_bot"] - s(3) - (anc["y_shoulder"] + s(4)))
            half = half_at(y)
            x = cx + sign * (half - s(5))
            pts.append((x, y))
        pygame.draw.lines(big, GOLD_DK, False, pts, max(2, s(1)))
        pygame.draw.lines(big, GOLD, False, pts, max(1, s(1) // 2))

    # Centre emerald gem on belly
    gem_round(big, cx, anc["y_belly"], s(3) + s(1) // 2,
              EMERALD, EMERALD_HI)
    # Tiny gold burst around the emerald
    for ang_deg in (45, 135, 225, 315):
        ang = math.radians(ang_deg)
        x1 = cx + math.cos(ang) * s(6)
        y1 = anc["y_belly"] + math.sin(ang) * s(6)
        x2 = cx + math.cos(ang) * s(8)
        y2 = anc["y_belly"] + math.sin(ang) * s(8)
        pygame.draw.line(big, GOLD,
                         (x1, y1), (x2, y2), max(2, s(1) // 2 + 1))

    # Gold neck collar (3-layer)
    n_top = anc["y_neck_bot"] - s(1)
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - anc["neck_half"] - s(3), n_top - s(3),
                      anc["neck_half"] * 2 + s(6), s(7)))
    pygame.draw.rect(big, GOLD_DK,
                     (cx - anc["neck_half"] - s(2), n_top - s(3),
                      anc["neck_half"] * 2 + s(4), s(6)))
    pygame.draw.rect(big, GOLD,
                     (cx - anc["neck_half"] - s(2), n_top - s(2),
                      anc["neck_half"] * 2 + s(4), s(4)))
    pygame.draw.line(big, GOLD_HI,
                     (cx - anc["neck_half"] - s(1), n_top - s(1)),
                     (cx + anc["neck_half"] + s(1), n_top - s(1)),
                     max(1, s(1) // 2))

    # Twin gold tassel cords tied around the neck
    cord_y = n_top + s(4)
    cord_loop_w = s(11)
    # central knot
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - s(2) - s(1) // 2, cord_y - s(1) - s(1) // 2,
                      s(4) + s(1), s(3) + s(1)))
    pygame.draw.rect(big, GOLD,
                     (cx - s(2), cord_y - s(1), s(4), s(3)))
    # cords wrapping around (curves)
    for sign in (-1, 1):
        for k in range(3):
            t = k / 2.0
            x_st = cx + sign * (s(2))
            x_end = cx + sign * (anc["neck_half"] + s(1))
            # curve down + outward
            curve = []
            for cj in range(10):
                ct = cj / 9.0
                xp = x_st + (x_end - x_st) * ct
                yp = cord_y + math.sin(ct * math.pi * 0.6) * s(1)
                curve.append((xp, yp))
            pygame.draw.lines(big, GOLD, False, curve, max(2, s(1) // 2 + 1))

    # Tassels hanging below the neck on both sides
    for sign in (-1, 1):
        t_top_x = cx + sign * (anc["neck_half"] + s(2))
        t_top_y = cord_y + s(2)
        t_bot_x = cx + sign * (anc["neck_half"] + s(5))
        t_bot_y = t_top_y + s(12)
        # Rope segment
        rope_pts = []
        for k in range(8):
            t = k / 7.0
            xp = t_top_x + (t_bot_x - t_top_x) * t
            yp = t_top_y + (t_bot_y - t_top_y - s(5)) * t
            rope_pts.append((xp, yp))
        pygame.draw.lines(big, GOLD_DK, False, rope_pts, max(3, s(1) + 1))
        pygame.draw.lines(big, GOLD, False, rope_pts, max(2, s(1)))
        # Tassel bell (gold trapezoid)
        bell_top = (rope_pts[-1][0], rope_pts[-1][1])
        bw = s(4)
        bh = s(6)
        pygame.draw.polygon(big, NEAR_BLK,
                            [(bell_top[0] - bw // 2 - s(1) // 3,
                              bell_top[1] + s(1) // 3),
                             (bell_top[0] + bw // 2 + s(1) // 3,
                              bell_top[1] + s(1) // 3),
                             (bell_top[0] + bw // 2 - s(1) + s(1) // 3,
                              bell_top[1] + bh + s(1) // 3),
                             (bell_top[0] - bw // 2 + s(1) + s(1) // 3,
                              bell_top[1] + bh + s(1) // 3)])
        pygame.draw.polygon(big, GOLD,
                            [(bell_top[0] - bw // 2, bell_top[1]),
                             (bell_top[0] + bw // 2, bell_top[1]),
                             (bell_top[0] + bw // 2 - s(1),
                              bell_top[1] + bh),
                             (bell_top[0] - bw // 2 + s(1),
                              bell_top[1] + bh)])
        # threads
        for tdx in range(-bw // 2 + s(1), bw // 2, max(1, s(1))):
            pygame.draw.line(big, GOLD,
                             (bell_top[0] + tdx, bell_top[1] + bh),
                             (bell_top[0] + tdx, bell_top[1] + bh + s(5)),
                             max(1, s(1) // 2))

    # Foot ring with pearls
    f_y = anc["y_foot"]
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - anc["foot_half"] - s(2), f_y - s(1),
                      anc["foot_half"] * 2 + s(4), s(6)))
    pygame.draw.rect(big, GOLD_DK,
                     (cx - anc["foot_half"] - s(1), f_y - s(1),
                      anc["foot_half"] * 2 + s(2), s(5)))
    pygame.draw.rect(big, GOLD,
                     (cx - anc["foot_half"] - s(1), f_y,
                      anc["foot_half"] * 2 + s(2), s(3)))
    # Pearl dots
    for dx in range(-anc["foot_half"], anc["foot_half"] + 1, s(3)):
        aa_circle(big, (245, 240, 230), cx + dx, f_y + s(1),
                  max(1, s(1) // 2))

    # Jeweled finial stopper — gold scrollwork holding an emerald, tilted
    stop_cx = cx + s(2)
    stop_base_y = anc["y_mouth"] - s(2)
    angle = math.radians(-12)
    # Base disk
    pygame.draw.ellipse(big, NEAR_BLK,
                        (stop_cx - s(7) - s(1) // 2,
                         stop_base_y - s(3) - s(1) // 2,
                         s(14) + s(1), s(6) + s(1)))
    pygame.draw.ellipse(big, GOLD_DK,
                        (stop_cx - s(7), stop_base_y - s(3),
                         s(14), s(6)))
    pygame.draw.ellipse(big, GOLD,
                        (stop_cx - s(7) + s(1) // 2,
                         stop_base_y - s(3) + s(1) // 2,
                         s(14) - s(1), s(5) - s(1)))
    # Stem rising up at angle
    stem_top_x = stop_cx + math.cos(angle - math.pi / 2) * s(8)
    stem_top_y = stop_base_y + math.sin(angle - math.pi / 2) * s(8)
    pygame.draw.line(big, NEAR_BLK,
                     (stop_cx + s(1) // 3, stop_base_y - s(1) + s(1) // 3),
                     (stem_top_x + s(1) // 3, stem_top_y + s(1) // 3),
                     max(5, s(1) + 1))
    pygame.draw.line(big, GOLD_DK,
                     (stop_cx, stop_base_y - s(1)),
                     (stem_top_x, stem_top_y),
                     max(4, s(1) + 1))
    pygame.draw.line(big, GOLD,
                     (stop_cx - s(1) // 2, stop_base_y - s(1)),
                     (stem_top_x - s(1) // 2, stem_top_y),
                     max(2, s(1)))
    # Emerald jewel at the top of the stem
    gem_diamond(big, stem_top_x, stem_top_y - s(2), s(3),
                EMERALD, EMERALD_HI)
    # Two side curls on the stopper base
    for sign in (-1, 1):
        curl_pts = []
        for k in range(8):
            t = k / 7.0
            cxp = stop_cx + sign * (s(2) + math.sin(t * math.pi) * s(2))
            cyp = stop_base_y - s(2) - t * s(5)
            curl_pts.append((cxp, cyp))
        pygame.draw.lines(big, GOLD_DK, False, curl_pts, max(2, s(1)))
        pygame.draw.lines(big, GOLD, False, curl_pts, max(1, s(1) // 2))

    # Smoke escaping
    smoke_origin_x = cx - s(3)
    smoke_origin_y = anc["y_mouth"] - s(1)
    smoke_ribbon(big, smoke_origin_x, smoke_origin_y, SMOKE,
                 n_puffs=14, height_n=42, curl=2.0, start_radius=4)

    sparkles_around(big, stem_top_x, stem_top_y, n=6, radius_n=18,
                    color=(255, 245, 200), rng_seed=22)
    sparkles_around(big, cx, cy - s(2), n=5, radius_n=42,
                    color=(235, 220, 255), rng_seed=27)


# ─────────────────────────────────────────────────────────────────────
# Variant 3 — Apothecary Antique. Aged emerald-green glass, parchment
# label with calligraphy, red wax seal, brass chain dangling from neck.
# ─────────────────────────────────────────────────────────────────────

def draw_bottle_3_apothecary(big, cx, cy):
    pal = {
        "dk":    ( 14,  60,  40),
        "base":  ( 40, 115,  70),
        "hi":    (160, 215, 175),
        "sheen": (235, 255, 240),
    }
    BRASS    = (185, 145,  60)
    BRASS_HI = (240, 215, 145)
    BRASS_DK = (115,  85,  35)
    PARCH    = (235, 215, 165)
    PARCH_HI = (255, 240, 200)
    PARCH_DK = (170, 150, 100)
    INK      = ( 80,  45,  20)
    WAX      = (175,  35,  35)
    WAX_HI   = (220,  90,  90)
    CORK     = (155,  95,  45)
    CORK_HI  = (215, 160,  95)
    SMOKE    = [(220, 240, 220), (175, 215, 180), (110, 175, 130),
                ( 60, 130,  90)]

    silhouette, anc = bottle_silhouette(cx, cy)
    paint_glass_body(big, silhouette, anc, pal)
    paint_internal_swirl(big, silhouette, anc, SMOKE,
                         star_color=(255, 240, 200), star_count=10)

    half_at = anc["half_at"]

    # Brass neck collar
    n_top = anc["y_neck_bot"] - s(1)
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - anc["neck_half"] - s(2), n_top - s(2),
                      anc["neck_half"] * 2 + s(4), s(6)))
    pygame.draw.rect(big, BRASS_DK,
                     (cx - anc["neck_half"] - s(1), n_top - s(2),
                      anc["neck_half"] * 2 + s(2), s(5)))
    pygame.draw.rect(big, BRASS,
                     (cx - anc["neck_half"] - s(1), n_top - s(1),
                      anc["neck_half"] * 2 + s(2), s(3)))
    pygame.draw.line(big, BRASS_HI,
                     (cx - anc["neck_half"], n_top),
                     (cx + anc["neck_half"], n_top),
                     max(1, s(1) // 2))

    # Parchment label across the belly — gentle curved rectangle
    # with torn edges, calligraphy script lines, ink border, and a
    # red wax seal at the bottom.
    lbl_top_y = anc["y_belly"] - s(8)
    lbl_bot_y = anc["y_belly"] + s(10)
    # Compute body half at top + bottom of label
    half_top = half_at(lbl_top_y)
    half_bot = half_at(lbl_bot_y)
    lbl_pad = s(3)
    # Label silhouette — slightly torn edges (jaggy left edge)
    label_pts = [
        (cx - half_top + lbl_pad, lbl_top_y),
        (cx - half_top + lbl_pad - s(1), lbl_top_y + s(2)),
        (cx - half_top + lbl_pad,     lbl_top_y + s(5)),
        (cx - half_top + lbl_pad - s(1), lbl_top_y + s(8)),
        (cx - (half_top + half_bot) // 2 + lbl_pad,
         (lbl_top_y + lbl_bot_y) // 2),
        (cx - half_bot + lbl_pad - s(1), lbl_bot_y - s(4)),
        (cx - half_bot + lbl_pad, lbl_bot_y),
        (cx + half_bot - lbl_pad, lbl_bot_y),
        (cx + half_bot - lbl_pad + s(1), lbl_bot_y - s(3)),
        (cx + (half_top + half_bot) // 2 - lbl_pad,
         (lbl_top_y + lbl_bot_y) // 2),
        (cx + half_top - lbl_pad + s(1), lbl_top_y + s(5)),
        (cx + half_top - lbl_pad, lbl_top_y),
    ]
    # Shadow
    sh_pts = [(x + s(1), y + s(1)) for x, y in label_pts]
    filled_poly(big, NEAR_BLK, sh_pts)
    # Parchment darker rim
    filled_poly(big, PARCH_DK, label_pts)
    # Parchment fill
    inner = []
    for x, y in label_pts:
        dx = (x - cx) * 0.92
        dy = (y - anc["y_belly"]) * 0.92
        inner.append((cx + dx, anc["y_belly"] + dy))
    filled_poly(big, PARCH, inner)
    # Highlight crease (diagonal)
    pygame.draw.line(big, PARCH_HI,
                     (cx - half_top + lbl_pad + s(2), lbl_top_y + s(2)),
                     (cx + half_top - lbl_pad - s(2), lbl_top_y + s(4)),
                     max(1, s(1) // 2))

    # Calligraphy script lines — wavy ink strokes
    for line_y_off in (-s(3), s(0), s(3)):
        line_y = anc["y_belly"] + line_y_off
        # local label width
        local_half = (half_top + half_bot) / 2 - lbl_pad - s(1)
        # squiggle: 6 points with sine bump
        pts = []
        for k in range(10):
            t = k / 9.0
            xp = cx + (-local_half + 2 * local_half * t)
            yp = line_y + math.sin(t * math.tau * 1.3) * s(1) // 2
            pts.append((xp, yp))
        pygame.draw.lines(big, INK, False, pts, max(2, s(1) // 2 + 1))

    # Wax seal at bottom of label
    seal_cx = cx
    seal_cy = lbl_bot_y - s(2)
    seal_r = s(4)
    # outer rim (drips)
    for ang_deg in range(0, 360, 30):
        ang = math.radians(ang_deg + 10)
        x = seal_cx + math.cos(ang) * seal_r
        y = seal_cy + math.sin(ang) * seal_r
        aa_circle(big, WAX, x, y, max(2, s(1)))
    # Seal disc
    aa_circle(big, NEAR_BLK, seal_cx + s(1) // 2, seal_cy + s(1) // 2,
              seal_r + s(1))
    aa_circle(big, WAX, seal_cx, seal_cy, seal_r)
    aa_circle(big, WAX_HI, seal_cx - s(1), seal_cy - s(1),
              max(1, seal_r * 3 // 4))
    # Letter "G" stamp on the seal
    font_g = pygame.font.SysFont("Times New Roman", s(5), bold=True)
    g_surf = font_g.render("G", True, WAX)
    g_dark = font_g.render("G", True, (90, 15, 15))
    big.blit(g_dark,
             (seal_cx - g_surf.get_width() // 2 + s(1) // 4,
              seal_cy - g_surf.get_height() // 2 + s(1) // 4))
    big.blit(g_dark,
             (seal_cx - g_surf.get_width() // 2,
              seal_cy - g_surf.get_height() // 2))
    # Highlight on top-left of G
    aa_circle(big, WAX_HI, seal_cx - s(2), seal_cy - s(2),
              max(1, s(1) // 2))

    # Brass chain dangling from the neck (loops on the left side)
    chain_anchor_x = cx - anc["neck_half"] - s(1)
    chain_anchor_y = n_top + s(2)
    link_y = chain_anchor_y
    link_x = chain_anchor_x
    chain_dy = s(2)
    for k in range(8):
        link_y_new = chain_anchor_y + s(2) + k * chain_dy
        link_x_new = chain_anchor_x - s(2) - math.sin(k * 0.9) * s(2)
        # link ellipse
        pygame.draw.ellipse(big, NEAR_BLK,
                            (link_x_new - s(2) - s(1) // 2,
                             link_y_new - s(1) - s(1) // 2,
                             s(4) + s(1), s(2) + s(1)))
        pygame.draw.ellipse(big, BRASS_DK,
                            (link_x_new - s(2),
                             link_y_new - s(1),
                             s(4), s(2)))
        pygame.draw.ellipse(big, BRASS,
                            (link_x_new - s(2) + s(1) // 2,
                             link_y_new - s(1),
                             s(3), max(1, s(1))))
        link_x, link_y = link_x_new, link_y_new
    # End cap of chain — small charm
    aa_circle(big, NEAR_BLK, link_x + s(1) // 2, link_y + s(2) + s(1) // 2,
              s(2))
    aa_circle(big, BRASS, link_x, link_y + s(2), s(2))
    aa_circle(big, BRASS_HI, link_x - s(1) // 2, link_y + s(2) - s(1) // 2,
              max(1, s(1) // 2))

    # Foot ring
    f_y = anc["y_foot"]
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - anc["foot_half"] - s(2), f_y - s(1),
                      anc["foot_half"] * 2 + s(4), s(5)))
    pygame.draw.rect(big, BRASS_DK,
                     (cx - anc["foot_half"] - s(1), f_y - s(1),
                      anc["foot_half"] * 2 + s(2), s(4)))
    pygame.draw.rect(big, BRASS,
                     (cx - anc["foot_half"] - s(1), f_y,
                      anc["foot_half"] * 2 + s(2), s(2)))

    # Aged cork stopper at angle (with horizontal bands for age)
    cork_cx = cx + s(3)
    cork_cy = anc["y_mouth"] - s(5)
    cork_w = s(8)
    cork_h = s(10)
    angle = math.radians(-15)
    cork_pts = []
    for vx, vy in ((-cork_w // 2, -cork_h // 2),
                    (cork_w // 2, -cork_h // 2),
                    (cork_w // 2, cork_h // 2),
                    (-cork_w // 2, cork_h // 2)):
        rx = vx * math.cos(angle) - vy * math.sin(angle)
        ry = vx * math.sin(angle) + vy * math.cos(angle)
        cork_pts.append((cork_cx + rx, cork_cy + ry))
    filled_poly(big, NEAR_BLK,
                [(x + s(1), y + s(1)) for x, y in cork_pts])
    filled_poly(big, CORK, cork_pts)
    # Horizontal aging band
    band_pts_a = []
    band_pts_b = []
    for vx, vy in ((-cork_w // 2, -cork_h // 6),
                    (cork_w // 2, -cork_h // 6)):
        rx = vx * math.cos(angle) - vy * math.sin(angle)
        ry = vx * math.sin(angle) + vy * math.cos(angle)
        band_pts_a.append((cork_cx + rx, cork_cy + ry))
    for vx, vy in ((-cork_w // 2, cork_h // 6),
                    (cork_w // 2, cork_h // 6)):
        rx = vx * math.cos(angle) - vy * math.sin(angle)
        ry = vx * math.sin(angle) + vy * math.cos(angle)
        band_pts_b.append((cork_cx + rx, cork_cy + ry))
    pygame.draw.line(big, (95, 55, 25),
                     band_pts_a[0], band_pts_a[1], max(2, s(1) // 2 + 1))
    pygame.draw.line(big, (95, 55, 25),
                     band_pts_b[0], band_pts_b[1], max(2, s(1) // 2 + 1))
    # Top highlight on cork
    hi_pts = []
    for vx, vy in ((-cork_w // 2 + s(1), -cork_h // 2 + s(1)),
                    (cork_w // 2 - s(1), -cork_h // 2 + s(1)),
                    (cork_w // 2 - s(1), -cork_h // 4),
                    (-cork_w // 2 + s(1), -cork_h // 4)):
        rx = vx * math.cos(angle) - vy * math.sin(angle)
        ry = vx * math.sin(angle) + vy * math.cos(angle)
        hi_pts.append((cork_cx + rx, cork_cy + ry))
    filled_poly(big, CORK_HI, hi_pts)

    # Smoke escaping
    smoke_origin_x = cx - s(2)
    smoke_origin_y = anc["y_mouth"] - s(1)
    smoke_ribbon(big, smoke_origin_x, smoke_origin_y, SMOKE,
                 n_puffs=13, height_n=38, curl=1.6, start_radius=4)

    sparkles_around(big, cork_cx, cork_cy, n=4, radius_n=14,
                    color=(255, 245, 200), rng_seed=23)


# ─────────────────────────────────────────────────────────────────────
# Variant 4 — Faceted Crystal. Pale-cyan cut-glass with visible
# diamond facets across the body, multi-gem stopper, gold rim,
# heavy sparkle ring.
# ─────────────────────────────────────────────────────────────────────

def draw_bottle_4_faceted(big, cx, cy):
    pal = {
        "dk":    ( 60, 130, 170),
        "base":  (130, 195, 220),
        "hi":    (220, 245, 255),
        "sheen": (255, 255, 255),
    }
    GOLD     = (255, 220, 110)
    GOLD_HI  = (255, 245, 175)
    GOLD_DK  = (180, 130,  40)
    RUBY     = (220,  55,  75)
    RUBY_HI  = (255, 175, 195)
    EMERALD  = ( 70, 175, 110)
    EMERALD_HI = (180, 240, 200)
    SAPPHIRE = ( 70, 100, 220)
    SAPPHIRE_HI = (175, 200, 255)
    WHITE    = (250, 250, 250)
    SMOKE    = [WHITE, (195, 235, 255), (130, 195, 235),
                ( 75, 145, 200)]

    silhouette, anc = bottle_silhouette(cx, cy)
    paint_glass_body(big, silhouette, anc, pal)
    paint_internal_swirl(big, silhouette, anc, SMOKE,
                         star_color=WHITE, star_count=12)

    half_at = anc["half_at"]

    # Cut-crystal facets — a vertical column of LARGE diamond
    # panels down the centre of the body, flanked by smaller side
    # facets. Each facet is a full polygon outline in sheen white,
    # with a darker triangle on the lower-right half (the shadow
    # face of a cut gem), and a bright catch-light dot in the
    # upper-left quadrant. Sparse enough that the bottle reads as
    # a single crystal, not a quilt.
    facet_clip = pygame.Surface((PW, PH), pygame.SRCALPHA)

    def draw_facet(facet_cx, facet_cy, w, h):
        local_half = half_at(facet_cy)
        # Don't draw if it would clip the silhouette
        if abs(facet_cx - cx) + w // 2 > local_half - s(1):
            return
        pts = [(facet_cx, facet_cy - h // 2),
               (facet_cx + w // 2, facet_cy),
               (facet_cx, facet_cy + h // 2),
               (facet_cx - w // 2, facet_cy)]
        # Inner shadow half (lower-right triangle)
        shadow_tri = [pts[0], pts[1], pts[2]]
        pygame.draw.polygon(facet_clip, (*pal["dk"], 100),
                            shadow_tri)
        # Full outline — sheen white
        pygame.draw.polygon(facet_clip, (*pal["sheen"], 250),
                            pts, max(3, s(1) + 1))
        # Inner highlight crescent (upper-left edge of light face)
        pygame.draw.line(facet_clip, (*pal["sheen"], 255),
                         pts[3], pts[0], max(2, s(1)))
        # Catch-light dot
        pygame.draw.circle(facet_clip, (255, 255, 255, 255),
                           (int(facet_cx - w // 5),
                            int(facet_cy - h // 6)),
                           max(2, s(1) + 1))

    # Central column of 3 big facets
    center_facets = [
        (cx, anc["y_shoulder"] + s(7),  s(14), s(14)),
        (cx, anc["y_belly"],            s(16), s(16)),
        (cx, anc["y_body_bot"] - s(7),  s(13), s(13)),
    ]
    # Side facets (one each side of belly), smaller
    side_facets = [
        (cx - s(12), anc["y_belly"] - s(8), s(9), s(9)),
        (cx + s(12), anc["y_belly"] - s(8), s(9), s(9)),
        (cx - s(12), anc["y_belly"] + s(8), s(9), s(9)),
        (cx + s(12), anc["y_belly"] + s(8), s(9), s(9)),
    ]
    for fcx, fcy, fw, fh in center_facets + side_facets:
        draw_facet(fcx, fcy, fw, fh)
    clip_to_body(facet_clip, silhouette)
    big.blit(facet_clip, (0, 0))

    # Bright sheen line on the upper-left curve (already from paint_glass_body)
    # add a secondary bright streak on upper-right too
    sheen_pts_r = []
    for k in range(12):
        t = k / 11.0
        y = anc["y_shoulder"] + t * (anc["y_belly"] - anc["y_shoulder"])
        half = half_at(y)
        sheen_pts_r.append((cx + half * 0.55, y))
    pygame.draw.lines(big, pal["hi"], False, sheen_pts_r,
                      max(2, s(1)))

    # Gold rim collar with double band
    n_top = anc["y_neck_bot"] - s(1)
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - anc["neck_half"] - s(3), n_top - s(3),
                      anc["neck_half"] * 2 + s(6), s(8)))
    pygame.draw.rect(big, GOLD_DK,
                     (cx - anc["neck_half"] - s(2), n_top - s(3),
                      anc["neck_half"] * 2 + s(4), s(7)))
    pygame.draw.rect(big, GOLD,
                     (cx - anc["neck_half"] - s(2), n_top - s(2),
                      anc["neck_half"] * 2 + s(4), s(5)))
    # Inner darker line (band-split)
    pygame.draw.line(big, GOLD_DK,
                     (cx - anc["neck_half"] - s(1), n_top + s(1)),
                     (cx + anc["neck_half"] + s(1), n_top + s(1)),
                     max(1, s(1) // 2))
    pygame.draw.line(big, GOLD_HI,
                     (cx - anc["neck_half"] - s(1), n_top - s(1)),
                     (cx + anc["neck_half"] + s(1), n_top - s(1)),
                     max(1, s(1) // 2))

    # Foot ring with multi-band gold + small gem dots
    f_y = anc["y_foot"]
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - anc["foot_half"] - s(2), f_y - s(1),
                      anc["foot_half"] * 2 + s(4), s(7)))
    pygame.draw.rect(big, GOLD_DK,
                     (cx - anc["foot_half"] - s(1), f_y - s(1),
                      anc["foot_half"] * 2 + s(2), s(6)))
    pygame.draw.rect(big, GOLD,
                     (cx - anc["foot_half"] - s(1), f_y,
                      anc["foot_half"] * 2 + s(2), s(4)))
    pygame.draw.line(big, GOLD_HI,
                     (cx - anc["foot_half"] + s(1), f_y + s(1)),
                     (cx + anc["foot_half"] - s(1), f_y + s(1)),
                     max(1, s(1) // 2))
    # Tiny gem accents on the foot
    for gem_x in (cx - anc["foot_half"] + s(4),
                  cx, cx + anc["foot_half"] - s(4)):
        aa_circle(big, NEAR_BLK, gem_x, f_y + s(2), max(2, s(1)))
        aa_circle(big, EMERALD, gem_x, f_y + s(2), max(1, s(1)))

    # Multi-gem stopper — gold disk holding 3 gems in a row, tilted
    stop_cx = cx + s(2)
    stop_base_y = anc["y_mouth"] - s(2)
    angle = math.radians(-10)
    # Base disk
    pygame.draw.ellipse(big, NEAR_BLK,
                        (stop_cx - s(8) - s(1) // 2,
                         stop_base_y - s(3) - s(1) // 2,
                         s(16) + s(1), s(6) + s(1)))
    pygame.draw.ellipse(big, GOLD_DK,
                        (stop_cx - s(8), stop_base_y - s(3),
                         s(16), s(6)))
    pygame.draw.ellipse(big, GOLD,
                        (stop_cx - s(8) + s(1) // 2,
                         stop_base_y - s(3) + s(1) // 2,
                         s(16) - s(1), s(5) - s(1)))
    # Top stem with 3 gems
    stem_top_x = stop_cx + math.cos(angle - math.pi / 2) * s(8)
    stem_top_y = stop_base_y + math.sin(angle - math.pi / 2) * s(8)
    pygame.draw.line(big, NEAR_BLK,
                     (stop_cx + s(1) // 3, stop_base_y - s(1) + s(1) // 3),
                     (stem_top_x + s(1) // 3, stem_top_y + s(1) // 3),
                     max(5, s(1) + 1))
    pygame.draw.line(big, GOLD_DK,
                     (stop_cx, stop_base_y - s(1)),
                     (stem_top_x, stem_top_y),
                     max(4, s(1) + 1))
    pygame.draw.line(big, GOLD,
                     (stop_cx - s(1) // 2, stop_base_y - s(1)),
                     (stem_top_x - s(1) // 2, stem_top_y),
                     max(2, s(1)))
    # Three gems clustered at top
    gem_round(big, stem_top_x - s(3), stem_top_y - s(1), s(2) + s(1) // 2,
              EMERALD, EMERALD_HI)
    gem_diamond(big, stem_top_x, stem_top_y - s(4), s(3),
                RUBY, RUBY_HI)
    gem_round(big, stem_top_x + s(3), stem_top_y - s(1), s(2) + s(1) // 2,
              SAPPHIRE, SAPPHIRE_HI)

    # Smoke
    smoke_origin_x = cx - s(3)
    smoke_origin_y = anc["y_mouth"] - s(1)
    smoke_ribbon(big, smoke_origin_x, smoke_origin_y, SMOKE,
                 n_puffs=14, height_n=44, curl=1.7, start_radius=4)

    # Heavy sparkle ring around the whole bottle
    sparkles_around(big, cx, cy, n=14, radius_n=46,
                    color=WHITE, rng_seed=14)
    sparkles_around(big, cx, cy, n=6, radius_n=38,
                    color=(255, 245, 200), rng_seed=15)
    sparkles_around(big, stem_top_x, stem_top_y, n=7, radius_n=14,
                    color=WHITE, rng_seed=17)


# ─────────────────────────────────────────────────────────────────────
# Variant 5 — Celestial Nebula. Deep cosmic navy glass, constellation
# lines etched on the surface, comet-streak stopper, bright golden
# core star INSIDE the bottle.
# ─────────────────────────────────────────────────────────────────────

def draw_bottle_5_celestial(big, cx, cy):
    pal = {
        "dk":    (  8,  10,  40),
        "base":  ( 22,  20,  78),
        "hi":    ( 90,  75, 170),
        "sheen": (220, 215, 250),
    }
    GOLD     = (255, 220, 110)
    GOLD_HI  = (255, 245, 195)
    GOLD_DK  = (180, 130,  40)
    SILVER   = (215, 220, 240)
    SILVER_HI = (250, 250, 255)
    NEBULA   = [(130,  60, 200), (220,  90, 170), ( 60, 130, 230)]
    SMOKE    = [(255, 250, 230), (220, 200, 255), (130, 110, 220),
                ( 80,  60, 180)]
    CYAN     = (175, 230, 255)
    WHITE    = (250, 250, 250)

    silhouette, anc = bottle_silhouette(cx, cy)
    paint_glass_body(big, silhouette, anc, pal)

    # Internal cosmic content — nebula clouds + many stars + bright
    # golden core star
    cosmic = pygame.Surface((PW, PH), pygame.SRCALPHA)
    rng = random.Random(9)
    # Nebula clouds
    for _ in range(10):
        nx = cx + rng.randint(-s(14), s(14))
        ny = rng.randint(anc["y_shoulder"] + s(2),
                          anc["y_body_bot"] - s(2))
        nr = rng.randint(s(3), s(7))
        col = rng.choice(NEBULA)
        sub = pygame.Surface((nr * 2 + 4, nr * 2 + 4),
                             pygame.SRCALPHA)
        pygame.draw.circle(sub, (*col, 130),
                           (nr + 2, nr + 2), nr)
        cosmic.blit(sub, (nx - nr - 2, ny - nr - 2))
    # Bright core star at the heart
    core_x = cx
    core_y = anc["y_belly"]
    for r_n, a in ((s(10), 70), (s(6), 140), (s(3), 230)):
        sub = pygame.Surface((r_n * 2 + 4, r_n * 2 + 4),
                             pygame.SRCALPHA)
        pygame.draw.circle(sub, (255, 240, 180, a),
                           (r_n + 2, r_n + 2), r_n)
        cosmic.blit(sub, (core_x - r_n - 2, core_y - r_n - 2))
    # 4-point cross around core
    for dx_, dy_ in ((s(11), 0), (-s(11), 0), (0, s(11)), (0, -s(11))):
        pygame.draw.line(cosmic, (255, 240, 180, 230),
                         (core_x, core_y),
                         (core_x + dx_, core_y + dy_),
                         max(2, s(1)))
    # Tiny stars
    for j in range(22):
        sx_p = cx + rng.randint(-s(16), s(16))
        sy_p = rng.randint(anc["y_shoulder"] + s(2),
                            anc["y_body_bot"] - s(2))
        sr = max(1, s(1) // 2 + rng.randint(0, 1))
        if j % 4 == 0:
            pygame.draw.line(cosmic, (*WHITE, 220),
                             (sx_p - sr * 3, sy_p),
                             (sx_p + sr * 3, sy_p),
                             max(1, s(1) // 3))
            pygame.draw.line(cosmic, (*WHITE, 220),
                             (sx_p, sy_p - sr * 3),
                             (sx_p, sy_p + sr * 3),
                             max(1, s(1) // 3))
        pygame.draw.circle(cosmic, (*WHITE, 240), (sx_p, sy_p), sr)
    clip_to_body(cosmic, silhouette)
    big.blit(cosmic, (0, 0))

    # Constellation lines etched on the SURFACE of the glass (drawn
    # on top, slightly transparent silver). 4 constellations of 3-4
    # silver dots connected by thin lines.
    half_at = anc["half_at"]
    constellations = [
        # (relative coords from belly)
        [(s(-12), s(-22)), (s(-7), s(-18)), (s(-10), s(-12))],
        [(s(8), s(-20)), (s(13), s(-15)), (s(11), s(-10))],
        [(s(-13), s(0)), (s(-9), s(5)), (s(-12), s(10)),
         (s(-7), s(12))],
        [(s(10), s(6)), (s(14), s(10)), (s(11), s(15))],
    ]
    for const in constellations:
        for k in range(len(const) - 1):
            x1 = cx + const[k][0]
            y1 = anc["y_belly"] + const[k][1]
            x2 = cx + const[k + 1][0]
            y2 = anc["y_belly"] + const[k + 1][1]
            pygame.draw.line(big, SILVER,
                             (x1, y1), (x2, y2), max(2, s(1) // 2 + 1))
        for px_, py_ in const:
            x = cx + px_
            y = anc["y_belly"] + py_
            aa_circle(big, SILVER_HI, x, y, max(2, s(1)))
            aa_circle(big, WHITE, x - s(1) // 2, y - s(1) // 2,
                      max(1, s(1) // 2))

    # Gold + silver layered neck collar (cosmic feel)
    n_top = anc["y_neck_bot"] - s(1)
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - anc["neck_half"] - s(3), n_top - s(3),
                      anc["neck_half"] * 2 + s(6), s(8)))
    pygame.draw.rect(big, GOLD_DK,
                     (cx - anc["neck_half"] - s(2), n_top - s(3),
                      anc["neck_half"] * 2 + s(4), s(7)))
    pygame.draw.rect(big, GOLD,
                     (cx - anc["neck_half"] - s(2), n_top - s(2),
                      anc["neck_half"] * 2 + s(4), s(4)))
    pygame.draw.rect(big, SILVER,
                     (cx - anc["neck_half"] - s(2), n_top + s(2),
                      anc["neck_half"] * 2 + s(4), s(2)))
    pygame.draw.line(big, GOLD_HI,
                     (cx - anc["neck_half"] - s(1), n_top - s(1)),
                     (cx + anc["neck_half"] + s(1), n_top - s(1)),
                     max(1, s(1) // 2))

    # Foot ring — silver + gold layered with star dots
    f_y = anc["y_foot"]
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - anc["foot_half"] - s(2), f_y - s(1),
                      anc["foot_half"] * 2 + s(4), s(7)))
    pygame.draw.rect(big, GOLD_DK,
                     (cx - anc["foot_half"] - s(1), f_y - s(1),
                      anc["foot_half"] * 2 + s(2), s(6)))
    pygame.draw.rect(big, GOLD,
                     (cx - anc["foot_half"] - s(1), f_y,
                      anc["foot_half"] * 2 + s(2), s(3)))
    pygame.draw.rect(big, SILVER,
                     (cx - anc["foot_half"] - s(1), f_y + s(3),
                      anc["foot_half"] * 2 + s(2), s(1)))
    # Tiny star dots on foot
    for dx in range(-anc["foot_half"] + s(2), anc["foot_half"],
                    max(1, s(3))):
        aa_circle(big, GOLD_HI, cx + dx, f_y + s(2),
                  max(1, s(1) // 2))

    # Comet-streak stopper — a stylized comet (gold star with silver
    # streak trail) angled out of the bottle mouth.
    stop_cx = cx + s(2)
    stop_base_y = anc["y_mouth"] - s(2)
    angle = math.radians(-22)
    # Base socket (small)
    pygame.draw.ellipse(big, NEAR_BLK,
                        (stop_cx - s(7) - s(1) // 2,
                         stop_base_y - s(2) - s(1) // 2,
                         s(14) + s(1), s(5) + s(1)))
    pygame.draw.ellipse(big, GOLD_DK,
                        (stop_cx - s(7), stop_base_y - s(2),
                         s(14), s(5)))
    pygame.draw.ellipse(big, GOLD,
                        (stop_cx - s(7) + s(1) // 2,
                         stop_base_y - s(2) + s(1) // 2,
                         s(14) - s(1), s(4) - s(1)))
    # Comet head — star with rays at the top of an angled streak
    head_dx = math.cos(angle - math.pi / 2) * s(11)
    head_dy = math.sin(angle - math.pi / 2) * s(11)
    head_x = stop_cx + head_dx
    head_y = stop_base_y + head_dy
    # streak (tapered silver trail behind the head)
    trail_pts = []
    for k in range(10):
        t = k / 9.0
        tx = stop_cx + head_dx * t
        ty = stop_base_y - s(1) + head_dy * t
        trail_pts.append((tx, ty))
    # draw trail with tapered width
    for k in range(len(trail_pts) - 1):
        t = k / (len(trail_pts) - 1)
        w = max(2, int(s(1) * 1.5 + t * s(2)))
        a = int(80 + t * 175)
        surf_l = pygame.Surface((PW, PH), pygame.SRCALPHA)
        pygame.draw.line(surf_l, (*SILVER, a),
                         trail_pts[k], trail_pts[k + 1], w)
        big.blit(surf_l, (0, 0))
    # Comet head — 4-point star
    star_r = s(5)
    star_pts = []
    for j in range(8):
        ang = j * math.pi / 4
        r = star_r if j % 2 == 0 else star_r // 2
        star_pts.append((head_x + math.cos(ang) * r,
                         head_y + math.sin(ang) * r))
    filled_poly(big, NEAR_BLK,
                [(x + s(1) // 3, y + s(1) // 3) for x, y in star_pts])
    filled_poly(big, GOLD, star_pts)
    # bright centre
    aa_circle(big, GOLD_HI, head_x, head_y, max(2, s(1) + 1))
    aa_circle(big, WHITE, head_x - s(1) // 2, head_y - s(1) // 2,
              max(1, s(1)))

    # Smoke escaping from beneath the comet
    smoke_origin_x = cx - s(4)
    smoke_origin_y = anc["y_mouth"] - s(1)
    smoke_ribbon(big, smoke_origin_x, smoke_origin_y, SMOKE,
                 n_puffs=15, height_n=44, curl=2.4, start_radius=4)

    # Outer star sparkles around the bottle
    sparkles_around(big, cx, cy, n=10, radius_n=46,
                    color=WHITE, rng_seed=14)
    sparkles_around(big, cx, cy - s(8), n=5, radius_n=38,
                    color=CYAN, rng_seed=17)
    sparkles_around(big, head_x, head_y, n=5, radius_n=12,
                    color=(255, 245, 200), rng_seed=33)


# ─────────────────────────────────────────────────────────────────────
LAMPS = [
    ("1: Royal Sapphire",       draw_bottle_1_royal_sapphire),
    ("2: Arabesque Imperial",   draw_bottle_2_arabesque),
    ("3: Apothecary Antique",   draw_bottle_3_apothecary),
    ("4: Faceted Crystal",      draw_bottle_4_faceted),
    ("5: Celestial Nebula",     draw_bottle_5_celestial),
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
    margin = 18
    label_h = 28
    small_band_h = SH + 8
    cell_h = DH + label_h + small_band_h + 8
    sheet_w = DW * cols + margin * (cols + 1)
    sheet_h = cell_h * rows + margin * (rows + 1)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 24, 32))
    font_big = pygame.font.SysFont("Arial", 20, bold=True)
    font_small = pygame.font.SysFont("Arial", 11)
    small_caption = font_small.render("in-game scale", True,
                                       (170, 180, 200))
    # Pad LAMPS so we draw the 5 variants into the 6-cell grid
    # (last cell stays empty / blue panel)
    for i in range(cols * rows):
        col, row = i % cols, i // cols
        x = margin + col * (DW + margin)
        y = margin + row * (cell_h + margin)
        if i >= len(LAMPS):
            # Empty cell — subtle filler
            pygame.draw.rect(sheet, (30, 32, 42),
                             (x - 2, y - 2, DW + 4, DH + 4))
            continue
        label, fn = LAMPS[i]
        portrait = render_one(fn, DISPLAY_BIG)
        small = render_one(fn, DISPLAY_SMALL)
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
        ind_path = os.path.join(OUT_DIR, f"bottle_{i + 1}_{tag}.png")
        pygame.image.save(portrait, ind_path)
    out = os.path.join(OUT_DIR, f"bottle_sheet_{tag}.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
