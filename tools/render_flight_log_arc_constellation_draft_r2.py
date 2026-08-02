#!/usr/bin/env python3
"""
constellation_draft  ·  flight-log arc  ·  round 2  (re-roll)

Changes from round 1:
- Unflown nodes: hollow ink rings instead of filled cool-white dots
- Flown chain: 3px + soft bloom on SRCALPHA surface
- Fewer flown nodes: START, GEYSER, death terminus only (drop EARLY)
- GEYSER: 4-point gold star (8px) with leader label at R=186
- Death terminus: 5px GOLD circle + 4px INK keyline + 6-step fading stub
- NEWBIE lasso pulled inward (R=176 outer, R=156 inner)
- DAY COMPLETE: hollow ring + 2px GOLD outer ring
- Lighter header: 66px fade band, single metadata line, GOLD rule
"""
import os
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

ROOT = "/home/user/skybit"
FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"

W, H = 360, 640

# ── palette ───────────────────────────────────────────────────────────────────
INK   = (6, 8, 14)
GOLD  = (255, 206, 92)
CREAM = (246, 240, 230)
COOL  = (150, 168, 196)

# ── arc geometry ──────────────────────────────────────────────────────────────
CX, CY  = 180, 430
R       = 168
EASE_P  = 0.652


def ease(p):
    return max(0.0, min(1.0, p)) ** EASE_P


def arc_angle(p):
    return math.pi * (1.0 - ease(p))


def arc_pos(p, radius=R):
    a = arc_angle(p)
    return (CX + radius * math.cos(a), CY - radius * math.sin(a))


def radial_unit(p):
    """Outward-pointing unit vector at phase p, screen coords (y down)."""
    a = arc_angle(p)
    return (math.cos(a), -math.sin(a))


# ── font helper ───────────────────────────────────────────────────────────────
_fonts: dict = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


def draw_text(surf, s, size, color=CREAM, center=None, midleft=None,
              shadow=True):
    f = font(size)
    img = f.render(s, True, color)
    rect = img.get_rect()
    if center:
        rect.center = center
    elif midleft:
        rect.midleft = midleft
    if shadow:
        sh = pygame.Surface(img.get_size(), pygame.SRCALPHA)
        sh.blit(img, (0, 0))
        sh.fill((0, 0, 0, 190), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(sh, (rect.x + 1, rect.y + 1))
    surf.blit(img, rect)
    return rect


# ── background ────────────────────────────────────────────────────────────────
def build_skybit_bg(w=360, h=640):
    surf = pygame.Surface((w, h))
    sky_bot_y = int(h * 0.62)
    for y in range(sky_bot_y):
        t = y / sky_bot_y
        c = (
            int(8  + (18 - 8)  * t),
            int(12 + (40 - 12) * t),
            int(40 + (90 - 40) * t),
        )
        pygame.draw.line(surf, c, (0, y), (w - 1, y))
    for y in range(sky_bot_y, h):
        pygame.draw.line(surf, (10, 16, 48), (0, y), (w - 1, y))
    rng = random.Random(20260801)
    star_zone = int(h * 0.55)
    for _ in range(40):
        sx, sy = rng.randrange(w), rng.randrange(star_zone)
        a = rng.randint(100, 210)
        r = 1 if rng.random() < 0.8 else 2
        lay = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(lay, (220, 230, 255, a), (r + 1, r + 1), r)
        surf.blit(lay, (sx - r - 1, sy - r - 1))
    far_y = int(h * 0.60)
    pts_far = [(0, h)]
    for x in range(0, w + 1, 3):
        offs = (math.sin(x * 0.022 + 1.4) * 28 + math.sin(x * 0.041 + 0.6) * 14)
        pts_far.append((x, far_y + int(offs)))
    pts_far.append((w, h))
    pygame.draw.polygon(surf, (35, 45, 100), pts_far)
    near_y = int(h * 0.70)
    pts_near = [(0, h)]
    for x in range(0, w + 1, 3):
        offs = (math.sin(x * 0.033 + 2.1) * 22 + math.sin(x * 0.058 + 1.0) * 10)
        pts_near.append((x, near_y + int(offs)))
    pts_near.append((w, h))
    pygame.draw.polygon(surf, (22, 30, 72), pts_near)
    return surf


# ── 4-point star glyph ────────────────────────────────────────────────────────
def draw_star(surf, cx, cy, r_long=5, r_short=2, color=GOLD):
    pts = []
    for i in range(8):
        angle = math.radians(i * 45)
        r = r_long if i % 2 == 0 else r_short
        pts.append((cx + r * math.cos(angle), cy - r * math.sin(angle)))
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])
    pygame.draw.circle(surf, (255, 255, 255), (int(cx), int(cy)), 1)


