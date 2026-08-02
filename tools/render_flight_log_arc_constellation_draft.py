#!/usr/bin/env python3
"""
constellation_draft  ·  flight-log arc  ·  round 1

The day is a constellation being drawn mid-flight.
Flown region: warm gold star nodes connected by gold hairlines.
Past death: nodes are present as cool-white dim circles, but the LINES STOP COLD.
Mystery = absent connection, not hidden geometry.
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


# ── background (copied from render_flight_log_progress_sun_arc.py) ────────────
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
    START_POS   = arc_pos(0.0)
    EARLY_POS   = arc_pos(0.09)
    GEYSER_POS  = arc_pos(0.167)
    DEATH_POS   = arc_pos(0.184)

    unflown = [
        arc_pos(0.300),
        arc_pos(0.403, 163),   # CLOWN — inward 5px
        arc_pos(0.430, 173),   # RAIN  — outward 5px
        arc_pos(0.620),
        arc_pos(0.820),
        arc_pos(1.0),          # DAY COMPLETE
    ]

    # ── Step 2: unflown nodes (draw first, below flown layer) ─────────────────
    for i, (x, y) in enumerate(unflown):
        is_end = (i == len(unflown) - 1)
        r = 4 if is_end else 3
        if is_end:
            # Faint dim-gold keyline ring around DAY COMPLETE node
            pygame.draw.circle(surf, (80, 65, 20), (int(x), int(y)), 6, 2)
        lay = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(lay, (214, 226, 248, 190), (r + 1, r + 1), r)
        surf.blit(lay, (int(x) - r - 1, int(y) - r - 1))

    # ── Step 3: NEWBIE lasso (dotted arc boundary around opening cluster) ──────
    # Arc spans angle 180° (start) down to death_angle_deg ≈ 120.3°
    death_angle_deg = math.degrees(arc_angle(0.184))
    start_angle_deg = 180.0
    angle_span_deg  = start_angle_deg - death_angle_deg   # ≈ 59.7°

    for lasso_r in (182, 154):
        arc_len = math.radians(angle_span_deg) * lasso_r
        num_dots = max(2, int(arc_len / 6))
        for k in range(num_dots):
            t = k / num_dots
            a_deg = start_angle_deg - t * angle_span_deg
            a     = math.radians(a_deg)
            x = CX + lasso_r * math.cos(a)
            y = CY - lasso_r * math.sin(a)
            if 0 <= x < W and 0 <= y < H:
                lay = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(lay, (200, 180, 120, 150), (3, 3), 2)
                surf.blit(lay, (int(x) - 3, int(y) - 3))

    # Bracket foot at the START end — a few dots bridging outer→inner at 180°
    foot_a = math.radians(180.0)
    sx_out = CX + 182 * math.cos(foot_a)
    sy_out = CY - 182 * math.sin(foot_a)
    sx_in  = CX + 154 * math.cos(foot_a)
    sy_in  = CY - 154 * math.sin(foot_a)
    for k in range(5):
        t  = k / 4
        bx = sx_out + (sx_in - sx_out) * t
        by = sy_out + (sy_in - sy_out) * t
        if 0 <= bx < W and 0 <= by < H:
            lay = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(lay, (200, 180, 120, 150), (3, 3), 2)
            surf.blit(lay, (int(bx) - 3, int(by) - 3))

    # ── Step 4: gold hairline chain — flown arc p=0 → p=0.184 only ────────────
    chain_pts = []
    for i in range(101):
        p = 0.184 * i / 100
        x, y = arc_pos(p)
        chain_pts.append((int(x), int(y)))
    if len(chain_pts) >= 2:
        pygame.draw.lines(surf, GOLD, False, chain_pts, 2)

    # ── Step 5: flown star nodes at START, EARLY, GEYSER ─────────────────────
    for (x, y) in (START_POS, EARLY_POS, GEYSER_POS):
        cx, cy = int(x), int(y)
        # INK keyline polygon (1px larger radii)
        ink_pts = []
        for i in range(8):
            angle = math.radians(i * 45)
            rk = 6 if i % 2 == 0 else 3
            ink_pts.append((int(cx + rk * math.cos(angle)),
                            int(cy - rk * math.sin(angle))))
        pygame.draw.polygon(surf, INK, ink_pts)
        draw_star(surf, cx, cy)

    # ── Step 6: death chain terminus ─────────────────────────────────────────
    dx, dy = int(DEATH_POS[0]), int(DEATH_POS[1])

    # Keyline then gold disc
    pygame.draw.circle(surf, INK, (dx, dy), 6)
    pygame.draw.circle(surf, GOLD, (dx, dy), 4)

    # Short fading stub extending the chain forward from the terminus
    eps = 0.002
    tx0, ty0 = arc_pos(max(0.0, 0.184 - eps))
    tx1, ty1 = arc_pos(min(1.0, 0.184 + eps))
    tlen = math.hypot(tx1 - tx0, ty1 - ty0)
    if tlen > 0:
        tfx, tfy = (tx1 - tx0) / tlen, (ty1 - ty0) / tlen
    else:
        tfx, tfy = 1.0, 0.0

    stub_lay = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(9):
        alpha = int(200 * (1 - i / 8))
        px = int(dx + tfx * i)
        py = int(dy + tfy * i)
        if alpha > 0 and 0 <= px < W and 0 <= py < H:
            pygame.draw.circle(stub_lay, (*GOLD, alpha), (px, py), 1)
    surf.blit(stub_lay, (0, 0))

    # Small 4-point star marks the exact terminus
    draw_star(surf, dx, dy, r_long=4, r_short=1)

    # ── Step 7: GEYSER label ─────────────────────────────────────────────────
    gx, gy = GEYSER_POS
    gux, guy = radial_unit(0.167)
    lead = 18
    lx = int(gx + gux * lead)
    ly = int(gy + guy * lead)
    # Leader line from node to label anchor
    pygame.draw.line(surf, GOLD, (int(gx), int(gy)), (lx, ly), 1)
    draw_text(surf, "GEYSER", 9, color=CREAM, midleft=(lx + 2, ly))

    # ── Step 8: chain terminus label "ENDED HERE" ─────────────────────────────
    # Short gold leader from death node to text
    elx = dx + 14
    ely = dy - 16
    pygame.draw.line(surf, GOLD, (dx, dy), (elx, ely), 1)
    draw_text(surf, "ENDED HERE", 8, color=CREAM, midleft=(elx + 2, ely))

    # ── Step 9: chrome ───────────────────────────────────────────────────────
    # Header band — solid INK with a short downward fade
    pygame.draw.rect(surf, INK, (0, 0, W, 80))
    fade = pygame.Surface((W, 12), pygame.SRCALPHA)
    for i in range(12):
        a = int(220 * (1 - i / 12) ** 1.4)
        fade.fill((*INK, a), pygame.Rect(0, i, W, 1))
    surf.blit(fade, (0, 80))

    # "FLIGHT LOG" headline
    draw_text(surf, "FLIGHT LOG", 16, color=GOLD,
              center=(W // 2, 28), shadow=False)

    # Run metadata
    draw_text(surf, "DAY 1  ·  PILLAR 25  ·  0:47", 11,
              color=CREAM, center=(W // 2, 50), shadow=False)

    # Percentage line
    draw_text(surf, "18.4% OF THE DAY FLOWN", 9, color=GOLD,
              center=(W // 2, 70), shadow=False)

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
                            "constellation_draft", "round_1.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pygame.image.save(surf, out_path)
    loaded = pygame.image.load(out_path)
    print(f"saved {out_path}  size={loaded.get_size()}")
    assert loaded.get_size() == (360, 640), f"unexpected size {loaded.get_size()}"


if __name__ == "__main__":
    main()
