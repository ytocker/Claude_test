#!/usr/bin/env python3
"""altitude_ribbon · flight-log arc concept · round 1

The flown arc is a tapered gold band with real mass. Past death the band's
ink keylines continue as an EMPTY CHANNEL across the whole arc — the full
shape of the day is present, but only the flown portion has fill. Hidden
events register as channel pinches. Death = diagonal shear cut with rim-light.
"""
import os
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

ROOT      = "/home/user/skybit"
FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"

W, H = 360, 640

INK         = (6, 8, 14)
GOLD        = (255, 206, 92)
CREAM       = (246, 240, 230)
CHAN_INK    = (10, 14, 30)      # channel edge keyline (slightly lighter than INK)
CHAN_FILL   = (16, 20, 48)      # interior of empty channel
HATCH_COLOR = (150, 110, 40)    # newbie crosshatch
GEYSER_C    = (146, 232, 255)

CX, CY   = 180, 430
R        = 168
EASE_P   = 0.652
DEATH_P  = 0.184

DEATH_PILLAR = 25
DAY_N        = 1
TIME_ALIVE   = 47

_fonts: dict = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


def ease(p):
    return max(0.0, min(1.0, p)) ** EASE_P


def arc_angle(p):
    return math.pi * (1.0 - ease(p))


def arc_pos(p):
    a = arc_angle(p)
    return (CX + R * math.cos(a), CY - R * math.sin(a))


def radial_unit(p):
    a = arc_angle(p)
    return (math.cos(a), -math.sin(a))


def lerp(a, b, t):
    return a + (b - a) * t


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


# ── chrome helpers ────────────────────────────────────────────────────────────

def text_blit(surf, s, size, center=None, midleft=None, color=CREAM):
    f = font(size)
    img = f.render(s, True, color)
    r = img.get_rect()
    if center:
        r.center = center
    elif midleft:
        r.midleft = midleft
    surf.blit(img, r)
    return r


def draw_pill(surf, rect, fill=(30, 20, 10), border=GOLD, border_w=2, radius=6, fill_alpha=230):
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s, (*fill, fill_alpha), s.get_rect(), border_radius=radius)
    pygame.draw.rect(s, (*border, 255), s.get_rect(), width=border_w, border_radius=radius)
    surf.blit(s, rect.topleft)


def alpha_line(surf, rgba, p0, p1, width=1):
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


# ── main render ───────────────────────────────────────────────────────────────