def main():
    # Step 1: base background
    surf = build_skybit_bg(W, H)

    # ── precompute node positions ─────────────────────────────────────────────
    START_POS  = arc_pos(0.0)
    GEYSER_POS = arc_pos(0.167)
    DEATH_POS  = arc_pos(0.184)

    # Unflown nodes (draw below flown layer)
    unflown = [
        (arc_pos(0.300),       False, ""),          # unnamed intermediate
        (arc_pos(0.403, 163),  False, "CLOWN"),     # inward 5px
        (arc_pos(0.430, 173),  False, "RAIN"),      # outward 5px
        (arc_pos(0.620),       False, ""),           # unnamed intermediate
        (arc_pos(0.820),       False, "SNOWSTORM"),
        (arc_pos(1.0),         True,  "DAY COMPLETE"),  # special
    ]

    # ── Step 2: unflown nodes — hollow ink rings ──────────────────────────────
    # Draw on a SRCALPHA surface for alpha on the keyline
    node_lay = pygame.Surface((W, H), pygame.SRCALPHA)

    for (x, y), is_end, label in unflown:
        ix, iy = int(x), int(y)

        if is_end:
            # DAY COMPLETE: hollow ring (r=6, 2px COOL) + 1px INK keyline + 2px GOLD outer ring
            pygame.draw.circle(node_lay, (*GOLD, 255), (ix, iy), 9, 2)      # 2px GOLD outer
            pygame.draw.circle(node_lay, (*INK, 120), (ix, iy), 7, 1)       # 1px INK keyline
            pygame.draw.circle(node_lay, (*COOL, 255), (ix, iy), 6, 2)      # 2px COOL inner ring
        else:
            # Standard hollow ring: COOL ring + faint INK keyline
            pygame.draw.circle(node_lay, (*COOL, 255), (ix, iy), 5, 2)      # empty ring
            pygame.draw.circle(node_lay, (*INK, 120), (ix, iy), 6, 1)       # 1px darker outer keyline

    surf.blit(node_lay, (0, 0))

    # ── Step 3: NEWBIE lasso — pulled inward (R=176 outer, R=156 inner) ───────
    death_angle_deg = math.degrees(arc_angle(0.184))
    start_angle_deg = 180.0
    angle_span_deg  = start_angle_deg - death_angle_deg   # ~59.7°

    lasso_lay = pygame.Surface((W, H), pygame.SRCALPHA)

    for lasso_r in (176, 156):
        arc_len = math.radians(angle_span_deg) * lasso_r
        num_dots = max(2, int(arc_len / 6))
        for k in range(num_dots):
            t = k / num_dots
            a_deg = start_angle_deg - t * angle_span_deg
            a     = math.radians(a_deg)
            x = CX + lasso_r * math.cos(a)
            y = CY - lasso_r * math.sin(a)
            if 0 <= x < W and 0 <= y < H:
                pygame.draw.circle(lasso_lay, (200, 180, 120, 150), (int(x), int(y)), 2)

    # Bracket foot at START end — bridge outer to inner at 180°
    foot_a = math.radians(180.0)
    sx_out = CX + 176 * math.cos(foot_a)
    sy_out = CY - 176 * math.sin(foot_a)
    sx_in  = CX + 156 * math.cos(foot_a)
    sy_in  = CY - 156 * math.sin(foot_a)
    for k in range(5):
        t  = k / 4
        bx = sx_out + (sx_in - sx_out) * t
        by = sy_out + (sy_in - sy_out) * t
        if 0 <= bx < W and 0 <= by < H:
            pygame.draw.circle(lasso_lay, (200, 180, 120, 150), (int(bx), int(by)), 2)

    surf.blit(lasso_lay, (0, 0))

    # NEWBIE label — inside the lasso at R=162, in the upper arc zone
    # Upper zone is around p=0.09 (midpoint of the flown arc span)
    lasso_label_a = math.radians(start_angle_deg - 0.5 * angle_span_deg)
    nlx = int(CX + 162 * math.cos(lasso_label_a))
    nly = int(CY - 162 * math.sin(lasso_label_a))
    draw_text(surf, "NEWBIE", 9, color=(200, 180, 120), center=(nlx, nly))

    # ── Step 4: gold chain with bloom — flown arc p=0 → p=0.184 ──────────────
    chain_pts = []
    for i in range(101):
        p = 0.184 * i / 100
        x, y = arc_pos(p)
        chain_pts.append((int(x), int(y)))

    if len(chain_pts) >= 2:
        # Bloom pass: 6px stroke at alpha 60 on SRCALPHA surface
        bloom_lay = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.lines(bloom_lay, (*GOLD, 60), False, chain_pts, 6)
        surf.blit(bloom_lay, (0, 0))
        # Solid chain on top: 3px
        pygame.draw.lines(surf, GOLD, False, chain_pts, 3)

    # ── Step 5: flown star nodes — START and GEYSER only (drop EARLY) ─────────
    # START node — standard star
    sx, sy = int(START_POS[0]), int(START_POS[1])
    ink_pts = []
    for i in range(8):
        angle = math.radians(i * 45)
        rk = 6 if i % 2 == 0 else 3
        ink_pts.append((int(sx + rk * math.cos(angle)),
                        int(sy - rk * math.sin(angle))))
    pygame.draw.polygon(surf, INK, ink_pts)
    draw_star(surf, sx, sy)

    # GEYSER node — 4-point gold star, 8px (r_long=8), with INK keyline polygon
    gx, gy = int(GEYSER_POS[0]), int(GEYSER_POS[1])
    ink_pts_g = []
    for i in range(8):
        angle = math.radians(i * 45)
        rk = 9 if i % 2 == 0 else 4
        ink_pts_g.append((int(gx + rk * math.cos(angle)),
                          int(gy - rk * math.sin(angle))))
    pygame.draw.polygon(surf, INK, ink_pts_g)
    draw_star(surf, gx, gy, r_long=8, r_short=3)

    # ── Step 6: death chain terminus ─────────────────────────────────────────
    dx, dy = int(DEATH_POS[0]), int(DEATH_POS[1])

    # 5px GOLD circle with 4px INK keyline (keyline drawn as outer ring first)
    pygame.draw.circle(surf, INK, (dx, dy), 7)      # INK keyline backing
    pygame.draw.circle(surf, GOLD, (dx, dy), 5)     # 5px GOLD circle

    # 6-step alpha-fading stub in the arc tangent direction
    eps = 0.002
    tx0, ty0 = arc_pos(max(0.0, 0.184 - eps))
    tx1, ty1 = arc_pos(min(1.0, 0.184 + eps))
    tlen = math.hypot(tx1 - tx0, ty1 - ty0)
    if tlen > 0:
        tfx, tfy = (tx1 - tx0) / tlen, (ty1 - ty0) / tlen
    else:
        tfx, tfy = 1.0, 0.0

    stub_lay = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(6):
        alpha = int(200 * (1 - i / 5))
        px = int(dx + tfx * (i + 1) * 2)
        py = int(dy + tfy * (i + 1) * 2)
        if alpha > 0 and 0 <= px < W and 0 <= py < H:
            pygame.draw.circle(stub_lay, (*GOLD, alpha), (px, py), 1)
    surf.blit(stub_lay, (0, 0))

    # ── Step 7: GEYSER label — leader at R=186, pulled outward ───────────────
    gfx, gfy = radial_unit(0.167)
    # Leader endpoint at R=186
    lead_r = 186
    a_geyser = arc_angle(0.167)
    lx = int(CX + lead_r * math.cos(a_geyser))
    ly = int(CY - lead_r * math.sin(a_geyser))
    pygame.draw.line(surf, GOLD, (gx, gy), (lx, ly), 1)
    draw_text(surf, "GEYSER", 9, color=CREAM, midleft=(lx + 2, ly))

    # ── Step 8: ENDED HERE label near death terminus ──────────────────────────
    elx = dx + 14
    ely = dy - 16
    pygame.draw.line(surf, GOLD, (dx, dy), (elx, ely), 1)
    draw_text(surf, "ENDED HERE", 8, color=CREAM, midleft=(elx + 2, ely))

    # ── Step 9: chrome — lighter 66px fade header ────────────────────────────
    # Fade from (6,8,14,200) at y=0 to transparent at y=66
    header_lay = pygame.Surface((W, 66), pygame.SRCALPHA)
    for yi in range(66):
        t = yi / 66.0
        a = int(200 * (1.0 - t) ** 1.2)
        if a > 0:
            header_lay.fill((*INK, a), pygame.Rect(0, yi, W, 1))
    surf.blit(header_lay, (0, 0))

    # "FLIGHT LOG" 16px GOLD at y=28
    draw_text(surf, "FLIGHT LOG", 16, color=GOLD,
              center=(W // 2, 28), shadow=False)

    # Metadata 11px CREAM at y=50
    draw_text(surf, "DAY 1  ·  PILLAR 25  ·  0:47  ·  18.4%", 11,
              color=CREAM, center=(W // 2, 50), shadow=False)

    # 1px GOLD rule at y=66
    pygame.draw.line(surf, GOLD, (0, 66), (W - 1, 66), 1)

    # BACK button — 80×28 pill, dark fill, 2px gold border
    btn_rect = pygame.Rect(0, 0, 80, 28)
    btn_rect.center = (180, 610)
    btn_surf = pygame.Surface((80, 28), pygame.SRCALPHA)
    pygame.draw.rect(btn_surf, (30, 20, 10, 255), btn_surf.get_rect(),
                     border_radius=14)
    pygame.draw.rect(btn_surf, (*GOLD, 255), btn_surf.get_rect(),
                     width=2, border_radius=14)
    surf.blit(btn_surf, btn_rect.topleft)
    draw_text(surf, "BACK", 11, color=GOLD, center=(180, 610), shadow=False)

    # ── save ─────────────────────────────────────────────────────────────────
    out_path = os.path.join(ROOT, "docs", "flight_log_arc",
                            "constellation_draft", "round_2.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pygame.image.save(surf, out_path)
    loaded = pygame.image.load(out_path)
    print(f"saved {out_path}  size={loaded.get_size()}")
    assert loaded.get_size() == (360, 640), f"unexpected size {loaded.get_size()}"


if __name__ == "__main__":
    main()
