#!/usr/bin/env python3
"""
sealed_horizon  ·  flight-log arc  ·  round 2

Round 2 art-director fixes applied:
  Fix 1 — warm flown interior (42,38,60) vs cold sealed flap (12,16,40)
  Fix 2 — tear is hero: 4px full-opacity cream, gold node at death position
  Fix 3 — GEYSER placed via arc_pos(0.167) on the band centerline
  Fix 4 — wax seals dimmed to bronze; DAY COMPLETE slightly brighter
  Fix 5 — dark header band with FLIGHT LOG / sub-header / 1px rule; callout removed
"""
import os
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

W, H = 360, 640
CX, CY = 180, 430
R = 168
R_INNER = 163
R_OUTER = 173
EASE_P = 0.652
DEATH_P = 0.184

ROOT = "/home/user/skybit"
FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"

INK   = (6,   8,  14)
GOLD  = (255, 206, 92)
CREAM = (246, 240, 230)

# Fix 4 bronze palette
BRONZE_SEAL     = (150, 112,  52)   # regular wax seals
BRONZE_SEAL_RIM = (184, 140,  58)   # unchanged rim
BRONZE_DAY      = (180, 135,  65)   # DAY COMPLETE seal (slightly brighter)

_fonts: dict = {}


def font(size: int) -> pygame.font.Font:
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


# ── single phase → screen mapping ──────────────────────────────────────────────

def ease(p: float) -> float:
    return max(0.0, min(1.0, p)) ** EASE_P


def arc_angle(p: float) -> float:
    """Phase → arc angle in radians. p=0 → π (180°), p=1 → 0°."""
    return math.pi * (1.0 - ease(p))


def arc_pos(p: float, radius: float = R):
    a = arc_angle(p)
    return (CX + radius * math.cos(a), CY - radius * math.sin(a))


def radial_unit(p: float):
    """Outward-pointing unit vector at phase p, screen coords (y down)."""
    a = arc_angle(p)
    return (math.cos(a), -math.sin(a))


# ── build_skybit_bg ─────────────────────────────────────────────────────────────

def build_skybit_bg(w: int = 360, h: int = 640) -> pygame.Surface:
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
        offs = math.sin(x * 0.022 + 1.4) * 28 + math.sin(x * 0.041 + 0.6) * 14
        pts_far.append((x, far_y + int(offs)))
    pts_far.append((w, h))
    pygame.draw.polygon(surf, (35, 45, 100), pts_far)
    near_y = int(h * 0.70)
    pts_near = [(0, h)]
    for x in range(0, w + 1, 3):
        offs = math.sin(x * 0.033 + 2.1) * 22 + math.sin(x * 0.058 + 1.0) * 10
        pts_near.append((x, near_y + int(offs)))
    pts_near.append((w, h))
    pygame.draw.polygon(surf, (22, 30, 72), pts_near)
    return surf


# ── helpers ─────────────────────────────────────────────────────────────────────

