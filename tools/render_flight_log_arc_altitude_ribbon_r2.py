#!/usr/bin/env python3
"""altitude_ribbon · flight-log arc concept · round 2

Round 2 art-director fixes applied:
  Fix 1: GEYSER moved to p=0.167 (inside flown band, before death at 0.184)
  Fix 2: Crosshatch drawn AFTER gold fill, clamped to min(0.20, DEATH_P)
  Fix 3: Smooth pinch transitions — squeeze ramps instead of hard rectangular steps
  Fix 4: DAY COMPLETE terminus upgraded to dim-gold ring
  Fix 5: NEWBIE bracket label removed (crosshatch texture alone communicates zone)
  Fix 6: Chrome header normalised; death callout chip removed (header carries the data)
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
CHAN_INK    = (10, 14, 30)      # channel edge keyline
CHAN_FILL   = (16, 20, 48)      # interior of empty channel
HATCH_COLOR = (150, 110, 40)    # newbie crosshatch — darker amber
GEYSER_C    = (146, 232, 255)   # cyan geyser glyph

CX, CY   = 180, 430
R        = 168
EASE_P   = 0.652
DEATH_P  = 0.184

GEYSER_P = 0.167   # Fix 1: inside flown zone before death (was 0.27)

DEATH_PILLAR = 25
DAY_N        = 1
TIME_ALIVE   = 47

# Fix 3: smooth pinch — centres and ramp width
PINCH_CENTERS = [0.403, 0.430, 0.820]   # CLOWN, RAIN, SNOWSTORM
PINCH_RAMP    = 0.008                    # half-ramp on each side of centre
HW_FULL       = 4.0
HW_MIN        = 1.5

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


def lerp(a, b, t):
    return a + (b - a) * t


def smooth_pinch_hw(p):
    """Fix 3: ramp the channel half-width smoothly around each hidden-event centre."""
    hw = HW_FULL
    for pc in PINCH_CENTERS:
        lo, hi = pc - PINCH_RAMP, pc + PINCH_RAMP
        if lo <= p <= pc:
            t = (p - lo) / PINCH_RAMP      # 0 → 1  (approaching centre)
            hw = min(hw, lerp(HW_FULL, HW_MIN, t))
        elif pc < p <= hi:
            t = (p - pc) / PINCH_RAMP      # 0 → 1  (leaving centre)
            hw = min(hw, lerp(HW_MIN, HW_FULL, t))
    return hw


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

    # ── 2. EMPTY CHANNEL (full arc p=0→1) with smooth pinch transitions (Fix 3)
    STEPS = 200
    all_inner = []
    all_outer = []

    for i in range(STEPS + 1):
        p = i / STEPS
        a = arc_angle(p)
        rx, ry = math.cos(a), -math.sin(a)
        ox = CX + R * math.cos(a)
        oy = CY - R * math.sin(a)
        hw = smooth_pinch_hw(p)   # Fix 3: smooth ramp instead of hard step
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

    # ── 3. FLOWN ARC gold fill (p=0→DEATH_P) — drawn BEFORE crosshatch ───────
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

    # Solid GOLD base polygon
    poly_pts = ([(int(x), int(y)) for x, y, _ in f_inner] +
                [(int(x), int(y)) for x, y, _ in reversed(f_outer)])
    pygame.draw.polygon(surf, GOLD, poly_pts)

    # Overdraw with thin colour-gradient stripes for warmth gradient
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

    # ── 4. NEWBIE PERIOD crosshatch AFTER gold fill (Fix 2) ──────────────────
    # Clamped to p=0→min(0.20, DEATH_P)=0.184 — never extends past the shear cut
    NEWBIE_END  = min(0.20, DEATH_P)   # 0.184
    HATCH_PITCH = 7.0
    prev_pt  = arc_pos(0.0)
    arc_dist = 0.0
    next_hatch = 3.5    # first hatch at half-pitch offset from start cap

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
                theta        = math.radians(35 * sign)
                cos_t, sin_t = math.cos(theta), math.sin(theta)
                hx = tx * cos_t - ty * sin_t
                hy = tx * sin_t + ty * cos_t
                half_len = hw * 1.8
                # Draw in darker amber (150, 110, 40) at 2px so it shows on gold
                pygame.draw.line(surf, HATCH_COLOR,
                                 (int(ox - hx * half_len), int(oy - hy * half_len)),
                                 (int(ox + hx * half_len), int(oy + hy * half_len)), 2)

    # ── 5. GEYSER notch at p=0.167 — now inside the flown zone (Fix 1) ───────
    gp  = GEYSER_P   # 0.167 — earned, before death
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

    # ── 7. DAY COMPLETE terminus — upgraded dim-gold ring (Fix 4) ────────────
    ca    = arc_angle(1.0)
    cap_x = CX + R * math.cos(ca)     # = 348
    cap_y = CY - R * math.sin(ca)     # = 430
    crx, cry = math.cos(ca), -math.sin(ca)
    cap_hw    = 4.0
    cap_inner = (int(cap_x - crx * cap_hw), int(cap_y - cry * cap_hw))
    cap_outer = (int(cap_x + crx * cap_hw), int(cap_y + cry * cap_hw))

    # Transverse cap line beneath the ring
    pygame.draw.line(surf, (100, 90, 60), cap_inner, cap_outer, 2)

    # Ring layers (back to front):
    #   r=9  filled dim gold  (80, 65, 20)
    #   r=5  filled INK — dark centre punch-out
    #   r=10 2px GOLD keyline ring
    cap_ctr = (int(cap_x), int(cap_y))
    pygame.draw.circle(surf, (80, 65, 20), cap_ctr, 9)
    pygame.draw.circle(surf, INK,          cap_ctr, 5)
    pygame.draw.circle(surf, GOLD,         cap_ctr, 10, 2)

    # ── 8. Chrome — normalised header (Fix 6); no NEWBIE label (Fix 5); no chip ─

    # ~66px dark header band — INK at alpha=180
    hdr = pygame.Surface((W, 66), pygame.SRCALPHA)
    hdr.fill((*INK, 180))
    surf.blit(hdr, (0, 0))

    # 1px GOLD rule at y=66
    alpha_line(surf, (*GOLD, 220), (0, 66), (W - 1, 66), 1)

    # "FLIGHT LOG" 16px GOLD centred at y=28
    text_blit(surf, "FLIGHT LOG", 16, center=(W // 2, 28), color=GOLD)

    # "DAY 1  ·  PILLAR 25  ·  0:47  ·  18.4%" 11px CREAM centred at y=50
    pct      = f"{DEATH_P * 100:.1f}%"
    subtitle = f"DAY {DAY_N}  ·  PILLAR {DEATH_PILLAR}  ·  0:{TIME_ALIVE:02d}  ·  {pct}"
    text_blit(surf, subtitle, 11, center=(W // 2, 50), color=CREAM)

    # BACK button
    back_r = pygame.Rect(0, 0, 80, 28)
    back_r.center = (180, 610)
    draw_pill(surf, back_r, fill=(30, 20, 10), border=GOLD, border_w=2,
              radius=6, fill_alpha=230)
    text_blit(surf, "BACK", 11, center=back_r.center, color=GOLD)

    # ── Save ──────────────────────────────────────────────────────────────────
    out = os.path.join(ROOT, "docs", "flight_log_arc", "altitude_ribbon", "round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(surf, out)
    loaded = pygame.image.load(out)
    print(f"saved {out}  {loaded.get_size()}")


if __name__ == "__main__":
    main()