def main():
    # 1. Background
    surf = build_skybit_bg(W, H)

    # ── 2. EMPTY CHANNEL (full arc p=0→1) ────────────────────────────────────
    STEPS = 200
    all_inner = []
    all_outer = []

    for i in range(STEPS + 1):
        p = i / STEPS
        a = arc_angle(p)
        rx, ry = math.cos(a), -math.sin(a)
        ox = CX + R * math.cos(a)
        oy = CY - R * math.sin(a)
        # Pinch at hidden event zones
        if (0.390 <= p <= 0.415) or (0.420 <= p <= 0.442) or (0.808 <= p <= 0.833):
            hw = 1.5
        else:
            hw = 4.0
        all_inner.append((ox - rx * hw, oy - ry * hw))
        all_outer.append((ox + rx * hw, oy + ry * hw))

    # Fill channel interior quad by quad
    for i in range(len(all_inner) - 1):
        poly = [
            (int(all_inner[i][0]),     int(all_inner[i][1])),
            (int(all_inner[i + 1][0]), int(all_inner[i + 1][1])),
            (int(all_outer[i + 1][0]), int(all_outer[i + 1][1])),
            (int(all_outer[i][0]),     int(all_outer[i][1])),
        ]
        pygame.draw.polygon(surf, CHAN_FILL, poly)

    # Ink edge lines
    ipts = [(int(x), int(y)) for x, y in all_inner]
    opts = [(int(x), int(y)) for x, y in all_outer]
    pygame.draw.lines(surf, CHAN_INK, False, ipts, 2)
    pygame.draw.lines(surf, CHAN_INK, False, opts, 2)

    # ── 3. NEWBIE PERIOD crosshatch (p=0→0.20, drawn before gold fill) ───────
    NEWBIE_END  = 0.20
    HATCH_PITCH = 7.0
    prev_pt  = arc_pos(0.0)
    arc_dist = 0.0
    next_hatch = 3.5    # first crosshatch at half-pitch so it doesn't land on the start cap

    for i in range(1, STEPS + 1):
        p = i / STEPS
        if p > NEWBIE_END:
            break
        curr_pt  = arc_pos(p)
        arc_dist += math.hypot(curr_pt[0] - prev_pt[0], curr_pt[1] - prev_pt[1])
        prev_pt  = curr_pt

        if arc_dist >= next_hatch:
            next_hatch += HATCH_PITCH
            a       = arc_angle(p)
            ox      = CX + R * math.cos(a)
            oy      = CY - R * math.sin(a)
            tx, ty  = math.sin(a), -math.cos(a)    # tangent direction (screen)
            hw      = 4.0
            for sign in (-1, 1):
                theta    = math.radians(35 * sign)
                cos_t, sin_t = math.cos(theta), math.sin(theta)
                # Rotate tangent by theta
                hx = tx * cos_t - ty * sin_t
                hy = tx * sin_t + ty * cos_t
                half_len = hw * 1.8          # long enough to span 8px channel at 35°
                pygame.draw.line(surf, HATCH_COLOR,
                                 (int(ox - hx * half_len), int(oy - hy * half_len)),
                                 (int(ox + hx * half_len), int(oy + hy * half_len)), 2)

    # ── 4. FLOWN ARC gold fill (p=0→DEATH_P) ─────────────────────────────────
    F_STEPS = 80
    f_inner = []
    f_outer = []

    for i in range(F_STEPS + 1):
        t  = i / F_STEPS
        p  = DEATH_P * t
        a  = arc_angle(p)
        rx, ry = math.cos(a), -math.sin(a)
        ox = CX + R * math.cos(a)
        oy = CY - R * math.sin(a)
        hw = lerp(3.0, 6.0, t)
        # Gradient: warm amber at start → bright gold at death
        col = (
            int(lerp(212, 255, t)),
            int(lerp(158, 206, t)),
            int(lerp(64,   92, t)),
        )
        f_inner.append((ox - rx * hw, oy - ry * hw, col))
        f_outer.append((ox + rx * hw, oy + ry * hw, col))

    # Build polygon (solid GOLD) and fill
    poly_pts = ([(int(x), int(y)) for x, y, _ in f_inner] +
                [(int(x), int(y)) for x, y, _ in reversed(f_outer)])
    pygame.draw.polygon(surf, GOLD, poly_pts)

    # Overdraw with thin colour-gradient stripes for the warmth gradient
    for i in range(F_STEPS):
        col = f_inner[i][2]
        p0i = (int(f_inner[i][0]),     int(f_inner[i][1]))
        p1i = (int(f_inner[i + 1][0]), int(f_inner[i + 1][1]))
        p0o = (int(f_outer[i][0]),     int(f_outer[i][1]))
        p1o = (int(f_outer[i + 1][0]), int(f_outer[i + 1][1]))
        pygame.draw.polygon(surf, col, [p0i, p1i, p1o, p0o])

    # 2px ink edges on gold band
    fi_pts = [(int(x), int(y)) for x, y, _ in f_inner]
    fo_pts = [(int(x), int(y)) for x, y, _ in f_outer]
    pygame.draw.lines(surf, INK, False, fi_pts, 2)
    pygame.draw.lines(surf, INK, False, fo_pts, 2)

    # ── 5. GEYSER notch at p=0.27 (in empty channel past death) ──────────────
    gp  = 0.27
    ga  = arc_angle(gp)
    gox = CX + R * math.cos(ga)
    goy = CY - R * math.sin(ga)
    grx, gry = math.cos(ga), -math.sin(ga)     # radial
    gtx, gty = math.sin(ga), -math.cos(ga)     # tangent

    notch_hw = 4.5      # half-width tangential (9px slot)
    notch_hr = 6.0      # half-depth radial    (12px deep)
    notch_poly = [
        (int(gox - gtx * notch_hw - grx * notch_hr),
         int(goy - gty * notch_hw - gry * notch_hr)),
        (int(gox + gtx * notch_hw - grx * notch_hr),
         int(goy + gty * notch_hw - gry * notch_hr)),
        (int(gox + gtx * notch_hw + grx * notch_hr),
         int(goy + gty * notch_hw + gry * notch_hr)),
        (int(gox - gtx * notch_hw + grx * notch_hr),
         int(goy - gty * notch_hw + gry * notch_hr)),
    ]
    pygame.draw.polygon(surf, INK, notch_poly)

    # Cyan geyser glyph: upward plume with two spreading arms
    gc_x, gc_y = int(gox), int(goy)
    pygame.draw.line(surf, GEYSER_C, (gc_x, gc_y + 3), (gc_x, gc_y - 3), 2)
    pygame.draw.line(surf, GEYSER_C, (gc_x, gc_y - 2), (gc_x - 3, gc_y - 6), 1)
    pygame.draw.line(surf, GEYSER_C, (gc_x, gc_y - 2), (gc_x + 3, gc_y - 6), 1)

    # ── 6. DEATH shear cut at p=DEATH_P ──────────────────────────────────────
    da  = arc_angle(DEATH_P)
    ddx = CX + R * math.cos(da)
    ddy = CY - R * math.sin(da)
    drx, dry = math.cos(da), -math.sin(da)     # radial unit at death
    dtx, dty = math.sin(da), -math.cos(da)     # tangent unit at death

    death_hw = 6.0
    # 30° rake: tangential offset = hw * tan(30°) ≈ hw * 0.577
    shear = death_hw * 0.577
    cut_inner = (ddx - drx * death_hw - dtx * shear,
                 ddy - dry * death_hw - dty * shear)
    cut_outer = (ddx + drx * death_hw + dtx * shear,
                 ddy + dry * death_hw + dty * shear)

    # 3px ink cut face
    pygame.draw.line(surf, INK,
                     (int(cut_inner[0]), int(cut_inner[1])),
                     (int(cut_outer[0]), int(cut_outer[1])), 3)
    # 2px warm rim-light offset 1px along tangent
    pygame.draw.line(surf, (255, 238, 190),
                     (int(cut_inner[0] + dtx), int(cut_inner[1] + dty)),
                     (int(cut_outer[0] + dtx), int(cut_outer[1] + dty)), 2)

    # Gold particles scattered around death point
    rng = random.Random(999)
    for _ in range(6):
        px = ddx + rng.uniform(-12, 12)
        py = ddy + rng.uniform(-12, 12)
        pr = rng.randint(1, 2)
        alpha = rng.randint(120, 200)
        p_lay = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(p_lay, (*GOLD, alpha), (pr + 1, pr + 1), pr)
        surf.blit(p_lay, (int(px) - pr - 1, int(py) - pr - 1))

    # ── 7. DAY COMPLETE cap at p=1.0 → (348, 430) ────────────────────────────
    ca  = arc_angle(1.0)
    cap_x = CX + R * math.cos(ca)     # = 348
    cap_y = CY - R * math.sin(ca)     # = 430
    crx, cry = math.cos(ca), -math.sin(ca)     # = (1, 0)
    cap_hw = 4.0
    cap_inner = (int(cap_x - crx * cap_hw), int(cap_y - cry * cap_hw))
    cap_outer = (int(cap_x + crx * cap_hw), int(cap_y + cry * cap_hw))
    pygame.draw.line(surf, GOLD, cap_inner, cap_outer, 3)
    pygame.draw.line(surf, INK,
                     (cap_inner[0] - 1, cap_inner[1]),
                     (cap_outer[0] - 1, cap_outer[1]), 1)

    # ── 8. NEWBIE bracket label outside arc R=185 near p=0.10 ────────────────
    nb_a  = arc_angle(0.10)
    nb_r  = 185
    nb_x  = int(CX + nb_r * math.cos(nb_a))
    nb_y  = int(CY - nb_r * math.sin(nb_a))
    nb_col = (200, 180, 120)
    text_blit(surf, "NEWBIE", 9, center=(nb_x, nb_y - 9), color=nb_col)
    bw = 22
    pygame.draw.line(surf, nb_col, (nb_x - bw, nb_y + 1), (nb_x + bw, nb_y + 1), 1)
    pygame.draw.line(surf, nb_col, (nb_x - bw, nb_y - 3), (nb_x - bw, nb_y + 5), 1)
    pygame.draw.line(surf, nb_col, (nb_x + bw, nb_y - 3), (nb_x + bw, nb_y + 5), 1)

    # ── 9. Chrome ─────────────────────────────────────────────────────────────

    # Semi-transparent header bar
    hdr = pygame.Surface((W, 68), pygame.SRCALPHA)
    hdr.fill((26, 22, 34, 220))
    surf.blit(hdr, (0, 0))
    alpha_line(surf, (*GOLD, 150), (0, 68), (W - 1, 68), 1)

    text_blit(surf, "FLIGHT LOG", 16, center=(W // 2, 28), color=GOLD)
    text_blit(surf, f"DAY {DAY_N}  ·  PILLAR {DEATH_PILLAR}  ·  0:{TIME_ALIVE:02d}",
              11, center=(W // 2, 50), color=CREAM)

    # Death callout: small dark pill with GOLD border, near the death point
    death_scr_x, death_scr_y = int(ddx), int(ddy)
    chip_label = "ENDED 18.4%"
    chip_f = font(9)
    chip_w  = chip_f.size(chip_label)[0] + 14
    chip_h  = 20
    chip_x  = max(4, min(W - chip_w - 4, death_scr_x + 18))
    chip_y  = max(80, min(H - chip_h - 4, death_scr_y + 18))
    chip_r  = pygame.Rect(chip_x, chip_y, chip_w, chip_h)
    alpha_line(surf, (*GOLD, 170),
               (death_scr_x, death_scr_y),
               (chip_x, chip_y + chip_h // 2), 1)
    draw_pill(surf, chip_r, fill=(30, 20, 10), border=GOLD, border_w=1,
              radius=4, fill_alpha=230)
    text_blit(surf, chip_label, 9, center=chip_r.center, color=CREAM)

    # BACK button: 80×28 centred at (180, 610)
    back_r = pygame.Rect(0, 0, 80, 28)
    back_r.center = (180, 610)
    draw_pill(surf, back_r, fill=(30, 20, 10), border=GOLD, border_w=2,
              radius=6, fill_alpha=230)
    text_blit(surf, "BACK", 11, center=back_r.center, color=GOLD)

    # ── Save ──────────────────────────────────────────────────────────────────
    out = os.path.join(ROOT, "docs", "flight_log_arc", "altitude_ribbon", "round_1.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(surf, out)
    loaded = pygame.image.load(out)
    print(f"saved {out}  {loaded.get_size()}")


if __name__ == "__main__":
    main()