def _text(surf: pygame.Surface, s: str, size: int, *,
          center=None, midleft=None, color=CREAM, shadow=None):
    f = font(size)
    img = f.render(s, True, color)
    rect = img.get_rect()
    if center:
        rect.center = center
    elif midleft:
        rect.midleft = midleft
    if shadow:
        sh = img.copy()
        sh.fill((*shadow[:3], 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow[3])
        surf.blit(sh, (rect.x + 1, rect.y + 1))
    surf.blit(img, rect)


def _alpha_line(surf: pygame.Surface, rgba, p0, p1, width: int = 1):
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


def _band_pts(a_start: float, a_end: float, radius: float, n: int = 100):
    """Arc-points from a_start to a_end at given radius."""
    pts = []
    for i in range(n + 1):
        t = i / n
        a = a_start + (a_end - a_start) * t
        pts.append((CX + radius * math.cos(a), CY - radius * math.sin(a)))
    return pts


def _annular_poly(a_start: float, a_end: float, n: int = 100):
    """Returns (inner_pts, outer_pts, closed_polygon)."""
    inner = _band_pts(a_start, a_end, R_INNER, n)
    outer = _band_pts(a_start, a_end, R_OUTER, n)
    poly = inner + list(reversed(outer))
    return inner, outer, poly


# ── main render ─────────────────────────────────────────────────────────────────

def render_screen() -> pygame.Surface:
    surf = build_skybit_bg(W, H)

    start_angle = math.pi          # 180°  (p=0)
    death_angle = arc_angle(DEATH_P)  # ≈ 2.099 rad = 120.3°  (p=0.184)
    end_angle   = 0.0              # 0°  (p=1)

    death_x, death_y = arc_pos(DEATH_P)

    # ── radial components at death angle ─────────────────────────────────────
    ux_d = math.cos(death_angle)
    uy_d = -math.sin(death_angle)
    # tangential (perpendicular to radial)
    perp_x = -uy_d
    perp_y  =  ux_d

    # ══ 2. Flown band interior  (180° → 120.3°) ════════════════════════════════
    # Fix 1: warm lifted fill so flown reads as "opened"
    inner_f, outer_f, flown_poly = _annular_poly(start_angle, death_angle, n=80)
    pygame.draw.polygon(surf, (42, 38, 60), flown_poly)

    # INK edges along inner and outer arcs
    pygame.draw.lines(surf, INK, False, inner_f, 2)
    pygame.draw.lines(surf, INK, False, outer_f, 2)

    # 3px GOLD route line at R=168
    route_pts = _band_pts(start_angle, death_angle, R, n=80)
    pygame.draw.lines(surf, GOLD, False, route_pts, 3)

    # Fix 3: GEYSER stamp placed via arc_pos(0.167) on band centerline
    gx, gy = arc_pos(0.167, radius=168)
    gx, gy, g_r = int(round(gx)), int(round(gy)), 8
    diamond = [
        (gx,       gy - g_r),
        (gx + g_r, gy),
        (gx,       gy + g_r),
        (gx - g_r, gy),
    ]
    pygame.draw.polygon(surf, GOLD, diamond)
    pygame.draw.polygon(surf, INK,  diamond, 2)

    # ══ 3. NEWBIE bracket  (R=150, 180° → 120.3°, open at death end) ═══════════
    R_BKT = 150
    bkt_col = (200, 180, 120)
    bkt_pts = _band_pts(start_angle, death_angle, R_BKT, n=60)
    bkt_lay = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.lines(bkt_lay, (*bkt_col, 150), False, bkt_pts, 2)

    # Foot mark at start (angle=180°)
    bs = bkt_pts[0]
    foot_e = (bs[0] + 6, bs[1])
    pygame.draw.line(bkt_lay, (*bkt_col, 150),
                     (int(bs[0]), int(bs[1])), (int(foot_e[0]), int(foot_e[1])), 2)

    surf.blit(bkt_lay, (0, 0))

    # NEWBIE label at bracket midpoint, offset inward
    mid_a = (start_angle + death_angle) / 2
    lx = int(CX + (R_BKT - 16) * math.cos(mid_a))
    ly = int(CY - (R_BKT - 16) * math.sin(mid_a))
    _text(surf, "NEWBIE", 9, center=(lx, ly), color=bkt_col)

    # ══ 4. Sealed flap  (120.3° → 0°) ══════════════════════════════════════════
    inner_s, outer_s, sealed_poly = _annular_poly(death_angle, end_angle, n=120)
    pygame.draw.polygon(surf, (12, 16, 40), sealed_poly)

    pygame.draw.lines(surf, INK, False, inner_s, 2)
    pygame.draw.lines(surf, INK, False, outer_s, 2)

    # ══ 5. Death tear  (Fix 2: hero tear — 4px, full-opacity cream) ═════════════
    rng_tear = random.Random(42)
    n_tear = rng_tear.randint(6, 8)
    tear_pts = []
    for i in range(n_tear):
        t = i / (n_tear - 1)
        rt = R_INNER + (R_OUTER - R_INNER) * t
        bx_ = CX + rt * ux_d
        by_ = CY + rt * uy_d
        noise = rng_tear.uniform(-2.0, 2.0)
        tear_pts.append((bx_ + perp_x * noise, by_ + perp_y * noise))

    tear_lay = pygame.Surface((W, H), pygame.SRCALPHA)
    # Fix 2: full-opacity cream tear edge
    tear_rgba = (230, 220, 200, 255)

    if len(tear_pts) > 1:
        pygame.draw.lines(tear_lay, tear_rgba, False,
                          [(int(p[0]), int(p[1])) for p in tear_pts], 4)

    # Triangular tab hanging outward past R_OUTER, 8px long
    tab_base_a = (CX + R_OUTER * ux_d + perp_x * 3.0,
                  CY + R_OUTER * uy_d + perp_y * 3.0)
    tab_base_b = (CX + R_OUTER * ux_d - perp_x * 3.0,
                  CY + R_OUTER * uy_d - perp_y * 3.0)
    tab_tip    = (CX + (R_OUTER + 8) * ux_d,
                  CY + (R_OUTER + 8) * uy_d)
    pygame.draw.polygon(tear_lay, tear_rgba,
                        [(int(tab_base_a[0]), int(tab_base_a[1])),
                         (int(tab_base_b[0]), int(tab_base_b[1])),
                         (int(tab_tip[0]),    int(tab_tip[1]))])

    surf.blit(tear_lay, (0, 0))

    # Fix 2: Gold node at band centerline where tear crosses death position
    pygame.draw.circle(surf, GOLD, (int(round(death_x)), int(round(death_y))), 4)
    pygame.draw.circle(surf, INK,  (int(round(death_x)), int(round(death_y))), 4, 2)

    # ══ 6. Bronze wax seals (Fix 4) ═════════════════════════════════════════════
    def wax_seal(px: float, py: float, radius: int = 5,
                 fill=BRONZE_SEAL) -> None:
        ix, iy = int(round(px)), int(round(py))
        pygame.draw.circle(surf, fill,            (ix, iy), radius)
        pygame.draw.circle(surf, BRONZE_SEAL_RIM, (ix, iy), radius, 2)
        pygame.draw.circle(surf, INK,             (ix, iy), radius + 1, 2)

    # CLOWN:      angle=80.5°, R=165
    ca = math.radians(80.5)
    wax_seal(CX + 165 * math.cos(ca), CY - 165 * math.sin(ca))

    # RAIN:       angle=76.2°, R=171
    ra = math.radians(76.2)
    wax_seal(CX + 171 * math.cos(ra), CY - 171 * math.sin(ra))

    # SNOWSTORM:  angle=21.8°, R=168
    sa = math.radians(21.8)
    wax_seal(CX + 168 * math.cos(sa), CY - 168 * math.sin(sa))

    # DAY COMPLETE: angle=0°, large seal — slightly brighter bronze
    wax_seal(CX + 168.0, float(CY), radius=8, fill=BRONZE_DAY)

    # ══ 7. Chrome ═══════════════════════════════════════════════════════════════

    # Fix 5: Dark header band with alpha ~200
    hdr_band = pygame.Surface((360, 66), pygame.SRCALPHA)
    pygame.draw.rect(hdr_band, (6, 8, 14, 200), hdr_band.get_rect())
    surf.blit(hdr_band, (0, 0))

    # "FLIGHT LOG" 16px GOLD centered at y=28
    _text(surf, "FLIGHT LOG", 16, center=(W // 2, 28), color=GOLD,
          shadow=(0, 0, 0, 160))

    # Sub-header with 18.4% completion included (Fix 5: replaces separate callout)
    _text(surf, "DAY 1  ·  PILLAR 25  ·  0:47  ·  18.4%", 11,
          center=(W // 2, 50), color=CREAM, shadow=(0, 0, 0, 120))

    # Fix 5: 1px GOLD rule at y=66
    pygame.draw.line(surf, GOLD, (0, 66), (W - 1, 66), 1)

    # ── BACK button ─────────────────────────────────────────────────────────────
    back_r = pygame.Rect(0, 0, 80, 28)
    back_r.center = (180, 610)
    back_s = pygame.Surface(back_r.size, pygame.SRCALPHA)
    pygame.draw.rect(back_s, (30, 20, 10, 255), back_s.get_rect(), border_radius=14)
    pygame.draw.rect(back_s, (*GOLD, 255), back_s.get_rect(), width=2, border_radius=14)
    surf.blit(back_s, back_r.topleft)
    _text(surf, "BACK", 11, center=back_r.center, color=GOLD)

    return surf


def main() -> None:
    screen = render_screen()
    out = os.path.join(ROOT, "docs", "flight_log_arc", "sealed_horizon", "round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(screen, out)
    loaded = pygame.image.load(out)
    assert loaded.get_size() == (360, 640), f"unexpected size {loaded.get_size()}"
    print(f"saved {out}  {loaded.get_size()}")


if __name__ == "__main__":
    main()
